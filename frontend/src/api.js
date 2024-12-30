const BASE_URL = "http://localhost:8000";

export async function registerUser(username, password) {
  const response = await fetch(`${BASE_URL}/register/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  return response.json();
}

export async function loginUser(username, password) {
  const response = await fetch(`${BASE_URL}/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  return response.json();
}

export async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${BASE_URL}/upload/`, {
    method: "POST",
    body: formData,
  });
  return response.json();
}

export async function searchDocuments(query) {
  const response = await fetch(`${BASE_URL}/search/?query=${query}`);
  return response.json();
}
