import os
import hashlib
import numpy as np
from sklearn.svm import SVC
import joblib

MODEL_PATH = "models/malware_model.joblib"
HASH_DB = "data/known_hashes.txt"

# Muat hash malware (buat file kosong jika belum ada)
if not os.path.exists(HASH_DB):
    with open(HASH_DB, "w") as f:
        f.write("e1c1d2b3a4f5e6d7c8b9a0f1e2d3c4b5a6d7e8f9\n")  # contoh

with open(HASH_DB, "r") as f:
    KNOWN_HASHES = set(h.strip() for h in f if h.strip())

# Muat atau latih model
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    # Model dummy untuk demo
    X = np.random.rand(100, 2)
    y = np.random.randint(0, 2, 100)
    model = SVC(probability=True).fit(X, y)
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)

def calculate_entropy(data):
    if len(data) == 0:
        return 0
    freq = np.bincount(np.frombuffer(data, dtype=np.uint8), minlength=256)
    prob = freq / len(data)
    prob = prob[prob > 0]
    return -np.sum(prob * np.log2(prob))

def extract_features(filepath):
    with open(filepath, "rb") as f:
        data = f.read()
    size = len(data)
    entropy = calculate_entropy(data)
    return np.array([[size, entropy]])

def scan_file_ai(filepath):
    # Cek hash
    with open(filepath, "rb") as f:
        sha1 = hashlib.sha1(f.read()).hexdigest()
    if sha1 in KNOWN_HASHES:
        return {
            "status": "malicious",
            "confidence": 1.0,
            "reason": "Known malware hash"
        }
    
    # Prediksi AI
    features = extract_features(filepath)
    proba = model.predict_proba(features)[0]
    malware_score = proba[1]
    
    if malware_score > 0.7:
        return {
            "status": "malicious",
            "confidence": float(malware_score),
            "reason": "AI static analysis"
        }
    else:
        return {
            "status": "clean",
            "confidence": float(1 - malware_score),
            "reason": "No threat detected"
}
