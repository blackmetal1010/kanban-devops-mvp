/**
 * API wrapper: authenticated fetch calls to the backend.
 * Redirects to login.html when the token is invalid/expired.
 */
const API = (() => {
  async function request(method, path, body = null) {
    if (!Auth.isLoggedIn()) {
      window.location.href = 'login.html';
      return;
    }
    const headers = {
      Authorization: `Bearer ${Auth.getToken()}`,
      'Content-Type': 'application/json',
    };
    const opts = { method, headers };
    if (body !== null) opts.body = JSON.stringify(body);

    let res;
    try {
      res = await fetch(path, opts);
    } catch (networkErr) {
      throw new Error('Network error — is the backend running?');
    }

    if (res.status === 401) {
      Auth.logout();
      window.location.href = 'login.html';
      return;
    }

    if (res.status === 204) return null;

    const data = await res.json().catch(() => null);
    if (!res.ok) {
      const detail = data?.detail;
      const msg = Array.isArray(detail)
        ? detail.map((e) => e.msg).join(', ')
        : detail || `HTTP ${res.status}`;
      throw new Error(msg);
    }
    return data;
  }

  return {
    get:    (path)         => request('GET',    path),
    post:   (path, body)   => request('POST',   path, body),
    put:    (path, body)   => request('PUT',    path, body),
    delete: (path)         => request('DELETE', path),
  };
})();
