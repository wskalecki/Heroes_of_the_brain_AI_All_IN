# Rynek: firmy od wearables EEG i neuroadaptacji (stan na listopad 2026)

Research pod Heroes of the Brain, kategoria Adaptive Systems. Cel: wiedzieć, kto już robi coś podobnego do Wachty i do pomysłu „AI oddaje ster człowiekowi”, żeby pitch nie trafił w zajęte miejsce.

## Mapa w jednym zdaniu

Sprzęt EEG do noszenia jest już produktem konsumenckim (opaski, słuchawki, pchełki), a „stan mózgu jako API dla aplikacji” też istnieje. **Nikt z poniższych nie sprzedaje integracji stanu operatora z narzędziami do monitoringu i obsługi incydentów (Grafana, PagerDuty) ani logiki „kiedy agent AI eskaluje do człowieka”.** To jest wasza luka.

---

## 1. Bezpieczeństwo i zmęczenie w przemyśle

### SmartCap (Australia), najbliższy konkurent Wachty w wersji „senność”
- **Co robi:** opaska LifeBand z czujnikami EEG wkładana do czapki, kasku albo noszona osobno. Liczy poziom czujności algorytmem „Universal Fatigue Algorithm” (sieci neuronowe na pasmach delta, theta, alfa, beta) i ostrzega operatora w czasie rzeczywistym.
- **Dla kogo:** kierowcy ciężarówek i operatorzy maszyn w kopalniach (Rio Tinto, Anglo American, Newcrest), potem budownictwo i transport.
- **Panel dla firmy:** LifeHub w chmurze, wysyła SMS-y i maile do przełożonych.
- **Wniosek dla nas:** wykrywanie senności operatora z EEG jest rozwiązane komercyjnie. SmartCap tylko alarmuje człowieka; nie zmienia zachowania oprogramowania.
- Źródła: [Mining3: SmartCap](https://mining3.com/?p=315) · [Rio Tinto case study](https://bestpractice.ai/ai-use-cases/case-studies/55261637-5e3d-44de-b1a2-8f992fc248aa) · [CRCA: Putting a cap on mining fatigue](https://crca.asn.au/putting-a-cap-on-mining-fatigue) · [Construction Dive](https://constructiondive.com/news/smartcap-tracks-brain-waves-to-keep-workers-awake-on-the-job/427999)

---

## 2. Neuroadaptacja interfejsów i AI (najbliżej waszej kategorii)

### Zander Labs (Niemcy / Holandia), najważniejszy punkt odniesienia naukowego
- **Co robi:** pasywne BCI, czyli system sam odczytuje stan użytkownika bez świadomych komend. Projekt NAFAS („Neuroadaptivity for Autonomous Systems”) za 29,85 mln euro, finansowany przez niemiecką Cyberagentur, 48 miesięcy, koniec planowany na listopad 2027.
- **Stan:** w styczniu 2026 pokazali pierwszy zintegrowany pasywny BCI, który wykrywa obciążenie poznawcze z EEG i dostosowuje interfejs. Mają własny plaster z elektrodami (Zypher).
- **Pozycjonowanie:** stan poznawczy człowieka jako nowe źródło danych do trenowania AI.
- **Wniosek dla nas:** to dokładnie wasza kategoria, ale na poziomie badań i obronności. Cytujcie ich w pitchu jako dowód, że kierunek jest poważny („Niemcy wydają na to 30 mln euro”), a siebie pozycjonujcie jako zastosowanie w konkretnym narzędziu.
- Źródła: [Cyberagentur: program BCI](https://www.cyberagentur.de/en/?p=3058) · [Fraunhofer IDMT: Mobile EEG for neuroadaptive systems](https://www.idmt.fraunhofer.de/en/Press_and_Media/press_releases/2026/Mobile-EEG-for-neuroadaptive-systems.html) · [BTU: 30 mln euro dla Zander Labs](https://www.b-tu.de/en/news/article/25419-30-millionen-euro-groesste-forschungsfinanzierung-in-europa-an-cottbuser-startup) · [BTU: A cartoon vision became research](https://www.b-tu.de/en/research/news/detail/31258-a-cartoon-vision-became-research)

### Arctop (USA / Izrael), oprogramowanie zamiast sprzętu
- **Co robi:** platforma Neuos, „warstwa inteligencji” między dowolnym sprzętem EEG (słuchawki, opaski, gogle VR) a aplikacjami. Udostępnia w czasie rzeczywistym skupienie, zadowolenie, obciążenie poznawcze, uwagę wzrokową i słuchową. Licencjonuje API i SDK firmom.
- **Klienci:** rozrywka i media (analityka reakcji widzów), sektor publiczny i wojsko (kontrakt z US Air Force Academy na adaptacyjne symulatory szkoleniowe), szkolenia chirurgiczne ze Stanford Medicine.
- **Finanse:** Series A 10 mln USD (2023), ok. 14 mln USD łącznie, ok. 15 osób.
- **Wniosek dla nas:** to najbliższy model biznesowy do waszego („ulepszamy istniejące narzędzia”), ale sprzedają platformę ogólną. Wasza przewaga to konkretna integracja pod jeden rynek.
- Źródła: [Carahsoft: Arctop dla sektora publicznego](https://carahsoft.com/arctop) · [Pulse 2.0: Series A](https://pulse2.com/arctop-10-million-funding/amp/) · [Wywiad z CEO (newsletter neurotech)](https://theneurotechnewsletter.substack.com/p/arctop-and-the-intelligence-layer) · [Profil YesPress](https://yespress.io/arctop)

### Neurosity (USA), EEG z integracją z asystentami AI
- **Co robi:** opaska Crown, 8 kanałów, 256 Hz, przetwarzanie na urządzeniu. Otwarte SDK w JavaScripcie i Pythonie, wyniki skupienia i spokoju jako strumienie danych, surowe EEG, obsługa LSL i BrainFlow.
- **Kluczowe dla nas:** od września 2025 mają serwer MCP, który podłącza dane z Crown do Claude'a i ChatGPT. Istnieją też otwarte projekty MCP dla innych opasek (bci-mcp, neuro-cube).
- **Cena:** 1 499 USD.
- **Wniosek dla nas:** „AI zna twój stan mózgu” już istnieje. Ale u nich to tryb pytania („jaki mam poziom skupienia?”). Nikt nie robi tak, żeby agent sam decydował o eskalacji i formie komunikatu na podstawie stanu człowieka.
- Źródła: [Neurosity MCP](https://neurosity.co/blog/introducing-the-neurosity-mcp) · [Co budują deweloperzy z SDK](https://neurosity.co/guides/best-developer-use-cases-neurosity-sdk) · [bci-mcp (open source)](https://pypi.org/project/bci-mcp/)

---

## 3. Słuchawki i pchełki z EEG (sprzęt konsumencki i firmowy)

### Neurable (USA), słuchawki MW75 Neuro z Master & Dynamic
- **Co robi:** słuchawki z redukcją szumów i suchymi, materiałowymi czujnikami EEG w nausznikach (12 kanałów). AI wykrywa skupienie i zmęczenie, a aplikacja proponuje przerwy („Brain Breaks”). Przetwarzanie na urządzeniu, ok. 10 h pracy z EEG.
- **Ceny:** start 699 USD; nowa wersja MW75 Neuro LT za 499 USD, wysyłka w 2026, tylko USA i Kanada.
- **Wniosek dla nas:** pomiar skupienia przy pracy umysłowej jest produktem konsumenckim. Dobry argument „sprzęt jest już na głowach ludzi”.
- Źródła: [Engadget](https://www.engadget.com/audio/headphones/neurables-brainwave-tracking-master--dynamic-headphones-tell-you-when-to-take-a-break-120004736.html) · [Neurable: MW75 Neuro LT](https://www.neurable.com/products/longevity) · [Neurable FAQ](https://neurable.com/faq)

### Emotiv (USA / Australia), pchełki MN8 dla firm
- **Co robi:** bezprzewodowe pchełki z 2 kanałami EEG w uchu. Mierzą stres i uwagę w miejscu pracy, sprzedawane jako rozwiązanie firmowe (bezpieczeństwo, wellness, produktywność). Współpraca z SAP i JLL. Poza tym gogle i czepki badawcze EPOC X, Insight, Flex.
- **Etyka:** Emotiv twierdzi, że klienci podpisują zobowiązanie, że nie będą awansować, karać ani zwalniać ludzi na podstawie danych z mózgu.
- **Wniosek dla nas:** temat „pracodawca czyta mózg pracownika” jest już publicznie dyskutowany (artykuł Vice). Wasz slajd o prywatności musi mieć konkretne zabezpieczenia.
- Źródła: [Emotiv: MN8 dla firm](https://www.medical-xprt.com/products/enterprise-neurotechnology-bluetooth-stereo-headset-757654) · [Emotiv: wellness w pracy](https://www.emotiv.com/blogs/news/workplace-wellness-using-eeg-technology) · [Vice: Emotiv i szefowie](https://vice.com/en/article/this-company-wants-to-help-your-boss-monitor-your-brainwaves-at-work)

### IDUN Technologies (Szwajcaria), EEG w uchu jako platforma
- **Co robi:** Guardian 4 to czwarta generacja pchełek z EEG (po 2 kanały na ucho, suche elektrody Dryode). Warstwy oprogramowania: przetwarzanie na urządzeniu, wyniki stanu poznawczego, łączenie z kontekstem. Współpraca z Analog Devices (CES 2025).
- **Wymieniane zastosowania:** asystenci AI dopasowani do poziomu uwagi, dźwięk neuroadaptacyjny, narzędzia produktywności świadome zmęczenia.
- Źródło: [audioXpress: IDUN Guardian 4](https://audioxpress.com/article/idun-technologies-from-concept-to-real-world-brain-sensing-platform)

### Naqi Logix (Kanada) + Wisear (Francja)
- **Co robi:** pchełki odczytujące sygnały bioelektryczne z ucha i mikrogesty twarzy jako sterowanie bez rąk, głosu i ekranu. W styczniu 2026 Naqi przejęło paryski Wisear.
- **Wniosek dla nas:** to raczej sterowanie (kategoria „hands-free”) niż adaptacja, ale pokazuje konsolidację rynku.
- Źródła: [Wearable Technologies](https://wearable-technologies.com/news/naqi-logix-acquires-neurotech-startup-wisear) · [Techcouver](https://techcouver.com/2026/02/12/naqi-logix-acquires-paris-neurotech-startup/)

---

## 4. Sen, medytacja, zdrowie mózgu

### Muse / Interaxon (Kanada)
- **Co robi:** opaski EEG do medytacji i snu. Muse S Athena łączy EEG, fNIRS i SpO2. Funkcje AI do snu: stymulacja głębokiego snu, inteligentny budzik, „wiek mózgu”. Wchodzą do badań klinicznych (Cumulus Neuroscience).
- **Ważne i świeże:** Science ujawniło (4 listopada 2026), że Interaxon wytrenował model fundamentowy mózgu na ok. 50 000 h EEG użytkowników, a polityka prywatności mówiła o tym niejasno, dopóki magazyn nie zapytał.
- **Wniosek dla nas:** świeży, konkretny przykład na slajd o prywatności: „dlatego surowe EEG nie opuszcza stanowiska”.
- Źródła: [Technobezz: Muse i 50 000 h EEG](https://www.technobezz.com/news/muse-sleep-headband-brainwave-data-ai) · [FourWeekMBA](https://fourweekmba.com/ai-muse-headband-maker-says-it-trained-ai-on-50000-eeg-hours/) · [Muse Brain Age](https://insider.fitt.co/press-release/your-body-has-an-age-now-your-brain-does-too/) · [Cumulus i Muse](https://www.mobihealthnews.com/news/cumulus-neuroscience-muse-add-home-sleep-eeg-cns-trial-platform)

---

## 5. Sprzęt badawczy i neuromarketing

### Bitbrain (Hiszpania)
- **Co robi:** suche opaski EEG Diadem (12 kanałów: Fp1, Fp2, AF7, AF8, F3, F4, P3, P4, PO7, PO8, O1, O2; 256 Hz) i Hero, tekstylne Ikon, pierścień do GSR i tętna. Do tego badania neuromarketingowe na zlecenie i współpraca z Noldus.
- Źródła: [Bitbrain: produkty](https://www.bitbrain.com/neurotechnology-products) · [Diadem](https://www.bitbrain.com/equipment/products/diadem)

### Neurotechnology / BrainAccess (Litwa), wasz sprzęt i sponsor
- **Co robi:** suche czapki i opaski (HALO 4 kanały, MINI 8, MIDI 16, MAXI 32), SDK w C, Pythonie i Kotlinie, LSL, hyperscanning. Pozycjonowane na badania, BCI i neuromarketing.
- **Wniosek dla nas:** w pitchu pokażcie, że wasz produkt daje BrainAccess nowy rynek (firmowe zastosowanie operatorskie), a nie konkuruje z nim.
- Źródło: [Neurotechnology: BrainAccess](https://neurotechnology.com/brainaccess.html)

---

## Tabela porównawcza

| Firma | Sprzęt | Główny stan | Zmienia oprogramowanie? | Rynek |
|---|---|---|---|---|
| SmartCap | opaska w czapce | senność | nie, alarmuje człowieka i przełożonego | kopalnie, transport |
| Zander Labs | plaster z elektrodami | obciążenie, zrozumienie, zaskoczenie | tak, ale na etapie badań | obronność, AI |
| Arctop | dowolny (licencja) | skupienie, obciążenie, uwaga | daje API, adaptację robi klient | wojsko, media, szkolenia |
| Neurosity | opaska Crown | skupienie, spokój | daje SDK i MCP, tryb pytania | deweloperzy |
| Neurable | słuchawki | skupienie, zmęczenie | nie, sugeruje przerwy | konsumenci |
| Emotiv | pchełki MN8 | stres, uwaga | nie, raporty dla firmy | firmy, badania |
| IDUN | pchełki | stan poznawczy, sen | platforma dla producentów | OEM, badania |
| Muse | opaska | sen, medytacja | nie | konsumenci, kliniki |
| **Wachta / „AI oddaje ster”** | **BrainAccess MINI** | **senność, przeciążenie** | **tak: routing alarmów i forma komunikatu w istniejących narzędziach** | **IT ops, dyspozytornie** |

## Co z tego wynika dla pitchu

1. **Nie mówcie „wykrywamy zmęczenie”.** To robi SmartCap od lat. Mówcie: „pierwsza warstwa, która zmienia zachowanie narzędzi do obsługi incydentów na podstawie stanu człowieka”.
2. **„AI zna twój stan” też już jest** (Neurosity MCP). Wasza nowość: agent sam decyduje, kiedy i jak eskalować, a człowiek nie musi o nic pytać.
3. **Wiarygodność kierunku:** Zander Labs (30 mln euro z budżetu państwa) i kontrakty wojskowe Arctop pokazują, że neuroadaptacja to poważny trend, a nie gadżet.
4. **Prywatność to wasz slajd obowiązkowy.** Dwa świeże przykłady: afera Muse z 50 000 h EEG i debata wokół Emotiv w pracy.
5. **Partnerstwo, nie konkurencja:** sprzęt kupujecie od BrainAccess, Emotiv albo Neurable. Wy sprzedajecie integrację.

## Czego tu nie ma
- Liczb o wielkości rynku: wymagają osobnego researchu z raportów.
- Systemów kamerowych do wykrywania zmęczenia kierowców (bez EEG). Jury może o nie zapytać jako o tańszą alternatywę.
