import telebot
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random

# Token del bot de Telegram
TOKEN = "7769484631:AAEmxtT7oNS3xeAvbAjPgOnF2Me27hhnzeo"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

def consultar_dni(dni):
    """Consulta un DNI y devuelve los datos o None si no hay resultados."""
    driver = setup_driver()
    url = "https://eldni.com/pe/buscar-datos-por-dni"
    driver.get(url)
    try:
        input_dni = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dni"))
        )
        input_dni.clear()
        input_dni.send_keys(dni)

        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btn-buscar-datos-por-dni"))
        )
        button.click()

        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table-striped.table-scroll"))
        )

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", class_="table table-striped table-scroll")
        if not table:
            return None  # No hay datos para este DNI

        tbody = table.find("tbody")
        if not tbody:
            return None

        rows = tbody.find_all("tr")
        if not rows:
            return None

        row = rows[0]
        cells = row.find_all("td")
        if len(cells) < 4:
            return None

        dni_res = cells[0].get_text(strip=True)
        nombres = cells[1].get_text(strip=True)
        apellido_paterno = cells[2].get_text(strip=True)
        apellido_materno = cells[3].get_text(strip=True)

        return (
            f"<b>DNI:</b> {dni_res}\n"
            f"<b>Nombres:</b> {nombres}\n"
            f"<b>Apellido Paterno:</b> {apellido_paterno}\n"
            f"<b>Apellido Materno:</b> {apellido_materno}"
        )
    except Exception:
        return None  # Si hay error, continuar con el siguiente
    finally:
        driver.quit()

# Manejador del comando /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Bienvenido.\nEnvía un número de DNI (8 dígitos) para consultar los datos.\n\n"
                          "Si quieres generar múltiples DNIs, envía un prefijo de 2 dígitos seguido de la cantidad de DNIs a generar.\n\n"
                          "Ejemplo: 79 10")

# Manejador para DNIs completos (8 dígitos)
@bot.message_handler(func=lambda m: m.text.isdigit() and len(m.text.strip()) == 8)
def handle_dni(message):
    dni = message.text.strip()
    resultado = consultar_dni(dni)
    if resultado:
        bot.reply_to(message, resultado)
    else:
        bot.reply_to(message, f"DNI {dni}: No se encontraron datos.")

# Manejador para generación de DNIs (2 primeros dígitos + cantidad deseada)
@bot.message_handler(func=lambda m: len(m.text.split()) == 2 and m.text.split()[0].isdigit() and len(m.text.split()[0]) == 2 and m.text.split()[1].isdigit())
def handle_dni_generation(message):
    parts = message.text.split()
    dni_prefijo = parts[0]  # Prefijo de 2 dígitos
    cantidad = int(parts[1])  # Número de DNIs a generar

    if cantidad > 20:  # Limitar a 20 para evitar spam
        bot.reply_to(message, "Por favor, solicita un máximo de 20 DNIs.")
        return

    bot.reply_to(message, f"Generando {cantidad} DNIs válidos con prefijo {dni_prefijo}XXXXXX...")

    dnIs_generados = set()
    resultados = []

    while len(resultados) < cantidad:
        dni = dni_prefijo + ''.join(random.choices("0123456789", k=6))  # Generar DNI aleatorio

        if dni in dnIs_generados:
            continue  # Evitar duplicados
        dnIs_generados.add(dni)

        resultado = consultar_dni(dni)

        if resultado:
            resultados.append(resultado)
            bot.send_message(message.chat.id, resultado)  # Enviar cada resultado uno por uno
            time.sleep(1)  # Pequeña pausa para evitar bloqueos

    bot.send_message(message.chat.id, f"✅ Se encontraron {cantidad} DNIs válidos.")

bot.polling()
