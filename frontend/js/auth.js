/**
 * Auth module: handles JWT storage and login/logout/register
 */
const Auth = (() => {
  const TOKEN_KEY = 'kanban_token';
  const USER_KEY  = 'kanban_user';

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function isLoggedIn() {
    const token = getToken();
    if (!token) return false;
    try {
      // Decode payload (no verification — just check expiry client-side)
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 > Date.now();
    } catch {
      return false;
    }
  }

  function getUser() {
    try {
      return JSON.parse(localStorage.getItem(USER_KEY) || 'null');
    } catch {
      return null;
    }
  }

  async function login(username, password) {
    const body = new URLSearchParams({ username, password });
    const res = await fetch('/api/auth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString(),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || `HTTP ${res.status}`);
    }
    const data = await res.json();
    localStorage.setItem(TOKEN_KEY, data.access_token);

    // Fetch and cache user info
    const meRes = await fetch('/api/auth/me', {
      headers: { Authorization: `Bearer ${data.access_token}` },
    });
    if (meRes.ok) {
      const user = await meRes.json();
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
    return data;
  }

  async function register(username, email, password) {
    const params = new URLSearchParams({ username, email, password });
    const res = await fetch(`/api/auth/register?${params}`, { method: 'POST' });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || `HTTP ${res.status}`);
    }
    return res.json();
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  return { getToken, isLoggedIn, getUser, login, register, logout };
})();
