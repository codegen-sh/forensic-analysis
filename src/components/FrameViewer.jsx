import { useState, useEffect } from 'react'

function FrameViewer() {
  const frameData = [
    { filename: "frame_001.png", path: "splice_frames/splice_1/frame_001.png", size: "2,116,047 bytes", time: "6h35m55s" },
    { filename: "frame_002.png", path: "splice_frames/splice_1/frame_002.png", size: "2,084,324 bytes", time: "6h35m56s" },
    { filename: "frame_003.png", path: "splice_frames/splice_1/frame_003.png", size: "2,012,467 bytes", time: "6h35m57s" },
    { filename: "frame_004.png", path: "splice_frames/splice_1/frame_004.png", size: "2,086,191 bytes", time: "6h35m58s" },
    { filename: "frame_005.png", path: "splice_frames/splice_1/frame_005.png", size: "2,062,775 bytes", time: "6h35m59s" },
    { filename: "frame_006.png", path: "splice_frames/splice_1/frame_006.png", size: "2,108,242 bytes", time: "6h36m00s" },
    { filename: "frame_007.png", path: "splice_frames/splice_1/frame_007.png", size: "2,067,485 bytes", time: "6h36m01s" },
    { filename: "frame_008.png", path: "splice_frames/splice_1/frame_008.png", size: "2,048,178 bytes", time: "6h36m02s" },
    { filename: "frame_009.png", path: "splice_frames/splice_1/frame_009.png", size: "2,010,795 bytes", time: "6h36m03s" },
    { filename: "frame_010.png", path: "splice_frames/splice_1/frame_010.png", size: "2,055,549 bytes", time: "6h36m04s" }
  ]

  const [currentFrameIndex, setCurrentFrameIndex] = useState(0)
  const [isAutoPlaying, setIsAutoPlaying] = useState(false)

  useEffect(() => {
    let interval = null
    if (isAutoPlaying) {
      interval = setInterval(() => {
        setCurrentFrameIndex(prevIndex => {
          const nextIndex = prevIndex + 1
          return nextIndex >= frameData.length ? 0 : nextIndex
        })
      }, 1000)
    }
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [isAutoPlaying, frameData.length])

  const currentFrame = frameData[currentFrameIndex]
  const isDiscontinuityFrame = currentFrameIndex === 1 || currentFrameIndex === 2

  const handleSliderChange = (e) => {
    setCurrentFrameIndex(parseInt(e.target.value))
  }

  const previousFrame = () => {
    if (currentFrameIndex > 0) {
      setCurrentFrameIndex(currentFrameIndex - 1)
    }
  }

  const nextFrame = () => {
    if (currentFrameIndex < frameData.length - 1) {
      setCurrentFrameIndex(currentFrameIndex + 1)
    }
  }

  const toggleAutoPlay = () => {
    setIsAutoPlaying(!isAutoPlaying)
  }

  return (
    <div className="frame-viewer">
      <h4>🎬 Interactive Frame Analysis - Splice Point Evidence</h4>
      <p>Use the slider below to examine frames around the splice point and observe the discontinuity:</p>
      
      <div className="frame-container">
        <img 
          src={currentFrame.path} 
          alt={`Frame ${currentFrameIndex + 1}`}
          className="frame-image"
          style={{
            border: isDiscontinuityFrame ? "3px solid #ff6b6b" : "2px solid #555"
          }}
        />
        <div className="frame-info">
          <span>Frame {currentFrameIndex + 1} of {frameData.length}</span>
          <span>{currentFrame.filename} ({currentFrame.time})</span>
          <span 
            style={{
              color: isDiscontinuityFrame ? "#ff6b6b" : "#e0e0e0",
              fontWeight: isDiscontinuityFrame ? "bold" : "normal"
            }}
          >
            Size: {currentFrame.size}
          </span>
        </div>
      </div>
      
      <div className="frame-controls">
        <button 
          onClick={previousFrame} 
          className="frame-btn"
          disabled={currentFrameIndex === 0}
        >
          ◀ Previous
        </button>
        <input 
          type="range" 
          min="0" 
          max={frameData.length - 1} 
          value={currentFrameIndex}
          onChange={handleSliderChange}
          className="frame-slider"
        />
        <button 
          onClick={nextFrame} 
          className="frame-btn"
          disabled={currentFrameIndex === frameData.length - 1}
        >
          Next ▶
        </button>
        <button 
          onClick={toggleAutoPlay} 
          className="frame-btn"
          style={{
            background: isAutoPlaying ? "#ff6b6b" : "#4ecdc4"
          }}
        >
          {isAutoPlaying ? "⏸ Stop" : "▶ Auto Play"}
        </button>
      </div>
      
      <div className="frame-timeline">
        <span>Before Splice (6h35m55s)</span>
        <div className="splice-indicator"></div>
        <span>After Splice (6h36m05s)</span>
      </div>
      
      <div className="discontinuity-info">
        <p><strong>🔍 What to look for:</strong></p>
        <ul>
          <li>Frame 2-3: Notice the <span className="highlight">5.0% file size jump</span> indicating compression change</li>
          <li>Visual artifacts or quality differences between frames</li>
          <li>Timing discontinuities at the splice boundary</li>
        </ul>
      </div>
    </div>
  )
}

export default FrameViewer

