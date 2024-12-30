import React, { useState } from "react";
import { registerUser, loginUser, uploadFile, searchDocuments } from "./api";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState("");
  const [result, setResult] = useState("");

  const handleRegister = async () => {
    const response = await registerUser(username, password);
    alert(response.message);
  };

  const handleLogin = async () => {
    const response = await loginUser(username, password);
    alert(response.message);
  };

  const handleUpload = async () => {
  if (!file) {
    alert("Please select a file");
    return;
  }
  const response = await uploadFile(file);
  if (response.message) {
    alert(response.message);
  } else {
    alert("Unexpected response");
  }
  };

  const handleSearch = async () => {
    const response = await searchDocuments(query);
    setResult(response.results);
  };

  return (
    <div className="app">
      <h1>FastAPI React Frontend</h1>

      <div>
        <h2>Register / Login</h2>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button onClick={handleRegister}>Register</button>
        <button onClick={handleLogin}>Login</button>
      </div>

      <div>
        <h2>Upload File</h2>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={handleUpload}>Upload</button>
      </div>

      <div>
        <h2>Search</h2>
        <input
          type="text"
          placeholder="Enter query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button onClick={handleSearch}>Search</button>
        <p>Result: {result}</p>
      </div>
    </div>
  );
}

export default App;
