import axios from "axios";

const api = axios.create({ baseURL: "http://localhost:8000" });

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
