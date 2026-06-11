const API_URL = "http://127.0.0.1:8000";

async function apiGet(path) {
    const response = await fetch(`${API_URL}${path}`);

    if (!response.ok) {
        throw new Error(`Error GET ${path}`);
    }

    return response.json();
}

async function apiPost(path, data) {
    const response = await fetch(`${API_URL}${path}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        throw new Error(`Error POST ${path}`);
    }

    return response.json();
}

async function apiPut(path, data) {
    const response = await fetch(`${API_URL}${path}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        throw new Error(`Error PUT ${path}`);
    }

    return response.json();
}