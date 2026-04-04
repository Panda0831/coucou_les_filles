#!/bin/bash
source venv/bin/activate
echo "🛑 Arrêt et nettoyage de la base de données..."
rm -f db.sqlite3
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
echo "✨ Recréation des migrations..."
python3 manage.py makemigrations
echo "⚙️  Application des migrations..."
python3 manage.py migrate
echo "✅ Base de données remise à zéro proprement."
./create_admin.sh
