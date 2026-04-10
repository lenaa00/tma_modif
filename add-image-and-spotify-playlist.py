import json
import base64
import os

# Chemins des dossiers
folder_path = "moodify-emotions"
json_path = "emotions.json"
output_path = os.path.join(folder_path, "emotions_with_images_and_music.json")

# 1. Dictionnaire des liens Spotify (à adapter avec tes playlists)
# On ne stocke que l'URL src de l'iframe pour garder le JSON propre
SPOTIFY_MAPPING = {
    "joie": "https://open.spotify.com/embed/playlist/37i9dQZF1EIgG2NEOhqsD7?utm_source=generator",
    "tristesse": "https://open.spotify.com/playlist/37i9dQZF1EIg85EO6f7KwU?utm_source=generator",
    "neutre": "https://open.spotify.com/embed/playlist/37i9dQZF1DX8UaYjZ9aZ96?utm_source=generator",
    "colere": "https://open.spotify.com/playlist/37i9dQZF1EIg85EO6f7KwU?utm_source=generator",
    "amour": "https://open.spotify.com/playlist/37i9dQZF1EIg85EO6f7KwU?utm_source=generator",
    "angoisse": "https://open.spotify.com/playlist/37i9dQZF1EIg85EO6f7KwU?utm_source=generator",
}

# 2. Charger le fichier JSON original
if not os.path.exists(json_path):
    print(f"Erreur : Le fichier {json_path} est introuvable.")
else:
    with open(json_path, "r", encoding="utf-8") as f:
        emotions = json.load(f)

    # 3. Parcourir chaque élément du JSON
    for i in emotions:
        emotion_name = i["emotion"].lower() # On passe en minuscule pour correspondre au dico
        image_filename = f"{emotion_name}.png"
        image_path = os.path.join(folder_path, image_filename)

        # --- Partie Image ---
        if os.path.exists(image_path):
            with open(image_path, "rb") as f_img:
                binary_data = f_img.read()
                base64_image = base64.b64encode(binary_data).decode('utf-8')
                i["image"] = f"data:image/png;base64,{base64_image}"
                print(f"Image ajoutée : {emotion_name}")
        else:
            i["image"] = None
            print(f"Image manquante : {image_filename}")

        # --- Partie Spotify URL ---
        # On récupère l'URL dans le dico, sinon on met une valeur par défaut
        i["spotify_url"] = SPOTIFY_MAPPING.get(emotion_name, "https://open.spotify.com/embed/playlist/37i9dQZF1DX8UaYjZ9aZ96")
        print(f"Musique liée : {emotion_name}")

    # 4. Sauvegarder le nouveau JSON complet
    os.makedirs(folder_path, exist_ok=True) # Crée le dossier s'il n'existe pas
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(emotions, f, indent=4, ensure_ascii=False)

    print(f"\nfichier sauvegardé sous : {output_path}")