import React, { useState, useRef, useEffect } from "react";

const RecordView = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [mediaBlobUrl, setMediaBlobUrl] = useState(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const videoRef = useRef(null);

  // Start recording
  const startRecording = async () => {
    try {
      // Request access to the user's screen, microphone, and webcam
      const screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
      const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const webcamStream = await navigator.mediaDevices.getUserMedia({ video: true });

      // Combine all streams into one
      const combinedStream = new MediaStream([
        ...screenStream.getTracks(),
        ...audioStream.getTracks(),
        ...webcamStream.getTracks(),
      ]);

      // Initialize the MediaRecorder
      mediaRecorderRef.current = new MediaRecorder(combinedStream, { mimeType: "video/webm" });

      // Handle data available event
      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      // Handle recording stop event
      mediaRecorderRef.current.onstop = () => {
        // Create a Blob from the recorded chunks
        const blob = new Blob(chunksRef.current, { type: "video/webm" });

        // Create a new video element to ensure metadata is loaded
        const video = document.createElement("video");
        video.src = URL.createObjectURL(blob);

        video.onloadedmetadata = () => {
          // Revoke the old URL
          if (mediaBlobUrl) {
            URL.revokeObjectURL(mediaBlobUrl);
          }

          // Set the new Blob URL
          const newBlobUrl = URL.createObjectURL(blob);
          setMediaBlobUrl(newBlobUrl);

          // Clean up the chunks array
          chunksRef.current = [];

          // Stop all tracks in the streams
          screenStream.getTracks().forEach((track) => track.stop());
          audioStream.getTracks().forEach((track) => track.stop());
          webcamStream.getTracks().forEach((track) => track.stop());
        };
      };

      // Start recording
      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error accessing media devices:", error);
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      // Request the final data chunk
      mediaRecorderRef.current.requestData();

      // Stop the recorder
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Handle download
  const handleDownload = () => {
    if (mediaBlobUrl) {
      const a = document.createElement("a");
      a.href = mediaBlobUrl;
      a.download = `recorded-video-${new Date().toISOString()}.webm`; // Set the filename
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  // Clean up on component unmount
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop();
      }
      if (mediaBlobUrl) {
        URL.revokeObjectURL(mediaBlobUrl);
      }
    };
  }, [mediaBlobUrl]);

  return (
    <div>
      <p>Status: {isRecording ? "Recording" : "Idle"}</p>
      <button onClick={startRecording} disabled={isRecording}>
        Start Recording
      </button>
      <button onClick={stopRecording} disabled={!isRecording}>
        Stop Recording
      </button>
      {mediaBlobUrl && (
        <div>
          <video ref={videoRef} src={mediaBlobUrl} controls autoPlay loop />
          <br />
          <button onClick={handleDownload}>Download Video</button>
        </div>
      )}
    </div>
  );
};

export default RecordView;