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

## Jak odtworzyć

```bash
pip install -e ".[analysis]"
```

```bash
python experiments/validate-on-recordings.py --figure docs/img/trafnosc-na-nagraniach.png
```
