"""
Tests unitaires pour l'application Moodify.

Lancer les tests :
    pip install pytest pytest-flask
    pytest tests/ -v
"""

import importlib
import io
import json
import sys
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def app_module():
    """Charge le module app avec MongoDB et Gemini mockes."""
    sys.modules.pop("app", None)

    with patch("google.genai.Client") as mock_genai_client, \
         patch("pymongo.MongoClient") as mock_mongo, \
         patch("dotenv.load_dotenv"), \
         patch("builtins.open", create=True):

        mock_genai_client.return_value = MagicMock()

        mock_db = MagicMock()
        mock_mongo.return_value.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = MagicMock()

        flask_app = importlib.import_module("app")
        flask_app.render_template = MagicMock(return_value="HTML MOCK")
        flask_app.LOCAL_EMOTION_MAP = {
            "joie": {"emotion": "joie", "spotify_url": "https://open.spotify.com/playlist/joie123"},
            "tristesse": {"emotion": "tristesse", "spotify_url": "https://open.spotify.com/playlist/tristesse123"},
            "colere": {"emotion": "colere", "spotify_url": "https://open.spotify.com/playlist/colere123"},
            "neutre": {"emotion": "neutre", "spotify_url": "https://open.spotify.com/playlist/neutre123"},
            "amour": {"emotion": "amour", "spotify_url": "https://open.spotify.com/playlist/amour123"},
            "angoisse": {"emotion": "angoisse", "spotify_url": "https://open.spotify.com/playlist/angoisse123"},
        }

        flask_app.app.config["TESTING"] = True
        flask_app.app.config["WTF_CSRF_ENABLED"] = False

        yield flask_app

        sys.modules.pop("app", None)


@pytest.fixture
def app(app_module):
    """Expose l'application Flask au plugin pytest-flask."""
    return app_module.app


@pytest.fixture
def client(app_module):
    """Client HTTP de test Flask."""
    return app_module.app.test_client()


def make_image_file(filename="test.jpg", content_type="image/jpeg"):
    """Cree un faux fichier image pour les requetes multipart."""
    return (io.BytesIO(b"fake_image_bytes"), filename, content_type)


class TestNormalizeSpotifyEmbedUrl:
    """Teste la fonction de normalisation des URLs Spotify."""

    def test_none_retourne_none(self, app_module):
        assert app_module.normalize_spotify_embed_url(None) is None

    def test_url_embed_deja_formattee_inchangee(self, app_module):
        url = "https://open.spotify.com/embed/playlist/abc123"
        assert app_module.normalize_spotify_embed_url(url) == url

    def test_url_playlist_convertie_en_embed(self, app_module):
        url = "https://open.spotify.com/playlist/abc123"
        result = app_module.normalize_spotify_embed_url(url)
        assert "embed" in result
        assert "abc123" in result

    def test_url_playlist_avec_query_params(self, app_module):
        url = "https://open.spotify.com/playlist/abc123?si=xyz"
        result = app_module.normalize_spotify_embed_url(url)
        assert "embed" in result
        assert "abc123" in result

    def test_id_alphanumerique_convertie_en_embed(self, app_module):
        result = app_module.normalize_spotify_embed_url("abc123XYZ")
        assert result == "https://open.spotify.com/embed/playlist/abc123XYZ"

    def test_url_inconnue_retournee_inchangee(self, app_module):
        url = "https://autre-site.com/playlist/xyz"
        assert app_module.normalize_spotify_embed_url(url) == url

    def test_chaine_vide_retournee_inchangee(self, app_module):
        assert app_module.normalize_spotify_embed_url("") == ""


class TestRouteIndex:
    """Teste la page d'accueil."""

    def test_index_retourne_200(self, client, app_module):
        with patch.object(app_module, "collection") as mock_col:
            mock_col.find.return_value = []
            response = client.get("/")
        assert response.status_code == 200

    def test_index_appelle_collection_find(self, client, app_module):
        with patch.object(app_module, "collection") as mock_col:
            mock_col.find.return_value = []
            client.get("/")
            mock_col.find.assert_called_once()


class TestRouteAdditional:
    def test_additional_retourne_200(self, client):
        response = client.get("/additional")
        assert response.status_code == 200


class TestRouteDebugMode:
    def test_debug_mode_retourne_200(self, client):
        response = client.get("/debug-mode")
        assert response.status_code == 200

    def test_debug_mode_retourne_json(self, client):
        response = client.get("/debug-mode")
        data = json.loads(response.data)
        assert "message" in data
        assert "debug" in data["message"].lower()


class TestRouteAnalyseEmotion:
    """Teste l'endpoint d'analyse d'emotion via Gemini."""

    def test_sans_image_retourne_400(self, client):
        response = client.post("/analyse-emotion", data={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_fichier_non_image_retourne_400(self, client):
        data = {"image": (io.BytesIO(b"not an image"), "file.txt", "text/plain")}
        response = client.post(
            "/analyse-emotion",
            data=data,
            content_type="multipart/form-data"
        )
        assert response.status_code == 400
        resp_data = json.loads(response.data)
        assert "error" in resp_data

    def test_analyse_reussie_retourne_json(self, client, app_module):
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "emotion": "joie",
            "confidence": 92,
            "analysis": "Visage souriant, grande joie !",
            "result": "joie"
        })

        with patch.object(app_module, "ai_client") as mock_ai:
            mock_ai.models.generate_content.return_value = mock_response
            data = {"image": make_image_file()}
            response = client.post(
                "/analyse-emotion",
                data=data,
                content_type="multipart/form-data"
            )

        assert response.status_code == 200
        resp_data = json.loads(response.data)
        assert resp_data["emotion"] == "joie"
        assert resp_data["confidence"] == 92

    def test_reponse_ia_vide_retourne_500(self, client, app_module):
        mock_response = MagicMock()
        mock_response.text = ""

        with patch.object(app_module, "ai_client") as mock_ai:
            mock_ai.models.generate_content.return_value = mock_response
            data = {"image": make_image_file()}
            response = client.post(
                "/analyse-emotion",
                data=data,
                content_type="multipart/form-data"
            )

        assert response.status_code == 500
        resp_data = json.loads(response.data)
        assert "error" in resp_data

    def test_reponse_ia_json_invalide_retourne_500(self, client, app_module):
        mock_response = MagicMock()
        mock_response.text = "Ceci n'est pas du JSON valide !!!"

        with patch.object(app_module, "ai_client") as mock_ai:
            mock_ai.models.generate_content.return_value = mock_response
            data = {"image": make_image_file()}
            response = client.post(
                "/analyse-emotion",
                data=data,
                content_type="multipart/form-data"
            )

        assert response.status_code == 500
        resp_data = json.loads(response.data)
        assert "error" in resp_data

    def test_reponse_ia_avec_markdown_fences_parsee_correctement(self, client, app_module):
        mock_response = MagicMock()
        mock_response.text = (
            "```json\n"
            "{\"emotion\": \"tristesse\", \"confidence\": 80, \"analysis\": \"Triste\", \"result\": \"tristesse\"}\n"
            "```"
        )

        with patch.object(app_module, "ai_client") as mock_ai:
            mock_ai.models.generate_content.return_value = mock_response
            data = {"image": make_image_file()}
            response = client.post(
                "/analyse-emotion",
                data=data,
                content_type="multipart/form-data"
            )

        assert response.status_code == 200
        resp_data = json.loads(response.data)
        assert resp_data["emotion"] == "tristesse"

    def test_exception_ia_retourne_500(self, client, app_module):
        with patch.object(app_module, "ai_client") as mock_ai:
            mock_ai.models.generate_content.side_effect = Exception("Gemini unreachable")
            data = {"image": make_image_file()}
            response = client.post(
                "/analyse-emotion",
                data=data,
                content_type="multipart/form-data"
            )

        assert response.status_code == 500
        resp_data = json.loads(response.data)
        assert "error" in resp_data
        assert "details" in resp_data


class TestRouteSaveEmotion:
    """Teste l'endpoint de sauvegarde des emotions."""

    def test_sans_corps_retourne_400(self, client):
        response = client.post(
            "/save-emotion",
            data="",
            content_type="application/json"
        )
        assert response.status_code == 400

    def test_emotion_manquante_retourne_400(self, client):
        response = client.post(
            "/save-emotion",
            data=json.dumps({}),
            content_type="application/json"
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_emotion_inconnue_retourne_404(self, client, app_module):
        with patch.object(app_module, "db") as mock_db:
            mock_col_emotions = MagicMock()
            mock_col_emotions.find_one.return_value = None
            mock_db.__getitem__.return_value = mock_col_emotions

            with patch.object(app_module, "LOCAL_EMOTION_MAP", {}):
                response = client.post(
                    "/save-emotion",
                    data=json.dumps({"emotion": "emotion_inexistante"}),
                    content_type="application/json"
                )

        assert response.status_code == 404

    def test_emotion_valide_depuis_local_map(self, client, app_module):
        with patch.object(app_module, "db") as mock_db:
            mock_col_emotions = MagicMock()
            mock_col_emotions.find_one.return_value = None
            mock_col_entries = MagicMock()

            def getitem(name):
                if name == "emotions":
                    return mock_col_emotions
                if name == "entries":
                    return mock_col_entries
                return MagicMock()

            mock_db.__getitem__.side_effect = getitem

            local_map = {
                "joie": {
                    "emotion": "joie",
                    "spotify_url": "https://open.spotify.com/playlist/joie123"
                }
            }

            with patch.object(app_module, "LOCAL_EMOTION_MAP", local_map):
                response = client.post(
                    "/save-emotion",
                    data=json.dumps({"emotion": "joie"}),
                    content_type="application/json"
                )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get("success") is True

    def test_emotion_normalisee_en_minuscules(self, client, app_module):
        """L'emotion 'JOIE' doit etre normalisee en 'joie'."""
        with patch.object(app_module, "db") as mock_db:
            mock_col_emotions = MagicMock()
            mock_col_emotions.find_one.return_value = None
            mock_col_entries = MagicMock()

            mock_db.__getitem__.side_effect = lambda name: (
                mock_col_emotions if name == "emotions" else mock_col_entries
            )

            local_map = {
                "joie": {
                    "emotion": "joie",
                    "spotify_url": "https://open.spotify.com/playlist/joie123"
                }
            }

            with patch.object(app_module, "LOCAL_EMOTION_MAP", local_map):
                response = client.post(
                    "/save-emotion",
                    data=json.dumps({"emotion": "JOIE"}),
                    content_type="application/json"
                )

        assert response.status_code == 200

    def test_reponse_contient_success_true(self, client, app_module):
        with patch.object(app_module, "db") as mock_db:
            mock_col_emotions = MagicMock()
            mock_col_emotions.find_one.return_value = None
            mock_col_entries = MagicMock()

            mock_db.__getitem__.side_effect = lambda name: (
                mock_col_emotions if name == "emotions" else mock_col_entries
            )

            local_map = {
                "tristesse": {
                    "emotion": "tristesse",
                    "spotify_url": "https://open.spotify.com/playlist/tristesse123"
                }
            }

            with patch.object(app_module, "LOCAL_EMOTION_MAP", local_map):
                response = client.post(
                    "/save-emotion",
                    data=json.dumps({"emotion": "tristesse"}),
                    content_type="application/json"
                )

        data = json.loads(response.data)
        assert data["success"] is True
        assert "message" in data

    def test_priorite_mongodb_sur_local_map(self, client, app_module):
        """Si MongoDB retourne une entree, elle est utilisee en priorite."""
        with patch.object(app_module, "db") as mock_db:
            mongo_emotion = {
                "emotion": "joie",
                "spotify_url": "https://open.spotify.com/embed/playlist/mongo_id"
            }
            mock_col_emotions = MagicMock()
            mock_col_emotions.find_one.return_value = mongo_emotion
            mock_col_entries = MagicMock()

            mock_db.__getitem__.side_effect = lambda name: (
                mock_col_emotions if name == "emotions" else mock_col_entries
            )

            with patch.object(app_module, "LOCAL_EMOTION_MAP", {}):
                response = client.post(
                    "/save-emotion",
                    data=json.dumps({"emotion": "joie"}),
                    content_type="application/json"
                )

        assert response.status_code == 200


class TestRoutePlaylist:
    """Teste la page de playlist."""

    def test_sans_entree_retourne_200(self, client, app_module):
        with patch.object(app_module, "db") as mock_db:
            mock_col = MagicMock()
            mock_col.find_one.return_value = None
            mock_db.__getitem__.return_value = mock_col

            response = client.get("/playlist")

        assert response.status_code == 200

    def test_avec_entree_retourne_200(self, client, app_module):
        with patch.object(app_module, "db") as mock_db:
            mock_entries = MagicMock()
            mock_entries.find_one.return_value = {
                "emotion": "joie",
                "spotify_url": "https://open.spotify.com/playlist/joie123"
            }
            mock_emotions = MagicMock()
            mock_emotions.find_one.return_value = {
                "emotion": "joie",
                "image": "joie.png",
                "description": "Une humeur joyeuse !"
            }

            def getitem(name):
                if name == "entries":
                    return mock_entries
                if name == "emotions":
                    return mock_emotions
                return MagicMock()

            mock_db.__getitem__.side_effect = getitem
            response = client.get("/playlist")

        assert response.status_code == 200

    def test_sans_emotion_correspondante_retourne_200(self, client, app_module):
        with patch.object(app_module, "db") as mock_db:
            mock_entries = MagicMock()
            mock_entries.find_one.return_value = {
                "emotion": "joie",
                "spotify_url": "https://open.spotify.com/playlist/joie123"
            }
            mock_emotions = MagicMock()
            mock_emotions.find_one.return_value = None

            mock_db.__getitem__.side_effect = lambda name: (
                mock_entries if name == "entries" else mock_emotions
            )

            response = client.get("/playlist")

        assert response.status_code == 200


class TestEntetesHTTP:
    """Verifie les en-tetes de securite ajoutes par after_request."""

    def test_csp_header_present(self, client):
        response = client.get("/debug-mode")
        assert "Content-Security-Policy" in response.headers

    def test_csp_header_contient_frame_ancestors(self, client):
        response = client.get("/debug-mode")
        csp = response.headers.get("Content-Security-Policy", "")
        assert "frame-ancestors" in csp
