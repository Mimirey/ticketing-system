import apiClient from "./client";
import type {Notification} from "../types";

export const getNotifications = async ()=>{
    const res = await apiClient.get<Notification[]>("/notifications");
    return res.data
}
export const getUnreadCount = async ()=>{
    const res = await apiClient.get<{unread_count: number}>("/notifications/unread-count");
    return res.data.unread_count
}
export const markAsRead = async (notificationId :number)=>{
    const res= await apiClient.patch<Notification[]>(`/notifications/${notificationId}/read`)
}