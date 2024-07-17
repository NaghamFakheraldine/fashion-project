import React from "react";

const UploadButton = ({ uploadToS3, children }) => {
  return <button onClick={uploadToS3}>{children}</button>;
};

export default UploadButton;
