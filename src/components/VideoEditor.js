import { useState, useRef } from "react";

export default function VideoEditor() {
  const [videoSrc, setVideoSrc] = useState(null);
  const [fileName, setFileName] = useState("");
  const [trimStart, setTrimStart] = useState(0);
  const [trimEnd, setTrimEnd] = useState(0);
  const [duration, setDuration] = useState(0);
  const videoRef = useRef(null);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileName(file.name);
      const url = URL.createObjectURL(file);
      setVideoSrc(url);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      const dur = videoRef.current.duration;
      setDuration(dur);
      setTrimEnd(dur);
    }
  };

  const handlePlay = () => {
    if (videoRef.current) {
      videoRef.current.currentTime = trimStart;
      videoRef.current.play();
    }
  };

  const handlePreviewTrim = () => {
    if (videoRef.current) {
      videoRef.current.currentTime = trimStart;
      videoRef.current.play();
      const checkTime = setInterval(() => {
        if (videoRef.current && videoRef.current.currentTime >= trimEnd) {
          videoRef.current.pause();
          clearInterval(checkTime);
        }
      }, 100);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="video-editor">
      <h2>Video Editor</h2>

      {!videoSrc ? (
        <div className="upload-area">
          <label className="upload-btn">
            Upload Video
            <input
              type="file"
              accept="video/*"
              onChange={handleFileUpload}
              style={{ display: "none" }}
            />
          </label>
          <p className="upload-hint">MP4, WebM, MOV supported</p>
        </div>
      ) : (
        <div className="editor-workspace">
          <div className="video-preview">
            <video
              ref={videoRef}
              src={videoSrc}
              onLoadedMetadata={handleLoadedMetadata}
              controls
              style={{ width: "100%", borderRadius: "8px" }}
            />
            <p className="file-name">{fileName}</p>
          </div>

          <div className="trim-controls">
            <h3>Trim Video</h3>
            <div className="trim-inputs">
              <div className="trim-field">
                <label>Start: {formatTime(trimStart)}</label>
                <input
                  type="range"
                  min={0}
                  max={duration}
                  step={0.1}
                  value={trimStart}
                  onChange={(e) => {
                    const val = parseFloat(e.target.value);
                    if (val < trimEnd) setTrimStart(val);
                  }}
                />
              </div>
              <div className="trim-field">
                <label>End: {formatTime(trimEnd)}</label>
                <input
                  type="range"
                  min={0}
                  max={duration}
                  step={0.1}
                  value={trimEnd}
                  onChange={(e) => {
                    const val = parseFloat(e.target.value);
                    if (val > trimStart) setTrimEnd(val);
                  }}
                />
              </div>
              <p className="duration-info">
                Selected: {formatTime(trimEnd - trimStart)} / Total: {formatTime(duration)}
              </p>
            </div>
            <div className="trim-actions">
              <button className="btn-preview" onClick={handlePreviewTrim}>
                Preview Trim
              </button>
              <button className="btn-play" onClick={handlePlay}>
                Play from Start
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}