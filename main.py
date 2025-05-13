from audio_app import AudioApp
from PyQt5 import QtWidgets
import sys

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AudioApp()
    window.show()
    sys.exit(app.exec_())
