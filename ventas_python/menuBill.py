import datetime
import json
import os
import time
from abc import ABC
from colorama import init, Fore, Style
import msvcrt  
import datetime

from tabulate import tabulate
from functools import reduce
from company import Company
from components import Menu, Valida
from customer import RegularClient, VipClient, JsonFile
from iCrud import ICrud
from product import Product
from sales import Sale
from utilities import borrarPantalla, gotoxy
from utilities import reset_color, red_color, green_color, blue_color, purple_color

path, _ = os.path.split(os.path.abspath(__file__))
white_color = Fore.WHITE
bold_white_color = Style.BRIGHT + Fore.WHITE
reset_color = Style.RESET_ALL
    
def message_decorator(func):
    def wrapper(*args, **kwargs):
        while True:
            borrarPantalla()
            result = func(*args, **kwargs)
            if isinstance(result, str):
                print("\n\n\033[91m\033[4m🚨 ERROR:", result, "\033[0m")
                time.sleep(2)
                continue
            else:
                return result
    return wrapper

def loadInvoices():
    with open('ventas_python/archivos/invoices.json', 'r') as f:
        return json.load(f)

def showInvoice(factura):
    factura = factura.copy() 
    print(tabulate([factura], headers="keys", tablefmt="pretty"))

def showInvoices(facturas):
    total_acumulado = reduce(lambda a, b: a + b['total'], facturas, 0)
    total_acumulado = round(total_acumulado, 2) 
    num_facturas = len(facturas)
    for factura in facturas:
        factura = factura.copy()  
    print(tabulate(facturas, headers="keys", tablefmt="pretty"))
    print(f"\n\033[92m Total Acumulado \033[97m=> \033[0m {total_acumulado}")
    print(f"\033[92m Cantidad de Facturas \033[97m=> \033[0m {num_facturas}")

def findInvoice(facturas, numero):
    for factura in facturas:
        if factura['factura'] == numero:
            return factura
    return None

def sortInvoices(facturas, orden):
    return sorted(facturas, key=lambda x: x['total'], reverse=(orden == 'max'))

class CrudClients(ICrud, ABC):
  @message_decorator
  def create(self):
    json_file_path = path + '/archivos/clients.json'
    json_file = JsonFile(json_file_path)
    
    print('\033[1m\033[4m\033[97mRegistrando cliente.\033[0m')

    dni = input("\n\033[92m Ingresar número de cédula \033[0m\033[97m=> \033[0m").strip()
    if ' ' in dni or not dni.isdigit() or len(dni) != 10:
        return "Formato correcto 10 dígitos numéricos completos. Sin espacios en medio."

    data = json_file.read()
    if data:
        clients = json.loads(data)
    else:
        clients = []

    for client in clients:
        if client["dni"] == dni:
            return "No se puede registrar el cliente porque ya existe uno con esa cédula. " 

    first_name = input("\n\033[92m Ingresar nombres completos \033[0m\033[97m=> \033[0m").strip()
    if not all(c.isalpha() or c.isspace() for c in first_name) or len(first_name.split()) != 2 or any(len(name) < 3 for name in first_name.split()):
        return "Ingresar nombres completos. Cada nombre debe tener más de 2 caracteres. Números y símbolos, NO."

    last_name = input("\n\033[92m Ingresar apellidos completos \033[0m\033[97m=> \033[0m").strip()
    if not all(c.isalpha() or c.isspace() for c in last_name) or len(last_name.split()) != 2 or any(len(lastname) < 3 for lastname in last_name.split()):
        return "Ingresar apellidos completos. Cada apellido debe tener más de 2 caracteres. Números y símbolos, NO."

    cliente = input("\n\033[92m Cliente : Regular o Vip \033[0m\033[97m=> \033[0m").lower()
    if not all(c.isalpha() or c.isspace() for c in cliente) or any(len(cliente) < 3 for cliente in cliente.split()):
        return "Regular o Vip. Regular o Vip debe tener más de 2 caracteres. Números y símbolos, NO."
    
    if cliente == "regular":
        client = RegularClient(first_name, last_name, dni, True)
    elif cliente == "vip":
        client = VipClient(first_name, last_name, dni)
        limite_vip = float(input("\n\033[92m Ingresar el límite de crédito \033[0m\033[97m=> \033[0m"))
        client.limit = max(min(limite_vip, 20000), 10000)

    borrarPantalla()
    client.show()

    if input("\033[1m\033[4m\033[97m\n ¿Desea guardar los datos? (YES/NO) => \033[0m").lower() == 'yes':
        clients.append(client.getJson())
        json_file.write(json.dumps(clients))
        print("\n\n \033[97m🟢 Cliente guardado. \033[0m")
    else:
        print("\n\n \033[97m🔴 Cliente no guardado. \033[0m")
    time.sleep(2)
    return None

  @message_decorator
  def update(self):
    json_file_path = path + '/archivos/clients.json'
    json_file = JsonFile(json_file_path)

    print('\n\033[1m\033[4m\033[97mActualizar datos del cliente.\033[0m')

    dni = input("\n\033[92m Ingresar número de cédula, para actualizar datos del cliente \033[0m\033[97m=> \033[0m").strip()
    if ' ' in dni or not dni.isdigit() or len(dni) != 10:
        return "Formato correcto 10 dígitos numéricos completos. --- 🚨 ERROR: Sin espacios en medio."

    old_clients = json.loads(json_file.read() or '[]')
    found_client = next((cliente for cliente in old_clients if cliente['dni'] == dni), None)

    if found_client is None:
        return "Cliente no encontrado."

    borrarPantalla()
    if found_client['valor'] == 0.1:
        client = RegularClient(found_client['first_name'], found_client['last_name'], found_client['dni'], True)
    else:
        client = VipClient(found_client['first_name'], found_client['last_name'], found_client['dni'])
        client.limit = found_client['valor']  

    client.show() 

    print("\n\033[97m\033[1m\033[4mEnter para actualizar o ESC para cancelar \033[0m")

    while True:
        if msvcrt.kbhit():
            entrada = msvcrt.getch()

            if entrada == b"\x1b":
                print()
                print("\033[91;4m❌ Actualización cancelada.\033[0m")
                time.sleep(1)
                break

            elif entrada == b"\r":
                borrarPantalla()
                print('\n\033[1m\033[4m\033[97mActualizando datos del cliente.\033[0m')

                new_dni = input("\n\033[92m Ingresar número de cédula \033[0m\033[97m=> \033[0m").strip()
                if ' ' in new_dni or not new_dni.isdigit() or len(new_dni) != 10:
                    return "Formato correcto 10 dígitos numéricos completos. Sin espacios en medio."

                if new_dni != found_client["dni"]:
                    return "No se puede cambiar el DNI. Solo se permite editar los datos del cliente con la cédula proporcionada inicialmente."

                first_name = input("\n\033[92m Ingresar nombres completos \033[0m\033[97m=> \033[0m").strip()
                if not all(c.isalpha() or c.isspace() for c in first_name) or len(first_name.split()) != 2 or any(len(name) < 3 for name in first_name.split()):
                    return "Ingresar nombres completos. Cada nombre debe tener más de 2 caracteres. Números y símbolos, NO."

                last_name = input("\n\033[92m Ingresar apellidos completos \033[0m\033[97m=> \033[0m").strip()
                if not all(c.isalpha() or c.isspace() for c in last_name) or len(last_name.split()) != 2 or any(len(lastname) < 3 for lastname in last_name.split()):
                    return "Ingresar apellidos completos. Cada apellido debe tener más de 2 caracteres. Números y símbolos, NO."

                cliente = input("\n\033[92m Cliente : Regular o Vip \033[0m\033[97m=> \033[0m").lower()
                if not all(c.isalpha() or c.isspace() for c in cliente) or any(len(cliente) < 3 for cliente in cliente.split()):
                    return "Regular o Vip. Regular o Vip debe tener más de 2 caracteres. Números y símbolos, NO."

                if cliente == "regular":
                    client = RegularClient(first_name, last_name, new_dni, True)
                elif cliente == "vip":
                    client = VipClient(first_name, last_name, new_dni)
                    limite_vip = float(input("\n\033[92m Ingresar el límite de crédito \033[0m\033[97m=> \033[0m"))
                    client.limit = max(min(limite_vip, 20000), 10000)

                borrarPantalla()
                client.show()

                if input("\033[1m\033[4m\033[97m\n ¿Desea guardar los datos? (YES/NO) => \033[0m").lower() == 'yes':
                    found_client["dni"] = new_dni
                    found_client["first_name"] = first_name
                    found_client["last_name"] = last_name
                    found_client["valor"] = client.discount if isinstance(client, RegularClient) else client.limit
                    json_file.write(json.dumps(old_clients))
                    print("\n⬇️")
                    print("\033[97m\033[4m🟢 Datos del cliente actualizados.\033[0m")
                    break
                else:
                    print("Opción inválida. Presione ESC para cancelar o Enter para continuar.")
    return None

  @message_decorator
  def delete(self):
    json_file_path = path + '/archivos/clients.json'
    json_file = JsonFile(json_file_path)

    print('\n\033[1m\033[4m\033[97mEliminará los datos del cliente.\033[0m')
    
    dni = input("\n\033[92m Ingresar número de cédula, para eliminar los datos del cliente \033[0m\033[97m=> \033[0m").strip()
    if ' ' in dni or not dni.isdigit() or len(dni) != 10:
        return "Formato correcto 10 dígitos numéricos completos. --- 🚨 ERROR: Sin espacios en medio."

    old_clients = json.loads(json_file.read() or "[]")
    
    updated_clients = list(filter(lambda client: client["dni"] != dni, old_clients))
    deleted = len(updated_clients) != len(old_clients)
    
    if deleted:
        borrarPantalla()
        print("\033[97m\033[1m\033[4m✅ Verificar Datos\033[0m")
        client_to_delete = next((client for client in old_clients if client["dni"] == dni), None)
        print("\n\033[92m DNI \033[97m=>\033[0m", dni)
        print("\033[92m Nombres \033[97m=>\033[0m", client_to_delete["first_name"])
        print("\033[92m Apellidos \033[97m=>\033[0m", client_to_delete["last_name"])
        print("\033[92m Límite de crédito \033[97m=>\033[0m", client_to_delete["valor"])

        aceptar = input("\n\033[97m\033[1m\033[4m¿Eliminar los datos del cliente. ? (YES/NO) => \033[0m").lower()
        
        if aceptar == 'yes':
            print("\n⬇️")
            print("\033[97m\033[4m🟢 Datos del cliente eliminados.\033[0m")
            json_file.write(json.dumps(updated_clients))
            time.sleep(2)
        else:
            print("\n⬇️")
            print("\033[97m\033[4m🔴 Eliminación cancelada.\033[0m")
            time.sleep(2)
    else:
        return "Cliente no encontrado. Verifique la cédula e intente de nuevo."

  @message_decorator
  def consult(self):
    json_file_path = path + '/archivos/clients.json'
    json_file = JsonFile(json_file_path)

    print('\033[1m\033[4m\033[97mConsulta datos del cliente.\033[0m')
    
    dni = input("\n\033[92m Ingresar número de cédula, para consultar los datos del cliente \033[0m\033[97m=> \033[0m").strip()
    if ' ' in dni or not dni.isdigit() or len(dni) != 10:
        return "Formato correcto 10 dígitos numéricos completos. --- 🚨 ERROR: Sin espacios en medio."

    old_clients = json.loads(json_file.read() or "[]")

    if not old_clients:
        print("JSON VACÍO")
        return

    found_clients = list(filter(lambda client: client["dni"] == dni, old_clients))
    
    if found_clients:
        borrarPantalla()
        print("\033[97m\033[1m\033[4m✅ Consultando Datos Clientes\033[0m")
        print()
        for client_data in found_clients:
            if client_data["valor"] == 0.1:
                client = RegularClient(client_data["first_name"], client_data["last_name"], client_data["dni"], True)
                tipo_cliente = "Cliente Minorista"
            else:
                client = VipClient(client_data["first_name"], client_data["last_name"], client_data["dni"])
                client.limit = client_data["valor"]  
                tipo_cliente = "Cliente VIP"
            print(f"\033[92m DNI \033[97m=>\033[0m {client.dni}")
            print(f"\033[92m Nombres \033[97m=>\033[0m {client.first_name}")
            print(f"\033[92m Apellidos \033[97m=>\033[0m {client.last_name}")
            if isinstance(client, VipClient):
                print(f"\033[92m Crédito \033[97m=>\033[0m {client.limit}")
            else:
                print(f"\033[92m Descuento \033[97m=>\033[0m {client.discount}")
            print(f"\033[92m Tipo de Cliente \033[97m=>\033[0m {tipo_cliente}")
        input("\n\033[1;4;97m⬅️  Enter para salir\033[0m")
    else:
        print("\n\033[1;4;97m🔴 No se encontró al cliente.\033[0m")

class CrudProducts(ICrud):
  @message_decorator
  def create(self):
    json_file_path = path + '/archivos/products.json'
    json_file = JsonFile(json_file_path)

    print('\033[1m\033[4m\033[97mRegistrando producto.\033[0m')
    
    id = input("\n\033[92m Ingresar ID del producto \033[0m\033[97m=> \033[0m").strip()
    if ' ' in id or not id.isdigit() or len(id) != 1:
        return "Del dígito. --- 🚨 ERROR: Sin espacios en medio."

    products_data = json.loads(json_file.read() or '[]')
    
    if any(product["id"] == id for product in products_data):
        return "Ya existe un producto con este ID."

    descripcion = input("\n\033[92m Ingresar descripción del producto \033[0m\033[97m=> \033[0m").strip()
    if not all(c.isalpha() or c.isspace() for c in descripcion) or any(len(descrip) < 3 for descrip in descripcion.split()):
        return "Ingresar productos existentes. --- 🚨 ERROR: Cada nombre del producto debe tener > 2 caracteres. --- 🚨 ERROR: Números y símbolos, NO."

    precio = input("\n\033[92m Ingresar precio del producto \033[0m\033[97m=> \033[0m").strip()
    if not precio.replace('.', '', 1).replace('-', '', 1).isdigit() or float(precio) < 0:
        return "Ingresar datos numéricos para el precio."

    stock = input("\n\033[92m Ingresar el stock del producto \033[0m\033[97m=> \033[0m").strip()
    if not stock.replace('.', '', 1).replace('-', '', 1).isdigit() or float(stock) < 0:
        return "Ingresar datos numéricos para el stock."
      
    precio = float(precio)
    stock = int(stock)
    
    borrarPantalla()
    print("\033[97m\033[1m\033[4m✅ Verificar Datos\033[0m")
    
    print(f"\n\033[92m ID \033[0m\033[97m =>\033[0m {id}\n\033[92m Descripción\033[0m\033[97m =>\033[0m {descripcion}\n\033[92m Precio $\033[0m\033[97m =>\033[0m {precio}\n\033[92m Stock\033[0m\033[97m =>\033[0m {stock}")

    if input("\n\033[97m\033[1m\033[4m¿Aceptar y guardar? (YES/NO) => \033[0m").lower() == 'yes':
        product = Product(id, descripcion, precio, stock)
        products_data.append(product.getJson())
        json_file.write(json.dumps(products_data))
        print("\n⬇️")
        print("\033[97m\033[4m🟢 Producto se guardó.\033[0m")
        time.sleep(2)
    else:
        print("\n⬇️")
        print("\033[97m\033[4m🔴 Producto no se guardó.\033[0m")
        time.sleep(2)

  @message_decorator
  def update(self):
    json_file_path = path + '/archivos/products.json'
    json_file = JsonFile(json_file_path)

    print('\033[1m\033[4m\033[97mActualizar datos del producto.\033[0m')
    
    id = input("\n\033[92m Ingresar ID del producto, para actualizar datos del producto \033[0m\033[97m=> \033[0m").strip()
    if ' ' in id or not id.isdigit() or len(id) != 1:
        return "Del dígito. --- 🚨 ERROR: Sin espacios en medio."

    products_data = json.loads(json_file.read() or '[]')
    if not any(product["id"] == id for product in products_data):
        return "No existe un producto con este ID."

    old_products = json.loads(json_file.read() or '[]')

    found_product = next((product for product in old_products if product["id"] == id), None)

    if found_product is None:
        return "Producto no encontrado. Verifique el ID e intente nuevamente."
    
    print(f"\033[92m\n ID \033[97m=> \033[0m {id} \n\033[92m Descripción \033[97m=> \033[0m {found_product['descripcion']}\n\033[92m Precio \033[97m=> \033[0m {found_product['precio']}\n\033[92m Stock \033[97m=> \033[0m {found_product['stock']}")
    
    print("\n\033[97m\033[1m\033[4mEnter para actualizar o ESC para cancelar \033[0m")
    
    while True:
        
        if msvcrt.kbhit():  
            entrada = msvcrt.getch()  
            
            if entrada == b"\x1b": 
                print("\n\033[91;4m❌ Actualización cancelada.\033[0m")
                time.sleep(1)
                break
            
            elif entrada == b"\r":  
                
                borrarPantalla()
                print('\033[1m\033[4m\033[97mActualizando datos del producto.\033[0m')
                id = input("\n\033[92m Ingresar ID del producto \033[0m\033[97m=> \033[0m").strip()
                if ' ' in id or not id.isdigit() or len(id) != 1:
                    return "Del dígito. --- 🚨 ERROR: Sin espacios en medio."
                
                products_data = json.loads(json_file.read() or '[]')
                if not any(product["id"] == id for product in products_data):
                    return "No existe un producto con este ID."

                if id != found_product["id"]:
                    return "No se puede cambiar el ID. Solo se permite editar los datos del producto con el ID proporcionado inicialmente."

                descripcion = input("\n\033[92m Ingresar descripción del producto \033[0m\033[97m=> \033[0m").strip()
                if not all(c.isalpha() or c.isspace() for c in descripcion) or any(len(descrip) < 3 for descrip in descripcion.split()):
                    return "Ingresar productos existentes. --- 🚨 ERROR: Cada nombre del producto debe tener > 2 caracteres. --- 🚨 ERROR: Números y símbolos, NO."

                precio = input("\n\033[92m Ingresar precio del producto \033[0m\033[97m=> \033[0m").strip()
                if not precio.replace('.', '', 1).replace('-', '', 1).isdigit() or float(precio) < 0:
                    return "Ingresar datos numéricos para el precio."

                stock = input("\n\033[92m Ingresar el stock del producto \033[0m\033[97m=> \033[0m").strip()
                if not stock.replace('.', '', 1).replace('-', '', 1).isdigit() or float(stock) < 0:
                    return "Ingresar datos numéricos para el stock."

                precio = float(precio)
                stock = int(stock)

                borrarPantalla()
                print("\033[97m\033[1m\033[4m✅ Verificar Datos Actualizados\033[0m")
                print(f"\n\033[92m ID \033[0m\033[97m =>\033[0m {id}\n\033[92m Descripción\033[0m\033[97m =>\033[0m {descripcion}\n\033[92m Precio $\033[0m\033[97m =>\033[0m {precio}\n\033[92m Stock\033[0m\033[97m =>\033[0m {stock}")
                aceptar = input("\n\033[97m\033[1m\033[4m¿Aceptar y guardar? (YES/NO) => \033[0m").lower()

                if aceptar == 'yes':
                    found_product["id"] = id
                    found_product["descripcion"] = descripcion
                    found_product["precio"] = precio
                    found_product["stock"] = stock

                    for product in old_products:
                        if product["id"] == str(id):
                            product["descripcion"] = descripcion
                            product["precio"] = precio
                            product["stock"] = stock
                            break

                    json_file.write(json.dumps(old_products))

                    print("\n⬇️")
                    print("\033[97m\033[4m🟢 Datos del producto actualizados.\033[0m")
                    break
                else:
                    print("\n⬇️")
                    print("\033[97m\033[4m🔴 Actualización cancelada.\033[0m")
                    break
            else:
                return "Opción inválida. Presione ESC para cancelar o Enter para continuar." 

  @message_decorator                          
  def delete(self):
    json_file_path = path + '/archivos/products.json'
    json_file = JsonFile(json_file_path)

    print('\033[1m\033[4m\033[97mEliminará los datos del producto.\033[0m')
    
    id = input("\n\033[92m Ingresar id del producto, para eliminar los datos del producto \033[0m\033[97m=> \033[0m").strip()
    if ' ' in id or not id.isdigit() or len(id) != 1:
        return "Del dígito. --- 🚨 ERROR: Sin espacios en medio."
          
    old_products = json.loads(json_file.read() or '[]')
    
    updated_products = list(filter(lambda product: product["id"] != id, old_products))
    deleted = len(updated_products) != len(old_products)
    
    if deleted:
        borrarPantalla()
        print("\n\033[97m\033[1m\033[4m✅ Verificar Datos\033[0m")
        product_to_delete = next((product for product in old_products if product["id"] == id), None)
        print("\033[92m ID \033[97m=>\033[0m", id)
        print("\033[92m Descripción \033[97m=>\033[0m", product_to_delete["descripcion"])
        print("\033[92m Precio \033[97m=>\033[0m", product_to_delete["precio"])
        print("\033[92m Stock \033[97m=>\033[0m", product_to_delete["stock"])
        aceptar = input("\n\033[97m\033[1m\033[4m¿Eliminar los datos del producto. ? (YES/NO) => \033[0m").lower()
        if aceptar == 'yes':
            print("\n⬇️")
            print("\033[97m\033[4m🟢 Datos del productos eliminados.\033[0m")
            json_file.write(json.dumps(updated_products))
            time.sleep(2)
        else:
            print("\n⬇️")
            print("\033[97m\033[4m🔴 Eliminación cancelada.\033[0m")
            time.sleep(2)
    else:
        return "Producto no encontrado. Verifique el id e intente nuevamente."

  @message_decorator
  def consult(self):
    json_file_path = path + '/archivos/products.json'
    json_file = JsonFile(json_file_path)

    print('\033[1m\033[4m\033[97mConsultará los datos del producto.\033[0m')
    id = input("\n\033[92m Ingresar id del producto, para consultar los datos del producto \033[0m\033[97m=> \033[0m").strip()
    if ' ' in id or not id.isdigit() or len(id) != 1:
        return "Del dígito. --- 🚨 ERROR: Sin espacios en medio."
      
    old_products = json.loads(json_file.read() or '[]')
    
    if not old_products:
        print("JSON VACIO")
        return
    
    found_products = list(filter(lambda product: product["id"] == id, old_products))
    
    if found_products:
        borrarPantalla()
        print("\033[97m\033[1m\033[4m✅ Consultando Datos\033[0m")
        print()
        headers = ["ID", "Descripción", "Precio", "Stock"]
        table = []
        for product in found_products:
            row = [product["id"], product["descripcion"], product["precio"], product["stock"]]
            table.append(row)
        print(tabulate(table, headers, tablefmt="pretty"))

        input("\n\033[1;4;97m⬅️  Enter para salir\033[0m")
    else:
        print("\n\033[1;4;97m🔴 No se encontró al cliente.\033[0m")

class CrudSales(ICrud):
  def create(self):
   
    validar = Valida()
    
    borrarPantalla()
    print('\033c', end='')
    gotoxy(2,1);print(green_color+"██"*50+reset_color)
    gotoxy(30,2);print(blue_color+"Registro de Venta")
    gotoxy(17,3);print(blue_color+Company.get_business_name())
    gotoxy(5,4);print(f"Factura#:F0999999 {' '*3} Fecha:{datetime.datetime.now()}")
    gotoxy(66,4);print(" Subtotal:")
    gotoxy(66,5);print(" Decuento:")
    gotoxy(66,6);print(" Iva     :")
    gotoxy(66,7);print(" Total   :")
    gotoxy(10,6);print("Cedula:")
    dni = validar.solo_numeros("Error: Solo numeros",23,6)
    
    json_file = JsonFile(path+'/archivos/clients.json')
    clients_data = json_file.find("dni", dni)
    
    if not clients_data:
        gotoxy(35,6);print("Cliente no existe")
        return
    
    client = clients_data[0]
    cli = RegularClient(client["first_name"], client["last_name"], client["dni"], card=True) 
    sale = Sale(cli)
    
    gotoxy(35,6);print(cli.fullName())
    gotoxy(2,8);print(green_color+"██"*50+reset_color) 
    gotoxy(5,9);print(purple_color+"Linea") 
    gotoxy(12,9);print("Id_Articulo") 
    gotoxy(24,9);print("Descripcion") 
    gotoxy(38,9);print("Precio") 
    gotoxy(48,9);print("Cantidad") 
    gotoxy(58,9);print("Subtotal") 
    gotoxy(70,9);print("n->Terminar Venta)"+reset_color)
    
    follow = "s"
    line = 1
    
    while follow.lower() == "s":
        gotoxy(7,9+line);print(line)
        gotoxy(15,9+line);id_articulo = validar.solo_numeros("Error: Solo numeros",15,9+line)
        
        json_file = JsonFile(path+'/archivos/products.json')
        prods = json_file.find("id", id_articulo)
        
        if not prods:
            gotoxy(24,9+line);print("Producto no existe")
            time.sleep(1)
            gotoxy(24,9+line);print(" "*20)
            
        else:    
            prods = prods[0]
            product = Product(prods["id"], prods["descripcion"], prods["precio"], prods["stock"])
            gotoxy(24,9+line);print(product.descrip)
            gotoxy(38,9+line);print(product.preci)
            gotoxy(49,9+line);qty = int(validar.solo_numeros("Error: Solo numeros",49,9+line))
            gotoxy(59,9+line);print(product.preci * qty)
            sale.add_detail(product, qty)
            gotoxy(76,4);print(round(sale.subtotal,2))
            gotoxy(76,5);print(round(sale.discount,2))
            gotoxy(76,6);print(round(sale.iva,2))
            gotoxy(76,7);print(round(sale.total,2))
            gotoxy(74,9+line);follow = input() or "s"  
            gotoxy(76,9+line);print(green_color+"✔"+reset_color)  
            line += 1
    
    gotoxy(15,9+line);print(red_color+"Esta seguro de grabar la venta(s/n):")
    gotoxy(54,9+line);procesar = input().lower()
    
    if procesar == "s":
        gotoxy(15,10+line);print("😊 Venta Grabada satisfactoriamente 😊"+reset_color)
        
        json_file = JsonFile(path+'/archivos/invoices.json')
        invoices = json_file.read()
        
        if invoices:
            invoices = json.loads(invoices)  
            ult_invoices = invoices[-1]["factura"] + 1
        else:
            ult_invoices = 1

        json_file = JsonFile(path+'/archivos/invoices.json')
        data = sale.getJson()
        data["factura"] = ult_invoices
        json_file.append(data)

    else:
        gotoxy(20,10+line);print("🤣 Venta Cancelada 🤣"+reset_color)    
    time.sleep(2)

  def update(self):
      
    while True:
        
        borrarPantalla()
        print('\033[1m\033[4m\033[97mActualizar datos de la factura.\033[0m')
        fact = input("\n\033[92m Ingresar número de factura, para actualizar los datos \033[0m\033[97m=> \033[0m").strip()
        if ' ' in fact or not fact.isdigit() or len(fact) != 1:
            print("\n\n\033[91m\033[4m🚨 ERROR: Incorrecto digite bien el número de la factura. --- 🚨 ERROR: Sin espacios en medio.\033[0m")
            time.sleep(2)
            continue
    
        fact = float(fact)
        
        json_file = JsonFile(path+'/archivos/invoices.json')
        clients_data = json_file.find("factura", fact)

        if clients_data:
            factura_encontrada = clients_data[0]  
            
            print('\n\033c', end='')
            gotoxy(2,1);print(green_color+"██"*50+reset_color)
            gotoxy(30,2);print(blue_color+"Registro de Venta")
            gotoxy(17,3);print(blue_color+Company.get_business_name())
            gotoxy(5,4);print(f"Factura#: {factura_encontrada['factura']} {' '*3} Fecha:{factura_encontrada['Fecha']}")
            gotoxy(66,4);print(" Subtotal: ", factura_encontrada["subtotal"])
            gotoxy(66,5);print(" Descuento: ", factura_encontrada["descuento"])
            gotoxy(66,6);print(" IVA     : ", factura_encontrada["iva"])
            gotoxy(66,7);print(" Total   : ", factura_encontrada["total"])
            gotoxy(10,6);print("Cliente: ", factura_encontrada["cliente"])
            gotoxy(2,8);print(green_color+"██"*50+reset_color) 
         
            input("\n\033[1m\033[4m\033[97mEnter si desea continuar => \033[0m\033[1m\033[4m\033[97m🚨 Datos que se van actualizar de la factura. ❗\033[0m")

            validar = Valida()
            
            borrarPantalla()
            print('\033c', end='')
            gotoxy(2,1);print(green_color+"██"*50+reset_color)
            gotoxy(30,2);print(blue_color+"Registro de Venta")
            gotoxy(17,3);print(blue_color+Company.get_business_name())
            gotoxy(5,4);print(f"Factura#: {factura_encontrada['factura']} {' '*3} Fecha:{datetime.datetime.now()}")
            gotoxy(66,4);print(" Subtotal:")
            gotoxy(66,5);print(" Descuento:")
            gotoxy(66,6);print(" IVA     :")
            gotoxy(66,7);print(" Total   :")
            gotoxy(10,6);print("Cedula:")
            dni = validar.solo_numeros("Error: Solo numeros",23,6)

            json_file = JsonFile(path+'/archivos/clients.json')
            clients_data = json_file.find("dni", dni)
            

            if not clients_data:
                gotoxy(35,6);print("Cliente no existe")
                return
            
            client = clients_data[0]
            cli = RegularClient(client["first_name"], client["last_name"], client["dni"], card=True) 
            sale = Sale(cli)
            
            gotoxy(35,6);print(cli.fullName())
            gotoxy(2,8);print(green_color+"██"*50+reset_color) 
            gotoxy(5,9);print(purple_color+"Linea") 
            gotoxy(12,9);print("Id_Articulo") 
            gotoxy(24,9);print("Descripcion") 
            gotoxy(38,9);print("Precio") 
            gotoxy(48,9);print("Cantidad") 
            gotoxy(58,9);print("Subtotal") 
            gotoxy(70,9);print("n->Terminar Venta)"+reset_color)

            follow = "s"
            line = 1
            
            while follow.lower() == "s":
                gotoxy(7,9+line);print(line)
                gotoxy(15,9+line);id_articulo = validar.solo_numeros("Error: Solo numeros",15,9+line)
                
                json_file_path = path + '/archivos/products.json'
                json_file = JsonFile(json_file_path)
                prods = json_file.find("id", id_articulo)
                
                if not prods:
                    gotoxy(24,9+line);print("Producto no existe")
                    time.sleep(1)
                    gotoxy(24,9+line);print(" "*20)
                    continue

                prods = prods[0]
                product = Product(prods["id"], prods["descripcion"], prods["precio"], prods["stock"])

                gotoxy(24,9+line);print(product.descrip)
                gotoxy(38,9+line);print(product.preci)

                qty = int(validar.solo_numeros("Error: Solo numeros",49,9+line))

                gotoxy(59,9+line);print(product.preci * qty)

                sale.add_detail(product, qty)
                gotoxy(76,4);print(round(sale.subtotal,2))
                gotoxy(76,5);print(round(sale.discount,2))
                gotoxy(76,6);print(round(sale.iva,2))
                gotoxy(76,7);print(round(sale.total,2))

                factura_encontrada["detalle"][0]["poducto"] = product.descrip
                factura_encontrada["detalle"][0]["precio"] = product.preci
                factura_encontrada["detalle"][0]["cantidad"] = qty

                gotoxy(74,9+line);follow = input() or "s"
                gotoxy(76,9+line);print(green_color+"✔"+reset_color)
                line += 1

            gotoxy(15,9+line);print(red_color+"Esta seguro de grabar la venta(s/n):")
            gotoxy(54,9+line);procesar = input().lower()
            
            if procesar == "s":
                gotoxy(15,10+line);print("😊 Venta Grabada satisfactoriamente 😊"+reset_color)
                json_file = JsonFile(path+'/archivos/invoices.json')
                invoices = json_file.read()
                
                if invoices:
                    invoices = json.loads(invoices)  
                    
                    for factura in invoices:
                        if factura["factura"] == fact:
                            factura["Fecha"] = datetime.datetime.now().strftime("%Y-%m-%d") 
                            factura["cliente"] = cli.fullName()  
                            factura["subtotal"] = sale.subtotal  
                            factura["descuento"] = sale.discount  
                            factura["iva"] = sale.iva 
                            factura["total"] = sale.total  
                            factura["detalle"] = factura_encontrada["detalle"] 
                            break
                else:
                    invoices = []

                json_file.write(json.dumps(invoices, indent=4))
            else:
                gotoxy(20,10+line);print("🤣 Venta Cancelada 🤣"+reset_color)    
                time.sleep(2)
                input("enter")
        else:
            input("Factura no encontrada, presione enter")

        break

  def delete(self):
      
        while True:
            borrarPantalla()
            print('\033[1m\033[4m\033[97mActualizar datos de la factura.\033[0m')
            fact = input("\n\033[92m Ingresar número de factura, para actualizar los datos \033[0m\033[97m=> \033[0m").strip()
            if ' ' in fact or not fact.isdigit() or len(fact) != 1:
                print("\n\033[91m\033[4m🚨 ERROR: Incorrecto, digite correctamente el número de la factura. --- 🚨 ERROR: Sin espacios en medio.\033[0m")
                time.sleep(2)
                continue
            
            fact = float(fact)
            
            json_file = JsonFile(path+'/archivos/invoices.json')
            clients_data = json_file.find("factura", fact)
            
            if not clients_data:
                print("\n\033[91m\033[4m❌ ERROR: No se encontró la factura. Por favor, vuelva a intentar.\033[0m")
                time.sleep(2)
                continue
            
            factura_encontrada = clients_data[0]
            
            print('\n\033c', end='')
            gotoxy(2,1);print(green_color+"██"*50+reset_color)
            gotoxy(30,2);print(blue_color+"Registro de Venta")
            gotoxy(17,3);print(blue_color+Company.get_business_name())
            gotoxy(5,4);print(f"Factura#: {factura_encontrada['factura']} {' '*3} Fecha:{factura_encontrada['Fecha']}")
            gotoxy(66,4);print(" Subtotal: ", factura_encontrada["subtotal"])
            gotoxy(66,5);print(" Descuento: ", factura_encontrada["descuento"])
            gotoxy(66,6);print(" IVA     : ", factura_encontrada["iva"])
            gotoxy(66,7);print(" Total   : ", factura_encontrada["total"])
            gotoxy(10,6);print("Cliente: ", factura_encontrada["cliente"])
            gotoxy(2,8);print(green_color+"██"*50+reset_color)
            
            print("\n\033[1;97mPresione \033[4;97mESC\033[0;1;97m para cancelar o \033[4;97mEnter\033[0;1;97m para eliminar facturar.\033[0m")

            while True:
                if msvcrt.kbhit():
                    entrada = msvcrt.getch()
                    if entrada == b"\x1b":
                        print("\n\033[91;4m❌ Operación cancelada.\033[0m")
                        time.sleep(1)
                        break

                    elif entrada == b"\r":
                        fact = float(fact)
                        json_file_path = path + '/archivos/invoices.json'
                        
                        with open(json_file_path, 'r+') as file:
                            invoices = json.load(file)
                            
                            for i, factura in enumerate(invoices):
                                if factura["factura"] == fact:
                                    del invoices[i]
                                    
                            file.seek(0)
                            json.dump(invoices, file, indent=4)
                            file.truncate()
                        break
            break
                                
  def consult(self):
    facturas = loadInvoices()
    while True:
        borrarPantalla()
        print('\033[1m\033[4m\033[97mConsultar una factura o todas las facturas.\033[0m')
        accion = input("\n\033[92m Presione Enter consultar unicamente una factura o Fac para todas las \033[0m\033[97m=> \033[0m").strip()
        
        if accion == "":
            borrarPantalla()
            print('\033[1m\033[4m\033[97mConsultar datos de la factura.\033[0m')
            numero = input("\n\033[92m Ingresar el número de la factura \033[0m\033[97m=> \033[0m").strip()
            if not numero.isdigit():
                print("\033[91m\033[4m🚨 ERROR: Incorrecto, digite bien el número de la factura. --- 🚨 ERROR: Sin espacios en medio.\033[0m")
                time.sleep(2)
                continue
            else:
                print()
                factura = findInvoice(facturas, int(numero))
                if factura is not None:
                    showInvoice(factura)
                else:
                    print("La factura no fue encontrada.")
            input(f"\n\033[1m\033[97mPresione Enter para salir.\033[0m")
            break
        elif accion == "fac":
            while True:
                borrarPantalla()
                print('\033[1m\033[4m\n\033[97mConsulta de todas las facturas.\033[0m')
                showInvoices(facturas)
                orden = input("\n\033[92m Max para > a < y Min para < a >  \033[0m\033[97m=> \033[0m").strip()
                if orden in ['max', 'min']:
                    facturas = sortInvoices(facturas, orden)
                    showInvoices(facturas)  
                elif orden == 's':
                    break
                else:
                    print("\033[91m\033[4m🚨 ERROR: Orden no reconocido. Por favor, intente de nuevo.\033[0m")
                    time.sleep(2)
        else:
            print("\033[91m\033[4m🚨 ERROR: Acción no reconocida. Por favor, intente de nuevo.\033[0m")
            time.sleep(2)
            continue

opc = ''
while opc != '4':
    borrarPantalla()
    menu_main = Menu("💻 Menu Facturacion", [" 1) Clientes", " 2) Productos", " 3) Ventas", " 4) Salir"], 20, 10)
    opc = menu_main.menu()
    if opc == "1":
        opc1 = ''
        while opc1 != '5':
            borrarPantalla()
            menu_clients = Menu("👥 Menu Clientes", [" 1) Ingresar", " 2) Actualizar", " 3) Eliminar", " 4) Consultar", " 5) Salir"], 10, 10)
            opc1 = menu_clients.menu()

            if opc1 == "1":
                borrarPantalla()
                print("\033[1;4;97m🚨 Seguro de agregar un nuevo cliente.\033[1;4;31m❓\033[0m")
                print("\n\033[1;97mPresione \033[4;97mESC\033[0;1;97m para cancelar o \033[4;97mEnter\033[0;1;97m para continuar.\033[0m")
                
                while True:
                    if msvcrt.kbhit():  
                        entrada = msvcrt.getch()  
                        if entrada == b"\x1b": 
                            print("\n\033[91;4m❌ Operación cancelada.\033[0m")
                            time.sleep(2)
                            break
                        elif entrada == b"\r":  
                            crud_clients = CrudClients()
                            crud_clients.create()
                            break
                        else:
                            print("\n\033[91m\033[4m🚨 Opción inválida. Presione ESC para cancelar o Enter para continuar.\033[0m")
                time.sleep(2)

            elif opc1 == "2":
                borrarPantalla()
                print("\033[1;4;97m🚨 Seguro de actualizar datos del cliente.\033[1;4;31m❓\033[0m")
                print("\n\033[1;97mPresione \033[4;97mESC\033[0;1;97m para cancelar o \033[4;97mEnter\033[0;1;97m para continuar.\033[0m")
                
                while True:
                    if msvcrt.kbhit():
                        entrada = msvcrt.getch()
                        if entrada == b"\x1b":
                            print("\n\033[91;4m❌ Operación cancelada.\033[0m")
                            time.sleep(2)
                            break
                        elif entrada == b"\r":
                            crud_clients = CrudClients()
                            crud_clients.update()
                            break
                        else:
                            print("\n\033[91m\033[4m🚨 Opción inválida. Presione ESC para cancelar o Enter para continuar.\033[0m")
                time.sleep(2)

            elif opc1 == "3":
                borrarPantalla()
                print("\033[1;4;97m🚨 Seguro de eliminar datos del cliente.\033[1;4;31m❓\033[0m")
                print("\n\033[1;97mPresione \033[4;97mESC\033[0;1;97m para cancelar o \033[4;97mEnter\033[0;1;97m para continuar.\033[0m")
                
                while True:
                    if msvcrt.kbhit():
                        entrada = msvcrt.getch()
                        if entrada == b"\x1b":
                            print("\n\033[91;4m❌ Operación cancelada.\033[0m")
                            time.sleep(2)
                            break
                        elif entrada == b"\r":
                            crud_clients = CrudClients()
                            crud_clients.delete()
                            break
                        else:
                          print("\n\033[91m\033[4m🚨 Opción inválida. Presione ESC para cancelar o Enter para continuar.\033[0m")
                          time.sleep(2)

            elif opc1 == "4":
                borrarPantalla()
                print("\033[1;4;97m🚨 Consulta datos del cliente.\033[1;4;31m ❗\033[0m")
                print("\n\033[1;97mPresione \033[4;97mESC\033[0;1;97m para cancelar o \033[4;97mEnter\033[0;1;97m para continuar.\033[0m")
                
                while True:
                    if msvcrt.kbhit():
                        entrada = msvcrt.getch()
                        if entrada == b"\x1b":
                            print("\n\033[91;4m❌ Operación cancelada.\033[0m")
                            time.sleep(1)
                            break
                        elif entrada == b"\r":
                            crud_clients = CrudClients()
                            crud_clients.consult()
                            break
                        else:
                            print("\n\033[91m\033[4m🚨 Opción inválida. Presione ESC para cancelar o Enter para continuar.\033[0m")
                time.sleep(2)
                     
    elif opc == "2":
        opc2 = ''
        while opc2 != '5':
            borrarPantalla()
            menu_products = Menu("🏷️ Menu Productos", [" 1) Ingresar", " 2) Actualizar", " 3) Eliminar", " 4) Consultar", " 5) Salir"], 20, 10)
            opc2 = menu_products.menu()
            if opc2 == "1":
                borrarPantalla()
                print("\033[1;4;97m🚨 Seguro de agregar un nuevo producto.\033[1;4;31m❓\033[0m")
                print("\n\033[1;97mPresione \033[4;97mESC\033[0;1;97m para cancelar o \033[4;97mEnter\033[0;1;97m para continuar.\033[0m")
                
                while True:
                    if msvcrt.kbhit():  
                        entrada = msvcrt.getch()  
                        if entrada == b"\x1b": 
                            print("\n\033[91;4m❌ Operación cancelada.\033[0m")
                            time.sleep(2)
                            break
                        elif entrada == b"\r":  
                            crud_productos = CrudProducts()
                            crud_productos.create()
                            break
                        else:
                            print("\n\033[91m\033[4m🚨 Opción inválida. Presione ESC para cancelar o Enter para continuar.\033[0m")
                time.sleep(2)

            elif opc2 == "2":
                borrarPantalla()
                print("\033[1;4;97m🚨 Seguro de actualizar los datos de un producto.\033[1;4;31m❓\033[0m")
                print("\n\033[1;97mPresione \033[4;97mESC\033[0;1;97m para cancelar o \033[4;97mEnter\033[0;1;97m para continuar.\033[0m")
                
                while True:
                    if msvcrt.kbhit():  
                        entrada = msvcrt.getch()  
                        if entrada == b"\x1b": 
                            print("\n\033[91;4m❌ Operación cancelada.\033[0m")
                            time.sleep(2)
                            break
                        elif entrada == b"\r":  
                            crud_productos = CrudProducts()
                            crud_productos.update()
                            break
                        else:
                            print("\n\033[91m\033[4m🚨 Opción inválida. Presione ESC para cancelar o Enter para continuar.\033[0m")
                time.sleep(2)
                
            elif opc2 == "3":
                borrarPantalla()
                print("\033[1;4;97m🚨 Seguro de eliminar los datos de un producto.\033[1;4;31m❓\033[0m")
                print("\n\033[1;97mPresione \033[4;97mESC\033[0;1;97m para cancelar o \033[4;97mEnter\033[0;1;97m para continuar.\033[0m")
                
                while True:
                    if msvcrt.kbhit():  
                        entrada = msvcrt.getch()  
                        if entrada == b"\x1b": 
                            print("\n\033[91;4m❌ Operación cancelada.\033[0m")
                            time.sleep(2)
                            break
                        elif entrada == b"\r":  
                            crud_productos = CrudProducts()
                            crud_productos.delete()
                            break
                        else:
                            print("\n\033[91m\033[4m🚨 Opción inválida. Presione ESC para cancelar o Enter para continuar.\033[0m")

            elif opc2 == "4":
                borrarPantalla()
                print("\033[1;4;97m🚨 Consulta datos del producto.\033[1;4;31m❓\033[0m")
                print("\n\033[1;97mPresione \033[4;97mESC\033[0;1;97m para cancelar o \033[4;97mEnter\033[0;1;97m para continuar.\033[0m")
                
                while True:
                    if msvcrt.kbhit():  
                        entrada = msvcrt.getch()  
                        if entrada == b"\x1b": 
                            print("\n\033[91;4m❌ Operación cancelada.\033[0m")
                            time.sleep(2)
                            break
                        elif entrada == b"\r":  
                            crud_productos = CrudProducts()
                            crud_productos.consult()
                            break
                        else:
                            print("\n\033[91m\033[4m🚨 Opción inválida. Presione ESC para cancelar o Enter para continuar.\033[0m")

    elif opc == "3":
        opc3 = ''
        while opc3 != '5':
            borrarPantalla()
            sales = CrudSales()
            menu_sales = Menu("📠 Menu Ventas", [" 1) Registro Venta", " 2) Modificar", " 3) Eliminar", " 4) Consultar", " 5) Salir"], 20, 10)
            opc3 = menu_sales.menu()
            if opc3 == "1":
                borrarPantalla()
                print("\033[1;4;97m🚨 Ingresar datos a la factura.\033[1;4;31m❓\033[0m")
                print("\n\033[1;97mPresione \033[4;97mESC\033[0;1;97m para cancelar o \033[4;97mEnter\033[0;1;97m para continuar.\033[0m")
                
                while True:
                    if msvcrt.kbhit():  
                        entrada = msvcrt.getch()  
                        if entrada == b"\x1b": 
                            print("\n\033[91;4m❌ Operación cancelada.\033[0m")
                            time.sleep(2)
                            break
                            
                        elif entrada == b"\r":  
                            sales.create()
                            break
                            
                        else:
                            print("\n\033[91m\033[4m🚨 Opción inválida. Presione ESC para cancelar o Enter para continuar.\033[0m")
                 
                  
            elif opc3 == "2":
                borrarPantalla()
                print("\033[1;4;97m🚨 Actualizar datos de la factura.\033[1;4;31m❓\033[0m")
                print("\n\033[1;97mPresione \033[4;97mESC\033[0;1;97m para cancelar o \033[4;97mEnter\033[0;1;97m para continuar.\033[0m")
                
                while True:
                    if msvcrt.kbhit():  
                        entrada = msvcrt.getch()  
                        if entrada == b"\x1b": 
                            print("\n\033[91;4m❌ Operación cancelada.\033[0m")
                            time.sleep(2)
                            break
                            
                        elif entrada == b"\r":  
                            sales.update()
                            break
                            
                        else:
                            print("\n\033[91m\033[4m🚨 Opción inválida. Presione ESC para cancelar o Enter para continuar.\033[0m")
               
            elif opc3 == "3":
                borrarPantalla()
                print("\033[1;4;97m🚨 Eliminar datos de la factura.\033[1;4;31m❓\033[0m")
                print("\n\033[1;97mPresione \033[4;97mESC\033[0;1;97m para cancelar o \033[4;97mEnter\033[0;1;97m para continuar.\033[0m")
                
                while True:
                    if msvcrt.kbhit():  
                        entrada = msvcrt.getch()  
                        if entrada == b"\x1b": 
                            print("\n\033[91;4m❌ Operación cancelada.\033[0m")
                            time.sleep(2)
                            break
                            
                        elif entrada == b"\r":  
                            sales.delete()
                            break
                            
                        else:
                            print("\n\033[91m\033[4m🚨 Opción inválida. Presione ESC para cancelar o Enter para continuar.\033[0m")
                            
            elif opc3 == "4":
                borrarPantalla()
                print("\033[1;4;97m🚨 Consultando datos de la factura.\033[1;4;31m❓\033[0m")
                print("\n\033[1;97mPresione \033[4;97mESC\033[0;1;97m para cancelar o \033[4;97mEnter\033[0;1;97m para continuar.\033[0m")
                
                while True:
                    if msvcrt.kbhit():  
                        entrada = msvcrt.getch()  
                        if entrada == b"\x1b": 
                            print("\n\033[91;4m❌ Operación cancelada.\033[0m")
                            time.sleep(2)
                            break
                            
                        elif entrada == b"\r":  
                            sales.consult()
                            break
                            
                        else:
                            print("\n\033[91m\033[4m🚨 Opción inválida. Presione ESC para cancelar o Enter para continuar.\033[0m")
                time.sleep(2)

input("Presione una tecla para salir...")
borrarPantalla()