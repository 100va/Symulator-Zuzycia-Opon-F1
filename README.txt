PROJEKT: Symulator Strategii F1 (2024)
AUTOR: Dawid Maligranda
DATA: 11.02.2026

1. OPIS PROJEKTU
Aplikacja służy do analizy strategii wyścigowych Formuły 1. Wykorzystuje historyczne dane o torach i kierowcach, a następnie symuluje przebieg wyścigu z uwzględnieniem fizyki zużycia opon i spalania paliwa.

2. INSTRUKCJA UŻYTKOWANIA
a) Uruchom plik main.py.
b) Kliknij "WCZYTAJ DANE ŹRÓDŁOWE" i wskaż folder zawierający pliki CSV (folder 'data').
c) Wybierz wyścig, kierowcę oraz profil trudności toru.
d) Kliknij "URUCHOM ANALIZĘ".
e) Wyniki można zapisać przyciskiem "ZAPISZ WYNIKI".

3. STRUKTURA MODUŁÓW
- src/modele.py: Klasy fizyczne (Bolid, Opony). Implementacja OOP (polimorfizm, hermetyzacja).
- src/logika_wyscigu.py: Silnik symulacji i klasa DataLoader (ETL).
- src/obsluga_plikow.py: Moduł pomocniczy do operacji I/O (CSV/TXT).
- src/gui.py: Interfejs graficzny (PyQt5).
- tests.py: Testy jednostkowe.

4. WYMAGANIA
- Python 3.8+
- Biblioteki: PyQt5, csv, os, unittest