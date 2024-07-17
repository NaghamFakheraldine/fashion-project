import React from "react";
import { useDrag } from "react-dnd";
import "./DraggableImage.css";

const DraggableImage = ({ image }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: "image",
    item: { image },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  }));

  return (
    <img
      ref={drag}
      src={image}
      alt="draggable"
      className={`draggable-image ${isDragging ? "dragging" : ""}`}
    />
  );
};

export default DraggableImage;
