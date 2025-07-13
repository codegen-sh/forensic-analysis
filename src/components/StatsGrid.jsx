function StatsGrid() {
  const stats = [
    { number: "19.5", label: "GB Video File" },
    { number: "10.9", label: "Hours Duration" },
    { number: "6:36", label: "Splice Location" },
    { number: "5.0%", label: "Frame Size Change" }
  ]

  return (
    <div className="stats-grid">
      {stats.map((stat, index) => (
        <div key={index} className="stat-card">
          <span className="stat-number">{stat.number}</span>
          <div className="stat-label">{stat.label}</div>
        </div>
      ))}
    </div>
  )
}

export default StatsGrid

