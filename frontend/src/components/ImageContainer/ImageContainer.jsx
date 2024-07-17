import React, { useState } from "react";
import DraggableImage from "./DraggableImage/DraggableImage";
import image1 from "../../images/image1.jpeg";
import "./ImageContainer.css";

const ImageContainer = ({ imgInImageContainer }) => {
  const [image, setImage] = useState(image1);

  return (
    <div className="image-container">
      <h3 className="image-title">Image</h3>
      <div className="image-wrapper">
        <DraggableImage image={image} />
      </div>
    </div>
  );
};

export default ImageContainer;
