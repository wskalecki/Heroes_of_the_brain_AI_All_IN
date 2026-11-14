# Wielkość rynku i wybór kierunku: Wachta / „AI oddaje ster”

Research pod pitch na Heroes of the Brain (listopad 2026). Uzupełnia plik `rynek-eeg-wearables.md` (konkurencja).

> **Uwaga o liczbach z raportów rynkowych:** szacunki firm badawczych dla tego samego rynku różnią się kilkukrotnie (patrz sekcja 1). Na slajdzie podawajcie zawsze źródło i rok, a najlepiej przedział, nie jedną liczbę.

---

## 1. Rynek sprzętu i BCI (kontekst, nie wasz rynek)

| Rynek | Wartość | Prognoza | Źródło |
|---|---|---|---|
| Wearable EEG headsets | 1,73 mld USD (2025) → 1,95 mld USD (2026) | 3,08 mld USD w 2030, CAGR 12,2% | [The Business Research Company via ResearchAndMarkets](https://www.researchandmarkets.com/reports/6012848/wearable-electroencephalogram-eeg-headsets) |
| Wearable EEG headsets (inna definicja) | 145,8 mln USD (2024) | 256,6 mln USD w 2030, CAGR 9,9% | [Market Glass / GlobeNewswire](https://www.globenewswire.com/news-release/2025/01/31/3018673/0/en/Wearable-EEG-Headsets-Strategic-Business-Report-2025-2030-Rising-Demand-for-Brain-Health-Monitoring-Fuels-Adoption.html) |
| BCI ogółem | 2,2 mld USD (2025), 2,8 mld USD (2026) | 8,6 mld USD w 2036, CAGR 11,8%; nieinwazyjne BCI mają największy udział | [Meticulous Research](https://www.meticulousresearch.com/product/brain-computer-interface-market-6654) |
| BCI ogółem (inna metodologia) | 1,4 mld USD (2026) | 2,26 mld USD w 2031; nieinwazyjne zestawy dały 75,9% przychodu w 2025 | [Mordor Intelligence via GII](https://www.giiresearch.com/report/moi2123491-brain-computer-interface-market-share-analysis.html) |

**Wniosek:** rozrzut 10x między raportami dla „wearable EEG” pokazuje, że to młody rynek. Nie budujcie pitchu na rynku sprzętu. Wasz rynek to oprogramowanie do operacji i bezpieczeństwa, a EEG jest tylko czujnikiem.

---

## 2. Rynki, w które realnie się wpinacie

### 2a. IT ops, dyżury i obsługa incydentów
- **PagerDuty (lider dyżurów):** przychód 492,5 mln USD w roku fiskalnym 2026 (+5,4%), ARR 498,7 mln USD, 15 351 płacących klientów, ponad 35 000 klientów łącznie z darmowymi. Sami nazywają się „control plane for AI operations” i rozwijają agentów SRE. [Wyniki PagerDuty FY2026](https://www.businesswire.com/news/home/20260312052737/en/PagerDuty-Announces-Fourth-Quarter-and-Full-Year-Fiscal-2026-Financial-)
- **Rynek oprogramowania do zarządzania incydentami:** 3,94 mld USD w 2025 → 11,4 mld USD w 2032, CAGR 16,4% ([VPA Research](https://www.marketresearch.com/VPA-Research-v4245/Incident-Management-Software-Size-Share-40859583)). Inny raport podaje 1,24 mld USD w 2023 i 2,26 mld USD w 2030 ([Orbis/QYResearch](https://orbisresearch.com/reports/index/incident-management-software-global-market-share-and-ranking-overall-sales-and-demand-forecast-2024-2030)).
- **Platformy ITSM:** 15,44 mld USD w 2025 → 30,15 mld USD w 2030 ([Virtue Market Research](https://virtuemarketresearch.com/report/it-service-management-itsm-platforms-market)).

**Ból (liczby do slajdu „Problem”):**
- Przestoje kosztują firmy z Global 2000 **400 mld USD rocznie**, czyli 200 mln USD na firmę i ok. 9% zysków; minuta przestoju to średnio **9 000 USD** ([Splunk + Oxford Economics, The Hidden Costs of Downtime](https://splunk.com/en_us/pdfs/gated/ebooks/the-hidden-costs-of-downtime.pdf)).
- **77%** zespołów dyżurnych dostaje co najmniej 10 alarmów dziennie, a 57% mówi, że mniej niż 30% z nich wymaga działania; prawie 40% organizacji twierdzi, że ponad jedna czwarta dyżurnych ma objawy wypalenia ([2026 State of Production Reliability, 1 039 respondentów](https://www.carriermanagement.com/news/2026/04/08/286535.htm)).
- **75%** brytyjskich zespołów IT miało w 2025 awarie przez przegapione alarmy; 13% globalnie celowo ignoruje lub wycisza alarmy ([Splunk via Computer Weekly](https://www.computerweekly.com/news/366637587/Three-quarters-of-UK-IT-teams-beset-by-outages-due-to-missing-alerts)).
- Prawie **70% SRE** mówi, że stres z dyżurów przyczynia się do wypalenia i chęci odejścia ([Catchpoint 2025 via DevOps.com](https://devops.com/on-call-the-silent-force-shaping-engineering-culture/)).

### 2b. Centra bezpieczeństwa (SOC)
- Średnio **960 alarmów dziennie** na organizację, 3 181 w dużych firmach; ok. **40%** alarmów nie jest badanych ([Prophet Security, State of AI in SOC](https://www.prophetsecurity.ai/blog/6-key-takeaways-from-the-ai-in-soc-survey-report)).
- **60%** zespołów miało przypadek, gdy zignorowany alarm okazał się istotny ([Prophet Security via SecurityInfoWatch](https://www.securityinfowatch.com/ai/article/55315748/prophet-security-report-highlights-urgent-need-for-ai-in-socs)). W edycji 2026 mediana nieprzebadanych alarmów to 22% ([zestawienie NHIMG](https://www.nhimg.org/soc-and-alert-statistics-guide)).
- **83%** analityków czuje się przytłoczonych liczbą alarmów ([IT Brief](https://itbrief.co.uk/story/soc-analysts-face-alert-overload-duplicate-effort-survey-finds)).

### 2c. Zarządzanie zmęczeniem w przemyśle i transporcie (zajęte przez SmartCap)
- Oprogramowanie do zarządzania ryzykiem zmęczenia: **345 mln USD (2025) → 877 mln USD (2032)**, CAGR 14,5% ([LP Information](https://www.marketresearch.com/LP-Information-Inc-v4134/Global-Fatigue-Risk-Management-Software-44138237)).
- Systemy wykrywania zmęczenia kierowców: 1,85 mld USD (2025) → 5,55 mld USD (2034) ([Intel Market Research](https://www.intelmarketresearch.com/fatigue-driving-monitoring-system-market-market-22052)). Głównie kamery, nie EEG.

### 2d. Kontrola ruchu lotniczego i dyspozytornie
- Rozporządzenie UE 2017/373 (od stycznia 2020) nakłada na instytucje zapewniające służby ruchu lotniczego wymagania dotyczące zmęczenia i stresu kontrolerów; Eurocontrol wydał wytyczne w kwietniu 2024 ([Terenzi i in., Aerospace 2024](https://katalog.lib.cas.cz/KNAV/EdsRecord/edsdoj,edsdoj.b73c3c90a4ac46a385a48c8abe506e6e)).
- Badanie EASA na 216 kontrolerach: **5,6% dyżurów** wiązało się z krytycznym poziomem zmęczenia; główne przyczyny to nocne zmiany i monotonny ruch ([Vrancken i in. 2025](https://reports.nlr.nl/items/488da708-e0de-4fe0-bd7c-0cb459a1bbb9)).
- Badania EEG nad kontrolerami już są (projekt STRESS w ramach SESAR z Uniwersytetem Sapienza) ([OHS Online](https://ohsonline.com/articles/2017/06/19/eurocontrol-participating-in-fatigue-research.aspx)).

---

## 3. Bariera prawna, która decyduje o kierunku: EU AI Act art. 5

**To najważniejsza sekcja dla wyboru kierunku.**

- AI Act **zakazuje rozpoznawania emocji w miejscu pracy i w edukacji**, z wyjątkiem celów medycznych i bezpieczeństwa. Wytyczne Komisji wprost wymieniają EEG ([IAPP](https://iapp.org/news/a/neurotechnologies-under-the-eu-ai-act-where-law-meets-science)).
- **Zmęczenie to stan fizyczny, nie emocja.** Wykrywanie zmęczenia pilota czy kierowcy w celu ostrzeżenia go nie jest rozpoznawaniem emocji ([Lewis Silkin](https://www.lewissilkin.com/insights/2025/02/17/understanding-the-eu-ai-acts-prohibited-practices-key-workplace-and-advertising-102k011)).
- **Wykrywanie wypalenia lub depresji w pracy jest zakazane** i nie mieści się w wyjątku bezpieczeństwa (tamże).
- Wyjątek bezpieczeństwa jest wąski: nie jest furtką do ogólnego monitoringu dobrostanu pracowników ([SecurePrivacy](https://secureprivacy.ai/blog/eu-ai-act-article-5-prohibited-ai-practices-and-compliance-guide-2026)).
- Szara strefa: proponowane zmiany (Digital Omnibus) mogą rozszerzyć zakaz na „poziom zaangażowania i stany psychologiczne” ([analiza sota.io](https://sota.io/blog/eu-ai-act-digital-omnibus-art-5-1-j-emotion-inference-workplace-education-prohibition-developer)). Niezweryfikowane w oficjalnym tekście.

**Co to oznacza dla was:**
- ✅ Bezpieczne: **czujność, senność, mikrosen** (stany fizyczne) w kontekście bezpieczeństwa operacji.
- 🟡 Szara strefa: **obciążenie poznawcze** jako metryka; bezpieczniej opisywać je jako „przeciążenie zadaniowe” powiązane z bezpieczeństwem, nie jako stan psychiczny.
- ❌ Unikać: stres, frustracja, emocje, zaangażowanie, wypalenie. Nie mówcie w pitchu „wykrywamy stres pracownika”.
- Pomysł z panelem kierownika „kto jest wypalony” jest w UE **nielegalny**. Panel ma pokazywać tylko gotowość do przejęcia incydentu.

**To jest argument dla was, nie przeszkoda:** konkurencja z USA (Emotiv, Neurable) mówi o stresie i dobrostanie. Wy budujecie produkt zgodny z AI Act od pierwszego dnia, oparty tylko na czujności i bezpieczeństwie.

---

## 4. Ocena segmentów (skala 1–10)

Kryteria:
- **Ból:** jak bardzo to boli i czy da się to wyrazić w pieniądzach.
- **Luka:** jak mało konkurencji z EEG.
- **Prawo UE:** 10 = bezpiecznie w świetle AI Act.
- **Sprzedaż:** 10 = krótki cykl, decyduje jeden zespół.
- **Demo:** jak dobrze to wypada na scenie przy waszym sprzęcie.
- **Wynik:** Ból×0,25 + Luka×0,25 + Prawo×0,2 + Sprzedaż×0,15 + Demo×0,15 (wagi do zmiany).

| Segment | Ból | Luka | Prawo UE | Sprzedaż | Demo | **Wynik** |
|---|---|---|---|---|---|---|
| **IT ops / dyżury (PagerDuty, Grafana)** | 8 | 9 | 7 | 8 | 9 | **8,25** |
| **SOC (centra bezpieczeństwa)** | 9 | 9 | 6 | 7 | 8 | **7,95** |
| Kontrola ruchu lotniczego / dyspozytornie energetyczne | 9 | 6 | 9 | 2 | 7 | **6,9** |
| Agenci AI eskalujący do człowieka (horyzontalnie) | 7 | 8 | 7 | 5 | 9 | **7,25** |
| Kopalnie i transport | 9 | 2 | 9 | 4 | 6 | **6,05** |
| Pracownicy umysłowi i skupienie (konsumencko) | 4 | 2 | 3 | 6 | 8 | **4,25** |

Uzasadnienie kilku ocen:
- **IT ops, prawo 7:** czujność dyżurnego to argument bezpieczeństwa operacji, ale nie bezpieczeństwa życia, więc trzymajcie się stanów fizycznych.
- **SOC, sprzedaż 7:** SOC ma budżet, ale jest ostrożniejszy wobec nowych narzędzi.
- **Kontrola ruchu lotniczego, sprzedaż 2:** regulacja już wymaga zarządzania zmęczeniem, ale certyfikacja i zamówienia publiczne trwają latami.
- **Kopalnie, luka 2:** SmartCap jest standardem.
- **Konsumenci, prawo 3:** marketing „skupienia i stresu” przy pracy wchodzi w zakaz, a rynek jest zajęty przez Neurable i Muse.

---

## 5. Rekomendacja

**Wejście: IT ops i dyżury (on-call), z SOC jako drugim krokiem.**
Produkt: warstwa do PagerDuty, Opsgenie i Grafany, w której agent AI obsługuje incydent sam i eskaluje do człowieka, uwzględniając jego czujność. Wybiera, kogo obudzić, i dobiera formę komunikatu.

Dlaczego:
1. Ból jest policzalny w pieniądzach (9 000 USD za minutę przestoju) i potwierdzony ankietami z 2026.
2. Nikt nie robi tego z EEG; konkurencja w IT ops (np. Rootly On-Call Health) mierzy wypalenie z metadanych incydentów, nie stan człowieka w chwili alarmu ([Rootly](https://rootly.com/blog/introducing-on-call-burnout-detector.md)).
3. Integracje przez API, więc pilot to tygodnie, a nie lata.
4. Trend agentów AI w ops: PagerDuty sam buduje agentów SRE, więc jest naturalnym partnerem lub kupującym.
5. Demo na hackathonie jest wiarygodne: senność z alfy działa na waszym sprzęcie.

**Ekspansja (slajd „co dalej”):** dyspozytornie energetyczne i kontrola ruchu lotniczego, gdzie prawo UE już wymaga zarządzania zmęczeniem i gdzie wyjątek bezpieczeństwa z AI Act jest najmocniejszy.

**Model przychodu (założenie do weryfikacji, nie dane):** licencja za stanowisko dyżurne miesięcznie. Jako punkt odniesienia: średnia stawka za dyżur wynosi ok. 540 USD tygodniowo na osobę ([incident.io](https://incident.io/content/uncovering-the-mysteries-of-on-call)), więc firmy już płacą za dyżury i rozumieją ich koszt.

**Przykładowe wyliczenie rynku dostępnego (ilustracja, same założenia):**
- jeśli 10% z 15 351 płacących klientów PagerDuty wdroży produkt,
- średnio 20 stanowisk dyżurnych na klienta,
- 30 USD za stanowisko miesięcznie,
- to ok. 1 535 × 20 × 30 × 12 ≈ **11 mln USD rocznie** tylko w bazie jednego partnera.

Na slajdzie podpiszcie to jako założenia, nie dane.

---

## 6. Ryzyka do slajdu
1. **Akceptacja:** czy dyżurny założy opaskę w nocy w domu. Odpowiedź: słuchawki z EEG (Neurable) i pchełki (Emotiv, IDUN) już są w sprzedaży.
2. **Prawo:** AI Act i RODO (dane biometryczne). Odpowiedź: tylko stany fizyczne, przetwarzanie lokalne, operator widzi to samo co system.
3. **Sygnał:** suche elektrody i ruch. Odpowiedź: łączenie z sygnałami niebiologicznymi (czas reakcji na alarm, aktywność klawiatury).
4. **Sprzęt:** zależność od dostawcy. Odpowiedź: warstwa niezależna od sprzętu (BrainAccess, Muse, Neurable przez LSL lub BrainFlow).

## Czego tu nie ma
- Liczby dyżurnych inżynierów i analityków SOC w Europie (brak wiarygodnego źródła).
- Oficjalnego tekstu Digital Omnibus: trzeba sprawdzić przed finałem.
