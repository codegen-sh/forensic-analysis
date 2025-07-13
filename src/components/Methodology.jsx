import ExpandableSection from './ExpandableSection'

function Methodology() {
  return (
    <div className="methodology">
      <h3>🔬 Technical Methodology</h3>
      <p style={{ marginBottom: '20px', color: '#ccc' }}>
        Our analysis follows standard digital forensics practices using industry-standard tools and techniques.
      </p>

      <ExpandableSection title="Step 1: Video Acquisition & Verification" defaultExpanded={true}>
        <div className="step">
          <h4>Download and Integrity Check</h4>
          <p>Downloaded the 19.5 GB DOJ video file and verified its integrity using cryptographic hashes.</p>
          <div className="command-block">
            wget https://www.justice.gov/opa/media/1407001/dl?inline -O raw_video.mp4<br/>
            sha256sum raw_video.mp4
          </div>
        </div>
      </ExpandableSection>

      <ExpandableSection title="Step 2: Metadata Extraction">
        <div className="step">
          <h4>Comprehensive Metadata Analysis</h4>
          <p>Used ExifTool to extract all embedded metadata, including Adobe-specific XMP data.</p>
          <div className="command-block">
            exiftool -all -G1 -s raw_video.mp4 &gt; metadata.txt<br/>
            exiftool -XMP -b raw_video.mp4 &gt; xmp_metadata.xml
          </div>
          <ul style={{ marginTop: '10px', paddingLeft: '20px' }}>
            <li>Creator tool identification</li>
            <li>Project file path extraction</li>
            <li>Timeline and editing history</li>
            <li>Source file references</li>
          </ul>
        </div>
      </ExpandableSection>

      <ExpandableSection title="Step 3: Splice Point Calculation">
        <div className="step">
          <h4>Mathematical Analysis</h4>
          <p>Calculated exact splice location using metadata timestamps and frame rates.</p>
          <div className="command-block">
            # XMP metadata shows splice at frame: 6035539564454400<br/>
            # Video timebase: 254016000000<br/>
            python3 -c "print(6035539564454400 / 254016000000)"<br/>
            # Result: 23760.47 seconds = 6h 36m 0s
          </div>
        </div>
      </ExpandableSection>

      <ExpandableSection title="Step 4: Frame Analysis">
        <div className="step">
          <h4>Visual Discontinuity Detection</h4>
          <p>Extracted frames around the calculated splice point to verify visual evidence.</p>
          <div className="command-block">
            ffmpeg -ss 23759 -t 4 -vf "fps=1" -q:v 2 splice_frames/frame_%03d.png raw_video.mp4<br/>
            ls -la splice_frames/frame_*.png | awk '&#123;print $9, $5&#125;'
          </div>
          <ul style={{ marginTop: '10px', paddingLeft: '20px' }}>
            <li>5.0% file size change between consecutive frames</li>
            <li>Compression artifacts indicating different encoding</li>
            <li>Visual discontinuities at predicted splice point</li>
          </ul>
        </div>
      </ExpandableSection>

      <ExpandableSection title="Step 5: Validation & Documentation">
        <div className="step">
          <h4>Independent Verification</h4>
          <p>Cross-referenced findings with multiple analysis tools and documented all procedures.</p>
          <ul style={{ paddingLeft: '20px' }}>
            <li>MediaInfo analysis for additional metadata</li>
            <li>Hexadecimal inspection of file headers</li>
            <li>Frame-by-frame visual inspection</li>
            <li>Statistical analysis of compression patterns</li>
          </ul>
        </div>
      </ExpandableSection>
    </div>
  )
}

export default Methodology
