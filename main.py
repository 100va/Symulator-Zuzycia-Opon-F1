import sys
from PyQt5.QtWidgets import QApplication
from src.gui import AplikacjaF1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    okno = AplikacjaF1()
    okno.show()
    sys.exit(app.exec_())