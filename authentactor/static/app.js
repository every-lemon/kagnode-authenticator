"use strict";
const paths = {
  shield:
    '<path d="M12 3 21 7v5c0 5-6 8-9 10-3-2-9-5-9-10V7Z"/><path d="m8 12 3 3 5-6"/>',
  lock: '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3"/>',
  key: '<circle cx="8" cy="9" r="5"/><path d="m11.5 12.5 9 9M16 17l3-3M19 20l3-3"/>',
  layout:
    '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18M9 9h12"/>',
  fingerprint:
    '<path d="M5 12a7 7 0 0 1 14 0c0 4-1 7-3 9M3 16c0-2 0-4 .5-6M7 20c2-2 2-5 2-8a3 3 0 0 1 6 0c0 4-1 6-2 8M11 22c2-4 2-8 2-10M4 7a10 10 0 0 1 17 5c0 2 0 4-1 6M5 21c1-2 2-5 2-8"/>',
  star: '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9Z"/>',
  sparkles:
    '<path d="m12 3 2.6 6.4L21 12l-6.4 2.6L12 21l-2.6-6.4L3 12l6.4-2.6ZM20 2v4M18 4h4M4 19v3M2.5 20.5h3"/>',
  "shield-check":
    '<path d="m12 3 9 4v5c0 5-6 8-9 10-3-2-9-5-9-10V7Z"/><path d="m8 12 3 3 5-6"/>',
  settings:
    '<path d="m9 3-.6 3-2 .9L3.5 6l-2 3.5L4 11v2l-2.5 1.5 2 3.5 2.9-.9 2 .9.6 3h4l.6-3 2-.9 2.9.9 2-3.5L20 13v-2l2.5-1.5-2-3.5-2.9.9-2-.9L15 3Z"/><circle cx="12" cy="12" r="3"/>',
  server:
    '<rect x="3" y="3" width="18" height="7" rx="2"/><rect x="3" y="14" width="18" height="7" rx="2"/><path d="M7 6.5h.01M7 17.5h.01M11 6.5h6M11 17.5h6"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  "arrow-right": '<path d="M4 12h16m-6-6 6 6-6 6"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7h.01"/>',
  flask:
    '<path d="M9 3h6M10 3v6L4 19c-.5 1 0 2 1 2h14c1 0 1.5-1 1-2L14 9V3M7 15h10"/>',
  layers: '<path d="m12 3 10 5-10 5L2 8Zm-10 9 10 5 10-5M2 16l10 5 10-5"/>',
  search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
  grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
  list: '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
  copy: '<rect x="8" y="8" width="13" height="13" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/>',
  eye: '<path d="M2 12c5-9 15-9 20 0-5 9-15 9-20 0Z"/><circle cx="12" cy="12" r="3"/>',
  "eye-off":
    '<path d="m3 3 18 18M10.5 5c5-.8 9.5 2.5 11.5 7a20 20 0 0 1-4 4.5M6 6.5A20 20 0 0 0 2 12c5 9 15 9 20 0M10 10a3 3 0 0 0 4 4"/>',
  globe:
    '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18"/>',
  lightbulb: '<path d="M9 18v-2a6 6 0 1 1 6 0v2M9 18h6M9 21h6M10 24h4"/>',
  "check-circle": '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
  check: '<path d="m4 12 5 5L20 6"/>',
  refresh:
    '<path d="M20 7v5h-5M4 17v-5h5M5.5 7a8 8 0 0 1 13 0L20 12M4 12l1.5 5a8 8 0 0 0 13 0"/>',
  download: '<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
  upload: '<path d="M12 16V4m-5 5 5-5 5 5M4 16v5h16v-5"/>',
  x: '<path d="m6 6 12 12M6 18 18 6"/>',
  menu: '<path d="M3 6h18M3 12h18M3 18h18"/>',
  edit: '<path d="m15 5 4 4M3 21l5-1L21 7a2.8 2.8 0 0 0-4-4L4 16ZM3 21l1-5"/>',
  alert: '<path d="m12 3 10 18H2Z M12 9v5M12 17h.01"/>',
  trash: '<path d="M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7M14 10v7"/>',
};
const $ = (id) => document.getElementById(id);
const esc = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      })[c],
  );
const svg = (name, extra = "") =>
  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" ${extra}>${paths[name] || paths.shield}</svg>`;

function icons(root = document) {
  root.querySelectorAll("[data-icon]").forEach((e) => {
    e.innerHTML = svg(e.dataset.icon);
  });
}
const state = {
  items: [],
  view: "overview",
  filter: "all",
  demo: false,
  csrf: null,
  initialized: false,
  authMode: "unlock",
  account: null,
  preview: false,
  settings: {
    auto_lock: 15,
  },
  editId: null,
  itemType: "password",
  itemIcon: "",
  generated: "",
  serverOffset: 0,
  lastInput: Date.now(),
  lastActivity: 0,
  codesBusy: false,
  refreshBusy: false,
  unlocked: false,
  grid: true,
  authBusy: false,
  authTransition: false,
};
const titles = {
  overview: ["Your vault", "Your codes and saved logins, together."],
  authenticators: [
    "Authenticators",
    "Your verification codes, ready when you need them.",
  ],
  passwords: ["Passwords", "Find a saved login or add a new one."],
  "backup-codes": [
    "Backup codes",
    "Recovery codes for when your usual sign-in method is unavailable.",
  ],
  favorites: ["Favorites", "The accounts you reach for most."],
  generator: [
    "Password generator",
    "Create a different password for every account.",
  ],
  security: ["Security check", "Review password length, variety, and reuse."],
  settings: [
    "Vault settings",
    "Manage locking, your master password, and encrypted backups.",
  ],
};
const pagePaths = Object.fromEntries(
  Object.keys(titles).map((view) => [view, "/" + view]),
);
const pathView = (path) =>
  Object.keys(pagePaths).find(
    (view) => pagePaths[view] === path.replace(/\/$/, ""),
  );
let returnView =
  pathView(new URLSearchParams(location.search).get("next") || "") ||
  pathView(location.pathname) ||
  "overview";
paths.sun =
  '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/>';
paths.user =
  '<circle cx="12" cy="8" r="4"/><path d="M5 21v-2a7 7 0 0 1 14 0v2"/>';
paths.home =
  '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1Z"/>';
paths["arrow-up-right"] = '<path d="M6 18 18 6M6 6h12v12"/>';
function loading(label) {
  $("loading-label").textContent = label;
  $("loading").hidden = false;
}
let detailItem = null,
  generatedSequence = 0,
  clipboardSequence = 0,
  lastCodeAttempt = 0;

function toast(message, error = false) {
  const e = document.createElement("div");
  e.className = "toast" + (error ? " error" : "");
  e.setAttribute("role", error ? "alert" : "status");
  e.innerHTML =
    svg(error ? "alert" : "check-circle") + `<span>${esc(message)}</span>`;
  $("toasts").append(e);
  setTimeout(() => e.remove(), error ? 6500 : 3800);
}
async function api(path, method = "GET", data) {
  const requestCsrf = state.csrf;
  const options = {
    method,
    headers: {
      "X-Requested-With": "Authentactor",
    },
    credentials: "same-origin",
    cache: "no-store",
  };
  if (method !== "GET") {
    options.headers["Content-Type"] = "application/json";
    options.headers["X-CSRF-Token"] = state.csrf || "";
    options.body = JSON.stringify(data || {});
  }
  let response;
  try {
    response = await fetch("/api" + path, options);
  } catch {
    throw new Error(
      "Cannot reach your server. Check the connection and try again.",
    );
  }
  const payload = await response.json();
  if (!response.ok) {
    if (
      response.status === 401 &&
      !["/unlock", "/setup"].includes(path) &&
      state.unlocked &&
      requestCsrf === state.csrf &&
      !state.authTransition
    ) {
      showAuth();
      toast("Your vault has been locked.");
    }
    const err = new Error(payload.error || "Unable to complete this request.");
    err.status = response.status;
    throw err;
  }
  if (requestCsrf && requestCsrf !== state.csrf)
    throw new Error("The vault session changed. Please try again.");
  return payload;
}

function showError(id, message) {
  const element = $(id);
  if (!element) return;
  element.textContent = message;
  element.hidden = !message;
}

function closeDialogs() {
  window.KagNodeControls?.close();
  document.querySelectorAll("dialog[open]").forEach((d) => d.close());
}

function clearSensitive() {
  state.items = [];
  state.csrf = null;
  state.generated = "";
  state.itemIcon = "";
  detailItem = null;
  state.editId = null;
  $("items").replaceChildren();
  $("security-items").replaceChildren();
  $("detail-content").replaceChildren();
  $("utility-content").replaceChildren();
  $("generated-password").textContent = "";
  $("account-email").textContent = "";
  $("vault-subtitle").textContent = "";
  document.querySelector(".topbar .avatar").textContent = "?";
  $("item-form").reset();
  $("master-password").value = "";
  $("confirm-password").value = "";
  $("item-password").type = "password";
}

function showAuth(mode) {
  const email = state.account?.email || $("auth-email").value;
  returnView = pathView(location.pathname) || returnView;
  closeDialogs();
  clearSensitive();
  state.account = null;
  state.authMode =
    mode ||
    (["/setup", "/signup"].includes(location.pathname) || !state.initialized
      ? "setup"
      : "unlock");
  const signup = state.authMode === "setup";
  state.unlocked = false;
  state.demo = false;
  $("loading").hidden = true;
  $("dashboard").hidden = true;
  $("auth-screen").hidden = false;
  $("auth-email").value = email;
  $("auth-title").textContent = signup ? "Create an account" : "Sign in";
  $("auth-description").textContent = signup
    ? "Create a separate encrypted vault for this email."
    : "Enter your email and password to open your vault.";
  $("auth-button").textContent = signup ? "Create account" : "Sign in";
  $("auth-switch").textContent = signup
    ? "Already have an account? Sign in"
    : "Create an account";
  $("confirm-wrap").hidden = !signup;
  $("confirm-password").required = signup;
  $("master-password").minLength = signup ? 12 : 1;
  $("master-password").autocomplete = signup
    ? "new-password"
    : "current-password";
  $("master-password").placeholder = signup
    ? "At least 12 characters"
    : "Your password";
  $("master-password").type = "password";
  $("master-note").textContent = signup
    ? "This password encrypts your vault. Email cannot be used to reset it."
    : "Use the existing vault password. Your email identifies the account.";
  $("auth-preview").hidden = !state.preview;
  showError("auth-error", "");
  document.title = `${signup ? "Create account" : "Sign in"} · KagNode. Authenticator`;
  history.replaceState(
    null,
    "",
    (signup ? "/setup" : "/unlock") +
      "?next=" +
      encodeURIComponent(pagePaths[returnView]),
  );
  $("sidebar").classList.remove("open");
  $("nav-scrim").hidden = true;
  $("mobile-menu").setAttribute("aria-expanded", "false");
}
async function showDashboard() {
  state.lastInput = Date.now();
  state.lastActivity = 0;
  state.unlocked = true;
  $("loading").hidden = true;
  $("auth-screen").hidden = true;
  $("dashboard").hidden = false;
  $("demo-pill").hidden = !state.demo;
  $("demo-banner").hidden = !state.demo;
  $("preview-banner").hidden = !state.preview;
  $("lock-label").textContent = state.demo ? "Exit demo" : "Sign out";
  $("sync-label").textContent = state.demo ? "Sample vault" : "Vault unlocked";
  $("demo-exit").innerHTML =
    (state.initialized ? "Unlock your vault" : "Set up your vault") +
    svg("arrow-right");
  $("vault-subtitle").textContent = state.demo
    ? "Sample vault"
    : state.account?.email || "Your vault";
  $("account-email").textContent = state.demo
    ? "demo@example.com"
    : state.account?.email || "";
  const avatar = document.querySelector(".topbar .avatar");
  avatar.textContent = state.demo
    ? "D"
    : (state.account?.email || "?").charAt(0).toUpperCase();
  avatar.title = state.account?.email || "Demo account";
  avatar.setAttribute("aria-label", "Account settings");
  navigate(returnView, { history: "replace" });
  try {
    await refreshItems();
  } catch (error) {
    if (state.unlocked) {
      $("vault-load-error").hidden = false;
      toast(error.message, true);
    }
  }
}
async function refreshItems() {
  $("vault-load-error").hidden = true;
  const showSkeleton = !state.demo && !state.items.length;
  if (showSkeleton) {
    state.loadingItems = true;
    $("items").setAttribute("aria-busy", "true");
    $("items").innerHTML = Array.from(
      { length: 3 },
      () =>
        '<div class="skeleton-card" aria-hidden="true"><i class="skeleton-line"></i><i class="skeleton-line"></i><i class="skeleton-line"></i></div>',
    ).join("");
    $("empty").hidden = true;
  }
  try {
    if (state.demo) {
      updateDemoCodes();
    } else {
      const data = await api("/items");
      state.items = data.items;
      state.settings = data.settings;
      state.serverOffset = data.server_time * 1000 - Date.now();
    }
  } catch (error) {
    if (showSkeleton) $("items").replaceChildren();
    throw error;
  } finally {
    state.loadingItems = false;
    $("items").removeAttribute("aria-busy");
  }
  renderStats();
  if (
    [
      "overview",
      "authenticators",
      "passwords",
      "backup-codes",
      "favorites",
    ].includes(state.view)
  )
    renderItems();
  if (state.view === "security") renderSecurity();
  $("auto-lock").value = String(state.settings.auto_lock);
  window.KagNodeControls?.sync();
}

function renderStats() {
  const items = state.items,
    pw = items.filter((i) => i.has_password),
    otp = items.filter((i) => i.has_totp),
    strong = pw.filter((i) => i.strength === "strong").length;
  $("stat-total").textContent = items.length;
  $("stat-totp").textContent = otp.length;
  $("stat-passwords").textContent = pw.length;
  $("stat-strong").innerHTML =
    strong + `<span class="stat-unit"> / ${pw.length}</span>`;
  $("stat-strength-note").textContent =
    pw.length && strong === pw.length
      ? "No basic issues found"
      : "Based on length & variety";
  $("nav-totp-count").textContent = otp.length;
  $("launch-totp-count").textContent =
    otp.length + " " + (otp.length === 1 ? "account" : "accounts");
  $("launch-password-count").textContent =
    pw.length + " " + (pw.length === 1 ? "password" : "passwords");
  $("nav-password-count").textContent = pw.length;
  $("nav-backup-count").textContent = items.filter(
    (i) => i.has_backup_codes,
  ).length;
  $("filter-backup").textContent = items.filter(
    (i) => i.has_backup_codes,
  ).length;
  $("security-dot").hidden = !pw.some((i) => i.strength === "weak" || i.reused);
  $("filter-all").textContent = items.length;
  $("filter-totp").textContent = otp.length;
  $("filter-password").textContent = pw.length;
}

function navigate(view, options = {}) {
  if (!titles[view] || !state.unlocked) return;
  closeDialogs();
  returnView = view;
  const address = pagePaths[view] + (state.demo ? "?demo=1" : "");
  const current = location.pathname + location.search;
  if (options.history !== "none" && current !== address)
    history[options.history === "replace" ? "replaceState" : "pushState"](
      { view },
      "",
      address,
    );
  state.view = view;
  document
    .querySelector(".main")
    .classList.toggle("is-overview", view === "overview");
  $("workspace-cards").hidden = view !== "overview";
  state.filter =
    view === "authenticators"
      ? "totp"
      : view === "passwords"
        ? "password"
        : view === "backup-codes"
          ? "backup"
          : "all";
  const [title, subtitle] = titles[view];
  $("page-title").textContent = title;
  $("page-subtitle").textContent = subtitle;
  $("breadcrumb-current").textContent =
    view === "overview" ? "Overview" : title;
  $("topbar-current").textContent = view === "overview" ? "Overview" : title;
  document.title = `${title} · KagNode. Authenticator`;
  document.querySelectorAll(".nav-item").forEach((e) => {
    const active = e.dataset.view === view;
    e.classList.toggle("active", active);
    active
      ? e.setAttribute("aria-current", "page")
      : e.removeAttribute("aria-current");
  });
  document.querySelectorAll("a[data-view]").forEach((link) => {
    link.href = pagePaths[link.dataset.view] + (state.demo ? "?demo=1" : "");
  });
  const vault = [
    "overview",
    "authenticators",
    "passwords",
    "backup-codes",
    "favorites",
  ].includes(view);
  $("vault-view").hidden = !vault;
  $("generator-view").hidden = view !== "generator";
  $("security-view").hidden = view !== "security";
  $("settings-view").hidden = view !== "settings";
  $("page-actions").hidden = !vault;
  $("vault-add-button").hidden = view !== "overview";
  $("stats").hidden = view !== "overview";
  $("filters").hidden = view !== "overview";
  $("items-heading").firstChild.textContent =
    view === "overview"
      ? "All vault items "
      : view === "favorites"
        ? "Your favorites "
        : view === "backup-codes"
          ? "Your backup codes "
          : "Your " + view + " ";
  $("search").value = "";
  if (vault) renderItems();
  if (view === "generator") generate().catch((e) => toast(e.message, true));
  if (view === "security") renderSecurity();
  if (view === "settings")
    $("auto-lock").value = String(state.settings.auto_lock);
  $("sidebar").classList.remove("open");
  $("nav-scrim").hidden = true;
  $("mobile-menu").setAttribute("aria-expanded", "false");
  window.KagNodeControls?.sync();
}

function domain(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "";
  }
}

function logo(item) {
  const color =
    item.demoColor ||
    ["orange", "blue", "purple", "dark", "green", "red"][
      [...item.name].reduce((s, c) => s + c.charCodeAt(0), 0) % 6
    ];
  return `<div class="site-logo logo-${esc(color)}">${item.icon ? `<img src="${esc(item.icon)}" alt="" loading="lazy">` : esc(item.name.charAt(0).toUpperCase())}</div>`;
}

function formatCode(code) {
  if (!code) return "··· ···";
  const mid = code.length / 2;
  return code.slice(0, mid) + " " + code.slice(mid);
}

function timer(item) {
  return `<div class="timer" data-timer="${esc(item.id)}"><svg viewBox="0 0 28 28" aria-hidden="true"><circle class="timer-track" cx="14" cy="14" r="12"/><circle class="timer-progress" cx="14" cy="14" r="12"/></svg><span>–</span></div>`;
}

function renderItems() {
  if (state.loadingItems) return;
  let items = state.items
    .filter((i) => state.view !== "favorites" || i.favorite)
    .filter(
      (i) =>
        state.filter === "all" ||
        (state.filter === "totp"
          ? i.has_totp
          : state.filter === "backup"
            ? i.has_backup_codes
            : i.has_password),
    );
  const search = $("search").value.trim().toLowerCase();
  items = items.filter((i) =>
    [i.name, i.username, i.url].some((v) =>
      String(v).toLowerCase().includes(search),
    ),
  );
  items.sort((a, b) =>
    $("sort").value === "recent"
      ? b.updated_at - a.updated_at
      : a.name.localeCompare(b.name),
  );
  $("items").classList.toggle("list-layout", !state.grid);
  $("items").innerHTML = items
    .map(
      (i) =>
        `<article class="item-card" data-id="${esc(i.id)}"><div class="item-card-heading">${logo(i)}<button class="item-title" data-action="detail"><strong>${esc(i.name)}</strong><small>${esc(i.username || domain(i.url) || "Personal account")}</small></button><button class="icon-button ${i.favorite ? "favorite-active" : ""}" data-action="favorite" aria-label="${i.favorite ? "Remove from" : "Add to"} favorites" aria-pressed="${i.favorite}">${svg("star")}</button></div>${itemCredentials(i)}<div class="item-card-footer">${i.url ? `<a href="${esc(i.url)}" target="_blank" rel="noopener noreferrer">${svg("globe")}${esc(domain(i.url))}</a>` : "<span>App account</span>"}<button class="text-button" data-action="detail">View details ${svg("arrow-right")}</button></div></article>`,
    )
    .join("");
  $("empty").hidden = items.length > 0;
  $("items-footer").hidden = !items.length;
  $("item-count").textContent = items.length;
  $("results-label").textContent =
    `Showing ${items.length} ${items.length === 1 ? "item" : "items"}`;
  const isSearch = search.length > 0 || state.items.length > 0;
  $("empty-title").textContent = isSearch
    ? search
      ? "No matching items."
      : state.view === "favorites"
        ? "Keep your favorites close."
        : "Nothing here just yet."
    : "Make yourself at home.";
  $("empty-description").innerHTML = search
    ? "Try another name, account, or website."
    : state.view === "favorites"
      ? "Tap the star on an item to keep it here."
      : "Add an authenticator, saved login, or backup codes to get started.";
  $("empty-add").hidden = !!search || state.view === "favorites";
  document
    .querySelectorAll("[data-filter]")
    .forEach((e) =>
      e.classList.toggle("active", e.dataset.filter === state.filter),
    );
  tickTimers();
}

function itemCredentials(i) {
  let content = "";
  if (i.has_totp)
    content = `<div class="code-area"><button class="code-text" data-code="${esc(i.id)}" data-action="copy-code" aria-label="Copy ${esc(i.name)} verification code">${formatCode(i.code)}</button><div class="code-side"><button class="icon-button" data-action="copy-code" aria-label="Copy verification code">${svg("copy")}</button>${timer(i)}</div></div><div class="item-type-line">${svg("fingerprint")}Verification code · ${i.period}s${i.has_password ? '<span class="pill">Password saved</span>' : ""}</div>`;
  else if (i.has_password)
    content = `<div class="code-area password-area"><button class="code-text" data-action="copy-password" aria-label="Copy ${esc(i.name)} password">••••••••••••</button><button class="icon-button" data-action="copy-password" aria-label="Copy password">${svg("copy")}</button></div><div class="item-type-line">${svg("key")}Password<span class="pill ${esc(i.strength)}">${esc(i.strength?.charAt(0).toUpperCase() + i.strength?.slice(1))}</span></div>`;
  if (i.has_backup_codes)
    content += `<button class="backup-summary" data-action="detail">${svg("shield-check")}<span>${i.backup_codes_remaining} of ${i.backup_codes_total} backup codes available</span>${svg("arrow-right")}</button>`;
  return content;
}

function tickTimers() {
  const now = (Date.now() + state.serverOffset) / 1000;
  document.querySelectorAll("[data-timer]").forEach((el) => {
    const item = state.items.find((i) => i.id === el.dataset.timer);
    if (!item) return;
    const left = Math.max(0, Math.ceil(item.expires_at - now));
    el.querySelector("span").textContent = left + "s";
    el.querySelector(".timer-progress").setAttribute(
      "stroke-dashoffset",
      String(75.4 * (1 - Math.min(1, left / item.period))),
    );
  });
  document.querySelectorAll("[data-code]").forEach((el) => {
    const item = state.items.find((i) => i.id === el.dataset.code);
    if (item) {
      el.textContent =
        item.expires_at > now ? formatCode(item.code) : "··· ···";
      el.dataset.stale = String(item.expires_at <= now);
    }
  });
}
async function refreshCodes() {
  if (state.codesBusy) return;
  state.codesBusy = true;
  lastCodeAttempt = Date.now();
  try {
    if (state.demo) {
      updateDemoCodes();
    } else {
      const data = await api("/codes");
      state.serverOffset = data.server_time * 1000 - Date.now();
      for (const c of data.codes) {
        const i = state.items.find((i) => i.id === c.id);
        if (i) Object.assign(i, c);
      }
    }
    tickTimers();
  } catch (e) {
    if (e.status !== 401)
      toast("Codes could not refresh. Check your connection.", true);
  } finally {
    state.codesBusy = false;
  }
}
async function copy(text, label = "Copied", clear = true) {
  let successful = false;
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      successful = true;
    } else {
      const area = document.createElement("textarea");
      area.className = "clipboard-helper";
      area.value = text;
      const previousFocus = document.activeElement;
      (document.querySelector("dialog[open]") || document.body).append(area);
      area.focus();
      area.select();
      successful = document.execCommand("copy");
      area.remove();
      previousFocus?.focus();
    }
  } catch {}
  if (!successful) {
    toast(
      "Copy unavailable in this browser. Open the item to select the value.",
      true,
    );
    return;
  }
  toast(label);
  const seq = ++clipboardSequence;
  if (clear && navigator.clipboard && window.isSecureContext) {
    setTimeout(async () => {
      if (seq !== clipboardSequence) return;
      try {
        if ((await navigator.clipboard.readText()) === text)
          await navigator.clipboard.writeText("");
      } catch {}
    }, 30000);
  }
}
async function itemAction(action, id) {
  const item = state.items.find((i) => i.id === id);
  if (!item) return;
  try {
    if (action === "favorite") {
      if (state.demo) {
        item.favorite = !item.favorite;
      } else {
        await api("/items/" + id, "PUT", {
          favorite: !item.favorite,
        });
        item.favorite = !item.favorite;
      }
      renderItems();
    }
    if (action === "detail") await openDetail(id);
    if (action === "copy-code") {
      if (item.expires_at <= (Date.now() + state.serverOffset) / 1000) {
        await refreshCodes();
        if (item.expires_at <= (Date.now() + state.serverOffset) / 1000)
          throw new Error("Waiting for a fresh code. Try again in a moment.");
      }
      await copy(item.code, "Verification code copied");
    }
    if (action === "copy-password") {
      const data = state.demo
        ? demoDetails(id)
        : (await api("/items/" + id)).item;
      await copy(data.password, "Password copied");
    }
  } catch (e) {
    toast(e.message, true);
  }
}

function setItemType(type) {
  state.itemType = type;
  for (const t of ["password", "totp", "both", "backup"]) {
    $("type-" + t).classList.toggle("selected", type === t);
    $("type-" + t).setAttribute("aria-pressed", String(type === t));
  }
  $("password-fields").hidden = !["password", "both"].includes(type);
  $("totp-fields").hidden = !["totp", "both"].includes(type);
  $("item-password").required = ["password", "both"].includes(type);
  $("item-secret").required = ["totp", "both"].includes(type);
  $("item-backup-codes").required = type === "backup";
  $("backup-optional").hidden = type === "backup";
}
async function openItem(id = null, prefill = "") {
  if (state.demo) {
    toast("Set up your vault to save your own items.");
    return;
  }
  closeDialogs();
  $("item-form").reset();
  $("item-password").type = "password";
  state.editId = id;
  state.itemIcon = "";
  $("item-dialog-title").textContent = id
    ? "Edit vault item"
    : "Add a new item";
  $("save-item").innerHTML =
    (id ? "Save changes" : "Save item") + svg("arrow-right");
  showError("item-error", "");
  $("item-icon-preview").textContent = "a";
  setItemType(
    state.view === "authenticators"
      ? "totp"
      : state.view === "backup-codes"
        ? "backup"
        : "password",
  );
  if (id) {
    try {
      const i = (await api("/items/" + id)).item;
      for (const field of [
        "name",
        "username",
        "url",
        "password",
        "secret",
        "notes",
        "algorithm",
        "digits",
        "period",
      ])
        $("item-" + field).value = i[field];
      $("item-favorite").checked = i.favorite;
      state.itemIcon = i.icon;
      $("item-backup-codes").value = (i.backup_codes || [])
        .map((c) => c.code)
        .join("\n");
      setItemType(
        i.password && i.secret
          ? "both"
          : i.secret
            ? "totp"
            : i.password
              ? "password"
              : "backup",
      );
      renderIconPreview();
    } catch (e) {
      toast(e.message, true);
      return;
    }
  }
  if (prefill) {
    $("item-password").value = prefill;
    setItemType("password");
  }
  window.KagNodeControls?.sync();
  $("item-dialog").showModal();
}

function renderIconPreview() {
  const url = state.itemIcon;
  $("item-icon-preview").innerHTML = url
    ? `<img src="${esc(url)}" alt="Website icon">`
    : esc(
        (
          $("item-name").value ||
          domain(
            ($("item-url").value.includes("://") ? "" : "https://") +
              $("item-url").value,
          ) ||
          "a"
        )
          .charAt(0)
          .toUpperCase(),
      );
}
async function fetchItemIcon(quiet = false) {
  if (!$("item-url").value.trim()) return;
  if ($("fetch-icon").disabled) return;
  const requestedUrl = $("item-url").value.trim();
  $("fetch-icon").disabled = true;
  $("fetch-icon").textContent = "Fetching…";
  try {
    const data = await api("/icon", "POST", {
      url: requestedUrl,
    });
    if ($("item-url").value.trim() === requestedUrl && $("item-dialog").open) {
      state.itemIcon = data.icon;
      renderIconPreview();
      if (!quiet) toast("Website icon fetched");
    }
  } catch (e) {
    if (!quiet) toast(e.message, true);
  } finally {
    $("fetch-icon").disabled = false;
    $("fetch-icon").textContent = "Fetch icon";
  }
}
async function saveItem(event) {
  event.preventDefault();
  if (state.demo) return;
  const btn = $("save-item");
  btn.disabled = true;
  showError("item-error", "");
  try {
    if (
      ["totp", "both"].includes(state.itemType) &&
      $("item-secret").value.toLowerCase().startsWith("otpauth://")
    )
      await parseSetupLink();
    const data = {};
    for (const field of [
      "name",
      "username",
      "url",
      "password",
      "secret",
      "notes",
      "algorithm",
      "digits",
      "period",
    ])
      data[field] = $("item-" + field).value;
    if (!["totp", "both"].includes(state.itemType)) data.secret = "";
    if (!["password", "both"].includes(state.itemType)) data.password = "";
    data.backup_codes = $("item-backup-codes").value;
    data.favorite = $("item-favorite").checked;
    data.icon = state.itemIcon;
    await api(
      state.editId ? "/items/" + state.editId : "/items",
      state.editId ? "PUT" : "POST",
      data,
    );
    $("item-dialog").close();
    toast(state.editId ? "Changes saved" : "Item added to your vault");
    await refreshItems();
  } catch (e) {
    showError("item-error", e.message);
  } finally {
    btn.disabled = false;
  }
}
async function parseSetupLink() {
  const secret = $("item-secret").value.trim();
  if (!secret.toLowerCase().startsWith("otpauth://")) return;
  const parsed = await api("/parse-totp", "POST", {
    secret,
  });
  for (const key of ["secret", "algorithm", "digits", "period"])
    $("item-" + key).value = parsed[key];
  if (!$("item-name").value) $("item-name").value = parsed.name || "";
  if (!$("item-username").value)
    $("item-username").value = parsed.username || "";
  renderIconPreview();
  window.KagNodeControls?.sync();
}
async function openDetail(id) {
  try {
    const i = state.demo ? demoDetails(id) : (await api("/items/" + id)).item;
    detailItem = i;
    const summary = state.items.find((x) => x.id === id);
    $("detail-content").innerHTML =
      `<div class="detail-hero">${logo(summary)}<div><h2>${esc(i.name)}</h2><p>${esc(i.username || "Personal account")}</p></div><button class="icon-button close-dialog" aria-label="Close">${svg("x")}</button></div><div class="detail-body">${i.username ? detailRow("Account", i.username, "username") : ""}${i.url ? detailRow("Website", i.url, "url") : ""}${i.password ? `<div class="detail-row"><label>Password</label><div><output id="detail-password" class="secret-value">••••••••••••••••</output><button class="icon-button" id="detail-reveal" aria-label="Show password">${svg("eye")}</button><button class="icon-button" data-detail-copy="password" aria-label="Copy password">${svg("copy")}</button></div></div>` : ""}${i.secret ? `<div class="detail-row"><label>Verification code · ${esc(i.algorithm)} · ${i.period}s</label><div><button class="code-text" data-code="${esc(i.id)}" data-detail-code="${esc(i.id)}" aria-label="Copy verification code">${formatCode(summary.code)}</button><div class="code-side">${timer(summary)}</div><button class="icon-button" data-detail-code="${esc(i.id)}" aria-label="Copy verification code">${svg("copy")}</button></div></div>` : ""}${backupCodeDetails(i)}${i.notes ? `<div class="detail-row"><label>Notes</label><output>${esc(i.notes)}</output></div>` : ""}<p class="small-note">Updated ${esc(new Date(i.updated_at * 1000).toLocaleDateString(undefined, { month: "long", day: "numeric", year: "numeric" }))}</p></div><div class="modal-footer"><button class="button danger small" id="detail-delete">${svg("trash")}Delete item</button><button class="button secondary small" id="detail-edit">${svg("edit")}Edit item</button></div>`;
    $("detail-dialog").showModal();
    tickTimers();
  } catch (e) {
    toast(e.message, true);
  }
}

function backupCodeDetails(item) {
  const codes = item.backup_codes || [];
  if (!codes.length) return "";
  const available = codes.filter((c) => !c.used).length;
  return `<section class="backup-details" aria-label="Backup codes"><div class="backup-details-heading"><h3>Backup codes</h3><span>${available} of ${codes.length} available</span></div><p class="small-note">Copying does not mark a code as used. After the service accepts it, mark it here.</p><div class="backup-code-list">${codes.map((c, index) => `<div class="backup-code-row ${c.used ? "is-used" : ""}" data-backup-id="${esc(c.id)}"><span class="backup-code-number">${index + 1}</span><output class="backup-code-value" aria-label="Backup code ${index + 1}">•••• •••• ••••</output><div class="backup-code-actions"><button type="button" class="icon-button" data-backup-action="reveal" aria-label="Show backup code ${index + 1}" aria-pressed="false">${svg("eye")}</button><button type="button" class="icon-button" data-backup-action="copy" aria-label="Copy backup code ${index + 1}" ${c.used ? "disabled" : ""}>${svg("copy")}</button><button type="button" class="button secondary small backup-usage" data-backup-action="usage" aria-label="${c.used ? "Mark available" : "Mark used"} backup code ${index + 1}">${svg(c.used ? "refresh" : "check")}<span>${c.used ? "Mark available" : "Mark used"}</span></button></div><span class="backup-code-status">${c.used ? "Used" + (c.used_at ? " · " + esc(new Date(c.used_at * 1000).toLocaleDateString()) : "") : "Available"}</span></div>`).join("")}</div></section>`;
}

async function backupCodeAction(button) {
  const item = detailItem,
    row = button.closest("[data-backup-id]");
  const code = item?.backup_codes?.find((c) => c.id === row.dataset.backupId);
  if (!code) return;
  const action = button.dataset.backupAction;
  if (action === "reveal") {
    const show = button.getAttribute("aria-pressed") !== "true";
    row.querySelector("output").textContent = show
      ? code.code
      : "•••• •••• ••••";
    button.setAttribute("aria-pressed", String(show));
    const number = row.querySelector(".backup-code-number").textContent;
    button.setAttribute(
      "aria-label",
      `${show ? "Hide" : "Show"} backup code ${number}`,
    );
    button.innerHTML = svg(show ? "eye-off" : "eye");
  } else if (action === "copy" && !code.used)
    await copy(code.code, "Backup code copied; mark it used after signing in");
  else if (action === "usage") {
    if (state.demo) {
      toast("Sample codes stay unchanged in the demo vault.");
      return;
    }
    button.disabled = true;
    try {
      await api(`/items/${item.id}/backup-codes/${code.id}/usage`, "POST", {
        used: !code.used,
      });
      if (detailItem?.id === item.id && $("detail-dialog").open)
        await openDetail(item.id);
      await refreshItems();
      toast(
        code.used ? "Backup code marked available" : "Backup code marked used",
      );
    } catch (error) {
      toast(error.message, true);
    } finally {
      button.disabled = false;
    }
  }
}

function detailRow(label, value, key) {
  return `<div class="detail-row"><label>${label}</label><div><output>${esc(value)}</output><button class="icon-button" data-detail-copy="${key}" aria-label="Copy ${label.toLowerCase()}">${svg("copy")}</button></div></div>`;
}

function utility(title, content, submitLabel, handler, danger = false) {
  $("utility-content").innerHTML =
    `<div class="modal-heading"><div><span class="eyebrow">YOUR PERSONAL VAULT</span><h2>${title}</h2></div><button class="icon-button close-dialog" aria-label="Close">${svg("x")}</button></div><form id="utility-form" class="utility-form">${content}<div id="utility-error" class="form-error" role="alert" hidden></div><div class="utility-actions"><button type="button" class="button secondary close-dialog">Cancel</button><button type="submit" id="utility-submit" class="button ${danger ? "danger" : "primary"}">${submitLabel}</button></div></form>`;
  $("utility-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    $("utility-submit").disabled = true;
    try {
      await handler();
      $("utility-dialog").close();
    } catch (err) {
      showError("utility-error", err.message);
    } finally {
      if ($("utility-submit")) $("utility-submit").disabled = false;
    }
  });
  $("utility-dialog").showModal();
}

function deleteItem() {
  if (state.demo) {
    toast("Sample items stay in the demo vault.");
    return;
  }
  const i = detailItem;
  closeDialogs();
  utility(
    "Delete this item?",
    `<p>Remove <strong>${esc(i.name)}</strong> from your vault? This cannot be undone. Export a backup first if you may need it later.</p>`,
    "Delete item",
    async () => {
      await api("/items/" + i.id, "DELETE");
      await refreshItems();
      toast("Item removed from your vault");
    },
    true,
  );
}

function generatorOptions() {
  return {
    length: Number($("password-length").value),
    uppercase: $("gen-uppercase").checked,
    lowercase: $("gen-lowercase").checked,
    numbers: $("gen-numbers").checked,
    symbols: $("gen-symbols").checked,
    exclude_ambiguous: $("gen-exclude").checked,
  };
}

function secureDemoPassword(options) {
  let alphabet = "";
  if (options.uppercase) alphabet += "ABCDEFGHJKLMNPQRSTUVWXYZ";
  if (options.lowercase) alphabet += "abcdefghijkmnpqrstuvwxyz";
  if (options.numbers) alphabet += "23456789";
  if (options.symbols) alphabet += "!@#$%^&*-_=+";
  if (!alphabet) throw new Error("Select at least one character type.");
  const chars = [];
  const array = new Uint32Array(1);
  for (let j = 0; j < options.length; j++) {
    do {
      crypto.getRandomValues(array);
    } while (
      array[0] >=
      Math.floor(4294967296 / alphabet.length) * alphabet.length
    );
    chars.push(alphabet[array[0] % alphabet.length]);
  }
  return chars.join("");
}
async function generate() {
  const seq = ++generatedSequence,
    options = generatorOptions();
  const data = state.demo
    ? {
        password: secureDemoPassword(options),
        strength:
          options.length >= 16
            ? "strong"
            : options.length >= 12
              ? "fair"
              : "weak",
      }
    : await api("/generate", "POST", options);
  if (seq !== generatedSequence || !state.unlocked) return;
  state.generated = data.password;
  $("generated-password").textContent = data.password;
  $("generated-strength").textContent =
    data.strength.charAt(0).toUpperCase() +
    data.strength.slice(1) +
    " password";
  document.querySelector(".strength-line").dataset.strength = data.strength;
}

function renderSecurity() {
  const pw = state.items.filter((i) => i.has_password),
    flagged = pw.filter((i) => i.strength !== "strong" || i.reused);
  $("security-title").textContent = pw.length
    ? flagged.length
      ? `${flagged.length} ${flagged.length === 1 ? "password needs" : "passwords need"} review.`
      : "No issues in these basic checks."
    : "No passwords to check yet.";
  $("security-description").textContent = pw.length
    ? `${pw.length} ${pw.length === 1 ? "password checked" : "passwords checked"} locally. Nothing is sent to an external service.`
    : "Save a password in your vault to see a local security check.";
  $("security-score").textContent = pw.length
    ? `${pw.length - flagged.length} / ${pw.length} pass basic checks`
    : "Local analysis";
  $("security-items").innerHTML = flagged
    .map(
      (i) =>
        `<div class="security-row" data-id="${esc(i.id)}">${logo(i)}<div class="security-text"><strong>${esc(i.name)}</strong><p>${esc(i.username || domain(i.url))}</p></div><span class="pill ${i.reused || i.strength === "weak" ? "weak" : "fair"}">${i.reused ? "Reused" : i.strength === "weak" ? "Weak password" : "Could be stronger"}</span><button class="button secondary small" data-security-edit="${esc(i.id)}">Review ${svg("arrow-right")}</button></div>`,
    )
    .join("");
  if (pw.length && !flagged.length)
    $("security-items").innerHTML =
      `<div class="empty-state"><div>${svg("check-circle")}</div><h3>No weak or repeated passwords found.</h3><p>Your saved passwords pass the basic length, variety, and reuse checks.</p></div>`;
}
async function backup() {
  if (state.demo) {
    toast("Set up your vault to export an encrypted backup.");
    return;
  }
  try {
    const data = await api("/backup");
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download =
      "kagnode-authenticator-backup-" +
      new Date().toISOString().slice(0, 10) +
      ".json";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    toast("Encrypted backup downloaded");
  } catch (e) {
    toast(e.message, true);
  }
}

function restore() {
  if (state.demo) {
    toast("Set up your vault to restore a backup.");
    return;
  }
  utility(
    "Restore a backup",
    `<p>Add items from a compatible encrypted backup. Your existing items are kept. Use the master password that protected the backup when it was created.</p><div class="field"><label for="backup-file">Encrypted backup file</label><input type="file" id="backup-file" accept=".json,application/json" required></div><div class="field"><label for="backup-password">Backup’s master password</label><input type="password" id="backup-password" autocomplete="off" required maxlength="1024"></div>`,
    "Restore items",
    async () => {
      const file = $("backup-file").files[0];
      if (!file || file.size > 16000000)
        throw new Error("Choose an encrypted backup smaller than 16 MB.");
      let backup;
      try {
        backup = JSON.parse(await file.text());
      } catch {
        throw new Error("This file is not a valid JSON backup.");
      }
      const result = await api("/restore", "POST", {
        backup,
        password: $("backup-password").value,
      });
      await refreshItems();
      toast(
        `${result.imported} items restored; ${result.skipped} already present.`,
      );
    },
  );
}

function changeMaster() {
  if (state.demo) {
    toast("Set up your vault to change its master password.");
    return;
  }
  utility(
    "Change master password",
    `<p>Your vault will be re-encrypted and other sessions locked. Existing backups will still need their original password.</p><div class="field"><label for="current-master">Current master password</label><input id="current-master" type="password" autocomplete="current-password" required maxlength="1024"></div><div class="field"><label for="new-master">New master password · at least 12 characters</label><input id="new-master" type="password" autocomplete="new-password" minlength="12" maxlength="1024" required></div><div class="field"><label for="new-master-confirm">Confirm new password</label><input id="new-master-confirm" type="password" autocomplete="new-password" required maxlength="1024"></div>`,
    "Update password",
    async () => {
      if ($("new-master").value !== $("new-master-confirm").value)
        throw new Error("The new passwords do not match.");
      state.authTransition = true;
      try {
        const data = await api("/change-password", "POST", {
          current: $("current-master").value,
          password: $("new-master").value,
        });
        state.csrf = data.csrf;
        toast("Master password updated. Other sessions are now locked.");
      } finally {
        state.authTransition = false;
      }
    },
  );
}
const demoSecretPassword = "Example-only-Password!42";

function demoDetails(id) {
  const i = state.items.find((x) => x.id === id);
  return {
    ...i,
    password: i.has_password ? demoSecretPassword : "",
    secret: i.has_totp ? "JBSWY3DPEHPK3PXP" : "",
    algorithm: "SHA1",
    backup_codes: i.has_backup_codes
      ? [
          {
            id: "sample-1",
            code: "DEMO-1234-5678",
            used: false,
            used_at: null,
          },
          {
            id: "sample-2",
            code: "DEMO-8765-4321",
            used: true,
            used_at: 1700000000,
          },
        ]
      : [],
    notes:
      "Sample item for exploring KagNode Authenticator. This is not a real account.",
  };
}

function updateDemoCodes() {
  const now = Date.now() / 1000;
  state.serverOffset = 0;
  state.items
    .filter((i) => i.has_totp)
    .forEach((i, j) => {
      i.code = String(
        (Math.floor(now / i.period) * 7919 + (j + 1) * 148451) % 1000000,
      ).padStart(6, "0");
      i.expires_at = (Math.floor(now / i.period) + 1) * i.period;
    });
}
async function startDemo() {
  state.demo = true;
  state.settings = {
    auto_lock: 15,
  };
  const samples = [
    [
      "Cloudflare",
      "hello@example.com",
      "cloudflare.com",
      true,
      true,
      true,
      "orange",
    ],
    ["GitHub", "alex@example.com", "github.com", true, true, true, "dark"],
    ["Google", "alex@gmail.com", "google.com", true, true, false, "blue"],
    ["Figma", "alex@studio.design", "figma.com", false, true, false, "purple"],
    ["Amazon", "alex@example.com", "amazon.com", true, false, false, "orange"],
    [
      "Microsoft",
      "alex@outlook.com",
      "microsoft.com",
      false,
      true,
      false,
      "blue",
    ],
  ];
  state.items = samples.map((s, j) => ({
    id: "demo-" + j,
    name: s[0],
    username: s[1],
    url: "https://" + s[2],
    has_totp: s[3],
    has_password: s[4],
    has_backup_codes: j === 1,
    backup_codes_total: j === 1 ? 2 : 0,
    backup_codes_remaining: j === 1 ? 1 : 0,
    favorite: s[5],
    demoColor: s[6],
    icon: "",
    strength: j === 3 ? "fair" : "strong",
    reused: false,
    period: 30,
    digits: 6,
    algorithm: "SHA1",
    updated_at: Date.now() / 1000 - j * 8000,
  }));
  await showDashboard();
}

function bind() {
  document.querySelectorAll("[data-view]").forEach((e) =>
    e.addEventListener("click", (event) => {
      if (
        e.tagName === "A" &&
        (event.metaKey ||
          event.ctrlKey ||
          event.shiftKey ||
          event.altKey ||
          event.button)
      )
        return;
      event.preventDefault();
      navigate(e.dataset.view);
    }),
  );
  window.addEventListener("popstate", () => {
    const demo = new URLSearchParams(location.search).get("demo") === "1";
    if (state.demo !== demo) {
      location.reload();
      return;
    }
    if (!state.unlocked) {
      showAuth();
      return;
    }
    const view = pathView(location.pathname);
    navigate(view || returnView, { history: view ? "none" : "replace" });
  });
  $("retry-items").addEventListener("click", () =>
    refreshItems().catch((error) => {
      $("vault-load-error").hidden = false;
      toast(error.message, true);
    }),
  );
  document.querySelectorAll("[data-filter]").forEach((e) =>
    e.addEventListener("click", () => {
      state.filter = e.dataset.filter;
      renderItems();
    }),
  );
  $("auth-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (state.authBusy) return;
    showError("auth-error", "");
    const password = $("master-password").value;
    if (
      state.authMode === "setup" &&
      password !== $("confirm-password").value
    ) {
      showError("auth-error", "The passwords do not match.");
      return;
    }
    state.authBusy = true;
    const btn = document.querySelector(".auth-submit");
    btn.disabled = true;
    loading(
      state.authMode === "setup" ? "Creating your account…" : "Signing in…",
    );
    try {
      const data = await api(
        state.authMode === "setup" ? "/setup" : "/unlock",
        "POST",
        {
          email: $("auth-email").value,
          password,
        },
      );
      state.csrf = data.csrf;
      state.settings = data.settings;
      state.account = data.account;
      state.initialized = true;
      state.demo = false;
      $("master-password").value = "";
      $("confirm-password").value = "";
      await showDashboard();
    } catch (err) {
      showError("auth-error", err.message);
    } finally {
      state.authBusy = false;
      btn.disabled = false;
      $("loading").hidden = true;
    }
  });
  $("auth-switch").addEventListener("click", () =>
    showAuth(state.authMode === "setup" ? "unlock" : "setup"),
  );
  $("demo-button").addEventListener("click", startDemo);
  $("demo-exit").addEventListener("click", () => showAuth());
  $("lock-button").addEventListener("click", async () => {
    if (state.demo) {
      showAuth();
      return;
    }
    try {
      loading("Signing out…");
      await Promise.all([
        api("/lock", "POST"),
        new Promise((resolve) => setTimeout(resolve, 400)),
      ]);
      showAuth();
      toast("Vault locked");
    } catch (e) {
      toast(e.message, true);
    } finally {
      $("loading").hidden = true;
    }
  });
  $("add-button").addEventListener("click", () => openItem());
  $("vault-add-button").addEventListener("click", () => openItem());
  $("quick-search").addEventListener("click", openQuickSearch);
  $("empty-add").addEventListener("click", () => openItem());
  $("search").addEventListener("input", renderItems);
  $("sort").addEventListener("change", renderItems);
  $("grid-view").addEventListener("click", () => setLayout(true));
  $("list-view").addEventListener("click", () => setLayout(false));
  $("items").addEventListener("click", (e) => {
    const button = e.target.closest("[data-action]");
    if (button)
      itemAction(button.dataset.action, button.closest("[data-id]").dataset.id);
  });
  for (const type of ["password", "totp", "both", "backup"])
    $("type-" + type).addEventListener("click", () => setItemType(type));
  $("item-form").addEventListener("submit", saveItem);
  $("item-name").addEventListener("input", renderIconPreview);
  $("item-url").addEventListener("input", () => {
    state.itemIcon = "";
    renderIconPreview();
  });
  $("item-url").addEventListener("change", () => fetchItemIcon(true));
  $("item-secret").addEventListener("change", () =>
    parseSetupLink().catch((e) => showError("item-error", e.message)),
  );
  $("fetch-icon").addEventListener("click", () => fetchItemIcon());
  $("quick-generate").addEventListener("click", async () => {
    try {
      const data = await api("/generate", "POST", {
        length: 20,
      });
      $("item-password").value = data.password;
      toast("New password generated. Save the item to keep it.");
    } catch (e) {
      toast(e.message, true);
    }
  });
  $("generator-promo").addEventListener("click", () => navigate("generator"));
  $("password-length").addEventListener("input", () => {
    $("length-value").textContent = $("password-length").value;
  });
  $("password-length").addEventListener("change", () =>
    generate().catch((e) => toast(e.message, true)),
  );
  for (const id of [
    "gen-uppercase",
    "gen-lowercase",
    "gen-numbers",
    "gen-symbols",
    "gen-exclude",
  ])
    $(id).addEventListener("change", () =>
      generate().catch((e) => toast(e.message, true)),
    );
  $("regenerate").addEventListener("click", () =>
    generate().catch((e) => toast(e.message, true)),
  );
  $("copy-generated").addEventListener("click", () => {
    if (state.generated) copy(state.generated, "Generated password copied");
  });
  $("save-generated").addEventListener("click", () => {
    if (state.generated) openItem(null, state.generated);
  });
  $("auto-lock").addEventListener("change", async () => {
    try {
      const minutes = Number($("auto-lock").value);
      if (!state.demo)
        await api("/settings", "PUT", {
          auto_lock: minutes,
        });
      state.settings.auto_lock = minutes;
      toast("Automatic lock updated");
    } catch (e) {
      $("auto-lock").value = String(state.settings.auto_lock);
      window.KagNodeControls?.sync();
      toast(e.message, true);
    }
  });
  $("backup").addEventListener("click", backup);
  $("restore-button").addEventListener("click", restore);
  $("change-master").addEventListener("click", changeMaster);
  $("security-items").addEventListener("click", (e) => {
    const b = e.target.closest("[data-security-edit]");
    if (b) openItem(b.dataset.securityEdit);
  });
  $("mobile-menu").addEventListener("click", () => {
    const open = $("sidebar").classList.toggle("open");
    $("nav-scrim").hidden = !open;
    $("mobile-menu").setAttribute("aria-expanded", String(open));
  });
  $("nav-scrim").addEventListener("click", () => {
    $("sidebar").classList.remove("open");
    $("nav-scrim").hidden = true;
    $("mobile-menu").setAttribute("aria-expanded", "false");
  });
  document.addEventListener("click", (e) => {
    const close = e.target.closest(".close-dialog");
    if (close) close.closest("dialog").close();
    const reveal = e.target.closest("[data-reveal]");
    if (reveal) {
      const input = $(reveal.dataset.reveal);
      input.type = input.type === "password" ? "text" : "password";
      const hidden = input.type === "password";
      reveal.setAttribute(
        "aria-label",
        (hidden ? "Show" : "Hide") + " password",
      );
      reveal.innerHTML = svg(hidden ? "eye" : "eye-off");
    }
  });
  $("detail-content").addEventListener("click", (e) => {
    const backupButton = e.target.closest("[data-backup-action]");
    if (backupButton)
      backupCodeAction(backupButton).catch((error) =>
        toast(error.message, true),
      );
    const copyBtn = e.target.closest("[data-detail-copy]");
    if (copyBtn && detailItem)
      copy(detailItem[copyBtn.dataset.detailCopy], "Copied");
    const code = e.target.closest("[data-detail-code]");
    if (code) itemAction("copy-code", code.dataset.detailCode);
    if (e.target.closest("#detail-reveal") && detailItem) {
      const hidden = $("detail-password").textContent.startsWith("••••");
      $("detail-password").textContent = hidden
        ? detailItem.password
        : "••••••••••••••••";
      $("detail-reveal").innerHTML = svg(hidden ? "eye-off" : "eye");
      $("detail-reveal").setAttribute(
        "aria-label",
        (hidden ? "Hide" : "Show") + " password",
      );
    }
    if (e.target.closest("#detail-delete")) deleteItem();
    if (e.target.closest("#detail-edit") && detailItem) openItem(detailItem.id);
  });
  $("detail-dialog").addEventListener("close", () => {
    detailItem = null;
    $("detail-content").replaceChildren();
  });
  $("utility-dialog").addEventListener("close", () => {
    if (!$("utility-dialog").open) $("utility-content").replaceChildren();
  });
  $("item-dialog").addEventListener("close", () => {
    $("item-password").value = "";
    $("item-secret").value = "";
    $("item-backup-codes").value = "";
    $("item-notes").value = "";
    state.itemIcon = "";
  });
  document.addEventListener("keydown", (e) => {
    if (
      (e.ctrlKey || e.metaKey) &&
      e.key.toLowerCase() === "k" &&
      state.unlocked
    ) {
      e.preventDefault();
      openQuickSearch();
      return;
    }
    const tag = e.target.tagName;
    if (
      e.key === "/" &&
      state.unlocked &&
      !["INPUT", "TEXTAREA", "SELECT"].includes(tag) &&
      !document.querySelector("dialog[open]") &&
      !$("vault-view").hidden
    ) {
      e.preventDefault();
      $("search").focus();
    }
    if (e.key === "Escape") {
      const wasOpen = $("sidebar").classList.contains("open");
      $("sidebar").classList.remove("open");
      $("nav-scrim").hidden = true;
      $("mobile-menu").setAttribute("aria-expanded", "false");
      if (wasOpen) $("mobile-menu").focus();
    }
  });
  for (const name of ["pointerdown", "keydown", "input"])
    document.addEventListener(
      name,
      () => {
        state.lastInput = Date.now();
      },
      {
        passive: true,
      },
    );
  window.addEventListener("pageshow", (e) => {
    if (e.persisted) location.reload();
  });
}

function openQuickSearch() {
  if (!state.unlocked) return;
  closeDialogs();
  $("utility-content").innerHTML =
    `<div class="quick-search-dialog"><div class="quick-search-heading"><div class="search-box"><span>${svg("search")}</span><input id="global-search" role="combobox" aria-label="Search all vault items" aria-autocomplete="list" aria-expanded="true" aria-controls="global-results" placeholder="Search your entire vault…" autocomplete="off"></div><button class="icon-button close-dialog" aria-label="Close search">${svg("x")}</button></div><div id="global-results" class="quick-search-results" role="listbox" aria-label="Matching vault items"></div><div class="quick-search-footer"><span id="quick-search-status" role="status">Search by name, account, or website</span><span class="quick-search-hint">↑ ↓ to select · Enter to open</span></div></div>`;
  let selected = 0;
  const select = (index) => {
    const rows = [...$("global-results").querySelectorAll("button")];
    if (!rows.length) {
      $("global-search").removeAttribute("aria-activedescendant");
      return;
    }
    selected = (index + rows.length) % rows.length;
    rows.forEach((row, i) =>
      row.setAttribute("aria-selected", String(i === selected)),
    );
    $("global-search").setAttribute("aria-activedescendant", rows[selected].id);
    rows[selected].scrollIntoView({ block: "nearest", behavior: "instant" });
  };
  const render = () => {
    const q = $("global-search").value.toLowerCase().trim();
    const found = state.items
      .filter((i) =>
        [i.name, i.username, i.url].some((t) =>
          String(t).toLowerCase().includes(q),
        ),
      )
      .slice(0, 8);
    $("global-results").innerHTML = found.length
      ? found
          .map(
            (i, index) =>
              `<button type="button" class="quick-result" role="option" aria-selected="false" id="global-result-${index}" data-search-id="${esc(i.id)}">${logo(i)}<span class="quick-result-copy"><strong>${esc(i.name)}</strong><small>${esc(i.username || domain(i.url) || "Personal account")}</small></span>${svg("arrow-right")}</button>`,
          )
          .join("")
      : '<div class="no-search-results"><strong>No matching items</strong><span>Try another name, account, or website.</span></div>';
    $("global-search").setAttribute("aria-expanded", String(found.length > 0));
    $("quick-search-status").textContent = found.length
      ? found.length === 8
        ? "Showing up to 8 matches"
        : found.length + " matching items"
      : "No matches";
    select(0);
  };
  $("global-search").addEventListener("input", render);
  $("global-results").addEventListener("click", (e) => {
    const b = e.target.closest("[data-search-id]");
    if (b) {
      $("utility-dialog").close();
      openDetail(b.dataset.searchId);
    }
  });
  $("global-search").addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      select(selected + (e.key === "ArrowDown" ? 1 : -1));
    }
    if (e.key === "Enter") {
      e.preventDefault();
      $("global-results").querySelector('[aria-selected="true"]')?.click();
    }
  });
  render();
  $("utility-dialog").showModal();
  $("global-search").focus();
}

function setLayout(grid) {
  state.grid = grid;
  $("grid-view").classList.toggle("selected", grid);
  $("list-view").classList.toggle("selected", !grid);
  $("grid-view").setAttribute("aria-pressed", String(grid));
  $("list-view").setAttribute("aria-pressed", String(!grid));
  renderItems();
}
async function heartbeat() {
  if (!state.unlocked) return;
  if (
    !state.demo &&
    Date.now() - state.lastInput >= state.settings.auto_lock * 60000
  ) {
    try {
      await api("/lock", "POST");
    } catch {}
    showAuth();
    toast("Vault automatically locked after inactivity.");
    return;
  }
  tickTimers();
  const now = (Date.now() + state.serverOffset) / 1000;
  if (
    state.items.some((i) => i.has_totp && i.expires_at <= now) &&
    Date.now() - lastCodeAttempt > 3000
  )
    await refreshCodes();
  if (
    !state.demo &&
    state.lastInput > state.lastActivity &&
    Date.now() - state.lastActivity > 30000
  ) {
    state.lastActivity = Date.now();
    try {
      await api("/activity", "POST");
    } catch (e) {
      if (e.status !== 401) state.lastActivity = Date.now();
    }
  }
}
async function boot() {
  icons();
  window.KagNodeControls?.enhance();
  bind();
  try {
    const data = await api("/status");
    state.initialized = data.initialized;
    state.preview = data.preview;
    state.account = data.account;
    state.csrf = data.csrf;
    state.settings = data.settings || {
      auto_lock: 15,
    };
    if (new URLSearchParams(location.search).get("demo") === "1")
      await startDemo();
    else if (data.unlocked) await showDashboard();
    else showAuth();
  } catch (e) {
    $("loading-label").textContent = e.message;
    $("loading").querySelector(".loading-dots").hidden = true;
    $("loading").querySelector(".loading-strip").hidden = true;
    $("loading-retry").hidden = false;
    $("loading-retry").addEventListener("click", () => location.reload(), {
      once: true,
    });
  }
  setInterval(heartbeat, 1000);
}
boot();
