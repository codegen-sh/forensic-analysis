function LegalImplications() {
  const implications = [
    "Misrepresentation: Video labeled as \"raw\" despite professional editing",
    "Content Modification: Original surveillance footage was altered using Adobe software", 
    "Source Substitution: Multiple video files combined into single presentation",
    "Chain of Custody: Evidence integrity compromised through undisclosed editing",
    "Transparency: Editing process not disclosed in official documentation"
  ]

  return (
    <div className="evidence-card">
      <h3>⚖️ Legal and Ethical Implications</h3>
      <p>This computational analysis reveals several concerning issues:</p>
      <ul style={{ marginLeft: "20px", marginTop: "15px" }}>
        {implications.map((implication, index) => (
          <li key={index}>
            <strong>{implication.split(':')[0]}:</strong> {implication.split(':')[1]}
          </li>
        ))}
      </ul>
      <p style={{ marginTop: "15px" }}>
        <strong>Note:</strong> This analysis focuses solely on technical metadata examination and makes no claims about the events depicted in the video.
      </p>
    </div>
  )
}

export default LegalImplications

