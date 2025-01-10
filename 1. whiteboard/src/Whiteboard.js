import React, { useState, useRef, useEffect } from "react";
import { useReactMediaRecorder } from "react-media-recorder-2";
import { DrawIoEmbed } from "react-drawio";
import "./App.css";

function Whiteboard() {
  const [webcamStream, setWebcamStream] = useState(null);
  const [isRecording, setIsRecording] = useState(false); // Track recording state
  const webcamVideoRef = useRef(null);

  const {
    status,
    startRecording: startScreenRecording,
    stopRecording,
    mediaBlobUrl,
  } = useReactMediaRecorder({
    screen: true,
    audio: true,
    video: true,
  });

  // Start webcam stream automatically when the component mounts
  useEffect(() => {
    const startWebcam = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        setWebcamStream(stream);
        if (webcamVideoRef.current) {
          webcamVideoRef.current.srcObject = stream;
        }
        console.log("Webcam started successfully");
      } catch (error) {
        console.error("Error accessing webcam:", error);
      }
    };

    startWebcam();

    // Cleanup webcam stream on unmount
    return () => {
      if (webcamStream) {
        webcamStream.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  // Handle download locally
  const handleDownload = async () => {
    try {
      // Stop the recording
      stopRecording();

      // Wait for the mediaBlobUrl to be available
      if (!mediaBlobUrl) {
        console.error("No recording available to download.");
        return;
      }

      // Fetch the recorded blob
      const response = await fetch(mediaBlobUrl);
      const blob = await response.blob();

      // Create a download link for the recording
      const timestamp = new Date().toLocaleString().replace(/[^\w\s]/gi, '');
      const filename = `recording_${timestamp}.webm`; // Use .webm for better compatibility

      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      console.log("Recording downloaded successfully");
    } catch (error) {
      console.error("Error handling download: ", error);
    }
  };

  // Start recording
  const startRecording = () => {
    startScreenRecording();
    setIsRecording(true);
  };

  // Stop recording and download
  const stopRecordingAndDownload = () => {
    stopRecording();
    setIsRecording(false);
    handleDownload();
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>
      {/* Button Bar */}
      <div style={{ display: "flex", justifyContent: "center", padding: "10px", backgroundColor: "#f0f0f0" }}>
        <button className="button" onClick={startRecording} style={{ marginRight: "10px" }}>
          Start Recording
        </button>
        <button className="button" onClick={stopRecordingAndDownload}>
          Stop Screen Recording
        </button>
      </div>

      {/* Whiteboard Container */}
      <div style={{ flex: 1, width: "200vh", height: "100%", overflow: "hidden", position: "relative",marginLeft:"5vh" }}>
        <DrawIoEmbed
          urlParameters={{
            ui: "sketch",
            spin: true,
            libraries: true,
            grid: 1,
          }}
          style={{ width: "100%", height: "100%", border: "none", transform: "scale(1)", transformOrigin: "0 0" }}
        />

        {/* Webcam Feed */}
        {webcamStream && (
          <div
            style={{
              position: "absolute",
              bottom: "20px",
              right: "20px",
              width: "600px", // Fixed width
              height: "400px", // Fixed height
              borderRadius: "8px",
              overflow: "hidden",
              boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
              zIndex: 1000,
            }}
          >
            <video
              ref={webcamVideoRef}
              autoPlay
              muted
              style={{ width: "100%", height: "100%", objectFit: "cover", transform: "scale(1)", transformOrigin: "0 0" }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default Whiteboard;