import ExpandableSection from './ExpandableSection'

function Methodology() {
  const steps = [
    {
      title: "1. Metadata Extraction",
      description: "Used ExifTool to extract all embedded metadata, including Adobe's proprietary XMP editing data.",
      command: "exiftool -j -a -u -g1 raw_video.mp4",
      details: "ExifTool is the industry standard for metadata extraction. The flags used: -j (JSON output), -a (allow duplicate tags), -u (unknown tags), -g1 (group by category)."
    },
    {
      title: "2. Adobe XMP Analysis", 
      description: "Parsed Adobe's internal editing metadata to identify software signatures and timing information.",
      command: "exiftool -xmp -b raw_video.mp4",
      details: "XMP (Extensible Metadata Platform) contains Adobe's proprietary editing information, including project files, timing data, and software signatures."
    },
    {
      title: "3. Timing Calculation",
      description: "Decoded Adobe's proprietary timing format to locate exact splice points in the video.",
      command: 'python3 -c "print(6035539564454400 / 254016000000)"',
      details: "Adobe uses a specific timing format where the numerator represents ticks and the denominator represents ticks per second. This calculation reveals the exact timestamp."
    },
    {
      title: "4. Frame Extraction & Analysis",
      description: "Extracted frames around predicted splice points and analyzed file sizes for compression discontinuities.",
      command: 'ffmpeg -ss 23759 -t 4 -vf "fps=1" frames/frame_%03d.png video.mp4',
      details: "FFmpeg extracts frames at 1fps starting from the calculated splice point. File size analysis reveals compression changes that indicate editing."
    }
  ]

  return (
    <div className="methodology">
      <h3>🔬 Computational Forensics Methodology</h3>
      <p>This analysis used industry-standard digital forensics tools and techniques:</p>
      
      {steps.map((step, index) => (
        <ExpandableSection key={index} title={step.title} defaultExpanded={index === 0}>
          <p>{step.description}</p>
          <div className="command-block">{step.command}</div>
          <p style={{ marginTop: '15px', fontStyle: 'italic', color: '#ccc' }}>
            <strong>Technical Details:</strong> {step.details}
          </p>
        </ExpandableSection>
      ))}
    </div>
  )
}

export default Methodology
