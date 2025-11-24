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
  localStorage.setItem('theme', theme);

  if (toggle) {
    toggle.textContent = theme === 'dark' ? '🌙' : '☀️';
  }
}

function initTheme() {
  const saved = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = saved || (prefersDark ? 'dark' : 'light');
  applyTheme(theme);

  const toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next);
    });
  }
}

/* === Basic auth helpers === */

function getAuthToken() {
  return localStorage.getItem('token');
}

function setAuthToken(token) {
  localStorage.setItem('token', token);
}

async function apiFetch(path, options = {}) {
  const token = getAuthToken();
  const headers = options.headers || {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${apiBase}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errorDetail = `Request failed with status ${res.status}`;
    try {
      const data = await res.json();
      if (data.detail) errorDetail = data.detail;
    } catch (e) {
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

async function loginUser(email, password) {
  try {
    const res = await fetch(`${apiBase}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username: email, password })
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

/* === DOMContentLoaded init === */

document.addEventListener('DOMContentLoaded', () => {
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
        list.innerHTML = '';
        templates.forEach((t) => {
          const li = document.createElement('li');
          li.textContent = `${t.name} (${t.category})`;
          list.appendChild(li);
        });
      } catch (err) {
        console.error(err);
        showAlert(err.message);
        list.innerHTML = 'Error loading templates.';
      }
    });
  }

  // Cases page
  const loadCasesBtn = document.getElementById('load-cases-btn');
  if (loadCasesBtn) {
    loadCasesBtn.addEventListener('click', async () => {
      const list = document.getElementById('cases-list');
      list.innerHTML = 'Loading...';
      try {
        const cases = await apiFetch('/cases');
        list.innerHTML = '';
        cases.forEach((c) => {
          const li = document.createElement('li');
          li.textContent = `${c.case_number}: ${c.title}`;
          list.appendChild(li);
        });
      } catch (err) {
        console.error(err);
        showAlert(err.message);
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
