import React, { useState } from "react";
import "./styles.css";
import { registerUser, loginUser, uploadDocument, searchDocument } from "./api";

const App = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [query, setQuery] = useState("");
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleRegister = async () => {
    const response = await registerUser(username, password);
    setMessage(response.message || "Error during registration");
  };

  const handleLogin = async () => {
    const response = await loginUser(username, password);
    setMessage(response.message || "Error during login");
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage("Please select a file to upload.");
      return;
    }
    const response = await uploadDocument(file);
    setMessage(response.message || "Error during upload");
  };

  const handleSearch = async () => {
    const response = await searchDocument(query);
    setMessage(response.results || "No results found");
  };

  return (
    <div className="app">
      <h1>Document Management System</h1>
      <div className="form">
        <h2>User Actions</h2>
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

      <div className="form">
        <h2>Document Actions</h2>
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button onClick={handleUpload}>Upload</button>
      </div>

      <div className="form">
        <h2>Search Documents</h2>
        <input
          type="text"
          placeholder="Enter your query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button onClick={handleSearch}>Search</button>
      </div>

      <div className="message">
        <h3>Response:</h3>
        <p>{message}</p>
      </div>
    </div>
  );
};

export default App;
