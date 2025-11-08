# 🌐 Telugu ↔ English Bidirectional Translator  

A smart and elegant web application that translates between **Telugu and English** using both **voice input** and **manual text input**.  
It automatically detects the language you speak or type, translates it into the target language, and stores recent translations for easy reference.  

---

## 🚀 Features

### 🗣️ Dual Input Mode  
- Speak through your microphone or type manually.  
- The system automatically detects whether you’re using **Telugu** or **English**.  

### 🌍 Bidirectional Translation  
- Instantly translates **Telugu → English** or **English → Telugu**.  
- You can swap the direction anytime using a single button.  

### 🕘 Translation History  
- Stores your past translations (locally) for quick reference.  
- View your most recent translations easily.  

### 💬 Simple and Professional UI  
- Calm, elegant color palette for better user focus.  
- Designed for clarity, usability, and minimal distractions.  

---

## 🧠 Tech Stack

### ⚙️ Backend
- **FastAPI** – for handling translation requests  
- **Hugging Face Transformers (NLLB-200)** – for accurate Telugu ↔ English translation  
- **PyTorch** – model runtime  
- **Uvicorn** – production-ready ASGI server  

### 💻 Frontend
- **React.js** – for building the user interface  
- **Axios** – for API communication  
- **Web Speech API** – for speech recognition and text-to-speech  
- **Local Storage** – to maintain recent translation history  
- **Custom CSS** – for professional design and responsive layout  

---

## 🧩 Setup & Run Locally

### Backend (FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # (use 'source venv/bin/activate' on Mac/Linux)
pip install -r requirements.txt
uvicorn inference_app:app --reload
✅ Now open http://127.0.0.1:8000/docs to test your API.

Frontend (React)
bash
Copy code
cd frontend
npm install
npm start
✅ Now visit http://localhost:3000 to use your translator.

