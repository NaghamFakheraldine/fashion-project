import React, { useState } from "react";
import PropTypes from "prop-types";
import "./TrainingDataContainer.css";
import images from "../../ImageImporter.js";

const imagesArray = Object.values(images);

const TrainingDataContainer = ({ closePopup, onSelectImage }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedImage, setSelectedImage] = useState(null);

  const handleImageClick = (image) => {
    if (selectedImage === image) {
      // Deselect the image if it's already selected
      setSelectedImage(null);
      onSelectImage(null); // Send back null to indicate deselection
    } else {
      // Select the clicked image
      setSelectedImage(image);
      onSelectImage(image); // Send the selected image back to the parent component
    }
  };

  return (
    <div className="training-data-container">
      <div className="training-data-header">
        <h2>Training Data</h2>
        <p>Choose an image as a reference</p>
        <button onClick={closePopup} className="close-button" title="Close">
          ✖
        </button>
      </div>
      <div className="training-data-content">
        <div className="search-bar">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search images..."
            className="search-input"
          />
          <button className="search-button">Search</button>
        </div>
        <div className="images">
          {imagesArray.map((image, index) => (
            <img
              key={index}
              src={image}
              className={`training-data-image ${selectedImage === image ? "selected" : ""
                }`}
              onClick={() => handleImageClick(image)}
              alt={`Training Data ${index + 1}`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

TrainingDataContainer.propTypes = {
  closePopup: PropTypes.func.isRequired,
  onSelectImage: PropTypes.func.isRequired,
};

export default TrainingDataContainer;
