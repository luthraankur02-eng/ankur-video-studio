import { useState } from "react";

const CHANNELS = [
  { id: "daily_talks", name: "Daily Talks by Ankur", style: "RealLifeLore Hindi geopolitics" },
  { id: "doodle_masti", name: "Doodle Masti", style: "Kids educational Hindi" },
  { id: "usmarket", name: "USMarketPulse", style: "US stock market analysis" },
];

export default function ScriptEditor() {
  const [topic, setTopic] = useState("");
  const [channel, setChannel] = useState("daily_talks");
  const [script, setScript] = useState("");
  const [loading, setLoading] = useState(false);

  const selectedChannel = CHANNELS.find((c) => c.id === channel);

  const generateScript = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    setScript("");
    try {
      const response = await fetch("http://localhost:5000/generate-script", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: `Tu ek expert YouTube script writer hai. Channel: "${selectedChannel.name}" (Style: ${selectedChannel.style}). Topic: "${topic}". Ek engaging Hindi YouTube script likho jisme Hook, Introduction, Main content (3-4 points), aur Conclusion ho. RealLifeLore jaisi storytelling style. Sirf script likho.`
        })
      });
      const data = await response.json();
      setScript(data.text || "Error aaya");
    } catch (err) {
      setScript("❌ Error: Server se connect nahi hua. Server chal raha hai?");
    }
    setLoading(false);
  };

  const copyScript = () => {
    navigator.clipboard.writeText(script);
    alert("Script copied!");
  };

  return (
    <div className="script-editor">
      <h1 className="page-title">Script Editor ✍️</h1>
      <p className="page-sub">AI se Hindi YouTube script generate karo</p>

      <div className="topic-row">
        <select className="channel-select" value={channel} onChange={(e) => setChannel(e.target.value)}>
          {CHANNELS.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
        <input
          className="topic-input"
          placeholder="Topic likho... jaise: Crimea situation 2026"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && generateScript()}
        />
        <button className="btn-primary" onClick={generateScript} disabled={loading || !topic.trim()}>
          {loading ? "Generating..." : "🚀 Generate"}
        </button>
      </div>

      <div className="script-output">
        {loading ? (
          <div className="loading-dots">⏳ Script generate ho rahi hai...</div>
        ) : script ? (
          <div className="script-text">{script}</div>
        ) : (
          <div className="script-placeholder">
            <span>✍️</span>
            <p>Topic daalo aur Generate dabao</p>
            <p style={{ fontSize: "12px" }}>AI RealLifeLore style Hindi script banayega</p>
          </div>
        )}
      </div>

      {script && (
        <div className="script-actions">
          <button className="btn-primary" onClick={copyScript}>📋 Copy Script</button>
          <button className="btn-secondary" onClick={() => setScript("")}>🗑️ Clear</button>
          <button className="btn-secondary" onClick={generateScript}>🔄 Regenerate</button>
        </div>
      )}
    </div>
  );
}