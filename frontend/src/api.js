import axios from 'axios';

export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';


export async function queryLLM(prompt, sessionId) {
  const res = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, session_id: sessionId })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function uploadFile(file, shared = false, onProgress) {
  const form = new FormData();
  form.append('file', file);
  form.append('shared', shared);
  try {
    const res = await axios.post(`${API_BASE}/upload`, form, {
      onUploadProgress: e => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total));
        }
      }
    });
    return res.data;
  } catch (err) {
    const msg = err.response?.data?.detail || err.message;
    throw new Error(msg);
  }
}

export async function generateTable(prompt) {
  const res = await fetch(`${API_BASE}/generate_table`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function analyzeFile(file, onProgress) {
  const form = new FormData();
  form.append('file', file);
  try {
    const res = await axios.post('http://localhost:8001/analysis', form, {
      onUploadProgress: e => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total));
        }
      }
    });
    const chart = res.headers['chart'];
    return { data: res.data, chart };
  } catch (err) {
    const msg = err.response?.data?.detail || err.message;
    throw new Error(msg);
  }
}

export async function getCitation(reqId, cid) {
  const res = await fetch(`${API_BASE}/source/${reqId}/${cid}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function exportPdf(content) {
  const res = await fetch(`${API_BASE}/export/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content })
  });
  if (!res.ok) throw new Error(await res.text());
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

export async function createChatSession() {
  const res = await fetch(`${API_BASE}/chat/sessions`, { method: 'POST' });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getWorkspaces() {
  const res = await fetch(`${API_BASE}/workspaces`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function loginUser(username, password) {
  const res = await fetch(`${API_BASE}/auth/jwt/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function registerUser(user) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}


export async function getDocuments() {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function deleteDocument(id) {
  const res = await fetch(`${API_BASE}/documents/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}


export async function setShared(id, shared) {
  const res = await fetch(`${API_BASE}/documents/${id}/share?shared=${shared}`, { method: 'POST' });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getAdminData() {
  const res = await fetch(`${API_BASE}/admin/data`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function setApiKey(key, model) {
  const form = new FormData();
  form.append('key', key);
  if (model) form.append('model', model);
  const res = await fetch(`${API_BASE}/admin/set_key`, { method: 'POST', body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function inviteUser(email, teamId) {
  const form = new FormData();
  form.append('email', email);
  if (teamId) form.append('team_id', teamId);
  const res = await fetch(`${API_BASE}/admin/invite`, { method: 'POST', body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function resetPassword(userId) {
  const form = new FormData();
  form.append('user_id', userId);
  const res = await fetch(`${API_BASE}/admin/reset_password`, { method: 'POST', body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function createWorkspace(name) {
  const form = new FormData();
  form.append('name', name);
  const res = await fetch(`${API_BASE}/admin/workspaces`, { method: 'POST', body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function deleteWorkspace(id) {
  const res = await fetch(`${API_BASE}/admin/workspaces/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function assignWorkspace(userId, teamId) {
  const form = new FormData();
  form.append('team_id', teamId);
  const res = await fetch(`${API_BASE}/users/${userId}/workspace`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
