import { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import {
  getVaultStatus, setupVault, unlockVault, lockVault,
  getInstitutions, getConnections, addConnection,
  updateManualBalance, syncConnection, deleteConnection, getNetWorth,
} from "../api";

const fmt = (n) => `₪${Number(n || 0).toLocaleString("he-IL", { maximumFractionDigits: 0 })}`;

const CATEGORY_LABELS = {
  bank: "בנק",
  credit_card: "כרטיס אשראי",
  investment_house: "בית השקעות",
  insurance_pension: "ביטוח ופנסיה",
  other: "אחר",
};
const CATEGORY_ICONS = {
  bank: "🏦", credit_card: "💳", investment_house: "📈", insurance_pension: "🛡️", other: "🗂️",
};
const FIELD_LABELS = {
  username: "שם משתמש", password: "סיסמה", userCode: "קוד משתמש/ת.ז",
  id: "מספר זהות", num: "מספר חשבון/סניף", card6Digits: "6 ספרות אחרונות בכרטיס",
  nationalID: "מספר זהות",
};

function errMsg(e, fallback) {
  return e?.response?.data?.detail || fallback;
}

export default function NetWorth() {
  const [vaultStatus, setVaultStatus] = useState(null);
  const [institutions, setInstitutions] = useState(null);
  const [nw, setNw] = useState(null);
  const [showAdd, setShowAdd] = useState(false);
  const [busyId, setBusyId] = useState(null);
  const [notice, setNotice] = useState(null);

  const refreshAll = () => {
    getVaultStatus().then(setVaultStatus);
    getInstitutions().then(setInstitutions);
    getNetWorth().then(setNw);
  };

  useEffect(refreshAll, []);

  if (!vaultStatus || !institutions || !nw) {
    return <div style={{ padding: 40, textAlign: "center", color: "#94a3b8" }}>טוען...</div>;
  }

  const handleSync = async (id) => {
    setBusyId(id);
    try {
      await syncConnection(id);
      refreshAll();
    } catch (e) {
      setNotice({ type: "error", text: errMsg(e, "הסנכרון נכשל") });
    } finally {
      setBusyId(null);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("למחוק את החיבור? הפעולה לא תמחק את הסיסמה מהבנק, רק תסיר אותו מכאן.")) return;
    await deleteConnection(id);
    refreshAll();
  };

  const handleEditManualBalance = async (conn) => {
    const val = window.prompt(`עדכון יתרה עבור ${conn.display_name}:`, conn.last_balance ?? 0);
    if (val === null) return;
    const num = Number(val);
    if (Number.isNaN(num)) return;
    await updateManualBalance(conn.id, num);
    refreshAll();
  };

  return (
    <div style={{ direction: "rtl", padding: 32 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 style={{ fontSize: 26, fontWeight: 700, color: "#1e293b" }}>הון ונכסים</h1>
        <VaultBadge vaultStatus={vaultStatus} onChange={refreshAll} />
      </div>

      {notice && (
        <div style={{
          background: notice.type === "error" ? "#fef2f2" : "#f0fdf4",
          color: notice.type === "error" ? "#b91c1c" : "#166534",
          padding: "10px 16px", borderRadius: 8, marginBottom: 16, fontSize: 14,
          display: "flex", justifyContent: "space-between",
        }}>
          <span>{notice.text}</span>
          <span style={{ cursor: "pointer" }} onClick={() => setNotice(null)}>✕</span>
        </div>
      )}

      {!vaultStatus.exists && <VaultSetupCard onDone={refreshAll} />}
      {vaultStatus.exists && !vaultStatus.unlocked && <VaultUnlockCard onDone={refreshAll} />}

      {/* KPI */}
      <div style={{
        background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 1px 3px rgba(0,0,0,.1)",
        marginBottom: 24, borderTop: "4px solid #34d399",
      }}>
        <div style={{ color: "#64748b", fontSize: 13, marginBottom: 6 }}>סה״כ הון נטו</div>
        <div style={{ fontSize: 36, fontWeight: 700, color: nw.total >= 0 ? "#1e293b" : "#ef4444" }}>{fmt(nw.total)}</div>
        <div style={{ display: "flex", gap: 8, marginTop: 12, flexWrap: "wrap" }}>
          {nw.by_category.map((c) => (
            <span key={c.category} style={{
              background: "#f1f5f9", borderRadius: 999, padding: "4px 12px", fontSize: 13, color: "#334155",
            }}>
              {CATEGORY_ICONS[c.category] || "🗂️"} {CATEGORY_LABELS[c.category] || c.category}: {fmt(c.total)}
            </span>
          ))}
        </div>
      </div>

      {nw.history.length > 1 && (
        <div style={{ background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 1px 3px rgba(0,0,0,.1)", marginBottom: 24 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16, color: "#1e293b" }}>הון לאורך זמן</h2>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={nw.history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" tick={{ fontSize: 11 }} />
              <YAxis tickFormatter={(v) => `₪${(v / 1000).toFixed(0)}K`} />
              <Tooltip formatter={(v) => fmt(v)} />
              <Line type="monotone" dataKey="total" stroke="#34d399" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Connections */}
      <div style={{ background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 1px 3px rgba(0,0,0,.1)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, color: "#1e293b" }}>חיבורים</h2>
          <button onClick={() => setShowAdd(true)} style={btnPrimary}>+ הוסף חיבור</button>
        </div>

        {nw.connections.length === 0 && (
          <div style={{ color: "#94a3b8", padding: 20, textAlign: "center" }}>עדיין לא חיברת גופים - לחצו על "הוסף חיבור" כדי להתחיל.</div>
        )}

        {nw.connections.map((c) => (
          <ConnectionRow
            key={c.id}
            conn={c}
            busy={busyId === c.id}
            onSync={() => handleSync(c.id)}
            onEditBalance={() => handleEditManualBalance(c)}
            onDelete={() => handleDelete(c.id)}
          />
        ))}
      </div>

      {showAdd && (
        <AddConnectionModal
          institutions={institutions}
          vaultStatus={vaultStatus}
          onClose={() => setShowAdd(false)}
          onVaultChange={refreshAll}
          onAdded={() => { setShowAdd(false); refreshAll(); }}
          onError={(msg) => setNotice({ type: "error", text: msg })}
        />
      )}
    </div>
  );
}

function VaultBadge({ vaultStatus, onChange }) {
  if (!vaultStatus.exists) return null;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <span style={{
        fontSize: 13, padding: "6px 12px", borderRadius: 999,
        background: vaultStatus.unlocked ? "#f0fdf4" : "#fef2f2",
        color: vaultStatus.unlocked ? "#166534" : "#b91c1c",
      }}>
        {vaultStatus.unlocked ? "🔓 הכספת פתוחה" : "🔒 הכספת נעולה"}
      </span>
      {vaultStatus.unlocked && (
        <button onClick={async () => { await lockVault(); onChange(); }} style={btnGhost}>נעל</button>
      )}
    </div>
  );
}

function VaultSetupCard({ onDone }) {
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    if (password !== confirm) { setError("הסיסמאות לא תואמות"); return; }
    try {
      await setupVault(password);
      onDone();
    } catch (e) {
      setError(errMsg(e, "שגיאה בהגדרת הכספת"));
    }
  };

  return (
    <Card title="🔐 הגדרת כספת סיסמאות">
      <p style={{ color: "#64748b", fontSize: 14, marginBottom: 16 }}>
        כדי לחבר בנקים ולקבל יתרות באופן אוטומטי, קודם צריך להגדיר סיסמת-על אחת שתשמש להצפנת פרטי ההתחברות
        לבנקים - הם נשמרים מוצפנים במחשב שלכם בלבד, ואף אחד (כולל אנחנו) לא יכול לקרוא אותם בלי הסיסמה הזו.
        אין צורך בסיסמת-על כדי להוסיף בתי השקעות/ביטוח באופן ידני.
      </p>
      <form onSubmit={submit} style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <input type="password" placeholder="סיסמת-על (6+ תווים)" value={password} onChange={(e) => setPassword(e.target.value)} style={input} />
        <input type="password" placeholder="אימות סיסמה" value={confirm} onChange={(e) => setConfirm(e.target.value)} style={input} />
        <button type="submit" style={btnPrimary}>הגדר כספת</button>
      </form>
      {error && <div style={{ color: "#ef4444", fontSize: 13, marginTop: 8 }}>{error}</div>}
    </Card>
  );
}

function VaultUnlockCard({ onDone }) {
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    try {
      await unlockVault(password);
      onDone();
    } catch (e) {
      setError(errMsg(e, "סיסמה שגויה"));
    }
  };

  return (
    <Card title="🔒 פתיחת כספת">
      <form onSubmit={submit} style={{ display: "flex", gap: 8 }}>
        <input type="password" placeholder="סיסמת-על" value={password} onChange={(e) => setPassword(e.target.value)} style={input} />
        <button type="submit" style={btnPrimary}>פתח</button>
      </form>
      {error && <div style={{ color: "#ef4444", fontSize: 13, marginTop: 8 }}>{error}</div>}
    </Card>
  );
}

const STATUS_LABELS = {
  never: { text: "טרם סונכרן", color: "#94a3b8" },
  ok: { text: "מסונכרן", color: "#16a34a" },
  error: { text: "שגיאה", color: "#ef4444" },
  locked: { text: "ממתין לפתיחת כספת", color: "#f59e0b" },
};

function ConnectionRow({ conn, busy, onSync, onEditBalance, onDelete }) {
  const st = STATUS_LABELS[conn.status] || STATUS_LABELS.never;
  return (
    <div style={{
      display: "flex", alignItems: "center", justifyContent: "space-between",
      padding: "14px 4px", borderBottom: "1px solid #e2e8f0", gap: 12, flexWrap: "wrap",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, minWidth: 220 }}>
        <span style={{ fontSize: 22 }}>{CATEGORY_ICONS[conn.category] || "🗂️"}</span>
        <div>
          <div style={{ fontWeight: 600, color: "#1e293b" }}>{conn.display_name}</div>
          <div style={{ fontSize: 12, color: "#94a3b8" }}>
            {CATEGORY_LABELS[conn.category] || conn.category} · {conn.person}
            {conn.kind === "manual" && " · ידני"}
          </div>
        </div>
      </div>

      <div style={{ fontWeight: 700, fontSize: 16, color: (conn.last_balance ?? 0) >= 0 ? "#1e293b" : "#ef4444" }}>
        {fmt(conn.last_balance)}
      </div>

      <div style={{ fontSize: 12, color: st.color, minWidth: 130 }}>
        {st.text}
        {conn.last_error && <div title={conn.last_error} style={{ color: "#ef4444", maxWidth: 220, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{conn.last_error}</div>}
        {conn.last_synced_at && <div style={{ color: "#94a3b8" }}>עודכן: {conn.last_synced_at.slice(0, 16).replace("T", " ")}</div>}
      </div>

      <div style={{ display: "flex", gap: 8 }}>
        {conn.kind === "scraped" && (
          <button onClick={onSync} disabled={busy} style={btnGhost}>{busy ? "מסנכרן..." : "🔄 סנכרן"}</button>
        )}
        {conn.kind === "manual" && (
          <button onClick={onEditBalance} style={btnGhost}>✏️ עדכן יתרה</button>
        )}
        <button onClick={onDelete} style={{ ...btnGhost, color: "#ef4444" }}>🗑️</button>
      </div>
    </div>
  );
}

function AddConnectionModal({ institutions, vaultStatus, onClose, onVaultChange, onAdded, onError }) {
  const [tab, setTab] = useState(institutions.node_available ? "scraped" : "manual");
  const [institutionId, setInstitutionId] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [person, setPerson] = useState("משותף");
  const [balance, setBalance] = useState("");
  const [fields, setFields] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const list = tab === "scraped" ? institutions.scraped : institutions.manual;
  const selected = list.find((i) => i.id === institutionId);

  const submit = async (e) => {
    e.preventDefault();
    if (!institutionId) return;
    setSubmitting(true);
    try {
      const payload = {
        institution_id: institutionId,
        kind: tab,
        display_name: displayName || undefined,
        person,
      };
      if (tab === "scraped") payload.credentials = fields;
      if (tab === "manual") payload.balance = Number(balance || 0);
      await addConnection(payload);
      onAdded();
    } catch (err) {
      onError(err?.response?.data?.detail || "הוספת החיבור נכשלה");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={overlay} onClick={onClose}>
      <div style={modal} onClick={(e) => e.stopPropagation()}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
          <h2 style={{ fontSize: 18, fontWeight: 700 }}>הוספת חיבור</h2>
          <span style={{ cursor: "pointer" }} onClick={onClose}>✕</span>
        </div>

        <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
          <button
            onClick={() => { setTab("scraped"); setInstitutionId(""); }}
            style={tab === "scraped" ? tabActive : tabInactive}
          >🏦 בנק / כרטיס אשראי (אוטומטי)</button>
          <button
            onClick={() => { setTab("manual"); setInstitutionId(""); }}
            style={tab === "manual" ? tabActive : tabInactive}
          >📈 בית השקעות / ביטוח (ידני)</button>
        </div>

        {tab === "scraped" && !institutions.scraper_ready && (
          <div style={{ background: "#fffbeb", color: "#92400e", padding: 10, borderRadius: 8, fontSize: 13, marginBottom: 12 }}>
            {institutions.node_available
              ? "חבילות הסקרייפר לא הותקנו עדיין - הריצו npm install בתיקיית scraper (ראו scraper/README.md)."
              : "Node.js לא נמצא במחשב - חיבור אוטומטי לבנקים דורש התקנתו (ראו scraper/README.md). אפשר בינתיים להוסיף בתי השקעות/ביטוח ידנית."}
          </div>
        )}

        {tab === "scraped" && !vaultStatus.unlocked && (
          <div style={{ background: "#fef2f2", color: "#b91c1c", padding: 10, borderRadius: 8, fontSize: 13, marginBottom: 12 }}>
            יש לפתוח את הכספת (למעלה בעמוד) לפני הוספת חיבור בנקאי אוטומטי.
          </div>
        )}

        <form onSubmit={submit}>
          <div style={{ marginBottom: 12 }}>
            <label style={label}>מוסד</label>
            <select value={institutionId} onChange={(e) => setInstitutionId(e.target.value)} style={input} required>
              <option value="">בחרו מוסד...</option>
              {list.map((i) => <option key={i.id} value={i.id}>{i.name}</option>)}
            </select>
          </div>

          <div style={{ marginBottom: 12 }}>
            <label style={label}>שם תצוגה (אופציונלי)</label>
            <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder={selected?.name || ""} style={input} />
          </div>

          <div style={{ marginBottom: 12 }}>
            <label style={label}>שייך ל</label>
            <select value={person} onChange={(e) => setPerson(e.target.value)} style={input}>
              <option>משותף</option>
              <option>רועי</option>
              <option>ניקול</option>
            </select>
          </div>

          {tab === "scraped" && selected && selected.fields.map((f) => (
            <div key={f} style={{ marginBottom: 12 }}>
              <label style={label}>{FIELD_LABELS[f] || f}</label>
              <input
                type={f.toLowerCase().includes("password") ? "password" : "text"}
                value={fields[f] || ""}
                onChange={(e) => setFields({ ...fields, [f]: e.target.value })}
                style={input}
                required
              />
            </div>
          ))}

          {tab === "manual" && (
            <div style={{ marginBottom: 12 }}>
              <label style={label}>יתרה נוכחית (₪)</label>
              <input type="number" value={balance} onChange={(e) => setBalance(e.target.value)} style={input} />
            </div>
          )}

          <button
            type="submit"
            disabled={submitting || !institutionId || (tab === "scraped" && (!vaultStatus.unlocked || !institutions.scraper_ready))}
            style={{ ...btnPrimary, width: "100%", marginTop: 8, opacity: submitting ? 0.6 : 1 }}
          >
            {submitting ? "מוסיף..." : "הוסף חיבור"}
          </button>
        </form>
      </div>
    </div>
  );
}

function Card({ title, children }) {
  return (
    <div style={{ background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 1px 3px rgba(0,0,0,.1)", marginBottom: 24 }}>
      <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12, color: "#1e293b" }}>{title}</h2>
      {children}
    </div>
  );
}

const input = {
  padding: "10px 12px", borderRadius: 8, border: "1px solid #cbd5e1", fontSize: 14, flex: 1, minWidth: 160,
  fontFamily: "inherit", direction: "rtl",
};
const label = { display: "block", fontSize: 13, color: "#64748b", marginBottom: 4 };
const btnPrimary = {
  background: "#3b82f6", color: "#fff", border: "none", borderRadius: 8, padding: "10px 16px",
  fontSize: 14, fontWeight: 600, cursor: "pointer",
};
const btnGhost = {
  background: "#f1f5f9", color: "#334155", border: "none", borderRadius: 8, padding: "8px 12px",
  fontSize: 13, cursor: "pointer",
};
const tabActive = { ...btnGhost, background: "#3b82f6", color: "#fff" };
const tabInactive = btnGhost;
const overlay = {
  position: "fixed", inset: 0, background: "rgba(15,23,42,.5)", display: "flex",
  alignItems: "center", justifyContent: "center", zIndex: 1000,
};
const modal = {
  background: "#fff", borderRadius: 12, padding: 24, width: 480, maxWidth: "90vw",
  maxHeight: "85vh", overflowY: "auto", direction: "rtl",
};
