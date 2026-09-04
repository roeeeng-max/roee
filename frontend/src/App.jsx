import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import NetWorth from "./pages/NetWorth";
import Transactions from "./pages/Transactions";
import Upload from "./pages/Upload";
import Budget from "./pages/Budget";
import Files from "./pages/Files";

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: "flex", minHeight: "100vh", background: "#f8fafc", fontFamily: "'Segoe UI', Tahoma, sans-serif" }}>
        <Sidebar />
        <main style={{ flex: 1, marginRight: 220, minHeight: "100vh" }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/networth" element={<NetWorth />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/budget" element={<Budget />} />
            <Route path="/files" element={<Files />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
