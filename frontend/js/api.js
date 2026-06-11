const API_BASE_URL = "http://127.0.0.1:8000";

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  if (!response.ok) {
    let message = "Error en la comunicació amb el servidor";

    try {
      const error = await response.json();
      message = error.detail || message;
    } catch {
      // Ignorem errors de parseig
    }

    throw new Error(message);
  }

  if (response.status === 204) return null;

  return response.json();
}

export function apiGet(endpoint) {
  return request(endpoint);
}

export function apiPost(endpoint, data) {
  return request(endpoint, {
    method: "POST",
    body: JSON.stringify(data)
  });
}

export function apiPut(endpoint, data) {
  return request(endpoint, {
    method: "PUT",
    body: JSON.stringify(data)
  });
}