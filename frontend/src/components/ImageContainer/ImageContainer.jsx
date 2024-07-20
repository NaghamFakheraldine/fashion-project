import React from "react";
import DraggableImage from "./DraggableImage/DraggableImage";
import "./ImageContainer.css";

const ImageContainer = ({ imgInImageContainer }) => {
  return (
    <div className="image-container">
      <h3 className="image-title">Generated Images</h3>
      <div className="image-grid">
        {imgInImageContainer.map((image, index) => (
          <div key={image.file_name || index} className="image-wrapper">
            <DraggableImage image={image} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default ImageContainer;
