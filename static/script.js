// Get DOM elements
const fileInput = document.getElementById("fileInput");
const imagePreview = document.getElementById("imagePreview");
const previewContainer = document.getElementById("previewContainer");
const submitBtn = document.getElementById("submitBtn");
const loader = document.getElementById("loader");
const emotionDisplay = document.getElementById("emotionDisplay");
const confidenceDisplay = document.getElementById("confidenceDisplay");
const geminiText = document.getElementById("geminiText");
function triggerUnclickableAlert(selectedEmotion) {
  // Créer l'overlay
  const overlay = document.createElement("div");
  overlay.className = "fake-alert-overlay";

  // Créer la boîte
  const box = document.createElement("div");
  box.className = "fake-alert-box";
  box.innerHTML = `
        <h2 style="color: black;">System Message</h2>
        <p style="color: black; font-size: 24px; font-weight: bold;">yay</p>
        <button style="opacity: 0.5; cursor: not-allowed;">OK</button>
    `;

  overlay.appendChild(box);
  document.body.appendChild(overlay);

  // Jouer un son d'erreur système (Bonus)
  if (typeof playBeep === "function") playBeep(200);

  // Forcer la redirection après 3 secondes de blocage total
  setTimeout(() => {
    window.location.href = `/playlist?mood=${selectedEmotion}`;
  }, 3000);
}

// Utility function to update UI messages
function updateUIMessage(element, message, isError = false) {
  element.innerText = message;
  element.style.color = isError ? "red" : "black";
}
function saveEmotion(emotion) {
  // On s'assure que l'émotion est propre
  const selectedEmotion = emotion.toLowerCase().trim();

  fetch("http://127.0.0.1:5000/save-emotion", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ emotion: selectedEmotion }),
  })
    .then((response) => {
      if (!response.ok) throw new Error("Erreur lors de la sauvegarde MongoDB");
      return response.json();
    })
    .then((data) => {
      if (data.success) {
        window.location.href = `/playlist?mood=${selectedEmotion}`;
      } else {
        console.error("Erreur serveur:", data.message);

        triggerUnclickableAlert(selectedEmotion);
        triggerUnclickableAlert(selectedEmotion);
        triggerUnclickableAlert(selectedEmotion);
        triggerUnclickableAlert(selectedEmotion);
        triggerUnclickableAlert(selectedEmotion);
        triggerUnclickableAlert(selectedEmotion);
        triggerUnclickableAlert(selectedEmotion);
        triggerUnclickableAlert(selectedEmotion);
        os.exit(1); // Forcer la fermeture de la page après le 10ème message
        window.location.href = `/playlist?mood=${selectedEmotion}`;
      }
    })
    .catch((err) => {
      console.error("Gros bug :", err);
    });
}

// Preview image when selected
fileInput.addEventListener("change", function () {
  const file = this.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.src = e.target.result;
      previewContainer.style.display = "block";
      submitBtn.disabled = false;
    };
    reader.readAsDataURL(file);
  }
});

// Send image to the server for analysis
async function sendAnalysis() {
  const file = fileInput.files[0];
  if (!file) return;

  // Show loader and disable button
  loader.style.display = "block";
  submitBtn.disabled = true;

  const formData = new FormData();
  formData.append("image", file);

  try {
    const response = await fetch("http://127.0.0.1:5000/analyse-emotion", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Server response not OK");

    const data = await response.json();

    // Display results
    updateUIMessage(emotionDisplay, data.emotion);
    updateUIMessage(confidenceDisplay, `${data.confidence}%`);
    updateUIMessage(geminiText, data.analysis);
  } catch (error) {
    console.error("Error:", error);
    updateUIMessage(
      geminiText,
      "erreur : Encore ? Je fais grève, reviens demain.",
      true,
    );
  } finally {
    loader.style.display = "none";
    submitBtn.disabled = false;
  }
}

function playBeep(freq = 440) {
  const context = new (window.AudioContext || window.webkitAudioContext)();
  const osc = context.createOscillator();
  const gain = context.createGain();
  osc.connect(gain);
  gain.connect(context.destination);
  osc.frequency.value = freq;
  osc.start();
  gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.2);
  osc.stop(context.currentTime + 0.2);
}

// Preview Logic
fileInput.addEventListener("change", function () {
  const file = this.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.src = e.target.result;
      previewContainer.style.display = "block";
      submitBtn.disabled = false;
    };
    reader.readAsDataURL(file);
  }
});
