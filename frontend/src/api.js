const BASE_URL = "http://localhost:8000";

export const registerUser = async (username, password) => {
  try {
    const response = await fetch(`${BASE_URL}/register/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    return await response.json();
  } catch (error) {
    return { message: "Error during registration" };
  }
};

export const loginUser = async (username, password) => {
  try {
    const response = await fetch(`${BASE_URL}/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    return await response.json();
  } catch (error) {
    return { message: "Error during login" };
  }
};

export const uploadDocument = async (file) => {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${BASE_URL}/upload/`, {
      method: "POST",
      body: formData,
    });
    return await response.json();
  } catch (error) {
    return { message: "Error during upload" };
  }
};

export const searchDocument = async (query) => {
  try {
    const response = await fetch(`${BASE_URL}/search/?query=${query}`);
    return await response.json();
  } catch (error) {
    return { message: "Error during search" };
  }
};
