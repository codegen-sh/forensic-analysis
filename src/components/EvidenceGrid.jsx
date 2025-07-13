import FrameViewer from './FrameViewer'

function EvidenceGrid() {
  return (
    <div className="evidence-grid">
      <div className="evidence-card">
        <h3>🔍 Adobe Editing Signatures</h3>
        <p>Definitive proof of professional video editing software usage:</p>
        <div className="command-block">
CreatorTool: <span className="highlight">Adobe Media Encoder 2024.0 (Windows)</span>
{'\n'}WindowsAtomUncProjectPath: <span className="highlight">MJCOLE~1</span>
{'\n'}Project: <span className="highlight">mcc_4.prproj</span>
        </div>
        <p><strong>Command used:</strong></p>
        <div className="command-block">
exiftool -CreatorTool -WindowsAtomUncProjectPath raw_video.mp4
        </div>
      </div>
      
      <div className="evidence-card">
        <h3>⏰ Splice Point Calculation</h3>
        <p>Adobe timing metadata reveals exact splice location:</p>
        <div className="command-block">
Adobe Timing: time:0d<span className="highlight">6035539564454400</span>f<span className="highlight">254016000000</span>
{'\n'}Calculation: 6035539564454400 ÷ 254016000000
{'\n'}Result: <span className="highlight">23760.47 seconds = 6h 36m 0s</span>
        </div>
        <p><strong>Command used:</strong></p>
        <div className="command-block">
python3 -c "print(6035539564454400 / 254016000000)"
        </div>
      </div>
      
      <div className="evidence-card">
        <h3>🎬 Visual Frame Evidence</h3>
        <p>Frame analysis confirms splice point with compression discontinuity:</p>
        <div className="command-block">
Frame 2 (6h36m00s): <span className="highlight">2,155,188 bytes</span>
{'\n'}Frame 3 (6h36m01s): <span className="highlight">2,263,396 bytes</span>
{'\n'}Size Change: <span className="highlight">+108,208 bytes (+5.0%)</span>
        </div>
        
        <FrameViewer />
        
        <p><strong>Commands used:</strong></p>
        <div className="command-block">
ffmpeg -ss 23759 -t 4 -vf "fps=1" frames/frame_%03d.png video.mp4
{'\n'}ls -la frames/*.png | awk '{'{'}print $9, $5{'}'}'
        </div>
      </div>
      
      <div className="evidence-card">
        <h3>📁 Source Clips Identified</h3>
        <p>Multiple source files found in Adobe XMP metadata:</p>
        <div className="command-block">
Clip 1: <span className="highlight">2025-05-22 21-12-48.mp4</span> (23.76 sec)
{'\n'}Clip 2: <span className="highlight">2025-05-22 16-35-21.mp4</span> (15.56 sec)
{'\n'}Total: <span className="highlight">39.32 seconds</span> of replacement content
        </div>
        <p>These clips were spliced into the surveillance video at the 6h 36m mark, replacing original footage.</p>
      </div>
    </div>
  )
}

export default EvidenceGrid

