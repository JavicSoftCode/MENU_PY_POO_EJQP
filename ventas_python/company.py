class Company:
    next = 0  # Variable de clase (estática) para almacenar el próximo ID disponible

    # Método constructor que se ejecuta cuando se instancia la clase
    def __init__(self, name="SuperMaxi", ruc="0943213456001"):
        # Incrementa el contador de ID para cada nueva instancia
        Company.next += 1
        # Variables de instancia
        self.__id = Company.next  # Asigna el ID único a la instancia actual privada
        self.business_name = name  # Asigna el nombre de la empresa a la instancia actual
        self.ruc = ruc  # Asigna el RUC de la empresa a la instancia actual

    # Método de usuario que muestra la información de la empresa (ID, nombre y RUC)
    def show(self):
       # print(f"Id:{self.__id} Empresa: {self.business_name} ruc:{self.ruc}")
        # Método para imprimir los detalles del cliente minorista en la consola
        print(f"\033[1m\033[4m\033[97mDatos De Empresa ⬇️ \033[0m  \033[92m \n\n RUC \033[97m=> \033[0m {self.ruc} \n\033[92m Nombre D' Empresa \033[97m=> \033[0m {self.business_name}\033")

    def getJson(self):
        return {"id": self.__id, "rasonsocial": self.business_name, "ruc": self.ruc}

    @staticmethod
    def get_business_name():
        return f"Empresa:Corporacion el Rosado ruc:0876543294001"