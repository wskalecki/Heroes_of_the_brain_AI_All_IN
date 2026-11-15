"use strict";

const SVG_NS = "http://www.w3.org/2000/svg";
const $ = (id) => document.getElementById(id);

// Static icon markup (no data in it). The status colour comes from `currentColor`.
const ICONS = {
  good: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="currentColor"/><path d="M7.5 12.5l3 3 6-6.5" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  warning: '<svg viewBox="0 0 24 24"><path d="M12 3 2.2 20.2h19.6z" fill="currentColor" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="M12 9.6v4.8" stroke="#0b0b0b" stroke-width="2.2" stroke-linecap="round"/><circle cx="12" cy="17.4" r="1.2" fill="#0b0b0b"/></svg>',
  critical: '<svg viewBox="0 0 24 24"><path d="M8 2h8l6 6v8l-6 6H8l-6-6V8z" fill="currentColor"/><path d="M8.5 8.5l7 7m0-7l-7 7" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/></svg>',
  info: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="currentColor"/><path d="M9.5 8v8m5-8v8" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/></svg>',
  neutral: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="currentColor"/><circle cx="7.5" cy="12" r="1.4" fill="#fff"/><circle cx="12" cy="12" r="1.4" fill="#fff"/><circle cx="16.5" cy="12" r="1.4" fill="#fff"/></svg>',
};

const STATES = {
  calibrating: { tone: "neutral", label: "Kalibracja", short: "Kalibracja" },
  no_signal: { tone: "neutral", label: "Brak wiarygodnego sygnału", short: "Brak sygnału" },
  break: { tone: "info", label: "Przerwa trwa", short: "Na przerwie" },
  ok: { tone: "good", label: "Możesz pracować", short: "Może pracować" },
  warn: { tone: "warning", label: "Zaplanuj przerwę", short: "Wkrótce przerwa" },
  stop: { tone: "critical", label: "Przerwa teraz", short: "Przerwa teraz" },
};

const FAST_WINDOW_S = 180;
const MAX_HISTORY = 900;
const MAX_TRACE = 4000;

const app = {
  config: null,
  primary: null,
  workers: new Map(),
  scenario: "driver",
  connected: false,
  dirty: false,
};

// ---------- formatting ----------

const decimal = (value, digits = 1) => value.toFixed(digits).replace(".", ",");

function duration(minutes) {
  if (minutes == null) return "—";
  if (minutes < 1) return "mniej niż minutę";
  const total = Math.round(minutes);
  if (total < 60) return `${total} min`;
  const hours = Math.floor(total / 60);
  const rest = total % 60;
  return rest ? `${hours} h ${rest} min` : `${hours} h`;
}

// Polish plural: 1 mrugnięcie, 2-4 mrugnięcia, 5+ mrugnięć.
function plural(n, one, few, many) {
  if (n === 1) return one;
  const tens = n % 100;
  return n % 10 >= 2 && n % 10 <= 4 && (tens < 12 || tens > 14) ? few : many;
}

function clock(hours) {
  const total = Math.round(hours * 60) % (24 * 60);
  return `${String(Math.floor(total / 60)).padStart(2, "0")}:${String(total % 60).padStart(2, "0")}`;
}

function reserveTone(entry) {
  if (!entry || entry.state === "calibrating" || entry.state === "no_signal") return "neutral";
  if (entry.reserve < app.config.stop_below) return "critical";
  if (entry.reserve < app.config.warn_below) return "warning";
  return "good";
}

function advice(entry) {
  const driver = app.scenario === "driver";
  const plan = driver ? "Zaplanuj postój" : "Zaplanuj przerwę";
  const act = driver ? "Zjedź na najbliższy parking." : "Przekaż pacjentów i zrób przerwę.";
  switch (entry.state) {
    case "calibrating":
      return `Patrz spokojnie przed siebie. Postęp: ${Math.round(entry.calibration * 100)}%.`;
    case "no_signal":
      return "Popraw czepek. Bez sygnału system nie zgaduje.";
    case "break":
      return "Odpoczynek trwa, rezerwa wraca.";
    case "ok": {
      const lead = driver ? "Jedź dalej." : "Możesz kontynuować dyżur.";
      return entry.minutes_to_warn == null ? lead : `${lead} Przerwę zaplanuj najpóźniej za ${duration(entry.minutes_to_warn)}.`;
    }
    case "warn":
      if (entry.reserve < app.config.warn_below) return `${plan} w ciągu ${duration(entry.minutes_to_stop)}.`;
      return `Niedawno wykryto spadek czujności. ${plan} przy najbliższej okazji.`;
    case "stop":
      if (entry.lapse && entry.lapse_kind === "eyes_open") {
        return `Senność przy otwartych oczach: oczy są otwarte, ale mózg przestaje reagować. ${act}`;
      }
      if (entry.lapse && entry.lapse_kind === "eyes_closed") return `Oczy zamknięte dłużej niż kilka sekund (mikrosen). ${act}`;
      if (entry.lapse) return `Wykryto spadek czujności. ${act}`;
      if (entry.probe_failed_recently) return `Reakcja za wolna albo jej brak przy sprawdzeniu. ${act}`;
      return `Rezerwa wyczerpana. ${act}`;
    default:
      return "";
  }
}

// ---------- SVG line chart ----------

function svgEl(name, attrs, parent) {
  const node = document.createElementNS(SVG_NS, name);
  for (const [key, value] of Object.entries(attrs || {})) node.setAttribute(key, value);
  if (parent) parent.appendChild(node);
  return node;
}

// Drop x-axis labels that would collide; the first and last labels always stay.
function spaced(ticks, sx, minGap = 86) {
  const kept = [];
  ticks.forEach((tick, i) => {
    const last = i === ticks.length - 1;
    while (last && kept.length > 1 && sx(tick.value) - sx(kept[kept.length - 1].value) < minGap) kept.pop();
    if (!kept.length || last || sx(tick.value) - sx(kept[kept.length - 1].value) >= minGap) kept.push(tick);
  });
  return kept;
}

class Chart {
  constructor(figure, options) {
    this.plot = figure.querySelector(".plot");
    this.tableView = figure.querySelector(".table-view");
    this.toggle = figure.querySelector("[data-table-toggle]");
    this.options = options;
    this.points = [];
    this.bands = [];
    this.cursorPx = null;
    this.pixels = [];

    this.toggle.addEventListener("click", () => {
      const show = this.toggle.getAttribute("aria-pressed") !== "true";
      this.toggle.setAttribute("aria-pressed", String(show));
      this.toggle.textContent = show ? "Wykres" : "Tabela";
      this.plot.hidden = show;
      this.tableView.hidden = !show;
      this.render();
    });
    this.plot.addEventListener("pointermove", (event) => {
      this.cursorPx = event.clientX - this.plot.getBoundingClientRect().left;
      this.render();
    });
    this.plot.addEventListener("pointerleave", () => this.clearCursor());
    this.plot.addEventListener("blur", () => this.clearCursor());
    this.plot.addEventListener("focus", () => {
      const last = this.pixels[this.pixels.length - 1];
      if (last && this.cursorPx == null) { this.cursorPx = last.x; this.render(); }
    });
    this.plot.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      event.preventDefault();
      const current = this.nearest();
      if (current < 0) return;
      const next = Math.min(this.pixels.length - 1, Math.max(0, current + (event.key === "ArrowLeft" ? -1 : 1)));
      this.cursorPx = this.pixels[next].x;
      this.render();
    });
    new ResizeObserver(() => this.render()).observe(this.plot);
  }

  set(points, bands) {
    this.points = points;
    this.bands = bands || [];
    this.render();
  }

  clearCursor() {
    this.cursorPx = null;
    $("tooltip").hidden = true;
    this.render();
  }

  nearest() {
    if (this.cursorPx == null || !this.pixels.length) return -1;
    let best = 0;
    for (let i = 1; i < this.pixels.length; i++) {
      if (Math.abs(this.pixels[i].x - this.cursorPx) < Math.abs(this.pixels[best].x - this.cursorPx)) best = i;
    }
    return best;
  }

  render() {
    if (!app.config) return;
    if (!this.tableView.hidden) return this.renderTable();
    const o = this.options;
    const width = Math.max(320, this.plot.clientWidth);
    const height = o.height;
    const m = { left: 34, right: o.rightMargin, top: 16, bottom: 26 };
    const [x0, x1] = o.xDomain(this.points);
    const [y0, y1] = o.yDomain(this.points);
    const sx = (x) => m.left + ((x - x0) / (x1 - x0)) * (width - m.left - m.right);
    const sy = (y) => height - m.bottom - ((y - y0) / (y1 - y0)) * (height - m.top - m.bottom);
    const right = width - m.right;
    const bottom = height - m.bottom;

    const svg = svgEl("svg", { viewBox: `0 0 ${width} ${height}`, role: "img", "aria-hidden": "true" });

    for (const tick of o.yTicks(y0, y1)) {
      svgEl("line", { x1: m.left, x2: right, y1: sy(tick), y2: sy(tick), stroke: "var(--grid)", "stroke-width": 1 }, svg);
      svgEl("text", { x: m.left - 8, y: sy(tick) + 4, "text-anchor": "end" }, svg).textContent = String(tick);
    }
    svgEl("line", { x1: m.left, x2: right, y1: bottom, y2: bottom, stroke: "var(--axis)", "stroke-width": 1 }, svg);
    for (const tick of spaced(o.xTicks(x0, x1), sx)) {
      svgEl("text", { x: sx(tick.value), y: height - 6, "text-anchor": tick.anchor || "middle" }, svg).textContent = tick.label;
    }

    for (const [from, to] of this.bands) {
      const a = Math.max(m.left, sx(from));
      const b = Math.min(right, Math.max(sx(to), a + 2));
      svgEl("rect", { x: a, y: m.top, width: b - a, height: bottom - m.top, fill: "var(--critical)", opacity: 0.1 }, svg);
      svgEl("rect", { x: a, y: m.top, width: b - a, height: 3, fill: "var(--critical)" }, svg);
    }

    for (const threshold of o.thresholds()) {
      const y = sy(threshold.value);
      svgEl("line", { x1: m.left, x2: right, y1: y, y2: y, stroke: "var(--ink-2)", "stroke-width": 1 }, svg);
      svgEl("text", { x: right + 8, y: y + 4, class: "label-2" }, svg).textContent = threshold.label;
    }

    // Line with gaps where the value is missing (rejected windows).
    this.pixels = [];
    let path = "";
    let pen = false;
    let segmentStart = null;
    const areas = [];
    for (const point of this.points) {
      if (point.y == null || point.x < x0) {
        if (pen && segmentStart) areas.push([segmentStart, this.pixels[this.pixels.length - 1]]);
        pen = false;
        continue;
      }
      const px = { x: sx(point.x), y: sy(Math.min(y1, Math.max(y0, point.y))), point };
      path += `${pen ? "L" : "M"}${px.x.toFixed(1)} ${px.y.toFixed(1)}`;
      if (!pen) segmentStart = px;
      pen = true;
      this.pixels.push(px);
    }
    if (o.area && this.pixels.length > 1) {
      const first = this.pixels[0];
      const last = this.pixels[this.pixels.length - 1];
      svgEl("path", { d: `${path}L${last.x.toFixed(1)} ${bottom}L${first.x.toFixed(1)} ${bottom}Z`, fill: "var(--series-1)", opacity: 0.1 }, svg);
    }
    if (path) {
      svgEl("path", { d: path, fill: "none", stroke: "var(--series-1)", "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }, svg);
    }

    const last = this.pixels[this.pixels.length - 1];
    if (last) {
      svgEl("circle", { cx: last.x, cy: last.y, r: 4, fill: "var(--series-1)", stroke: "var(--surface)", "stroke-width": 2 }, svg);
      const label = svgEl("text", { x: last.x - 8, y: Math.max(m.top + 12, last.y - 10), "text-anchor": "end", class: "label-strong" }, svg);
      label.textContent = o.formatValue(last.point.y);
    }

    const index = this.nearest();
    if (index >= 0) {
      const hit = this.pixels[index];
      svgEl("line", { x1: hit.x, x2: hit.x, y1: m.top, y2: bottom, stroke: "var(--ink-2)", "stroke-width": 1 }, svg);
      svgEl("circle", { cx: hit.x, cy: hit.y, r: 4, fill: "var(--series-1)", stroke: "var(--surface)", "stroke-width": 2 }, svg);
      this.showTooltip(hit);
    }

    this.plot.replaceChildren(svg);
  }

  showTooltip(hit) {
    const tooltip = $("tooltip");
    const value = document.createElement("span");
    value.className = "tooltip-value";
    value.textContent = this.options.formatValue(hit.point.y);
    const label = document.createElement("span");
    label.className = "tooltip-label";
    label.textContent = ` ${this.options.formatX(hit.point.x)}`;
    tooltip.replaceChildren(value, label);
    tooltip.hidden = false;
    const box = this.plot.getBoundingClientRect();
    const left = Math.min(window.innerWidth - tooltip.offsetWidth - 8, Math.max(8, box.left + hit.x + 12));
    tooltip.style.left = `${left}px`;
    tooltip.style.top = `${Math.max(8, box.top + hit.y - tooltip.offsetHeight - 10)}px`;
  }

  renderTable() {
    const table = document.createElement("table");
    const head = table.createTHead().insertRow();
    for (const title of this.options.tableHead) {
      const cell = document.createElement("th");
      cell.scope = "col";
      cell.textContent = title;
      head.appendChild(cell);
    }
    const body = table.createTBody();
    const rows = this.points.filter((point) => point.y != null).slice(-this.options.tableRows).reverse();
    for (const point of rows) {
      const row = body.insertRow();
      row.insertCell().textContent = this.options.formatX(point.x);
      row.insertCell().textContent = this.options.formatValue(point.y);
    }
    this.tableView.replaceChildren(table);
  }
}

const charts = {};

function buildCharts() {
  charts.fast = new Chart($("chart-fast"), {
    height: 230,
    rightMargin: 48,
    xDomain: () => [-FAST_WINDOW_S, 0],
    yDomain: (points) => {
      const top = Math.max(6, ...points.map((p) => (p.y == null ? 0 : p.y + 1)));
      return [-3, Math.ceil(top)];
    },
    yTicks: (y0, y1) => {
      const ticks = [];
      for (let v = 0; v <= y1; v += 5) ticks.push(v);
      return ticks;
    },
    xTicks: () => [
      { value: -180, label: "3 min temu", anchor: "start" },
      { value: -120, label: "2 min" },
      { value: -60, label: "1 min" },
      { value: 0, label: "teraz", anchor: "end" },
    ],
    thresholds: () => [{ value: app.config.z_enter, label: "próg" }],
    formatValue: (y) => decimal(y),
    formatX: (x) => (x >= -0.5 ? "teraz" : `${Math.round(-x)} s temu`),
    tableHead: ["Kiedy", "Wskaźnik (z-score)"],
    tableRows: 30,
  });
  charts.reserve = new Chart($("chart-reserve"), {
    height: 230,
    rightMargin: 122,
    area: true,
    xDomain: (points) => {
      const end = points.length ? points[points.length - 1].x : 0;
      return [0, Math.max(60, Math.ceil(end / 30) * 30)];
    },
    yDomain: () => [0, 100],
    yTicks: () => [0, 25, 50, 75, 100],
    xTicks: (x0, x1) => {
      const step = x1 <= 120 ? 30 : x1 <= 360 ? 60 : 120;
      const ticks = [];
      for (let v = 0; v <= x1; v += step) {
        ticks.push({ value: v, label: v === 0 ? "start" : duration(v), anchor: v === 0 ? "start" : v === x1 ? "end" : "middle" });
      }
      return ticks;
    },
    thresholds: () => [
      { value: app.config.warn_below, label: "zaplanuj przerwę" },
      { value: app.config.stop_below, label: "przerwa teraz" },
    ],
    formatValue: (y) => `${Math.round(y)}%`,
    formatX: (x) => (x < 1 ? "start zmiany" : `po ${duration(x)} pracy`),
    tableHead: ["Czas pracy", "Rezerwa"],
    tableRows: 30,
  });
}

// ---------- rendering ----------

function latest(worker) {
  return worker && worker.history.length ? worker.history[worker.history.length - 1] : null;
}

function setIcon(node, tone) {
  node.innerHTML = ICONS[tone];
}

function renderWorker() {
  const worker = app.workers.get(app.primary);
  if (!worker) return;
  const entry = latest(worker);
  $("worker-name").textContent = worker.name;

  const badge = $("source-badge");
  badge.dataset.kind = app.connected ? (worker.live ? "live" : "replay") : "off";
  badge.textContent = app.connected ? (worker.live ? "na żywo" : "odtworzenie nagrania") : "rozłączono";

  const banner = $("state");
  if (worker.error || !entry) {
    banner.dataset.tone = "neutral";
    setIcon($("state-icon"), "neutral");
    $("state-label").textContent = worker.error ? "Brak połączenia ze źródłem" : "Czekam na sygnał";
    $("state-advice").textContent = worker.error || "";
    return;
  }

  const view = STATES[entry.state];
  banner.dataset.tone = view.tone;
  setIcon($("state-icon"), view.tone);
  $("state-label").textContent = view.label;
  $("state-advice").textContent = advice(entry);

  const calibrating = entry.state === "calibrating";
  $("reserve-value").textContent = calibrating ? "—" : String(Math.round(entry.reserve));
  const meter = $("reserve-meter");
  meter.dataset.tone = reserveTone(entry);
  meter.setAttribute("aria-valuenow", String(Math.round(entry.reserve)));
  $("reserve-fill").style.width = `${calibrating ? 0 : entry.reserve}%`;

  $("tile-work").textContent = calibrating ? "—" : duration(entry.work_min);
  $("sub-work").textContent = entry.awake_h == null
    ? (entry.clock_h == null ? "" : `godzina ${clock(entry.clock_h)}`)
    : `${decimal(entry.awake_h, 1)} h od przebudzenia, godz. ${clock(entry.clock_h)}`;
  $("tile-drain").textContent = calibrating ? "—" : `${decimal(entry.drain_per_hour, 0)}% / h`;
  $("sub-drain").textContent = entry.context_factor && entry.context_factor > 1.005
    ? `pora doby i czuwanie: ×${decimal(entry.context_factor, 2)}`
    : "";
  const eyes = { open: "otwarte", closed: "zamknięte" };
  $("tile-eyes").textContent = eyes[entry.eye_state] || "—";
  $("sub-eyes").textContent = entry.blinks_per_min == null ? "ustalanie progu mrugnięć" : `${Math.round(entry.blinks_per_min)} ${plural(Math.round(entry.blinks_per_min), "mrugnięcie", "mrugnięcia", "mrugnięć")} / min`;
  $("tile-lapses").textContent = String(entry.lapse_count);
  $("sub-lapses").textContent = entry.lapse_count
    ? `oczy zamknięte: ${entry.lapses_eyes_closed}, otwarte: ${entry.lapses_eyes_open}`
    : "";
  $("tile-rt").textContent = entry.probes_done ? (entry.last_rt_ms == null ? "brak" : `${Math.round(entry.last_rt_ms)} ms`) : "—";
  $("sub-rt").textContent = entry.probes_done
    ? `prób: ${entry.probes_done}, za wolnych lub bez reakcji: ${entry.probe_lapses}`
    : `próba pojawi się po spadku czujności i co ${Math.round(app.config.probe_interval_s / 60)} min`;
  $("tile-quality").textContent = `${Math.round(entry.quality * 100)}%`;
  $("btn-break").textContent = entry.on_break ? "Zakończ przerwę" : "Rozpocznij przerwę";

  const now = entry.t;
  const recent = worker.history.filter((e) => e.t >= now - FAST_WINDOW_S);
  const bands = [];
  let start = null;
  for (const e of recent) {
    if (e.lapse && start == null) start = e.t - now;
    if (!e.lapse && start != null) { bands.push([start, e.t - now]); start = null; }
  }
  if (start != null) bands.push([start, 0]);
  charts.fast.set(recent.map((e) => ({ x: e.t - now, y: e.calibration < 1 ? null : e.fast })), bands);

  const stride = Math.max(1, Math.ceil(worker.trace.length / 600));
  const trace = worker.trace.filter((_, i) => i % stride === 0).map(([x, y]) => ({ x, y }));
  if (!calibrating) trace.push({ x: entry.work_min, y: entry.reserve });
  charts.reserve.set(trace, []);
}

function renderTeam() {
  const list = $("team-list");
  const rows = [];
  let stopped = null;
  let best = null;
  for (const worker of app.workers.values()) {
    const entry = latest(worker);
    const view = entry && !worker.error ? STATES[entry.state] : { tone: "neutral", short: worker.error ? "Brak połączenia" : "Czeka na sygnał" };
    const known = entry && !worker.error && entry.state !== "calibrating" && entry.state !== "no_signal";

    const row = document.createElement("li");
    row.className = "team-row";
    const name = document.createElement("span");
    name.className = "team-name";
    name.textContent = worker.name;
    const status = document.createElement("span");
    status.className = "team-status";
    status.dataset.tone = view.tone;
    const icon = document.createElement("span");
    icon.className = "state-icon";
    icon.setAttribute("aria-hidden", "true");
    setIcon(icon, view.tone);
    const text = document.createElement("span");
    text.textContent = view.short;
    status.append(icon, text);
    const meter = document.createElement("div");
    meter.className = "meter";
    meter.dataset.tone = known ? reserveTone(entry) : "neutral";
    const fill = document.createElement("div");
    fill.className = "meter-fill";
    fill.style.width = `${known ? entry.reserve : 0}%`;
    meter.appendChild(fill);
    const value = document.createElement("span");
    value.className = "team-value";
    value.textContent = known ? `${Math.round(entry.reserve)}%` : "—";
    row.append(name, status, meter, value);
    rows.push(row);

    if (known && entry.state === "stop" && !stopped) stopped = worker;
    if (known && entry.state === "ok" && (!best || entry.reserve > latest(best).reserve)) best = worker;
  }
  list.replaceChildren(...rows);

  const note = $("team-advice");
  note.hidden = !stopped;
  if (stopped) {
    note.textContent = best
      ? `${stopped.name}: przerwa teraz. Najwięcej rezerwy ma ${best.name} (${Math.round(latest(best).reserve)}%).`
      : `${stopped.name}: przerwa teraz. Nikt z zespołu nie ma teraz pełnej gotowości.`;
  }
}

function render() {
  app.dirty = false;
  if (!app.config) return;
  renderWorker();
  renderTeam();
}

function schedule() {
  if (app.dirty) return;
  app.dirty = true;
  requestAnimationFrame(render);
}

function placeMeterMarks() {
  $("mark-stop").style.left = `calc(${app.config.stop_below}% - 1px)`;
  $("mark-warn").style.left = `calc(${app.config.warn_below}% - 1px)`;
  $("meter-legend").textContent =
    `Poniżej ${app.config.warn_below}%: zaplanuj przerwę. Poniżej ${app.config.stop_below}%: przerwa teraz.`;
  const scaleValue = app.config.time_scale;
  $("time-note").textContent =
    scaleValue === 1 ? "" : scaleValue === 60 ? "Demo: 1 minuta na ekranie to 1 godzina zmiany." : `Demo: czas zmiany płynie ${scaleValue} razy szybciej.`;
}

// ---------- connection ----------

let socket = null;

function send(action) {
  if (socket && socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify({ action, worker: app.primary }));
}

function onMessage(message) {
  if (message.type === "hello") {
    probe.cancel();
    app.config = message.config;
    app.primary = message.primary;
    app.workers = new Map(message.workers.map((w) => [w.id, { ...w }]));
    placeMeterMarks();
  } else if (message.type === "update") {
    const worker = app.workers.get(message.worker);
    if (!worker) return;
    worker.error = null;
    worker.history.push(message.data);
    if (worker.history.length > MAX_HISTORY) worker.history.shift();
    if (message.data.state !== "calibrating") {
      worker.trace.push([message.data.work_min, message.data.reserve]);
      if (worker.trace.length > MAX_TRACE) worker.trace.shift();
    }
  } else if (message.type === "status") {
    const worker = app.workers.get(message.worker);
    if (worker) worker.error = message.error;
  } else if (message.type === "probe") {
    probe.show(message);
    return;
  }
  schedule();
}

// ---------- reaction probe ----------

const probe = {
  active: null,
  timer: null,

  cancel() {
    clearTimeout(this.timer);
    this.active = null;
    $("probe").hidden = true;
  },

  show(message) {
    if (this.active) return;
    this.active = {
      id: message.id,
      worker: message.worker,
      shownAt: 0,
      thresholdMs: message.threshold_ms || app.config.probe_lapse_ms,
    };
    const target = $("probe-target");
    delete target.dataset.result;
    $("probe-title").textContent = "Reakcja!";
    const why = { event: "Sprawdzenie po spadku czujności", schedule: "Kontrola okresowa", manual: "Sprawdzenie" };
    $("probe-text").textContent = `${why[message.reason] || "Sprawdzenie"}: naciśnij spację albo kliknij`;
    $("probe").hidden = false;
    beep();
    // Measure from the first frame the prompt is actually on screen.
    requestAnimationFrame(() => {
      if (!this.active) return;
      this.active.shownAt = performance.now();
      target.focus();
      this.timer = setTimeout(() => this.finish(null), message.timeout_ms || app.config.probe_timeout_ms);
    });
  },

  respond() {
    if (!this.active || !this.active.shownAt) return;
    this.finish(performance.now() - this.active.shownAt);
  },

  finish(rtMs) {
    if (!this.active) return;
    clearTimeout(this.timer);
    const { id, worker, thresholdMs } = this.active;
    this.active = null;
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ action: "probe_response", worker, id, rt_ms: rtMs == null ? null : Math.round(rtMs) }));
    }
    const lapse = rtMs == null || rtMs > thresholdMs;
    $("probe-target").dataset.result = lapse ? "lapse" : "ok";
    $("probe-title").textContent = rtMs == null ? "Brak reakcji" : `${Math.round(rtMs)} ms`;
    $("probe-text").textContent = lapse ? "Reakcja za wolna: to liczy się jako spadek czujności" : "Reakcja w normie";
    setTimeout(() => { if (!this.active) $("probe").hidden = true; }, 1500);
  },
};

let audio = null;
function beep() {
  try {
    audio = audio || new (window.AudioContext || window.webkitAudioContext)();
    const osc = audio.createOscillator();
    const gain = audio.createGain();
    osc.frequency.value = 880;
    gain.gain.setValueAtTime(0.15, audio.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audio.currentTime + 0.25);
    osc.connect(gain).connect(audio.destination);
    osc.start();
    osc.stop(audio.currentTime + 0.25);
  } catch (error) { /* sound is optional */ }
}

function connect() {
  const scheme = location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(`${scheme}://${location.host}/ws`);
  socket.addEventListener("open", () => { app.connected = true; schedule(); });
  socket.addEventListener("message", (event) => onMessage(JSON.parse(event.data)));
  socket.addEventListener("close", () => {
    app.connected = false;
    schedule();
    setTimeout(connect, 1000);
  });
}

// ---------- controls ----------

function setScenario(name) {
  app.scenario = name;
  for (const button of document.querySelectorAll("[data-scenario]")) {
    button.setAttribute("aria-pressed", String(button.dataset.scenario === name));
  }
  try { localStorage.setItem("wachta-scenario", name); } catch (error) { /* storage can be unavailable */ }
  schedule();
}

function init() {
  buildCharts();
  for (const button of document.querySelectorAll("[data-scenario]")) {
    button.addEventListener("click", () => setScenario(button.dataset.scenario));
  }
  try {
    const saved = localStorage.getItem("wachta-scenario");
    if (saved === "driver" || saved === "nurse") setScenario(saved);
  } catch (error) { /* storage can be unavailable */ }

  $("btn-break").addEventListener("click", () => {
    const entry = latest(app.workers.get(app.primary));
    send(entry && entry.on_break ? "break_end" : "break_start");
  });
  $("btn-calibrate").addEventListener("click", () => send("recalibrate"));
  $("btn-probe").addEventListener("click", () => send("probe_now"));
  $("probe-target").addEventListener("pointerdown", (event) => { event.preventDefault(); probe.respond(); });
  document.addEventListener("keydown", (event) => {
    if (probe.active && (event.code === "Space" || event.key === "Enter")) {
      event.preventDefault();
      probe.respond();
    }
  });
  $("btn-reset").addEventListener("click", () => send("reset"));
  connect();
}

init();
