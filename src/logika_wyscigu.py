import csv
import os
from src.modele import Bolid, OponaSoft, OponaMedium, OponaHard

# Konfiguracja dostępnych strategii wyścigowych
# Każda strategia zawiera listę obiektów opon w kolejności użycia.
STRATEGIE_DANE = [
    {"nazwa": "Soft ➔ Hard (1 PIT)", "opony": [OponaSoft(), OponaHard()]},
    {"nazwa": "Medium ➔ Hard (1 PIT)", "opony": [OponaMedium(), OponaHard()]},
    {"nazwa": "Soft ➔ Medium ➔ Soft (2 PIT)", "opony": [OponaSoft(), OponaMedium(), OponaSoft()]}
]


class Wyscig:
    """Klasa typu Data Class przechowująca informacje o konkretnym Grand Prix."""

    def __init__(self, race_id, nazwa, rok, tor, sredni_pitstop, trudnosc=1.0):
        self.id = race_id
        self.nazwa = nazwa
        self.rok = rok
        self.tor = tor
        self.pit_cost = sredni_pitstop
        self.trudnosc = trudnosc

    # Metody specjalne
    def __str__(self):
        return f"{self.rok} {self.nazwa} ({self.tor})"


class SymulatorStrategii:
    """
    Silnik symulacji. Odpowiada za przeliczenie przebiegu wyścigu okrążenie po okrążeniu.
    """

    def symuluj_wyscig(self, bolid, strategia, tempo_bazowe, pit_cost, trudnosc_toru, dystans=56):
        """
        Główna pętla symulacyjna.
        bolid: Obiekt bolidu (z paliwem).
        strategia: Wybrany zestaw opon.
        tempo_bazowe: Średnie tempo kierowcy (w ms).
        pit_cost: Koszt przejazdu przez aleję serwisową.
        trudnosc_toru: Mnożnik degradacji (np. 1.4 dla trudnego toru).
        return: Całkowity czas wyścigu oraz lista z historią okrążeń.
        """
        czas_calkowity = 0.0
        historia_okrazen = []
        bolid._Bolid__paliwo = 110.0  # Reset paliwa (dostęp do zmiennej prywatnej dla nowej symulacji)

        opony_lista = strategia['opony']
        idx_opony = 0
        obecna_opona = opony_lista[idx_opony]
        wiek_opony = 0

        # Logika Agresji: Skraca żywotność opon przy strategiach wielostopowych (2+ pitstopy),
        # aby wymusić wykorzystanie przewagi świeżej gumy.
        teoretyczny_limit = obecna_opona.limit_bazowy / trudnosc_toru
        wspolczynnik_agresji = 0.75 if len(opony_lista) >= 3 else 1.0
        limit_planowany = teoretyczny_limit * wspolczynnik_agresji

        for i in range(dystans):
            is_pit = False
            koszt_pitstopu = 0

            # 1. FIZYKA: Obliczenie wpływu opon i paliwa
            strata_opony_sec = obecna_opona.oblicz_strata_czasowa(wiek_opony, trudnosc_toru)
            strata_opony_ms = strata_opony_sec * 1000

            zysk_paliwa_ms = bolid.pobierz_zysk_paliwa()
            bolid.spalaj_paliwo()

            # 2. STRATEGIA: Decyzja o zjeździe do boksu
            # Warunek A: Osiągnięto planowany limit okrążeń.
            cond_limit = wiek_opony >= limit_planowany
            # Warunek B (Bezpiecznik): Opona straciła przyczepność (strata > 2.5s) - zjazd awaryjny.
            cond_awaria = strata_opony_sec > 2.5
            mamy_zapas = idx_opony < len(opony_lista) - 1

            if (cond_limit or cond_awaria) and mamy_zapas:
                is_pit = True
                koszt_pitstopu = pit_cost

                # Zmiana opony na kolejną z listy
                idx_opony += 1
                obecna_opona = opony_lista[idx_opony]
                wiek_opony = 0

                # Rekalkulacja limitu dla nowej mieszanki
                teoretyczny_limit = obecna_opona.limit_bazowy / trudnosc_toru
                limit_planowany = teoretyczny_limit * wspolczynnik_agresji

                # Reset straty dla nowej opony (świeża guma = wiek 0)
                strata_opony_sec = obecna_opona.oblicz_strata_czasowa(0, trudnosc_toru)
                strata_opony_ms = strata_opony_sec * 1000

            # 3. SUMOWANIE CZASU
            czas_okrazenia = tempo_bazowe + strata_opony_ms + koszt_pitstopu - zysk_paliwa_ms

            czas_calkowity += czas_okrazenia
            wiek_opony += 1

            historia_okrazen.append({
                "nr": i + 1,
                "czas_ms": czas_okrazenia,
                "opona": obecna_opona.nazwa,
                "is_pit": is_pit
            })

        return czas_calkowity, historia_okrazen


class DataLoader:
    """Klasa odpowiedzialna za wczytywanie i przetwarzanie danych z plików CSV (ETL)."""

    def __init__(self):
        self.kat = None  # Ścieżka do danych (inicjalnie pusta)

    def ustaw_sciezke(self, nowa_sciezka):
        """Ustawia dynamicznie folder z danymi źródłowymi."""
        self.kat = nowa_sciezka

    def oszacuj_trudnosc(self, nazwa_toru):
        """Heurystyka określająca trudność toru na podstawie nazwy."""
        n = nazwa_toru.lower()
        if "qatar" in n or "spain" in n or "silverstone" in n: return 1.4  # High Deg
        if "monaco" in n or "russia" in n or "mexico" in n: return 0.7  # Low Deg
        return 1.0

    def pobierz_wyscigi(self):
        """Wczytuje listę wyścigów, łącząc dane z tabel races i circuits."""
        if not self.kat: return []

        wyscigi = []
        try:
            # Słownik pomocniczy do szybkiego wyszukiwania nazw torów (Optymalizacja)
            tory = {}
            with open(os.path.join(self.kat, 'circuits.csv'), encoding='utf-8') as f:
                for row in csv.DictReader(f): tory[row['circuitId']] = row['name']

            # Zbiór ID wyścigów, dla których mamy czasy okrążeń (filtrowanie)
            with open(os.path.join(self.kat, 'lap_times.csv')) as f:
                ids = {row['raceId'] for row in csv.DictReader(f)}

            with open(os.path.join(self.kat, 'races.csv'), encoding='utf-8') as f:
                for r in csv.DictReader(f):
                    if r['raceId'] in ids:
                        nazwa_toru = tory.get(r['circuitId'], "Tor Nieznany")
                        trudnosc = self.oszacuj_trudnosc(nazwa_toru)
                        obj = Wyscig(int(r['raceId']), r['name'], r['year'], nazwa_toru, 20000, trudnosc)
                        wyscigi.append({"obj": obj, "display": f"{r['year']} {r['name']} (@ {nazwa_toru})"})

            # Sortowanie: Od najnowszych
            return sorted(wyscigi, key=lambda x: x['obj'].id, reverse=True)[:15]
        except Exception as e:
            print(f"Błąd danych: {e}")
            return []

    def pobierz_kierowcow(self, race_id):
        """Pobiera listę kierowców i ich średnie tempo dla danego wyścigu."""
        if not self.kat: return [], 22000

        try:
            with open(os.path.join(self.kat, 'drivers.csv'), encoding='utf-8') as f:
                drivers = {d['driverId']: d['surname'] for d in csv.DictReader(f)}

            # Agregacja czasów okrążeń dla każdego kierowcy
            czasy = {}
            with open(os.path.join(self.kat, 'lap_times.csv')) as f:
                for r in csv.DictReader(f):
                    # Filtrowanie błędnych okrążeń (>140s)
                    if int(r['raceId']) == race_id and int(r['milliseconds']) < 140000:
                        czasy.setdefault(r['driverId'], []).append(int(r['milliseconds']))

            # Obliczenie średniego czasu pit-stopu na tym torze
            pits = []
            with open(os.path.join(self.kat, 'pit_stops.csv')) as f:
                pits = [int(p['milliseconds']) for p in csv.DictReader(f) if
                        int(p['raceId']) == race_id and int(p['milliseconds']) < 60000]
            avg_pit = sum(pits) / len(pits) if pits else 22000

            wynik = []
            for d_id, t in czasy.items():
                srednia = sum(t) / len(t)
                b = Bolid(drivers.get(d_id, "?"))
                wynik.append((b, srednia))
            return wynik, avg_pit
        except:
            return [], 22000