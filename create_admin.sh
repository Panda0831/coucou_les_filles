#!/bin/bash
source venv/bin/activate
echo "⚙️ Création d'un super-utilisateur (admin / admin123)..."
export DJANGO_SUPERUSER_PASSWORD=admin123
python3 manage.py createsuperuser --username admin --email admin@example.com --noinput || echo "ℹ️ L'admin existe déjà ou erreur de création."
unset DJANGO_SUPERUSER_PASSWORD
echo "✅ Fait ! Connectez-vous avec admin / admin123"
