import React, { useState } from "react";
import DraggableSavedImage from "./DraggableSavedImage/DraggableSavedImage";
import images from "../../ImageImporter";

const imagesArray = Object.values(images);

const SavedImagesContainer = ({ generatedImages }) => {
  const [currentPage, setCurrentPage] = useState(0);
  const imagesPerPage = 16;

  const handleNextPage = () => {
    if ((currentPage + 1) * imagesPerPage < images.length) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handlePreviousPage = () => {
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1);
    }
  };

  const startIndex = currentPage * imagesPerPage;
  const endIndex = startIndex + imagesPerPage;
  const currentImages = generatedImages.slice(startIndex, endIndex);

  return (
    <div
      style={{
        width: "99%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        border: "1px solid #ccc",
        borderRadius: "10px",
        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
        marginTop: "20px",
        backgroundColor: "#f8f8f8",
        padding: "10px",
      }}
    >
      <h3 style={{ margin: "10px 0", color: "#333" }}>Saved Images</h3>
      <div
        style={{
          width: "100%",
          display: "flex",
          alignItems: "center",
        }}
      >
        <button
          onClick={handlePreviousPage}
          disabled={currentPage === 0}
          style={{
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "5px",
            padding: "8px 16px",
            cursor: currentPage === 0 ? "not-allowed" : "pointer",
            opacity: currentPage === 0 ? 0.5 : 1,
            marginRight: "10px",
          }}
        >
          &lt;
        </button>
        <div
          style={{
            display: "flex",
            overflowX: "auto",
            width: "100%",
            height: "140px",
            justifyContent: "center",
            alignItems: "center",
            padding: "10px",
          }}
        >
          {currentImages.map((img, index) => (
            <div
              key={index}
              style={{
                flex: "0 0 100px",
                margin: "0 5px",
                display: "flex",
                justifyContent: "center",
              }}
            >
              <DraggableSavedImage image={img} />
            </div>
          ))}
        </div>
        <button
          onClick={handleNextPage}
          disabled={endIndex >= imagesArray.length}
          style={{
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "5px",
            padding: "8px 16px",
            cursor: endIndex >= imagesArray.length ? "not-allowed" : "pointer",
            opacity: endIndex >= imagesArray.length ? 0.5 : 1,
            marginLeft: "10px",
          }}
        >
          &gt;
        </button>
      </div>
    </div>
  );
};

export default SavedImagesContainer;
