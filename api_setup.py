import os
from dotenv import load_dotenv
from google import genai

# Charger les variables du fichier .env
load_dotenv()

# Récupérer la clé API
api_key = os.getenv("API_KEY_GEMINI")

# Configurer le SDK avec la clé
if api_key:
    genai.configure(api_key=api_key)
    print("Clé API chargée avec succès.")
else:
    print("Erreur : Clé API introuvable. Vérifiez le fichier .env")

# Exemple d'initialisation du modèle
model = genai.GenerativeModel('gemini-1.5-flash')