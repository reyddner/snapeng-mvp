/**
 * Autenticação SNAPENG via cookies HttpOnly (credentials: include).
 * Arquivo: frontend/static/js/auth.js
 */
(function (window) {
  const LEGACY_ACCESS = "access_token";
  const LEGACY_REFRESH = "refresh_token";

  function clearLegacyTokens() {
    try {
      localStorage.removeItem(LEGACY_ACCESS);
      localStorage.removeItem(LEGACY_REFRESH);
    } catch (_) {
      /* ignore */
    }
  }

  // Limpa tokens antigos no boot (migração F4→sessão cookie).
  clearLegacyTokens();

  async function refreshTokens() {
    const response = await fetch("/api/v1/auth/refresh", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    if (!response.ok) return false;
    return true;
  }

  async function authFetch(url, options = {}) {
    const headers = Object.assign({}, options.headers || {});
    let response = await fetch(
      url,
      Object.assign({}, options, { headers, credentials: "include" })
    );
    if (response.status !== 401) return response;

    const refreshed = await refreshTokens();
    if (!refreshed) return response;
    return fetch(
      url,
      Object.assign({}, options, { headers, credentials: "include" })
    );
  }

  async function getCurrentUser() {
    const response = await authFetch("/api/v1/auth/me");
    if (!response.ok) return null;
    return response.json();
  }

  async function hasSession() {
    return Boolean(await getCurrentUser());
  }

  async function logout(redirectTo) {
    try {
      await fetch("/api/v1/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (_) {
      /* ignore */
    }
    clearLegacyTokens();
    window.location.href = redirectTo || "/";
  }

  window.SnapEngAuth = {
    // Mantidos por compatibilidade; sessão real é cookie HttpOnly.
    getAccessToken: function () {
      return null;
    },
    getRefreshToken: function () {
      return null;
    },
    setTokens: function () {
      clearLegacyTokens();
    },
    clearTokens: clearLegacyTokens,
    refreshTokens,
    authFetch,
    getCurrentUser,
    hasSession,
    logout,
  };
})(window);
