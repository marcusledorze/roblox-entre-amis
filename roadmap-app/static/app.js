"use strict";
// Roadmap STEAL A CRYSTAL! — kanban local. Tout le texte passe par textContent (pas d'innerHTML).

const COLORS = { ideas: "--col-ideas", rc: "--col-rc", p1: "--col-p1", p2: "--col-p2", doing: "--col-doing", done: "--col-done" };
const state = { rev: -1, columns: [], cards: [], editing: null, dragId: null };

const $ = (sel) => document.querySelector(sel);
const el = (tag, cls, text) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text != null) n.textContent = text;
  return n;
};

async function api(method, path, body) {
  const opts = { method, headers: {} };
  if (body !== undefined) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify({ ...body, actor: "user" });
  }
  const res = await fetch(path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

function setStatus(text) {
  $("#status").textContent = text;
}

async function load(force) {
  try {
    const data = await api("GET", "/api/board");
    if (!force && data.rev === state.rev) return;
    if (state.editing || state.dragId) return; // ne pas perturber une édition en cours
    Object.assign(state, { rev: data.rev, columns: data.columns, cards: data.cards });
    render();
    setStatus("à jour");
  } catch (e) {
    setStatus("serveur injoignable");
  }
}

function matches(card) {
  if ($("#onlyPending").checked && !card.pending) return false;
  const q = $("#search").value.trim().toLowerCase();
  if (!q) return true;
  return [card.title, card.description, card.theme, card.security].join(" ").toLowerCase().includes(q);
}

function cardEl(card) {
  const li = el("li", "card" + (card.pending ? " pending" : ""));
  li.draggable = true;
  li.tabIndex = 0;
  li.dataset.id = card.id;
  li.append(el("h3", null, card.title));
  if (card.description) li.append(el("p", null, card.description));
  const meta = el("div", "meta");
  if (card.pending) meta.append(el("span", "chip pend", "À traiter"));
  if (card.theme) meta.append(el("span", "chip", card.theme));
  if (card.effort) meta.append(el("span", "chip", "Effort " + card.effort));
  if (card.risk) meta.append(el("span", "chip risk-" + card.risk, "Risque " + card.risk));
  if (card.security) meta.append(el("span", "chip sec", "Sécurité"));
  if (card.notes && card.notes.length) meta.append(el("span", "chip note", "✓ " + card.notes.length + " note(s)"));
  if (meta.childElementCount) li.append(meta);
  li.addEventListener("click", () => openEditor(card));
  li.addEventListener("keydown", (e) => { if (e.key === "Enter") openEditor(card); });
  li.addEventListener("dragstart", (e) => {
    state.dragId = card.id;
    li.classList.add("dragging");
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", card.id);
  });
  li.addEventListener("dragend", () => {
    li.classList.remove("dragging");
    state.dragId = null;
  });
  return li;
}

function dropIndex(list, y) {
  const items = [...list.querySelectorAll(".card:not(.dragging)")];
  const idx = items.findIndex((it) => y < it.getBoundingClientRect().top + it.offsetHeight / 2);
  return idx === -1 ? items.length : idx;
}

function render() {
  const board = $("#board");
  board.replaceChildren();
  let pending = 0;
  for (const col of state.columns) {
    const cards = state.cards.filter((c) => c.column === col.id).sort((a, b) => a.position - b.position);
    pending += cards.filter((c) => c.pending).length;
    const visible = cards.filter(matches);
    const section = el("section", "column");
    section.style.setProperty("--col", `var(${COLORS[col.id] || "--accent"})`);
    const head = el("header");
    head.append(el("h2", null, col.title), el("span", "n", String(visible.length)));
    const add = el("button", "add", "+");
    add.title = "Ajouter une carte dans « " + col.title + " »";
    add.setAttribute("aria-label", add.title);
    add.addEventListener("click", () => openEditor(null, col.id));
    head.append(add);
    const list = el("ul", "cards");
    list.dataset.column = col.id;
    list.addEventListener("dragover", (e) => { e.preventDefault(); list.classList.add("over"); });
    list.addEventListener("dragleave", () => list.classList.remove("over"));
    list.addEventListener("drop", async (e) => {
      e.preventDefault();
      list.classList.remove("over");
      const id = e.dataTransfer.getData("text/plain");
      const position = dropIndex(list, e.clientY);
      state.dragId = null;
      try {
        await api("PATCH", "/api/cards/" + encodeURIComponent(id), { column: col.id, position });
        setStatus("déplacé");
      } catch (err) {
        setStatus("erreur : " + err.message);
      }
      load(true);
    });
    visible.forEach((c) => list.append(cardEl(c)));
    section.append(head, list);
    board.append(section);
  }
  $("#pendingCount").textContent = String(pending);
}

// ---------- éditeur ----------
function openEditor(card, column) {
  const form = $("#editForm");
  const sel = form.elements.column;
  sel.replaceChildren(...state.columns.map((c) => { const o = el("option", null, c.title); o.value = c.id; return o; }));
  state.editing = card ? card.id : "new";
  $("#editTitle").textContent = card ? "Modifier la carte" : "Nouvelle carte";
  for (const f of ["title", "description", "theme", "effort", "risk", "security"]) form.elements[f].value = card ? card[f] || "" : "";
  sel.value = card ? card.column : column || "ideas";
  $("#deleteBtn").hidden = !card;
  $("#formError").textContent = "";
  const notes = $("#notes");
  notes.replaceChildren();
  if (card && (card.pending || (card.notes && card.notes.length))) {
    notes.hidden = false;
    if (card.pending) notes.append(el("p", "pend", "À traiter par Claude : " + (card.pendingReason || "modifiée")));
    if (card.notes && card.notes.length) {
      notes.append(el("h4", null, "Notes de Claude"));
      card.notes.slice(-5).forEach((n) => notes.append(el("p", null, n.at.replace("T", " ") + " — " + n.text)));
    }
  } else {
    notes.hidden = true;
  }
  $("#editor").showModal();
  form.elements.title.focus();
}

function closeEditor() {
  $("#editor").close();
  state.editing = null;
  load(true);
}

$("#editForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target.elements;
  const body = {};
  for (const k of ["title", "description", "theme", "effort", "risk", "security", "column"]) body[k] = f[k].value;
  try {
    if (state.editing === "new") await api("POST", "/api/cards", body);
    else await api("PATCH", "/api/cards/" + encodeURIComponent(state.editing), body);
    setStatus("enregistré");
    closeEditor();
  } catch (err) {
    $("#formError").textContent = err.message;
  }
});
$("#cancelBtn").addEventListener("click", closeEditor);
$("#editor").addEventListener("cancel", () => { state.editing = null; });
$("#editor").addEventListener("close", () => { state.editing = null; });
$("#deleteBtn").addEventListener("click", async () => {
  if (!confirm("Supprimer cette carte ?")) return;
  try {
    await api("DELETE", "/api/cards/" + encodeURIComponent(state.editing));
    setStatus("supprimé");
    closeEditor();
  } catch (err) {
    $("#formError").textContent = err.message;
  }
});

$("#search").addEventListener("input", render);
$("#onlyPending").addEventListener("change", render);

load(true);
setInterval(load, 4000); // Claude peut modifier la roadmap pendant que la page est ouverte
