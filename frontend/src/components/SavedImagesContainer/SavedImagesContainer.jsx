import React, { useState, useEffect } from "react";
import DraggableSavedImage from "./DraggableSavedImage/DraggableSavedImage";

const SavedImagesContainer = () => {
  const [currentPage, setCurrentPage] = useState(0);
  const imagesPerPage = 16;
  const [images, setImages] = useState([]);
  const [totalPages, setTotalPages] = useState(0);

  const fetchImages = async (page = 0) => {
    try {
      const response = await fetch(
        `http://localhost:5000/api/get-paginated-images?page=${page}&imagesPerPage=${imagesPerPage}`
      );
      const data = await response.json();
      setImages(data.images);
      setTotalPages(data.totalPages);
    } catch (error) {
      console.error("Error fetching images:", error);
    }
  };

  useEffect(() => {
    fetchImages(currentPage);
  }, [currentPage]);

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

  return (
    <div
      style={{
        width: "100%",
        display: "flex",
        alignItems: "center",
        paddingTop: "40px",
      }}
    >
      <button onClick={handlePreviousPage} disabled={currentPage === 0}>
        &lt;
      </button>
      <div
        style={{
          display: "flex",
          overflowX: "auto",
          width: "100%",
          height: "200px",
          justifyContent: "center",
        }}
      >
        {images.map((img, index) => (
          <div key={index} style={{ flex: "0 0 100px", margin: "0 5px" }}>
            <DraggableSavedImage image={img.url} />
          </div>
        ))}
      </div>
      <button
        onClick={handleNextPage}
        disabled={currentPage === totalPages - 1}
      >
        &gt;
      </button>
    </div>
  );
};

export default SavedImagesContainer;
