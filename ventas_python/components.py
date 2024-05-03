from colorama import Fore, Style
from utilities import borrarPantalla, gotoxy
import time, os


class Menu:
    def __init__(self, titulo, opciones, col, fil):
        self.titulo = titulo
        self.opciones = opciones
        self.col = col
        self.fil = fil

    def menu(self):
        print('\033[1m\033[4m\033[97m' + self.titulo + '\033[0m')
        print()
        for opcion in self.opciones:
            print(Fore.LIGHTGREEN_EX + opcion)
            print()
        opc = input('\033[1m\033[4m\033[97mElegir =>\033[0m ')
        return opc


class Valida:
    def solo_numeros(self, mensajeError, col, fil):
        while True:
            gotoxy(col, fil)
            valor = input()
            try:
                if int(valor) > 0:
                    break
            except:
                gotoxy(col, fil);
                print(mensajeError)
                time.sleep(1)
                gotoxy(col, fil);
                print(" " * 20)
        return valor

    def solo_letras(self, mensaje, mensajeError):
        while True:
            valor = str(input("       ------>   | {} ".format(mensaje)))
            if valor.isalpha():
                break
            else:
                print("      ------><  | {} ".format(mensajeError))
        return valor

    def solo_decimales(self, mensaje, mensajeError):
        while True:
            valor = str(input("     ------>   | {} ".format(mensaje)))
            try:
                valor = float(valor)
                if valor > float(0):
                    break
            except:
                print("      ------><  | {} ".format(mensajeError))
        return valor

    def cedula():
        pass


class otra:
    pass


if __name__ == '__main__':
    # instanciar el menu
    opciones_menu = ["1. Entero", "2. Letra", "3. Decimal"]
    menu = Menu(titulo="-- Mi Menú --", opciones=opciones_menu, col=10, fil=5)
    # llamada al menu
    opcion_elegida = menu.menu()
    print("Opción escogida:", opcion_elegida)
    valida = Valida()
    if (opciones_menu == 1):
        numero_validado = valida.solo_numeros("Mensaje de error", 10, 10)
        print("Número validado:", numero_validado)

    numero_validado = valida.solo_numeros("Mensaje de error", 10, 10)
    print("Número validado:", numero_validado)

    letra_validada = valida.solo_letras("Ingrese una letra:", "Mensaje de error")
    print("Letra validada:", letra_validada)

    decimal_validado = valida.solo_decimales("Ingrese un decimal:", "Mensaje de error")
    print("Decimal validado:", decimal_validado)
