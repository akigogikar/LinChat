import axios from 'axios';

export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function friendlyMessage(msg) {
  if (!msg) return 'An unexpected error occurred.';
  if (msg.length > 200 || /traceback/i.test(msg)) {
    return 'An unexpected error occurred.';
  }
  return msg;
}

async function fetchJson(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) {
    let msg;
    try {
      const data = await res.json();
      msg = data.detail || data.message;
    } catch {
      msg = await res.text();
    }
    throw new Error(friendlyMessage(msg));
  }
  return res.json();
}

export async function queryLLM(prompt, sessionId) {
  return fetchJson(`${API_BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, session_id: sessionId })
  });
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
    const msg = err.response?.data?.detail || err.response?.data?.message || err.message;
    throw new Error(friendlyMessage(msg));
  }
}

export async function generateTable(prompt) {
  return fetchJson(`${API_BASE}/generate_table`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  });
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
    const msg = err.response?.data?.detail || err.response?.data?.message || err.message;
    throw new Error(friendlyMessage(msg));
  }
}

export async function analysisResults(file, onProgress) {
  const form = new FormData();
  form.append('file', file);
  try {
    const res = await axios.post(`${API_BASE}/analysis/results`, form, {
      onUploadProgress: e => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total));
        }
      }
    });
    return res.data;
  } catch (err) {
    const msg = err.response?.data?.detail || err.response?.data?.message || err.message;
    throw new Error(friendlyMessage(msg));
  }
}

export async function getCitation(reqId, cid) {
  return fetchJson(`${API_BASE}/source/${reqId}/${cid}`);
}

export async function exportPdf(content) {
  const res = await fetch(`${API_BASE}/export/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content })
  });
  if (!res.ok) {
    let msg;
    try { msg = await res.text(); } catch { msg = ''; }
    throw new Error(friendlyMessage(msg));
  }
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

export async function createChatSession() {
  return fetchJson(`${API_BASE}/chat/sessions`, { method: 'POST' });
}

export async function getWorkspaces() {
  return fetchJson(`${API_BASE}/workspaces`);
}

export async function loginUser(username, password) {
  return fetchJson(`${API_BASE}/auth/jwt/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
}

export async function registerUser(user) {
  return fetchJson(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user)
  });
}


export async function getDocuments() {
  return fetchJson(`${API_BASE}/documents`);
}

export async function deleteDocument(id) {
  return fetchJson(`${API_BASE}/documents/${id}`, { method: 'DELETE' });
}


export async function setShared(id, shared) {
  return fetchJson(`${API_BASE}/documents/${id}/share?shared=${shared}`, { method: 'POST' });
}

export async function getAdminData() {
  return fetchJson(`${API_BASE}/admin/data`);
}

export async function setApiKey(key, model) {
  const form = new FormData();
  form.append('key', key);
  if (model) form.append('model', model);
  return fetchJson(`${API_BASE}/admin/set_key`, { method: 'POST', body: form });
}

export async function inviteUser(email, teamId) {
  const form = new FormData();
  form.append('email', email);
  if (teamId) form.append('team_id', teamId);
  return fetchJson(`${API_BASE}/admin/invite`, { method: 'POST', body: form });
}

export async function resetPassword(userId) {
  const form = new FormData();
  form.append('user_id', userId);
  return fetchJson(`${API_BASE}/admin/reset_password`, { method: 'POST', body: form });
}

export async function createWorkspace(name) {
  const form = new FormData();
  form.append('name', name);
  return fetchJson(`${API_BASE}/admin/workspaces`, { method: 'POST', body: form });
}

export async function deleteWorkspace(id) {
  return fetchJson(`${API_BASE}/admin/workspaces/${id}`, { method: 'DELETE' });
}

export async function assignWorkspace(userId, teamId) {
  const form = new FormData();
  form.append('team_id', teamId);
  return fetchJson(`${API_BASE}/users/${userId}/workspace`, {
    method: 'POST',
    body: form,
  });
}

export async function customAnalysis(prompt, file, onProgress) {
  const form = new FormData();
  form.append('file', file);
  try {
    const res = await axios.post(
      `${API_BASE}/custom_analysis?prompt=${encodeURIComponent(prompt)}`,
      form,
      {
        onUploadProgress: e => {
          if (onProgress && e.total) {
            onProgress(Math.round((e.loaded * 100) / e.total));
          }
        }
      }
    );
    const chart = res.headers['chart'];
    return { data: res.data, chart };
  } catch (err) {
    const msg = err.response?.data?.detail || err.response?.data?.message || err.message;
    throw new Error(friendlyMessage(msg));
  }
}
