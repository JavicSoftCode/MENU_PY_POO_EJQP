import os
import json
import time
import msvcrt  
import datetime
from abc import ABC
from colorama import init, Fore, Style

from sales import Sale
from iCrud import ICrud
from product import Product
from company import Company
from functools import reduce
from tabulate import tabulate
from components import Menu, Valida
from utilities import borrarPantalla, gotoxy
from customer import RegularClient, VipClient, JsonFile
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

def loadClients():
    with open('ventas_python/archivos/clients.json', 'r') as f:
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

def validateCedula(dni):
    if ' ' in dni or not dni.isdigit() or len(dni) != 10:
        return False
    else:
        suma = 0
        for i, digito in enumerate(dni[:-1]):
            multiplicador = 2 if i % 2 == 0 else 1
            producto = int(digito) * multiplicador
            if producto >= 10:
                producto -= 9
            suma += producto
        residuo = suma % 10
        if residuo == 0:
            residuo = 10
        verificador = 10 - residuo
        return verificador == int(dni[-1])
    
class CrudClients(ICrud, ABC):
  @message_decorator
  def create(self):
    json_file_path = path + '/archivos/clients.json'
    json_file = JsonFile(json_file_path)
    
    print('\033[1m\033[4m\033[97mRegistrando cliente.\033[0m')

    dni = input("\n\033[92m Ingresar número de cédula \033[0m\033[97m=> \033[0m").strip()
    if not validateCedula(dni):
        return "Cédula incorrecta. Asegúrese de ingresar un número de cédula válido con 10 dígitos numéricos completos y sin espacios en medio."

    data = json_file.read()

    clients = json.loads(data) if data else []

    existing_client = list(map(lambda client: client["dni"] == dni, clients))

    if any(existing_client):
        return " No se puede registrar el cliente porque ya existe uno con esa cédula."

    first_name = input("\n\033[92m Ingresar nombres completos \033[0m\033[97m=> \033[0m").strip()
    if not all(c.isalpha() or c.isspace() for c in first_name) or len(first_name.split()) != 2 or any(len(name) < 3 for name in first_name.split()):
        return "Ingresar nombres completos. Cada nombre debe tener más de 2 caracteres. Números y símbolos, NO."

    last_name = input("\n\033[92m Ingresar apellidos completos \033[0m\033[97m=> \033[0m").strip()
    if not all(c.isalpha() or c.isspace() for c in last_name) or len(last_name.split()) != 2 or any(len(lastname) < 3 for lastname in last_name.split()):
        return "Ingresar apellidos completos. Cada apellido debe tener más de 2 caracteres. Números y símbolos, NO."

    cliente = input("\n\033[92m Cliente : Regular o Vip \033[0m\033[97m=> \033[0m").lower().strip()
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

    if not validateCedula(dni):
        return "🚨 ERROR: Formato de cédula incorrecto. Deben ser 10 dígitos numéricos completos, sin espacios en medio."

    old_clients = json.loads(json_file.read() or '[]')
    found_client = next((cliente for cliente in old_clients if cliente['dni'] == dni), None)

    if found_client is None:
        return "🚷 Cliente no encontrado."

    borrarPantalla()

    if 'discount' in found_client:
        client = RegularClient(found_client['first_name'], found_client['last_name'], found_client['dni'], True)
    else:
        client = VipClient(found_client['first_name'], found_client['last_name'], found_client['dni'])
        client.limit = found_client['limit']  

    client.show()

    print("\n\033[97m\033[1m\033[4mEnter para actualizar o ESC para cancelar \033[0m")

    while True:
        if msvcrt.kbhit():
            entrada = msvcrt.getch()

            if entrada == b"\x1b":
                print()
                return "\033[91;4m❌ Actualización cancelada.\033[0m"
                time.sleep(1)
                break

            elif entrada == b"\r":
                borrarPantalla()
                print('\n\033[1m\033[4m\033[97mActualizando datos del cliente.\033[0m')

                while True:
                    new_dni = input("\n\033[92m Ingresar número de cédula \033[0m\033[97m=> \033[0m").strip()
                    if not validateCedula(new_dni):
                        return "🚨 Formato incorrecto. Debe ser de 10 dígitos numéricos completos."
                    if new_dni != found_client["dni"]:
                        return "🚨 No se puede cambiar el DNI. Debe ser el mismo que el original."
                    break

                while True:
                    first_name = input("\n\033[92m Ingresar nombres completos \033[0m\033[97m=> \033[0m").strip()
                    if not all(c.isalpha() or c.isspace() for c in first_name) or len(first_name.split()) != 2 or any(len(name) < 3 for name in first_name.split()):
                        return "🚨 Nombres incorrectos. Deben ser dos nombres completos."
                    break

                while True:
                    last_name = input("\n\033[92m Ingresar apellidos completos \033[0m\033[97m=> \033[0m").strip()
                    if not all(c.isalpha() or c.isspace() for c in last_name) or len(last_name.split()) != 2 or any(len(lastname) < 3 for lastname in last_name.split()):
                        return "🚨 Apellidos incorrectos. Deben ser dos apellidos completos."
                    break

                while True:
                    cliente = input("\n\033[92m Cliente : Regular o Vip \033[0m\033[97m=> \033[0m").lower()
                    if cliente not in ["regular", "vip"]:
                        return "🚨 Debe ser 'Regular' o 'Vip'."
                    break

                if cliente == "regular":
                    client = RegularClient(new_dni, first_name, last_name, True)
                    if "limit" in found_client:
                        del found_client["limit"]
                    found_client["discount"] = client.discount

                elif cliente == "vip":
                    client = VipClient(new_dni, first_name, last_name)
                    while True:
                        try:
                            limite_vip = float(input("\n\033[92m Ingresar el límite de crédito \033[0m\033[97m=> \033[0m"))
                            if limite_vip < 10000:
                                limite_vip = 10000
                            elif limite_vip > 20000:
                                limite_vip = 20000
                            client.limit = limite_vip
                            break
                        except ValueError:
                            return "🚨 El valor debe ser numérico."
                    if "discount" in found_client:
                        del found_client["discount"]
                    found_client["limit"] = client.limit

                found_client["first_name"] = first_name
                found_client["last_name"] = last_name
                found_client["dni"] = new_dni

                json_file.write(json.dumps(old_clients, indent=4))

                print ("\n\033[92;4m✅ Actualización completada.\033[0m")
                time.sleep(2)
                break
                
  @message_decorator
  def delete(self):
    json_file_path = path + '/archivos/clients.json'
    json_file = JsonFile(json_file_path)

    print('\n\033[1m\033[4m\033[97mEliminará los datos del cliente.\033[0m')

    dni = input("\n\033[92m Ingresar número de cédula, para eliminar los datos del cliente \033[0m\033[97m=> \033[0m").strip()

    if not validateCedula(dni):
        return "🚨 Error en la cédula. Asegúrese de que tenga 10 dígitos numéricos completos sin espacios."

    old_clients = json.loads(json_file.read() or "[]")

    client_to_delete = next((client for client in old_clients if client["dni"] == dni), None)

    if not client_to_delete:
        return "🚷 Cliente no encontrado."

    borrarPantalla()
    print("\033[97m\033[1m\033[4m✅ Verificar Datos\033[0m")
    print("\n\033[92m DNI \033[97m=>\033[0m", dni)
    print("\033[92m Nombres \033[97m=>\033[0m", client_to_delete["first_name"])
    print("\033[92m Apellidos \033[97m=>\033[0m", client_to_delete["last_name"])

    if "limit" in client_to_delete:
        print("\033[92m Límite de crédito del cliente mayorista \033[97m=>\033[0m", client_to_delete["limit"])
    elif "discount" in client_to_delete:
        print("\033[92m Descuento del cliente minorista \033[97m=>\033[0m", client_to_delete["discount"])

    aceptar = input("\n\033[97m\033[1m\033[4m¿Eliminar los datos del cliente? (YES/NO) => \033[0m").lower()

    if aceptar == 'yes':
        print("\n⬇️")
        print("\033[97m\033[4m🟢 Datos del cliente eliminados.\033[0m")
        updated_clients = list(filter(lambda client: client["dni"] != dni, old_clients))
        json_file.write(json.dumps(updated_clients, indent=4))
        time.sleep(2)
    else:
        print("\n⬇️")
        print("\033[97m\033[4m🔴 Eliminación cancelada.\033[0m")
        time.sleep(2)

  @message_decorator
  def consult(self):
    json_file_path = path + '/archivos/clients.json'
    json_file = JsonFile(json_file_path)

    while True:
        borrarPantalla()
        print('\033[1m\033[4m\033[97mConsulta datos del cliente.\033[0m')

        accion = input("\n\033[92m Presione Enter para consultar un cliente específico, 'all' para mostrar todos o 's' para salir: \033[0m\033[97m=> \033[0m").strip()

        if accion == "":
            dni = input("\n\033[92m Ingresar número de cédula para consultar los datos del cliente \033[0m\033[97m=> \033[0m").strip()

            if not validateCedula(dni):
                print("Formato incorrecto: La cédula debe contener 10 dígitos numéricos completos.")
                input("\nPresione Enter para continuar.")
                continue

            old_clients = json.loads(json_file.read() or "[]")

            if not old_clients:
                print("JSON VACÍO")
                input("\nPresione Enter para continuar.")
                continue

            found_clients = list(filter(lambda client: client["dni"] == dni, old_clients))

            if found_clients:
                borrarPantalla()
                print("\033[97m\033[1m\033[4m✅ Consultando Datos del Cliente\033[0m")
                print()
                for client_data in found_clients:
                    if "discount" in client_data:
                        client = RegularClient(client_data.get("first_name", ""), client_data.get("last_name", ""), client_data["dni"], True)
                        tipo_cliente = "Cliente Minorista"
                        dato_especial = client.discount
                        etiqueta_especial = "Descuento"
                    elif "limit" in client_data:
                        client = VipClient(client_data.get("first_name", ""), client_data.get("last_name", ""), client_data["dni"])
                        client.limit = client_data["limit"]
                        tipo_cliente = "Cliente VIP"
                        dato_especial = client.limit
                        etiqueta_especial = "Límite de crédito"

                    data = [
                        ["DNI", "Nombres", "Apellidos", etiqueta_especial, "Tipo de Cliente"],
                        [client.dni, client.first_name, client.last_name, dato_especial, tipo_cliente]
                    ]
                    print(tabulate(data, tablefmt='grid'))
                input("\n\033[1;4;97m⬅️  Enter para salir\033[0m")
                continue  # Regresar al menú principal

            else:
                print("\n\033[1;4;97m🔴 No se encontró al cliente.\033[0m")
                input("\nPresione Enter para continuar.")
                continue

        elif accion == "all":
            old_clients = json.loads(json_file.read() or "[]")

            if not old_clients:
                print("JSON VACÍO")
                input("\nPresione Enter para continuar.")
                continue

            borrarPantalla()
            print("\033[97m\033[1m\033[4m✅ Consultando Todos los Clientes\033[0m")
            print()
            for client_data in old_clients:
                if "discount" in client_data:
                    client = RegularClient(client_data.get("first_name", ""), client_data.get("last_name", ""), client_data["dni"], True)
                    tipo_cliente = "Cliente Minorista"
                    dato_especial = client.discount
                    etiqueta_especial = "Descuento"
                elif "limit" in client_data:
                    client = VipClient(client_data.get("first_name", ""), client_data.get("last_name", ""), client_data["dni"])
                    client.limit = client_data["limit"]
                    tipo_cliente = "Cliente VIP"
                    dato_especial = client.limit
                    etiqueta_especial = "Límite de crédito"

                data = [
                    ["DNI", "Nombres", "Apellidos", etiqueta_especial, "Tipo de Cliente"],
                    [client.dni, client.first_name, client.last_name, dato_especial, tipo_cliente]
                ]
                print(tabulate(data, tablefmt='grid'))

            while True:
                action = input("\n\033[92mEscriba 'vip' para ver solo VIP, 'regular' para ver solo regulares, o 's' para salir: \033[0m\033[97m=> \033[0m").strip()

                if action == "vip":
                    vip_clients = [client for client in old_clients if "limit" in client]

                    if not vip_clients:
                        print("No se encontraron clientes VIP.")
                        input("\nPresione Enter para continuar.")
                        continue

                    borrarPantalla()
                    print("\033[97m\033[1m\033[4m✅ Consultando Clientes VIP\033[0m")
                    print()
                    for client_data in vip_clients:
                        client = VipClient(client_data.get("first_name", ""), client_data.get("last_name", ""), client_data["dni"])
                        client.limit = client_data["limit"]
                        data = [
                            ["DNI", "Nombres", "Apellidos", "Límite de crédito", "Tipo de Cliente"],
                            [client.dni, client.first_name, client.last_name, client.limit, "Cliente VIP"]
                        ]
                        print(tabulate(data, tablefmt='grid'))
                    input("\n\033[1;4;97m⬅️  Enter para continuar\033[0m")
                    continue  

                elif action == "regular":
                    regular_clients = [client for client in old_clients if "discount" in client]

                    if not regular_clients:
                        print("No se encontraron clientes regulares.")
                        input("\nPresione Enter para continuar.")
                        continue

                    borrarPantalla()
                    print("\033[97m\033[1m\033[4m✅ Consultando Clientes Regulares\033[0m")
                    print()
                    for client_data in regular_clients:
                        client = RegularClient(client_data.get("first_name", ""), client_data.get("last_name", ""), client_data["dni"], True)
                        data = [
                            ["DNI", "Nombres", "Apellidos", "Descuento", "Tipo de Cliente"],
                            [client.dni, client.first_name, client.last_name, client.discount, "Cliente Minorista"]
                        ]
                        print(tabulate(data, tablefmt='grid'))
                    input("\n\033[1;4;97m⬅️  Enter para continuar\033[0m")
                    continue 

                elif action == "s":
                    break  

                else:
                    print("\033[91m\033[4m🚨 ERROR: Acción no reconocida. Por favor, intente de nuevo.\033[0m")
                    input("\nPresione Enter para continuar.")
                    continue  

            break  

        elif accion == "s":
            break  

        else:
            print("\033[91m\033[4m🚨 ERROR: Acción no reconocida. Por favor, intente de nuevo.\033[0m")
            input("\nPresione Enter para continuar.")
            continue  

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

        descripcion_lower = descripcion.lower()
        if any(product["descripcion"].lower() == descripcion_lower for product in products_data):
            return "Ya existe un producto con esta descripción. --- 🚨 ERROR: No se puede registrar el producto."

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

    found_product = next((product for product in products_data if product["id"] == id), None)

    if found_product is None:
        return "Producto no encontrado. Verifique el ID e intente nuevamente."
    
    borrarPantalla()
    print('\033[1m\033[4m\033[97mVerificación de datos del producto.\033[0m')

    print(f"\033[92m\n ID \033[97m=> \033[0m {id} \n\033[92m Descripción \033[97m=> \033[0m {found_product['descrip']}\n\033[92m Precio \033[97m=> \033[0m {found_product['preci']}\n\033[92m Stock \033[97m=> \033[0m {found_product['stock']}")
    
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

                while True:
                    descripcion = input("\n\033[92m Ingresar descripción del producto \033[0m\033[97m=> \033[0m").strip()
                    if not all(c.isalpha() or c.isspace() for c in descripcion) or any(len(descrip) < 3 for descrip in descripcion.split()):
                        return "🚨 ERROR: Cada nombre del producto debe tener > 2 caracteres y no debe contener números o símbolos."
                    else:
                        # Verificar si la descripción ya existe en otro producto
                        descripcion_lower = descripcion.lower()
                        if any(product["descrip"].lower() == descripcion_lower and product["id"] != id for product in products_data):
                            return "🚨 ERROR: Ya existe un producto con esta descripción."
                        else:
                            break  # Si la descripción es válida, salir del bucle

                while True:
                    precio = input("\n\033[92m Ingresar precio del producto \033[0m\033[97m=> \033[0m").strip()
                    if not precio.replace('.', '', 1).replace('-', '', 1).isdigit() or float(precio) < 0:
                        return "🚨 ERROR: Ingresar datos numéricos para el precio."
                    else:
                        precio = float(precio)
                        break  # Si el precio es válido, salir del bucle

                while True:
                    stock = input("\n\033[92m Ingresar el stock del producto \033[0m\033[97m=> \033[0m").strip()
                    if not stock.replace('.', '', 1).replace('-', '', 1).isdigit() or float(stock) < 0:
                        return "🚨 ERROR: Ingresar datos numéricos para el stock."
                    else:
                        stock = int(stock)
                        break  # Si el stock es válido, salir del bucle

                borrarPantalla()
                print("\033[97m\033[1m\033[4m✅ Verificar Datos Actualizados\033[0m")
                print(f"\n\033[92m ID \033[0m\033[97m =>\033[0m {id}\n\033[92m Descripción\033[0m\033[97m =>\033[0m {descripcion}\n\033[92m Precio $\033[0m\033[97m =>\033[0m {precio}\n\033[92m Stock\033[0m\033[97m =>\033[0m {stock}")
                aceptar = input("\n\033[97m\033[1m\033[4m¿Aceptar y guardar? (YES/NO) => \033[0m").lower()

                if aceptar == 'yes':
                    # Actualizar los valores en la lista de productos
                    for product in products_data:
                        if product["id"] == id:
                            product["descrip"] = descripcion
                            product["preci"] = precio
                            product["stock"] = stock
                            break

                    # Escribir los datos actualizados de nuevo al archivo JSON
                    json_file.write(json.dumps(products_data))

                    print("\n⬇️")
                    print("\033[97m\033[4m🟢 Datos del producto actualizados.\033[0m")
                    break
                else:
                    print("\n⬇️")
                    print("\033[97m\033[4m🔴 Actualización cancelada.\033[0m")
                    break

            else:
                return "🚨 ERROR: Opción inválida. Presione ESC para cancelar o Enter para continuar."
            
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
        print("\n\033[92m ID \033[97m=>\033[0m", id)
        print("\033[92m Descripción \033[97m=>\033[0m", product_to_delete["descrip"])
        print("\033[92m Precio \033[97m=>\033[0m", product_to_delete["preci"])
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
    json_file_path_products = path + '/archivos/products.json'
    json_file_path_invoices = path + '/archivos/invoices.json'
    
    json_file_products = JsonFile(json_file_path_products)
    json_file_invoices = JsonFile(json_file_path_invoices)

    while True:
        borrarPantalla()
        print('\033[1m\033[4m\033[97mConsulta de productos.\033[0m')

        accion = input("\n\033[92m Presione Enter para consultar un producto específico, 'all' para mostrar todos, 'mayor' para productos más vendidos, 'menor' para productos menos vendidos, 'stock' para productos sin stock o 's' para salir: \033[0m\033[97m=> \033[0m").strip().lower()

        borrarPantalla()
        print('\033[1m\033[4m\033[97mConsulta de productos.\033[0m')

        if accion == "":
            id_producto = input("\n\033[92m Ingresar ID del producto para consultar sus datos \033[0m\033[97m=> \033[0m").strip()

            if not id_producto.isdigit():
                print("\n🔴 ERROR: El ID del producto debe ser un número.")
                input("\nPresione Enter para continuar.")
                continue

            old_products = json.loads(json_file_products.read() or '[]')

            if not old_products:
                print("⚠️ JSON VACÍO.")
                input("\nPresione Enter para continuar.")
                continue

            found_products = list(filter(lambda product: product["id"] == id_producto, old_products))

            if found_products:
                borrarPantalla()
                print("\033[97m\033[1m\033[4m✅ Consultando Datos del Producto\033[0m")
                print()

                headers = ["ID", "Descripción", "Precio", "Stock"]
                table = [[p["id"], p["descrip"], p["preci"], p["stock"]] for p in found_products]
                print(tabulate(table, headers, tablefmt="pretty"))
            else:
                print("\n🔴 No se encontró el producto con el ID proporcionado.")
            
            input("\n\033[1;4;97m⬅️  Enter para continuar\033[0m")
            continue  # Regresar al menú principal

        elif accion == "all":
            old_products = json.loads(json_file_products.read() or '[]')

            if not old_products:
                print("⚠️ JSON VACÍO.")
                input("\nPresione Enter para continuar.")
                continue

            borrarPantalla()
            print("\033[97m\033[1m\033[4m✅ Consultando Todos los Productos\033[0m")
            print()

            headers = ["ID", "Descripción", "Precio", "Stock"]
            table = [[p["id"], p["descrip"], p["preci"], p["stock"]] for p in old_products]
            print(tabulate(table, headers, tablefmt="pretty"))

            while True:
                accion = input("\n\033[92m Escriba 'mayor' para mostrar productos más vendidos, 'menor' para productos con bajas ventas, 'stock' para productos sin stock o 's' para salir: \033[0m\033[97m=> \033[0m").strip().lower()
                if accion in ["mayor", "menor", "stock", "s"]:
                    break
                else:
                    print("\033[91m\033[4m🚨 ERROR: Acción no reconocida. Por favor, intente de nuevo.\033[0m")

        if accion == "mayor":
            while True:
                try:
                    min_sales = int(input("\n\033[92m Ingrese la cantidad mínima de ventas: \033[0m\033[97m=> \033[0m").strip())
                    if min_sales < 0:
                        raise ValueError
                    break
                except ValueError:
                    print("\n🔴 ERROR: La cantidad mínima de ventas debe ser un número entero positivo.")

            old_products = json.loads(json_file_products.read() or '[]')
            old_invoices = json.loads(json_file_invoices.read() or '[]')

            if not old_products or not old_invoices:
                print("⚠️ JSON VACÍO.")
                input("\nPresione Enter para continuar.")
                continue

            # Calcular las ventas totales por producto
            sales = {}
            for invoice in old_invoices:
                for item in invoice["detalle"]:
                    product_name = item["producto"]
                    quantity = item["cantidad"]
                    # Buscar el ID del producto por su nombre
                    product_id = next((p["id"] for p in old_products if p["descrip"] == product_name), None)
                    if product_id:
                        if product_id in sales:
                            sales[product_id] += quantity
                        else:
                            sales[product_id] = quantity

            # Filtrar productos con ventas mayores o iguales al valor mínimo
            products_vendidos = [p for p in old_products if sales.get(p["id"], 0) >= min_sales]

            # Mostrar ventas calculadas en tabla
            headers_sales = ["ID Producto", "Ventas", "Total Ventas"]
            table_sales = [[p["id"], sales.get(p["id"], 0), sales.get(p["id"], 0) * p["preci"]] for p in old_products]
            print("\n\033[97m\033[1m\033[4mVentas Calculadas por Producto\033[0m")
            print(tabulate(table_sales, headers_sales, tablefmt="pretty"))

            if products_vendidos:
                borrarPantalla()
                print("\033[97m\033[1m\033[4m✅ Productos con ventas mayores o iguales a {} unidades\033[0m".format(min_sales))
                print()

                headers = ["ID", "Descripción", "Ventas", "Total Ventas"]
                table = [[p["id"], p["descrip"], sales.get(p["id"], 0), sales.get(p["id"], 0) * p["preci"]] for p in products_vendidos]
                print(tabulate(table, headers, tablefmt="pretty"))
            else:
                print("\n🔴 No hay productos con ventas mayores o iguales a {} unidades.".format(min_sales))

            input("\n\033[1;4;97m⬅️  Enter para continuar\033[0m")

        elif accion == "menor":
            while True:
                try:
                    max_sales = int(input("\n\033[92m Ingrese la cantidad máxima de ventas: \033[0m\033[97m=> \033[0m").strip())
                    if max_sales < 0:
                        raise ValueError
                    break
                except ValueError:
                    print("\n🔴 ERROR: La cantidad máxima de ventas debe ser un número entero positivo.")

            old_products = json.loads(json_file_products.read() or '[]')
            old_invoices = json.loads(json_file_invoices.read() or '[]')

            if not old_products or not old_invoices:
                print("⚠️ JSON VACÍO.")
                input("\nPresione Enter para continuar.")
                continue

            # Calcular las ventas totales por producto
            sales = {}
            for invoice in old_invoices:
                for item in invoice["detalle"]:
                    product_name = item["producto"]
                    quantity = item["cantidad"]
                    # Buscar el ID del producto por su nombre
                    product_id = next((p["id"] for p in old_products if p["descrip"] == product_name), None)
                    if product_id:
                        if product_id in sales:
                            sales[product_id] += quantity
                        else:
                            sales[product_id] = quantity

            # Filtrar productos con ventas menores o iguales a la cantidad máxima
            products_menos_vendidos = [p for p in old_products if sales.get(p["id"], 0) <= max_sales]

            # Mostrar ventas calculadas en tabla
            headers_sales = ["ID Producto", "Ventas", "Total Ventas"]
            table_sales = [[p["id"], sales.get(p["id"], 0), sales.get(p["id"], 0) * p["preci"]] for p in old_products]
            print("\n\033[97m\033[1m\033[4mVentas Calculadas por Producto\033[0m")
            print(tabulate(table_sales, headers_sales, tablefmt="pretty"))

            if products_menos_vendidos:
                borrarPantalla()
                print("\033[97m\033[1m\033[4m✅ Productos con ventas menores o iguales a {} unidades\033[0m".format(max_sales))
                print()

                headers = ["ID", "Descripción", "Ventas", "Total Ventas"]
                table = [[p["id"], p["descrip"], sales.get(p["id"], 0), sales.get(p["id"], 0) * p["preci"]] for p in products_menos_vendidos]
                print(tabulate(table, headers, tablefmt="pretty"))
            else:
                print("\n🔴 No hay productos con ventas menores o iguales a {} unidades.".format(max_sales))

            input("\n\033[1;4;97m⬅️  Enter para continuar\033[0m")

        elif accion == "stock":
            old_products = json.loads(json_file_products.read() or '[]')

            if not old_products:
                print("⚠️ JSON VACÍO.")
                input("\nPresione Enter para continuar.")
                continue

            # Filtrar productos sin stock
            products_sin_stock = [p for p in old_products if p["stock"] <= 0]

            borrarPantalla()
            print("\033[97m\033[1m\033[4m✅ Productos sin Stock\033[0m")
            print()

            headers = ["ID", "Descripción", "Stock"]
            table = [[p["id"], p["descrip"], p["stock"]] for p in products_sin_stock]
            print(tabulate(table, headers, tablefmt="pretty"))

            input("\n\033[1;4;97m⬅️  Enter para continuar\033[0m")

        elif accion == "s":
            break

        else:
            print("\033[91m\033[4m🚨 ERROR: Acción no reconocida. Por favor, intente de nuevo.\033[0m")
            input("\nPresione Enter para continuar.")

class CrudSales(ICrud):
  def create(self):
        validar = Valida()
        borrarPantalla()
        print('\033c', end='')
        gotoxy(2, 1); print(green_color + "██" * 50 + reset_color)
        gotoxy(30, 2); print(blue_color + "Registro de Venta")
        gotoxy(17, 3); print(blue_color + Company.get_business_name())
        gotoxy(5, 4); print(f"Factura#:F0999999 {' ' * 3} Fecha:{datetime.datetime.now()}")
        gotoxy(66, 4); print(" Subtotal:")
        gotoxy(66, 5); print(" Descuento:")
        gotoxy(66, 6); print(" Iva     :")
        gotoxy(66, 7); print(" Total   :")
        gotoxy(10, 6); print("Cedula:")
        dni = validar.solo_numeros("Error: Solo numeros", 23, 6)
        
        json_file = JsonFile(path+'/archivos/clients.json')
        clients_data = json_file.find("dni", dni)
        
        if not clients_data:
            gotoxy(35, 6); print("Cliente no existe")
            return
        
        client = clients_data[0]
        cli = RegularClient(client["first_name"], client["last_name"], client["dni"], card=True) 
        sale = Sale(cli)
        
        gotoxy(35, 6); print(cli.fullName())
        gotoxy(2, 8); print(green_color + "██" * 50 + reset_color) 
        gotoxy(5, 9); print(purple_color + "Linea") 
        gotoxy(12, 9); print("Id_Articulo") 
        gotoxy(24, 9); print("Descripcion") 
        gotoxy(38, 9); print("Precio") 
        gotoxy(48, 9); print("Cantidad") 
        gotoxy(58, 9); print("Subtotal") 
        gotoxy(70, 9); print("n->Terminar Venta)" + reset_color)
        
        follow = "s"
        line = 1
        
        while follow.lower() == "s":
            gotoxy(7, 9 + line); print(line)
            gotoxy(15, 9 + line); id_articulo = validar.solo_numeros("Error: Solo numeros", 15, 9 + line)
            
            json_file = JsonFile(path+'/archivos/products.json')
            prods = json_file.find("id", id_articulo)
            
            if not prods:
                gotoxy(24, 9 + line); print("Producto no existe")
                time.sleep(1)
                gotoxy(24, 9 + line); print(" " * 20)
            else:    
                prods = prods[0]
                product = Product(prods["id"], prods["descrip"], prods["preci"], prods["stock"])
                gotoxy(24, 9 + line); print(product.descrip)
                gotoxy(38, 9 + line); print(product.preci)

                # Verificar si hay suficiente stock
                gotoxy(49, 9 + line); qty = int(validar.solo_numeros("Error: Solo numeros", 49, 9 + line))
                if qty > product.stock:
                    gotoxy(24, 9 + line + 1); print(f"Stock insuficiente. Disponible: {product.stock}")
                    time.sleep(2)
                    gotoxy(24, 9 + line + 1); print(" " * 30)  # Limpiar el mensaje de error
                else:
                    # Restar la cantidad vendida del stock disponible
                    product.stock -= qty

                    # Actualizar el stock en el archivo JSON
                    products_data = json.loads(json_file.read() or '[]')
                    for prod in products_data:
                        if prod["id"] == product.id:
                            prod["stock"] = product.stock
                            break
                    json_file.write(json.dumps(products_data))

                    gotoxy(59, 9 + line); print(product.preci * qty)
                    sale.add_detail(product, qty)
                    gotoxy(76, 4); print(round(sale.subtotal, 2))
                    gotoxy(76, 5); print(round(sale.discount, 2))
                    gotoxy(76, 6); print(round(sale.iva, 2))
                    gotoxy(76, 7); print(round(sale.total, 2))
                    gotoxy(74, 9 + line); follow = input() or "s"  
                    gotoxy(76, 9 + line); print(green_color + "✔" + reset_color)  
                    line += 1
        
        gotoxy(15, 9 + line); print(red_color + "Esta seguro de grabar la venta(s/n):")
        gotoxy(54, 9 + line); procesar = input().lower()
        
        if procesar == "s":
            gotoxy(15, 10 + line); print("😊 Venta Grabada satisfactoriamente 😊" + reset_color)
            
            # Guardar la factura
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
            gotoxy(20, 10 + line); print("🤣 Venta Cancelada 🤣" + reset_color)    
        time.sleep(2)

  def update(self):
    while True:
        borrarPantalla()
        print('\033[1m\033[4m\033[97mActualizar datos de la factura.\033[0m')
        fact = input("\n\033[92m Ingresar número de factura, para actualizar los datos \033[0m\033[97m=> \033[0m").strip()
        if ' ' in fact or not fact.isdigit():
            print("\n\n\033[91m\033[4m🚨 ERROR: Incorrecto, digite bien el número de la factura. --- 🚨 ERROR: Sin espacios en medio.\033[0m")
            time.sleep(2)
            continue
        
        fact = float(fact)
        
        json_file = JsonFile(path + '/archivos/invoices.json')
        clients_data = json_file.find("factura", fact)

        if clients_data:
            factura_encontrada = clients_data[0]
            old_sale_details = factura_encontrada.get("detalle", [])
            
            # Muestra detalles de la factura
            print('\n\033c', end='')
            gotoxy(2, 1); print(green_color + "██" * 50 + reset_color)
            gotoxy(30, 2); print(blue_color + "Registro de Venta")
            gotoxy(17, 3); print(blue_color + Company.get_business_name())
            gotoxy(5, 4); print(f"Factura#: {factura_encontrada['factura']} {' ' * 3} Fecha:{factura_encontrada['Fecha']}")
            gotoxy(66, 4); print(" Subtotal: ", factura_encontrada["subtotal"])
            gotoxy(66, 5); print(" Descuento: ", factura_encontrada["descuento"])
            gotoxy(66, 6); print(" IVA     : ", factura_encontrada["iva"])
            gotoxy(66, 7); print(" Total   : ", factura_encontrada["total"])
            gotoxy(10, 6); print("Cliente: ", factura_encontrada["cliente"])
            gotoxy(2, 8); print(green_color + "██" * 50 + reset_color)
         
            input("\n\033[1m\033[4m\033[97mEnter si desea continuar => \033[0m\033[1m\033[4m\033[97m🚨 Datos que se van actualizar de la factura. ❗\033[0m")

            validar = Valida()
            
            borrarPantalla()
            print('\033c', end='')
            gotoxy(2, 1); print(green_color + "██" * 50 + reset_color)
            gotoxy(30, 2); print(blue_color + "Registro de Venta")
            gotoxy(17, 3); print(blue_color + Company.get_business_name())
            gotoxy(5, 4); print(f"Factura#: {factura_encontrada['factura']} {' ' * 3} Fecha:{datetime.datetime.now()}")
            gotoxy(66, 4); print(" Subtotal:")
            gotoxy(66, 5); print(" Descuento:")
            gotoxy(66, 6); print(" IVA     :")
            gotoxy(66, 7); print(" Total   :")
            gotoxy(10, 6); print("Cedula:")
            dni = validar.solo_numeros("Error: Solo numeros", 23, 6)

            json_file = JsonFile(path + '/archivos/clients.json')
            clients_data = json_file.find("dni", dni)

            if not clients_data:
                gotoxy(35, 6); print("Cliente no existe")
                return
            
            client = clients_data[0]
            cli = RegularClient(client["first_name"], client["last_name"], client["dni"], card=True) 
            sale = Sale(cli)
            
            gotoxy(35, 6); print(cli.fullName())
            gotoxy(2, 8); print(green_color + "██" * 50 + reset_color)
            gotoxy(5, 9); print(purple_color + "Linea")
            gotoxy(12, 9); print("Id_Articulo")
            gotoxy(24, 9); print("Descripcion")
            gotoxy(38, 9); print("Precio")
            gotoxy(48, 9); print("Cantidad")
            gotoxy(58, 9); print("Subtotal")
            gotoxy(70, 9); print("n->Terminar Venta)" + reset_color)

            follow = "s"
            line = 1
            
            while follow.lower() == "s":
                gotoxy(7, 9 + line); print(line)
                gotoxy(15, 9 + line); id_articulo = validar.solo_numeros("Error: Solo numeros", 15, 9 + line)
                
                json_file_path = path + '/archivos/products.json'
                json_file = JsonFile(json_file_path)
                prods = json_file.find("id", id_articulo)
                
                if not prods:
                    gotoxy(24, 9 + line); print("Producto no existe")
                    time.sleep(1)
                    gotoxy(24, 9 + line); print(" " * 20)
                    continue

                prods = prods[0]
                product = Product(prods["id"], prods["descrip"], prods["preci"], prods["stock"])

                # Busca si este producto ya estaba en la factura anterior
                old_detail = next((item for item in old_sale_details if item["producto"] == product.descrip), None)

                if old_detail:
                    # Si ya estaba, revertimos el stock primero
                    previous_qty = old_detail["cantidad"]
                    product.stock += previous_qty
                
                gotoxy(24, 9 + line); print(product.descrip)
                gotoxy(38, 9 + line); print(product.preci)

                qty = int(validar.solo_numeros("Error: Solo numeros", 49, 9 + line))

                if qty > product.stock:
                    gotoxy(24, 9 + line + 1); print(f"Stock insuficiente. Disponible: {product.stock}")
                    time.sleep(2)
                    gotoxy(24, 9 + line + 1); print(" " * 30)  # Limpiar el mensaje de error
                    continue

                # Restar la nueva cantidad del stock
                product.stock -= qty
                gotoxy(59, 9 + line); print(product.preci * qty)

                sale.add_detail(product, qty)
                gotoxy(76, 4); print(round(sale.subtotal, 2))
                gotoxy(76, 5); print(round(sale.discount, 2))
                gotoxy(76, 6); print(round(sale.iva, 2))
                gotoxy(76, 7); print(round(sale.total, 2))

                # Actualiza los detalles de la factura con la nueva información
                if old_detail:
                    old_detail["cantidad"] = qty
                    old_detail["precio"] = product.preci
                else:
                    factura_encontrada["detalle"].append({
                        "producto": product.descrip,
                        "cantidad": qty,
                        "precio": product.preci
                    })

                gotoxy(74, 9 + line); follow = input() or "s"
                gotoxy(76, 9 + line); print(green_color + "✔" + reset_color)
                line += 1

            gotoxy(15, 9 + line); print(red_color + "Esta seguro de grabar la venta(s/n):")
            gotoxy(54, 9 + line); procesar = input().lower()
            
            if procesar == "s":
                gotoxy(15, 10 + line); print("😊 Venta Grabada satisfactoriamente 😊" + reset_color)
                
                # Actualizar el archivo de productos
                json_file = JsonFile(json_file_path)
                all_products = json_file.read()
                
                if all_products:
                    all_products = json.loads(all_products)
                    for prod in all_products:
                        if prod["id"] == product.id:
                            prod["stock"] = product.stock
                            break
                    json_file.write(json.dumps(all_products, indent=4))

                # Actualizar el archivo de facturas
                json_file = JsonFile(path + '/archivos/invoices.json')
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
                gotoxy(15, 10 + line); print("❌ Venta cancelada ❌" + reset_color)
            
            input("\n\n\033[1m\033[4m\033[97mEnter para continuar... \033[0m")
            return

  def delete(self):
    while True:
        borrarPantalla()
        print('\033[1m\033[4m\033[97mActualizar datos de la factura.\033[0m')
        fact = input("\n\033[92m Ingresar número de factura, para actualizar los datos \033[0m\033[97m=> \033[0m").strip()
        
        # Validar si el número de factura es un número entero positivo
        if not fact.isdigit():
            print("\n\033[91m\033[4m🚨 ERROR: Debe ingresar un número entero sin espacios.\033[0m")
            time.sleep(2)
            continue
        
        fact = int(fact)  # Convertir el número de factura a entero
        
        # Verificar si la factura existe en el archivo JSON
        json_file_path = path + '/archivos/invoices.json'
        
        with open(json_file_path, 'r') as file:
            invoices = json.load(file)
            
        # Buscar la factura
        factura_encontrada = next((factura for factura in invoices if factura["factura"] == fact), None)
        
        if not factura_encontrada:
            print("\n\033[91m\033[4m❌ ERROR: No se encontró la factura. Por favor, vuelva a intentar.\033[0m")
            time.sleep(2)
            continue
        
        print('\n\033c', end='')
        gotoxy(2, 1); print(green_color + "██" * 50 + reset_color)
        gotoxy(30, 2); print(blue_color + "Registro de Venta")
        gotoxy(17, 3); print(blue_color + Company.get_business_name())
        gotoxy(5, 4); print(f"Factura#: {factura_encontrada['factura']} {' '*3} Fecha: {factura_encontrada['Fecha']}")
        gotoxy(66, 4); print(" Subtotal: ", factura_encontrada["subtotal"])
        gotoxy(66, 5); print(" Descuento: ", factura_encontrada["descuento"])
        gotoxy(66, 6); print(" IVA     : ", factura_encontrada["iva"])
        gotoxy(66, 7); print(" Total   : ", factura_encontrada["total"])
        gotoxy(10, 6); print("Cliente: ", factura_encontrada["cliente"])
        gotoxy(2, 8); print(green_color + "██" * 50 + reset_color)
        
        print("\n\033[1;97mPresione \033[4;97mESC\033[0;1;97m para cancelar o \033[4;97mEnter\033[0;1;97m para eliminar factura.\033[0m")
        
        while True:
            if msvcrt.kbhit():
                entrada = msvcrt.getch()
                if entrada == b"\x1b":  # ESC
                    print("\n\033[91;4m❌ Operación cancelada.\033[0m")
                    time.sleep(1)
                    break
                elif entrada == b"\r":  # Enter
                    # Eliminar la factura del archivo JSON
                    with open(json_file_path, 'r+') as file:
                        invoices = json.load(file)
                        invoices = [factura for factura in invoices if factura["factura"] != fact]
                        
                        file.seek(0)
                        json.dump(invoices, file, indent=4)
                        file.truncate()
                    
                    print("\n\033[92m✅ Factura eliminada con éxito.\033[0m")
                    time.sleep(2)
                    break
        break
                                
  def consult(self):
    facturas = loadInvoices()
    clients = loadClients()

    while True:
        borrarPantalla()
        print('\033[1m\033[4m\033[97mConsultar una factura o todas las facturas.\033[0m')
        accion = input("\n\033[92m Presione Enter para consultar una factura específica, 'vip' para facturas VIP, 'regular' para facturas regulares o 'fac' para todas las facturas \033[0m\033[97m=> \033[0m").strip().lower()

        if accion == "":
            # Consultar una factura específica
            borrarPantalla()
            print('\033[1m\033[4m\033[97mConsultar datos de una factura.\033[0m')
            numero = input("\n\033[92m Ingresar el número de la factura \033[0m\033[97m=> \033[0m").strip()
            if not numero.isdigit():
                print("\033[91m\033[4m🚨 ERROR: Número de factura incorrecto. Ingrese un número válido sin espacios.\033[0m")
                time.sleep(2)
                continue
            else:
                factura = findInvoice(facturas, int(numero))
                if factura is not None:
                    showInvoice(factura)
                else:
                    print("La factura no fue encontrada.")
            input(f"\n\033[1m\033[97mPresione Enter para salir.\033[0m")
            break
        
        elif accion == "vip" or accion == "regular":
            # Filtrar facturas por tipo de cliente (VIP o Regular)
            client_dnis = [client['dni'] for client in clients if ('limit' in client and accion == 'vip') or ('discount' in client and accion == 'regular')]
            
            filtered_facturas = [factura for factura in facturas if any(client['first_name'] + ' ' + client['last_name'] == factura['cliente'] for client in clients if client['dni'] in client_dnis)]
            
            if filtered_facturas:
                borrarPantalla()
                client_type = 'VIP' if accion == 'vip' else 'Regular'
                print(f'\033[1m\033[4m\033[97mFacturas {client_type}\033[0m')
                showInvoices(filtered_facturas)
            else:
                client_type = 'VIP' if accion == 'vip' else 'Regular'
                print(f"No hay facturas para clientes {client_type}.")

            input(f"\n\033[1m\033[97mPresione Enter para salir.\033[0m")
            break
        
        elif accion == "fac":
            while True:
                borrarPantalla()
                print('\033[1m\033[4m\n\033[97mConsulta de todas las facturas.\033[0m')
                showInvoices(facturas)
                orden = input("\n\033[92m Escriba 'max' para ordenar de mayor a menor y 'min' para ordenar de menor a mayor, o 's' para salir: \033[0m\033[97m=> \033[0m").strip().lower()
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