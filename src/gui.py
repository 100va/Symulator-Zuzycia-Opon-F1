from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLabel, QFileDialog, QMessageBox, QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import os

# Importy modułów wewnętrznych (Logika biznesowa i obsługa plików)
from src.logika_wyscigu import DataLoader, SymulatorStrategii, STRATEGIE_DANE
from src.obsluga_plikow import MenadzerPlikow


class AplikacjaF1(QMainWindow):
    """
    Główna klasa interfejsu graficznego (GUI).
    Reprezentuje warstwę 'View' w architekturze aplikacji.
    Odpowiada za interakcję z użytkownikiem i wyświetlanie wyników,
    nie wykonując przy tym skomplikowanych obliczeń (deleguje je do logiki).
    """

    def __init__(self):
        """Konstruktor inicjalizujący okno i podpinający logikę."""
        super().__init__()  # Wywołanie konstruktora klasy nadrzędnej (wymagane przez PyQt)

        # Konfiguracja głównego okna
        self.setWindowTitle("Symulator Strategii F1")
        self.setGeometry(100, 100, 1150, 900)

        # Inicjalizacja obiektów logiki (Model)
        self.loader = DataLoader()  # Odpowiada za wczytywanie CSV
        self.symulator = SymulatorStrategii()  # Silnik obliczeniowy
        self.obecny_wyscig = None  # Przechowuje wybrany obiekt wyścigu

        # --- BUDOWA INTERFEJSU (LAYOUT) ---
        wid = QWidget()
        self.setCentralWidget(wid)
        lay = QVBoxLayout(wid)  # Układ wertykalny (elementy jeden pod drugim)

        # Tytuł aplikacji
        lbl_title = QLabel("🏁 Symulator Strategii i Zużycia Opon")
        font = lbl_title.font()
        font.setPointSize(16)
        font.setBold(True)
        lbl_title.setFont(font)
        lbl_title.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl_title)

        # --- GÓRA: Pasek Wyboru ---
        h1 = QHBoxLayout()
        # Lista wyścigów
        self.c_race = QComboBox()
        self.c_race.currentIndexChanged.connect(self.on_race)  # Sygnał zmiany wyboru
        h1.addWidget(self.c_race, stretch=2)

        # Lista kierowców
        self.c_driver = QComboBox()
        h1.addWidget(self.c_driver, stretch=1)
        lay.addLayout(h1)

        # --- ŚRODEK: Konfiguracja Toru ---
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Profil toru:"))
        self.c_trudnosc = QComboBox()
        # Dodajemy dane (tekst, wartość liczbowa)
        self.c_trudnosc.addItem("MONAKO (0.7x)", 0.7)
        self.c_trudnosc.addItem("ABU ZABI (1.0x)", 1.0)
        self.c_trudnosc.addItem("KATAR (1.4x)", 1.4)
        self.c_trudnosc.setCurrentIndex(1)
        h2.addWidget(self.c_trudnosc)
        h2.addSpacing(20)  # Odstęp
        h2.addWidget(QLabel("Liczba okrążeń:"))
        self.sb_laps = QSpinBox()
        self.sb_laps.setRange(1, 100)  # Minimum 1, maksimum 100
        self.sb_laps.setValue(56)  # Domyślnie 56
        self.sb_laps.setStyleSheet("background: white; color: black; padding: 5px;")
        h2.addWidget(self.sb_laps)


        lay.addLayout(h2)


        # --- INFO: Status walidacji ---
        self.lbl_info = QLabel("⚠️ Najpierw wczytaj folder z danymi CSV!")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        self.lbl_info.setStyleSheet("color: red; font-weight: bold;")  # Wyróżnienie błędu
        lay.addWidget(self.lbl_info)

        # --- PRZYCISK: Uruchomienie ---
        btn_run = QPushButton("URUCHOM ANALIZĘ")
        btn_run.setFixedHeight(40)
        btn_run.clicked.connect(self.run_sim)  # Podpięcie funkcji logicznej
        lay.addWidget(btn_run)

        # --- DÓŁ: Obsługa Plików ---
        h_files = QHBoxLayout()
        btn_load = QPushButton("Wczytaj Dane (.CSV)")
        btn_load.clicked.connect(self.wczytaj_dane_z_folderu)
        h_files.addWidget(btn_load)

        btn_save = QPushButton("Zapisz Wyniki")
        btn_save.clicked.connect(self.zapisz_wyniki)
        h_files.addWidget(btn_save)
        lay.addLayout(h_files)

        # --- TABELA WYNIKÓW ---
        self.table = QTableWidget(0, 4)
        # Pobieramy nazwy strategii dynamicznie z konfiguracji
        self.names = ["OKR"] + [s['nazwa'] for s in STRATEGIE_DANE]
        self.table.setHorizontalHeaderLabels(self.names)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)  # Pasek 'zebra' dla czytelności
        lay.addWidget(self.table)

        # Etykieta podsumowania
        self.lbl_total = QLabel("")
        self.lbl_total.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.lbl_total)

    def wczytaj_dane_z_folderu(self):
        """
        Otwiera dialog wyboru folderu i waliduje zawartość plików CSV.
        Zapewnia odporność programu na błędne dane wejściowe.
        """
        folder = QFileDialog.getExistingDirectory(self, "Wybierz folder z danymi CSV")
        if not folder: return  # Anulowano wybór

        # WALIDACJA: Sprawdzamy czy fizycznie istnieją wymagane pliki
        wymagane = ['races.csv', 'drivers.csv', 'lap_times.csv', 'circuits.csv', 'pit_stops.csv']
        brakujace = []
        for plik in wymagane:
            if not os.path.exists(os.path.join(folder, plik)):
                brakujace.append(plik)

        if brakujace:
            # Wyświetlamy błąd krytyczny użytkownikowi
            QMessageBox.critical(self, "Błąd", f"Brakuje plików:\n{', '.join(brakujace)}")
            return

        # Przekazanie ścieżki do logiki i odświeżenie GUI
        self.loader.ustaw_sciezke(folder)
        self.odswiez_liste_wyscigow()

        self.lbl_info.setText(f"✅ Dane załadowane: {os.path.basename(folder)}")
        self.lbl_info.setStyleSheet("color: green; font-weight: bold;")
        QMessageBox.information(self, "Sukces", "Dane poprawne. Wybierz wyścig.")

    def odswiez_liste_wyscigow(self):
        """Pobiera listę wyścigów z DataLoadera i wypełnia ComboBox."""
        dane = self.loader.pobierz_wyscigi()

        # OPTYMALIZACJA: Blokujemy sygnały, aby nie wywoływać on_race() przy każdym dodaniu
        self.c_race.blockSignals(True)
        self.c_race.clear()

        if not dane:
            self.c_race.addItem("Brak danych", None)
        else:
            self.c_race.addItem("-- Wybierz Wyścig --", None)
            for item in dane:
                # addItem przyjmuje tekst (wyświetlany) i UserData (ukryty obiekt)
                self.c_race.addItem(item['display'], item['obj'])

        self.c_race.blockSignals(False)

    def on_race(self):
        """Slot obsługujący zmianę wybranego wyścigu."""
        wyscig = self.c_race.currentData()  # Pobieramy ukryty obiekt wyścigu
        if not wyscig: return

        self.obecny_wyscig = wyscig
        # Pobieramy kierowców i średni pit-stop dla danego toru
        kierowcy, pit_stop = self.loader.pobierz_kierowcow(wyscig.id)
        self.obecny_wyscig.pit_cost = pit_stop

        self.lbl_info.setText(f"📍 {wyscig.tor} | Pit-Stop: {pit_stop / 1000:.1f}s")
        self.lbl_info.setStyleSheet("color: black; font-weight: bold;")

        # AUTOMATYZACJA: Ustawienie trudności na podstawie danych historycznych
        if hasattr(wyscig, 'trudnosc'):
            if wyscig.trudnosc > 1.2:
                self.c_trudnosc.setCurrentIndex(2)  # High Deg
            elif wyscig.trudnosc < 0.9:
                self.c_trudnosc.setCurrentIndex(0)  # Low Deg
            else:
                self.c_trudnosc.setCurrentIndex(1)  # Standard

        # Odświeżenie listy kierowców
        self.c_driver.blockSignals(True)
        self.c_driver.clear()
        for bolid, tempo in kierowcy:
            self.c_driver.addItem(bolid.kierowca, (bolid, tempo))
        self.c_driver.blockSignals(False)

    def run_sim(self):
        """
        Główna funkcja sterująca.
        Pobiera dane z GUI, uruchamia symulację i wizualizuje wyniki w tabeli.
        """
        if not self.loader.kat:
            QMessageBox.warning(self, "Uwaga", "Wczytaj najpierw dane!")
            return

        dane = self.c_driver.currentData()
        if not dane: return
        bolid, base_pace = dane

        LAPS = self.sb_laps.value()
        self.table.setRowCount(LAPS)
        trudnosc = self.c_trudnosc.currentData()
        wyniki = []
        self.table.setRowCount(LAPS)
        trudnosc = self.c_trudnosc.currentData()

        # Iteracja po wszystkich dostępnych strategiach
        for col, strat in enumerate(STRATEGIE_DANE):
            # 1. Obliczenia (Logika Biznesowa)
            czas, okr = self.symulator.symuluj_wyscig(
                bolid, strat, base_pace, self.obecny_wyscig.pit_cost, trudnosc, LAPS
            )
            wyniki.append((strat['nazwa'], czas))

            # 2. Wizualizacja (GUI)
            for i, o in enumerate(okr):
                if col == 0:
                    self.table.setItem(i, 0, QTableWidgetItem(str(o['nr'])))

                # Konwersja czasu (ms -> min:sec)
                minuty = int(o['czas_ms'] // 60000)
                sekundy = (o['czas_ms'] % 60000) / 1000

                # Ustalenie wyglądu komórki
                if o['is_pit']:
                    tekst = "BOX"
                    kolor_tla = Qt.red
                    kolor_tekstu = Qt.white
                else:
                    tekst = f"{minuty}:{sekundy:05.2f}"
                    kolor_tla = Qt.white
                    # Kolorowanie tekstu zależnie od mieszanki opon
                    if "Soft" in o['opona']:
                        kolor_tekstu = Qt.red
                    elif "Medium" in o['opona']:
                        kolor_tekstu = Qt.darkYellow
                    else:
                        kolor_tekstu = Qt.black

                item = QTableWidgetItem(tekst)
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(QColor(kolor_tekstu))
                if o['is_pit']:
                    item.setBackground(QColor(kolor_tla))

                self.table.setItem(i, col + 1, item)

        # Sortowanie wyników i wyświetlenie podsumowania
        wyniki.sort(key=lambda x: x[1])
        najlepszy = wyniki[0][1]
        info = "WYNIKI:\n"
        for i, (nazwa, czas) in enumerate(wyniki):
            strata = (czas - najlepszy) / 1000
            info += f"{i + 1}. {nazwa}: +{strata:.2f}s\n"
        self.lbl_total.setText(info)

    def zapisz_wyniki(self):
        """
        Pobiera aktualny stan tabeli i przekazuje go do modułu zapisu.
        Implementuje zasadę 'What You See Is What You Get'.
        """
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Błąd", "Brak danych.")
            return

        sciezka, _ = QFileDialog.getSaveFileName(self, "Zapisz", "", "CSV (*.csv);;TXT (*.txt)")
        if not sciezka: return

        # Pobieranie nagłówków
        naglowki = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]

        # Pobieranie danych z tabeli (Scraping)
        dane = []
        for r in range(self.table.rowCount()):
            wiersz = []
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                wiersz.append(item.text() if item else "")
            dane.append(wiersz)

        # Delegacja zapisu do Menadżera Plików
        if sciezka.endswith('.txt'):
            ok, msg = MenadzerPlikow.zapisz_txt(sciezka, naglowki, dane, self.lbl_info.text())
        else:
            ok, msg = MenadzerPlikow.zapisz_csv(sciezka, naglowki, dane)

        if ok:
            QMessageBox.information(self, "Info", msg)
        else:
            QMessageBox.critical(self, "Błąd", msg)