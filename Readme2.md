# Moodify — TMA

> **Contexte scolaire** : Bachelor Système Numérique 2 — Matière TMA  
> **Équipe** : Adi Katia · Luce-Dubas Léna · Touazi Yacine · Feha Hermann Junior

---

## Présentation du projet

**Moodify** est une application web qui analyse l'expression faciale d'un utilisateur à partir d'une photo, détecte son émotion dominante grâce à l'IA (Google Gemini), puis lui propose une playlist Spotify adaptée à son humeur.

Dans le cadre de la matière **TMA**, un groupe nous a remis le projet initial contenant plusieurs bugs et lacunes. Notre mission était de :

1. **Identifier et corriger les bugs** présents dans le code original.
2. **Apporter des améliorations** fonctionnelles et visuelles au projet.
3. **Écrire des tests unitaires** pour valider les corrections.

---

## Technologies utilisées

| Catégorie | Outils |
|---|---|
| Backend | Python 3, Flask, Flask-CORS |
| IA / ML | Google Gemini (via `google-genai`) |
| Base de données | MongoDB Atlas (via `pymongo`) |
| Frontend | HTML5, CSS3, JavaScript (Vanilla) |
| Configuration | Python-dotenv |
| Tests | pytest, pytest-flask |
| Média | Vidéos MP4 / GIFs par émotion |
| Versionnement | Git |

---

## Structure du projet

```
tma_modif/
├── app.py                        # Backend Flask (routes + logique métier)
├── api_setup.py                  # Configuration de l'API
├── add-image-and-spotify-playlist.py  # Script d'alimentation de la BDD
├── emotions.json                 # Données d'émotions (référence locale)
├── entries.json                  # Exemple d'entrées utilisateur
├── static/
│   ├── style.css                 # Design de l'application
│   ├── script.js                 # Logique frontend
│   ├── fond.jpg                  # Image de fond
│   └── videos/                   # Médias associés aux émotions
│       ├── amour.mp4
│       ├── colere.mp4
│       ├── joie.mp4
│       ├── tristesse.mp4
│       ├── angoisse.gif
│       └── neutre.gif
├── templates/
│   ├── index.html                # Page d'accueil (sélection d'émotion)
│   ├── additional.html           # Page d'analyse via upload d'image
│   └── playlist.html             # Page de résultat / playlist Spotify
├── moodify-emotions/
│   ├── emotions_with_images_and_music.json  # Données enrichies (images + musique)
│   └── *.png                     # Images illustratives par émotion
└── tests/
    ├── __init__.py
    └── test_unit.py              # Tests unitaires (pytest)
```

---

## Prérequis

- Python 3.8+
- pip
- Un compte MongoDB Atlas (ou MongoDB local)
- Une clé API Google Gemini

---

## Installation

### 1. Cloner le dépôt

```bash
git clone <repository-url>
cd tma_modif
```

### 2. Installer les dépendances

```bash
pip install flask flask-cors google-genai pymongo python-dotenv pytest pytest-flask
```

### 3. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
GEMINI_API_KEY=votre_cle_api_gemini
MONGO_URI=votre_uri_mongodb_atlas
```

### 4. Lancer l'application

```bash
python app.py
```

L'application est accessible sur : [http://127.0.0.1:5000](http://127.0.0.1:5000)

### 5. Lancer les tests

```bash
pytest tests/ -v
```

---

## Fonctionnalités

- **Détection d'émotion par IA** : l'utilisateur upload une photo, Gemini analyse l'expression faciale et retourne l'émotion parmi : `joie`, `tristesse`, `neutre`, `colère`, `amour`, `angoisse`.
- **Playlist Spotify personnalisée** : selon l'émotion détectée, une playlist Spotify est proposée via un lecteur intégré.
- **Médias animés par émotion** : chaque émotion est illustrée par une vidéo MP4 ou un GIF.
- **Historique en base de données** : chaque analyse est enregistrée dans MongoDB (émotion + URL Spotify + date).
- **Fallback local** : si MongoDB est indisponible, l'application se replie sur les données locales JSON.

---

## Endpoints API

### `GET /`
Page d'accueil affichant les émotions disponibles avec leurs médias associés.

### `GET /additional`
Page permettant d'uploader une image pour l'analyse par IA.

### `POST /analyse-emotion`
Analyse une image et retourne l'émotion détectée.

- **Corps** : `multipart/form-data` avec un champ `image` (fichier image)
- **Réponse (succès)** :
```json
{
  "emotion": "joie",
  "confidence": 92,
  "analysis": "Expression joyeuse et lumineuse. Continuez comme ça !",
  "result": "joie"
}
```
- **Réponse (erreur)** :
```json
{
  "error": "Erreur lors de l'analyse de l'image",
  "details": "..."
}
```

### `POST /save-emotion`
Enregistre une émotion en base de données avec l'URL Spotify associée.

- **Corps** : `application/json` avec `{ "emotion": "joie" }`
- **Réponse (succès)** :
```json
{
  "success": true,
  "message": "Emotion enregistrée avec succès"
}
```

### `GET /playlist`
Affiche la dernière émotion enregistrée et sa playlist Spotify.

### `GET /debug-mode`
Route cachée retournant un message de débogage.

---

## Bugs corrigés (TMA)

Voici la liste des bugs identifiés dans le projet original et les corrections apportées :

### Bug 1 — Mauvais nom de base de données MongoDB
- **Problème** : le backend pointait vers `"Moodifi"` au lieu de `"Moodify"`, empêchant toute connexion à la bonne base.
- **Fichier** : `app.py`
- **Correction** : remplacement de `db_client["Moodifi"]` par `db_client["Moodify"]`.

---

### Bug 2 — Noms de collections incohérents dans `/save-emotion`
- **Problème** : la route utilisait `db["entrie"]` et `db["emotion"]` au lieu de `db["entries"]` et `db["emotions"]`, causant des erreurs silencieuses lors de l'enregistrement.
- **Fichier** : `app.py`
- **Correction** : harmonisation des noms de collections avec ceux utilisés dans les autres routes.

---

### Bug 3 — Absence de vérification du type MIME dans `/analyse-emotion`
- **Problème** : n'importe quel fichier pouvait être envoyé à l'IA, y compris des fichiers non-images.
- **Fichier** : `app.py`
- **Correction** : ajout d'un contrôle `content_type.startswith("image/")` avant traitement.

---

### Bug 4 — Gestion d'erreur silencieuse dans `/analyse-emotion`
- **Problème** : le bloc `except` renvoyait uniquement `"error"` sans message ni détail, rendant le débogage impossible.
- **Fichier** : `app.py`
- **Correction** : renvoi d'un JSON structuré `{"error": "...", "details": str(e)}`.

---

### Bug 5 — Parsing JSON non sécurisé de la réponse IA
- **Problème** : `json.loads()` plantait si la réponse de Gemini était vide ou mal formatée, sans aucun message d'erreur clair.
- **Fichier** : `app.py`
- **Correction** : ajout d'une vérification de la réponse vide et d'un `try/except` sur le parsing JSON.

---

### Bug 6 — Absence de vérification de `request.get_json()` dans `/save-emotion`
- **Problème** : si la requête ne contenait pas de JSON valide, `data.get(...)` plantait avec une `AttributeError`.
- **Fichier** : `app.py`
- **Correction** : ajout d'une vérification `if not data` avant d'accéder aux champs.

---

### Bug 7 — URL Spotify codée en dur (`http://127.0.0.1:5000`)
- **Problème** : les appels fetch utilisaient l'adresse localhost hardcodée, empêchant tout déploiement ou accès depuis un autre réseau.
- **Fichier** : `static/script.js`
- **Correction** : remplacement par `window.location.origin` pour construire les URLs dynamiquement.

---

### Bug 8 — Erreurs JavaScript sur les pages sans éléments DOM
- **Problème** : les variables DOM étaient initialisées en dehors d'un `DOMContentLoaded`, causant des erreurs `null` sur les pages ne possédant pas ces éléments (ex : page playlist).
- **Fichier** : `static/script.js`
- **Correction** : déplacement de l'initialisation dans un `document.addEventListener("DOMContentLoaded", ...)` avec vérifications de présence des éléments.

---

### Bug 9 — Listener `fileInput.addEventListener` dupliqué
- **Problème** : l'événement `change` sur le champ fichier était déclaré deux fois, causant des comportements imprévisibles.
- **Fichier** : `static/script.js`
- **Correction** : suppression du doublon, un seul listener conservé.

---

### Bug 10 — Réponse `/save-emotion` sans champ `success`
- **Problème** : le frontend testait `data.success` pour déclencher la redirection, mais le backend ne renvoyait pas ce champ.
- **Fichier** : `app.py`
- **Correction** : ajout de `"success": True` dans la réponse JSON.

---

### Bug 11 — URL Spotify mal formatée dans le lecteur intégré
- **Problème** : le template `playlist.html` construisait l'URL Spotify avec un format incorrect (`/embed/playlist/{{ item.spotify_url }}`), ne fonctionnant pas si l'URL complète était déjà stockée.
- **Fichiers** : `app.py`, `templates/playlist.html`
- **Correction** : ajout d'une fonction `normalize_spotify_embed_url()` dans le backend pour normaliser tous les formats d'URL Spotify en format embed.

---

### Bug 12 — Alertes JavaScript malveillantes en boucle
- **Problème** : en cas d'erreur lors de la sauvegarde, le code appelait `triggerUnclickableAlert()` en boucle (×8), bloquant totalement l'interface, puis tentait d'appeler `os.exit(1)` (inexistant en JavaScript).
- **Fichier** : `static/script.js`
- **Correction** : suppression de tout ce bloc, remplacement par une gestion d'erreur propre avec message affiché dans l'UI.

---

## Améliorations apportées

### Amélioration 1 — Médias animés par émotion (vidéos MP4 / GIFs)
Chaque émotion est désormais illustrée par un média animé (vidéo ou GIF) au lieu d'une simple image statique. Les templates détectent automatiquement l'extension `.mp4` pour afficher une balise `<video>` ou une balise `<img>` selon le cas.

### Amélioration 2 — Fallback sur données locales JSON
Lorsque MongoDB ne contient pas de données (base vide ou inaccessible), l'application se replie automatiquement sur le fichier local `emotions_with_images_and_music.json` pour afficher les émotions et leurs ressources.

### Amélioration 3 — Refonte visuelle complète
L'interface a été entièrement redessinée : fond personnalisé, grille de cartes responsive (3 colonnes), palette de couleurs cohérente, boutons stylisés, et mise en page centrée sur toutes les pages.

### Amélioration 4 — Bouton "Charger un fichier" sur la page d'accueil
Un bouton de navigation direct vers la page d'analyse (`/additional`) a été ajouté sur la page d'accueil, rendant le parcours utilisateur plus intuitif.

### Amélioration 5 — Suite de tests unitaires (pytest)
Une suite complète de tests unitaires a été rédigée dans `tests/test_unit.py` :


#### Tableau récapitulatif

| Nom du test | Partie testée | Vérification | Utilité |
|---|---|---|---|
| `test_none_retourne_none` | `normalize_spotify_embed_url` | Retourne `None` si la valeur d'entrée est `None` | Évite les erreurs si aucune URL n'est fournie |
| `test_url_embed_deja_formattee_inchangee` | `normalize_spotify_embed_url` | Ne modifie pas une URL Spotify déjà au format embed | Évite de casser une URL valide |
| `test_url_playlist_convertie_en_embed` | `normalize_spotify_embed_url` | Convertit une URL playlist classique en URL embed | Permet l'affichage correct dans un lecteur intégré |
| `test_url_playlist_avec_query_params` | `normalize_spotify_embed_url` | Gère aussi les URLs avec paramètres | Couvre un cas fréquent |
| `test_id_alphanumerique_convertie_en_embed` | `normalize_spotify_embed_url` | Transforme un ID Spotify seul en URL embed complète | Gère les données simplifiées |
| `test_url_inconnue_retournee_inchangee` | `normalize_spotify_embed_url` | Laisse inchangée une URL non Spotify | Évite une transformation incorrecte |
| `test_chaine_vide_retournee_inchangee` | `normalize_spotify_embed_url` | Laisse inchangée une chaîne vide | Vérifie un cas limite |
| `test_index_retourne_200` | Route `/` | Vérifie que la page d'accueil répond correctement | Confirme que la route principale fonctionne |
| `test_index_appelle_collection_find` | Route `/` | Vérifie que la route récupère les données MongoDB | Confirme l'accès aux émotions enregistrées |
| `test_additional_retourne_200` | Route `/additional` | Vérifie que la page supplémentaire répond correctement | Confirme que la route existe |
| `test_debug_mode_retourne_200` | Route `/debug-mode` | Vérifie que la route répond avec HTTP 200 | Confirme que la route de debug fonctionne |
| `test_debug_mode_retourne_json` | Route `/debug-mode` | Vérifie que la réponse est bien en JSON | Confirme le format attendu |
| `test_sans_image_retourne_400` | Route `/analyse-emotion` | Refuse une requête sans image | Vérifie la validation des entrées |
| `test_fichier_non_image_retourne_400` | Route `/analyse-emotion` | Refuse un fichier qui n'est pas une image | Empêche un mauvais usage de la route |
| `test_analyse_reussie_retourne_json` | Route `/analyse-emotion` | Retourne bien un JSON valide si l'analyse réussit | Vérifie le fonctionnement normal |
| `test_reponse_ia_vide_retourne_500` | Route `/analyse-emotion` | Retourne une erreur si l'IA répond avec un texte vide | Vérifie la robustesse de l'application |
| `test_reponse_ia_json_invalide_retourne_500` | Route `/analyse-emotion` | Retourne une erreur si la réponse IA n'est pas un JSON valide | Sécurise le parsing |
| `test_reponse_ia_avec_markdown_fences_parsee_correctement` | Route `/analyse-emotion` | Nettoie puis lit un JSON entouré de balises Markdown | Gère un format courant des réponses IA |
| `test_exception_ia_retourne_500` | Route `/analyse-emotion` | Retourne une erreur propre si l'appel IA échoue | Vérifie la gestion des exceptions |
| `test_sans_corps_retourne_400` | Route `/save-emotion` | Refuse une requête sans corps JSON | Vérifie la présence des données minimales |
| `test_emotion_manquante_retourne_400` | Route `/save-emotion` | Refuse une requête sans champ `emotion` | Vérifie le champ obligatoire |
| `test_emotion_inconnue_retourne_404` | Route `/save-emotion` | Retourne 404 si l'émotion n'existe pas | Évite l'enregistrement de données invalides |
| `test_emotion_valide_depuis_local_map` | Route `/save-emotion` | Accepte une émotion trouvée dans les données locales | Vérifie le fallback local |
| `test_emotion_normalisee_en_minuscules` | Route `/save-emotion` | Convertit une émotion en majuscules en minuscules | Rend le traitement plus souple |
| `test_reponse_contient_success_true` | Route `/save-emotion` | Vérifie la présence de `success: true` dans la réponse | Garantit le contrat attendu par le frontend |
| `test_priorite_mongodb_sur_local_map` | Route `/save-emotion` | Utilise MongoDB en priorité sur les données locales | Vérifie la logique métier |
| `test_sans_entree_retourne_200` | Route `/playlist` | Vérifie que la page playlist fonctionne sans historique | Évite un plantage si aucune donnée n'existe |
| `test_avec_entree_retourne_200` | Route `/playlist` | Vérifie que la page playlist fonctionne avec une entrée valide | Couvre le scénario nominal |
| `test_sans_emotion_correspondante_retourne_200` | Route `/playlist` | Vérifie que la page ne plante pas si l'émotion liée est absente | Gère les incohérences de données |
| `test_csp_header_present` | Sécurité HTTP | Vérifie la présence de l'en-tête `Content-Security-Policy` | Confirme une protection de sécurité |
| `test_csp_header_contient_frame_ancestors` | Sécurité HTTP | Vérifie que la directive `frame-ancestors` est présente | Confirme le contenu de la politique CSP |

### Résumé

Ces tests permettent de vérifier que :

- les fonctions utilitaires se comportent correctement 
- les routes principales de l'application répondent comme attendu 
- les erreurs sont bien gérées en cas d'entrée invalide ou de panne externe 
- certaines protections HTTP sont bien présentes

Ils servent donc à garantir la stabilité, la robustesse et la cohérence globale de l'application.


---

## Licence

Ce projet est réalisé dans un cadre pédagogique — Bachelor Système Numérique 2, matière TMA.