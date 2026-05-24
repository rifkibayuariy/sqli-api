import os
import urllib.parse
import html
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow

# 1. Konfigurasi Tracking URI DagsHub
os.environ["MLFLOW_TRACKING_URI"] = "https://dagshub.com/rifkibayuariy/sqli-detection.mlflow"

app = FastAPI(title="SQLi Defense API")

class FeedbackForm(BaseModel):
    query_text: str

# 2. Fungsi Preprocessing (Sama persis dengan prepare.py di DVC)
def eda_based_clean_text(text):
    text = str(text)
    text = urllib.parse.unquote(text)
    text = html.unescape(text)
    text = text.lower()
    text = re.sub(r'/\*.*?\*/', ' ', text)
    text = re.sub(r'[\(\)]', ' ', text)
    text = re.sub(r'([\'"=\-\+\*/<>;])', r' \1 ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# 3. Tarik Model dari DagsHub
try:
    print("⏳ Menghubungi DagsHub MLflow...")
    model_uri = "models:/SQLi-Detection-Model/latest" 
    model = mlflow.sklearn.load_model(model_uri)
    print("✅ Model berhasil diunduh dan aktif!")
except Exception as e:
    print(f"❌ Gagal memuat model: {e}")
    model = None

# 4. Endpoint Deteksi
@app.post("/api/scan")
def scan_input(data: FeedbackForm):
    if not model:
        raise HTTPException(status_code=500, detail="Model gagal dimuat dari cloud.")
    
    text = data.query_text
    
    # 5. BERSIHKAN INPUT SEBELUM DIPREDIKSI
    clean_text = eda_based_clean_text(text)
    
    # Prediksi menggunakan teks yang sudah bersih
    prediction = model.predict([clean_text])[0]
    
    return {
        "input": text,
        "cleaned_input": clean_text,  # Ditambahkan agar kamu bisa memantau hasil pembersihannya
        "is_sqli": bool(prediction == 1)
    }