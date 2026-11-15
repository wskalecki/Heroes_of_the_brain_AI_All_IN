// Records the real Wachta dashboard while it replays a team EEG recording, driven by the demo beats
// from docs/scenariusz-demo.md. Output: JPEG frames (device pixels, via CDP screenshots), a frame index and events.json
// (WebSocket updates, probes, cursor path, clicks, element rectangles) for build-demo-video.py.
//
//   node submission/capture-dashboard.js OUT_DIR [PYTHON] [RECORDING] [START_S]
//
// Needs: node + playwright (Chromium), the wachta package on PYTHONPATH (src/) and the recordings in data/recordings.
// The capture runs in real time (about 3 minutes). Nothing is written into the repository.

const { chromium } = require("playwright");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const OUT = path.resolve(process.argv[2] || "capture");
const PY = process.argv[3] || "python3";
const RECORDING = process.argv[4] || "wojtek";
const START_S = process.argv[5] || "200";
const REPO = path.resolve(__dirname, "..");
const PORT = 8765;
// The dashboard page is 1172 CSS px tall, so the viewport must be at least that tall to show the supervisor panel.
const VIEW = { width: 1920, height: 1180 };
const DPR = 1.25;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const now = () => Date.now() / 1000;

const events = [];      // named beats with timestamps and visible texts
const updates = [];     // main worker updates (1 per window)
const probes = [];      // probe messages from the server
const cursor = [];      // {t, x, y}
const clicks = [];      // {t, x, y}
let latest = null;
let frameCount = 0;

async function main() {
  fs.mkdirSync(path.join(OUT, "frames"), { recursive: true });
  const server = spawn(PY, ["-m", "wachta.server", "--file", RECORDING, "--start", START_S, "--port", String(PORT),
    "--time-scale", "10", "--wake", "07:00", "--clock", "02:30", "--team", "rudy:380", "adi:370"], {
    cwd: REPO, env: { ...process.env, PYTHONPATH: path.join(REPO, "src"), PYTHONDONTWRITEBYTECODE: "1" },
  });
  server.stderr.on("data", (d) => process.stderr.write(`[server] ${d}`));
  server.stdout.on("data", (d) => process.stderr.write(`[server] ${d}`));
  const serverStart = now();

  const browser = await chromium.launch();
  try {
    await run(browser);
  } finally {
    await browser.close();
    server.kill();
  }
  console.log(`done: ${frameCount} frames, server up ${(now() - serverStart).toFixed(0)} s`);
}

async function run(browser) {
  const context = await browser.newContext({ viewport: VIEW, deviceScaleFactor: DPR });
  const page = await context.newPage();
  const cdp = await context.newCDPSession(page);

  // Frames: the CDP screencast only delivers CSS pixels, so take device-pixel screenshots (clip.scale) in a loop instead.
  const frames = [];
  let capturing = false;
  async function captureLoop() {
    while (capturing) {
      const t0 = now();
      let shot;
      try { shot = await cdp.send("Page.captureScreenshot", { format: "jpeg", quality: 86, clip: { x: 0, y: 0, width: VIEW.width, height: VIEW.height, scale: DPR } }); } catch { break; }
      const t1 = now();
      const name = `f${String(frameCount++).padStart(6, "0")}.jpg`;
      frames.push([(t0 + t1) / 2, name]);
      fs.writeFile(path.join(OUT, "frames", name), Buffer.from(shot.data, "base64"), () => {});
    }
  }

  page.on("websocket", (ws) => {
    ws.on("framereceived", (e) => {
      let msg;
      try { msg = JSON.parse(e.payload); } catch { return; }
      const t = now();
      if (msg.type === "update" && msg.worker === "w0") {
        latest = msg.data;
        updates.push({ ...msg.data, rec_t: msg.data.t, t });
      } else if (msg.type === "update") {
        updates.push({ t, worker: msg.worker, state: msg.data.state, reserve: msg.data.reserve, team: true });
      } else if (msg.type === "probe") {
        probes.push({ t, ...msg });
      }
    });
  });
  page.on("pageerror", (e) => console.error("pageerror", e.message));
  page.on("console", (m) => { if (m.type() === "error") console.error("console error", m.text()); });

  // Wait until the server has loaded the recording.
  for (let i = 0; i < 120; i++) {
    try { const r = await fetch(`http://127.0.0.1:${PORT}/api/state`); if (r.ok) break; } catch {}
    await sleep(500);
  }
  await page.goto(`http://127.0.0.1:${PORT}/`);
  await page.waitForSelector("#state-label");
  capturing = true;
  const loop = captureLoop();
  const captureStart = now();

  // ---------- helpers ----------
  let mouse = { x: -1, y: -1 };
  const rectOf = (sel) => page.evaluate((s) => {
    const n = document.querySelector(s);
    if (!n) return null;
    const r = n.getBoundingClientRect();
    return { x: r.x, y: r.y, w: r.width, h: r.height };
  }, sel);
  const center = async (sel) => { const r = await rectOf(sel); return { x: r.x + r.w / 2, y: r.y + r.h / 2 }; };
  const ease = (u) => (u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2);
  async function moveTo(x, y, ms = 1200) {
    if (mouse.x < 0) mouse = { x, y: y + 80 };
    const x0 = mouse.x, y0 = mouse.y, t0 = Date.now();
    for (;;) {
      const u = Math.min(1, (Date.now() - t0) / ms);
      const e = ease(u);
      mouse = { x: x0 + (x - x0) * e, y: y0 + (y - y0) * e };
      await page.mouse.move(mouse.x, mouse.y);
      cursor.push({ t: now(), x: mouse.x, y: mouse.y });
      if (u >= 1) break;
      await sleep(12);
    }
  }
  async function click() {
    clicks.push({ t: now(), x: mouse.x, y: mouse.y });
    await page.mouse.down(); await sleep(70); await page.mouse.up();
  }
  async function waitFor(cond, ms = 240000, label = "condition") {
    const t0 = Date.now();
    while (Date.now() - t0 < ms) { if (cond()) return; await sleep(40); }
    throw new Error(`timeout waiting for ${label}`);
  }
  const texts = async () => page.evaluate(() => ({
    label: document.getElementById("state-label").textContent,
    advice: document.getElementById("state-advice").textContent,
    reserve: document.getElementById("reserve-value").textContent,
    eyes: document.getElementById("tile-eyes").textContent,
    drain: document.getElementById("tile-drain").textContent,
    awake: document.getElementById("sub-work").textContent,
    rt: document.getElementById("tile-rt").textContent,
    team: [...document.querySelectorAll(".team-row")].map((r) => r.textContent.trim()),
    badge: document.getElementById("source-badge").textContent,
  }));
  const beat = async (name, extra = {}) => {
    const e = { name, t: now(), latest: latest && { state: latest.state, reserve: latest.reserve, lapse: latest.lapse,
      lapse_kind: latest.lapse_kind, eye_state: latest.eye_state, context_factor: latest.context_factor,
      drain_per_hour: latest.drain_per_hour, awake_h: latest.awake_h, last_rt_ms: latest.last_rt_ms }, texts: await texts(), ...extra };
    events.push(e);
    console.log(`[${(e.t - captureStart).toFixed(1)}s] ${name}`, JSON.stringify(e.latest), e.texts.label);
    return e;
  };

  // ---------- beat A: calibration done, hover over both charts ----------
  await waitFor(() => latest && latest.state !== "calibrating", 240000, "end of calibration");
  await sleep(1500);
  const rects = {};
  for (const sel of ["body", ".worker", "#state", ".hero", ".tiles", ".charts", "#chart-fast", "#chart-fast .plot", "#chart-reserve",
    "#chart-reserve .plot", ".team", "#team-list", "#btn-probe", "#btn-break", "#btn-reset", "[data-scenario=nurse]",
    "[data-scenario=driver]", "#tile-eyes", "#tile-rt", ".foot"]) rects[sel] = await rectOf(sel);
  await beat("A_start");
  const fast = rects["#chart-fast .plot"], res = rects["#chart-reserve .plot"];
  await sleep(3500);   // the camera first frames the status card, no cursor yet
  await moveTo(fast.x + fast.w * 0.25, fast.y + fast.h * 0.55, 1300);
  await moveTo(fast.x + fast.w * 0.9, fast.y + fast.h * 0.55, 2600);
  await moveTo(res.x + res.w * 0.2, res.y + res.h * 0.45, 1300);
  await moveTo(res.x + res.w * 0.85, res.y + res.h * 0.4, 2200);
  await sleep(500);
  await beat("A_end");

  // ---------- beat B: manual reaction probe, answered in ~250 ms ----------
  const b = await center("#btn-probe");
  const probeCountBefore = probes.length;
  await beat("B_start");
  await moveTo(b.x, b.y, 1300);
  await sleep(250);
  await click();
  await beat("B_click");
  await waitFor(() => probes.length > probeCountBefore, 15000, "manual probe");
  await page.waitForFunction(() => !document.getElementById("probe").hidden, null, { timeout: 5000 });
  await sleep(270);
  await page.keyboard.press("Space");
  clicks.push({ t: now(), x: -1, y: -1, key: "Space" });
  await sleep(350);
  const probeResult = await page.evaluate(() => ({
    title: document.getElementById("probe-title").textContent, text: document.getElementById("probe-text").textContent }));
  rects["#probe-target"] = await rectOf("#probe-target");
  await beat("B_result", { probeResult });
  await sleep(2600);
  await beat("B_end");
  await moveTo(rects["#state"].x + rects["#state"].w * 0.9, rects["#state"].y + rects["#state"].h * 1.4, 1200);

  // ---------- beat C: eyes closed -> red alarm, then supervisor panel ----------
  await waitFor(() => latest && latest.lapse, 240000, "lapse");
  const lapse = await beat("C_lapse");
  await sleep(400);
  const chartEnd = { x: fast.x + fast.w - 70, y: fast.y + fast.h * 0.4 };
  await moveTo(chartEnd.x, chartEnd.y, 1500);
  await sleep(900);
  const team = rects["#team-list"];
  await moveTo(team.x + team.w * 0.25, team.y + team.h * 0.35, 1700);
  await sleep(3500);
  await beat("C_end");

  // ---------- beat D: automatic probe after the event, nobody answers ----------
  await moveTo(team.x + team.w * 0.55, team.y + team.h * 0.8, 1200);
  const probesBeforeD = probes.length;
  await waitFor(() => probes.length > probesBeforeD && probes[probes.length - 1].reason === "event", 240000, "event probe");
  await beat("D_probe");
  const before = latest ? latest.probe_lapses : 0;
  await waitFor(() => latest && latest.probe_lapses > before, 12000, "failed probe");
  rects["#probe-target-fail"] = await rectOf("#probe-target");
  await beat("D_fail", { probeResult: await page.evaluate(() => ({
    title: document.getElementById("probe-title").textContent, text: document.getElementById("probe-text").textContent })) });
  await sleep(600);
  const rt = await center("#tile-rt");
  await moveTo(rt.x, rt.y, 1300);
  await sleep(3200);
  await beat("D_end");

  // ---------- beat E: nurse scenario, start a break, reserve recovers ----------
  const nurse = await center("[data-scenario=nurse]");
  await moveTo(nurse.x, nurse.y, 1300);
  await sleep(200);
  await click();
  await sleep(1800);
  await beat("E_nurse");
  const brk = await center("#btn-break");
  await moveTo(brk.x, brk.y, 1300);
  await sleep(250);
  await click();
  await sleep(1000);
  await beat("E_break");
  await moveTo(brk.x + 260, brk.y - 300, 1500);
  await sleep(50000);
  await beat("E_end");

  capturing = false;
  await loop;
  await sleep(500);
  const first = frames[0] ? await sizeOf(path.join(OUT, "frames", frames[0][1])) : null;
  fs.writeFileSync(path.join(OUT, "frames.json"), JSON.stringify(frames));
  fs.writeFileSync(path.join(OUT, "events.json"), JSON.stringify({
    view: VIEW, dpr: DPR, frame_size: first, captureStart, recording: RECORDING, start_s: START_S,
    events, updates, probes, cursor, clicks, rects,
  }));
}

function sizeOf(file) {
  const b = fs.readFileSync(file);   // JPEG: find SOF0/SOF2 marker
  let i = 2;
  while (i < b.length) {
    if (b[i] !== 0xff) { i++; continue; }
    const m = b[i + 1];
    if (m >= 0xc0 && m <= 0xcf && m !== 0xc4 && m !== 0xc8 && m !== 0xcc) return { h: b.readUInt16BE(i + 5), w: b.readUInt16BE(i + 7) };
    i += 2 + b.readUInt16BE(i + 2);
  }
  return null;
}

main().catch((e) => { console.error(e); process.exit(1); });
