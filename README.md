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

### 3. Lancer le projet

Exécutez notre script de démarrage interactif :

```bash
./start.sh
```

_Le script vous demandera si vous souhaitez utiliser **Docker** ou une installation **locale**._

---

## 🐳 Utilisation avec Docker (Recommandé)

L'utilisation de Docker garantit que le projet fonctionnera de la même manière sur toutes les machines.

### Démarrage rapide avec Docker
1.  **Lancer le projet** : `./start.sh` (répondre `y` à la question sur Docker).
2.  **Créer un Admin** (pendant que le conteneur tourne) :
    ```bash
    docker-compose exec web python manage.py createsuperuser --username admin --email admin@example.com
    ```

### Commandes Docker utiles
- **Arrêter le projet** : `docker-compose down`
- **Reconstruire l'image** : `docker-compose build`
- **Voir les logs** : `docker-compose logs -f`

---

## 📦 Utilisation en Local (sans Docker)

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
