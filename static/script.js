// Variables initialisées à null pour éviter une erreur sur les pages qui n'ont pas ces éléments.
let fileInput = null;
let imagePreview = null;
let previewContainer = null;
let submitBtn = null;
let loader = null;
let emotionDisplay = null;
let confidenceDisplay = null;
let geminiText = null;

document.addEventListener("DOMContentLoaded", () => {
  fileInput = document.getElementById("fileInput");
  imagePreview = document.getElementById("imagePreview");
  previewContainer = document.getElementById("previewContainer");
  submitBtn = document.getElementById("submitBtn");
  loader = document.getElementById("loader");
  emotionDisplay = document.getElementById("emotionDisplay");
  confidenceDisplay = document.getElementById("confidenceDisplay");
  geminiText = document.getElementById("geminiText");

  if (fileInput && imagePreview && previewContainer && submitBtn) {
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
  }
});

function triggerUnclickableAlert(selectedEmotion) {
  const overlay = document.createElement("div");
  overlay.className = "fake-alert-overlay";

  const box = document.createElement("div");
  box.className = "fake-alert-box";
  box.innerHTML = `
        <h2 style="color: black;">System Message</h2>
        <p style="color: black; font-size: 24px; font-weight: bold;">yay</p>
        <button style="opacity: 0.5; cursor: not-allowed;">OK</button>
    `;

  overlay.appendChild(box);
  document.body.appendChild(overlay);

  if (typeof playBeep === "function") playBeep(200);

  setTimeout(() => {
    window.location.href = `/playlist?mood=${selectedEmotion}`;
  }, 3000);
}

function updateUIMessage(element, message, isError = false) {
  element.innerText = message;
  element.style.color = isError ? "red" : "black";
}
function saveEmotion(emotion) {
  const selectedEmotion = emotion.toLowerCase().trim();
  const saveUrl = `${window.location.origin}/save-emotion`;
  console.log("Envoi de l'émotion à :", saveUrl, selectedEmotion);

  fetch(saveUrl, {
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
        window.location.href = "/playlist";
      } else {
        console.error("Erreur serveur:", data.message);
        window.location.href = "/playlist";
      }
    })
    .catch((err) => {
      console.error("Gros bug :", err);
    });
}

async function sendAnalysis() {
  const file = fileInput?.files?.[0];
  if (!file) {
    updateUIMessage(geminiText, "Veuillez choisir une image avant l'analyse.", true);
    return;
  }


  loader.style.display = "block";
  submitBtn.disabled = true;

  const formData = new FormData();
  formData.append("image", file);

  try {
    const analyseUrl = `${window.location.origin}/analyse-emotion`;
    console.log("Envoi de l'image à :", analyseUrl);
    const response = await fetch(analyseUrl, {
      method: "POST",
      body: formData,
    });

    let data;
    try {
      data = await response.json();
    } catch {
      data = null;
    }

    if (!response.ok) {
      const message =
        data?.details || data?.error || "Erreur serveur lors de l'analyse.";
      console.error("Analyse échouée :", message, data);
      updateUIMessage(geminiText, message, true);
      return;
    }


    updateUIMessage(emotionDisplay, data.emotion);
    updateUIMessage(confidenceDisplay, `${data.confidence}%`);
    updateUIMessage(geminiText, data.analysis);

    // Sauvegarde l'émotion et affiche la playlist
    if (data.emotion) {
      saveEmotion(data.emotion);
    }
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
