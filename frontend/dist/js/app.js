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
    toggle.textContent = theme === 'dark' ? '☾ Тёмная' : '☀ Светлая';
    toggle.setAttribute(
      'aria-label',
      theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'
    );
  }
}

function initTheme() {
  const saved = localStorage.getItem('theme');
  const preferred = saved || 'light';
  applyTheme(preferred);

  const toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      const current =
        document.documentElement.getAttribute('data-theme') || 'light';
      const next = current === 'light' ? 'dark' : 'light';
      applyTheme(next);
    });
  }
}

/* === Ads handling (placeholder, позже привяжем к API) === */

function initAdSlots() {
  const adSlot = document.getElementById('ad-slot-main');
  if (!adSlot) return;

  const plan = localStorage.getItem('plan') || 'free';
  if (plan !== 'free') {
    adSlot.classList.add('ad-hidden');
    return;
  }

  // TODO: заменить на загрузку кода с бэкенда (панель администратора)
  adSlot.innerHTML =
    '<div class="ad-placeholder">Рекламный блок (настраивается в панели администратора для бесплатных аккаунтов)</div>';
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
    return await res.json();
  } catch (err) {
    showAlert(err.message);
    throw err;
  }
}

async function loginUser(username, password) {
  try {
    const body = new URLSearchParams();
    body.append('username', username);
    body.append('password', password);
    const res = await fetch(`${apiBase}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body
    });
    if (!res.ok) {
      const error = await res.text();
      throw new Error(error || 'Login failed');
    }
    return await res.json();
  } catch (err) {
    showAlert(err.message);
    throw err;
  }
}

// General API fetch function with authorization
async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('token');
  const headers = options.headers || {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(`${apiBase}${path}`, {
    ...options,
    headers
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(error || `Request to ${path} failed`);
  }
  return await res.json();
}

/* === Page initialization === */

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initAdSlots();

  // Detect if on auth page or dashboard
  const loginBox = document.getElementById('login-box');
  const dashboard = document.getElementById('content');

  if (loginBox) {
    initAuthPage();
  } else if (dashboard) {
    initDashboardPage();
  }
});

/* === Auth page logic === */

function initAuthPage() {
  const loginBtn = document.getElementById('login-btn');
  const registerBtn = document.getElementById('register-btn');
  const showRegister = document.getElementById('show-register');
  const showLogin = document.getElementById('show-login');
  const loginBox = document.getElementById('login-box');
  const registerBox = document.getElementById('register-box');

  // Переключение вкладок
  const tabLogin = document.getElementById('tab-login');
  const tabRegister = document.getElementById('tab-register');

  function activateLogin() {
    if (loginBox && registerBox) {
      loginBox.style.display = 'block';
      registerBox.style.display = 'none';
    }
    if (tabLogin && tabRegister) {
      tabLogin.classList.add('active');
      tabRegister.classList.remove('active');
    }
  }

  function activateRegister() {
    if (loginBox && registerBox) {
      loginBox.style.display = 'none';
      registerBox.style.display = 'block';
    }
    if (tabLogin && tabRegister) {
      tabLogin.classList.remove('active');
      tabRegister.classList.add('active');
    }
  }

  if (showRegister) {
    showRegister.addEventListener('click', (e) => {
      e.preventDefault();
      activateRegister();
    });
  }
  if (showLogin) {
    showLogin.addEventListener('click', (e) => {
      e.preventDefault();
      activateLogin();
    });
  }
  if (tabLogin) {
    tabLogin.addEventListener('click', activateLogin);
  }
  if (tabRegister) {
    tabRegister.addEventListener('click', activateRegister);
  }

  // По умолчанию показываем логин
  activateLogin();

  // Handle login
  if (loginBtn) {
    loginBtn.addEventListener('click', async () => {
      const username = document.getElementById('login-username').value.trim();
      const password = document.getElementById('login-password').value.trim();
      if (!username || !password) {
        showAlert('Please enter both username and password');
        return;
      }
      try {
        const data = await loginUser(username, password);
        localStorage.setItem('token', data.access_token);
        // Здесь можно позже сохранять план (free/pro) из профиля
        window.location.href = 'dashboard.html';
      } catch (err) {
        console.error(err);
      }
    });
  }

  // Handle registration
  if (registerBtn) {
    registerBtn.addEventListener('click', async () => {
      const username = document
        .getElementById('register-username')
        .value.trim();
      const email = document.getElementById('register-email').value.trim();
      const password = document
        .getElementById('register-password')
        .value.trim();

      if (!username || !email || !password) {
        showAlert('Please fill out all fields');
        return;
      }
      try {
        await registerUser(username, email, password);
        // Auto-login after registration
        const data = await loginUser(username, password);
        localStorage.setItem('token', data.access_token);
        window.location.href = 'dashboard.html';
      } catch (err) {
        console.error(err);
      }
    });
  }
}

/* === Dashboard logic === */

function initDashboardPage() {
  // Check if logged in
  const token = localStorage.getItem('token');
  if (!token) {
    window.location.href = 'index.html';
    return;
  }

  // Navigation
  const navLinks = document.querySelectorAll('.nav-links a[data-page]');
  navLinks.forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      navLinks.forEach((l) => l.classList.remove('active'));
      document.querySelectorAll('.page').forEach((page) => {
        page.classList.remove('active');
      });
      link.classList.add('active');
      const pageId = `page-${link.dataset.page}`;
      const page = document.getElementById(pageId);
      if (page) {
        page.classList.add('active');
      }
    });
  });

  // AI page
  const aiBtn = document.getElementById('ai-ask-btn');
  if (aiBtn) {
    aiBtn.addEventListener('click', async () => {
      const query = document.getElementById('ai-query').value.trim();
      const responseEl = document.getElementById('ai-response');
      if (!query) {
        showAlert('Please enter your legal question.');
        return;
      }
      responseEl.textContent = 'Processing...';
      try {
        const data = await apiFetch('/ai/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ query })
        });
        responseEl.textContent = data.answer || 'No answer received.';
      } catch (err) {
        console.error(err);
        showAlert(err.message);
        responseEl.textContent = 'Error while processing your request.';
      }
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
          li.textContent = t.name;
          list.appendChild(li);
        });
      } catch (err) {
        console.error(err);
        showAlert(err.message);
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
          li.textContent = c.title;
          list.appendChild(li);
        });
      } catch (err) {
        console.error(err);
        showAlert(err.message);
      }
    });
  }

  // Profile page
  const profileInfo = document.getElementById('profile-info');
  if (profileInfo) {
    (async () => {
      try {
        const profile = await apiFetch('/auth/profile');
        profileInfo.textContent = `Username: ${profile.username} | Email: ${profile.email}`;
        // TODO: здесь позже можно показать план (free/pro) и кнопки апгрейда
      } catch (err) {
        console.error(err);
        showAlert(err.message);
      }
    })();
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
}
