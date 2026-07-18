import { useState } from "react";
import ScriptEditor from "./components/ScriptEditor";
import Channels from "./components/Channels";
import Dashboard from "./components/Dashboard";
import VideoEditor from "./components/VideoEditor";
import "./App.css";

const NAV = [
  { id: "dashboard", label: "Dashboard", icon: "📊" },
  { id: "script", label: "Script Editor", icon: "📝" },
  { id: "editor", label: "Video Editor", icon: "🎬" },
  { id: "channels", label: "Channels", icon: "📺" },
];

export default function App() {
  const [active, setActive] = useState("dashboard");

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <span className="logo-icon">🎬</span>
          <span className="logo-text">Ankur Video Studio</span>
        </div>
        <nav className="sidebar-nav">
          {NAV.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${active === item.id ? "active" : ""}`}
              onClick={() => setActive(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">v1.1.0</div>
      </aside>
      <main className="main-content">
        {active === "dashboard" && <Dashboard setActive={setActive} />}
        {active === "script" && <ScriptEditor />}
        {active === "editor" && <VideoEditor />}
        {active === "channels" && <Channels />}
      </main>
    </div>
  );
}