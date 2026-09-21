// Use 127.0.0.1 by default: on Windows, localhost may resolve to IPv6 (::1) while uvicorn binds IPv4.
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export function getToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("propopuli_token");
}

export function setToken(token) {
  localStorage.setItem("propopuli_token", token);
}

export function clearToken() {
  localStorage.removeItem("propopuli_token");
}

export async function api(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch {
    throw new Error(
      `Cannot reach API at ${API_BASE}. Start the backend: cd backend, activate venv, uvicorn app.main:app --reload`
    );
  }
  const text = await res.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { detail: text };
    }
  }
  if (!res.ok) {
    const err = new Error(data?.detail?.detail || data?.detail || "Request failed");
    err.status = res.status;
    err.payload = data;
    throw err;
  }
  return data;
}
