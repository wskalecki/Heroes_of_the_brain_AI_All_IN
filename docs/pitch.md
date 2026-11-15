# Pitch: personalizacja norm zmęczenia

Zadanie D1 z [`zadania.md`](zadania.md). Treść 10 slajdów: jedno zdanie główne, co pokazać i źródło każdej liczby.
Zasady: [`podstawy-naukowe.md`](podstawy-naukowe.md) §6 (co wolno twierdzić) i [`jury-i-kryteria.md`](jury-i-kryteria.md) §3.
Przebieg demo: [`scenariusz-demo.md`](scenariusz-demo.md).

## Pozycjonowanie w jednym zdaniu

**Wachta liczy normy zmęczenia dla konkretnego człowieka, a nie dla zegara: krótkie sesje EEG z testem reakcji uczą
osobistego profilu, a system na tej podstawie zmienia plan przerw i obsady.**

Co się zmieniło względem wcześniejszej wersji i dlaczego:

| Było | Jest | Powód |
|---|---|---|
| „Wykrywamy senność” | „Personalizujemy normy zmęczenia” | Senność przy otwartych oczach pokazują tylko dane publiczne (AUC 0,75); na naszych nagraniach mamy zamknięte oczy |
| „EEG kalibruje, zegarek pilnuje” | „EEG i test reakcji ustalają profil, na co dzień działa model kontekstu; zegarek to dodatkowy, osobny sygnał” | Serce i EEG nie są zamienne (COG-BCI, \|r\| ≤ 0,16) |
| EEG na głowie przez całą zmianę | Okresowe sesje kalibracyjne; EEG na żywo tylko w rolach, gdzie kask już jest | Akceptacja i koszt; ciągły monitoring EEG ma już SmartCap |

## Slajdy

### 1. Tytuł

**„Wachta: normy zmęczenia liczone dla człowieka, nie dla zegara.”**
Pod spodem nazwa zespołu i kategoria (Systemy adaptacyjne).

### 2. Problem

**„Przepisy dają wszystkim ten sam limit, a zmęczenie każdego dopada inaczej.”**

- Kierowca zawodowy w UE: maks. 9 h jazdy dziennie, przerwa 45 min po 4,5 h. Te same liczby dla każdego, niezależnie od snu i pory doby. Źródło: [Komisja Europejska, czas jazdy i odpoczynku](https://transport.ec.europa.eu/transport-modes/road/social-provisions/driving-time-and-rest-periods_en) (rozporządzenie 561/2006).
- Zmęczenie przyczynia się do 10–20% wypadków drogowych. Źródło: [Europejskie Obserwatorium Bezpieczeństwa Ruchu Drogowego (ERSO), zmęczenie](https://road-safety.transport.ec.europa.eu/statistics-and-analysis/statistics-and-analysis-archive/fatigue/fatigue_en). Na slajdzie podać przedział, bo szacunki zależą od definicji (od 6% do 24% w różnych badaniach).

### 3. Luka

**„Ludzie różnią się podatnością na zmęczenie w stały sposób, a ani normy, ani kamery tego nie mierzą.”**

- Różnice między osobami w spadku sprawności po braku snu są systematyczne i powtarzalne u tej samej osoby (Van Dongen i in. 2004, *Sleep* 27(3):423-33). Źródło: `podstawy-naukowe.md`, poz. 28.
- Kamera w aucie sprawdza, czy oczy są zamknięte. Nie widzi, czy mózg przy otwartych oczach jeszcze reaguje.
- Lotnictwo już dopuszcza normy oparte na danych (systemy zarządzania ryzykiem zmęczenia, FRMS) jako alternatywę dla sztywnych limitów. Źródło: [IATA FRMS 2025](https://www.iata.org/contentassets/5f976bb3ca2446f3a40e88b18dd61fbb/frms_white-paper_2025.pdf). Jeden z dokumentów roboczych ICAO (zgromadzenie A42) krytykuje, że FRMS nadal opierają się głównie na limitach i samoocenie; przed slajdem znaleźć i podać numer dokumentu.

### 4. Rozwiązanie

**„Osobisty profil zmęczenia z krótkich sesji EEG i testu reakcji, a z niego osobisty plan przerw.”**

Trzy elementy:
1. **Sesja kalibracyjna** (kilka minut, np. na początku zmiany, po nocach, raz w miesiącu): EEG z czepka i 3-minutowy test reakcji PVT-B. To uczy wzorca tej osoby.
2. **Model kontekstu na co dzień**: czas od przebudzenia, pora doby, czas pracy (uproszczony model dwuprocesowy). Bez czepka.
3. **Tryb na żywo** w rolach, gdzie kask albo czepek już jest: EEG wykrywa zamknięcie oczu i fale alfy w ciągu kilku sekund, a system od razu zmienia plan.

### 5. Jak to działa: pętla adaptacyjna

**„System nie tylko mierzy: sam zmienia rekomendację, prosi o reakcję i wskazuje zmiennika.”**

Diagram: sygnał (EEG: alfa z tyłu głowy, mrugnięcia; kontekst; reakcja) → stan (rezerwa czujności, rodzaj spadku) → zmiana zachowania
(„zaplanuj przerwę”, „przerwa teraz”, próba reakcji, zmiennik w panelu przełożonego). To jest odpowiedź na kryterium „zgodność z tematem”.

### 6. Demo

Film albo demo na żywo według [`scenariusz-demo.md`](scenariusz-demo.md). Ten sam przebieg: noc, kalibracja, szybka reakcja,
zamknięte oczy i „przerwa teraz”, brak reakcji przy otwartych oczach, zmiennik, przerwa.

### 7. Dowody

**„Mechanizm działa na naszym sprzęcie, a personalizacja ma oparcie w danych.”**

| Liczba | Źródło |
|---|---|
| Zamknięte oczy wykryte w 5 z 5 nagrań (4 osoby), 1 fałszywy alarm w 48 min | [`trafnosc-na-nagraniach.md`](trafnosc-na-nagraniach.md), wykres `img/trafnosc-na-nagraniach.png` |
| Senność w danych publicznych: alfa rośnie u 11 z 11 osób, AUC 0,75 (0,52–0,91) | notebook 04, wykres `img/drowsiness-public-auc-and-calibration.png` |
| Model osobisty: trafność 0,83 (AUC 0,90) wobec 0,66–0,72 dla jednego modelu dla wszystkich | notebook 04, tabela strategii |
| Kontekst (czas jazdy, pora doby) podnosi AUC z 0,76 do 0,88 | Lu i in. 2022, `podstawy-naukowe.md` poz. 3 |
| HRV zmienia się z czasem zadania tak jak czujność, ale jej nie mierzy (RMSSD a 1/RT: r = 0,18, po uwzględnieniu czasu zadania 0,05; 29 osób) | notebook 10 |
| 15 minut monotonii (T1, jedna osoba, KSS 5) bez ani jednego fałszywego alarmu, zamknięcie oczu wykryte po ok. 9 s | [`sesja-monotonii-wojtek.md`](sesja-monotonii-wojtek.md) |

### 8. Co zweryfikowane, a co założone (zadanie D4)

| Zweryfikowane | Założone, do sprawdzenia w pilotażu |
|---|---|
| Wykrywanie zamkniętych oczu i alfy na suchych elektrodach | Że osobisty limit przewiduje spadki czujności lepiej niż norma czasu i sam model kontekstu |
| Senność widać w EEG na naszych 8 kanałach (dane publiczne) | Senność przy otwartych oczach na naszych własnych nagraniach (zbieramy, zadanie C4; w sesji T1 jej nie było, KSS 5) |
| Personalizacja poprawia rozróżnianie stanów (dane publiczne) | Parametry rezerwy (tempo spadku, kary, wpływ nocy) |
| Działająca pętla na żywo z czepkiem BrainAccess | Że zegarek może zastąpić sesje EEG (nasze dane: nie zastąpi, może uzupełnić) |
| Zero fałszywych alarmów w 15 min monotonii (T1: jedna osoba, jedna sesja, KSS 5) | Że alfa przy otwartych oczach ostrzega przed spadkiem czujności: **sprawdziliśmy i nie ostrzega** (AUC 0,52 na 29 osobach, notebook 06), więc tego nie obiecujemy |

### 9. Rynek, model, prawo

**„Zaczynamy tam, gdzie kask już jest albo przepisy już wymagają zarządzania zmęczeniem.”**

- **Segment wejścia (propozycja, decyzja w zadaniu D2):** kopalnie, budowa, operatorzy maszyn (kask jest, EEG w kasku akceptowalne);
  potem branże z obowiązkiem zarządzania zmęczeniem (lotnictwo i kontrola ruchu, energetyka). Transport drogowy jako trzeci krok,
  bo tam wygrywa tania, obowiązkowa kamera.
- **Różnica względem SmartCap:** oni alarmują, my zmieniamy plan pracy i ustalamy osobisty limit. Źródło: [`rynek-eeg-wearables.md`](rynek-eeg-wearables.md).
- **Rynek:** oprogramowanie do zarządzania ryzykiem zmęczenia 345 mln USD (2025) → 877 mln USD (2032). Źródło: LP Information, w [`rynek-wielkosc-i-kierunek.md`](rynek-wielkosc-i-kierunek.md) §2c. Podać jako szacunek z jednego raportu.
- **Model:** licencja za stanowisko miesięcznie plus sesje kalibracyjne; sprzęt od partnera (BrainAccess). Kwoty jako założenia, nie dane.
- **Prawo:** zmęczenie to stan fizyczny, a nie emocja, więc nie podlega zakazowi rozpoznawania emocji w pracy ([AI Act, motyw 18](https://artificialintelligenceact.eu/recital/18/)).
  Surowe EEG zostaje u pracownika, przełożony widzi tylko gotowość.

### 10. Co dalej

**„Pilotaż na jednej zmianie: czy osobisty limit przewiduje spadki czujności lepiej niż norma.”**

- Miary: lapsy w teście PVT-B, zdarzenia na zmianie, ocena senności (KSS). Porównanie trzech wariantów: norma czasu, model kontekstu, model osobisty.
- Własne nocne pomiary z testem reakcji już zbieramy (zadanie C4).
- Zespół: imiona i role.

## Zdania, których nie używamy

Z [`podstawy-naukowe.md`](podstawy-naukowe.md) §6 i [`scenariusz-demo.md`](scenariusz-demo.md):
„wykrywamy senność z trafnością X%”, „zegarek zastąpi EEG”, „mierzymy stres / skupienie / przeciążenie”,
„rezerwa jest zmierzona”, „EEG ostrzega przed spadkiem czujności”, „system przewiduje mikrosen” (notebook 06: alfa nie przewiduje lapsu). Liczb rynkowych nie podajemy bez źródła i roku.
