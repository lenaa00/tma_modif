# Moodify

Moodify is a web application that analyzes emotions from images and provides a curated Spotify playlist 

## Features
- Upload an image to analyze emotions.
- View the detected emotion and confidence level.
- Get a Spotify playlist tailored to the detected emotion.
- Interactive and responsive user interface.

## Prerequisites
To run Moodify, ensure you have the following installed:
- Python 3.8+
- pip (Python package manager)
- MongoDB (for storing emotions and entries)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Moodify
```

### 2. Install Dependencies
install packages
pip install python-dotenv flask flask-cors google-genai pymongo 

```

### 3. Configure MongoDB
Ensure MongoDB is running locally or remotely. Update the database connection string in `app.py` if necessary.

### 4. Run the Application
Start the Flask server:
```bash
python app.py
```
The application will be available at `http://127.0.0.1:5000`.

### 5. Access the Web Interface
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## Folder Structure
```
Moodify/

│   ├── app.py               # Flask backend
│   ├── static/              # Static files (CSS, JS)
│   │   ├── style.css        # Styling for the app
│   │   ├── script.js        # Frontend logic
│   ├── templates/           # HTML templates
│   │   ├── index.html       # Home page
│   │   ├── playlist.html    # Playlist page
│   ├── README.md            # Project documentation
│   ├── emotions.json        # Sample emotions data
│   ├── entries.json         # Sample entries data
```
## problemes rencontrés : 
## Issues Encountered

- The application occasionally crashes
- Database entries are no longer being saved.
- The AI analysis functionality is not operational.
- before working, refer to hanine to set up mongo db, and give the user acces to the databse


## API Endpoints

### 1. `/analyse-emotion` (POST)
- **Description**: Accepts an image and returns the detected emotion and confidence level.
- **Request**:
  - Method: `POST`
  - Body: FormData with an image file.
- **Response**:
  ```json
  {
    "emotion": "happy",
    "confidence": 95.0
  }
  ```

### 2. `/save-emotion` (POST)
- **Description**: Saves the detected emotion and its associated Spotify playlist URL.
- **Request**:
  - Method: `POST`
  - Body: JSON with `emotion` and `spotify_url`.
- **Response**:
  ```json
  {
    "message": "Emotion enregistrée avec succès"
  }
  ```

### 3. `/playlist` (GET)
- **Description**: Displays the most recent emotion and its Spotify playlist.
- **Response**: Renders the `playlist.html` template.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- Flask for the backend framework.
- MongoDB for the database.
- Spotify for the playlists.
- Open-source libraries and tools.
