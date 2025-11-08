import argparse
from datasets import load_dataset, Dataset, concatenate_datasets
from transformers import MarianMTModel, MarianTokenizer, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq
import pandas as pd

def preprocess_function(examples, tokenizer, max_length=128):
    inputs = tokenizer(examples['en'], max_length=max_length, truncation=True)
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(examples['te'], max_length=max_length, truncation=True)
    inputs["labels"] = labels["input_ids"]
    return inputs

def load_csv_dataset(path):
    df = pd.read_csv(path, sep="\t")
    return Dataset.from_pandas(df)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed_dir", type=str, required=True)
    parser.add_argument("--output_dir", type=str, required=True)
    parser.add_argument("--model_name", type=str, default="Helsinki-NLP/opus-mt-en-ROMANCE")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=4)
    args = parser.parse_args()

    # Load datasets
    train_dataset = concatenate_datasets([
        load_csv_dataset(f"{args.processed_dir}/train.tsv"),
        load_csv_dataset(f"{args.processed_dir}_swapped/train.tsv")
    ])

    val_dataset = concatenate_datasets([
        load_csv_dataset(f"{args.processed_dir}/val.tsv"),
        load_csv_dataset(f"{args.processed_dir}_swapped/val.tsv")
    ])

    test_dataset = concatenate_datasets([
        load_csv_dataset(f"{args.processed_dir}/test.tsv"),
        load_csv_dataset(f"{args.processed_dir}_swapped/test.tsv")
    ])

    # Load tokenizer and model
    tokenizer = MarianTokenizer.from_pretrained(args.model_name)
    model = MarianMTModel.from_pretrained(args.model_name)

    # Preprocess datasets
    tokenized_train = train_dataset.map(lambda x: preprocess_function(x, tokenizer), batched=True)
    tokenized_val = val_dataset.map(lambda x: preprocess_function(x, tokenizer), batched=True)
    tokenized_test = test_dataset.map(lambda x: preprocess_function(x, tokenizer), batched=True)

    # Data collator
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    # Training arguments
    training_args = Seq2SeqTrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        num_train_epochs=args.epochs,
        save_total_limit=2,
        predict_with_generate=True,
        logging_dir='./logs',
        logging_steps=50,
        save_strategy="steps",
        save_steps=500,
        eval_steps=500,
        #evaluation_strategy="steps"
    )

    # Trainer
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        tokenizer=tokenizer,
        data_collator=data_collator
    )

    trainer.train()
    trainer.save_model(args.output_dir)

if __name__ == "__main__":
    main()
