import ExpandableSection from './ExpandableSection'

function LegalImplications() {
  return (
    <div className="evidence-card">
      <h3>⚖️ Legal and Ethical Considerations</h3>
      <p style={{ marginBottom: '20px' }}>
        This analysis is provided for digital forensics research, transparency in government evidence presentation, 
        and public interest in evidence integrity.
      </p>

      <ExpandableSection title="Analysis Scope & Limitations">
        <ul style={{ paddingLeft: '20px' }}>
          <li>Does not modify the original video file</li>
          <li>Focuses solely on technical metadata examination</li>
          <li>Uses standard digital forensics methodologies</li>
          <li>Makes no claims about the events depicted in the video</li>
          <li>Findings should be verified independently by qualified experts</li>
        </ul>
      </ExpandableSection>

      <ExpandableSection title="Educational Purpose">
        <p style={{ marginBottom: '15px' }}>
          This tool is provided for educational and research purposes. The analysis demonstrates:
        </p>
        <ul style={{ paddingLeft: '20px' }}>
          <li>Digital forensics research and education techniques</li>
          <li>Metadata analysis methodologies</li>
          <li>Video editing detection methods</li>
          <li>Chain of custody considerations in digital evidence</li>
        </ul>
      </ExpandableSection>

      <ExpandableSection title="Disclaimer">
        <div style={{ 
          background: 'rgba(255, 107, 107, 0.1)', 
          padding: '15px', 
          borderRadius: '8px',
          border: '1px solid #ff6b6b'
        }}>
          <p style={{ color: '#ff6b6b', fontWeight: 'bold', marginBottom: '10px' }}>
            ⚠️ Important Notice
          </p>
          <p>
            This analysis is based on technical metadata examination using standard digital forensics practices. 
            Users should verify findings independently and consult with qualified digital forensics experts 
            for legal or evidentiary purposes. The findings presented here are for educational and research 
            purposes only.
          </p>
        </div>
      </ExpandableSection>
    </div>
  )
}

export default LegalImplications

