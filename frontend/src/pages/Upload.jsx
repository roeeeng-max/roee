import { useState, useRef } from "react";
import { uploadFile } from "../api";

export default function Upload() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef();

  const handle = async (file) => {
    if (!file) return;
    setLoading(true);
    setStatus(null);
    try {
      const res = await uploadFile(file);
      setStatus({ ok: true, msg: `✅ הועלה בהצלחה! יובאו ${res.imported} עסקאות מ-${res.filename}` });
    } catch (e) {
      setStatus({ ok: false, msg: `❌ שגיאה: ${e.response?.data?.detail || e.message}` });
    }
    setLoading(false);
  };

  return (
    <div style={{ direction: "rtl", padding: 32, fontFamily: "inherit" }}>
      <h1 style={{ fontSize: 26, fontWeight: 700, marginBottom: 8 }}>העלאת קבצים</h1>
      <p style={{ color: "#64748b", marginBottom: 32 }}>תמיכה ב-Excel (.xlsx/.xls), CSV, ו-PDF של דפי בנק</p>

      {/* Drop zone */}
      <div
        onDragOver={e => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={e => { e.preventDefault(); setDragging(false); handle(e.dataTransfer.files[0]); }}
        onClick={() => inputRef.current.click()}
        style={{
          border: `2px dashed ${dragging ? "#3b82f6" : "#cbd5e1"}`,
          borderRadius: 16, padding: 60, textAlign: "center", cursor: "pointer",
          background: dragging ? "#eff6ff" : "#f8fafc",
          transition: "all .2s",
        }}
      >
        <div style={{ fontSize: 48, marginBottom: 12 }}>📂</div>
        <div style={{ fontSize: 18, fontWeight: 600, color: "#334155", marginBottom: 8 }}>
          גרור קובץ לכאן או לחץ לבחירה
        </div>
        <div style={{ color: "#94a3b8", fontSize: 14 }}>Excel, CSV, PDF</div>
        <input ref={inputRef} type="file" accept=".xlsx,.xls,.csv,.pdf" hidden onChange={e => handle(e.target.files[0])} />
      </div>

      {loading && (
        <div style={{ marginTop: 24, padding: 16, background: "#eff6ff", borderRadius: 10, textAlign: "center", color: "#3b82f6" }}>
          ⏳ מעבד קובץ...
        </div>
      )}

      {status && (
        <div style={{
          marginTop: 24, padding: 16, borderRadius: 10, textAlign: "center",
          background: status.ok ? "#f0fdf4" : "#fef2f2",
          color: status.ok ? "#16a34a" : "#dc2626",
          fontSize: 16, fontWeight: 600,
        }}>
          {status.msg}
        </div>
      )}

      <div style={{ marginTop: 40, background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 1px 3px rgba(0,0,0,.1)" }}>
        <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>איך זה עובד?</h2>
        <ul style={{ color: "#475569", lineHeight: 2, paddingRight: 20 }}>
          <li>המערכת מזהה אוטומטית עמודות תאריך, תיאור וסכום</li>
          <li>קטגוריות מוקצות אוטומטית לפי שם הסוחר</li>
          <li>ניתן לערוך קטגוריות ואחראי בעמוד העסקאות</li>
          <li>קבצי PDF של דפי בנק נסרקים לאיתור טבלאות</li>
        </ul>
      </div>
    </div>
  );
}
