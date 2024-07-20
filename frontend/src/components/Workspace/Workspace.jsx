import React, { useRef, useEffect, useState } from "react";
import CanvasDraw from "react-canvas-draw";
import { useDrop } from "react-dnd";

const Workspace = ({
  tool,
  color,
  drawingSize,
  clearCanvasRef,
  undoRef,
  saveImageRef,
  onImageSave,
}) => {
  const canvasRef = useRef(null);
  const [backgroundImage, setBackgroundImage] = useState(null);

  const handleClear = () => {
    canvasRef.current.clear();
  };

  const handleUndo = () => {
    canvasRef.current.undo();
  };

  clearCanvasRef.current = handleClear;
  undoRef.current = handleUndo;

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
      // Ensure the correct image data is used
      console.log("Dropped image:", item.image); // Debugging line
      setBackgroundImage(item.image);
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

  // const saveImage = () => {
  //   const drawingCanvas = canvasRef.current.canvasContainer.children[1];
  //   const hiddenCanvas = document.createElement("canvas");
  //   hiddenCanvas.width = 512;
  //   hiddenCanvas.height = 512;
  //   const ctx = hiddenCanvas.getContext("2d");

  //   if (backgroundImage) {
  //     const img = new Image();
  //     img.crossOrigin = "anonymous"; // Ensure CORS is handled for external images
  //     img.src = backgroundImage;
  //     img.onload = () => {
  //       ctx.drawImage(img, 0, 0, 512, 512);
  //       ctx.drawImage(drawingCanvas, 0, 0, 512, 512);

  //       const link = document.createElement("a");
  //       link.href = hiddenCanvas.toDataURL("image/png");
  //       link.download = "workspace-image.png";
  //       link.click();
  //     };
  //   } else {
  //     ctx.drawImage(drawingCanvas, 0, 0, 512, 512);
  //     const link = document.createElement("a");
  //     link.href = hiddenCanvas.toDataURL("image/png");
  //     link.download = "workspace-image.png";
  //     link.click();
  //   }
  // };

  const saveImage = () => {
    return new Promise((resolve, reject) => {
      const drawingCanvas = canvasRef.current.canvasContainer.children[1];
      const hiddenCanvas = document.createElement("canvas");
      hiddenCanvas.width = 512;
      hiddenCanvas.height = 512;
      const ctx = hiddenCanvas.getContext("2d");

      if (backgroundImage) {
        const img = new Image();
        img.crossOrigin = "anonymous"; // Ensure CORS is handled for external images
        img.src = backgroundImage;
        img.onload = () => {
          ctx.drawImage(img, 0, 0, 512, 512);
          ctx.drawImage(drawingCanvas, 0, 0, 512, 512);

          resolve(hiddenCanvas.toDataURL("image/png"));
        };
      } else {
        ctx.drawImage(drawingCanvas, 0, 0, 512, 512);
        resolve(hiddenCanvas.toDataURL("image/png"));
      }
    });
  };

  saveImageRef.current = saveImage;

  useEffect(() => {
    const handleSaveImage = async () => {
      const imageData = await saveImage();
      onImageSave(imageData);
    };

    saveImageRef.current = handleSaveImage;
  }, [onImageSave, saveImage]);

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
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
      }}
    >
      <h3 style={{ textAlign: "center" }}>Workspace</h3>
      <div
        style={{
          width: "469px",
          height: "512px",
          position: "relative",
          justifyContent: "center",
          alignItems: "center",
          textAlign: "center",
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
            backgroundImage: `url(${backgroundImage})`,
            backgroundPosition: "center",
            backgroundSize: "contain",
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
