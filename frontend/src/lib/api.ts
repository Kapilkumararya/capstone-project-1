export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export async function fetchApi(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem("auth_token");

  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  } else {
    // Let the browser set Content-Type for FormData
    headers.delete("Content-Type");
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let message = "API request failed";
    try {
      const errorData = await response.json();
      if (Array.isArray(errorData.detail)) {
        message = errorData.detail[0].msg;
      } else {
        message = errorData.detail || message;
      }
    } catch (e) {
      // Ignore JSON parse error for error responses
    }
    throw new Error(message);
  }

  // Handle 204 No Content
  if (response.status === 204) return null;

  return response.json();
}
