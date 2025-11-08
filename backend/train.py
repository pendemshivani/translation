# train.py
import argparse
from datasets import load_dataset
from transformers import MarianMTModel, MarianTokenizer, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq

def preprocess_function(examples, tokenizer, max_length=128):
    model_inputs = tokenizer(examples['en'], max_length=max_length, truncation=True)
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(examples['te'], max_length=max_length, truncation=True)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=str, required=True)
    parser.add_argument("--val", type=str, required=True)
    parser.add_argument("--test", type=str, required=True)
    parser.add_argument("--output_dir", type=str, required=True)
    parser.add_argument("--model_name", type=str, default="Helsinki-NLP/opus-mt-en-te")
    parser.add_argument("--per_device_train_batch_size", type=int, default=4)
    parser.add_argument("--per_device_eval_batch_size", type=int, default=4)
    parser.add_argument("--num_train_epochs", type=int, default=3)
    parser.add_argument("--learning_rate", type=float, default=5e-5)
    parser.add_argument("--max_length", type=int, default=128)
    args = parser.parse_args()

    data_files = {"train": args.train, "validation": args.val, "test": args.test}
    raw_datasets = load_dataset("csv", data_files=data_files, delimiter="\t")

    tokenizer = MarianTokenizer.from_pretrained(args.model_name)
    model = MarianMTModel.from_pretrained(args.model_name)

    tokenized_datasets = raw_datasets.map(lambda x: preprocess_function(x, tokenizer, max_length=args.max_length), batched=True)

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    training_args = Seq2SeqTrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.per_device_train_batch_size,
        per_device_eval_batch_size=args.per_device_eval_batch_size,
        learning_rate=args.learning_rate,
        save_total_limit=3,
        num_train_epochs=args.num_train_epochs,
        predict_with_generate=True,
        logging_dir='./logs',
        logging_steps=100,
        save_strategy="steps",
        save_steps=500,
        eval_steps=500,
        evaluation_strategy="steps",
        fp16=False,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        tokenizer=tokenizer,
        data_collator=data_collator
    )

    trainer.train()
    trainer.save_model(args.output_dir)

if __name__ == "__main__":
    main()
