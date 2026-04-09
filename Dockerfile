# Utiliser une image Python officielle légère
FROM python:3.12-slim

# Définir des variables d'environnement
# Empêche Python d'écrire des fichiers .pyc sur le disque
ENV PYTHONDONTWRITEBYTECODE 1
# Empêche Python de mettre en mémoire tampon les sorties stdout et stderr
ENV PYTHONUNBUFFERED 1

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Installer les dépendances système nécessaires pour Pillow et autres
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier des dépendances
COPY requirements.txt /app/

# Installer les dépendances Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet dans le conteneur
COPY . /app/

# Rendre le script entrypoint exécutable
RUN chmod +x /app/entrypoint.sh

# Exposer le port sur lequel Django tourne
EXPOSE 8000

# Utiliser le script entrypoint pour lancer l'application
CMD ["/app/entrypoint.sh"]
