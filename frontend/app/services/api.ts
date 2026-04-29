import * as SecureStore from 'expo-secure-store';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL;

export const getToken = async () => {
  return await SecureStore.getItemAsync('userToken');
};

export const saveToken = async (token: string) => {
  await SecureStore.setItemAsync('userToken', token);
};

export const clearToken = async () => {
  await SecureStore.deleteItemAsync('userToken');
};

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getToken();
  
  if (!API_BASE_URL) {
    console.error("EXPO_PUBLIC_API_BASE_URL is not defined in .env file");
  }

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  };

  if (options.headers) {
    Object.assign(headers, options.headers);
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 204) {
      return null as T;
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API Request Failed: ${response.status}`);
    }

    return response.json();
  } catch (error: any) {
    console.error(`Network request error to ${API_BASE_URL}${endpoint}:`, error);
    if (error.message === 'Network request failed') {
      throw new Error(`서버에 접속할 수 없습니다. 주소(${API_BASE_URL})와 방화벽 설정을 확인하세요.`);
    }
    throw error;
  }
}
