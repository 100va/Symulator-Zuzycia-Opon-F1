import csv
import os

class MenadzerPlikow:
    @staticmethod
    def zapisz_csv(sciezka, naglowki, dane):
        try:
            with open(sciezka, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(naglowki)
                writer.writerows(dane)
            return True, "Zapisano plik CSV."
        except Exception as e:
            return False, f"Błąd zapisu: {e}"

    @staticmethod
    def zapisz_txt(sciezka, naglowki, dane, info):
        try:
            with open(sciezka, 'w', encoding='utf-8') as f:
                f.write(f"Raport symulacji: {info}\n")
                f.write("-" * 30 + "\n")
                # Zapis nagłówków
                f.write("\t".join(naglowki) + "\n")
                # Zapis każdego wiersza danych
                for wiersz in dane:
                    f.write("\t".join(wiersz) + "\n")
            return True, "Zapisano raport TXT."
        except Exception as e:
            return False, f"Błąd zapisu: {e}"

    @staticmethod
    def wczytaj_csv(sciezka):
        if not os.path.exists(sciezka):
            return False, "Brak pliku", []
        try:
            with open(sciezka, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                wszystkie_dane = list(reader)
                if len(wszystkie_dane) > 0:
                    naglowki = wszystkie_dane[0]
                    reszta = wszystkie_dane[1:]
                    return True, "Wczytano", (naglowki, reszta)
            return False, "Plik pusty", []
        except Exception as e:
            return False, f"Błąd: {e}", []