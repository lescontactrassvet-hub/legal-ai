// Simple frontend logic for LegalAI application

const apiBase = 'https://api.legalai.su';

// Utility function to show a message in case of errors
function showAlert(message) {
  alert(message);
}

// Authentication functions
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

// Page initialization
document.addEventListener('DOMContentLoaded', () => {
  // Detect if on auth page or dashboard
  const loginBox = document.getElementById('login-box');
  const dashboard = document.getElementById('content');

  if (loginBox) {
    // Auth page logic
    initAuthPage();
  } else if (dashboard) {
    // Dashboard page logic
    initDashboardPage();
  }
});

function initAuthPage() {
  const loginBtn = document.getElementById('login-btn');
  const registerBtn = document.getElementById('register-btn');
  const showRegister = document.getElementById('show-register');
  const showLogin = document.getElementById('show-login');
  const loginBox = document.getElementById('login-box');
  const registerBox = document.getElementById('register-box');

  // Toggle between login and register
  showRegister.addEventListener('click', (e) => {
    e.preventDefault();
    loginBox.style.display = 'none';
    registerBox.style.display = 'block';
  });
  showLogin.addEventListener('click', (e) => {
    e.preventDefault();
    registerBox.style.display = 'none';
    loginBox.style.display = 'block';
  });

  // Handle login
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
      window.location.href = 'dashboard.html';
    } catch (err) {
      console.error(err);
    }
  });

  // Handle registration
  registerBtn.addEventListener('click', async () => {
    const username = document.getElementById('register-username').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value.trim();
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

function initDashboardPage() {
  // Check if logged in
  const token = localStorage.getItem('token');
  if (!token) {
    window.location.href = 'index.html';
    return;
  }

  // Navigation
  const navLinks = document.querySelectorAll('.nav-links a[data-page]');
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      // Remove active class from all links
      navLinks.forEach(l => l.classList.remove('active'));
      // Hide all pages
      document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
      // Activate the clicked link
      link.classList.add('active');
      const pageId = 'page-' + link.getAttribute('data-page');
      document.getElementById(pageId).classList.add('active');
      // Load content if necessary
      if (pageId === 'page-profile') {
        loadProfile();
      }
    });
  });

  // Logout handler
  document.getElementById('logout-link').addEventListener('click', (e) => {
    e.preventDefault();
    localStorage.removeItem('token');
    window.location.href = 'index.html';
  });

  // AI ask handler
  const askBtn = document.getElementById('ai-ask-btn');
  if (askBtn) {
    askBtn.addEventListener('click', async () => {
      const query = document.getElementById('ai-query').value.trim();
      if (!query) {
        showAlert('Please enter your question');
        return;
      }
      try {
        const data = await apiFetch('/ai/ask', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ query })
        });
        const resDiv = document.getElementById('ai-response');
        resDiv.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        showAlert(err.message);
      }
    });
  }

  // Load templates
  const loadTemplatesBtn = document.getElementById('load-templates-btn');
  if (loadTemplatesBtn) {
    loadTemplatesBtn.addEventListener('click', async () => {
      try {
        const templates = await apiFetch('/docs/templates');
        const list = document.getElementById('templates-list');
        list.innerHTML = '';
        templates.forEach(t => {
          const li = document.createElement('li');
          li.textContent = t;
          list.appendChild(li);
        });
      } catch (err) {
        showAlert(err.message);
      }
    });
  }

  // Load cases
  const loadCasesBtn = document.getElementById('load-cases-btn');
  if (loadCasesBtn) {
    loadCasesBtn.addEventListener('click', async () => {
      try {
        const cases = await apiFetch('/legal-cases');
        const list = document.getElementById('cases-list');
        list.innerHTML = '';
        cases.forEach(c => {
          const li = document.createElement('li');
          li.textContent = JSON.stringify(c);
          list.appendChild(li);
        });
      } catch (err) {
        showAlert(err.message);
      }
    });
  }

  // Load profile
  async function loadProfile() {
    try {
      const profile = await apiFetch('/auth/profile');
      const infoDiv = document.getElementById('profile-info');
      infoDiv.textContent = JSON.stringify(profile, null, 2);
    } catch (err) {
      showAlert(err.message);
    }
  }

  // Load default profile if profile page is initial active
  const activePage = document.querySelector('.page.active');
  if (activePage && activePage.id === 'page-profile') {
    loadProfile();
  }
}
