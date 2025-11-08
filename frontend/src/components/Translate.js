import { getTransliterateSuggestions } from "@ai4bharat/indic-transliterate";
import axios from "axios";
import { useEffect, useRef, useState } from "react";
import "./Translate.css";

const NUM_BARS = 10;
const MAX_HISTORY = 10;

const Translate = () => {
  const [text, setText] = useState("");
  const [translation, setTranslation] = useState("");
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [sourceLang, setSourceLang] = useState("en");
  const [targetLang, setTargetLang] = useState("te");
  const [history, setHistory] = useState([]);
  const [levels, setLevels] = useState(Array(NUM_BARS).fill(2));

  const recognitionRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);
  const animationRef = useRef(null);
  const micStreamRef = useRef(null);

  useEffect(() => {
    const saved = localStorage.getItem("translatorHistory");
    if (saved) setHistory(JSON.parse(saved));
  }, []);

  useEffect(() => {
    localStorage.setItem("translatorHistory", JSON.stringify(history));
  }, [history]);

  // 🎙️ Initialize speech recognition
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => setListening(true);
    recognition.onend = () => stopMicVisualization();

    recognition.onresult = async (event) => {
      const rawTranscript = event.results[0][0].transcript.trim();
      let processedText = rawTranscript;

      if (sourceLang === "te") {
        try {
          const suggestions = await getTransliterateSuggestions(rawTranscript, "te");
          processedText = suggestions[0]?.text || rawTranscript;
        } catch {
          console.warn("Telugu transliteration failed.");
        }
      }

      setText(processedText);
      await handleTranslate(processedText, sourceLang);
    };

    recognitionRef.current = recognition;
  }, [sourceLang]);

  // 🌊 Smooth neural wave visualization
  const startMicVisualization = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      micStreamRef.current = stream;
      audioContextRef.current = new (window.AudioContext ||
        window.webkitAudioContext)();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      const analyser = audioContextRef.current.createAnalyser();
      analyser.fftSize = 64;
      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      source.connect(analyser);

      analyserRef.current = analyser;
      dataArrayRef.current = dataArray;

      const draw = () => {
        animationRef.current = requestAnimationFrame(draw);
        analyser.getByteFrequencyData(dataArray);
        const avg = dataArray.reduce((a, b) => a + b, 0) / bufferLength;
        const normalized = Math.max(2, Math.min(10, avg / 25));
        const newLevels = Array(NUM_BARS)
          .fill(0)
          .map(() => normalized + Math.random() * 2);
        setLevels(newLevels);
      };
      draw();
    } catch (err) {
      console.error("Microphone access denied:", err);
    }
  };

  const stopMicVisualization = () => {
    setListening(false);
    cancelAnimationFrame(animationRef.current);
    if (micStreamRef.current)
      micStreamRef.current.getTracks().forEach((t) => t.stop());
    if (audioContextRef.current) audioContextRef.current.close();
    setLevels(Array(NUM_BARS).fill(2));
  };

  const handleVoiceInput = () => {
    if (!recognitionRef.current) return alert("Voice input not supported.");
    if (listening) {
      recognitionRef.current.stop();
      stopMicVisualization();
    } else {
      recognitionRef.current.lang = sourceLang === "te" ? "te-IN" : "en-US";
      recognitionRef.current.start();
      startMicVisualization();
    }
  };

  const handleTranslate = async (inputText = text, lang = sourceLang) => {
    if (!inputText.trim()) return alert("Please type or speak something!");
    setLoading(true);
    setTranslation("");

    try {
      const res = await axios.post("http://127.0.0.1:8000/translate", {
        text: inputText,
        source_lang: lang,
        target_lang: lang === "te" ? "en" : "te",
      });

      let output = res.data.translation || "No translation available";

      if (lang === "en" && targetLang === "te") {
        try {
          const suggestions = await getTransliterateSuggestions(output, "te");
          output = suggestions[0]?.text || output;
        } catch {
          console.warn("Telugu transliteration failed.");
        }
      }

      setTranslation(output);

      const newEntry = {
        id: Date.now(),
        text: inputText,
        translation: output,
        from: lang,
        to: lang === "te" ? "en" : "te",
      };
      setHistory([newEntry, ...history].slice(0, MAX_HISTORY));
    } catch (err) {
      console.error(err);
      setTranslation("⚠️ Translation failed.");
    } finally {
      setLoading(false);
    }
  };

  const speakEnglish = () => {
    if (!translation) return;
    const synth = window.speechSynthesis;
    const utter = new SpeechSynthesisUtterance(translation);
    utter.lang = "en-US";
    synth.cancel();
    synth.speak(utter);
  };

  const swapLanguages = () => {
    setSourceLang((prev) => (prev === "en" ? "te" : "en"));
    setTargetLang((prev) => (prev === "te" ? "en" : "te"));
    setTranslation("");
    setText("");
  };

  return (
    <div className="translator-wrapper">
      <div className="translator-card">
        <header>
          <h1>Telugu ↔ English Translator</h1>
          
        </header>

        <div className="lang-row">
          <div className="lang-label">
            <span>{sourceLang === "en" ? "English" : "Telugu"}</span>
          </div>
          <button className="swap-btn" onClick={swapLanguages}>⇄</button>
          <div className="lang-label">
            <span>{targetLang === "en" ? "English" : "Telugu"}</span>
          </div>
        </div>

        <div className="input-area">
          <textarea
            value={text}
            placeholder="🎤 Speak or type here..."
            onChange={(e) => setText(e.target.value)}
          />
          <button
            className={`mic-btn ${listening ? "listening" : ""}`}
            onClick={handleVoiceInput}
          >
            {listening ? (
              <div className="live-wave">
                {levels.map((h, i) => (
                  <span key={i} style={{ height: `${h * 5}px` }}></span>
                ))}
              </div>
            ) : (
              "🎤 Speak"
            )}
          </button>
        </div>

        <button
          className="translate-btn"
          onClick={() => handleTranslate()}
          disabled={loading}
        >
          {loading ? "Translating..." : "Translate"}
        </button>

        {translation && (
          <div className="output-box">
            <h2>Translation</h2>
            <p>{translation}</p>
            <div className="output-actions">
              <button onClick={speakEnglish}>🔊 Pronounce English</button>
            </div>
          </div>
        )}

        {history.length > 0 && (
          <div className="history-section">
            <h3>Recent Translations</h3>
            {history.map((h) => (
              <div key={h.id} className="history-item">
                <strong>{h.text}</strong> → {h.translation}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Translate;
