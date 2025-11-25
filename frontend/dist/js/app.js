// Simple frontend logic for LegalAI application

const apiBase = 'https://api.legalai.su';

// Utility function to show a message in case of errors
function showAlert(message) {
  alert(message);
}

/* === Theme handling === */

function applyTheme(theme) {
  const root = document.documentElement;
  const toggle = document.getElementById('theme-toggle');

  root.setAttribute('data-theme', theme);
  if (toggle) {
    toggle.checked = theme === 'dark';
  }
  localStorage.setItem('theme', theme);
}

function initTheme() {
  const saved = localStorage.getItem('theme');
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = saved || (prefersDark ? 'dark' : 'light');
  applyTheme(theme);

  const toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('change', () => {
      applyTheme(toggle.checked ? 'dark' : 'light');
    });
  }
}

/* === Token handling === */

function getAuthToken() {
  try {
    return localStorage.getItem('token');
  } catch {
    return null;
  }
}

function setAuthToken(token) {
  try {
    localStorage.setItem('token', token);
  } catch {
    // ignore storage errors
  }
}

/* === API helper === */

async function apiFetch(path, options = {}) {
  const url = `${apiBase}${path}`;
  const token = getAuthToken();

  const headers = options.headers || {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  headers['Accept'] = 'application/json';

  const res = await fetch(url, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errorDetail = `Request failed with status ${res.status}`;
    try {
      const data = await res.json();
      if (data && data.detail) {
        errorDetail = Array.isArray(data.detail)
          ? data.detail.map((d) => d.msg || d.message || d).join('; ')
          : data.detail;
      }
    } catch {
      // ignore JSON parse error
    }
    throw new Error(errorDetail);
  }

  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return res.json();
  }
  return res.text();
}

/* === Authentication functions === */

async function registerUser(username, email, password) {
  try {
    const res = await fetch(`${apiBase}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, email, password })
    });
    if (!res.ok) {
      const error = await res.text();
      throw new Error(error || 'Registration failed');
    }
    showAlert('Registration successful. You can now log in.');
    window.location.href = 'login.html';
  } catch (err) {
    console.error(err);
    showAlert(err.message);
  }
}

// ИСПРАВЛЕНО: логин теперь отправляет данные в формате x-www-form-urlencoded,
// как реально ждёт backend (OAuth2PasswordRequestForm: username + password).
async function loginUser(login, password) {
  try {
    // Формируем тело запроса: username и password
    const body = new URLSearchParams();
    body.append('username', login);
    body.append('password', password);

    const res = await fetch(`${apiBase}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body,
    });

    if (!res.ok) {
      const error = await res.text();
      throw new Error(error || 'Login failed');
    }
    const data = await res.json();
    setAuthToken(data.access_token);
    window.location.href = 'dashboard.html';
  } catch (err) {
    console.error(err);
    showAlert(err.message);
  }
}

/* === Initialization on DOMContentLoaded === */

document.addEventListener('DOMContentLoaded', () => {
  // Theme init
  initTheme();

  // Registration page
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const username = document.getElementById('reg-username').value.trim();
      const email = document.getElementById('reg-email').value.trim();
      const password = document.getElementById('reg-password').value.trim();
      if (!username || !email || !password) {
        showAlert('Please fill in all fields.');
        return;
      }
      registerUser(username, email, password);
    });
  }

  // Login page
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value.trim();
      const password = document.getElementById('login-password').value.trim();
      if (!email || !password) {
        showAlert('Please enter email and password.');
        return;
      }
      // email/логин передаём как login → на бэкенд идёт в поле username
      loginUser(email, password);
    });
  }

  // Simple router for sidebar links (if present)
  const navLinks = document.querySelectorAll('[data-nav]');
  const pages = document.querySelectorAll('[data-page]');
  if (navLinks.length && pages.length) {
    navLinks.forEach((link) => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const target = link.getAttribute('data-nav');
        pages.forEach((page) => {
          page.classList.toggle('active', page.getAttribute('data-page') === target);
        });
        navLinks.forEach((l) => l.classList.remove('active'));
        link.classList.add('active');
      });
    });
  }

  // Documents page
  const loadTemplatesBtn = document.getElementById('load-templates-btn');
  if (loadTemplatesBtn) {
    loadTemplatesBtn.addEventListener('click', async () => {
      const list = document.getElementById('templates-list');
      list.innerHTML = 'Loading...';
      try {
        const templates = await apiFetch('/documents/templates');
        if (!Array.isArray(templates)) {
          list.innerHTML = 'No templates found.';
          return;
        }
        list.innerHTML = templates
          .map((t) => `<li>${t.name || t.id}</li>`)
          .join('');
      } catch (err) {
        console.error(err);
        list.innerHTML = 'Error loading templates.';
      }
    });
  }

  const loadCasesBtn = document.getElementById('load-cases-btn');
  if (loadCasesBtn) {
    loadCasesBtn.addEventListener('click', async () => {
      const list = document.getElementById('cases-list');
      list.innerHTML = 'Loading...';
      try {
        const cases = await apiFetch('/legal-cases/search?query=example');
        if (!Array.isArray(cases)) {
          list.innerHTML = 'No cases found.';
          return;
        }
        list.innerHTML = cases
          .map((c) => `<li>${c.title || c.id}</li>`)
          .join('');
      } catch (err) {
        console.error(err);
        list.innerHTML = 'Error loading cases.';
      }
    });
  }

  // Dashboard page: базовый хук для будущего чата Татьяны
  // (здесь позже подключим единый чат к /ai/ask)
  const dashboardEl = document.querySelector('[data-page="dashboard"]');
  if (dashboardEl) {
    // Точка расширения: сюда будем добавлять логику чата
    console.log('Dashboard loaded: ready for Tatiana chat integration.');
  }

  // Logout
  const logoutLink = document.getElementById('logout-link');
  if (logoutLink) {
    logoutLink.addEventListener('click', (e) => {
      e.preventDefault();
      localStorage.removeItem('token');
      window.location.href = 'index.html';
    });
  }
});
