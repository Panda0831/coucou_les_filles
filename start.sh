#!/bin/bash

# Arrêter le script en cas d'erreur
set -e

echo "--------------------------------------------------"
echo "🚀 Lancement de l'installation du projet Hackathon"
echo "--------------------------------------------------"

# 1. Création de l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel (venv)..."
    python3 -m venv venv
fi

# 2. Activation de l'environnement virtuel
echo "🔌 Activation de l'environnement virtuel..."
source venv/bin/activate

# 3. Installation/Mise à jour des dépendances
echo "📥 Installation des requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Application des migrations
echo "⚙️  Application des migrations de la base de données..."
python3 manage.py migrate

# 5. Message final et lancement
echo "--------------------------------------------------"
echo "✅ Installation terminée avec succès !"
echo "🌐 Le serveur va démarrer sur http://127.0.0.1:8000/"
echo "💡 (Note : Pour utiliser le Chat IA, n'oubliez pas d'exporter votre GROQ_API_KEY)"
echo "--------------------------------------------------"

python3 manage.py runserver
