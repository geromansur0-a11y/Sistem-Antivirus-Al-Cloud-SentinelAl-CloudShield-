// Ganti dengan URL backend produksi Anda
const API_BASE = "https://api.sentinelai.com"; // atau localhost saat dev

export const scanFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/scan/file`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error("Scan gagal");
  return res.json();
};

export const checkUrl = async (url) => {
  const res = await fetch(`${API_BASE}/scan/url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  return res.json();
};
