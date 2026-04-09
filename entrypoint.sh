#!/bin/bash

# Appliquer les migrations
echo "⚙️  Application des migrations de la base de données..."
python manage.py migrate

# Lancer le serveur
echo "🌐 Lancement du serveur sur le port 8000..."
python manage.py runserver 0.0.0.0:8000
