import React, { useState } from "react";

const SearchBar = ({
  prompt,
  setPrompt,
  promptToImage,
  promptToImageWithReference,
  selectedTrainingImage,
}) => {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        marginBottom: "20px",
      }}
    >
      <input
        type="text"
        placeholder="Enter Prompt..."
        onChange={(e) => setPrompt(e.target.value)}
        style={{
          width: "60%",
          padding: "10px 20px",
          borderRadius: "20px 0 0 20px",
          boxShadow: "0 2px 5px rgba(0, 0, 0, 0.2)",
          border: "1px solid #ccc",
          outline: "none",
          fontSize: "16px",
          borderRight: "none", // to merge with the button
        }}
        value={prompt}
      />
      <button
        onClick={
          selectedTrainingImage ? promptToImageWithReference : promptToImage
        }
        style={{
          padding: "10px 20px",
          borderRadius: "0 20px 20px 0",
          boxShadow: "0 2px 5px rgba(0, 0, 0, 0.2)",
          border: "1px solid #ccc",
          borderLeft: "none", // to merge with the input field
          cursor: "pointer",
          fontSize: "16px",
          display: "flex",
          alignItems: "center",
          background: "#fff",
          color: "#4CAF50",
        }}
      >
        <i className="fas fa-paper-plane" style={{ marginRight: "8px" }}></i>
      </button>
    </div>
  );
};

export default SearchBar;
