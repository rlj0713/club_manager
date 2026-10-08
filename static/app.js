const state = {
  user: null,
  clubs: [],
  events: [],
  calendarMonth: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
  eventClubId: null,
};
const $ = (selector) => document.querySelector(selector);

async function api(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const text = response.status === 204 ? "" : await response.text();
  let body = null;
  if (text) {
    try { body = JSON.parse(text); }
    catch { body = { error: `Server returned an unexpected response (${response.status})` }; }
  }
  if (!response.ok) throw new Error(body?.error || `Request failed (${response.status})`);
  return body;
}

function message(text, isError = false) {
  $("#message").textContent = text;
  $("#message").className = isError ? "message error" : "message";
}

function formData(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function showApp() {
  $("#auth-panel").classList.add("hidden");
  $("#app-panel").classList.remove("hidden");
  $("#session-status").classList.remove("hidden");
  $("#current-user").textContent =
    `Signed in as ${state.user.name} (${state.user.email})${state.user.is_admin ? " — admin" : ""}`;
  $("#profile-link").href = `/users/${state.user.id}`;
}

function showAuth() {
  $("#app-panel").classList.add("hidden");
  $("#session-status").classList.add("hidden");
  $("#auth-panel").classList.remove("hidden");
}

async function signIn(path, form) {
  try {
    state.user = await api(path, { method: "POST", body: JSON.stringify(formData(form)) });
    showApp();
    navigate(`/users/${state.user.id}`);
    message("Signed in.");
  } catch (error) { message(error.message, true); }
}

function profileView() {
  const user = state.user;
  $("#view").innerHTML = `
    <div class="card"><h2>Your profile</h2>
      <form id="profile-form" class="form">
        <label>Name <input name="name" value="${escapeHtml(user.name)}" required></label>
        <label>Username <input name="username" value="${escapeHtml(user.username)}" required></label>
        <label>Email <input name="email" type="email" value="${escapeHtml(user.email)}" required></label>
        <label>New password <input name="password" type="password" placeholder="Leave blank to keep current"></label>
        <button type="submit">Save profile</button>
      </form>
      <div class="actions"><button id="delete-account" class="danger">Delete account</button></div>
    </div>`;
  $("#profile-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = formData(event.target);
    if (!data.password) delete data.password;
    try {
      state.user = await api(`/api/users/${user.id}`, { method: "PUT", body: JSON.stringify(data) });
      showApp(); profileView(); message("Profile updated.");
    } catch (error) { message(error.message, true); }
  });
  $("#delete-account").addEventListener("click", async () => {
    try {
      await api(`/api/users/${user.id}`, { method: "DELETE" });
      state.user = null; showAuth(); message("Account deleted.");
    } catch (error) { message(error.message, true); }
  });
}

const clubColors = ["#1769aa", "#7c3aed", "#c2410c", "#047857", "#b42318", "#a21caf"];

function clubColor(clubId) {
  return clubColors[clubId % clubColors.length];
}

function escapeAttribute(value) {
  return escapeHtml(value).replace(/"/g, "&quot;");
}

function formatEventDate(value) {
  return new Intl.DateTimeFormat(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function calendarView(events, calendarMonth) {
  const year = calendarMonth.getFullYear();
  const month = calendarMonth.getMonth();
  const firstDay = new Date(year, month, 1).getDay();
  const lastDate = new Date(year, month + 1, 0).getDate();
  const eventsByDay = new Map();

  for (const event of events) {
    const date = new Date(event.date);
    if (date.getFullYear() !== year || date.getMonth() !== month) continue;
    const dayEvents = eventsByDay.get(date.getDate()) || [];
    dayEvents.push(event);
    eventsByDay.set(date.getDate(), dayEvents);
  }

  const cells = [];
  for (let index = 0; index < firstDay; index += 1) {
    cells.push('<div class="calendar-day empty"></div>');
  }
  for (let day = 1; day <= lastDate; day += 1) {
    const dayEvents = eventsByDay.get(day) || [];
    cells.push(`<div class="calendar-day"><div class="calendar-date">${day}</div>${dayEvents.map(event =>
      `<a class="calendar-event" href="/events/${event.id}" style="--club-color:${clubColor(event.club_id)}" title="${escapeAttribute(event.name)}">${escapeHtml(event.name)}</a>`
    ).join("")}</div>`);
  }
  while (cells.length % 7 !== 0) {
    cells.push('<div class="calendar-day empty"></div>');
  }

  return `<div class="calendar">${["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    .map(day => `<div class="calendar-heading">${day}</div>`).join("")}${cells.join("")}</div>`;
}

function renderDashboard() {
  const visibleClubs = state.user.is_admin
    ? state.clubs
    : state.clubs.filter(club => club.members.includes(state.user.username));
  const month = new Intl.DateTimeFormat(undefined, { month: "long", year: "numeric" })
    .format(state.calendarMonth);

  $("#view").innerHTML = `${visibleClubs.length ? `<div class="club-list">${visibleClubs.map(club => `
        <a class="club-card" href="/clubs/${club.id}" style="--club-color:${clubColor(club.id)}">
          <h3>${escapeHtml(club.name)}</h3><p>${club.members.length} member${club.members.length === 1 ? "" : "s"}</p>
        </a>`).join("")}</div>` : "<p>You do not belong to any clubs yet.</p>"}
      ${state.user.is_admin ? `<div class="actions dashboard-actions">
        <a href="/clubs">Add club</a>
      </div>` : ""}
      <div class="calendar-nav">
        <button type="button" data-calendar-month="-1" aria-label="Previous month">&larr;</button>
        <h2>${escapeHtml(month)} events</h2>
        <button type="button" data-calendar-month="1" aria-label="Next month">&rarr;</button>
      </div>
      ${calendarView(state.events, state.calendarMonth)}`;
  bindDashboardActions();
}

async function dashboardView() {
  try {
    [state.clubs, state.events] = await Promise.all([api("/api/clubs"), api("/api/events")]);
    renderDashboard();
  } catch (error) { message(error.message, true); }
}

function bindDashboardActions() {
  document.querySelectorAll("[data-calendar-month]").forEach(button => button.addEventListener("click", () => {
    state.calendarMonth = new Date(
      state.calendarMonth.getFullYear(),
      state.calendarMonth.getMonth() + Number(button.dataset.calendarMonth),
      1,
    );
    renderDashboard();
  }));
}

async function clubsView() {
  try {
    state.clubs = await api("/api/clubs");
    $("#view").innerHTML = `<h2>Clubs</h2>${state.clubs.map(club => `
      <article class="item"><h3><a href="/clubs/${club.id}">${escapeHtml(club.name)}</a></h3>
        <p>Members: ${club.members.map(escapeHtml).join(", ") || "None"}</p>
      </article>`).join("")}
      ${state.user.is_admin ? `<div class="card"><h3>New club</h3>
        <form id="new-club" class="inline"><label>Name <input name="name" required></label><button>Create</button></form>
      </div>` : ""}`;
    bindClubActions();
  } catch (error) { message(error.message, true); }
}

function bindClubActions() {
  $("#new-club")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    try { await api("/api/clubs", { method: "POST", body: JSON.stringify(formData(event.target)) }); clubsView(); }
    catch (error) { message(error.message, true); }
  });
}

async function eventsView() {
  try {
    [state.events, state.clubs] = await Promise.all([api("/api/events"), api("/api/clubs")]);
    $("#view").innerHTML = `<h2>Events</h2>${state.events.map(event => `
      <article class="item"><h3><a href="/events/${event.id}">${escapeHtml(event.name)}</a></h3>
        <p>${escapeHtml(event.location)} · ${new Date(event.date).toLocaleString()}</p>
      </article>`).join("") || "<p>No events are available for your clubs.</p>"}
      ${state.user.is_admin ? `<div class="card"><h3>New event</h3>
        <form id="new-event" class="form"><label>Name <input name="name" required></label>
        <label>Location <input name="location" required></label>
        <label>Date and time <input name="date" type="datetime-local" required></label>
        <label>Club <select name="club_id" required>${state.clubs.map(c => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join("")}</select></label>
        <button>Create</button></form>
      </div>` : ""}`;
    bindEventActions();
  } catch (error) { message(error.message, true); }
}

function bindEventActions() {
  $("#new-event")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = formData(event.target); data.club_id = Number(data.club_id);
    try { await api("/api/events", { method: "POST", body: JSON.stringify(data) }); eventsView(); }
    catch (error) { message(error.message, true); }
  });
}

async function showView(view) {
  if (view === "dashboard") await dashboardView();
  if (view === "profile") profileView();
  if (view === "clubs") await clubsView();
  if (view === "events") await eventsView();
}

async function clubDetailView(clubId) {
  try {
    const club = await api(`/api/clubs/${clubId}`);
    $("#view").innerHTML = `<div class="card"><h2>${escapeHtml(club.name)}</h2>
      <p>Members: ${club.members.map(escapeHtml).join(", ") || "None"}</p>
      <h3>Events</h3>
      <ul class="club-event-list">${club.events.map(event => `<li><a class="club-event-link" href="/events/${event.id}"><strong>${escapeHtml(event.name)}</strong><span>${formatEventDate(event.date)}</span></a></li>`).join("") || "<li>No events</li>"}</ul>
      ${state.user.is_admin ? `<h3>Admin controls</h3>
        <form id="club-name-form" class="form">
          <label>Club name <input name="name" value="${escapeAttribute(club.name)}" required></label>
          <button type="submit">Save club</button>
        </form>
        <form id="club-member-form" class="form">
          <label>Username or email <input name="identifier" required></label>
          <button type="submit">Add member</button>
        </form>
        <form id="club-event-form" class="form">
          <label>Event name <input name="name" required></label>
          <label>Location <input name="location" required></label>
          <label>Date and time <input name="date" type="datetime-local" required></label>
          <button type="submit">Create event</button>
        </form>
        <button type="button" class="danger" id="delete-club">Delete club</button>` : ""}
    </div>`;
    $("#club-name-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        await api(`/api/clubs/${club.id}`, { method: "PUT", body: JSON.stringify(formData(event.target)) });
        clubDetailView(club.id);
        message("Club updated.");
      } catch (error) { message(error.message, true); }
    });
    $("#club-member-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const identifier = formData(event.target).identifier;
      try {
        await api(`/api/clubs/${club.id}/members`, { method: "POST", body: JSON.stringify({ username: identifier }) });
        clubDetailView(club.id);
        message("Member added.");
      } catch (error) { message(error.message, true); }
    });
    $("#club-event-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const data = formData(event.target);
      data.club_id = club.id;
      try {
        const createdEvent = await api("/api/events", { method: "POST", body: JSON.stringify(data) });
        window.location.href = `/events/${createdEvent.id}`;
      } catch (error) { message(error.message, true); }
    });
    $("#delete-club")?.addEventListener("click", async () => {
      try {
        await api(`/api/clubs/${club.id}`, { method: "DELETE" });
        window.location.href = "/clubs";
      } catch (error) { message(error.message, true); }
    });
  } catch (error) { message(error.message, true); }
}

async function eventDetailView(eventId) {
  try {
    const event = await api(`/api/events/${eventId}`);
    $("#view").innerHTML = `<div class="card"><h2>${escapeHtml(event.name)}</h2>
      <p>${escapeHtml(event.location)} · ${new Date(event.date).toLocaleString()}</p>
      ${state.user.is_admin ? `<form id="event-detail-form" class="form">
        <label>Name <input name="name" value="${escapeAttribute(event.name)}" required></label>
        <label>Location <input name="location" value="${escapeAttribute(event.location)}" required></label>
        <label>Date and time <input name="date" type="datetime-local" value="${escapeAttribute(event.date.slice(0, 16))}" required></label>
        <button type="submit">Save event</button>
        <button type="button" class="danger" id="delete-event-detail">Delete event</button>
      </form>` : ""}</div>`;
    $("#event-detail-form")?.addEventListener("submit", async (formEvent) => {
      formEvent.preventDefault();
      try {
        await api(`/api/events/${event.id}`, { method: "PUT", body: JSON.stringify(formData(formEvent.target)) });
        window.location.href = "/";
      } catch (error) { message(error.message, true); }
    });
    $("#delete-event-detail")?.addEventListener("click", async () => {
      try {
        await api(`/api/events/${event.id}`, { method: "DELETE" });
        window.location.href = "/events";
      } catch (error) { message(error.message, true); }
    });
  } catch (error) { message(error.message, true); }
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[char]));
}

function navigate(path) {
  history.pushState({}, "", path);
  route();
}

function route() {
  if (!state.user) {
    showAuth();
    const register = location.pathname === "/register";
    $("#login-form").classList.toggle("hidden", register);
    $("#register-form").classList.toggle("hidden", !register);
    document.querySelectorAll(".tab").forEach(tab => tab.classList.toggle("active", register === (tab.dataset.authTab === "register")));
    return;
  }

  showApp();
  const page = document.body.dataset.page;
  if (page === "dashboard") showView("dashboard");
  else if (page === "clubs") showView("clubs");
  else if (page === "club-detail") clubDetailView(Number(location.pathname.split("/").pop()));
  else if (page === "events") showView("events");
  else if (page === "event-detail") eventDetailView(Number(location.pathname.split("/").pop()));
  else if (location.pathname === `/users/${state.user.id}` || location.pathname === "/") showView("profile");
  else navigate(`/users/${state.user.id}`);
}

document.querySelectorAll("[data-auth-tab]").forEach(button => button.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach(tab => tab.classList.remove("active"));
  button.classList.add("active");
  $("#login-form").classList.toggle("hidden", button.dataset.authTab !== "login");
  $("#register-form").classList.toggle("hidden", button.dataset.authTab !== "register");
  history.pushState({}, "", button.dataset.authTab === "register" ? "/register" : "/login");
}));
$("#login-form").addEventListener("submit", event => { event.preventDefault(); signIn("/api/login", event.target); });
$("#register-form").addEventListener("submit", event => { event.preventDefault(); signIn("/api/users", event.target); });
window.addEventListener("popstate", route);
$("#logout-button").addEventListener("click", async () => {
  await api("/api/logout", { method: "POST" });
  state.user = null; navigate("/login"); message("Signed out.");
});

api("/api/me")
  .then(user => { state.user = user; route(); })
  .catch(() => route());
