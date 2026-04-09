#!/bin/bash

# Arrêter le script en cas d'erreur
set -e

echo "--------------------------------------------------"
echo "🚀 Lancement du projet Hackathon"
echo "--------------------------------------------------"

# Demander à l'utilisateur s'il veut utiliser Docker
read -p "Voulez-vous lancer le projet avec Docker ? (y/n) " use_docker

if [[ "$use_docker" =~ ^[Yy]$ ]]; then
    echo "🐳 Lancement avec Docker..."
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Erreur : docker-compose n'est pas installé."
        exit 1
    fi
    
    # Vérifier si .env existe, sinon copier .env.example
    if [ ! -f ".env" ]; then
        echo "📝 Création du fichier .env à partir de .env.example..."
        cp .env.example .env
        echo "⚠️  N'oubliez pas d'ajouter votre GROQ_API_KEY dans le fichier .env !"
    fi

    docker-compose up --build
else
    echo "📦 Lancement en local (sans Docker)..."
    
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
fi
