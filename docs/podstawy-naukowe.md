# Podstawy naukowe: EEG + sygnały fizjologiczne w ocenie zmęczenia, senności i czujności

> **Status:** opracowanie przygotowane 14.11.2026 z literatury i sprawdzone źródło po źródle (abstrakt lub pełny tekst, status przy każdej pozycji).
> Identyfikatory PMID wyrywkowo porównano z tytułami w PubMed. Liczby z abstraktów warto jeszcze raz przejrzeć w pełnym tekście, zanim trafią na slajd.
> Sekcje o naszych wynikach odwołują się do notebooków w `data/analysis/`.

Opracowanie dla projektu Wachta. Stan na 2026-11-14. Każde źródło ma status weryfikacji:
**[VERIFIED: full text]** (czytany pełny tekst lub jego kluczowe fragmenty), **[VERIFIED: abstract]** (czytany abstrakt / rekord PubMed),
**[NOT VERIFIED]** (nie udało się potwierdzić, nie cytować jako faktu).

## Streszczenie (10 linii)

1. Wzrost mocy theta/alfa przy senności i zmiany alfa zależne od stanu oczu to wynik stary i wielokrotnie potwierdzony, ale **kierunek zmiany alfa zależy od tego, czy oczy są otwarte, czy zamknięte**. Wykrycie zamknięcia oczu to nie to samo co wykrycie senności.
2. Senność zwykle obniża tętno (HR) i zwiększa jego zmienność. Pobudzenie wysiłkiem lub zaangażowaniem w zadanie może działać w drugą stronę, więc HR/HRV nie są markerem jednoznacznym.
3. HRV sama działa umiarkowanie: 61% (3 klasy, 86 kierowców w realnym ruchu), AUC 0,76 z opaski piersiowej. Kontekst (pora dnia, czas jazdy) podnosi AUC do 0,88.
4. Fuzja modalności zwykle poprawia wynik, ale w literaturze dominuje walidacja wewnątrzosobowa z losowym podziałem okien. Przy leave-one-subject-out wyniki spadają do ok. 55-79%.
5. PPG z nadgarstka nadaje się do HR i trendów HRV w spoczynku. W ruchu i przy pojedynczych pomiarach bezwzględnych błąd RMSSD sięga −41% do +118%.
6. RMSSD z 60 s EKG jest akceptowalne (dla EKG w spoczynku r ≈ 0,94 już przy 3×10 s, 0,986 przy 120 s). LF/HF z 60 s nie ma sensu, a jego interpretacja jako „balansu współczulno-przywspółczulnego” jest kwestionowana.
7. Podatność na brak snu to cecha osobnicza, stabilna u danej osoby (Van Dongen 2004). To mocny argument za kalibracją osobistą.
8. Nie znalazłem badania, które robi dokładnie „krótka sesja EEG → osobisty model dla taniego czujnika”. Są precedensy częściowe: EEG jako etykieta lub walidacja dla HRV i eye-trackingu.
9. Model „rezerwy czujności” powinien uwzględniać proces homeostatyczny, fazę okołodobową i czas wykonywania zadania (modele dwu- i trzyprocesowe).
10. Wszystkie liczby z briefu, które miałem sprawdzić, potwierdziłem co najmniej na poziomie abstraktu. Szczegóły i luki opisuję niżej.

---

## 1. Fizjologia

**Alfa, theta i zamknięcie oczu.** Przejście z oczu zamkniętych do otwartych obniża moc we wszystkich pasmach, najsilniej alfa. Średnia alfa jest używana jako wskaźnik pobudzenia w spoczynku. Przy zamkniętych oczach poziom przewodnictwa skóry korelował ujemnie z alfa (n = 28; Barry i in. 2007). W 40-godzinnej deprywacji snu senność subiektywna korelowała **ujemnie** z globalną alfa (8-12 Hz) i **dodatnio** z czołowo-centralną theta (Strijkstra i in. 2003). W protokole constant routine moc 6,25-9 Hz rosła z czasem czuwania (n = 9; Cajochen i in. 1995). Walidacja KSS (n = 16 kobiet, 8 sesji dziennie przez 3 dni) pokazała, że wraz z KSS rosną moc alfa i theta, współczynnik tłumienia alfa (stosunek alfa przy oczach otwartych do zamkniętych), czas reakcji i liczba lapsów w PVT. Korelacja KSS z lapsami wynosiła średnio r = 0,56 (Kaida i in. 2006). W terenie u maszynistów (n = 11) w nocnej jeździe rosły alfa, w mniejszym stopniu theta i delta, a także wolne ruchy gałek ocznych. Korelacje wewnątrzosobowe z senością były „bardzo wysokie”, ale efekt dotyczył głównie 6 najbardziej sennych osób (Torsvall i Åkerstedt 1987).
*Wniosek dla zespołu:* alfa przy otwartych oczach rośnie, gdy pojawiają się „wtrącenia” senności. Alfa przy zamkniętych oczach u sennej osoby słabnie. Detektor „oczy zamknięte”, który działa u was 4/4, jest dobrym testem jakości sygnału i sprzętu. **Nie jest** jeszcze dowodem detekcji senności.

**Układ autonomiczny.** W przeglądzie badań pilotów i kierowców senność wiązała się ze wzrostem częstości mrugania i spadkiem HR (Borghini i in. 2014). W realnej jeździe (n = 43) ciężkiej senności towarzyszyło niższe HR i wyższa ogólna zmienność rytmu (Lu i in. 2022). RMSSD i moc HF są zwykle interpretowane jako wskaźniki aktywności nerwu błędnego. Billman (2013) pokazuje jednak, że stosunek LF/HF **nie mierzy** balansu współczulno-przywspółczulnego: LF nie jest czystym wskaźnikiem układu współczulnego, a HF zależy też od oddechu. Nie należy więc mówić „LF/HF = poziom współczulny”.

**Dlaczego EEG i HRV mogą się nie zgadzać.** To dwa różne układy o różnych skalach czasu. EEG zmienia się w sekundach (mikrosen, wtrącenia alfa), a HRV liczy się z okien od dziesiątek sekund do minut. Na HR/HRV silnie wpływają: oddech (sprzężenie oddechowo-sercowe), ruch i aktywność fizyczna, postawa, mowa, stresory umysłowe (Schäfer i Vagedes 2013; Shaffer i Ginsberg 2017), a w ruchu drogowym wiele czynników innych niż senność (Persson i in. 2019). Eksploracyjne badanie (n = 12, 5 h) pokazało rozbieżne sygnatury. Zadania wymagające aktywnej pracy dawały dominację współczulną i wzrost beta. Monotonne monitorowanie dawało alfa ciemieniowo-potyliczną i przejście w kierunku przywspółczulnym (Hu i in. 2026). *Interpretacja waszego wyniku z COG-BCI:* wzrost HR u 13/16 osób w trakcie 10-minutowego PVT jest **przeciwny** do typowego profilu senności (spadek HR). Pasuje raczej do zaangażowania i wysiłku w zadaniu albo do efektu początku zadania. To hipoteza, nie wynik. Słabe korelacje EEG z HRV minuta do minuty (|r| ≤ 0,16) są zgodne z literaturą i nie świadczą o błędzie analizy.

## 2. Fuzja modalności: dowody

**Sprawdzone pozycje z briefu:**

- **Fujiwara i in. 2019, IEEE TBME** [VERIFIED: abstract]. Symulator, 34 uczestników, RRI z EKG. Ośmiu cech HRV monitorowano metodą multivariate statistical process control (detekcja anomalii). Referencją był zapis senności z EEG oceniony przez specjalistę. Senność wykryto przed 12 z 13 epizodów pre-N1, przy 1,7 fałszywego alarmu na godzinę. **Potwierdzone.** Zastrzeżenia: tylko 13 epizodów, symulator. Z abstraktu nie wynika, czy model jest budowany osobno dla każdej osoby (detekcja anomalii zwykle wymaga osobistego okresu „normalnego”). Tego nie zweryfikowałem.
- **Persson i in. 2019, EMBC** [VERIFIED: abstract]. 86 kierowców, realne drogi, warunki wypoczęte i po deprywacji snu, 24 metryki HRV, SVM, etykiety KSS w 3 klasach. Prawie wszystkie metryki różniły się istotnie między poziomami senności, a mimo to trafność klasyfikacji wyniosła tylko **61%**, najgorzej dla ciężkiej senności. Autorzy piszą wprost, że wysokich wyników z kontrolowanych badań nie udało się powtórzyć w realnych warunkach. **Potwierdzone.** Schematu walidacji nie zweryfikowałem.
- **Lu i in. 2022, IEEE T-ITS 23(5):4801-4810**, „Detecting Driver Sleepiness Using Consumer Wearable Devices in Manual and Partial Automated Real-Road Driving” [VERIFIED: abstract]. 43 uczestników, realna droga, jazda manualna i częściowo zautomatyzowana, wypoczęci i po deprywacji. HR z konsumenckiej **opaski piersiowej**, KSS co 5 min, AdaBoost. Same HRV dały **AUC = 0,76**, a po dodaniu czasu jazdy i informacji dzień/noc **AUC = 0,88**. **Potwierdzone.** Wniosek: kontekst czasowy niesie dużą część informacji. Schematu walidacji (osobowy czy nie) nie zweryfikowałem, bo PDF był niedostępny.
- **Wu i in. 2023, Comput Biol Med 167:107590** [VERIFIED: abstract]. Porównanie czołowego EEG, EOG, RRI i oddechu w konfiguracji możliwej do noszenia. Ciągła estymacja senności (regresja, przejście z czuwania do senności). Najlepszy praktyczny zestaw to **czołowe EEG lub EOG + RRI + oddech wyliczony z RRI**. Gdy liczy się wygoda, obiecujące jest samo RRI + oddech z RRI. Abstrakt nie podaje liczb (współczynników korelacji) ani liczby osób, więc **nie cytować konkretnych wartości**.
- **Rivas-Vidal i in., Front Neuroergon** (DOI 10.3389/fnrgo.2025.1736672; w PMC opublikowane 29.01.2026, tom 6) [VERIFIED: full text]. Przegląd systematyczny (PRISMA), 47 badań z równoczesnym EEG i eye-trackingiem (ET). Fuzja zwykle poprawiała klasyfikację. **Dla czujności EEG było lepsze od ET**, a dla obciążenia i mind wandering ET było lepsze od EEG. Przykłady dla czujności: Pan i in. 2024 (4 klasy): ET 75,8%, EEG 83,0%, fuzja 88,8%. Farha i in. 2022 (2 klasy): ET 76,8%, EEG 92%, fuzja 96,8%. Dla zmęczenia i senności **wpływu fuzji nie dało się ocenić**, bo brakowało danych porównawczych. Autorzy piszą, że mało badań stosowało walidację międzyosobową, a tam wyniki były niższe.
- **LaRocco i in. 2020, Front Neuroinform** (PMC7593569) [VERIFIED: full text]. 46 badań z tanimi headsetami EEG (NeuroSky, Muse, Emotiv, OpenBCI), z czego ok. 27 podało trafność. Najniższa wynosiła 31% (NeuroSky), następna 79,4% (OpenBCI). Proste cechy widmowe „konsekwentnie” wykrywały senność. Różne definicje senności, kalibracje i metryki uniemożliwiały porównania, a niezawodność w warunkach pracy pozostaje problemem.

**Dodatkowe źródła:**

- **Chua i in. 2012, Sleep** [VERIFIED: abstract]. 24 mężczyzn, 40 h bez snu, PVT co 2 h. Moc RR w paśmie 0,02-0,08 Hz śledziła profil lapsów PVT i wykrywała wzrost lapsów **równie dobrze jak moc EEG**, z czułością i swoistością zbliżoną do PERCLOS. To najmocniejszy dowód, że EKG niesie informację o czujności, uzyskany jednak przy całkowitej deprywacji snu, czyli przy dużym efekcie.
- **Vicente i in. 2016, Med Biol Eng Comput** [VERIFIED: abstract]. HRV na 3 bazach, 3475 minut jazdy oznaczonych minuta po minucie. PPV 0,96, czułość **0,59**, swoistość 0,98. Detektor deprywacji snu na podstawie pierwszych 3 minut jazdy (30 kierowców): PPV 0,80, czułość 0,62, swoistość 0,88. Wysoka swoistość idzie w parze z niską czułością.
- **Kundinger i in. 2020, Sensors** [VERIFIED: full text]. Najlepsza ilustracja zawyżania wyników. 30 osób (27 w analizie), symulator, nadgarstek Empatica E4 i referencyjne EKG. Cechy HRV liczono z okien 5 min przesuwanych co **2 s**. Test „zależny od użytkownika” (10-krotna stratyfikowana CV na tych silnie nakładających się oknach) dał do **92,1% (nadgarstek) i 97,4% (EKG)**. Leave-one-subject-out dał tylko **43-73% (nadgarstek) i 26-79% (EKG)**, z F1 dla klasy „senny” 0,12-0,65. Wysoki wynik z abstraktu (>92%) wynika głównie z przecieku danych między foldami.
- **Borghini i in. 2014, Neurosci Biobehav Rev** [VERIFIED: abstract]. EEG, EOG i HR u pilotów i kierowców układają się w spójną sekwencję zmian. Obciążenie to theta↑ i alfa↓. Przejście w zmęczenie to theta, delta i alfa↑. Senność to częstsze mruganie i HR↓. Detekcja działa „offline z trafnością około 90%, ale nie online”.
- **Lal i Craig 2001, Biol Psychol** [VERIFIED: abstract]. Klasyczny przegląd: EEG to najbardziej obiecujący wskaźnik zmęczenia kierowcy, a przejście w zmęczenie wiąże się głównie ze zmianami theta i delta.
- **Paulo i in. 2021, IEEE TNSRE** [VERIFIED: abstract]. EEG, 27 osób, leave-one-subject-out, zrównoważona trafność do **75,9%**. Daje punkt odniesienia dla waszego średniego AUC 0,75 między osobami.

**Ocena ogólna.** Fuzja w laboratorium poprawia wynik o kilka do kilkunastu punktów procentowych. Większość badań ma jednak 10-40 osób, symulator i walidację wewnątrzosobową. Jedyne duże badanie w realnym ruchu z samą HRV (Persson, n = 86) dało 61%.

## 3. Wearables: sprawdzenie realiów

- **PPG a EKG.** Zmienność rytmu z PPG (PRV) jest wystarczająco dokładna w spoczynku, ale zwykle zawyża zmienność krótkoterminową. Aktywność fizyczna i część stresorów umysłowych psują zgodność, „często w niedopuszczalnym stopniu” (Schäfer i Vagedes 2013). Przegląd 18 badań wearables (w tym tylko 2 z PPG) pokazał bardzo dobrą do doskonałej korelację w spoczynku, malejącą wraz z intensywnością wysiłku (Georgiou i in. 2018). Błąd bezwzględny HR z optycznych czujników był w aktywności średnio o 30% wyższy niż w spoczynku i różnił się między urządzeniami (Bent i in. 2020).
- **Garmin.** Walidacja Forerunner 955 (czujnik Elevate v4; n = 23, spoczynek, kontrolowany oddech): HR r ≥ 0,94 względem EKG. RMSSD z PPG było powtarzalne, ale zgodność z EKG była ograniczona, z błędem proporcjonalnym. Granice zgodności wynosiły od −43% do +52% na leżąco i od −41% do +118% na siedząco. Autorzy uznali urządzenie za dobre do HR i **trendów wewnątrzosobowych**, ale nie do bezwzględnej oceny autonomicznej (Casanova-Lizón i in. 2026). Dokumentacja Connect IQ podaje, że **Venu 2** obsługuje `heartBeatIntervals`, czyli odstępy uderzenie-uderzenie w ms [VERIFIED: dokumentacja producenta]. Jakości tych danych dla Venu 2 w ruchu **nie znalazłem** w recenzowanych pracach. Nie zweryfikowałem też, czy Venu 2 ma ten sam czujnik co Forerunner 955.
- **Długość okna RMSSD.** W badaniu na 3387 osobach (EKG w spoczynku) RMSSD z jednego 10-sekundowego zapisu korelowało z RMSSD z 4-5 min na poziomie r = 0,85-0,86, ze średniej z 3×10 s r = 0,94, a z 120 s r = 0,986 (Munoz i in. 2015). Okno 60 s nie było testowane bezpośrednio, ale leży między wariantami o dobrej zgodności, więc **60 s dla RMSSD z EKG jest uzasadnione**. Dla PPG w trakcie zadania tego nie wiadomo. Normy krótkoterminowe, ultrakrótkie i 24-godzinne nie są wymienne (Shaffer i Ginsberg 2017). Kundinger i in. powołują się na Task Force (1996), który zaleca 2-5 min dla cech częstotliwościowych. Sam dokument Task Force sprawdziłem tylko na poziomie metadanych. **LF/HF ani HF z 60 s nie liczyć**, a przynajmniej nie interpretować.
- **Czy detekcja senności z samego wearable działa?** Częściowo. Opaska piersiowa w realnej jeździe daje AUC 0,76, a z kontekstem 0,88 (Lu 2022). Nadgarstek w symulatorze przy uczciwej walidacji (LOSO) daje 55-73% (Kundinger 2020). HRV z EKG w realnym ruchu daje 61% (Persson 2019). To sygnał wspierający, nie samodzielny detektor.
- **EDA, temperatura skóry, akcelerometr, oddech.** Oddech wyliczony z RRI pomagał w fuzji (Wu 2023). EDA koreluje ujemnie z alfa przy zamkniętych oczach (Barry 2007). Nie zweryfikowałem żadnego badania, które dawałoby liczby dla EDA, temperatury skóry czy akcelerometru w detekcji senności, więc **nie cytować ich jako dowodu**. Akcelerometr ma realną wartość jako detektor ruchu, który unieważnia okna HRV. To wniosek z prac o artefaktach ruchowych (Bent, Schäfer), a nie z badań senności.

## 4. Personalizacja

- **Różnice osobnicze to cecha, nie szum.** Van Dongen i in. (2004) trzykrotnie poddali 21 osób 36-godzinnej deprywacji snu, w odstępach co najmniej 2 tygodni. Różnice w pogorszeniu sprawności były **systematyczne i stabilne u danej osoby**. Ich skala była duża w porównaniu z efektem wcześniejszego ograniczenia snu (średnio 4,1 h/dobę mniej przez 7 dni). Nie wyjaśniał ich poziom wyjściowy ani inne predyktory. Różnice skupiały się w 3 wymiarach: ocena subiektywna, przetwarzanie poznawcze i czujność behawioralna.
- **W danych z terenu efekt bywa skupiony u części osób** (Torsvall i Åkerstedt 1987: zmiany EEG i EOG głównie u 6 z 11 maszynistów).
- **Modele osobowe a populacyjne.** U Kundingera różnica między modelem zależnym a niezależnym od użytkownika jest ogromna (92% wobec ok. 60%), ale jest zawyżona przez przeciek okien, więc nie jest czystą miarą zysku z personalizacji. Przegląd EEG+ET również notuje spadki przy walidacji międzyosobowej (Rivas-Vidal 2025). Próby modeli EEG bez kalibracji osiągają 75,9% w LOSO (Paulo 2021) i 76,7-83,3% między zbiorami danych (Cui i in. 2023). Wasze 81% (osobowy, ok. 1 min na klasę) wobec 66-72% (międzyosobowy) mieści się w tym obrazie. Rozrzut AUC 0,52-0,91 między osobami pokazuje, że **u części ludzi marker alfa po prostu nie działa**, i trzeba to umieć wykryć.
- **Wearable lepiej mierzy zmianę u tej samej osoby niż wartość bezwzględną** (Casanova-Lizón 2026). Shaffer i Ginsberg (2017) zalecają uzupełniać normy własnymi danymi. To argument za osobistą linią bazową HR i RMSSD.
- **EEG jako „nauczyciel” dla taniego czujnika: precedensy.** Fujiwara 2019 walidował detektor HRV względem EEG. Larue i in. 2015 (cytowane w przeglądzie Rivas-Vidal) użyli EEG jako etykiety do klasyfikacji czujności z eye-trackingu (4 klasy, ok. 91%). Chua 2012 porównywał HRV, EEG i PERCLOS w tych samych sesjach. **Nie znalazłem** pracy, która uczy osobisty model wearable z krótkiej osobistej sesji EEG. Pomysł jest więc nowy w tej konkretnej formie, ale nieprzetestowany. Ryzyko: jeśli EEG i HRV korelują słabo minuta do minuty (u was |r| ≤ 0,16), etykiety z EEG mogą słabo przenosić się na HRV.

## 5. Skale czasu i model „rezerwy czujności”

- **Proces S i proces C.** Model dwuprocesowy: homeostatyczny proces S oddziałuje z okołodobowym procesem C i przewiduje czas oraz intensywność snu (Borbély i in. 2016, reappraisal). Model trzyprocesowy łączy składową okołodobową z homeostatyczną (czas od przebudzenia, ilość snu) i przewiduje czujność w skali 1-16 oraz wykonanie zadań monotonnych. Wskazuje też progi ryzyka (Åkerstedt i Folkard 1997). Rozszerzenie modelu: fazę procesu C można przyjąć jako ustawioną godziną przebudzenia. Wykryto też efekt czasu na zmianie: czujność spada w trakcie zmiany i na końcu lekko się podnosi (Folkard i in. 1999).
- **Czas zadania.** Deprywacja snu nasila spadek wykonania w trakcie pojedynczej sesji PVT i daje więcej lapsów (>500 ms) (Lim i Dinges 2008).
- **Pomiar behawioralny.** W 10-minutowym PVT najczulsze na brak snu są lapsy i szybkość odpowiedzi (1/RT). Wielkości efektu wynoszą 1,59-1,94 przy całkowitej deprywacji i 0,88-1,21 przy częściowej. **Średni i medianowy RT** autorzy odradzają jako miarę główną (Basner i Dinges 2011). 3-minutowy PVT-B ma średnio o 22,7% mniejsze efekty, ale nadal średnie do dużych, przy progu lapsu 355 ms (Basner i in. 2011). KSS jest zwalidowany względem EEG i PVT (Kaida 2006).
- **Dowód empiryczny, że kontekst się liczy.** Dodanie czasu jazdy i pory dnia podniosło AUC z 0,76 do 0,88 (Lu 2022).
- *Implikacja:* „rezerwa” powinna mieć część a priori (sen, godzina przebudzenia, pora dnia, czas zadania) i część mierzoną (sygnały osoby). Bez części a priori model porównuje się z bazą, którą sama pora dnia mogłaby pobić.

## 6. Co możemy, a czego nie możemy twierdzić w pitchu

**Możemy uczciwie powiedzieć:**
1. Alfa potyliczna to najlepiej udokumentowany marker EEG senności i stanu oczu. Na naszym sprzęcie działa (zamknięcie oczu wykryte u 4/4 osób). Zaznaczamy, że to test sygnału, nie detekcja senności.
2. Na publicznym zbiorze z jazdy marker alfa rozróżnia stany ze średnim AUC 0,75 na osobę, ale z rozrzutem 0,52-0,91. To zgodne z literaturą dla modeli bez kalibracji (ok. 76%).
3. Ludzie różnią się podatnością na zmęczenie w sposób stabilny (Van Dongen 2004), a nasz model osobowy (ok. 1 min danych na klasę) dał ok. 81% wobec 66-72% dla modelu ogólnego. Personalizacja ma więc sens.
4. Tętno i HRV niosą informację o czujności (Chua 2012; Lu 2022). U nas RMSSD korelowało z czasem reakcji ujemnie u 16/16 osób, choć słabo (r = −0,23).
5. Tanie wearables dobrze mierzą HR i trendy u tej samej osoby, słabiej wartości bezwzględne HRV i źle w ruchu. Dlatego chcemy osobistej linii bazowej, a nie progów populacyjnych.
6. Fuzja sygnałów w laboratorium zwykle poprawia wynik, a kontekst (pora dnia, czas zadania) wyraźnie pomaga.

**Nie wolno nam twierdzić:**
1. Że zegarek „wykrywa senność” albo „mierzy czujność”. Najlepsze uczciwe wyniki z samego wearable to AUC 0,76 (opaska piersiowa) i ok. 55-73% przy LOSO (nadgarstek).
2. Że EEG i HRV „mówią to samo”. U nas korelacja minuta do minuty |r| ≤ 0,16, a literatura pokazuje rozbieżne sygnatury.
3. Że wykrycie zamkniętych oczu to wykrycie senności.
4. Że LF/HF mierzy „balans współczulny” albo „stres”, ani niczego o wykrywaniu stresu, wypalenia czy przeciążenia poznawczego.
5. Że mamy trafność >90%. Takie liczby w literaturze to zwykle walidacja wewnątrzosobowa z losowym podziałem okien (np. Kundinger: 92% → ok. 60% przy LOSO).
6. Że kalibracja EEG → wearable jest udowodniona. To hipoteza bez bezpośredniego precedensu.
7. Że theta czołowa lub (theta+alfa)/beta działają na naszym sprzęcie. Nasze dane temu przeczą (referencja Fp1, artefakty EMG).
8. Że wzrost HR w 10-minutowym PVT to oznaka zmęczenia. Literatura wiąże senność raczej ze spadkiem HR.

---

## Tabela źródeł

| # | Autorzy | Rok | Czasopismo / konferencja | DOI / PMID | Co pokazuje | Status |
|---|---|---|---|---|---|---|
| 1 | Fujiwara K i in. | 2019 | IEEE Trans Biomed Eng 66(6):1769-78 | 10.1109/TBME.2018.2879346 / 30403616 | HRV (MSPC) a EEG: 12/13 epizodów pre-N1, 1,7 FP/h, n = 34, symulator | VERIFIED: abstract |
| 2 | Persson A i in. | 2019 | EMBC 2019:6537-40 | 10.1109/EMBC.2019.8857229 / 31947339 | HRV, 86 kierowców, realna droga, SVM 3 klasy: 61% | VERIFIED: abstract |
| 3 | Lu K i in. | 2022 | IEEE T-ITS 23(5):4801-10 | 10.1109/TITS.2021.3127944 | Opaska piersiowa, n = 43, realna droga: AUC 0,76 → 0,88 z kontekstem | VERIFIED: abstract |
| 4 | Wu Y i in. | 2023 | Comput Biol Med 167:107590 | 10.1016/j.compbiomed.2023.107590 / 37897962 | Czołowe EEG/EOG + RRI + oddech to najlepsza kombinacja (bez liczb w abstrakcie) | VERIFIED: abstract |
| 5 | Rivas-Vidal M i in. | 2025/2026 | Front Neuroergon 6:1736672 | 10.3389/fnrgo.2025.1736672 / 41696456 | Przegląd 47 badań EEG+ET: fuzja zwykle lepsza, EEG lepsze dla czujności, mało walidacji międzyosobowej | VERIFIED: full text |
| 6 | LaRocco J i in. | 2020 | Front Neuroinform 14:553352 | 10.3389/fninf.2020.553352 / 33178004 | Tanie headsety EEG: 46 badań, trafności 31% do >90%, niespójne definicje | VERIFIED: full text |
| 7 | Chua EC i in. | 2012 | Sleep 35(3):325-34 | 10.5665/sleep.1688 / 22379238 | Moc RR 0,02-0,08 Hz przewiduje lapsy PVT jak EEG i PERCLOS, n = 24, 40 h bez snu | VERIFIED: abstract |
| 8 | Vicente J i in. | 2016 | Med Biol Eng Comput 54(6):927-37 | 10.1007/s11517-015-1448-7 / 26780463 | HRV: czułość 0,59, swoistość 0,98 na minutach jazdy | VERIFIED: abstract |
| 9 | Kundinger T i in. | 2020 | Sensors 20(4):1029 | 10.3390/s20041029 / 32075030 | Nadgarstek E4 a EKG: 92% (zależny od użytkownika, przeciek) wobec 43-73% LOSO | VERIFIED: full text |
| 10 | Borghini G i in. | 2014 | Neurosci Biobehav Rev 44:58-75 | 10.1016/j.neubiorev.2012.10.003 / 23116991 | EEG, EOG i HR w sekwencji obciążenie → zmęczenie → senność; ok. 90% offline, nie online | VERIFIED: abstract |
| 11 | Lal SK, Craig A | 2001 | Biol Psychol 55(3):173-94 | 10.1016/s0301-0511(00)00085-5 / 11240213 | Przegląd: EEG (theta, delta) najbardziej obiecujące | VERIFIED: abstract |
| 12 | Paulo JR i in. | 2021 | IEEE TNSRE 29:905-15 | 10.1109/TNSRE.2021.3079505 / 33979288 | EEG LOSO bez kalibracji: 75,9%, n = 27 | VERIFIED: abstract |
| 13 | Cui J i in. | 2023 | EMBC 2023:1-6 | 10.1109/EMBC40787.2023.10340982 / 38083525 | EEG między zbiorami danych: 76,7-83,3% | VERIFIED: abstract |
| 14 | Barry RJ i in. | 2007 | Clin Neurophysiol 118(12):2765-73 | 10.1016/j.clinph.2007.07.028 / 17911042 | Oczy zamknięte a otwarte: alfa jako wskaźnik pobudzenia, EDA ujemnie z alfa | VERIFIED: abstract |
| 15 | Strijkstra AM i in. | 2003 | Neurosci Lett 340(1):17-20 | 10.1016/s0304-3940(03)00033-8 / 12648748 | Senność: alfa↓ (globalnie), theta↑ (czołowo) | VERIFIED: abstract |
| 16 | Cajochen C i in. | 1995 | Sleep 18(10):890-4 | 10.1093/sleep/18.10.890 / 8746397 | Moc 6,25-9 Hz rośnie z czasem czuwania, n = 9 | VERIFIED: abstract |
| 17 | Torsvall L, Åkerstedt T | 1987 | Electroencephalogr Clin Neurophysiol 66(6):502-11 | 10.1016/0013-4694(87)90096-4 / 2438115 | Maszyniści w nocy: alfa i wolne ruchy oczu↑, efekt u 6/11 | VERIFIED: abstract |
| 18 | Kaida K i in. | 2006 | Clin Neurophysiol 117(7):1574-81 | 10.1016/j.clinph.2006.03.011 / 16679057 | Walidacja KSS względem EEG i PVT, r = 0,56 z lapsami | VERIFIED: abstract |
| 19 | Billman GE | 2013 | Front Physiol 4:26 | 10.3389/fphys.2013.00026 / 23431279 | LF/HF nie mierzy balansu współczulno-przywspółczulnego | VERIFIED: full text |
| 20 | Hu Z i in. | 2026 | Front Physiol 17:1871218 | 10.3389/fphys.2026.1871218 / 42488621 | Rozbieżne sygnatury oko-mózg-serce (aktywne a pasywne zmęczenie), n = 12, eksploracyjne | VERIFIED: abstract |
| 21 | Schäfer A, Vagedes J | 2013 | Int J Cardiol 166(1):15-29 | 10.1016/j.ijcard.2012.03.119 / 22809539 | PRV z PPG dobra w spoczynku, psuje się w ruchu i przy stresorach | VERIFIED: abstract |
| 22 | Georgiou K i in. | 2018 | Folia Med 60(1):7-20 | 10.2478/folmed-2018-0012 / 29668452 | Wearables a HRV: dobrze w spoczynku, gorzej w wysiłku | VERIFIED: abstract |
| 23 | Bent B i in. | 2020 | npj Digit Med 3:18 | 10.1038/s41746-020-0226-6 / 32047863 | Optyczny HR: błąd w aktywności o 30% wyższy | VERIFIED: abstract |
| 24 | Casanova-Lizón A i in. | 2026 | Sensors 26(20):6549 | 10.3390/s26206549 / 42944412 | Garmin Elevate v4: HR r ≥ 0,94, RMSSD LoA do +118% | VERIFIED: abstract |
| 25 | Munoz ML i in. | 2015 | PLoS One 10(9):e0138921 | 10.1371/journal.pone.0138921 / 26414314 | RMSSD z 10-120 s a 5 min: r = 0,85-0,986, n = 3387 | VERIFIED: abstract |
| 26 | Shaffer F, Ginsberg JP | 2017 | Front Public Health 5:258 | 10.3389/fpubh.2017.00258 / 29034226 | Metryki HRV, normy niewymienne między długościami okien | VERIFIED: abstract |
| 27 | Task Force ESC/NASPE | 1996 | Circulation 93(5):1043-65 | PMID 8598068 | Standardy HRV (2-5 min dla cech częstotliwościowych, za Kundingerem) | metadane, treść NOT VERIFIED |
| 28 | Van Dongen HP i in. | 2004 | Sleep 27(3):423-33 | PMID 15164894 | Cechowa, stabilna podatność na brak snu, n = 21 × 3 | VERIFIED: abstract |
| 29 | Borbély AA i in. | 2016 | J Sleep Res 25(2):131-43 | 10.1111/jsr.12371 / 26762182 | Model dwuprocesowy (S + C), reappraisal | VERIFIED: abstract |
| 30 | Åkerstedt T, Folkard S | 1997 | Chronobiol Int 14(2):115-23 | 10.3109/07420529709001149 / 9095372 | Model trzyprocesowy czujności | VERIFIED: abstract |
| 31 | Folkard S i in. | 1999 | J Biol Rhythms 14(6):577-87 | 10.1177/074873099129000911 / 10643755 | Faza ustawiona przez godzinę przebudzenia, efekt czasu na zmianie | VERIFIED: abstract |
| 32 | Lim J, Dinges DF | 2008 | Ann N Y Acad Sci 1129:305-22 | 10.1196/annals.1417.002 / 18591490 | Deprywacja snu nasila spadek w trakcie zadania, lapsy | VERIFIED: abstract |
| 33 | Basner M, Dinges DF | 2011 | Sleep 34(5):581-91 | 10.1093/sleep/34.5.581 / 21532951 | PVT: lapsy i 1/RT zamiast średniego RT; d = 1,59-1,94 | VERIFIED: abstract |
| 34 | Basner M i in. | 2011 | Acta Astronaut 69(11-12):949-59 | 10.1016/j.actaastro.2011.07.015 / 22025811 | PVT-B (3 min) ważny, próg lapsu 355 ms | VERIFIED: abstract |
| 35 | Garmin Connect IQ API | 2026 | dokumentacja producenta | developer.garmin.com/connect-iq/api-docs/Toybox/Sensor/HeartRateData.html | Venu 2 udostępnia odstępy uderzenie-uderzenie | VERIFIED: strona producenta |
| — | Larue i in. | 2015 | (cytowane w #5) | — | EEG jako etykieta dla ET, ok. 91% | NOT VERIFIED (tylko przez przegląd #5) |

**Na slajd (5):** Van Dongen 2004 (#28), Lu 2022 (#3), Persson 2019 (#2), Chua 2012 (#7), Rivas-Vidal 2025 (#5). Alternatywnie Kundinger 2020 (#9), jeśli slajd dotyczy rzetelności walidacji.
