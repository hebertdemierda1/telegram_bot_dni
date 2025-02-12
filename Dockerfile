FROM python:3.11

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos al contenedor
COPY . .

# Instalar Poetry
RUN pip install poetry

# Desactivar la creación de virtualenv
RUN poetry config virtualenvs.create false

# Instalar las dependencias sin dependencias de desarrollo
RUN poetry install --no-dev

# Comando para ejecutar el bot
CMD ["poetry", "run", "python", "bot_telegram_dni.py"]
