import React, { useState } from "react";
import {
  FaPen,
  FaEraser,
  FaHighlighter,
  FaUndo,
  FaTrash,
} from "react-icons/fa";
import "./DrawingTools.css";

const DrawingTools = ({
  setTool,
  setColor,
  setdrawingSize,
  clearCanvas,
  undoDrawing,
}) => {
  const [selectedColor, setSelectedColor] = useState("#000000");
  // const [eraserSize, setEraserSizeState] = useState(4);

  const handleColorChange = (e) => {
    setSelectedColor(e.target.value);
    setColor(e.target.value);
  };

  const handleEraserSizeChange = (size) => {
    setdrawingSize(size);
    // setEraserSizeState(size);
  };

  return (
    <div className="tools-container">
      <h3 className="tools-title">Tools</h3>
      <div className="tools-icons">
        <FaPen
          className="tool-icon"
          onClick={() => setTool("pen")}
          title="Pen"
        />
        <FaHighlighter
          className="tool-icon"
          onClick={() => setTool("highlighter")}
          title="Highlighter"
        />
        <FaEraser
          className="tool-icon"
          onClick={() => setTool("eraser")}
          title="Eraser"
        />
        <div className="eraser-size">
          <label>Size:</label>
          <button
            className="eraser-button"
            onClick={() => handleEraserSizeChange(4)}
          >
            Small
          </button>
          <button
            className="eraser-button"
            onClick={() => handleEraserSizeChange(10)}
          >
            Medium
          </button>
          <button
            className="eraser-button"
            onClick={() => handleEraserSizeChange(15)}
          >
            Large
          </button>
        </div>
        <input
          title="Color Picker"
          type="color"
          value={selectedColor}
          onChange={handleColorChange}
          className="color-picker"
        />
        <FaTrash
          className="tool-icon"
          onClick={clearCanvas}
          title="Delete All"
        />
        <FaUndo className="tool-icon" onClick={undoDrawing} title="Undo" />
      </div>
    </div>
  );
};

export default DrawingTools;
