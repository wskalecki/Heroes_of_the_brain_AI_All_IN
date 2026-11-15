#!/usr/bin/env python3
"""Generate 10-slide 16:9 HTML and PDF pitch deck from docs/pitch.md."""

import base64
from pathlib import Path
import subprocess

REPO = Path("/home/antigravity/wskalecki/Heroes_of_the_brain_AI_All_IN")
ART = Path(
    "str(Path(__file__).resolve().parent)"
)


def b64_img(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def main() -> None:
    img_driver = b64_img(ART / "driver_night_broll_1794703303398.jpg")
    img_nurse = b64_img(ART / "nurse_shift_broll_1794703305071.jpg")
    img_dash_probe = b64_img(REPO / "docs/img/dashboard-proba-reakcji.png")
    img_dash_stop = b64_img(REPO / "docs/img/dashboard-przerwa-teraz.png")
    img_trafnosc = b64_img(REPO / "docs/img/trafnosc-na-nagraniach.png")
    img_drowsiness = b64_img(REPO / "docs/img/drowsiness-public-auc-and-calibration.png")
    img_heart = b64_img(
        REPO / "docs/img/rmssd-vs-vigilance-lapses-response-speed-cogbci.png"
    )
    img_t1 = b64_img(REPO / "docs/img/t1-kontrola-negatywna.png")

    html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<title>Wachta — Prezentacja 10 slajdów (Heroes of the Brain 2026)</title>
<style>
  @page {{
    size: 16in 9in;
    margin: 0;
  }}
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "DejaVu Sans", sans-serif;
    background: #0f172a;
    color: #0f172a;
  }}
  .slide {{
    width: 16in;
    height: 9in;
    page-break-after: always;
    break-after: page;
    position: relative;
    overflow: hidden;
    background: #f8fafc;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 0.55in 0.7in 0.45in 0.7in;
  }}
  .slide.dark {{
    background: linear-gradient(135deg, #0b1120 0%, #16213e 100%);
    color: #f8fafc;
  }}
  .topbar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13pt;
    font-weight: 600;
    color: #64748b;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 10px;
    margin-bottom: 18px;
  }}
  .slide.dark .topbar {{
    color: #94a3b8;
    border-bottom-color: rgba(255,255,255,0.14);
  }}
  .pill {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 11.5pt;
    font-weight: 700;
    background: #dbeafe;
    color: #1d4ed8;
  }}
  .slide.dark .pill {{
    background: rgba(56, 189, 248, 0.18);
    color: #38bdf8;
  }}
  h1.headline {{
    font-size: 27pt;
    line-height: 1.2;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 18px;
    letter-spacing: -0.02em;
  }}
  .slide.dark h1.headline {{
    color: #ffffff;
  }}
  .content {{
    flex: 1;
    display: flex;
    gap: 28px;
    align-items: stretch;
  }}
  .col {{
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }}
  .card {{
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 18px 22px;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
  }}
  .slide.dark .card {{
    background: rgba(30, 41, 59, 0.82);
    border-color: rgba(255, 255, 255, 0.14);
    color: #f1f5f9;
  }}
  .card h3 {{
    font-size: 15.5pt;
    font-weight: 700;
    margin-bottom: 8px;
    color: #0f172a;
  }}
  .slide.dark .card h3 {{
    color: #38bdf8;
  }}
  .card p, .card li {{
    font-size: 13.5pt;
    line-height: 1.42;
    color: #334155;
  }}
  .slide.dark .card p, .slide.dark .card li {{
    color: #e2e8f0;
  }}
  ul.clean {{
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }}
  ul.clean li {{
    position: relative;
    padding-left: 20px;
  }}
  ul.clean li::before {{
    content: "•";
    position: absolute;
    left: 0;
    color: #2563eb;
    font-weight: 900;
  }}
  .slide.dark ul.clean li::before {{
    color: #38bdf8;
  }}
  .stat-num {{
    font-size: 32pt;
    font-weight: 800;
    color: #1d4ed8;
    line-height: 1.05;
    margin-bottom: 4px;
  }}
  .stat-num.warn {{
    color: #d97706;
  }}
  .stat-num.danger {{
    color: #dc2626;
  }}
  .stat-num.ok {{
    color: #15803d;
  }}
  .source {{
    font-size: 10.5pt;
    color: #64748b;
    margin-top: 6px;
    font-style: italic;
  }}
  .slide.dark .source {{
    color: #94a3b8;
  }}
  .footer {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 10.5pt;
    color: #64748b;
    border-top: 1px solid #e2e8f0;
    padding-top: 10px;
    margin-top: 14px;
  }}
  .slide.dark .footer {{
    color: #94a3b8;
    border-top-color: rgba(255,255,255,0.14);
  }}
  table.data-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 12.2pt;
  }}
  table.data-table th {{
    background: #eff6ff;
    color: #1e3a8a;
    text-align: left;
    padding: 9px 12px;
    border-bottom: 2px solid #bfdbfe;
    font-weight: 700;
  }}
  table.data-table td {{
    padding: 8px 12px;
    border-bottom: 1px solid #e2e8f0;
    color: #1e293b;
    vertical-align: top;
    line-height: 1.34;
  }}
  .img-box {{
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    padding: 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }}
  .img-box img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    border-radius: 6px;
  }}
  .flow-grid {{
    display: grid;
    grid-template-columns: 1fr 40px 1fr 40px 1fr;
    align-items: stretch;
    gap: 8px;
    width: 100%;
  }}
  .flow-arrow {{
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26pt;
    font-weight: 800;
    color: #2563eb;
  }}
  .badge-green {{
    background: #dcfce7;
    color: #166534;
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 11pt;
  }}
  .badge-amber {{
    background: #fef3c7;
    color: #92400e;
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 11pt;
  }}
  .badge-red {{
    background: #fee2e2;
    color: #991b1b;
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 11pt;
  }}
</style>
</head>
<body>

<!-- SLAJD 1: TYTUŁ -->
<section class="slide dark">
  <div class="topbar">
    <span>Heroes of the Brain 2026 · Kategoria: <strong>Adaptive Systems</strong></span>
    <span class="pill">Zespół AI All In · BrainAccess MINI (8 kanałów EEG, 250 Hz)</span>
  </div>
  <div class="content" style="align-items: center;">
    <div class="col" style="flex: 1.18; gap: 20px;">
      <div style="font-size: 15pt; font-weight: 700; color: #38bdf8; letter-spacing: 0.04em; text-transform: uppercase;">
        Personalizacja norm zmęczenia i rezerw czujności
      </div>
      <h1 class="headline" style="font-size: 36pt; line-height: 1.15; margin-bottom: 6px;">
        Wachta: normy zmęczenia liczone dla człowieka, nie dla zegara.
      </h1>
      <p style="font-size: 16.5pt; line-height: 1.48; color: #cbd5e1;">
        Krótkie sesje EEG z testem reakcji uczą <strong>osobistego profilu pracownika</strong>, a w rolach podwyższonego ryzyka pętla na żywo wykrywa spadki czujności i od razu zmienia plan przerw oraz obsady.
      </p>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 8px;">
        <div class="card">
          <h3>Kalibracja osobista</h3>
          <p>60 s EEG + test reakcji PVT-B wyznaczają osobisty próg zamiast jednej normy dla wszystkich.</p>
        </div>
        <div class="card">
          <h3>Pętla adaptacyjna</h3>
          <p>EEG (O1/O2, F3/F4) + kontekst doby + próby reakcji → decyzja o przerwie i wskazanie zmiennika.</p>
        </div>
        <div class="card">
          <h3>Prywatność (AI Act)</h3>
          <p>Surowy sygnał EEG zostaje na stanowisku pracownika — przełożony widzi wyłącznie gotowość.</p>
        </div>
      </div>
    </div>
    <div class="col" style="flex: 0.88; gap: 14px;">
      <div class="img-box" style="background: rgba(15,23,42,0.7); border-color: rgba(255,255,255,0.16); padding: 8px;">
        <img src="{img_driver}" style="height: 250px; width: 100%; object-fit: cover;">
      </div>
      <div class="img-box" style="background: #ffffff; padding: 8px;">
        <img src="{img_dash_stop}" style="height: 235px; width: 100%; object-fit: contain;">
      </div>
    </div>
  </div>
  <div class="footer">
    <span>Zespół <strong>AI All In</strong>: Wojtek · Adrian · Filip · Rudy</span>
    <span>Slajd 1 / 10</span>
  </div>
</section>

<!-- SLAJD 2: PROBLEM -->
<section class="slide">
  <div class="topbar">
    <span>Wachta · Problem</span>
    <span class="pill">Slajd 2 / 10</span>
  </div>
  <h1 class="headline">Przepisy dają wszystkim ten sam limit, a zmęczenie każdego dopada inaczej.</h1>
  <div class="content">
    <div class="col" style="flex: 1.05;">
      <div class="card">
        <div class="stat-num">4,5 h jazdy → 45 min przerwy</div>
        <h3>Sztywny zegar w przepisach (maks. 9 h dziennie)</h3>
        <p>Identyczny limit czasu pracy dla każdego kierowcy i operatora — niezależnie od długu snu, pory doby (02:30 w nocy vs południe) i indywidualnej odporności.</p>
        <div class="source">Źródło: Komisja Europejska, rozporządzenie (WE) nr 561/2006 (czas jazdy i odpoczynku).</div>
      </div>
      <div class="card">
        <div class="stat-num danger">10–20% wypadków drogowych</div>
        <h3>Skutek zmęczenia za kierownicą (zakres 6–24% w badaniach)</h3>
        <p>Szacunki różnią się w zależności od definicji i kraju, ale senność pozostaje jedną z głównych przyczyn najcięższych wypadków na drogach szybkiego ruchu.</p>
        <div class="source">Źródło: Europejskie Obserwatorium Bezpieczeństwa Ruchu Drogowego (ERSO, raport Fatigue).</div>
      </div>
      <div class="card">
        <div class="stat-num warn">17–19 h bez snu ≈ 0,05% alkoholu</div>
        <h3>Spadek sprawności psychomotorycznej</h3>
        <p>Po 17–19 godzinach od przebudzenia czas reakcji i liczba pominięć bodźców spadają do poziomu odpowiadającego 0,5 promila alkoholu we krwi.</p>
        <div class="source">Źródło: Dawson i Reid (1997), Nature 388:235.</div>
      </div>
    </div>
    <div class="col" style="flex: 0.95;">
      <div class="img-box" style="padding: 0; overflow: hidden; height: 320px;">
        <img src="{img_nurse}" style="width: 100%; height: 100%; object-fit: cover;">
      </div>
      <div class="card" style="background: #eff6ff; border-color: #bfdbfe; flex: 1;">
        <h3 style="color: #1e3a8a;">Co dzieje się na zmianie nocnej?</h3>
        <ul class="clean">
          <li><strong>Ten sam zegar, różny stan mózgu:</strong> po 6 godzinach zmiany jedna osoba ma pełną rezerwę czujności, a druga wchodzi w epizody zamknięcia oczu.</li>
          <li><strong>Przerwa z kalendarza bywa za późno albo za wcześnie:</strong> sztywny grafik nie wie, kto dziś spał 4 godziny, a kto 8 godzin.</li>
          <li><strong>Brak informacji dla przełożonego:</strong> dyspozytor lub oddziałowa nie widzą, kto w zespole ma rezerwę, by bezpiecznie przejąć zadanie.</li>
        </ul>
      </div>
    </div>
  </div>
  <div class="footer">
    <span>Wszystkie liczby posiadają udokumentowane źródła w docs/podstawy-naukowe.md</span>
    <span>Slajd 2 / 10</span>
  </div>
</section>

<!-- SLAJD 3: LUKA -->
<section class="slide">
  <div class="topbar">
    <span>Wachta · Luka technologiczna i regulacyjna (Kamera i zegarek a Wachta)</span>
    <span class="pill">Slajd 3 / 10</span>
  </div>
  <h1 class="headline">Ludzie różnią się podatnością na zmęczenie w stały sposób, a ani normy, ani kamery tego nie mierzą.</h1>
  <div class="content">
    <div class="col" style="flex: 1.15; gap: 10px;">
      <div class="card" style="padding: 13px 18px;">
        <h3>1. Podatność na brak snu to stała cecha osobnicza (Van Dongen i in. 2004)</h3>
        <p>Spadki sprawności po deprywacji snu różnią się między ludźmi wielokrotnie i są <strong>systematyczne oraz powtarzalne u tej samej osoby</strong>. Jedna norma czasu pracy z definicji nie pasuje do wszystkich.</p>
        <div class="source">Źródło: Van Dongen i in. (2004), Sleep 27(3):423–433 (docs/podstawy-naukowe.md, poz. 28).</div>
      </div>
      <div class="card" style="padding: 13px 18px;">
        <h3>2. Kamera w kabinie widzi powiekę — Wachta sprawdza korę mózgową i reakcję</h3>
        <p>Kamera DMS alarmuje dopiero, gdy powieki są już zamknięte. Nie widzi wzrostu mocy alfy (8–12 Hz) na O1/O2, nie odróżnia odpoczynku od pracy i nie weryfikuje czasu reakcji po incydencie.</p>
      </div>
      <div class="card" style="padding: 13px 18px;">
        <h3>3. Zegarek (HRV) nie zastąpi EEG — to osobny sygnał uzupełniający</h3>
        <p>Sprawdziliśmy na zbiorze <strong>COG-BCI (29 osób, zadanie PVT)</strong>: RMSSD z EKG zmienia się z czasem trwania zadania podobnie jak czujność (<em>r</em> = 0,18), ale po odjęciu czasu zadania korelacja z szybkością reakcji spada do <strong><em>r</em> = 0,05</strong> (<em>p</em> = 0,11).</p>
        <div class="source">Źródło: nasza analiza w data/analysis/10-heart-vs-eeg-lapses-and-response-speed.ipynb.</div>
      </div>
      <div class="card" style="padding: 13px 18px;">
        <h3>4. Prawo lotnicze już dopuszcza normy oparte na danych (FRMS)</h3>
        <p>Systemy zarządzania ryzykiem zmęczenia (FRMS) są legalną alternatywą dla sztywnych limitów, ale w praktyce wciąż opierają się głównie na limitach czasu i subiektywnej samoocenie KSS.</p>
        <div class="source">Źródło: IATA FRMS White Paper (2025) oraz dokumenty robocze ICAO (Zgromadzenie A42).</div>
      </div>
    </div>
    <div class="col" style="flex: 0.85; gap: 10px;">
      <div class="img-box" style="flex: 1; padding: 8px;">
        <img src="{img_heart}" style="max-height: 310px;">
        <div class="source" style="text-align: center; margin-top: 6px;">
          Notebook 10 (COG-BCI, 29 osób): HRV (RMSSD) odzwierciedla czas na zadaniu, ale po jego uwzględnieniu nie mierzy spadków czujności (<em>r</em> = 0,05).
        </div>
      </div>
      <div class="card" style="background: #fefce8; border-color: #fde047; padding: 14px 18px;">
        <h3 style="color: #854d0e;">Wniosek projektowy Wachty</h3>
        <p style="color: #713f12;">Zamiast obiecywać, że „zegarek zastąpi EEG”, używamy krótkich sesji EEG + testu reakcji do wyznaczenia osobistego profilu, a na co dzień łączymy go z modelem kontekstu doby.</p>
      </div>
    </div>
  </div>
  <div class="footer">
    <span>Kamera = geometria powieki po fakcie · Zegarek = tło autonomiczne · Wachta = EEG + reakcja + kontekst</span>
    <span>Slajd 3 / 10</span>
  </div>
</section>

<!-- SLAJD 4: ROZWIĄZANIE -->
<section class="slide">
  <div class="topbar">
    <span>Wachta · Rozwiązanie</span>
    <span class="pill">Slajd 4 / 10</span>
  </div>
  <h1 class="headline">Osobisty profil zmęczenia z krótkich sesji EEG i testu reakcji, a z niego osobisty plan przerw.</h1>
  <div class="content" style="flex-direction: column; gap: 20px;">
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 22px; flex: 1;">
      <div class="card" style="border-top: 6px solid #2563eb; display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div class="pill" style="margin-bottom: 12px;">Element 1 · Kalibracja profilu</div>
          <h3 style="font-size: 18pt; margin-bottom: 12px;">Krótka sesja kalibracyjna EEG + PVT-B</h3>
          <ul class="clean">
            <li>Wykonywana na początku zmiany, po zmianach nocnych lub okresowo (kilka minut).</li>
            <li><strong>60 s oczy otwarte + 40 s zamknięte:</strong> wyznacza osobistą bazę alfy i sprawdza reaktywność markera (<em>R<sub>z</sub></em> ≥ 2,5, notebook 07).</li>
            <li><strong>3-minutowy test reakcji PVT-B</strong> w przeglądarce (<code>wachta.pvt</code>): wyznacza osobistą medianę czasu reakcji i podatność po braku snu.</li>
          </ul>
        </div>
        <div class="source">Nie wymaga noszenia czepka przez 8 godzin u każdego pracownika.</div>
      </div>

      <div class="card" style="border-top: 6px solid #0284c7; display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div class="pill" style="margin-bottom: 12px;">Element 2 · Praca na co dzień</div>
          <h3 style="font-size: 18pt; margin-bottom: 12px;">Osobisty model kontekstu (bez czepka)</h3>
          <ul class="clean">
            <li>Łączy wyuczony profil pracownika z <strong>uproszczonym modelem dwuprocesowym</strong> (proces homeostatyczny S + rytm dobowy C).</li>
            <li>Uwzględnia: <strong>czas od przebudzenia</strong> (<code>--wake</code>), <strong>porę doby</strong> (<code>--clock</code>, dołek 02:00–06:00 przyspiesza spadek rezerwy 1,6×) i czas pracy.</li>
            <li>Krótkie próby reakcji z harmonogramu korygują prognozę czasu do przerwy (<code>minutes_to_warn</code>, <code>minutes_to_stop</code>).</li>
          </ul>
        </div>
        <div class="source">Lekkie wdrożenie tam, gdzie kask nie jest używany na co dzień.</div>
      </div>

      <div class="card" style="border-top: 6px solid #16a34a; display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div class="pill" style="margin-bottom: 12px;">Element 3 · Role wysokiego ryzyka</div>
          <h3 style="font-size: 18pt; margin-bottom: 12px;">Tryb na żywo z opaską / wkładką w kasku</h3>
          <ul class="clean">
            <li>Dla stanowisk, gdzie kask lub opaska są już naturalne (górnictwo, operatorzy ciężkich maszyn, dyżury nocne).</li>
            <li>8 suchych elektrod <strong>BrainAccess MINI</strong> (250 Hz): wykrywa zamknięcie oczu i wzrost alfy (O1/O2) w ciągu kilku sekund.</li>
            <li>System od razu przełącza rekomendację na <strong>„Przerwa teraz”</strong> i wskazuje zmiennika w panelu przełożonego.</li>
          </ul>
        </div>
        <div class="source">Przetwarzanie w 100% lokalne na komputerze stanowiskowym.</div>
      </div>
    </div>

    <div class="card" style="background: #0f172a; color: #f8fafc; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center;">
      <div style="font-size: 14pt;">
        <strong style="color: #38bdf8;">Co zmieniliśmy po analizie danych (strumień B):</strong> zamiast zakładać, że sama alfa przy otwartych oczach wyprzedza każdy błąd o minutę (notebook 06: AUC = 0,52), połączyliśmy detekcję zdarzeń ostrych EEG z aktywnymi próbami czasu reakcji i kalibracją osobistą (notebook 04: wzrost AUC z 0,76 do 0,90).
      </div>
    </div>
  </div>
  <div class="footer">
    <span>Architektura 3-warstwowa: Kalibracja osobista → Model kontekstu na co dzień → Pętla EEG na żywo w kasku</span>
    <span>Slajd 4 / 10</span>
  </div>
</section>

<!-- SLAJD 5: JAK TO DZIAŁA: PĘTLA ADAPTACYJNA -->
<section class="slide">
  <div class="topbar">
    <span>Wachta · Jak to działa: pętla adaptacyjna (kryterium: Zgodność z tematem — 20 pkt)</span>
    <span class="pill">Slajd 5 / 10</span>
  </div>
  <h1 class="headline">System nie tylko mierzy: sam zmienia rekomendację, prosi o reakcję i wskazuje zmiennika.</h1>
  <div class="content" style="flex-direction: column; justify-content: space-between;">
    <div class="flow-grid" style="flex: 1;">
      <div class="card" style="border-left: 6px solid #2563eb;">
        <div class="pill" style="margin-bottom: 8px;">1. WEJŚCIE: 4 STRUMIENIE</div>
        <h3>Sygnał biologiczny i kontekst</h3>
        <ul class="clean" style="margin-top: 8px;">
          <li><strong>EEG potyliczne (O1, O2):</strong> wyrazistość pasma alfa (8–12 Hz) względem sąsiednich pasm w oknie 4 s co 1 s.</li>
          <li><strong>EEG czołowe (F3, F4):</strong> detekcja mrugnięć i stanu oczu (<code>otwarte</code> / <code>zamknięte</code>).</li>
          <li><strong>Kontekst zmiany:</strong> czas od przebudzenia + pora doby (mnożnik spadku rezerwy do 2,56× w nocy).</li>
          <li><strong>Czas reakcji:</strong> odpowiedź spacją/klikiem na krótki ton 660 Hz (okno 3 s).</li>
          <li><strong>Kontrola jakości:</strong> odrzucanie okien z artefaktami ruchu/EMG (> 150 µV ptp).</li>
        </ul>
      </div>

      <div class="flow-arrow">→</div>

      <div class="card" style="border-left: 6px solid #d97706;">
        <div class="pill" style="margin-bottom: 8px;">2. MODEL OSOBISTY</div>
        <h3>Stan i rezerwa czujności</h3>
        <ul class="clean" style="margin-top: 8px;">
          <li><strong>Kalibracja indywidualna (60 s):</strong> mediana i MAD na czystych oknach wyznaczają jednostkę <em>z</em> danej osoby.</li>
          <li><strong>Rozdzielenie przyczyny spadku:</strong>
            <br>• <em>Zamknięte oczy / mikrosen</em> (alfa <em>z</em> ≥ 2,5 przez ≥ 3 s + brak mrugnięć)
            <br>• <em>Spadek reaktywności przy otwartych oczach</em> (próba reakcji > 1,5× normy lub > 3 s).</li>
          <li><strong>Rezerwa czujności (0–100%):</strong> spada z pracą i incydentami, <strong>odnawia się w trakcie przerwy</strong> (+2,2 pkt%/min).</li>
        </ul>
      </div>

      <div class="flow-arrow">→</div>

      <div class="card" style="border-left: 6px solid #dc2626;">
        <div class="pill" style="margin-bottom: 8px;">3. ADAPTACJA ZACHOWANIA</div>
        <h3>Decyzja i zamknięcie pętli</h3>
        <ul class="clean" style="margin-top: 8px;">
          <li><span class="badge-green">Możesz pracować</span> — cicha praca, prognoza czasu do kolejnej przerwy.</li>
          <li><span class="badge-amber">Zaplanuj przerwę</span> — wyzwalana automatycznie <strong>próba reakcji</strong> weryfikująca czujność.</li>
          <li><span class="badge-red">Przerwa teraz</span> — dwutonowy alarm dźwiękowy (880/660 Hz) + nakaz zjechania / przekazania zmiany.</li>
          <li><strong>Weryfikacja po incydencie:</strong> po otwarciu oczu system sam wystawia próbę reakcji — powrót do zielonego stanu wymaga jej zaliczenia.</li>
          <li><strong>Panel przełożonego:</strong> automatycznie wskazuje zmiennika z najwyższą rezerwą.</li>
        </ul>
      </div>
    </div>

    <div class="card" style="background: #f1f5f9; padding: 14px 20px;">
      <p style="font-size: 13pt; color: #1e293b;">
        <strong>Dlaczego to pełny system adaptacyjny (Adaptive Systems):</strong> pętla działa w obu kierunkach — stan mózgu i reakcja pracownika zmieniają zachowanie interfejsu i plan obsady, a po odpoczynku lub zaliczonej próbie system automatycznie adaptuje rekomendację z powrotem.
      </p>
    </div>
  </div>
  <div class="footer">
    <span>Implementacja: src/wachta/filter.py · features.py · baseline.py · blinks.py · index.py · server.py</span>
    <span>Slajd 5 / 10</span>
  </div>
</section>

<!-- SLAJD 6: DEMO -->
<section class="slide">
  <div class="topbar">
    <span>Wachta · Scenariusz Demo (na żywo z BrainAccess MINI oraz w trybie odtwarzania)</span>
    <span class="pill">Slajd 6 / 10</span>
  </div>
  <h1 class="headline">Ten sam przebieg w filmie i na żywo: noc, kalibracja, próba reakcji, mikrosen, zmiennik i przerwa.</h1>
  <div class="content">
    <div class="col" style="flex: 0.95; justify-content: space-between;">
      <div class="card" style="padding: 14px 18px;">
        <h3>Przebieg demonstracji (docs/scenariusz-demo.md)</h3>
        <ul class="clean" style="gap: 8px; margin-top: 6px;">
          <li><strong>1. Kontekst nocy (02:30, 19 h czuwania):</strong> po 60 s kalibracji osobistej system pokazuje stan <span class="badge-green">Możesz pracować</span> i tempo spadku rezerwy 26%/h.</li>
          <li><strong>2. Szybka próba reakcji:</strong> odpowiedź spacją w <strong>248 ms</strong> (w osobistej normie) utrzymuje zielony status.</li>
          <li><strong>3. Zamknięcie oczu (mikrosen):</strong> wzrost alfy na O1/O2 powyżej progu 2,5 przez 3 s uruchamia <span class="badge-red">Przerwa teraz</span> i alarm dźwiękowy.</li>
          <li><strong>4. Weryfikacja przy otwartych oczach:</strong> po otwarciu oczu system sam prosi o reakcję — <strong>brak odpowiedzi (> 3 s)</strong> potwierdza spadek czujności.</li>
          <li><strong>5. Zmiennik i regeneracja:</strong> panel przełożonego wskazuje zmiennika (<em>Rudy — 84%</em>), a kliknięcie <code>Rozpocznij przerwę</code> odnawia rezerwę.</li>
        </ul>
      </div>
      <div class="card" style="background: #eff6ff; border-color: #bfdbfe; padding: 14px 18px;">
        <h3 style="color: #1e3a8a;">Uruchomienie jednym poleceniem</h3>
        <p style="font-family: monospace; font-size: 11.5pt; background: #ffffff; padding: 8px 10px; border-radius: 6px; border: 1px solid #cbd5e1; margin-top: 4px;">
          wachta --source board --wake 19 --clock 02:30<br>
          wachta --source replay --file data/recordings/wojtek_1-raw.fif --speed 4
        </p>
      </div>
    </div>
    <div class="col" style="flex: 1.05; gap: 12px;">
      <div class="img-box" style="flex: 1; padding: 8px;">
        <img src="{img_dash_probe}" style="max-height: 235px;">
        <div class="source">Krok 2 i 4: Aktywna próba reakcji na dashboardzie (pomarańczowy krąg + ton 660 Hz).</div>
      </div>
      <div class="img-box" style="flex: 1; padding: 8px;">
        <img src="{img_dash_stop}" style="max-height: 235px;">
        <div class="source">Krok 3 i 5: Stan „Przerwa teraz” po zamknięciu oczu i wskazanie zmiennika w Panelu przełożonego.</div>
      </div>
    </div>
  </div>
  <div class="footer">
    <span>Film demo 1:54 (wachta-demo-2min.mp4) pokazuje dokładnie ten sam kod działający w przeglądarce</span>
    <span>Slajd 6 / 10</span>
  </div>
</section>

<!-- SLAJD 7: DOWODY -->
<section class="slide">
  <div class="topbar">
    <span>Wachta · Dowody na naszym sprzęcie i w danych publicznych</span>
    <span class="pill">Slajd 7 / 10</span>
  </div>
  <h1 class="headline">Mechanizm działa na naszym sprzęcie, a personalizacja ma oparcie w danych.</h1>
  <div class="content">
    <div class="col" style="flex: 1.15;">
      <div class="card" style="padding: 14px 18px;">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width: 62%;">Wynik / Liczba</th>
              <th>Źródło w repozytorium</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>5 z 5 bloków zamkniętych oczu wykrytych</strong> (4 osoby, 5 nagrań BrainAccess MINI), tylko <strong>1 fałszywy alarm w 48 min</strong> poza blokiem (AUC 0,88–0,99)</td>
              <td><code>docs/trafnosc-na-nagraniach.md</code>,<br><code>img/trafnosc-na-nagraniach.png</code></td>
            </tr>
            <tr>
              <td><strong>15 min monotonii (T1, 1 osoba, KSS 5):</strong> <strong>0 fałszywych alarmów</strong> przez 13 min otwartych oczu, zamknięcie oczu wykryte po ok. 9 s (0,9% odrzuconych okien)</td>
              <td><code>docs/sesja-monotonii-wojtek.md</code>,<br>notebook 09</td>
            </tr>
            <tr>
              <td><strong>Senność przy otwartych oczach (dane publiczne):</strong> alfa na O1/O2 rośnie u <strong>11 z 11 osób</strong>, mediana <strong>AUC = 0,75</strong> (zakres 0,52–0,91) na naszych 8 kanałach</td>
              <td>notebook 04 (Cui i in. 2022, CC BY 4.0),<br><code>img/drowsiness-public-auc-and-calibration.png</code></td>
            </tr>
            <tr>
              <td><strong>Personalizacja podnosi trafność z 0,66–0,72 do 0,83 (AUC z 0,76 do 0,90)</strong> wobec jednego wspólnego modelu dla wszystkich</td>
              <td>notebook 04, tabela strategii kalibracji</td>
            </tr>
            <tr>
              <td><strong>Kontekst zmiany</strong> (czas jazdy, pora doby) podnosi AUC detekcji zmęczenia z <strong>0,76 do 0,88</strong></td>
              <td>Lu i in. (2022), <code>docs/podstawy-naukowe.md</code> poz. 3</td>
            </tr>
            <tr>
              <td><strong>HRV a czujność (29 osób, COG-BCI):</strong> RMSSD zmienia się z czasem zadania jak 1/RT (<em>r</em> = 0,18), ale po uwzględnieniu czasu nie mierzy czujności (<em>r</em> = 0,05)</td>
              <td>notebook 10 (Hinss i in. 2023, CC BY 4.0)</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="col" style="flex: 0.85; gap: 12px;">
      <div class="img-box" style="flex: 1; padding: 8px;">
        <img src="{img_trafnosc}" style="max-height: 240px;">
        <div class="source">Własne nagrania BrainAccess MINI (5 nagrań, 4 osoby): 5/5 bloków wykrytych.</div>
      </div>
      <div class="img-box" style="flex: 1; padding: 8px;">
        <img src="{img_drowsiness}" style="max-height: 240px;">
        <div class="source">Zbiór Cui i in. (2022, 11 osób): kalibracja osobista podnosi AUC z 0,76 do 0,90.</div>
      </div>
    </div>
  </div>
  <div class="footer">
    <span>Wszystkie wykresy są w 100% odtwarzalne ze skryptów w experiments/ oraz notebooków w data/analysis/</span>
    <span>Slajd 7 / 10</span>
  </div>
</section>

<!-- SLAJD 8: CO ZWERYFIKOWANE, A CO ZAŁOŻONE -->
<section class="slide">
  <div class="topbar">
    <span>Wachta · Uczciwość badawcza: co zweryfikowane, a co założone (zadanie D4)</span>
    <span class="pill">Slajd 8 / 10</span>
  </div>
  <h1 class="headline">Oddzielamy to, co udowodniliśmy na sprzęcie i danych, od założeń do pilotażu.</h1>
  <div class="content">
    <div class="col">
      <div class="card" style="border-top: 6px solid #16a34a; flex: 1;">
        <h3 style="color: #15803d; font-size: 17pt; margin-bottom: 12px;">✓ Zweryfikowane w tym projekcie</h3>
        <ul class="clean" style="gap: 13px;">
          <li><strong>Wykrywanie zamkniętych oczu i wzrostu alfy na suchych elektrodach BrainAccess MINI:</strong> 5 z 5 bloków na nagraniach zespołu, 1 fałszywy alarm w 48 min.</li>
          <li><strong>Zero fałszywych alarmów w 15-minutowej sesji monotonii (T1, KSS 5):</strong> stabilna praca w cichych warunkach, wykrycie zamknięcia oczu po ok. 9 s.</li>
          <li><strong>Senność przy otwartych oczach widać na naszych 8 kanałach w danych publicznych:</strong> wzrost alfy u 11 z 11 osób (AUC 0,75) w zbiorze Cui i in. 2022.</li>
          <li><strong>Personalizacja istotnie poprawia rozróżnianie stanów:</strong> kalibracja na osobę podnosi AUC z 0,76 do 0,90 (trafność z 0,66–0,72 do 0,83).</li>
          <li><strong>Działająca pętla adaptacyjna na żywo z czepkiem BrainAccess:</strong> kalibracja 60 s → detekcja → próba reakcji → zmiana stanu i wskazanie zmiennika.</li>
        </ul>
      </div>
    </div>
    <div class="col">
      <div class="card" style="border-top: 6px solid #d97706; flex: 1;">
        <h3 style="color: #b45309; font-size: 17pt; margin-bottom: 12px;">→ Założone / zweryfikowane negatywnie (do pilotażu)</h3>
        <ul class="clean" style="gap: 13px;">
          <li><strong>Hipoteza główna do pilotażu:</strong> że osobisty limit czasu pracy wyznaczony z EEG i PVT-B przewiduje spadki czujności na zmianie lepiej niż sztywna norma i sam model kontekstu.</li>
          <li><strong>Senność przy otwartych oczach na naszych własnych nagraniach:</strong> protokół nocny z testem PVT-B jest gotowy (<code>docs/protokol-nocny.md</code>, zadanie C4); w dziennej sesji T1 badany miał KSS 5 (brak senności).</li>
          <li><strong>Parametry równania rezerwy czujności:</strong> tempo spadku (12%/h), kary za incydenty i mnożnik nocny (1,6×) to jawne założenia inżynierskie w <code>config.py</code>.</li>
          <li><strong>Zegarek (HRV) jako zamiennik EEG:</strong> nasze dane pokazują, że <strong>nie zastąpi</strong> sesji EEG (<em>r</em> = 0,05 po odjęciu czasu zadania), może jedynie uzupełniać kontekst.</li>
          <li><strong>Czy alfa przy otwartych oczach ostrzega przed lapsem w kolejnej minucie?</strong> <strong style="color: #dc2626;">Sprawdziliśmy i nie ostrzega</strong> (AUC = 0,52 na 29 osobach w COG-BCI, notebook 06) — dlatego wyzwalaczem prób jest zdarzenie ostre i harmonogram, a nie podprogowa alfa.</li>
        </ul>
      </div>
    </div>
  </div>
  <div class="footer">
    <span>Zasada zespołu (docs/podstawy-naukowe.md §6): nie obiecujemy tego, czego dane nie potwierdzają</span>
    <span>Slajd 8 / 10</span>
  </div>
</section>

<!-- SLAJD 9: RYNEK, MODEL, PRAWO -->
<section class="slide">
  <div class="topbar">
    <span>Wachta · Rynek, model wdrożenia i zgodność z AI Act</span>
    <span class="pill">Slajd 9 / 10</span>
  </div>
  <h1 class="headline">Zaczynamy tam, gdzie kask już jest albo przepisy już wymagają zarządzania zmęczeniem.</h1>
  <div class="content">
    <div class="col">
      <div class="card">
        <h3>1. Kolejność wejścia na rynek (3 kroki)</h3>
        <ul class="clean">
          <li><strong>Krok 1 — Kopalnie, budowa, operatorzy ciężkich maszyn:</strong> kask ochronny jest już obowiązkowy, więc opaska/wkładka EEG w kasku jest akceptowalna od pierwszego dnia.</li>
          <li><strong>Krok 2 — Branże z prawnym obowiązkiem FRMS:</strong> lotnictwo, kontrola ruchu lotniczego, energetyka i dyspozytornie (gotowe ramy prawne na osobiste normy zmęczenia).</li>
          <li><strong>Krok 3 — Transport drogowy:</strong> jako trzeci etap (w kabinie ciężarówki dziś wygrywa tania, obowiązkowa kamera DMS; wchodzimy tam z okresową kalibracją + modelem kontekstu).</li>
        </ul>
      </div>
      <div class="card">
        <h3>2. Różnica względem SmartCap (Wenco / KGHM)</h3>
        <p><strong>SmartCap jedynie alarmuje</strong> przy ciągłym noszeniu czepka. <strong>Wachta zamyka pętlę zarządzania zmianą:</strong> wyznacza osobisty limit z krótkich sesji EEG + PVT-B, łączy go z kontekstem doby i wskazuje gotowego zmiennika w zespole.</p>
        <div class="source">Źródło: analiza konkurencji w docs/rynek-eeg-wearables.md.</div>
      </div>
    </div>
    <div class="col">
      <div class="card">
        <div class="stat-num">345 mln USD (2025) → 877 mln USD (2032)</div>
        <h3>3. Rynek oprogramowania do zarządzania ryzykiem zmęczenia</h3>
        <p>Szacunek globalnego rynku systemów FRMS (CAGR ~14%). Model biznesowy Wachty (założenie do walidacji): miesięczna subskrypcja B2B za stanowisko + okresowe sesje kalibracyjne; sprzęt EEG od partnera (<strong>BrainAccess</strong>).</p>
        <div class="source">Źródło: raport LP Information, omówiony w docs/rynek-wielkosc-i-kierunek.md §2c.</div>
      </div>
      <div class="card" style="background: #f0fdf4; border-color: #bbf7d0; flex: 1;">
        <h3 style="color: #166534;">4. Prawo i etyka: zgodność z unijnym AI Act (motyw 18)</h3>
        <ul class="clean">
          <li><strong>Zmęczenie i senność to stany fizyczne/fizjologiczne, a nie emocje:</strong> motyw 18 AI Act wprost wyłącza wykrywanie zmęczenia (np. u pilotów i kierowców w celu zapobiegania wypadkom) spod zakazu rozpoznawania emocji w miejscu pracy (art. 5 ust. 1 lit. f).</li>
          <li><strong>Ochrona danych biometrycznych (RODO):</strong> surowe przebiegi EEG są przetwarzane lokalnie i zostają u pracownika. Przełożony widzi wyłącznie 3-stopniową gotowość do pracy.</li>
        </ul>
      </div>
    </div>
  </div>
  <div class="footer">
    <span>Pozycjonowanie prawne: bezpieczeństwo pracy (BHP / FRMS), zero śledzenia emocji czy stresu</span>
    <span>Slajd 9 / 10</span>
  </div>
</section>

<!-- SLAJD 10: CO DALEJ I ZESPÓŁ -->
<section class="slide dark">
  <div class="topbar">
    <span>Wachta · Co dalej: plan pilotażu i zespół</span>
    <span class="pill">Slajd 10 / 10</span>
  </div>
  <h1 class="headline">Pilotaż na jednej zmianie: czy osobisty limit przewiduje spadki czujności lepiej niż norma.</h1>
  <div class="content">
    <div class="col" style="flex: 1.1;">
      <div class="card">
        <h3>Plan walidacji w pilotażu (3 porównywane warianty)</h3>
        <ul class="clean" style="margin-top: 8px;">
          <li><strong>Wariant A (punkt odniesienia):</strong> sztywna norma czasu pracy (zegar).</li>
          <li><strong>Wariant B:</strong> sam model kontekstu (czas od przebudzenia + pora doby, bez kalibracji osobistej).</li>
          <li><strong>Wariant C (Wachta):</strong> osobisty profil wyznaczony z krótkich sesji EEG + PVT-B połączony z kontekstem zmiany.</li>
        </ul>
        <p style="margin-top: 12px;"><strong>Miary sukcesu:</strong> liczba lapsów (RT > 500 ms) w 3-minutowym teście PVT-B na koniec zmiany, zdarzenia ostre na zmianie oraz subiektywna skala senności KSS.</p>
      </div>
      <div class="card">
        <h3>Co już trwa po zamrożeniu kodu</h3>
        <p>Protokół nocnych punktów pomiarowych z testem reakcji PVT-B zaraz po nagraniu EEG jest gotowy i wdrożony w kodzie (<code>python -m wachta.session</code>, <code>python -m wachta.pvt</code>, <code>experiments/analyze-night-checkpoint.py</code>).</p>
      </div>
      <div class="card" style="background: rgba(56, 189, 248, 0.12); border-color: rgba(56, 189, 248, 0.35);">
        <h3>Publiczne repozytorium i pełna powtarzalność wyników</h3>
        <p style="font-family: monospace; font-size: 13.5pt; color: #38bdf8; margin-top: 4px;">
          https://github.com/wskalecki/Heroes_of_the_brain_AI_All_IN
        </p>
        <p style="font-size: 12pt; margin-top: 6px; color: #cbd5e1;">
          76 testów jednostkowych i regresyjnych w CI · 10 notebooków analitycznych · działający pakiet <code>wachta</code>.
        </p>
      </div>
    </div>
    <div class="col" style="flex: 0.9;">
      <div class="card" style="flex: 1; display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <h3>Zespół AI All In — podział strumieni</h3>
          <ul class="clean" style="margin-top: 12px; gap: 14px;">
            <li><strong>Wojtek — Sygnał i aplikacja (Strumień A):</strong> potok DSP w czasie rzeczywistym, detekcja alfy i mrugnięć, serwer WebSocket, dashboard, integracja z BrainAccess MINI.</li>
            <li><strong>Adrian — Dane i dowody (Strumień B):</strong> walidacja statystyczna na 5 nagraniach własnych i zbiorach publicznych (Cui 2022, COG-BCI), 10 notebooków weryfikujących hipotezy.</li>
            <li><strong>Filip — Pomiary i protokoły (Strumień C):</strong> nagrania EEG na suchych elektrodach, sesje kontrolne i protokół pomiarów nocnych z PVT-B.</li>
            <li><strong>Rudy — Pitch, rynek i demo (Strumień D):</strong> pozycjonowanie regulacyjne (AI Act, FRMS), analiza rynku wearables EEG i scenariusz wdrożenia.</li>
          </ul>
        </div>
        <div class="img-box" style="background: #ffffff; padding: 6px; margin-top: 12px;">
          <img src="{img_t1}" style="max-height: 155px;">
        </div>
      </div>
    </div>
  </div>
  <div class="footer">
    <span>Wachta — zmęczenie i czujność mierzone na człowieku, nie na zegarze</span>
    <span>Heroes of the Brain 2026 · Slajd 10 / 10</span>
  </div>
</section>

</body>
</html>
"""

    html_out = ART / "wachta-prezentacja-10-slajdow.html"
    pdf_out = ART / "wachta-prezentacja-10-slajdow.pdf"
    html_out.write_text(html, encoding="utf-8")

    cmd = [
        "/usr/bin/chromium",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_out}",
        f"file://{html_out}",
    ]
    subprocess.run(cmd, check=True)
    print(f"PDF generated: {pdf_out} ({pdf_out.stat().st_size / 1024:.1f} kB)")


if __name__ == "__main__":
    main()
