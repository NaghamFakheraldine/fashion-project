import React, { useRef, useEffect, useState } from "react";
import CanvasDraw from "react-canvas-draw";
import { useDrop } from "react-dnd";

const SAVE_IMAGE_URL = "http://localhost:5000/api/save-image";

let globalVariable = "";
const Workspace = ({
  tool,
  color,
  drawingSize,
  clearCanvasRef,
  undoRef,
  saveImageRef,
  uploadToS3Ref,
}) => {
  const canvasRef = useRef(null);
  const [backgroundImage, setBackgroundImage] = useState(null);
  const [backgroundImageUpload, setBackgroundImageUpload] = useState(null);

  const handleClear = () => {
    canvasRef.current.clear();
  };

  const handleUndo = () => {
    canvasRef.current.undo();
  };
  useEffect(() => {
    if (clearCanvasRef) {
      clearCanvasRef.current = handleClear;
    }
    if (undoRef) {
      undoRef.current = handleUndo;
    }
    if (saveImageRef) {
      saveImageRef.current = saveImage;
    }
    if (uploadToS3Ref) {
      uploadToS3Ref.current = uploadToS3;
    }
  }, [clearCanvasRef, undoRef, saveImageRef, uploadToS3Ref]);

  const getBrushSettings = () => {
    if (tool === "highlighter") {
      return {
        brushRadius: drawingSize,
        brushColor: `${color}80`, // 80 is the hex value for 50% opacity
      };
    } else if (tool === "eraser") {
      return {
        brushRadius: drawingSize,
        brushColor: "#FFFFFF",
      };
    } else {
      return {
        brushRadius: drawingSize,
        brushColor: color,
      };
    }
  };

  const brushSettings = getBrushSettings();

  const [{ canDrop, isOver }, drop] = useDrop(() => ({
    accept: ["image", "savedImage"],
    drop: (item) => {
      setBackgroundImage(item.image);
      globalVariable =item.image;
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
      canDrop: monitor.canDrop(),
    }),
  }));

  useEffect(() => {
    const resizeCanvas = () => {
      if (canvasRef.current) {
        canvasRef.current.canvasContainer.children[1].style.width = "100%";
        canvasRef.current.canvasContainer.children[1].style.height = "100%";
      }
    };
    window.addEventListener("resize", resizeCanvas);
    resizeCanvas(); // initial resize
    return () => window.removeEventListener("resize", resizeCanvas);
  }, []);

  useEffect(() => {
    // Remove grid lines
    if (canvasRef.current) {
      const gridCanvas = canvasRef.current.canvasContainer.children[0];
      gridCanvas.style.display = "none";
    }
  }, []);

  const uploadToS3 = async () => {
    const drawingCanvas = canvasRef.current.canvasContainer.children[1];
    const hiddenCanvas = document.createElement("canvas");
    hiddenCanvas.width = drawingCanvas.width;
    hiddenCanvas.height = drawingCanvas.height;
    const ctx = hiddenCanvas.getContext("2d");

    if (globalVariable) {
      const img = new Image();
      img.src = backgroundImage;

      img.onload = () => {
        const aspectRatio = img.width / img.height;
        const bgWidth = hiddenCanvas.width * 0.5;
        const bgHeight = bgWidth / aspectRatio;
        const xOffset = (hiddenCanvas.width - bgWidth) / 2;
        const yOffset = (hiddenCanvas.height - bgHeight) / 2;

        ctx.drawImage(img, xOffset, yOffset, bgWidth, bgHeight);
        ctx.drawImage(drawingCanvas, 0, 0);
      };
    }

    ctx.drawImage(drawingCanvas, 0, 0);

    const dataURL = hiddenCanvas.toDataURL("image/png");

    try {
      const response = await fetch(SAVE_IMAGE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          imageData: dataURL,
          originalFilename: "workspace-image.png",
        }),
      });

      const responseData = await response.json();

      if (response.status === 200) {
        console.log("Image uploaded successfully:", responseData);
      } else {
        console.error("Failed to upload image:", responseData);
      }
    } catch (error) {
      console.error("Error uploading image:", error);
    }
  };

  const saveImage = () => {
    const drawingCanvas = canvasRef.current.canvasContainer.children[1];
    const hiddenCanvas = document.createElement("canvas");
    hiddenCanvas.width = drawingCanvas.width;
    hiddenCanvas.height = drawingCanvas.height;
    const ctx = hiddenCanvas.getContext("2d");

    if (backgroundImage) {
      const img = new Image();
      img.src = backgroundImage;

      img.onload = () => {
        const aspectRatio = img.width / img.height;
        const bgWidth = hiddenCanvas.width * 0.5;
        const bgHeight = bgWidth / aspectRatio;
        const xOffset = (hiddenCanvas.width - bgWidth) / 2;
        const yOffset = (hiddenCanvas.height - bgHeight) / 2;

        ctx.drawImage(img, xOffset, yOffset, bgWidth, bgHeight);
        ctx.drawImage(drawingCanvas, 0, 0);

        const link = document.createElement("a");
        link.href = hiddenCanvas.toDataURL("image/png");
        link.download = "workspace-image.png";
        link.click();
      };
    } else {
      ctx.drawImage(drawingCanvas, 0, 0);
      const link = document.createElement("a");
      link.href = hiddenCanvas.toDataURL("image/png");
      link.download = "workspace-image.png";
      link.click();
    }
  };

  saveImageRef.current = saveImage;

  return (
    <div
      ref={drop}
      style={{
        width: "98%",
        height: "90%",
        border: "1px solid #ccc",
        padding: "10px",
        minHeight: "400px",
        position: "relative",
        backgroundColor: "#f5f5f5",
        borderRadius: "10px",
      }}
    >
      <h3 style={{ textAlign: "center" }}>Workspace</h3>
      <div
        style={{
          width: "100%",
          height: "90%",
          position: "relative",
        }}
      >
        <CanvasDraw
          ref={canvasRef}
          brushRadius={brushSettings.brushRadius}
          brushColor={brushSettings.brushColor}
          lazyRadius={0}
          style={{
            background: "none",
            width: "100%",
            height: "100%",
            backgroundImage: backgroundImage
              ? `url(${backgroundImage})`
              : "none",
            backgroundPosition: "center",
            backgroundSize: "50%",
            backgroundRepeat: "no-repeat",
            backgroundColor: "white",
            border: "solid 1px #ccc",
          }}
        />
      </div>
    </div>
  );
};

export default Workspace;
