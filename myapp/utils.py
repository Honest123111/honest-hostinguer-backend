import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from .models import Load, AddressO, AddressD, Customer, ProcessedEmail, Stop
import requests
import time

# Credenciales de Gmail
GMAIL_USER = "aventurastorefigures@gmail.com"
GMAIL_PASSWORD = "jnwz asgl hwae mcdi"
IMAP_SERVER = "imap.gmail.com"

# Función para obtener coordenadas usando Nominatim con Google Maps como respaldo
def get_coordinates(address, zip_code=None, state=None, retries=3, delay=5):
    query = address
    if state:
        query += f", {state}"
    if zip_code:
        query += f", {zip_code}"

    # Intentar obtener coordenadas con Nominatim
    url_nominatim = "https://nominatim.openstreetmap.org/search"
    params_nominatim = {
        "q": query,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "YourAppName/1.0 (your_email@example.com)"
    }

    for attempt in range(retries):
        try:
            response = requests.get(url_nominatim, params=params_nominatim, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data:
                latitude = data[0]["lat"]
                longitude = data[0]["lon"]
                return f"{latitude},{longitude}"
            else:
                print(f"Nominatim no encontró coordenadas para la dirección: {query}")
        except requests.exceptions.RequestException as e:
            print(f"Intento {attempt + 1} fallido al obtener coordenadas con Nominatim para {query}: {e}")
            time.sleep(delay)

    # Intentar obtener coordenadas con Google Maps como respaldo
    try:
        google_api_key = "AIzaSyAmmAZPLEowFIuQpox5eEyGgLtaIaTPD_o"  # Reemplazar con tu clave de API
        url_google = "https://maps.googleapis.com/maps/api/geocode/json"
        params_google = {
            "address": query,
            "key": google_api_key
        }

        response = requests.get(url_google, params=params_google, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            latitude = location["lat"]
            longitude = location["lng"]
            return f"{latitude},{longitude}"
        else:
            print(f"Google Maps no encontró coordenadas para la dirección: {query}. Status: {data['status']}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener coordenadas con Google Maps para {query}: {e}")
        return None


# Función para leer correos y procesar cargas
def fetch_and_create_load():
    try:
        print("Iniciando la extracción de correos electrónicos...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(GMAIL_USER, GMAIL_PASSWORD)
        mail.select("inbox")

        # Fecha de hace 2 días
        two_days_ago = datetime.now() - timedelta(days=2)
        two_days_ago_str = two_days_ago.strftime("%d-%b-%Y")

        # Buscar correos con el asunto "NEW LOAD"
        search_criteria = f'(SUBJECT "NEW LOAD" SINCE "{two_days_ago_str}")'
        status, messages = mail.search(None, search_criteria)

        for num in messages[0].split():
            status, msg_data = mail.fetch(num, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    # ID del mensaje
                    msg_id = msg["Message-ID"]
                    if ProcessedEmail.objects.filter(message_id=msg_id).exists():
                        print(f"Correo con ID {msg_id} ya procesado.")
                        continue

                    # Decodificar cuerpo del correo
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode('utf-8', 'ignore')
                                break
                    else:
                        body = msg.get_payload(decode=True).decode('utf-8', 'ignore')

                    # Parsear y crear carga
                    load_data = parse_email_body(body)
                    if load_data:
                        create_load_from_data(load_data)

                    # Registrar el correo como procesado
                    ProcessedEmail.objects.create(message_id=msg_id)

        mail.logout()
        print("Extracción de correos completada con éxito.")
    except Exception as e:
        print(f"Error en fetch_and_create_load: {e}")


# Función para parsear el cuerpo del correo
def parse_email_body(body):
    try:
        lines = [line.strip() for line in body.splitlines() if line.strip()]

        print("Líneas extraídas del correo:")
        for line in lines:
            print(line)

        if len(lines) < 12:
            print("Error: el correo no contiene suficientes datos.")
            return None

        # Extraer Stops si están al final
        stops_data = []
        stops_start_index = 12  # Ajusta según el formato del correo
        for i in range(stops_start_index, len(lines), 5):  # Asumiendo 5 líneas por Stop
            if i + 4 >= len(lines):
                break
            stops_data.append({
                "location": lines[i].split(":")[1].strip(),
                "date_time": lines[i + 1].split(":")[1].strip(),
                "action_type": lines[i + 2].split(":")[1].strip(),
                "estimated_weight": int(lines[i + 3].split(":")[1].strip()),
                "quantity": int(lines[i + 4].split(":")[1].strip()),
            })

        # Extraer datos principales
        data = {
            "origin_zip": lines[0].split(":")[1].strip(),
            "origin_address": lines[1].split(":")[1].strip(),
            "origin_state": lines[2].split(":")[1].strip(),
            "destiny_zip": lines[3].split(":")[1].strip(),
            "destiny_address": lines[4].split(":")[1].strip(),
            "destiny_state": lines[5].split(":")[1].strip(),
            "customer_id": int(lines[6].split(":")[1].strip()),
            "equipment_type": lines[7].split(":")[1].strip(),
            "loaded_miles": int(lines[8].split(":")[1].strip()),
            "total_weight": int(lines[9].split(":")[1].strip()),
            "commodity": lines[10].split(":")[1].strip(),
            "offer": float(lines[11].split(":")[1].strip()),
            "stops": stops_data,  # Agregar Stops al resultado
        }
        return data
    except Exception as e:
        print(f"Error al parsear el correo: {e}")
        return None


# Función para crear la carga (Load) desde los datos del correo
def create_load_from_data(load_data):
    try:
        # Calcular coordenadas para origen y destino
        origin_coordinates = get_coordinates(load_data["origin_address"])
        if not origin_coordinates:
            print(f"Error: No se pudo obtener coordenadas para la dirección de origen {load_data['origin_address']}.")
            return

        destiny_coordinates = get_coordinates(load_data["destiny_address"])
        if not destiny_coordinates:
            print(f"Error: No se pudo obtener coordenadas para la dirección de destino {load_data['destiny_address']}.")
            return

        # Crear AddressO
        origin = AddressO.objects.create(
            zip_code=load_data["origin_zip"],
            address=load_data["origin_address"],
            state=load_data["origin_state"],
            coordinates=origin_coordinates
        )

        # Crear AddressD
        destiny = AddressD.objects.create(
            zip_code=load_data["destiny_zip"],
            address=load_data["destiny_address"],
            state=load_data["destiny_state"],
            coordinates=destiny_coordinates
        )

        # Obtener cliente
        customer = Customer.objects.get(id=load_data["customer_id"])

        # Crear Load
        load = Load.objects.create(
            origin=origin,
            destiny=destiny,
            equipment_type=load_data["equipment_type"],
            customer=customer,
            loaded_miles=load_data["loaded_miles"],
            total_weight=load_data["total_weight"],
            commodity=load_data["commodity"],
            offer=load_data["offer"],
        )

        # Crear Stops con coordenadas calculadas
        for stop_data in load_data.get("stops", []):
            stop_coordinates = get_coordinates(stop_data["location"])
            if not stop_coordinates:
                print(f"Error: No se pudo obtener coordenadas para el stop {stop_data['location']}.")
                continue

            Stop.objects.create(
                load=load,
                location=stop_data["location"],
                date_time=stop_data["date_time"],
                action_type=stop_data["action_type"],
                estimated_weight=stop_data["estimated_weight"],
                quantity=stop_data["quantity"],
                coordinates=stop_coordinates,
            )

        print(f"Load creado con éxito para el cliente {customer.name}")
    except Exception as e:
        print(f"Error al crear el Load: {e}")
