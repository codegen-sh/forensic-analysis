import { useState } from 'react'

function ExpandableSection({ title, children, defaultExpanded = false }) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  return (
    <div className="expandable-section">
      <button 
        className="expand-button"
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          background: 'linear-gradient(135deg, #4ecdc4, #45b7aa)',
          color: '#000',
          border: 'none',
          padding: '10px 20px',
          borderRadius: '8px',
          cursor: 'pointer',
          fontWeight: 'bold',
          fontSize: '1rem',
          marginBottom: '15px',
          transition: 'all 0.3s ease',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          width: '100%',
          justifyContent: 'space-between'
        }}
      >
        <span>{title}</span>
        <span style={{ transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.3s ease' }}>
          ▼
        </span>
      </button>
      {isExpanded && (
        <div 
          className="expandable-content"
          style={{
            animation: 'fadeIn 0.3s ease-in-out',
            background: 'rgba(255, 255, 255, 0.05)',
            padding: '20px',
            borderRadius: '8px',
            border: '1px solid #333'
          }}
        >
          {children}
        </div>
      )}
    </div>
  )
}

export default ExpandableSection

