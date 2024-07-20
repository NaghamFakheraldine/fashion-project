import React, { useEffect, useRef, useState } from "react";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import SearchBar from "./components/SearchBar";
import ImageContainer from "./components/ImageContainer/ImageContainer";
import Workspace from "./components/Workspace/Workspace";
import DrawingTools from "./components/DrawingTools/DrawingTools";
import SaveButton from "./components/SaveButton";
import SavedImagesContainer from "./components/SavedImagesContainer/SavedImagesContainer";
import TrainingDataContainer from "./components/TrainingDataContainer/TrainingDataContainer";
import { GrStorage } from "react-icons/gr";
import axios from "axios";
import "./App.css";

const App = () => {
  const [tool, setTool] = useState("pen");
  const [color, setColor] = useState("#000000");
  const [drawingSize, setdrawingSize] = useState(4);
  const [imgInImageContainer, setImgInImageContainer] = useState([]);
  const clearCanvasRef = useRef(null);
  const undoRef = useRef(null);
  const saveImageRef = useRef(null);
  const [isTrainingDataVisible, setIsTrainingDataVisible] = useState(false);
  const [selectedTrainingImage, setSelectedTrainingImage] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [savedImage, setSavedImage] = useState(null);
  const [generatedImages, setGeneratedImages] = useState([]);

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

  const toggleTrainingData = () => {
    setIsTrainingDataVisible(!isTrainingDataVisible);
  };

  const handleSelectImage = (image) => {
    setSelectedTrainingImage(image);
    // Handle API call or other logic with the selected image here
    // console.log("Selected training image:", selectedTrainingImage);
  };

  // APIs
  const promptToImage = () => {
    console.log("i am in the prompt image without reference");
    axios
      .post("http://127.0.0.1:5000/api/generate-image-from-prompt", {
        positive_prompt: prompt,
      })
      .then((response) => {
        // const imagesFromResponse = response.data.images;
        // setImgInImageContainer(imagesFromResponse);
        const decodedImages = response.data.images.map((img) => ({
          ...img,
          encoded_image_data: `data:image/png;base64,${img.encoded_image_data}`,
        }));
        setImgInImageContainer(decodedImages);
        setGeneratedImages((prevImages) => [...prevImages, ...decodedImages]);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  const promptToImageWithReference = () => {
    console.log("I am in the prompt image with reference");

    if (selectedTrainingImage) {
      // Function to convert image URL to Blob
      const imageUrlToBlob = async (url) => {
        const response = await fetch(url);
        const blob = await response.blob();
        return blob;
      };

      // Convert selectedTrainingImage URL to Blob
      imageUrlToBlob(selectedTrainingImage)
        .then((blob) => {
          // Create a FileReader instance
          const reader = new FileReader();

          // Set up the onloadend event handler
          reader.onloadend = () => {
            // Extract the base64 data from the result
            const base64data = reader.result.split(",")[1]; // Extracting base64 data

            // Make the API call with axios
            axios
              .post("http://127.0.0.1:5000/api/generate-image-from-reference", {
                positive_prompt: prompt,
                image: base64data, // Include base64 encoded image in the payload
              })
              .then((response) => {
                const imagesFromResponse = response.data.images;
                const decodedImages = imagesFromResponse.map((img) => ({
                  ...img,
                  encoded_image_data: `data:image/png;base64,${img.encoded_image_data}`,
                }));
                setImgInImageContainer(decodedImages);
                setGeneratedImages((prevImages) => [
                  ...prevImages,
                  ...decodedImages,
                ]);
              })
              .catch((error) => {
                console.log(error);
              });
          };

          // Read the selected image file as a data URL (base64)
          reader.readAsDataURL(blob);
        })
        .catch((error) => {
          console.error("Error converting image URL to Blob:", error);
        });
    }
  };

  const imageToImage = (imageData) => {
    setSavedImage(imageData);

    const imageUrlToBlob = async (url) => {
      const response = await fetch(url);
      const blob = await response.blob();
      return blob;
    };

    // Convert selectedTrainingImage URL to Blob
    imageUrlToBlob(imageData)
      .then((blob) => {
        // Create a FileReader instance
        const reader = new FileReader();

        // Set up the onloadend event handler
        reader.onloadend = () => {
          // Extract the base64 data from the result
          const base64data = reader.result.split(",")[1]; // Extracting base64 data

          console.log(base64data);

          // Make the API call with axios
          axios
            .post("http://127.0.0.1:5000/api/generate-image-from-sketch/", {
              positive_prompt: prompt,
              image: base64data, // Include base64 encoded image in the payload
            })
            .then((response) => {
              const imagesFromResponse = response.data.images;
              const decodedImages = imagesFromResponse.map((img) => ({
                ...img,
                encoded_image_data: `data:image/png;base64,${img.encoded_image_data}`,
              }));
              setImgInImageContainer(decodedImages);
              setGeneratedImages((prevImages) => [
                ...prevImages,
                ...decodedImages,
              ]);
            })
            .catch((error) => {
              console.log(error);
            });
        };

        // Read the selected image file as a data URL (base64)
        reader.readAsDataURL(blob);
      })
      .catch((error) => {
        console.error("Error converting image URL to Blob:", error);
      });
  };

  // useEffect(() => {}, []);

  return (
    <DndProvider backend={HTML5Backend}>
      <div style={{ padding: "10px" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            position: "relative",
          }}
        >
          <div style={{ flex: "1", textAlign: "left" }}>
            <button onClick={toggleTrainingData} className="icon-button">
              <GrStorage title="Training Data" className="storage-icon" />
            </button>
          </div>
          <div style={{ flex: "2", textAlign: "center" }}>
            <SearchBar
              prompt={prompt}
              setPrompt={setPrompt}
              promptToImage={promptToImage}
              promptToImageWithReference={promptToImageWithReference}
              selectedTrainingImage={selectedTrainingImage}
            />
          </div>
          <div style={{ flex: "1" }}></div>
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            height: "60vh",
            position: "relative",
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
              onImageSave={imageToImage}
            />
            <SaveButton saveImage={saveImage} />
          </div>
          <ImageContainer imgInImageContainer={imgInImageContainer} />
        </div>
        <SavedImagesContainer generatedImages={generatedImages} />
        {isTrainingDataVisible && (
          <TrainingDataContainer
            closePopup={toggleTrainingData}
            onSelectImage={handleSelectImage}
          />
        )}
      </div>
    </DndProvider>
  );
};

export default App;
