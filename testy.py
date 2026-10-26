import unittest
from src.modele import Bolid, OponaSoft, OponaHard


class TestF1Simulation(unittest.TestCase):

    def test_spalanie_paliwa(self):
        """Testuje hermetyzację i metodę spalania paliwa."""
        bolid = Bolid("Verstappen")
        # Dostęp do zmiennej prywatnej w celach testowych (name mangling)
        paliwo_start = bolid._Bolid__paliwo

        bolid.spalaj_paliwo()
        paliwo_koniec = bolid._Bolid__paliwo

        self.assertTrue(paliwo_koniec < paliwo_start, "Paliwo powinno maleć po okrążeniu")

    def test_polimorfizm_opon(self):
        """Sprawdza, czy różne opony zwracają różne straty czasowe (polimorfizm)."""
        soft = OponaSoft()
        hard = OponaHard()

        # Na 10 okrążeniu Soft powinien być szybszy (mieć mniejszą stratę bazy + zużycia)
        # LUB inny w charakterystyce. Tutaj sprawdzamy czy metody zwracają float.
        strata_s = soft.oblicz_strata_czasowa(5, 1.0)
        strata_h = hard.oblicz_strata_czasowa(5, 1.0)

        self.assertNotEqual(strata_s, strata_h, "Różne mieszanki powinny mieć różne osiągi")
        self.assertIsInstance(strata_s, float)

    def test_klif_opony(self):
        """Sprawdza, czy przekroczenie limitu drastycznie zwiększa stratę."""
        soft = OponaSoft()  # Limit 13

        czas_w_limicie = soft.oblicz_strata_czasowa(10, 1.0)
        czas_po_limicie = soft.oblicz_strata_czasowa(20, 1.0)

        roznica = czas_po_limicie - czas_w_limicie
        self.assertGreater(roznica, 1.0, "Po przekroczeniu limitu degradacja powinna być ogromna")


if __name__ == '__main__':
    unittest.main()