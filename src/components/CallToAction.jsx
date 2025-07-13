function CallToAction() {
  return (
    <div className="cta-section">
      <h3>🚀 Reproduce This Analysis</h3>
      <p style={{ marginBottom: '20px', fontSize: '1.1rem' }}>
        All tools and methods are open source. Verify our findings independently using the same techniques.
      </p>
      <a 
        href="https://github.com/codegen-sh/forensic-analysis" 
        className="cta-button"
        target="_blank"
        rel="noopener noreferrer"
      >
        📁 View Source Code
      </a>
      <a 
        href="https://github.com/codegen-sh/forensic-analysis/blob/main/README.md" 
        className="cta-button"
        target="_blank"
        rel="noopener noreferrer"
      >
        📖 Read Documentation
      </a>
      <a 
        href="https://github.com/codegen-sh/forensic-analysis/releases" 
        className="cta-button"
        target="_blank"
        rel="noopener noreferrer"
      >
        ⬇️ Download Tools
      </a>
    </div>
  )
}

export default CallToAction

