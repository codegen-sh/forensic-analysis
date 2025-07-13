import { useState } from 'react'

function ExpandableSection({ title, children, defaultExpanded = false }) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  return (
    <div className="expandable-section">
      <button 
        className="expand-button"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span>{title}</span>
        <span>{isExpanded ? '▼' : '▶'}</span>
      </button>
      {isExpanded && (
        <div className="expandable-content">
          {children}
        </div>
      )}
    </div>
  )
}

export default ExpandableSection

