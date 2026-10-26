from abc import ABC, abstractmethod

# --- KLASA BAZOWA (ABSTRAKCYJNA) ---
class MieszankaOpon(ABC):
    """
    Abstrakcyjna klasa bazowa definiująca interfejs dla wszystkich typów opon.
    Wykorzystuje bibliotekę ABC (Abstract Base Classes) do wymuszenia implementacji metod w klasach pochodnych.
    """
    def __init__(self, nazwa, limit_bazowy):
        """
        Inicjalizuje podstawowe parametry opony.
        :param nazwa: Nazwa mieszanki (np. "Soft", "Medium").
        :param limit_bazowy: Szacowana liczba okrążeń przed drastycznym spadkiem wydajności.
        """
        self.nazwa = nazwa
        self.limit_bazowy = limit_bazowy

    @abstractmethod
    def oblicz_strata_czasowa(self, wiek_opony, trudnosc_toru=1.0):
        """
        Metoda abstrakcyjna. Musi zostać zaimplementowana w klasach pochodnych.
        Oblicza stratę czasową (deltę) w sekundach wynikającą ze zużycia opony.
        """
        pass

# --- KLASY POCHODNE (POLIMORFIZM) ---

class OponaSoft(MieszankaOpon):
    """
    Reprezentuje miękką mieszankę opon (najszybsza, najszybsze zużycie).
    Implementuje specyficzną dla Softa krzywą degradacji.
    """
    def __init__(self):
        super().__init__("Soft", 11) # Przekazanie parametrów do konstruktora klasy bazowej

    def oblicz_strata_czasowa(self, wiek_opony, trudnosc_toru=1.0):
        """
        Oblicza stratę czasu dla opony Soft w modelu addytywnym.
        Charakterystyka: Wysoka degradacja początkowa, gwałtowny 'klif' po przekroczeniu limitu.
        """
        # Baza: 0.0s (punkt odniesienia - najszybsza opona)
        # Degradacja liniowa: +0.12s na okrążenie (skalowane trudnością toru)
        strata = 0.0 + (0.12 * wiek_opony * trudnosc_toru)

        # Obsługa 'Klifu' (Nieliniowy spadek wydajności po przekroczeniu limitu)
        realny_limit = self.limit_bazowy / trudnosc_toru
        if wiek_opony > realny_limit:
            nadmiar = wiek_opony - realny_limit
            # Kara rośnie potęgowo (wykładnik 1.5)
            strata += 0.4 * (nadmiar ** 1.5)

        return strata

class OponaMedium(MieszankaOpon):
    """
    Reprezentuje pośrednią mieszankę opon (balans między tempem a trwałością).
    """
    def __init__(self):
        super().__init__("Medium", 22)

    def oblicz_strata_czasowa(self, wiek_opony, trudnosc_toru=1.0):
        """
        Oblicza stratę czasu dla opony Medium.
        Startuje wolniej od Softa (+0.5s), ale zużywa się wolniej.
        """
        strata = 0.5 + (0.08 * wiek_opony * trudnosc_toru)

        realny_limit = self.limit_bazowy / trudnosc_toru
        if wiek_opony > realny_limit:
            nadmiar = wiek_opony - realny_limit
            strata += 0.3 * (nadmiar ** 1.4)

        return strata

class OponaHard(MieszankaOpon):
    """
    Reprezentuje twardą mieszankę opon (najwolniejsza, najtrwalsza).
    """
    def __init__(self):
        super().__init__("Hard", 40)

    def oblicz_strata_czasowa(self, wiek_opony, trudnosc_toru=1.0):
        """
        Oblicza stratę czasu dla opony Hard.
        Startuje znacznie wolniej (+1.2s), ale degradacja jest minimalna.
        Praktycznie brak efektu 'klifu'.
        """
        strata = 1.2 + (0.04 * wiek_opony * trudnosc_toru)
        return strata

# --- KLASA REPREZENTUJĄCA POJAZD (HERMETYZACJA) ---
class Bolid:
    """
    Klasa reprezentująca stan bolidu w trakcie wyścigu.
    Demonstruje hermetyzację danych (paliwo).
    """
    def __init__(self, kierowca):
        self.kierowca = kierowca
        # Zmienna prywatna (oznaczona __). Dostęp tylko przez metody klasy.
        self.__paliwo = 110.0

    def spalaj_paliwo(self):
        """Symuluje spalanie paliwa na jednym okrążeniu."""
        if self.__paliwo > 0:
            self.__paliwo -= 1.8

    def pobierz_zysk_paliwa(self):
        """
        Oblicza zysk czasowy wynikający ze zmniejszenia masy bolidu (spalania paliwa).
        :return: Zysk w milisekundach (im lżejszy bolid, tym większy zysk).
        """
        spalone = 110.0 - self.__paliwo
        return spalone * 35  # Każdy kg spalonego paliwa to ok. 35ms zysku