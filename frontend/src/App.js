import React, { useRef, useState } from "react";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import SearchBar from "./components/SearchBar";
import ImageContainer from "./components/ImageContainer/ImageContainer";
import Workspace from "./components/Workspace/Workspace";
import DrawingTools from "./components/DrawingTools/DrawingTools";
import SaveButton from "./components/SaveButton";
import UploadButton from "./components/DrawingTools/UploadButton";
import SavedImagesContainer from "./components/SavedImagesContainer/SavedImagesContainer";
import "./App.css";
//Adding the routes to the Flask
const GET_IMAGES_URL = "http://localhost:5000/api/get-images";

const App = () => {
  const [tool, setTool] = useState("pen");
  const [color, setColor] = useState("#000000");
  const [drawingSize, setdrawingSize] = useState(4);
  const [imgInImageContainer, setImgInImageContainer] = useState("");
  const clearCanvasRef = useRef(null);
  const undoRef = useRef(null);
  const saveImageRef = useRef(null);
  const uploadToS3Ref = useRef(null);

  const clearCanvas = () => {
    if (clearCanvasRef.current) {
      clearCanvasRef.current();
    }
  };

  const undoDrawing = () => {
    if (undoRef.current) {
      undoRef.current();
    }
  };

  const saveImage = () => {
    if (saveImageRef.current) {
      saveImageRef.current();
    }
  };

  const uploadToS3 = () => {
    if (uploadToS3Ref.current) {
      uploadToS3Ref.current();
    }
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div style={{ padding: "10px" }}>
        <SearchBar setImgInImageContainer={setImgInImageContainer} />
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            height: "60vh",
          }}
        >
          <DrawingTools
            setTool={setTool}
            setColor={setColor}
            setdrawingSize={setdrawingSize}
            clearCanvas={clearCanvas}
            undoDrawing={undoDrawing}
          />
          <div
            style={{ display: "flex", flexDirection: "column", width: "60%" }}
          >
            <Workspace
              tool={tool}
              color={color}
              drawingSize={drawingSize}
              clearCanvasRef={clearCanvasRef}
              undoRef={undoRef}
              saveImageRef={saveImageRef}
              uploadToS3Ref={uploadToS3Ref}
            />
            <SaveButton saveImage={saveImage} />
            <UploadButton uploadToS3={uploadToS3}>
              Upload to S3 here
            </UploadButton>
          </div>
          <ImageContainer imgInImageContainer={imgInImageContainer} />
        </div>
        <SavedImagesContainer />
      </div>
    </DndProvider>
  );
};

export default App;
