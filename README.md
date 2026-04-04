### TEMPLATE

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd Hackathon
```

### 2. Configurer l'environnement

Copiez le fichier d'exemple et ajoutez votre clé API Groq :

```bash
cp .env.example .env
```

### 3. Lancer l'installation et le serveur

Exécutez simplement notre script de démarrage :

```bash
./start.sh
```

_Le script va créer l'environnement virtuel, installer les dépendances, appliquer les migrations et lancer le serveur sur http://127.0.0.1:8000/._

## ⚡ Commandes Utiles (Trousse à outils)

- **Créer un Admin instantanément** : `./create_admin.sh` (Identifiants : `admin` / `admin123`)
- **Remise à zéro de la base de données** : `./reset_db.sh` (Utile si vous modifiez les modèles)
- **Lancer le serveur manuellement** : `python3 manage.py runserver`

## 🏗️ Architecture Technique

- **Backend** : Django 6.0
- **IA** : API Groq (llama-3.3-70b-versatile)
- **Base de données** : SQLite (parfait pour le prototypage rapide)
- **Frontend** : Django Templates, Tailwind CSS, JavaScript (Fetch API pour le chat)

## 👥 L'Équipe

ajout des membre dans about.html juste tape /about aminy url
Retrouvez plus de détails sur l'équipe sur la page `/about/` de l'application.
