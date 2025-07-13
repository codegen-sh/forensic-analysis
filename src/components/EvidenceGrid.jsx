import FrameViewer from './FrameViewer'
import ExpandableSection from './ExpandableSection'

function EvidenceGrid() {
  return (
    <div className="evidence-grid">
      <div className="evidence-card">
        <h3>🔍 Adobe Editing Signatures</h3>
        <p>Comprehensive metadata analysis reveals definitive proof of professional video editing:</p>
        
        <ExpandableSection title="View Technical Details">
          <div className="command-block">
            exiftool -CreatorTool -WindowsAtomUncProjectPath raw_video.mp4<br/>
            # Output: Adobe Media Encoder 2024.0 (Windows)
          </div>
          <ul style={{ marginTop: '15px', paddingLeft: '20px' }}>
            <li><strong>Software:</strong> Adobe Media Encoder 2024.0 (Windows)</li>
            <li><strong>User Account:</strong> <span className="highlight">MJCOLE~1</span></li>
            <li><strong>Project File:</strong> mcc_4.prproj</li>
            <li><strong>XMP Metadata:</strong> Extensive Adobe-specific editing data</li>
          </ul>
        </ExpandableSection>
      </div>

      <div className="evidence-card">
        <h3>📊 Source File Analysis</h3>
        <p>Multiple source video files identified through metadata examination:</p>
        
        <ExpandableSection title="View Source Files">
          <ul style={{ paddingLeft: '20px' }}>
            <li><strong>File 1:</strong> 2025-05-22 21-12-48.mp4 (23.76 seconds)</li>
            <li><strong>File 2:</strong> 2025-05-22 16-35-21.mp4 (15.56 seconds)</li>
            <li><strong>Total spliced content:</strong> ~39 seconds</li>
            <li><strong>Splice location:</strong> 6h 36m 0s into the video</li>
          </ul>
          <div className="command-block" style={{ marginTop: '15px' }}>
            python3 -c "print(6035539564454400 / 254016000000)"<br/>
            # Output: 23760.47 seconds = 6h 36m 0s
          </div>
        </ExpandableSection>
      </div>

      <FrameViewer />

      <div className="evidence-card">
        <h3>⚖️ Chain of Custody Issues</h3>
        <p>Critical problems with evidence integrity and presentation:</p>
        
        <ExpandableSection title="View Legal Implications">
          <ul style={{ paddingLeft: '20px' }}>
            <li>❌ <strong>Not raw footage</strong> - processed through professional editing software</li>
            <li>❌ <strong>Multiple sources</strong> - assembled from separate video files</li>
            <li>❌ <strong>Content substitution</strong> - 39 seconds replaced at critical time point</li>
            <li>❌ <strong>Deceptive labeling</strong> - calling edited footage "raw" surveillance</li>
            <li>❌ <strong>Undisclosed editing</strong> - no mention of post-processing in official documentation</li>
          </ul>
        </ExpandableSection>
      </div>
    </div>
  )
}

export default EvidenceGrid

