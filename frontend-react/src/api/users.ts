import apiClient from "./client";
import type {User} from "../types";

export const getStaffUsers= async ()=>{
    const res = await apiClient.get<User[]>("/users", {params: {role: "STAFF_IT"}});
    return res.data;
};