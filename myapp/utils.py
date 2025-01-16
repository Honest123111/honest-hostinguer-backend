import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from .models import Load, AddressO, AddressD, Customer, ProcessedEmail, Stop
import requests
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration for IMAP and SMTP servers
IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "aventurastorefigures@gmail.com"
EMAIL_PASSWORD = "jnwz asgl hwae mcdi"

# Function to send emails
def send_email(subject, body, recipient):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, recipient, msg.as_string())
        server.quit()

        print(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Function to fetch coordinates using Nominatim with Google Maps as backup
def get_coordinates(address, zip_code=None, state=None, retries=3, delay=5):
    query = address
    if state:
        query += f", {state}"
    if zip_code:
        query += f", {zip_code}"

    # Try to get coordinates with Nominatim
    url_nominatim = "https://nominatim.openstreetmap.org/search"
    params_nominatim = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": "YourAppName/1.0 (your_email@example.com)"}

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
                print(f"Nominatim could not find coordinates for the address: {query}")
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed to get coordinates with Nominatim for {query}: {e}")
            time.sleep(delay)

    # Try Google Maps as a fallback
    try:
        google_api_key = "AIzaSyDbt0MU_QRza_GErVNPhbsTL89KL3pAR-w"
        url_google = "https://maps.googleapis.com/maps/api/geocode/json"
        params_google = {"address": query, "key": google_api_key}
        response = requests.get(url_google, params=params_google, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            latitude = location["lat"]
            longitude = location["lng"]
            return f"{latitude},{longitude}"
        else:
            print(f"Google Maps could not find coordinates for the address: {query}. Status: {data['status']}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting coordinates with Google Maps for {query}: {e}")
        return None

# Function to send emails
def send_email(subject, body, recipient):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, recipient, msg.as_string())
        server.quit()

        print(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Function to fetch emails and process loads
def fetch_and_create_load():
    try:
        print("Starting email extraction...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        mail.select("inbox")

        # Search emails from the last 2 days
        two_days_ago = datetime.now() - timedelta(days=2)
        two_days_ago_str = two_days_ago.strftime("%d-%b-%Y")

        # Search emails with the subject "NEW LOAD"
        search_criteria = f'(SUBJECT "NEW LOAD" SINCE "{two_days_ago_str}")'
        status, messages = mail.search(None, search_criteria)
        print(f"Found {len(messages[0].split())} emails matching the criteria.")

        for num in messages[0].split():
            print(f"Processing email number {num.decode('utf-8')}...")
            status, msg_data = mail.fetch(num, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    # Message ID
                    msg_id = msg["Message-ID"]
                    if ProcessedEmail.objects.filter(message_id=msg_id).exists():
                        print(f"Email with ID {msg_id} already processed. Skipping.")
                        continue

                    # Decode the email body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode('utf-8', 'ignore')
                                break
                    else:
                        body = msg.get_payload(decode=True).decode('utf-8', 'ignore')

                    print(f"Email body: {body[:100]}...")  # Log a preview of the body

                    # Parse and create the load
                    load_data = parse_email_body(body)
                    if load_data:
                        print(f"Parsed load data: {load_data}")
                        create_load_from_data(load_data)
                        print(f"Load created successfully for data: {load_data}")
                    else:
                        print("Failed to parse load data. Skipping this email.")

                    # Mark the email as processed
                    ProcessedEmail.objects.create(message_id=msg_id)
                    print(f"Marked email with ID {msg_id} as processed.")

        mail.logout()
        print("Email extraction completed successfully.")
    except Exception as e:
        print(f"Error in fetch_and_create_load: {e}")
        import traceback
        traceback.print_exc()  # Show detailed error traceback


# Function to parse the email body
def parse_email_body(body):
    try:
        lines = [line.strip() for line in body.splitlines() if line.strip()]

        print("Extracted lines from email:")
        for line in lines:
            print(line)

        if len(lines) < 12:
            print("Error: Email does not contain enough data.")
            return None

        # Extract Stops
        stops_data = []
        stops_start_index = 12  # Adjust based on email format
        for i in range(stops_start_index, len(lines), 5):
            if i + 4 >= len(lines):
                break
            stops_data.append({
                "location": lines[i].split(":")[1].strip(),
                "date_time": lines[i + 1].split(":")[1].strip(),
                "action_type": lines[i + 2].split(":")[1].strip(),
                "estimated_weight": int(lines[i + 3].split(":")[1].strip()),
                "quantity": int(lines[i + 4].split(":")[1].strip()),
            })

        # Extract main data
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
            "stops": stops_data,
        }
        return data
    except Exception as e:
        print(f"Error parsing email: {e}")
        return None

# Function to create the Load from email data
def create_load_from_data(load_data):
    try:
        # Calculate coordinates for origin and destination
        origin_coordinates = get_coordinates(load_data["origin_address"])
        if not origin_coordinates:
            print(f"Error: Could not get coordinates for origin address {load_data['origin_address']}.")
            return

        destiny_coordinates = get_coordinates(load_data["destiny_address"])
        if not destiny_coordinates:
            print(f"Error: Could not get coordinates for destination address {load_data['destiny_address']}.")
            return

        # Create origin and destination addresses
        origin = AddressO.objects.create(
            zip_code=load_data["origin_zip"],
            address=load_data["origin_address"],
            state=load_data["origin_state"],
            coordinates=origin_coordinates
        )
        destiny = AddressD.objects.create(
            zip_code=load_data["destiny_zip"],
            address=load_data["destiny_address"],
            state=load_data["destiny_state"],
            coordinates=destiny_coordinates
        )

        # Get the customer
        customer = Customer.objects.get(id=load_data["customer_id"])

        # Create the Load
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

        # Create stops
        stops_details = ""
        for stop_data in load_data.get("stops", []):
            stop_coordinates = get_coordinates(stop_data["location"])
            if not stop_coordinates:
                print(f"Error: Could not get coordinates for stop {stop_data['location']}.")
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
            stops_details += (
                f"- Location: {stop_data['location']}\n"
                f"  Date/Time: {stop_data['date_time']}\n"
                f"  Action: {stop_data['action_type']}\n"
                f"  Estimated Weight: {stop_data['estimated_weight']} lbs\n"
                f"  Quantity: {stop_data['quantity']}\n\n"
            )

        print(f"Load successfully created for customer {customer.name}")

        # Send email notification
        subject = f"New Load Created - Customer: {customer.name}"
        body = (
            f"A new load has been successfully created.\n\n"
            f"Details of the Load:\n"
            f"Origin: {load.origin.address} ({load.origin.zip_code}, {load.origin.state})\n"
            f"Destination: {load.destiny.address} ({load.destiny.zip_code}, {load.destiny.state})\n"
            f"Equipment: {load.equipment_type}\n"
            f"Loaded Miles: {load.loaded_miles}\n"
            f"Total Weight: {load.total_weight} lbs\n"
            f"Commodity: {load.commodity}\n"
            f"Offer: ${load.offer}\n\n"
            f"Stops:\n{stops_details}\n"
            f"Thank you,\nHonest Transportation INC"
        )
        send_email(subject, body, recipient="danielcampu28@gmail.com")  # Replace with desired recipient
    except Exception as e:
        print(f"Error creating Load: {e}")

#############################################
# NUEVAS FUNCIONES PARA PROCESAR SPOT LOADS #
#############################################

def parse_spot_load_email_body(body):
    """
    Parse the Spot Load email body to extract load details.
    """
    try:
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        print("Extracted lines from Spot Load email:")
        for line in lines:
            print(line)

        lane_line = next((l for l in lines if l.startswith("Lane:")), None)
        if not lane_line:
            print("Error: Lane line is missing.")
            return None

        lane_parts = lane_line.split(":", 1)[1].strip().split("->")
        if len(lane_parts) < 2:
            print("Error: Lane does not contain sufficient parts.")
            return None

        origin = lane_parts[0].strip()
        stops = lane_parts[1:-1]
        destination = lane_parts[-1].strip()

        equipment_line = next((l for l in lines if l.startswith("Equipment Required:")), None)
        if not equipment_line:
            print("Error: Equipment line is missing.")
            return None
        equipment_type = equipment_line.split(":", 1)[1].strip()

        rate_line = next((l for l in lines if l.startswith("Rate:")), None)
        if not rate_line:
            print("Error: Rate line is missing.")
            return None
        rate_info = rate_line.split(":", 1)[1].strip()
        import re
        match = re.search(r"(\d+(\.\d+)?)", rate_info)
        offer = float(match.group(1)) if match else 0.0

        miles_line = next((l for l in lines if l.startswith("Miles:")), None)
        if not miles_line:
            print("Error: Miles line is missing.")
            return None
        miles_str = miles_line.split(":", 1)[1].strip().replace(" mi", "")
        loaded_miles = float(miles_str)

        total_weight = 0
        commodity = "General Freight"
        customer_id = 1

        stops_data = []
        for stop in stops:
            stop_coordinates = get_coordinates(stop)
            if not stop_coordinates:
                print(f"Error: Could not get coordinates for stop {stop}.")
                continue

            stops_data.append({
                "location": stop,
                "date_time": "",  # Default or extracted if available
                "action_type": "",  # Default or extracted if available
                "estimated_weight": 0,  # Default or extracted if available
                "quantity": 0,  # Default or extracted if available
                "coordinates": stop_coordinates,
            })

        data = {
            "origin_zip": "",  # Default or extracted if available
            "origin_address": origin,
            "origin_state": "",  # Default or extracted if available
            "destiny_zip": "",  # Default or extracted if available
            "destiny_address": destination,
            "destiny_state": "",  # Default or extracted if available
            "customer_id": customer_id,
            "equipment_type": equipment_type,
            "loaded_miles": int(loaded_miles),
            "total_weight": total_weight,
            "commodity": commodity,
            "offer": offer,
            "stops": stops_data,
        }
        return data
    except Exception as e:
        print(f"Error parsing spot load email: {e}")
        return None

def fetch_and_create_spot_load():
    try:
        print("Starting Spot Load email extraction...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        mail.select("inbox")

        two_days_ago = datetime.now() - timedelta(days=2)
        two_days_ago_str = two_days_ago.strftime("%d-%b-%Y")
        search_criteria = f'(SUBJECT "Amazon Relay Spot Load Capacity Request" SINCE "{two_days_ago_str}")'
        status, messages = mail.search(None, search_criteria)

        for num in messages[0].split():
            status, msg_data = mail.fetch(num, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    msg_id = msg["Message-ID"]

                    if ProcessedEmail.objects.filter(message_id=msg_id).exists():
                        print(f"Email with ID {msg_id} already processed.")
                        continue

                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode('utf-8', 'ignore')
                                break
                    else:
                        body = msg.get_payload(decode=True).decode('utf-8', 'ignore')

                    load_data = parse_spot_load_email_body(body)
                    if load_data:
                        create_load_from_data(load_data)

                    ProcessedEmail.objects.create(message_id=msg_id)

        mail.logout()
        print("Spot Load email extraction completed successfully.")
    except Exception as e:
        print(f"Error in fetch_and_create_spot_load: {e}")