import { useEffect, useState } from "react";
import { getTransactions, updateTransaction, deleteTransaction } from "../api";

const CATEGORIES = ["כללי","סופרמרקט","דלק","מסעדות","בריאות","ביגוד","בידור","חינוך","תחבורה","חשמל/מים","תקשורת"];
const fmt = (n) => `₪${Number(n).toLocaleString("he-IL", { maximumFractionDigits: 0 })}`;

export default function Transactions() {
  const [data, setData] = useState({ total: 0, items: [] });
  const [filters, setFilters] = useState({ skip: 0, limit: 50, sort_by: "date", sort_dir: "desc" });
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [person, setPerson] = useState("");
  const [editing, setEditing] = useState(null);

  const load = () => {
    const params = { ...filters };
    if (search) params.search = search;
    if (category) params.category = category;
    if (person) params.person = person;
    getTransactions(params).then(setData);
  };

  useEffect(() => { load(); }, [filters, search, category, person]);

  const saveEdit = async (id) => {
    await updateTransaction(id, editing);
    setEditing(null);
    load();
  };

  const del = async (id) => {
    if (!confirm("למחוק את העסקה?")) return;
    await deleteTransaction(id);
    load();
  };

  return (
    <div style={{ direction: "rtl", padding: 32, fontFamily: "inherit" }}>
      <h1 style={{ fontSize: 26, fontWeight: 700, marginBottom: 24 }}>כל העסקאות</h1>

      {/* Filters */}
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <input
          placeholder="🔍 חיפוש תיאור..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={inputStyle}
        />
        <select value={category} onChange={e => setCategory(e.target.value)} style={inputStyle}>
          <option value="">כל הקטגוריות</option>
          {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <select value={person} onChange={e => setPerson(e.target.value)} style={inputStyle}>
          <option value="">כולם</option>
          <option value="רועי">רועי</option>
          <option value="ניקול">ניקול</option>
          <option value="משותף">משותף</option>
        </select>
        <select value={filters.sort_by} onChange={e => setFilters(f => ({ ...f, sort_by: e.target.value }))} style={inputStyle}>
          <option value="date">מיין לפי תאריך</option>
          <option value="amount">מיין לפי סכום</option>
        </select>
        <select value={filters.sort_dir} onChange={e => setFilters(f => ({ ...f, sort_dir: e.target.value }))} style={inputStyle}>
          <option value="desc">מהגבוה לנמוך</option>
          <option value="asc">מהנמוך לגבוה</option>
        </select>
      </div>

      <div style={{ marginBottom: 12, color: "#64748b", fontSize: 14 }}>
        סה״כ {data.total} עסקאות
      </div>

      <div style={{ background: "#fff", borderRadius: 12, boxShadow: "0 1px 3px rgba(0,0,0,.1)", overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
          <thead>
            <tr style={{ background: "#f8fafc" }}>
              {["תאריך","תיאור","קטגוריה","אחראי","סכום",""].map(h => (
                <th key={h} style={{ padding: "12px 16px", textAlign: "right", fontWeight: 600, color: "#475569", borderBottom: "1px solid #e2e8f0" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.items.map(t => (
              <tr key={t.id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                <td style={{ padding: "10px 16px" }}>{t.date}</td>
                <td style={{ padding: "10px 16px", maxWidth: 250 }}>{t.description}</td>
                <td style={{ padding: "10px 16px" }}>
                  {editing?.id === t.id ? (
                    <select value={editing.category} onChange={e => setEditing(ed => ({ ...ed, category: e.target.value }))} style={{ ...inputStyle, fontSize: 12, padding: "4px 8px" }}>
                      {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                  ) : (
                    <span style={{ background: "#eff6ff", color: "#3b82f6", padding: "2px 8px", borderRadius: 999, fontSize: 12 }}>{t.category}</span>
                  )}
                </td>
                <td style={{ padding: "10px 16px" }}>
                  {editing?.id === t.id ? (
                    <select value={editing.person} onChange={e => setEditing(ed => ({ ...ed, person: e.target.value }))} style={{ ...inputStyle, fontSize: 12, padding: "4px 8px" }}>
                      <option value="רועי">רועי</option>
                      <option value="ניקול">ניקול</option>
                      <option value="משותף">משותף</option>
                    </select>
                  ) : t.person}
                </td>
                <td style={{ padding: "10px 16px", fontWeight: 700, color: "#ef4444" }}>{fmt(t.amount)}</td>
                <td style={{ padding: "10px 16px" }}>
                  {editing?.id === t.id ? (
                    <div style={{ display: "flex", gap: 6 }}>
                      <button onClick={() => saveEdit(t.id)} style={btnStyle("#34d399")}>שמור</button>
                      <button onClick={() => setEditing(null)} style={btnStyle("#94a3b8")}>ביטול</button>
                    </div>
                  ) : (
                    <div style={{ display: "flex", gap: 6 }}>
                      <button onClick={() => setEditing({ id: t.id, category: t.category, person: t.person })} style={btnStyle("#60a5fa")}>ערוך</button>
                      <button onClick={() => del(t.id)} style={btnStyle("#f87171")}>מחק</button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {data.total > filters.limit && (
        <div style={{ display: "flex", gap: 12, justifyContent: "center", marginTop: 20 }}>
          <button disabled={filters.skip === 0} onClick={() => setFilters(f => ({ ...f, skip: Math.max(0, f.skip - f.limit) }))} style={btnStyle("#60a5fa")}>הקודם</button>
          <span style={{ alignSelf: "center", color: "#64748b" }}>עמוד {Math.floor(filters.skip / filters.limit) + 1}</span>
          <button disabled={filters.skip + filters.limit >= data.total} onClick={() => setFilters(f => ({ ...f, skip: f.skip + f.limit }))} style={btnStyle("#60a5fa")}>הבא</button>
        </div>
      )}
    </div>
  );
}

const inputStyle = { padding: "8px 12px", borderRadius: 8, border: "1px solid #e2e8f0", fontSize: 14, outline: "none" };
const btnStyle = (bg) => ({ background: bg, color: "#fff", border: "none", borderRadius: 6, padding: "4px 10px", cursor: "pointer", fontSize: 12 });
