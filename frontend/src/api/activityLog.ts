import apiClient from "./client";
import type { ActivityLog } from "../types";

export const getActivityLogs = async (page: number = 1, pageSize: number =20) =>{
    const res = await apiClient.get<ActivityLog[]>("/activity-logs", {
        params: { page, page_size: pageSize },
    });
    return res.data;
}