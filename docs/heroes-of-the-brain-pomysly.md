# Heroes of the Brain 2026: pomysły (kategoria Adaptive Systems)

Sprzęt: BrainAccess MINI, 8 suchych elektrod, montaż ze starter packa **F3, F4, C3, C4, P3, P4, O1, O2**, 250 Hz, dane w MNE.

## 1. Wybrany pomysł: Wachta

**Jedno zdanie:** systemy monitoringu wiedzą wszystko o infrastrukturze i nic o człowieku, który na nią patrzy. Wachta dodaje im tę brakującą metrykę.

**Co to jest.** Warstwa adaptacyjna dla systemów monitoringu i dyżurów. Mierzy stan poznawczy operatora przez EEG i na tej podstawie zmienia sposób, w jaki istniejący dashboard pokazuje i kieruje alarmy.

**Problem.** Operatorzy pracujący na zmiany (bezpieczeństwo IT, energetyka, transport, przemysł) dostają ten sam strumień alarmów niezależnie od tego, czy są wypoczęci, przeciążeni, czy przysypiają. Zmęczony operator potwierdza alarmy bez czytania, a przeciążony gubi ten krytyczny.

**Rozwiązanie: trzy stany, trzy zachowania**

| Stan operatora | Sygnał | Co robi system |
|---|---|---|
| Skupiony | bazowy | pełny widok, bez zmian |
| Przeciążony | theta F3/F4 w górę, alfa P3/P4 w dół | ekran zwija się do jednego alarmu i jednego zdania od LLM |
| Senny | alfa O1/O2 w górę, wolne mrugnięcia | potwierdzenie wymaga aktywnej czynności, alarm krytyczny idzie równolegle do drugiej osoby |
| Cała zmiana | wskaźniki wszystkich | panel kierownika: kto może przejąć incydent |

Dodatek: potwierdzanie alarmu zaciśnięciem szczęki, gdy ręce są zajęte.

**Dlaczego to adaptive system.** Użytkownik niczym nie steruje. Oprogramowanie samo zmienia zachowanie na podstawie sygnału biologicznego, w czasie rzeczywistym i w zamkniętej pętli (pasywne BCI).

**Integracja.** Wtyczka do Grafany i reguły kierowania alarmów w systemach dyżurowych typu PagerDuty. Stan operatora jest zwykłą metryką, jak obciążenie procesora. Rozszerzamy narzędzia, nie zastępujemy ich.

**Technologia.** 60 s kalibracji na osobę (oczy otwarte / zamknięte), moc pasm w oknach 2 s z wygładzaniem, z-score względem bazy. Senność to sygnał solidny. Przeciążenie jest mniej stabilne i wymaga dalszej walidacji.

**Model biznesowy.** Licencja miesięczna za stanowisko operatorskie, sprzęt osobno. Rynek wejścia: branże, w których operatorzy już noszą sprzęt na głowie, a błąd jest kosztowny.

**Prywatność.** Surowe EEG nie opuszcza stanowiska. Na zewnątrz wychodzi tylko trzystanowy wskaźnik, a operator widzi to samo co przełożony.

**Ryzyka.** Jakość sygnału na suchych elektrodach przy ruchu, akceptacja czapki przez operatorów, wymogi prawne dotyczące danych biometrycznych pracowników.

**Następny krok po hackathonie.** Pilotaż na jednej zmianie u jednego klienta z pomiarem czasu reakcji na alarm krytyczny przed i po.

### Demo
1. Strona udająca dashboard z płynącymi alarmami (HTML + websocket).
2. Skrypt w Pythonie: strumień z `brainaccess`, kalibracja, moc pasm, wskaźnik stanu.
3. Scena: juror zakłada czapkę i zamyka oczy na 5 s, alarm przechodzi na telefon kolegi z drużyny. Potem zalew alarmów i ekran zwija się do jednego zdania.
4. Ukryty klawisz awaryjny na wypadek słabego sygnału.

### Szkielet PDF (10 slajdów)
1. Tytuł i jedno zdanie
2. Problem: operator o 3:00
3. Luka: narzędzia nie widzą człowieka
4. Rozwiązanie: trzy stany, trzy zachowania
5. Jak to działa (sygnał → wskaźnik → dashboard)
6. Integracje
7. Demo: zrzuty ekranu
8. Rynek i model biznesowy (liczby do uzupełnienia ze źródłami)
9. Prywatność
10. Zespół i co dalej

## 2. Co da się wyczytać z tego sprzętu

| Sygnał | Co oznacza | Elektrody | Wiarygodność w 24 h |
|---|---|---|---|
| Alfa 8–12 Hz | relaks, zamknięte oczy, odpłynięcie, senność | O1, O2, P3, P4 | wysoka |
| Mrugnięcia | częstość i długość rosną ze zmęczeniem | F3, F4 (słabiej niż na czole) | wysoka |
| Zaciśnięcie szczęki | napięcie, jawny „przycisk” | wszystkie | wysoka |
| Theta czołowa 4–7 Hz | obciążenie poznawcze | F3, F4 | średnia, po kalibracji |
| Zaangażowanie β/(α+θ) | uwaga vs nuda | F, C, P | średnia, tylko trend |
| Asymetria alfa F3/F4 | „walencja” emocji | F3, F4 | niska, unikać |
| Wyobrażenie ruchu (mu) | sterowanie | C3, C4 | niska, unikać |

## 3. Plany zapasowe

- **Plan B, najmniejsze ryzyko:** telewizor lub wykład, który pauzuje i cofa się, gdy odpłyniesz (pomysły 61 i 1). Opiera się wyłącznie na alfie.
- **Plan C, na show:** detektor mikrosnów kierowcy na symulatorze jazdy (41).
- **Alternatywa AI:** „AI, które wie, kiedy przestałeś nadążać” (81 + 82 + 83).

## 4. Pełna lista 100 pomysłów

Pogrubione to te najbardziej wykonalne w dobę.

### Nauka
1. **Wykład wideo, który sam się pauzuje i cofa o 20 s, gdy odpłyniesz.**
2. Fiszki, które wracają do kart, przy których mózg się męczył, a nie do tych, które źle kliknąłeś.
3. Czytnik oznaczający akapity „przeczytane oczami, nie mózgiem”.
4. Tutor LLM, który przełącza poziom wyjaśnień pod obciążenie.
5. Egzamin próbny z raportem „tu wiedziałeś, tu zgadywałeś”.
6. Kurs języka: nowe słówka tylko w oknach wysokiej uwagi, powtórki w dołkach.
7. Transkrypt spotkania z podświetlonymi fragmentami, przy których się wyłączyłeś.
8. Generator zadań z matmy trzymający cię między nudą a paniką.
9. Szybkie czytanie słowo po słowie, z tempem sterowanym uwagą.
10. Dzienny wykres „ile godzin faktycznie byłem obecny”.

### Programowanie
11. **LLM pair programmer, który milczy, dopóki nie utkniesz na dłużej niż 30 s.**
12. **Terminal, który blokuje deploy na produkcję, gdy jesteś zmęczony.**
13. Heatmapa repo: które pliki najbardziej bolą mózg.
14. Slack przepuszczający powiadomienia tylko wtedy, gdy nie jesteś w flow.
15. Dokumentacja, która zwija się i rozwija pod obciążenie.
16. Debugger proponujący przerwę po wykryciu pętli frustracji.
17. Test A/B czytelności kodu: mózg wskazuje łatwiejszą wersję.
18. Metadane w commicie: „napisane o 3:00 przy 20% uwagi”.
19. Code review z najtrudniejszymi plikami w szczycie uwagi.
20. Onboarding do cudzego kodu: ścieżka po plikach dobierana po obciążeniu.

### Gry
21. **Skradanka, w której strażnicy „słyszą” twój mózg.**
22. Snajper, któremu celownik stabilizuje się ze spokojem.
23. Labirynt, którego mapa odsłania się po 2 s zamkniętych oczu.
24. Tower defense: wieże biją mocniej, im bardziej się skupiasz.
25. Gra rytmiczna, w której tempo to twoja uwaga.
26. Speedrun medytacji.
27. Tamagotchi, które zdycha, gdy nie odpoczywasz.
28. Roguelike z poziomami generowanymi z EEG.
29. Mistrz gry LLM zmieniający tempo narracji pod zaangażowanie.
30. Wyścig ślimaków: wygrywa najspokojniejszy.

### Muzyka, media, sztuka
31. **Podcast, który sam przyspiesza do 2x na nudnych fragmentach.**
32. Trailer-o-metr: wykres uwagi sekunda po sekundzie.
33. Playlista ucząca się, co wprowadza w flow akurat ciebie.
34. Instrument: alfa to filtr, szczęka to stopa, mrugnięcie to werbel.
35. DJ set, w którym drop wchodzi na szczycie napięcia.
36. Film, którego montaż wybiera wątek ożywiający widza.
37. Obraz generowany z całej doby hackathonu.
38. Obraz w galerii, który zmienia się, gdy przestajesz patrzeć uważnie.
39. Książka z rozgałęzieniami wybieranymi nieświadomie.
40. Suchar-o-metr: reakcja na żart mierzona napięciem mięśni twarzy.

### Zdrowie i sen
41. **Detektor mikrosnów dla kierowcy na symulatorze jazdy.**
42. **Trener bruksizmu: liczy zaciskanie szczęki przy pracy.**
43. Budzik do drzemki, który budzi przed głębokim snem.
44. Budzik poranny, który wyłącza się, gdy mózg naprawdę wstał.
45. Trener oddechu z tempem dopasowanym do alfy.
46. Przerwa na oczy wyzwalana częstością mrugnięć.
47. Automatyczny chronotyp.
48. Kofeinometr.
49. Trening wystąpień: publiczność trudniejsza, gdy jesteś spokojny.
50. Bajka, która gra dalej tylko wtedy, gdy dziecko słucha.

### Praca
51. **Edytor, który ukrywa wszystko poza bieżącym zdaniem, gdy się rozpraszasz.**
52. Kalendarz układający zadania pod krzywą energii.
53. Skrzynka: trudne maile w szczytach, śmieciowe w dołkach.
54. Status „w flow, nie przeszkadzać” ustawiany sam.
55. Prezenter z podpowiedzią „tracisz ich”.
56. Dashboard BI, który upraszcza wykresy przy przeciążeniu.
57. Symulator negocjacji: klient-LLM naciska mocniej, gdy jesteś spokojny.
58. Próbna rozmowa rekrutacyjna z raportem stresu per pytanie.
59. Burza mózgów: LLM podrzuca bodziec przy zastoju.
60. Lampka na biurku jako znak dla współpracowników.

### Dom i otoczenie
61. **Telewizor, który pauzuje, gdy zaśniesz, i pamięta, gdzie skończyłeś.**
62. Telefon przechodzący w szarość przy bezmyślnym przewijaniu.
63. Przepis czytany na głos: kolejny krok, gdy „wróciłeś”.
64. Głośnik, który milknie, gdy myślisz.
65. Radio w aucie ściszające się przy trudnym manewrze.
66. Wirtualne okno z pogodą zależną od stanu.
67. Biurko, które każe wstać w dołku energii.
68. Zwierzak na biurku odzwierciedlający twój stan.
69. Tabliczka e-ink na drzwiach.
70. Ekspres, który wydaje kawę tylko naprawdę zmęczonym.

### Dwie osoby i publiczność
71. **Dashboard drużyny: kto ma iść spać, a kto kodować.**
72. Gra kooperacyjna: statek leci, gdy oboje jesteście skupieni.
73. Przeciąganie liny alfą 1 na 1.
74. Nauczyciel widzi na żywo, czy uczeń nadąża.
75. Nakładka dla streamera ze stanem mózgu.
76. Szachy z paskiem obciążenia przeciwnika.
77. Hamulec kłótni.
78. Sygnał przeciążenia dla opiekuna osoby niemówiącej.
79. Wizualizacje koncertu z mózgu artysty.
80. Publiczność głosuje na pitch uwagą.

### AI × mózg
81. **Chatbot, który wie, że przestałeś czytać.**
82. **Agent kodujący, który zwalnia, gdy nie nadążasz z czytaniem zmian.**
83. **Agent, który pyta o zgodę tylko wtedy, gdy możesz jej świadomie udzielić.**
84. Streszczenie o długości proporcjonalnej do pozostałej uwagi.
85. Głos AI z tempem dopasowanym do stanu.
86. Ocena odpowiedzi modelu reakcją mózgu zamiast kciuka.
87. Generator obrazów iterujący w stronę tego, co cię ożywia.
88. Zapora poznawcza przed „kup teraz”.
89. Zapis kontekstu w chwili utraty wątku.
90. Asystent, który pomaga mniej, gdy dajesz radę sam.

### Odjechane
91. **„Wrapped” twojego mózgu z 24 h hackathonu.**
92. Czapka-juror: ranking prezentacji według uwagi widza.
93. Gra, którą wygrywa się zasypiając.
94. Ekran, który znika, gdy patrzysz bez myślenia.
95. Paywall płacony uwagą.
96. Adblock wycinający reklamy, które porywają uwagę.
97. Budzik na nudny wykład, który wibruje u sąsiada.
98. Sklep blokujący zakup pod wpływem emocji.
99. Slajdy przebudowujące się pod uwagę jurora.
100. Horror, który straszy, gdy się rozluźnisz.
