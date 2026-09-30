import apiClient from "./client";
import type { DashboardStatistics, StatusChartItem,PriorityChartItem } from "../types";

export const getDashboardStatistics = async ()=>{
    const res = await apiClient.get<DashboardStatistics>("/dashboard/statistics");
    return res.data
}
export const getStatusChart = async ()=>{
    const res = await apiClient.get<StatusChartItem[]>("/dashboard/chart/status");
    return res.data
}
export const getPriorityChart = async ()=>{
    const res = await apiClient.get<PriorityChartItem[]>("/dashboard/chart/priority");
    return res.data
}