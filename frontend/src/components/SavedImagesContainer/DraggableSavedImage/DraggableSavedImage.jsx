import React from "react";
import { useDrag } from "react-dnd";

const DraggableSavedImage = ({ image }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: "savedImage",
    item: { image: image.encoded_image_data },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  }));

  return (
    <img
      ref={drag}
      src={image.encoded_image_data}
      alt="saved"
      style={{
        width: "100%",
        height: "100px",
        objectFit: "cover",
        opacity: isDragging ? 0.5 : 1,
      }}
    />
  );
};

export default DraggableSavedImage;
