class Product:
    next = 0

    def __init__(self, id=0, descrip="Ninguno", preci=0, stock=0):
        Product.next += 1
        self.__id = id  # ID único asignado a cada producto
        self.descrip = descrip
        self.preci = preci
        self.__stock = stock  # Atributo privado para el stock
        
    @property
    def id(self):
        # Getter para obtener el valor del atributo privado __id
        return self.__id

    @property
    def stock(self):
        # Getter para obtener el valor del atributo privado __stock
        return self.__stock

    @stock.setter
    def stock(self, value):
        # Setter para modificar el valor del atributo privado __stock
        if value < 0:
            raise ValueError("El stock no puede ser negativo")
        self.__stock = value
    
    def __repr__(self):
        return f'Producto:{self.__id} {self.descrip} {self.preci} {self.stock}'
    
    def __str__(self):
        return f'Producto:{self.__id} {self.descrip} {self.preci} {self.stock}'
    
    def getJson(self):
        return {"id": self.__id, "descrip": self.descrip, "preci": self.preci, "stock": self.stock}
      
    def show(self):
        print(f'{self.__id}  {self.descrip}           {self.preci}  {self.stock}')

          
if __name__ == '__main__':
    # Se ejecuta solo si este script es el principal
    product1 = Product("Aceite",2,1000)
    product2 = Product("Colas",3,5000)
    product3 = Product("leche",1,300)
    # Muestra la información de la primera empresa
    products = []
    products.append(product1)
    products.append(product2)
    products.append(product3)
    # print(products)
    prods=[]
    print('Id Descripcion Precio tock') 
    for prod in products:
      print(prod.getJson())
      prods.append(prod.getJson())
    print(prods)
    