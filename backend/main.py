import os
import re
import tempfile
import hashlib
import time
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# --- Konfigurasi ---
IOC_DIR = "iocs"
RATE_LIMIT = "10/minute"

# --- Load IOCs ---
def load_iocs():
    def read_lines(filename):
        path = os.path.join(IOC_DIR, filename)
        if not os.path.exists(path):
            return set()
        with open(path, "r") as f:
            return {line.strip().lower() for line in f if line.strip()}
    
    return {
        "hashes": read_lines("hashes.txt"),
        "bad_strings": read_lines("bad_strings.txt"),
        "bad_extensions": read_lines("bad_extensions.txt")
    }

IOCS = load_iocs()

# --- Inisialisasi FastAPI ---
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="CloudShield Pro")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def compute_hash(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def has_bad_extension(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in IOCS["bad_extensions"]

def check_bad_strings(file_path: str, max_size_mb=5) -> list:
    """Cek string berbahaya dalam file (hanya file <5MB)"""
    file_size = os.path.getsize(file_path)
    if file_size > max_size_mb * 1024 * 1024:
        return []
    
    bad_found = []
    try:
        with open(file_path, "rb") as f:
            content = f.read()
            # Coba decode sebagai teks
            text = content.decode("utf-8", errors="ignore").lower()
            for bad_str in IOCS["bad_strings"]:
                if bad_str in text:
                    bad_found.append(bad_str)
    except Exception:
        pass
    return bad_found

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("../static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.post("/scan")
@limiter.limit(RATE_LIMIT)
async def scan_file(request: Request, file: UploadFile = File(...)):
    findings = []
    risk = "low"

    # Cek ekstensi
    if has_bad_extension(file.filename):
        findings.append(f"Ekstensi berbahaya: {os.path.splitext(file.filename)[1]}")
        risk = "high"

    # Simpan file sementara
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Cek hash
        file_hash = compute_hash(tmp_path)
        if file_hash in IOCS["hashes"]:
            findings.append("Hash file cocok dengan malware dikenal")
            risk = "critical"

        # Cek string berbahaya (jika belum critical)
        if risk != "critical":
            bad_strings = check_bad_strings(tmp_path)
            for s in bad_strings:
                findings.append(f"String mencurigakan ditemukan: '{s}'")
            if bad_strings:
                risk = "medium" if risk == "low" else risk

        return {
            "filename": file.filename,
            "hash": file_hash,
            "malicious": len(findings) > 0,
            "findings": findings,
            "risk": risk,
            "scan_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "file_size": os.path.getsize(tmp_path)
        }
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
