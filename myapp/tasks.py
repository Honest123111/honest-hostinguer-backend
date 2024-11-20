from celery import shared_task
from .utils import fetch_and_create_load  # Importa la lógica de extracción desde utils.py

@shared_task
def extract_emails_task():
    """
    Tarea Celery para extraer correos electrónicos y crear Loads en la base de datos.
    """
    try:
        print("Iniciando la extracción de correos electrónicos...")
        fetch_and_create_load()  # Ejecuta la función que extrae los correos y crea los Loads
        print("Extracción de correos completada con éxito.")
    except Exception as e:
        # Imprime el error completo para obtener más detalles
        import traceback
        print(f"Error al ejecutar la tarea extract_emails_task: {e}")
        traceback.print_exc()  # Esto imprimirá el traceback completo del error para mayor claridad
