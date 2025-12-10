from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
from malware_detector import is_known_malware, load_or_train_model, predict_malware

app = FastAPI()

# Izinkan akses dari frontend lokal
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Buat folder upload
os.makedirs("uploads", exist_ok=True)
os.makedirs("../model", exist_ok=True)

# Load model saat startup
model = load_or_train_model()

@app.post("/scan")
async def scan_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Simpan file sementara
    file_id = str(uuid.uuid4())
    file_path = f"uploads/{file_id}_{file.filename}"
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    try:
        # Cek hash dulu
        if is_known_malware(file_path):
            result = {"status": "malicious", "confidence": 1.0, "reason": "Known malware hash"}
        else:
            is_malware, confidence = predict_malware(file_path, model)
            if is_malware:
                result = {"status": "malicious", "confidence": float(confidence), "reason": "AI detection"}
            else:
                result = {"status": "clean", "confidence": float(1 - confidence), "reason": "No threat detected"}
    finally:
        # Hapus file setelah scan
        if os.path.exists(file_path):
            os.remove(file_path)
    
    return JSONResponse(content=result)
