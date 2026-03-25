import { useState } from "react";

const SECTIONS = [
  {
    id: "execSummary",
    title: "סיכום מנהלים",
    placeholder:
      "- סקירת העסקה (רוכש, מוכר, מבנה)\n- נתוני מפתח (הכנסות, EBITDA, צמיחה)\n- רציונל השקעה (3-5 נקודות)\n- תשואה צפויה (IRR, MOIC)\n- המלצה",
  },
  {
    id: "thesis",
    title: "תזת השקעה",
    placeholder:
      "- מנהיגות שוק / מיצוב תחרותי\n- דינמיקת ענף (הגנתי / צומח / מפוצל)\n- הזדמנויות יצירת ערך (הרחבת מרג׳ין, צמיחה, M&A)\n- יתרונות תחרותיים ברורים",
  },
  {
    id: "bizOverview",
    title: "סקירת החברה",
    placeholder:
      "- תיאור פעילות החברה\n- מודל הכנסות ומוצר/שירות\n- מגזרי עסקים עיקריים\n- מה מייחד את החברה",
  },
  {
    id: "customers",
    title: "לקוחות ושווקים",
    placeholder:
      "- שוקי קצה וסגמנטציה\n- ריכוז לקוחות (Top 5/10)\n- מבנה חוזים / נראות הכנסות\n- הזדמנויות cross-sell / upsell",
  },
  {
    id: "marketOverview",
    title: "סקירת שוק וצמיחה",
    placeholder:
      "- גודל שוק (TAM / SAM / SOM) וצמיחה\n- מגמות ענף מרכזיות\n- מחסומי כניסה\n- רוחות גב מבניות (tailwinds)",
  },
  {
    id: "competitive",
    title: "נוף תחרותי",
    placeholder:
      "- מתחרים עיקריים\n- מיצוב מול עמיתים\n- חוזקות וחולשות יחסיות",
  },
  {
    id: "financials",
    title: "ביצועים פיננסיים",
    placeholder:
      "- ביצועים היסטוריים (הכנסות, EBITDA, מרג׳ין)\n- מגמות ומנועי צמיחה מרכזיים\n- שיקולי Quality of Earnings",
  },
  {
    id: "forecast",
    title: "תחזית והערכת שווי",
    placeholder:
      "- הנחות מפתח (צמיחה, מרג׳ינים)\n- גישת הערכה (Comps, עסקאות, DCF)\n- מכפיל כניסה מול הנחת יציאה\n- ניתוח רגישות",
  },
  {
    id: "risks",
    title: "סיכונים ומיטיגציות",
    placeholder:
      "- סיכוני השקעה מרכזיים\n- אסטרטגיות הפחתה לכל סיכון\n- שיקולי תרחיש שלילי (downside)",
  },
  {
    id: "recommendation",
    title: "המלצה",
    placeholder:
      "- עמדת השקעה סופית (השקע / אל תשקיע / המשך בדיקה)\n- נימוקי תמיכה עיקריים\n- צעדים מומלצים הבאים",
  },
  {
    id: "appendices",
    title: "נספחים",
    placeholder:
      "- מבנה בעלות\n- טבלאות פיננסיות\n- ניתוחים תומכים נוספים",
  },
];

const today = new Date().toLocaleDateString("he-IL");

const initialFields = {
  dealName: "",
  firmName: "",
  date: today,
  ...Object.fromEntries(SECTIONS.map((s) => [s.id, ""])),
};

export default function ICMemo() {
  const [fields, setFields] = useState(initialFields);
  const [exporting, setExporting] = useState(false);
  const [exportMsg, setExportMsg] = useState("");

  const update = (key, val) => setFields((p) => ({ ...p, [key]: val }));

  const exportPptx = async () => {
    setExporting(true);
    setExportMsg("");
    try {
      const { default: PptxGenJS } = await import("pptxgenjs");
      const pptx = new PptxGenJS();
      pptx.layout = "LAYOUT_WIDE";

      // ---- Slide 0: Cover ----
      const cover = pptx.addSlide();
      cover.background = { color: "1E3A5F" };

      cover.addText(fields.dealName || "שם הדיל", {
        x: 0.5, y: 2.2, w: 12.3, h: 1.2,
        fontSize: 40, bold: true, color: "FFFFFF",
        align: "center", fontFace: "Arial",
        rtlMode: true,
      });

      cover.addText("תזכיר ועדת השקעות (IC Memo)", {
        x: 0.5, y: 3.55, w: 12.3, h: 0.65,
        fontSize: 20, color: "93C5FD",
        align: "center", fontFace: "Arial",
        rtlMode: true,
      });

      cover.addText(
        `${fields.firmName ? fields.firmName + "  |  " : ""}${fields.date}  |  סודי`,
        {
          x: 0.5, y: 6.8, w: 12.3, h: 0.4,
          fontSize: 12, color: "64748B",
          align: "center", fontFace: "Arial",
        }
      );

      // ---- Slides 1–11: Sections ----
      SECTIONS.forEach((section, idx) => {
        const slide = pptx.addSlide();
        slide.background = { color: "F8FAFC" };

        // Title bar
        slide.addShape(pptx.ShapeType.rect, {
          x: 0, y: 0, w: "100%", h: 1.1,
          fill: { color: "1E3A5F" },
          line: { color: "1E3A5F" },
        });

        // Section number badge
        slide.addShape(pptx.ShapeType.ellipse, {
          x: 12.2, y: 0.2, w: 0.7, h: 0.7,
          fill: { color: "3B82F6" },
          line: { color: "3B82F6" },
        });
        slide.addText(`${idx + 1}`, {
          x: 12.2, y: 0.2, w: 0.7, h: 0.7,
          fontSize: 13, bold: true, color: "FFFFFF",
          align: "center", valign: "middle", fontFace: "Arial",
        });

        slide.addText(section.title, {
          x: 0.4, y: 0.15, w: 11.6, h: 0.8,
          fontSize: 24, bold: true, color: "FFFFFF",
          align: "right", fontFace: "Arial",
          rtlMode: true,
        });

        // Content
        const raw = fields[section.id] || "";
        const lines = raw.split("\n").filter((l) => l.trim());

        if (lines.length === 0) {
          slide.addText("(ללא תוכן)", {
            x: 0.5, y: 1.4, w: 12.3, h: 5.5,
            fontSize: 16, color: "94A3B8",
            align: "right", fontFace: "Arial",
            italic: true, rtlMode: true,
          });
        } else {
          const textArr = lines.map((line) => {
            const isBullet =
              line.trim().startsWith("-") || line.trim().startsWith("•");
            const text = isBullet
              ? "• " + line.replace(/^[-•]\s*/, "")
              : line;
            return {
              text,
              options: {
                fontSize: 16,
                color: "1E293B",
                align: "right",
                fontFace: "Arial",
                breakLine: true,
                paraSpaceAfter: isBullet ? 4 : 10,
                indentLevel: isBullet ? 1 : 0,
              },
            };
          });

          slide.addText(textArr, {
            x: 0.5, y: 1.4, w: 12.3, h: 5.5,
            valign: "top",
            rtlMode: true,
          });
        }

        // Footer
        slide.addText(
          `${fields.firmName || "IC Memo"}  |  ${fields.dealName || ""}  |  CONFIDENTIAL`,
          {
            x: 0.5, y: 7.15, w: 12.3, h: 0.3,
            fontSize: 9, color: "94A3B8",
            align: "center", fontFace: "Arial",
          }
        );
      });

      const fileName = `IC_Memo_${(fields.dealName || "Draft")
        .replace(/\s+/g, "_")
        .replace(/[^\w_]/g, "")}.pptx`;

      await pptx.writeFile({ fileName });
      setExportMsg("✓ הקובץ הורד בהצלחה");
    } catch (err) {
      console.error(err);
      setExportMsg("שגיאה בייצוא – בדוק את הקונסול");
    } finally {
      setExporting(false);
      setTimeout(() => setExportMsg(""), 4000);
    }
  };

  return (
    <div
      style={{
        direction: "rtl",
        padding: 32,
        fontFamily: "'Segoe UI', Tahoma, sans-serif",
        maxWidth: 900,
      }}
    >
      <h1
        style={{
          fontSize: 26,
          fontWeight: 700,
          marginBottom: 6,
          color: "#1e293b",
        }}
      >
        📋 תזכיר ועדת השקעות
      </h1>
      <p style={{ color: "#64748b", marginBottom: 28, fontSize: 14 }}>
        מלא את הפרטים בכל סעיף ולחץ על <strong>ייצא ל-PowerPoint</strong>{" "}
        לקבלת קובץ מוכן לוועדה (12 שקפים).
        <br />
        <span style={{ fontSize: 12 }}>
          טיפ: התחל שורה ב-<code>-</code> ליצירת נקודת תבליט בשקף.
        </span>
      </p>

      {/* Cover bar */}
      <div
        style={{
          background: "#fff",
          borderRadius: 12,
          padding: 20,
          boxShadow: "0 1px 3px rgba(0,0,0,.1)",
          marginBottom: 28,
          display: "flex",
          gap: 16,
          flexWrap: "wrap",
          alignItems: "flex-end",
          border: "1px solid #e2e8f0",
        }}
      >
        <CoverField
          label="שם הדיל / חברה"
          value={fields.dealName}
          onChange={(v) => update("dealName", v)}
          placeholder="לדוג׳: רכישת חברת XYZ"
          wide
        />
        <CoverField
          label="שם הפירמה / קרן"
          value={fields.firmName}
          onChange={(v) => update("firmName", v)}
          placeholder="לדוג׳: Alpha Capital"
        />
        <CoverField
          label="תאריך"
          value={fields.date}
          onChange={(v) => update("date", v)}
          placeholder={today}
        />

        <div style={{ display: "flex", flexDirection: "column", gap: 6, alignSelf: "flex-end" }}>
          <button
            onClick={exportPptx}
            disabled={exporting}
            style={{
              background: exporting ? "#93c5fd" : "#1e3a5f",
              color: "#fff",
              border: "none",
              borderRadius: 8,
              padding: "10px 26px",
              cursor: exporting ? "not-allowed" : "pointer",
              fontWeight: 700,
              fontSize: 15,
              fontFamily: "inherit",
              whiteSpace: "nowrap",
            }}
          >
            {exporting ? "מייצא..." : "📥 ייצא ל-PowerPoint"}
          </button>
          {exportMsg && (
            <span style={{ fontSize: 13, color: "#16a34a", fontWeight: 600 }}>
              {exportMsg}
            </span>
          )}
        </div>
      </div>

      {/* Section cards */}
      {SECTIONS.map((s, i) => (
        <SectionCard
          key={s.id}
          index={i + 1}
          section={s}
          value={fields[s.id]}
          onChange={(v) => update(s.id, v)}
        />
      ))}
    </div>
  );
}

function CoverField({ label, value, onChange, placeholder, wide }) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 4,
        flex: wide ? "1 1 260px" : "0 1 180px",
      }}
    >
      <label style={{ fontSize: 12, fontWeight: 600, color: "#475569" }}>
        {label}
      </label>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        style={{
          padding: "8px 12px",
          borderRadius: 8,
          border: "1px solid #e2e8f0",
          fontSize: 14,
          direction: "rtl",
          fontFamily: "inherit",
          outline: "none",
        }}
      />
    </div>
  );
}

function SectionCard({ index, section, value, onChange }) {
  const lineCount = value.split("\n").filter((l) => l.trim()).length;

  return (
    <div
      style={{
        background: "#fff",
        borderRadius: 12,
        boxShadow: "0 1px 3px rgba(0,0,0,.1)",
        marginBottom: 16,
        overflow: "hidden",
        border: "1px solid #e2e8f0",
      }}
    >
      {/* Card header */}
      <div
        style={{
          background: "#1e3a5f",
          padding: "12px 20px",
          display: "flex",
          alignItems: "center",
          gap: 10,
        }}
      >
        <span
          style={{
            background: "#3b82f6",
            color: "#fff",
            borderRadius: "50%",
            width: 26,
            height: 26,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 13,
            fontWeight: 700,
            flexShrink: 0,
          }}
        >
          {index}
        </span>
        <h2 style={{ margin: 0, fontSize: 17, fontWeight: 700, color: "#fff" }}>
          {section.title}
        </h2>
      </div>

      {/* Textarea */}
      <div style={{ padding: "16px 20px 12px" }}>
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={section.placeholder}
          rows={6}
          style={{
            width: "100%",
            padding: "12px 14px",
            borderRadius: 8,
            border: "1px solid #e2e8f0",
            fontSize: 14,
            lineHeight: 1.8,
            direction: "rtl",
            fontFamily: "inherit",
            resize: "vertical",
            color: "#1e293b",
            background: "#f8fafc",
            outline: "none",
            boxSizing: "border-box",
          }}
        />
        <div
          style={{
            fontSize: 11,
            color: "#94a3b8",
            marginTop: 4,
            textAlign: "left",
            direction: "ltr",
          }}
        >
          {lineCount} שורות · התחל ב-<code style={{ fontSize: 11 }}>-</code> לתבליט
        </div>
      </div>
    </div>
  );
}
