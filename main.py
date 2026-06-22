# main.py
# Ponto de entrada do TimeKeeper.
# Este é o arquivo que você executa: python main.py
#
# O que acontece aqui:
# 1. QApplication inicializa o framework Qt (gerencia eventos, janelas, fontes)
# 2. Aplicamos o tema visual global
# 3. Criamos e exibimos a janela principal
# 4. app.exec() entra no "event loop" — o app fica rodando até o usuário fechar

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from ui.main_window import MainWindow
from ui.styles import APP_STYLE


def main():
    # QApplication deve ser criado antes de qualquer widget
    app = QApplication(sys.argv)

    # Define a fonte padrão do app
    app.setFont(QFont("Segoe UI", 13))

    # Aplica o stylesheet global (tema visual)
    app.setStyleSheet(APP_STYLE)

    # Cria e exibe a janela principal
    window = MainWindow()
    window.show()

    # sys.exit garante que o código de saída do Qt é propagado corretamente
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
