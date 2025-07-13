function StatsGrid() {
  return (
    <div className="stats-grid">
      <div className="stat-card">
        <span className="stat-number">23,760</span>
        <div className="stat-label">Splice Point (seconds)</div>
      </div>
      <div className="stat-card">
        <span className="stat-number">39</span>
        <div className="stat-label">Seconds Replaced</div>
      </div>
      <div className="stat-card">
        <span className="stat-number">5.0%</span>
        <div className="stat-label">Frame Size Change</div>
      </div>
      <div className="stat-card">
        <span className="stat-number">2</span>
        <div className="stat-label">Source Files</div>
      </div>
    </div>
  )
}

export default StatsGrid

