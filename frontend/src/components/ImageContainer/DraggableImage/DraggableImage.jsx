import React from "react";
import { useDrag } from "react-dnd";
import "./DraggableImage.css";

const DraggableImage = ({ image }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: "image", // The type should match the drop target
    item: { image: image.encoded_image_data }, // Make sure this is the current image data
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  }));

  return (
    <img
      ref={drag}
      src={image.encoded_image_data}
      alt="draggable"
      className={`draggable-image ${isDragging ? "dragging" : ""}`}
    />
  );
};

export default DraggableImage;
