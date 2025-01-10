import React, { useState, useRef, useEffect } from "react";
import { DrawIoEmbed } from "react-drawio";

function Whiteboard() {
  const [webcamStream, setWebcamStream] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedChunks, setRecordedChunks] = useState([]);
  const webcamVideoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const combinedStreamRef = useRef(null);

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
      if (combinedStreamRef.current) {
        combinedStreamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  // Start recording
  const startRecording = async () => {
    try {
      // Get screen and webcam streams
      const screenStream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: true,
      });
      const webcamStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });

      // Combine screen and webcam streams
      const combinedStream = new MediaStream([
        ...screenStream.getVideoTracks(),
        ...webcamStream.getAudioTracks(),
        ...webcamStream.getVideoTracks(),
      ]);

      combinedStreamRef.current = combinedStream;

      // Create a MediaRecorder instance
      const mediaRecorder = new MediaRecorder(combinedStream, {
        mimeType: "video/webm; codecs=vp9",
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          setRecordedChunks((prev) => [...prev, event.data]);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(recordedChunks, { type: "video/webm" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `recording_${new Date().toISOString()}.webm`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        // Reset recorded chunks
        setRecordedChunks([]);
      };

      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
    } catch (error) {
      console.error("Error starting recording:", error);
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current = null;
      setIsRecording(false);
    }
    if (combinedStreamRef.current) {
      combinedStreamRef.current.getTracks().forEach((track) => track.stop());
      combinedStreamRef.current = null;
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>
      {/* Button Bar */}
      <div style={{ display: "flex", justifyContent: "center", padding: "10px", backgroundColor: "#f0f0f0" }}>
        <button
          className="button"
          onClick={startRecording}
          disabled={isRecording}
          style={{ marginRight: "10px" }}
        >
          Start Recording
        </button>
        <button
          className="button"
          onClick={stopRecording}
          disabled={!isRecording}
        >
          Stop Recording
        </button>
      </div>

      {/* Whiteboard Container */}
      <div style={{ flex: 1, width: "100%", height: "100%", overflow: "hidden", position: "relative" }}>
        <DrawIoEmbed
          urlParameters={{
            ui: "sketch",
            spin: true,
            libraries: true,
          }}
          style={{ width: "100%", height: "100%", border: "none" }}
        />

        {/* Webcam Feed */}
        {webcamStream && (
          <div
            style={{
              position: "absolute",
              bottom: "20px",
              right: "20px",
              width: "300px",
              height: "200px",
              borderRadius: "8px",
              overflow: "hidden",
              boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
              zIndex: 1000,
              marginRight: "35vh",
            }}
          >
            <video
              ref={webcamVideoRef}
              autoPlay
              muted
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default Whiteboard;