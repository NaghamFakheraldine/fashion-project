import React from "react";

const SaveButton = ({ saveImage }) => {
  return (
    <div style={{ textAlign: "center", paddingTop: "10px" }}>
      <button style={{ fontSize: "16px" }} onClick={saveImage}>
        Save Image
      </button>
    </div>
  );
};

export default SaveButton;
