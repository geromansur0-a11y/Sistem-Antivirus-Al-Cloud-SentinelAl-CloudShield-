// static/app.js
class CloudShieldPro {
  constructor() {
    this.isDark = localStorage.getItem('darkMode') === 'true';
    this.history = JSON.parse(localStorage.getItem('scanHistory') || '[]');
    this.init();
  }

  init() {
    this.applyTheme();
    document.getElementById('themeToggle').addEventListener('click', () => this.toggleTheme());
    document.getElementById('scanBtn').addEventListener('click', () => this.scan());
    this.renderHistory();
  }

  applyTheme() {
    if (this.isDark) {
      document.body.classList.add('dark');
      document.getElementById('themeToggle').textContent = '☀️';
    } else {
      document.body.classList.remove('dark');
      document.getElementById('themeToggle').textContent = '🌙';
    }
  }

  toggleTheme() {
    this.isDark = !this.isDark;
    localStorage.setItem('darkMode', this.isDark);
    this.applyTheme();
  }

  async scan() {
    const file = document.getElementById('fileInput').files[0];
    if (!file) return alert('Pilih file dulu!');

    const btn = document.getElementById('scanBtn');
    btn.disabled = true;
    btn.textContent = 'Memindai...';

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/scan', {
        method: 'POST',
        body: formData,
        headers: { 'X-Forwarded-For': '127.0.0.1' }
      });

      if (res.status === 429) {
        alert('Terlalu banyak scan! Tunggu 1 menit.');
        return;
      }

      const data = await res.json();
      this.showResult(data);
      this.saveToHistory(data);
    } catch (err) {
      alert('Error: ' + err.message);
    } finally {
      btn.disabled = false;
      btn.textContent = 'Scan File';
    }
  }

  showResult(data) {
    const riskColor = { low: 'green', medium: 'orange', high: 'red', critical: 'darkred' };
    const status = data.malicious 
      ? `<span style="color:${riskColor[data.risk]}">⚠️ ${data.risk.toUpperCase()}</span>`
      : `<span style="color:green">✅ AMAN</span>`;

    const findingsHtml = data.findings.length 
      ? `<ul>${data.findings.map(f => `<li>${f}</li>`).join('')}</ul>`
      : '<p>Tidak ada ancaman ditemukan.</p>';

    document.getElementById('result').innerHTML = `
      <div class="result">
        <h3>🔍 Hasil Analisis</h3>
        <p><strong>File:</strong> ${data.filename}</p>
        <p><strong>Status:</strong> ${status}</p>
        <p><strong>Ukuran:</strong> ${(data.file_size / 1024).toFixed(1)} KB</p>
        <p><strong>Hash:</strong> ${data.hash?.substring(0, 16)}...</p>
        <h4>Temuan:</h4>
        ${findingsHtml}
        <button onclick="cloudshield.exportPDF(${JSON.stringify(data)})">📄 Simpan sebagai PDF</button>
        <button onclick="cloudshield.exportJSON(${JSON.stringify(data)})">💾 Simpan sebagai JSON</button>
      </div>
    `;
  }

  exportPDF(data) {
    // Gunakan browser print-to-PDF
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html><head><title>Laporan CloudShield</title></head><body>
        <h2>CloudShield Pro - Laporan Scan</h2>
        <p><strong>File:</strong> ${data.filename}</p>
        <p><strong>Status:</strong> ${data.malicious ? 'BERBAHAYA' : 'AMAN'}</p>
        <p><strong>Risiko:</strong> ${data.risk}</p>
        <p><strong>Waktu:</strong> ${data.scan_time}</p>
        <h3>Temuan:</h3>
        <ul>${data.findings.map(f => `<li>${f}</li>`).join('')}</ul>
        <p><em>Dibuat di CloudShield Pro - ${new Date().toLocaleString()}</em></p>
      </body></html>
    `);
    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
    printWindow.close();
  }

  exportJSON(data) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cloudshield-report-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  saveToHistory(scan) {
    this.history.unshift({ ...scan, timestamp: new Date().toISOString() });
    this.history = this.history.slice(0, 10);
    localStorage.setItem('scanHistory', JSON.stringify(this.history));
    this.renderHistory();
  }

  renderHistory() {
    const container = document.getElementById('historyList');
    if (!container) return;
    container.innerHTML = `
      <h3>Riwayat Scan</h3>
      ${this.history.map(item => `
        <div class="history-item">
          <span class="${item.malicious ? 'malicious' : 'safe'}">${item.malicious ? '❌' : '✅'}</span>
          ${item.filename} <small>(${new Date(item.timestamp).toLocaleTimeString()})</small>
        </div>
      `).join('')}
    `;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.cloudshield = new CloudShieldPro();
});
