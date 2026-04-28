from collections import Counter
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
db = db_client["Moodify"]
collection = db["emotions"]


def load_local_emotions():
    local_path = os.path.join(
        os.path.dirname(__file__),
        "moodify-emotions",
        "emotions_with_images_and_music.json",
    )
    try:
        with open(local_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {item["emotion"].lower(): item for item in data if "emotion" in item}
    except Exception:
        return {}

LOCAL_EMOTION_MAP = load_local_emotions()
EMOTION_COLORS = {
    "joie": "#edca1a",
    "tristesse": "#166ee0",
    "colere": "#db4b4b",
    "amour": "#ef32c0",
    "angoisse": "#d9601a",
    "neutre": "#570ee0",
}


@app.after_request
def add_header(response):

    response.headers["Content-Security-Policy"] = "frame-ancestors 'self' *"
    return response


def get_emotion_color(emotion_name):
    return EMOTION_COLORS.get((emotion_name or "").lower(), "#94a3b8")


def format_entry_date(entry_date):
    if isinstance(entry_date, datetime):
        return entry_date.strftime("%d/%m %H:%M")
    return ""


def get_emotion_history(limit=10):
    collection_entries = db["entries"]

    try:
        cursor = collection_entries.find().sort("date", -1).limit(limit)
        raw_entries = list(cursor)
    except Exception:
        raw_entries = []

    raw_entries.reverse()

    history = []
    for item in raw_entries:
        emotion_name = item.get("emotion", "").strip()
        if not emotion_name:
            continue

        history.append(
            {
                "emotion": emotion_name,
                "date_label": format_entry_date(item.get("date")),
                "color": get_emotion_color(emotion_name),
            }
        )

    counts = Counter(entry["emotion"].lower() for entry in history)
    max_count = max(counts.values(), default=1)
    summary = []

    for emotion_name, total in counts.most_common():
        summary.append(
            {
                "emotion": emotion_name,
                "count": total,
                "width_percent": round((total / max_count) * 100, 2),
                "color": get_emotion_color(emotion_name),
            }
        )

    return history, summary


@app.route("/")
def index():
    # Récupération des émotions enregistrées depuis MongoDB.
    emotions_list = list(collection.find())

    display_emotions = []
    for item in emotions_list:
        emotion_key = item.get("emotion", "").lower().strip()
        local_item = LOCAL_EMOTION_MAP.get(emotion_key)
        if local_item:
            merged_item = {**local_item, **item}
            # Toujours privilégier le média local pour l'affichage.
            merged_item["image"] = local_item.get("image")
            merged_item["description"] = item.get("description") or local_item.get("description")
            display_emotions.append(merged_item)
        else:
            display_emotions.append(item)

    if not display_emotions:
        display_emotions = list(LOCAL_EMOTION_MAP.values())

    return render_template("index.html", emotions=display_emotions)


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
    # Correction TMA :
    # Problème : la route acceptait potentiellement des fichiers non image.
    # Cause : seule la présence du fichier était vérifiée, pas son type.
    # Correction : ajout d'un contrôle du type MIME avant l'envoi au modèle IA.
    if not file.content_type or not file.content_type.startswith("image/"): return jsonify({"error": "Le fichier doit être une image"}), 400

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
            model="gemini-3.1-flash-lite-preview", contents=[prompt, image_part]
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
    

def normalize_spotify_embed_url(spotify_url):
    if not spotify_url:
        return spotify_url

    if "open.spotify.com/embed/playlist" in spotify_url:
        return spotify_url

    if "open.spotify.com/playlist/" in spotify_url:
        
        parts = spotify_url.split("/playlist/")
        if len(parts) > 1:
            playlist_part = parts[1]
            playlist_id = playlist_part.split("?")[0].split("/")[0]
            query = ""
            if "?" in playlist_part:
                query = "?" + playlist_part.split("?", 1)[1]
            return f"https://open.spotify.com/embed/playlist/{playlist_id}{query}"

    if spotify_url.isalnum():
        return f"https://open.spotify.com/embed/playlist/{spotify_url}"

    return spotify_url


@app.route("/playlist", methods=["GET"])
def playlist():
    collection_entries = db["entries"]
    collection_emotions = db["emotions"]
    history, history_summary = get_emotion_history(limit=12)

    most_recent_entry = collection_entries.find_one(sort=[("_id", -1)])

    if not most_recent_entry:
        return render_template(
            "playlist.html",
            emotions=[],
            history=history,
            history_summary=history_summary,
        )

    emotion_data = collection_emotions.find_one(
        {"emotion": most_recent_entry["emotion"]}
    )

    if not emotion_data:
        return render_template(
            "playlist.html",
            emotions=[],
            history=history,
            history_summary=history_summary,
        )

    local_item = LOCAL_EMOTION_MAP.get(most_recent_entry["emotion"].lower())
    image_source = local_item.get("image") if local_item else emotion_data.get("image")
    description_source = emotion_data.get("description") or (local_item.get("description") if local_item else None)

    combined_data = {
        "emotion": most_recent_entry["emotion"],
        "spotify_url": normalize_spotify_embed_url(most_recent_entry["spotify_url"]),
        "image": image_source,
        "description": description_source,
    }

    return render_template(
        "playlist.html",
        emotions=[combined_data],
        history=history,
        history_summary=history_summary,
    )

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

    emotion = emotion.lower().strip()

    emotion_data = collection_emotions.find_one({"emotion": emotion})
    if not emotion_data or "spotify_url" not in emotion_data:
        emotion_data = LOCAL_EMOTION_MAP.get(emotion)

    if not emotion_data or "spotify_url" not in emotion_data:
        return jsonify({"error": "Spotify URL introuvable pour cette émotion"}), 404

    spotify_url = emotion_data["spotify_url"]

    collection_entries.insert_one(
        {
            "emotion": emotion,
            "spotify_url": spotify_url,
            "date": datetime.now(),
        }
    )

    # Correction TMA :
    # Problème : le frontend attendait une clé `success` dans la réponse.
    # Cause : la route renvoyait uniquement un `message` sans booléen de succès.
    # Correction : ajout de `success: True` dans la réponse JSON.
    return jsonify({"success": True, "message": "Emotion enregistrée avec succès"})


@app.route("/emotion-history", methods=["GET"])
def emotion_history():
    history, history_summary = get_emotion_history(limit=12)
    return jsonify(
        {
            "history": history,
            "summary": history_summary,
            "total_entries": len(history),
        }
    )


if __name__ == "__main__":
    app.run(port=5000, debug=True)
