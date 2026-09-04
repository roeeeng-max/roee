import axios from "axios";

const api = axios.create({ baseURL: "" });

export const getDashboard = () => api.get("/api/dashboard").then(r => r.data);
export const getTransactions = (params) => api.get("/api/transactions", { params }).then(r => r.data);
export const updateTransaction = (id, data) => api.put(`/api/transactions/${id}`, data).then(r => r.data);
export const deleteTransaction = (id) => api.delete(`/api/transactions/${id}`).then(r => r.data);
export const uploadFile = (file) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/api/upload", form).then(r => r.data);
};
export const getFiles = () => api.get("/api/files").then(r => r.data);
export const getBudget = (month) => api.get("/api/budget", { params: { month } }).then(r => r.data);
export const setBudget = (data) => api.post("/api/budget", data).then(r => r.data);
export const getStatsCategories = (month) => api.get("/api/stats/categories", { params: { month } }).then(r => r.data);

// ─── הון ונכסים ────────────────────────────────────────────────────────────
export const getVaultStatus = () => api.get("/api/vault/status").then(r => r.data);
export const setupVault = (password) => api.post("/api/vault/setup", { password }).then(r => r.data);
export const unlockVault = (password) => api.post("/api/vault/unlock", { password }).then(r => r.data);
export const lockVault = () => api.post("/api/vault/lock").then(r => r.data);
export const getInstitutions = () => api.get("/api/institutions").then(r => r.data);
export const getConnections = () => api.get("/api/connections").then(r => r.data);
export const addConnection = (data) => api.post("/api/connections", data).then(r => r.data);
export const updateManualBalance = (id, balance) => api.put(`/api/connections/${id}/balance`, { balance }).then(r => r.data);
export const syncConnection = (id) => api.post(`/api/connections/${id}/sync`).then(r => r.data);
export const deleteConnection = (id) => api.delete(`/api/connections/${id}`).then(r => r.data);
export const getNetWorth = () => api.get("/api/networth").then(r => r.data);
