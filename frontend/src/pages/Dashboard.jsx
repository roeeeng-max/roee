import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getDashboard, getNetWorth } from "../api";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend,
} from "recharts";

const COLORS = ["#60a5fa","#34d399","#f87171","#fbbf24","#a78bfa","#fb923c","#38bdf8","#4ade80","#f472b6","#94a3b8"];

const fmt = (n) => `₪${Number(n).toLocaleString("he-IL", { maximumFractionDigits: 0 })}`;

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [netWorth, setNetWorth] = useState(null);

  useEffect(() => {
    getDashboard().then(setData);
    getNetWorth().then(setNetWorth).catch(() => {});
  }, []);

  if (!data) return <div style={{ padding: 40, textAlign: "center", color: "#94a3b8" }}>טוען...</div>;

  return (
    <div style={{ direction: "rtl", padding: 32, fontFamily: "inherit" }}>
      <h1 style={{ fontSize: 26, fontWeight: 700, marginBottom: 24, color: "#1e293b" }}>דשבורד פיננסי</h1>

      {/* KPI cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px,1fr))", gap: 16, marginBottom: 32 }}>
        {netWorth && (
          <Link to="/networth" style={{ textDecoration: "none" }}>
            <KpiCard title="סה״כ הון (בנקים + השקעות)" value={fmt(netWorth.total)} color="#a78bfa" />
          </Link>
        )}
        <KpiCard title="סה״כ כל הזמנים" value={fmt(data.total_all_time)} color="#60a5fa" />
        <KpiCard title="החודש הנוכחי" value={fmt(data.total_this_month)} color="#34d399" />
        {data.by_person.map(p => (
          <KpiCard key={p.person} title={p.person} value={fmt(p.total)} color="#fbbf24" />
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 24 }}>
        {/* Category pie */}
        <Card title="הוצאות לפי קטגוריה">
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={data.by_category} dataKey="total" nameKey="category" cx="50%" cy="50%" outerRadius={100} label={({ category, percent }) => `${category} ${(percent*100).toFixed(0)}%`}>
                {data.by_category.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip formatter={(v) => fmt(v)} />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        {/* Monthly bar */}
        <Card title="הוצאות חודשיות">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.by_month}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} />
              <YAxis tickFormatter={(v) => `₪${(v/1000).toFixed(0)}K`} />
              <Tooltip formatter={(v) => fmt(v)} />
              <Bar dataKey="total" fill="#60a5fa" radius={[4,4,0,0]} name="הוצאות" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Top expenses */}
      <Card title="5 ההוצאות הגדולות ביותר">
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
          <thead>
            <tr style={{ background: "#f1f5f9" }}>
              {["תאריך","תיאור","קטגוריה","אחראי","סכום"].map(h => (
                <th key={h} style={{ padding: "8px 12px", textAlign: "right", fontWeight: 600 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.top_expenses.map(t => (
              <tr key={t.id} style={{ borderBottom: "1px solid #e2e8f0" }}>
                <td style={{ padding: "8px 12px" }}>{t.date}</td>
                <td style={{ padding: "8px 12px" }}>{t.description}</td>
                <td style={{ padding: "8px 12px" }}><Badge>{t.category}</Badge></td>
                <td style={{ padding: "8px 12px" }}>{t.person}</td>
                <td style={{ padding: "8px 12px", fontWeight: 700, color: "#ef4444" }}>{fmt(t.amount)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      {/* Budget status */}
      {data.budget_status.length > 0 && (
        <Card title="מצב תקציב החודש">
          {data.budget_status.map(b => (
            <div key={b.category} style={{ marginBottom: 16 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                <span style={{ fontWeight: 600 }}>{b.category}</span>
                <span style={{ color: b.remaining < 0 ? "#ef4444" : "#64748b" }}>
                  {fmt(b.spent)} / {fmt(b.limit)}
                </span>
              </div>
              <div style={{ background: "#e2e8f0", borderRadius: 8, height: 10 }}>
                <div style={{
                  width: `${Math.min((b.spent / b.limit) * 100, 100)}%`,
                  height: "100%", borderRadius: 8,
                  background: b.spent > b.limit ? "#ef4444" : b.spent > b.limit * 0.8 ? "#f59e0b" : "#34d399"
                }} />
              </div>
            </div>
          ))}
        </Card>
      )}
    </div>
  );
}

function KpiCard({ title, value, color }) {
  return (
    <div style={{ background: "#fff", borderRadius: 12, padding: 20, boxShadow: "0 1px 3px rgba(0,0,0,.1)", borderTop: `4px solid ${color}` }}>
      <div style={{ color: "#64748b", fontSize: 13, marginBottom: 6 }}>{title}</div>
      <div style={{ fontSize: 24, fontWeight: 700, color: "#1e293b" }}>{value}</div>
    </div>
  );
}

function Card({ title, children }) {
  return (
    <div style={{ background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 1px 3px rgba(0,0,0,.1)", marginBottom: 0 }}>
      <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16, color: "#1e293b" }}>{title}</h2>
      {children}
    </div>
  );
}

function Badge({ children }) {
  return (
    <span style={{ background: "#eff6ff", color: "#3b82f6", padding: "2px 8px", borderRadius: 999, fontSize: 12 }}>
      {children}
    </span>
  );
}
