import { useEffect, useState } from "react";
import { getFiles } from "../api";

export default function Files() {
  const [files, setFiles] = useState([]);

  useEffect(() => { getFiles().then(setFiles); }, []);

  return (
    <div style={{ direction: "rtl", padding: 32, fontFamily: "inherit" }}>
      <h1 style={{ fontSize: 26, fontWeight: 700, marginBottom: 24 }}>קבצים שהועלו</h1>
      {files.length === 0 ? (
        <div style={{ color: "#94a3b8", textAlign: "center", padding: 60 }}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>📁</div>
          <p>לא הועלו קבצים עדיין</p>
        </div>
      ) : (
        <div style={{ background: "#fff", borderRadius: 12, boxShadow: "0 1px 3px rgba(0,0,0,.1)", overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
            <thead>
              <tr style={{ background: "#f8fafc" }}>
                {["שם קובץ","סוג","עסקאות יובאו","תאריך העלאה"].map(h => (
                  <th key={h} style={{ padding: "12px 16px", textAlign: "right", fontWeight: 600, color: "#475569", borderBottom: "1px solid #e2e8f0" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {files.map(f => (
                <tr key={f.id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                  <td style={{ padding: "12px 16px" }}>📄 {f.filename}</td>
                  <td style={{ padding: "12px 16px" }}>
                    <span style={{ background: "#f0fdf4", color: "#16a34a", padding: "2px 8px", borderRadius: 999, fontSize: 12 }}>
                      {f.file_type}
                    </span>
                  </td>
                  <td style={{ padding: "12px 16px", fontWeight: 600 }}>{f.rows_imported}</td>
                  <td style={{ padding: "12px 16px", color: "#64748b" }}>{f.uploaded_at?.slice(0, 16)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
