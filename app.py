from datetime import datetime
import os
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)
CORS(app)


ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Correction TMA :
# Problème : le backend pointait vers une mauvaise base MongoDB.
# Cause : le nom utilisé dans le code ne correspondait pas à la base visible dans Atlas.
# Correction : mise à jour du nom de base pour utiliser la bonne base moodify.

db_client = MongoClient(os.getenv("MONGO_URI"))
db = db_client["moodify"]
collection = db["emotions"]


@app.after_request
def add_header(response):

    response.headers["Content-Security-Policy"] = "frame-ancestors 'self' *"
    return response


@app.route("/")
def index():
    # Récupération des émotions enregistrées
    emotions_list = list(collection.find())
    return render_template("index.html", emotions=emotions_list)


@app.route("/additional")
def additional_page():
    return render_template("additional.html")


@app.route("/debug-mode")
def debug_mode():
    return jsonify({"message": "You've discovered debug mode!"})

# Correction TMA :
# Problème : les erreurs de l'analyse IA n'étaient pas compréhensibles.
# Cause : le bloc except renvoyait seulement "error" sans détail.
# Correction : ajout d'un message explicite avec le détail de l'exception.
@app.route("/analyse-emotion", methods=["POST"])
def analyze_emotion():
    if "image" not in request.files:
        return jsonify({"error": "Aucune image reçue"}), 400

    file = request.files["image"]

    img_bytes = file.read()
    mime_type = file.content_type

    try:
        prompt = (
            "Analyse l'expression faciale sur cette image. "
            "Réponds uniquement au format JSON avec ces clés : "
            "'emotion' (un mot), 'confidence' (nombre entre 0 et 100), "
            "'analysis' (une description simple + quelques mots d'encouragement)."
            "lequel de ces mots décrit le mieux l'émotion : joie, tristesse, neutre, colère, amour, angoisse ?"
            "'result' (un mot parmi : joie, tristesse, neutre, colère, amour, angoisse)."
        )

        image_part = types.Part.from_bytes(data=img_bytes, mime_type=mime_type)

        response = ai_client.models.generate_content(
            model="gemini-2.5-flash", contents=[prompt, image_part]
        )

        # Correction TMA :
        # Problème : la réponse de l'IA pouvait ne pas être un JSON valide.
        # Cause : json.loads() plante si la réponse est vide ou mal formatée.
        # Correction : ajout d'une vérification de réponse vide et d'un try/except sur le parsing JSON.

        raw_text = response.text.replace("```json", "").replace("```", "").strip()
        
        if not raw_text:
            return jsonify({"error": "Le modèle n'a pas retourné de texte"}), 500
        
        try:
             parsed_data = json.loads(raw_text)
        except json.JSONDecodeError:
            return jsonify({
                "error": "Le modèle n'a pas retourné un JSON valide", 
                "raw_response": raw_text}), 500
        return jsonify(parsed_data)

    except Exception as e:
        return (
            jsonify(
                {"error": "Erreur lors de l'analyse de l'image", "details": str(e)}
            ),
            500,
        )


@app.route("/playlist", methods=["GET"])
def playlist():
    collection_entries = db["entries"]
    collection_emotions = db["emotions"]

    # Fetch the most recent entry from the entries collection
    most_recent_entry = collection_entries.find_one(sort=[("_id", -1)])

    if not most_recent_entry:
        return render_template("playlist.html", emotions=[])

    # Fetch the emotion data from the emotions collection
    emotion_data = collection_emotions.find_one(
        {"emotion": most_recent_entry["emotion"]}
    )

    if not emotion_data:
        return render_template("playlist.html", emotions=[])

    # Combine the most recent entry with the emotion data
    combined_data = {
        "emotion": most_recent_entry["emotion"],
        "spotify_url": most_recent_entry["spotify_url"],
        "image": emotion_data.get("image"),
        "description": emotion_data.get("description"),
    }

    return render_template("playlist.html", emotions=[combined_data])

# Correction TMA :
# Problème : la route utilisait des noms de collections incohérents.
# Cause : "entrie" et "emotion" ne correspondaient pas aux collections utilisées ailleurs.
# Correction : harmonisation avec "entries" et "emotions".
@app.route("/save-emotion", methods=["POST"])
def save_emotion():
    collection_entries = db["entries"]
    collection_emotions = db["emotions"]
    # Correction TMA :
    # Problème : la route pouvait planter si aucune donnée JSON n'était envoyée.
    # Cause : request.get_json() peut retourner None.
    # Correction : ajout d'une vérification avant d'accéder à data.get(...).
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    emotion = data.get("emotion")

    if not emotion:
        return jsonify({"error": "Emotion manquante"}), 400

    # Retrieve Spotify URL from the emotions collection
    emotion_data = collection_emotions.find_one({"emotion": emotion})
    if not emotion_data or "spotify_url" not in emotion_data:
        return jsonify({"error": "Spotify URL introuvable pour cette émotion"}), 404

    spotify_url = emotion_data["spotify_url"]

    # Save to the entries collection
    collection_entries.insert_one(
        {
            "emotion": emotion,
            "spotify_url": spotify_url,
            "date": datetime.now(),
        }
    )

    return jsonify({"message": "Emotion enregistrée avec succès"})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
