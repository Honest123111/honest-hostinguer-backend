import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from .models import Load, AddressO, AddressD, Customer, ProcessedEmail

# Credenciales de Gmail
GMAIL_USER = "aventurastorefigures@gmail.com"
GMAIL_PASSWORD = "jnwz asgl hwae mcdi"  # Cambia esto por la contraseña real
IMAP_SERVER = "imap.gmail.com"

def fetch_and_create_load():
    try:
        # Conectar al servidor IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(GMAIL_USER, GMAIL_PASSWORD)
        mail.select("inbox")  # Selecciona la bandeja de entrada

        # Obtener la fecha de hace 2 días
        two_days_ago = datetime.now() - timedelta(days=2)
        two_days_ago_str = two_days_ago.strftime("%d-%b-%Y")  # Formato: 20-Nov-2024

        # Buscar correos entre hace dos días y la fecha actual
        search_criteria = f'(SUBJECT "NEW LOAD" SINCE "{two_days_ago_str}")'
        status, messages = mail.search(None, search_criteria)

        # Procesar cada mensaje
        for num in messages[0].split():
            status, msg_data = mail.fetch(num, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    # Obtener el ID único del mensaje
                    msg_id = msg["Message-ID"]

                    # Verificar si ya se ha procesado este correo
                    if ProcessedEmail.objects.filter(message_id=msg_id).exists():
                        print(f"El correo con ID {msg_id} ya fue procesado.")
                        continue  # Ignorar este correo si ya se ha procesado

                    # Obtener el cuerpo del correo y decodificar correctamente en UTF-8
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode('utf-8', 'ignore')  # Cambiar a utf-8
                                break
                    else:
                        body = msg.get_payload(decode=True).decode('utf-8', 'ignore')  # Cambiar a utf-8

                    # Imprimir el contenido del correo para depuración
                    print("Contenido del correo recibido:")
                    print(body)

                    # Parsear el contenido del correo y crear la carga
                    load_data = parse_email_body(body)
                    if load_data:
                        create_load_from_data(load_data)

                    # Marcar este correo como procesado
                    ProcessedEmail.objects.create(message_id=msg_id)

        mail.logout()  # Cerrar sesión del servidor IMAP
    except Exception as e:
        print(f"Error en fetch_and_create_load: {e}")

def parse_email_body(body):
    try:
        # Limpiar el cuerpo del correo de líneas vacías o comentarios
        lines = [line for line in body.splitlines() if line.strip() and not line.strip().startswith('#')]

        # Imprimir las líneas extraídas para depuración
        print("Líneas extraídas del correo:")
        for line in lines:
            print(line)

        # Verificar si hay suficientes líneas
        if len(lines) < 14:  # Asegurarse de que haya al menos 14 líneas
            print("Error: el correo no contiene suficientes datos.")
            return None

        # Extraer datos
        data = {
            "origin_zip": lines[0].split(":")[1].strip() if len(lines) > 0 else "",
            "origin_address": lines[1].split(":")[1].strip() if len(lines) > 1 else "",
            "origin_state": lines[2].split(":")[1].strip() if len(lines) > 2 else "",
            "origin_coordinates": lines[3].split(":")[1].strip() if len(lines) > 3 else "",  # Coordenadas de origen
            "destiny_zip": lines[4].split(":")[1].strip() if len(lines) > 4 else "",
            "destiny_address": lines[5].split(":")[1].strip() if len(lines) > 5 else "",
            "destiny_state": lines[6].split(":")[1].strip() if len(lines) > 6 else "",
            "destiny_coordinates": lines[7].split(":")[1].strip() if len(lines) > 7 else "",  # Coordenadas de destino
            "customer_id": int(lines[8].split(":")[1].strip()) if len(lines) > 8 else 0,
            "equipment_type": lines[9].split(":")[1].strip() if len(lines) > 9 else "",
            "loaded_miles": int(lines[10].split(":")[1].strip()) if len(lines) > 10 else 0,
            "total_weight": int(lines[11].split(":")[1].strip()) if len(lines) > 11 else 0,
            "commodity": lines[12].split(":")[1].strip() if len(lines) > 12 else "",
            "offer": float(lines[13].split(":")[1].strip()) if len(lines) > 13 else 0.0,
        }
        return data
    except Exception as e:
        print(f"Error al parsear el correo: {e}")
        return None

def create_load_from_data(load_data):
    try:
        origin = AddressO.objects.create(
            zip_code=load_data["origin_zip"],
            address=load_data["origin_address"],
            state=load_data["origin_state"],
            coordinates=load_data["origin_coordinates"],  # Asignar las coordenadas
        )

        destiny = AddressD.objects.create(
            zip_code=load_data["destiny_zip"],
            address=load_data["destiny_address"],
            state=load_data["destiny_state"],
            coordinates=load_data["destiny_coordinates"],  # Asignar las coordenadas
        )

        customer = Customer.objects.get(id=load_data["customer_id"])

        Load.objects.create(
            origin=origin,
            destiny=destiny,
            equipment_type=load_data["equipment_type"],
            customer=customer,
            loaded_miles=load_data["loaded_miles"],
            total_weight=load_data["total_weight"],
            commodity=load_data["commodity"],
            offer=load_data["offer"],
        )
        print(f"Load creado con éxito para el cliente {customer.name}")
    except Exception as e:
        print(f"Error al crear el Load: {e}")
