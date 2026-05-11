import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow

load_dotenv()

app = FastAPI(title="SQLi Defense API")

class FeedbackForm(BaseModel):
    query_text: str

try:
    print("⏳ Menghubungi DagsHub MLflow...")
    model_uri = "models:/SQLi-Detection-Model/latest" 
    model = mlflow.sklearn.load_model(model_uri)
    print("✅ Model berhasil diunduh dan aktif!")
except Exception as e:
    print(f"❌ Gagal memuat model: {e}")
    model = None

@app.post("/api/scan")
def scan_input(data: FeedbackForm):
    if not model:
        raise HTTPException(status_code=500, detail="Model gagal dimuat dari cloud.")
    
    text = data.query_text
    
    prediction = model.predict([text])[0]
    
    return {
        "input": text,
        "is_sqli": bool(prediction == 1)
    }