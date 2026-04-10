

# Moodify

Moodify est une application web qui analyse les émotions à partir d'images pour proposer une playlist Spotify personnalisée.

## Fonctionnalités
- **Analyse d'image** : Importez une photo pour détecter l'émotion associée.
- **Détails de détection** : Visualisez l'émotion détectée et le niveau de confiance de l'IA.
- **Playlists Spotify** : Obtenez une playlist adaptée à votre humeur actuelle.
- **Interface responsive** : Une expérience utilisateur interactive et fluide.

## Technologies utilisées (TechStack)

Ce projet a été réalisé avec les technologies suivantes :

- **Frontend** : HTML, CSS, JavaScript
- **Backend** : Flask (Python)
- **Base de données** : MongoDB
- **IA/ML** : Google GenAI
- **Autres outils** : Python-dotenv, Flask-CORS, API Spotify
- **Gestion de version** : Git
- **Hébergement** : Localhost (serveur de développement Flask)
- **Gestionnaire de paquets** : pip

## Prérequis
Pour lancer Moodify, assurez-vous d'avoir installé :
- Python 3.8+
- pip (gestionnaire de paquets Python)
- MongoDB (pour le stockage des émotions et des entrées)

## Instructions d'installation

### 1. Cloner le dépôt
```bash
git clone <repository-url>
cd Moodify
```

### 2. Installer les dépendances
Installez les bibliothèques nécessaires :
```bash
pip install python-dotenv flask flask-cors google-genai pymongo 
```

### 3. Configurer MongoDB
Vérifiez que MongoDB tourne en local ou à distance. Si besoin, mettez à jour la chaîne de connexion dans `app.py`.

### 4. Lancer l'application
Démarrez le serveur Flask :
```bash
python app.py
```
L'application sera disponible sur `http://127.0.0.1:5000`.

### 5. Accéder à l'interface web
Ouvrez votre navigateur à l'adresse suivante :
```
http://127.0.0.1:5000
```

## Structure du projet
```
Moodify/
│   ├── app.py               # Backend Flask
│   ├── static/              # Fichiers statiques (CSS, JS)
│   │   ├── style.css        # Design de l'application
│   │   ├── script.js        # Logique frontend
│   ├── templates/           # Templates HTML
│   │   ├── index.html       # Page d'accueil
│   │   ├── playlist.html    # Page de la playlist
│   ├── README.md            # Documentation du projet
│   ├── emotions.json        # Exemple de données d'émotions
│   ├── entries.json         # Exemple de données d'entrées
```

## Problèmes rencontrés (Issues)

1. **Sauvegarde en base de données** : L'API rencontre parfois une erreur lors de l'exécution, empêchant l'enregistrement des entrées. Cela peut être lié à la configuration de MongoDB ou à la logique de l'API.
2. **Boutons de redirection** : Certains boutons de l'interface ne fonctionnent pas comme prévu (problème potentiel de routage ou d'erreurs JavaScript).
3. **Accès aux fonctionnalités IA** : 
   - La page dédiée à l'IA est parfois inaccessible.
   - Des erreurs "Internal Server Error" surviennent occasionnellement côté backend.
4. **Configuration MongoDB** : Avant de lancer l'application, il est nécessaire de consulter Hanine pour configurer MongoDB et s'assurer des droits d'accès.

## Points de terminaison de l'API (Endpoints)

### 1. `/analyse-emotion` (POST)
- **Description** : Analyse une image et renvoie l'émotion détectée.
- **Requête** : `FormData` contenant un fichier image.
- **Réponse** :
  ```json
  {
    "emotion": "happy",
    "confidence": 95.0
  }
  ```

### 2. `/save-emotion` (POST)
- **Description** : Enregistre l'émotion et l'URL de la playlist Spotify associée.
- **Requête** : JSON avec `emotion` et `spotify_url`.
- **Réponse** :
  ```json
  {
    "message": "Emotion enregistrée avec succès"
  }
  ```

### 3. `/playlist` (GET)
- **Description** : Affiche l'émotion la plus récente et sa playlist.
- **Réponse** : Génère le template `playlist.html`.

## Licence
Ce projet est sous licence MIT.

## Remerciements
- Flask pour le framework backend.
- MongoDB pour la base de données.
- Spotify pour les playlists.
- Les différentes bibliothèques open-source utilisées.
