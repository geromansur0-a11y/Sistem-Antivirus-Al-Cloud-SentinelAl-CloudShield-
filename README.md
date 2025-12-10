# 🛡️ CloudShield AI – Antivirus Cloud Berbasis Browser

Sistem antivirus berbasis cloud dengan deteksi AI. Upload file via browser → scan di server → hasil real-time.

> ⚠️ **Peringatan**: Ini adalah proyek edukatif. Jangan digunakan untuk proteksi keamanan nyata tanpa audit dan sandbox lengkap.

---

## 🚀 Fitur
- Upload file via drag & drop
- Deteksi berbasis:
  - Hash malware (blacklist)
  - AI statis (ukuran + entropy + model ML)
- Hasil real-time di browser
- Arsitektur cloud-ready (Docker + FastAPI + React/Vite)

---

## 🛠️ Instalasi

### Prasyarat
- Python 3.9+
- Node.js 18+
- Docker (opsional)

### Jalankan Langsung (Tanpa Docker)
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
