import * as SecureStore from 'expo-secure-store';
import { API_BASE_URL } from "./config";

// 1. Token Management
export const getToken = async (): Promise<string | null> => {
  try {
    return await SecureStore.getItemAsync('userToken');
  } catch (e) {
    console.error("Token retrieval error:", e);
    return null;
  }
};

export const saveToken = async (token: string): Promise<void> => {
  try {
    await SecureStore.setItemAsync('userToken', token);
  } catch (e) {
    console.error("Token save error:", e);
  }
};

export const savePushToken = async (token: string): Promise<void> => {
  try {
    console.log("Saving push token locally:", token);
    await SecureStore.setItemAsync('pushToken', token);
    
    // Also try to update on server if possible
    const userToken = await getToken();
    if (userToken) {
      try {
        await apiRequest("/auth/push-token", {
          method: "PUT",
          body: JSON.stringify({ token }),
        });
        console.log("Push token updated on server");
      } catch (err) {
        console.error("Failed to update push token on server:", err);
      }
    }
  } catch (e) {
    console.error("Push token local save error:", e);
  }
};

// 2. Cache Management
export const getMyKeywordsCache = async (): Promise<number[]> => {
  try {
    const cached = await SecureStore.getItemAsync('myKeywords');
    return cached ? JSON.parse(cached) : [];
  } catch (e) {
    return [];
  }
};

export const saveMyKeywordsCache = async (keywords: number[]): Promise<void> => {
  try {
    await SecureStore.setItemAsync('myKeywords', JSON.stringify(keywords));
  } catch (e) {}
};

// 3. Generic API Request Helper
export const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const token = await getToken();
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  };

  if (options.headers) {
    Object.assign(headers, options.headers);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return null;
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || "API request failed");
  }

  return response.json();
};

// 4. Specific API Functions

// Auth & User
export const fetchMe = async () => {
  return apiRequest("/auth/me");
};

// Keywords
export const fetchKeywords = async () => {
  return apiRequest("/keywords");
};

export const fetchMyKeywords = async (_token?: string) => {
  const data = await apiRequest("/users/me/keywords");
  if (data?.enabled) {
    await saveMyKeywordsCache(data.enabled);
  }
  return data;
};

export const updateMyKeywords = async (_token: string | null, enabled: number[]) => {
  const data = await apiRequest("/users/me/keywords", {
    method: "PUT",
    body: JSON.stringify({ enabled }),
  });
  await saveMyKeywordsCache(enabled);
  return data;
};

// Notices
export const pingDatabase = async () => {
  return apiRequest("/health/db");
};

export const fetchNotices = async (keywordId: string | null = null) => {
  const endpoint = keywordId ? `/notices?keyword_id=${keywordId}` : "/notices";
  return apiRequest(endpoint);
};

export const fetchNoticeDetail = async (noticeId: string) => {
  return apiRequest(`/notices/${noticeId}`);
};

// Chatbot
export const sendChatbotMessage = async (question: string) => {
  return apiRequest("/chatbot", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
};
