from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# -----------------------------------------------------
# FastAPI app setup
# -----------------------------------------------------
app = FastAPI(title="English ↔ Telugu Translator")

# Allow frontend access (adjust origin in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------
# Load NLLB-200 model
# -----------------------------------------------------
MODEL_NAME = "facebook/nllb-200-distilled-600M"

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
except Exception as e:
    raise RuntimeError(f"Failed to load model: {e}")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Language codes for NLLB-200
LANG_CODES = {
    "en": "eng_Latn",  # English
    "te": "tel_Telu"   # Telugu
}

# -----------------------------------------------------
# Request schema
# -----------------------------------------------------
class TranslationRequest(BaseModel):
    text: str
    source_lang: str    # 'en' or 'te'
    target_lang: str    # 'en' or 'te'

# -----------------------------------------------------
# Translation endpoint
# -----------------------------------------------------
@app.post("/translate")
async def translate(req: TranslationRequest):
    src_code = LANG_CODES.get(req.source_lang.lower())
    tgt_code = LANG_CODES.get(req.target_lang.lower())

    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    if not src_code or not tgt_code:
        raise HTTPException(status_code=400, detail="Supported languages are 'en' and 'te'.")
    if src_code == tgt_code:
        raise HTTPException(status_code=400, detail="Source and target languages must be different.")

    # Prepare input
    tokenizer.src_lang = src_code
    inputs = tokenizer(req.text, return_tensors="pt").to(device)

    # Generate translation
    generated_tokens = model.generate(
        **inputs,
        forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_code),
        max_length=200
    )

    translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

    return {
        "translation": translated_text,
        "source": req.source_lang,
        "target": req.target_lang
    }