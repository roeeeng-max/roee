import { useEffect, useState } from "react";
import { getBudget, setBudget, getStatsCategories } from "../api";

const CATEGORIES = ["סופרמרקט","דלק","מסעדות","בריאות","ביגוד","בידור","חינוך","תחבורה","חשמל/מים","תקשורת","כללי"];
const fmt = (n) => `₪${Number(n).toLocaleString("he-IL", { maximumFractionDigits: 0 })}`;

export default function Budget() {
  const [month, setMonth] = useState(() => new Date().toISOString().slice(0, 7));
  const [budgets, setBudgets] = useState([]);
  const [spent, setSpent] = useState([]);
  const [newCat, setNewCat] = useState(CATEGORIES[0]);
  const [newLimit, setNewLimit] = useState("");
  const [saving, setSaving] = useState(false);

  const load = async () => {
    const [b, s] = await Promise.all([getBudget(month), getStatsCategories(month)]);
    setBudgets(b);
    setSpent(s);
  };

  useEffect(() => { load(); }, [month]);

  const save = async () => {
    if (!newLimit) return;
    setSaving(true);
    await setBudget({ category: newCat, monthly_limit: parseFloat(newLimit), month });
    setNewLimit("");
    await load();
    setSaving(false);
  };

  const spentMap = Object.fromEntries(spent.map(s => [s.category, s.total]));

  return (
    <div style={{ direction: "rtl", padding: 32, fontFamily: "inherit" }}>
      <h1 style={{ fontSize: 26, fontWeight: 700, marginBottom: 24 }}>ניהול תקציב</h1>

      <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 28 }}>
        <label style={{ fontWeight: 600 }}>חודש:</label>
        <input type="month" value={month} onChange={e => setMonth(e.target.value)}
          style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #e2e8f0", fontSize: 14 }} />
      </div>

      {/* Add budget */}
      <div style={{ background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 1px 3px rgba(0,0,0,.1)", marginBottom: 24 }}>
        <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>הגדר תקציב לקטגוריה</h2>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          <select value={newCat} onChange={e => setNewCat(e.target.value)}
            style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #e2e8f0", fontSize: 14 }}>
            {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <input type="number" placeholder="סכום תקציב ₪" value={newLimit} onChange={e => setNewLimit(e.target.value)}
            style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #e2e8f0", fontSize: 14, width: 180 }} />
          <button onClick={save} disabled={saving}
            style={{ background: "#3b82f6", color: "#fff", border: "none", borderRadius: 8, padding: "8px 20px", cursor: "pointer", fontWeight: 600 }}>
            {saving ? "שומר..." : "שמור"}
          </button>
        </div>
      </div>

      {/* Budget list */}
      <div style={{ background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 1px 3px rgba(0,0,0,.1)" }}>
        <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 20 }}>מצב תקציב - {month}</h2>
        {budgets.length === 0 && <p style={{ color: "#94a3b8" }}>לא הוגדרו תקציבים לחודש זה</p>}
        {budgets.map(b => {
          const s = spentMap[b.category] || 0;
          const pct = Math.min((s / b.monthly_limit) * 100, 100);
          const over = s > b.monthly_limit;
          return (
            <div key={b.id} style={{ marginBottom: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                <span style={{ fontWeight: 600, fontSize: 15 }}>{b.category}</span>
                <span style={{ color: over ? "#ef4444" : "#64748b", fontWeight: over ? 700 : 400 }}>
                  {fmt(s)} / {fmt(b.monthly_limit)}
                  {over && " ⚠️ חריגה!"}
                </span>
              </div>
              <div style={{ background: "#f1f5f9", borderRadius: 8, height: 12 }}>
                <div style={{
                  width: `${pct}%`, height: "100%", borderRadius: 8,
                  background: over ? "#ef4444" : pct > 80 ? "#f59e0b" : "#34d399",
                  transition: "width .3s"
                }} />
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4, fontSize: 12, color: "#94a3b8" }}>
                <span>{pct.toFixed(0)}% נוצל</span>
                <span>נותר: {fmt(Math.max(b.monthly_limit - s, 0))}</span>
              </div>
            </div>
          );
        })}

        {/* Unbudgeted categories */}
        {spent.filter(s => !budgets.find(b => b.category === s.category)).length > 0 && (
          <>
            <hr style={{ margin: "20px 0", borderColor: "#f1f5f9" }} />
            <h3 style={{ fontSize: 14, color: "#94a3b8", marginBottom: 12 }}>קטגוריות ללא תקציב</h3>
            {spent.filter(s => !budgets.find(b => b.category === s.category)).map(s => (
              <div key={s.category} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid #f1f5f9" }}>
                <span>{s.category}</span>
                <span style={{ color: "#ef4444", fontWeight: 600 }}>{fmt(s.total)}</span>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}
