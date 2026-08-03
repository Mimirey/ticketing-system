import apiClient from "./client";
import type { LoginResponse } from "../types";

export const login = async (email: string, password: string) => {
  const res = await apiClient.post<LoginResponse>("/auth/login", { email, password });
  return res.data;
};