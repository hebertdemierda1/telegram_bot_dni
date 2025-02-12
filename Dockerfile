# Usa una imagen base con Python 3.11
FROM python:3.11

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar todo el contenido del proyecto al contenedor
COPY . .

# Limpiar posibles problemas con archivos de bloqueo o caché
RUN rm -rf poetry.lock __pycache__

# Instalar Poetry
RUN pip install poetry

# Configurar Poetry para que no use virtualenv
RUN poetry config virtualenvs.create false

# Instalar las dependencias (sin dependencias de desarrollo)
RUN poetry install --without dev

# Comando para ejecutar el bot al iniciar el contenedor
CMD ["poetry", "run", "python", "bot_telegram_dni.py"]
