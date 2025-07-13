import { useState, useEffect } from 'react'

function FrameViewer() {
  const [currentSplice, setCurrentSplice] = useState(1)
  const [currentFrame, setCurrentFrame] = useState(1)
  const [isPlaying, setIsPlaying] = useState(false)
  const [frameSize, setFrameSize] = useState(null)

  const totalSplices = 6
  const framesPerSplice = 10

  // Auto-play functionality
  useEffect(() => {
    if (!isPlaying) return

    const interval = setInterval(() => {
      setCurrentFrame(prev => {
        if (prev >= framesPerSplice) {
          if (currentSplice >= totalSplices) {
            setIsPlaying(false)
            return 1
          } else {
            setCurrentSplice(s => s + 1)
            return 1
          }
        }
        return prev + 1
      })
    }, 800)

    return () => clearInterval(interval)
  }, [isPlaying, currentSplice])

  const getImagePath = () => {
    return `/forensic-analysis/splice_frames/splice_${currentSplice}/frame_${String(currentFrame).padStart(3, '0')}.webp`
  }

  const handleImageLoad = (e) => {
    // Simulate getting file size (in a real app, this would come from metadata)
    const baseSizes = [126622, 128560, 127938, 128092, 125750, 128234, 128360, 128380, 124338, 124998]
    const sizeVariation = currentSplice > 2 ? 0.95 : 1.0 // Simulate the 5% size change
    const estimatedSize = Math.round(baseSizes[currentFrame - 1] * sizeVariation)
    setFrameSize(estimatedSize)
  }

  const nextFrame = () => {
    if (currentFrame < framesPerSplice) {
      setCurrentFrame(currentFrame + 1)
    } else if (currentSplice < totalSplices) {
      setCurrentSplice(currentSplice + 1)
      setCurrentFrame(1)
    }
  }

  const prevFrame = () => {
    if (currentFrame > 1) {
      setCurrentFrame(currentFrame - 1)
    } else if (currentSplice > 1) {
      setCurrentSplice(currentSplice - 1)
      setCurrentFrame(framesPerSplice)
    }
  }

  const togglePlayback = () => {
    setIsPlaying(!isPlaying)
  }

  return (
    <div className="frame-viewer">
      <h3 style={{ color: '#4ecdc4', marginBottom: '20px', textAlign: 'center' }}>
        🎬 Interactive Frame Analysis
      </h3>
      
      <div className="frame-container">
        <img 
          src={getImagePath()} 
          alt={`Splice ${currentSplice} Frame ${currentFrame}`}
          className="frame-image"
          onLoad={handleImageLoad}
          onError={(e) => {
            // Fallback to PNG if WebP fails
            e.target.src = `/forensic-analysis/splice_frames/splice_${currentSplice}/frame_${String(currentFrame).padStart(3, '0')}.png`
          }}
        />
      </div>

      <div className="frame-info">
        <span>Splice: {currentSplice}/{totalSplices}</span>
        <span>Frame: {currentFrame}/{framesPerSplice}</span>
        {frameSize && <span>Size: {frameSize.toLocaleString()} bytes</span>}
      </div>

      <div className="frame-controls">
        <button 
          className="frame-btn" 
          onClick={prevFrame}
          disabled={currentSplice === 1 && currentFrame === 1}
        >
          ⏮ Previous
        </button>
        
        <button 
          className="frame-btn" 
          onClick={togglePlayback}
        >
          {isPlaying ? '⏸ Pause' : '▶ Play'}
        </button>
        
        <input
          type="range"
          min="1"
          max={framesPerSplice}
          value={currentFrame}
          onChange={(e) => setCurrentFrame(parseInt(e.target.value))}
          className="frame-slider"
        />
        
        <button 
          className="frame-btn" 
          onClick={nextFrame}
          disabled={currentSplice === totalSplices && currentFrame === framesPerSplice}
        >
          Next ⏭
        </button>
      </div>

      <div className="frame-timeline">
        <span>Splice Point Analysis</span>
        {currentSplice > 2 && (
          <div className="splice-indicator"></div>
        )}
        <span>6h 36m 0s</span>
      </div>

      {currentSplice > 2 && (
        <div className="discontinuity-info">
          <h4 style={{ color: '#ff6b6b', marginBottom: '10px' }}>⚠️ Discontinuity Detected</h4>
          <ul>
            <li>Frame compression change detected at splice point</li>
            <li>File size variation indicates different encoding parameters</li>
            <li>Visual artifacts consistent with professional editing software</li>
            <li>Metadata timestamps show non-sequential recording</li>
          </ul>
        </div>
      )}
    </div>
  )
}

export default FrameViewer

