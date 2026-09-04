import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "דשבורד", icon: "📊" },
  { to: "/networth", label: "הון ונכסים", icon: "🏦" },
  { to: "/transactions", label: "עסקאות", icon: "💳" },
  { to: "/upload", label: "העלאת קבצים", icon: "📂" },
  { to: "/budget", label: "תקציב", icon: "🎯" },
  { to: "/files", label: "קבצים", icon: "📁" },
];

export default function Sidebar() {
  return (
    <aside style={{
      width: 220, background: "#1e293b", color: "#fff", minHeight: "100vh",
      padding: "24px 0", display: "flex", flexDirection: "column", gap: 4,
      position: "fixed", right: 0, top: 0, zIndex: 100
    }}>
      <div style={{ padding: "0 20px 24px", fontSize: 18, fontWeight: 700, color: "#60a5fa" }}>
        💰 רועי וניקול
      </div>
      {links.map(l => (
        <NavLink key={l.to} to={l.to} end={l.to === "/"} style={({ isActive }) => ({
          display: "flex", alignItems: "center", gap: 10, padding: "12px 20px",
          color: isActive ? "#60a5fa" : "#cbd5e1", textDecoration: "none",
          background: isActive ? "#334155" : "transparent",
          borderRight: isActive ? "3px solid #60a5fa" : "3px solid transparent",
          fontSize: 15,
        })}>
          <span>{l.icon}</span> {l.label}
        </NavLink>
      ))}
    </aside>
  );
}
