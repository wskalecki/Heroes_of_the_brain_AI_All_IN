# Trafność pipeline'u na nagraniach zespołu

Stan na 14.11.2026. To wynik skryptu `experiments/validate-on-recordings.py` na czterech nagraniach z `data/recordings/`.

## Co sprawdzamy

- Nagranie przechodzi od początku do końca przez ten sam kod, który liczy wskaźnik w demo:
  filtr przyczynowy 1–40 Hz, okna 2 s co 1 s, kalibracja z pierwszych 60 czystych okien.
- „Spadek czujności” to wyrazistość alfy na O1/O2 powyżej 2,5 odchylenia od własnej kalibracji przez co najmniej 3 s.
- Punktem odniesienia jest blok `eyes_closed` z adnotacji protokołu. Dobrowolne zamknięcie oczu zastępuje tu prawdziwy mikrosen.

## Wynik

| Osoba | Okna odrzucone | Oczy zamknięte wykryte | Opóźnienie | Pokrycie bloku | Fałszywe alarmy | Czas w fałszywym alarmie | AUC |
|---|---|---|---|---|---|---|---|
| adi | 10,1% | tak | 12 s | 69% | 0 w 7,0 min | 0,0% | 0,93 |
| filip | 3,2% | tak | 8 s | 90% | 1 w 12,6 min | 0,8% | 0,97 |
| rudy | 15,3% | tak | 7 s | 92% | 0 w 5,8 min | 0,0% | 0,99 |
| wojtek | 10,8% | tak | 13 s | 74% | 0 w 6,3 min | 1,3% | 0,89 |

Razem: wykryto 4 z 4 bloków, 1 fałszywy alarm w 32 min poza blokiem (po kalibracji).

![Wskaźnik czujności w czasie dla czterech nagrań](img/trafnosc-na-nagraniach.png)

Kolumny:

- **Okna odrzucone:** odsetek okien 2 s z amplitudą powyżej 300 µV (ruch, mięśnie).
- **Opóźnienie:** od początku bloku według ręcznie spisanego timeline'u do zgłoszenia spadku.
- **Pokrycie bloku:** odsetek okien bloku `eyes_closed`, w których stan to „spadek czujności”.
- **Fałszywe alarmy:** spadki zgłoszone poza blokiem `eyes_closed`, po zakończeniu kalibracji.
- **AUC:** jak dobrze sam wskaźnik (bez progu) oddziela okna z bloku `eyes_closed` od pozostałych; 0,5 to los, 1,0 to ideał.

## Jak czytać te liczby

- **To sprawdzenie mechanizmu, nie statystyka.** Cztery osoby, po jednym bloku na osobę.
- **Próg 2,5 dobraliśmy na tych samych nagraniach**, więc wynik jest optymistyczny. Przy progu 2,0 było 6 fałszywych alarmów
  zamiast jednego. Na nowych nagraniach z punktów pomiarowych trzeba to sprawdzić ponownie.
- **Opóźnienie zawiera niedokładność timeline'u.** Od chwili, gdy alfa po raz pierwszy przekracza próg w dwóch kolejnych
  oknach, do zgłoszenia mijają 4 s u każdej z czterech osób. Z tego 3 s to wymagane utrzymanie sygnału.
- **Zamknięte oczy to nie senność.** Alfa przy zamkniętych oczach jest najsilniejszym sygnałem, jaki ten sprzęt widzi.
  Prawdziwa senność daje słabsze zmiany. To uzupełni wykres z danych publicznych (zadanie B2).
- **Wskaźnik wolny i rezerwa nie są tu sprawdzane.** Ich parametry są założeniami.

## Stan oczu i próby reakcji (zadania A7, A8)

Kamera w aucie sprawdza, czy oczy są zamknięte. Żeby odróżnić to od senności przy otwartych oczach, pipeline liczy
mrugnięcia na F3/F4 (przy referencji Fp1 mrugnięcie to krótkie, duże wychylenie). Spadek czujności bez mrugnięć jest
oznaczany jako „oczy zamknięte”, a spadek przy mrugających oczach jako „senność przy otwartych oczach”.

Mrugnięcia na minutę w blokach protokołu (detektor z `src/wachta/blinks.py`, próg z pierwszych 20 s nagrania):

| Osoba | Rozmowa | Oczy zamknięte | Czytanie | Liczenie |
|---|---|---|---|---|
| adi | 4,2 | 0,0 | 9,6 | 12,9 |
| filip | 19,6 | 1,0 | 3,0 | 0,0 |
| rudy | 13,6 | 0,0 | 8,0 | 31,6 |
| wojtek | 13,0 | 12,4 | 1,0 | 0,0 |

| Osoba | Spadek w bloku oznaczony jako „oczy zamknięte” | Próba reakcji przed alarmem w bloku | Próby reakcji poza blokiem |
|---|---|---|---|
| adi | 100% okien | tak | 0,0 na 10 min |
| filip | 100% okien | tak | 3,2 na 10 min |
| rudy | 100% okien | tak | 1,7 na 10 min |
| wojtek | 43% okien | tak | 8,0 na 10 min |

Jak to czytać:

- **U trzech osób blok zamkniętych oczu jest prawie bez mrugnięć i cały oznaczony poprawnie.** U Wojtka detektor widzi serię
  wychyleń w 37.–41. s bloku i przy jego końcu. W tym samym miejscu spada jego alfa, więc to najpewniej krótkie otwarcie oczu,
  a nie błąd detektora. Bez nagrania wideo nie da się tego rozstrzygnąć.
- **Przy czytaniu i liczeniu ludzie mrugają rzadko** (u Filipa i Wojtka 0–3 razy na minutę). Same mrugnięcia nie wystarczą więc
  do oceny stanu oczu. Liczą się tylko razem ze wzrostem alfy.
- **Senności przy otwartych oczach nie da się tu sprawdzić**, bo nikt w tych nagraniach nie był senny. Dowody na nią pochodzą
  z danych publicznych (notebooki 04 i 05) i literatury (`podstawy-naukowe.md`). Własne dane mają dać nocne punkty pomiarowe (C4).
- **Próba reakcji pojawia się przed alarmem u wszystkich czterech osób**, czyli gdy wskaźnik dopiero rośnie. Ceną są próby poza
  blokiem: od 0 do 8 na 10 minut, najwięcej przy najbardziej zaszumionym sygnale (Wojtek). Wyższy próg próby (1,8 lub 2,0
  zamiast 1,5) zmniejsza ich liczbę, ale u Wojtka próba przestaje wyprzedzać alarm. Ustawienie do dostrojenia na większej
  liczbie nagrań.
- Czasu reakcji nie da się sprawdzić na nagraniach: próba wymaga człowieka przed ekranem.

## Jak odtworzyć

```bash
pip install -e ".[analysis]"
```

```bash
python experiments/validate-on-recordings.py --figure docs/img/trafnosc-na-nagraniach.png
```
