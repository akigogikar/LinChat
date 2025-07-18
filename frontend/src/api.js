export async function queryLLM(prompt) {
  const res = await fetch('/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function uploadFile(file, shared=false) {
  const form = new FormData();
  form.append('file', file);
  form.append('shared', shared);
  const res = await fetch('/upload', { method: 'POST', body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function generateTable(prompt) {
  const res = await fetch('/generate_table', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function analyzeFile(file) {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch('http://localhost:8001/analysis', { method: 'POST', body: form });
  if (!res.ok) throw new Error(await res.text());
  const chart = res.headers.get('Chart');
  const data = await res.json();
  return { data, chart };
}

export async function getCitation(reqId, cid) {
  const res = await fetch(`/source/${reqId}/${cid}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function exportPdf(content) {
  const res = await fetch('/export/pdf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content })
  });
  if (!res.ok) throw new Error(await res.text());
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

export async function loginUser(username, password) {
  const res = await fetch('/auth/jwt/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username, password })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function registerUser(user) {
  const res = await fetch('/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
