import { useState } from "react";

const DEFAULT_CHANNELS = [
  { id: 1, name: "Daily Talks by Ankur", platform: "YouTube", emoji: "🎙️", color: "#ff000022", textColor: "#ff6666", desc: "Geopolitics & current affairs — RealLifeLore Hindi style" },
  { id: 2, name: "Doodle Masti", platform: "YouTube", emoji: "🎨", color: "#ff000022", textColor: "#ff6666", desc: "Kids educational channel — animated videos" },
  { id: 3, name: "USMarketPulse", platform: "Instagram", emoji: "📈", color: "#e91e6322", textColor: "#e91e63", desc: "US stock market updates & analysis" },
];

export default function Channels() {
  const [channels, setChannels] = useState(DEFAULT_CHANNELS);
  const [adding, setAdding] = useState(false);
  const [newName, setNewName] = useState("");
  const [newPlatform, setNewPlatform] = useState("YouTube");

  const addChannel = () => {
    if (!newName.trim()) return;
    setChannels([...channels, {
      id: Date.now(), name: newName, platform: newPlatform,
      emoji: newPlatform === "YouTube" ? "📺" : "📸",
      color: newPlatform === "YouTube" ? "#ff000022" : "#e91e6322",
      textColor: newPlatform === "YouTube" ? "#ff6666" : "#e91e63",
      desc: "New channel"
    }]);
    setNewName("");
    setAdding(false);
  };

  return (
    <div className="channels-page">
      <h1 className="page-title">Channels 📺</h1>
      <p className="page-sub">Apne sabhi channels manage karo</p>

      <div className="channels-grid">
        {channels.map((ch) => (
          <div key={ch.id} className="channel-card">
            <div className="channel-header">
              <div className="channel-avatar" style={{ background: ch.color }}>
                {ch.emoji}
              </div>
              <div>
                <div className="channel-name">{ch.name}</div>
                <div className="channel-platform">{ch.platform}</div>
              </div>
            </div>
            <span className="channel-badge" style={{ background: ch.color, color: ch.textColor }}>
              {ch.platform}
            </span>
            <div className="channel-desc">{ch.desc}</div>
          </div>
        ))}

        {adding ? (
          <div className="channel-card">
            <input className="topic-input" placeholder="Channel name..." value={newName} onChange={(e) => setNewName(e.target.value)} style={{ marginBottom: "12px" }} />
            <select className="channel-select" value={newPlatform} onChange={(e) => setNewPlatform(e.target.value)} style={{ marginBottom: "12px", width: "100%" }}>
              <option>YouTube</option>
              <option>Instagram</option>
            </select>
            <div style={{ display: "flex", gap: "8px" }}>
              <button className="btn-primary" onClick={addChannel}>Add</button>
              <button className="btn-secondary" onClick={() => setAdding(false)}>Cancel</button>
            </div>
          </div>
        ) : (
          <div className="add-channel-card" onClick={() => setAdding(true)}>➕ Add Channel</div>
        )}
      </div>
    </div>
  );
}