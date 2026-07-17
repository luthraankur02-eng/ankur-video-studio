export default function Dashboard({ setActive }) {
  const channels = [
    { name: "Daily Talks by Ankur", platform: "YouTube", emoji: "🎙️" },
    { name: "Doodle Masti", platform: "YouTube", emoji: "🎨" },
    { name: "USMarketPulse", platform: "Instagram", emoji: "📈" },
  ];

  return (
    <div className="dashboard">
      <h1 className="page-title">Welcome back, Ankur! 👋</h1>
      <p className="page-sub">Ankur Video Studio — Create, Edit & Publish</p>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Channels</div>
          <div className="stat-value">3</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Scripts Generated</div>
          <div className="stat-value">0</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Videos Published</div>
          <div className="stat-value">0</div>
        </div>
      </div>

      <div className="quick-actions">
        <div className="section-title">Quick Actions</div>
        <div className="actions-grid">
          <div className="action-card" onClick={() => setActive("script")}>
            <div className="action-emoji">✍️</div>
            <div className="action-title">Generate Script</div>
            <div className="action-desc">AI se RealLifeLore style Hindi script banao</div>
          </div>
          <div className="action-card" onClick={() => setActive("channels")}>
            <div className="action-emoji">📺</div>
            <div className="action-title">Manage Channels</div>
            <div className="action-desc">YouTube & Instagram channels manage karo</div>
          </div>
          <div className="action-card">
            <div className="action-emoji">🎬</div>
            <div className="action-title">Video Editor</div>
            <div className="action-desc">Coming soon — CapCut style editor</div>
          </div>
          <div className="action-card">
            <div className="action-emoji">🚀</div>
            <div className="action-title">Auto Publish</div>
            <div className="action-desc">Coming soon — direct upload to all channels</div>
          </div>
        </div>
      </div>

      <div>
        <div className="section-title">Your Channels</div>
        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          {channels.map((ch) => (
            <div key={ch.name} style={{
              background: "#1a1a1a", border: "1px solid #2a2a2a",
              borderRadius: "10px", padding: "14px 16px",
              display: "flex", alignItems: "center", gap: "12px"
            }}>
              <span style={{ fontSize: "24px" }}>{ch.emoji}</span>
              <div>
                <div style={{ fontSize: "14px", fontWeight: 600 }}>{ch.name}</div>
                <div style={{ fontSize: "12px", color: "#888" }}>{ch.platform}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}