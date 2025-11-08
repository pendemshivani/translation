import axios from "axios";
import { useState } from "react";
import "./Translate.css";

const Translate = () => {
  const [text, setText] = useState("");
  const [sourceLang, setSourceLang] = useState("en");
  const [targetLang, setTargetLang] = useState("te");
  const [translation, setTranslation] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleTranslate = async () => {
    if (!text.trim()) return alert("Please enter text to translate!");
    setLoading(true);
    setTranslation("");
    try {
      const res = await axios.post("http://127.0.0.1:8000/translate", {
        text,
        source_lang: sourceLang,
        target_lang: targetLang,
      });
      setTranslation(res.data.translation);
    } catch (err) {
      console.error(err);
      setTranslation("⚠️ Translation failed. Check console for details.");
    } finally {
      setLoading(false);
    }
  };

  const swapLanguages = () => {
    setSourceLang(targetLang);
    setTargetLang(sourceLang);
    setTranslation("");
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(translation);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const handleClear = () => {
    setText("");
    setTranslation("");
  };

  return (
    <div className="translate-container">
      <h1>🌐 Pro Translator</h1>
      <p className="tagline">English ↔ Telugu made simple</p>

      <textarea
        rows="4"
        placeholder="Type your text here..."
        value={text}
        maxLength={500}
        onChange={(e) => setText(e.target.value)}
      />
      <div className="char-count">{text.length}/500 characters</div>

      <div className="language-selectors">
        <select
          value={sourceLang}
          onChange={(e) => setSourceLang(e.target.value)}
        >
          <option value="en">English</option>
          <option value="te">Telugu</option>
        </select>
        <button className="swap-btn" onClick={swapLanguages}>
          ⇄ Swap
        </button>
        <select
          value={targetLang}
          onChange={(e) => setTargetLang(e.target.value)}
        >
          <option value="te">Telugu</option>
          <option value="en">English</option>
        </select>
      </div>

      <div className="button-group">
        <button
          onClick={handleTranslate}
          className="translate-btn"
          disabled={loading}
        >
          {loading ? "Translating..." : "Translate"}
        </button>
        <button onClick={handleClear} className="clear-btn">
          Clear
        </button>
      </div>

      {translation && (
        <div className="translation-output">
          <h2>Translation:</h2>
          <p>{translation}</p>
          <button onClick={handleCopy} className="copy-btn">
            {copied ? "✅ Copied!" : "📋 Copy"}
          </button>
        </div>
      )}

      <div className="footer-info">
        <small>
          Source: {sourceLang.toUpperCase()} | Target: {targetLang.toUpperCase()}
        </small>
      </div>
    </div>
  );
};

export default Translate;
