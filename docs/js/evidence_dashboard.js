/**
 * Evidence Dashboard for Forensic Video Analysis
 * =============================================
 * 
 * Interactive dashboard for displaying multi-dimensional analysis results,
 * confidence scoring, and evidence aggregation.
 */

class EvidenceDashboard {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            showStats: options.showStats !== false,
            showControls: options.showControls !== false,
            enableExport: options.enableExport !== false,
            autoUpdate: options.autoUpdate !== false,
            ...options
        };
        
        this.analysisData = null;
        this.timelineChart = null;
        this.selectedTimeRange = null;
        this.currentView = 'overview';
        
        this.init();
    }
    
    init() {
        this.createLayout();
        this.setupEventListeners();
        
        if (this.options.autoUpdate) {
            this.startAutoUpdate();
        }
    }
    
    createLayout() {
        this.container.innerHTML = `
            <div class="multi-view-container">
                <div class="view-tabs">
                    <button class="view-tab active" data-view="overview">Overview</button>
                    <button class="view-tab" data-view="timeline">Timeline Analysis</button>
                    <button class="view-tab" data-view="evidence">Evidence Details</button>
                    <button class="view-tab" data-view="comparison">Frame Comparison</button>
                </div>
                
                <div class="view-content">
                    <div id="overview-view" class="view-panel active">
                        ${this.createOverviewPanel()}
                    </div>
                    
                    <div id="timeline-view" class="view-panel">
                        ${this.createTimelinePanel()}
                    </div>
                    
                    <div id="evidence-view" class="view-panel">
                        ${this.createEvidencePanel()}
                    </div>
                    
                    <div id="comparison-view" class="view-panel">
                        ${this.createComparisonPanel()}
                    </div>
                </div>
            </div>
        `;
    }
    
    createOverviewPanel() {
        return `
            <div class="analysis-dashboard">
                <div class="main-chart-container">
                    <h3>Analysis Overview</h3>
                    <div id="overview-chart" style="height: 400px;"></div>
                    
                    ${this.options.showControls ? `
                    <div class="analysis-controls">
                        <div class="control-group">
                            <label class="control-label">Analysis Sensitivity</label>
                            <input type="range" class="control-input" id="sensitivity-slider" 
                                   min="0.1" max="3.0" step="0.1" value="1.0">
                        </div>
                        <div class="control-group">
                            <label class="control-label">Time Range (seconds)</label>
                            <input type="number" class="control-input" id="start-time" placeholder="Start" style="width: 48%; display: inline-block;">
                            <input type="number" class="control-input" id="end-time" placeholder="End" style="width: 48%; display: inline-block; margin-left: 4%;">
                        </div>
                        <button class="control-button" id="apply-filters">Apply Filters</button>
                        <button class="control-button secondary" id="reset-filters">Reset</button>
                    </div>
                    ` : ''}
                </div>
                
                <div class="analysis-sidebar">
                    ${this.options.showStats ? this.createStatsPanel() : ''}
                    
                    <div class="evidence-summary">
                        <h4>Evidence Summary</h4>
                        <div id="evidence-cards-container">
                            <!-- Evidence cards will be populated here -->
                        </div>
                    </div>
                    
                    ${this.options.enableExport ? `
                    <div class="export-controls">
                        <button class="export-button" id="export-chart">Export Chart</button>
                        <button class="export-button" id="export-report">Export Report</button>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    createTimelinePanel() {
        return `
            <div class="timeline-container">
                <h3>Comprehensive Timeline Analysis</h3>
                <div id="main-timeline-chart" style="height: 500px;"></div>
                
                <div class="timeline-controls">
                    <div class="control-group">
                        <label class="control-label">Zoom to Time Range</label>
                        <button class="control-button" id="zoom-splice-1">Splice Point 1</button>
                        <button class="control-button" id="zoom-splice-2">Splice Point 2</button>
                        <button class="control-button" id="zoom-full">Full Video</button>
                    </div>
                    
                    <div class="control-group">
                        <label class="control-label">Analysis Layers</label>
                        <label><input type="checkbox" checked> Compression</label>
                        <label><input type="checkbox" checked> Optical Flow</label>
                        <label><input type="checkbox" checked> Color Histogram</label>
                        <label><input type="checkbox" checked> Noise Pattern</label>
                        <label><input type="checkbox" checked> Combined Score</label>
                    </div>
                </div>
                
                <div class="selected-range-info">
                    <h4>Selected Range Analysis</h4>
                    <div id="range-details">
                        <p>Select a time range on the chart to see detailed analysis</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    createEvidencePanel() {
        return `
            <div class="evidence-details-container">
                <h3>Detailed Evidence Analysis</h3>
                
                <div class="evidence-filters">
                    <select id="evidence-filter" class="control-input">
                        <option value="all">All Evidence</option>
                        <option value="high">High Confidence</option>
                        <option value="medium">Medium Confidence</option>
                        <option value="compression">Compression Evidence</option>
                        <option value="motion">Motion Evidence</option>
                        <option value="color">Color Evidence</option>
                        <option value="noise">Noise Evidence</option>
                    </select>
                </div>
                
                <div id="detailed-evidence-list">
                    <!-- Detailed evidence items will be populated here -->
                </div>
            </div>
        `;
    }
    
    createComparisonPanel() {
        return `
            <div class="frame-comparison-container">
                <h3>Frame-by-Frame Comparison</h3>
                
                <div class="comparison-controls">
                    <div class="control-group">
                        <label class="control-label">Splice Point</label>
                        <select id="splice-selector" class="control-input">
                            <option value="">Select splice point...</option>
                        </select>
                    </div>
                </div>
                
                <div class="frame-comparison-grid">
                    <div class="frame-comparison-item">
                        <h4>Before Splice</h4>
                        <div id="before-frame-container">
                            <img id="before-frame" src="" alt="Before splice frame">
                            <div class="frame-metrics" id="before-metrics">
                                <!-- Metrics will be populated here -->
                            </div>
                        </div>
                    </div>
                    
                    <div class="frame-comparison-item">
                        <h4>After Splice</h4>
                        <div id="after-frame-container">
                            <img id="after-frame" src="" alt="After splice frame">
                            <div class="frame-metrics" id="after-metrics">
                                <!-- Metrics will be populated here -->
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="difference-analysis">
                    <h4>Difference Analysis</h4>
                    <div id="difference-metrics">
                        <!-- Difference metrics will be populated here -->
                    </div>
                </div>
            </div>
        `;
    }
    
    createStatsPanel() {
        return `
            <div class="stats-panel">
                <h4>Analysis Statistics</h4>
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="stat-value" id="total-samples">-</span>
                        <span class="stat-label">Total Samples</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value" id="splice-points">-</span>
                        <span class="stat-label">Splice Points</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value" id="max-confidence">-</span>
                        <span class="stat-label">Max Confidence</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value" id="analysis-duration">-</span>
                        <span class="stat-label">Duration (min)</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    setupEventListeners() {
        // View tab switching
        this.container.addEventListener('click', (e) => {
            if (e.target.classList.contains('view-tab')) {
                this.switchView(e.target.dataset.view);
            }
        });
        
        // Control interactions
        if (this.options.showControls) {
            this.setupControlListeners();
        }
        
        // Export functionality
        if (this.options.enableExport) {
            this.setupExportListeners();
        }
        
        // Timeline chart interactions
        this.container.addEventListener('pointSelected', (e) => {
            this.handlePointSelection(e.detail);
        });
        
        this.container.addEventListener('timeRangeSelected', (e) => {
            this.handleTimeRangeSelection(e.detail.timeRange);
        });
    }
    
    setupControlListeners() {
        const applyFilters = this.container.querySelector('#apply-filters');
        const resetFilters = this.container.querySelector('#reset-filters');
        const sensitivitySlider = this.container.querySelector('#sensitivity-slider');
        
        if (applyFilters) {
            applyFilters.addEventListener('click', () => this.applyFilters());
        }
        
        if (resetFilters) {
            resetFilters.addEventListener('click', () => this.resetFilters());
        }
        
        if (sensitivitySlider) {
            sensitivitySlider.addEventListener('input', (e) => {
                this.updateSensitivity(parseFloat(e.target.value));
            });
        }
    }
    
    setupExportListeners() {
        const exportChart = this.container.querySelector('#export-chart');
        const exportReport = this.container.querySelector('#export-report');
        
        if (exportChart) {
            exportChart.addEventListener('click', () => this.exportChart());
        }
        
        if (exportReport) {
            exportReport.addEventListener('click', () => this.exportReport());
        }
    }
    
    switchView(viewName) {
        // Update tab states
        this.container.querySelectorAll('.view-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.view === viewName);
        });
        
        // Update panel visibility
        this.container.querySelectorAll('.view-panel').forEach(panel => {
            panel.classList.toggle('active', panel.id === `${viewName}-view`);
        });
        
        this.currentView = viewName;
        
        // Initialize view-specific components
        this.initializeView(viewName);
    }
    
    initializeView(viewName) {
        switch (viewName) {
            case 'timeline':
                this.initializeTimelineChart();
                break;
            case 'evidence':
                this.populateEvidenceDetails();
                break;
            case 'comparison':
                this.initializeFrameComparison();
                break;
        }
    }
    
    loadAnalysisData(data) {
        this.analysisData = data;
        this.updateDashboard();
    }
    
    updateDashboard() {
        if (!this.analysisData) return;
        
        // Update statistics
        if (this.options.showStats) {
            this.updateStatistics();
        }
        
        // Update evidence cards
        this.updateEvidenceCards();
        
        // Update charts based on current view
        if (this.currentView === 'overview') {
            this.updateOverviewChart();
        } else if (this.currentView === 'timeline') {
            this.updateTimelineChart();
        }
    }
    
    updateStatistics() {
        const stats = this.analysisData.summary;
        
        this.updateStatValue('total-samples', stats.total_samples);
        this.updateStatValue('splice-points', stats.splice_points_detected);
        this.updateStatValue('max-confidence', (stats.highest_confidence * 100).toFixed(1) + '%');
        
        // Calculate analysis duration
        const duration = this.analysisData.metadata?.video_info?.duration || 0;
        this.updateStatValue('analysis-duration', (duration / 60).toFixed(1));
    }
    
    updateStatValue(id, value) {
        const element = this.container.querySelector(`#${id}`);
        if (element) {
            element.textContent = value;
        }
    }
    
    updateEvidenceCards() {
        const container = this.container.querySelector('#evidence-cards-container');
        if (!container || !this.analysisData.splice_evidence) return;
        
        container.innerHTML = '';
        
        this.analysisData.splice_evidence.forEach((evidence, index) => {
            const card = this.createEvidenceCard(evidence, index);
            container.appendChild(card);
        });
    }
    
    createEvidenceCard(evidence, index) {
        const confidenceLevel = this.getConfidenceLevel(evidence.confidence);
        const card = document.createElement('div');
        card.className = `evidence-card ${confidenceLevel}-confidence`;
        
        card.innerHTML = `
            <div class="evidence-header">
                <span class="evidence-title">Splice Point ${index + 1}</span>
                <span class="confidence-badge ${confidenceLevel}">${(evidence.confidence * 100).toFixed(1)}%</span>
            </div>
            <div class="evidence-details">
                <div>Time: ${this.formatTime(evidence.start_time)} - ${this.formatTime(evidence.end_time)}</div>
                <div>Evidence Types: ${evidence.evidence_types.join(', ')}</div>
                <div>Statistical Significance: ${evidence.statistical_significance.toFixed(2)}σ</div>
                ${evidence.visual_artifacts.length > 0 ? 
                    `<div>Artifacts: ${evidence.visual_artifacts.join(', ')}</div>` : ''}
            </div>
        `;
        
        card.addEventListener('click', () => {
            this.focusOnEvidence(evidence);
        });
        
        return card;
    }
    
    getConfidenceLevel(confidence) {
        if (confidence >= 0.8) return 'high';
        if (confidence >= 0.5) return 'medium';
        return 'low';
    }
    
    initializeTimelineChart() {
        const chartContainer = this.container.querySelector('#main-timeline-chart');
        if (!chartContainer || !this.analysisData) return;
        
        if (!this.timelineChart) {
            this.timelineChart = new ForensicTimelineChart('main-timeline-chart', {
                width: chartContainer.offsetWidth,
                height: 500,
                enableZoom: true,
                enableBrush: true
            });
        }
        
        this.timelineChart.loadData(this.analysisData.timeseries_data);
    }
    
    updateOverviewChart() {
        // Create a simplified overview chart
        const chartContainer = this.container.querySelector('#overview-chart');
        if (!chartContainer || !this.analysisData) return;
        
        // Use a smaller version of the timeline chart for overview
        if (!this.overviewChart) {
            this.overviewChart = new ForensicTimelineChart('overview-chart', {
                width: chartContainer.offsetWidth,
                height: 400,
                enableZoom: false,
                enableBrush: true,
                showLegend: true
            });
        }
        
        this.overviewChart.loadData(this.analysisData.timeseries_data);
    }
    
    handlePointSelection(detail) {
        console.log('Point selected:', detail);
        
        // Update UI to show selected point details
        this.showPointDetails(detail);
    }
    
    handleTimeRangeSelection(timeRange) {
        this.selectedTimeRange = timeRange;
        console.log('Time range selected:', timeRange);
        
        // Update range details
        this.updateRangeDetails(timeRange);
    }
    
    showPointDetails(detail) {
        // Create or update a details panel
        let detailsPanel = this.container.querySelector('.point-details-panel');
        if (!detailsPanel) {
            detailsPanel = document.createElement('div');
            detailsPanel.className = 'point-details-panel';
            this.container.appendChild(detailsPanel);
        }
        
        detailsPanel.innerHTML = `
            <h4>Analysis Point Details</h4>
            <div>Time: ${this.formatTime(detail.timestamp)}</div>
            <div>Technique: ${detail.technique}</div>
            <div>Value: ${detail.value.toFixed(3)}</div>
        `;
    }
    
    updateRangeDetails(timeRange) {
        const detailsContainer = this.container.querySelector('#range-details');
        if (!detailsContainer) return;
        
        const [startTime, endTime] = timeRange;
        const duration = endTime - startTime;
        
        detailsContainer.innerHTML = `
            <div>Selected Range: ${this.formatTime(startTime)} - ${this.formatTime(endTime)}</div>
            <div>Duration: ${duration.toFixed(1)} seconds</div>
            <div>Analysis in progress...</div>
        `;
        
        // Analyze the selected range
        this.analyzeTimeRange(timeRange);
    }
    
    analyzeTimeRange(timeRange) {
        // Perform analysis on the selected time range
        if (!this.analysisData || !this.analysisData.timeseries_data) return;
        
        const [startTime, endTime] = timeRange;
        const data = this.analysisData.timeseries_data;
        
        // Find data points in the range
        const rangeIndices = data.timestamps
            .map((time, index) => ({ time, index }))
            .filter(item => item.time >= startTime && item.time <= endTime)
            .map(item => item.index);
        
        if (rangeIndices.length === 0) return;
        
        // Calculate statistics for the range
        const rangeStats = {
            compression: this.calculateRangeStats(data.compression, rangeIndices),
            optical_flow: this.calculateRangeStats(data.optical_flow, rangeIndices),
            histogram: this.calculateRangeStats(data.histogram, rangeIndices),
            noise: this.calculateRangeStats(data.noise, rangeIndices),
            anomaly_scores: this.calculateRangeStats(data.anomaly_scores, rangeIndices)
        };
        
        this.displayRangeStats(rangeStats);
    }
    
    calculateRangeStats(dataArray, indices) {
        if (!dataArray || indices.length === 0) return { mean: 0, max: 0, min: 0, std: 0 };
        
        const values = indices.map(i => dataArray[i] || 0);
        const mean = values.reduce((a, b) => a + b, 0) / values.length;
        const max = Math.max(...values);
        const min = Math.min(...values);
        const variance = values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length;
        const std = Math.sqrt(variance);
        
        return { mean, max, min, std };
    }
    
    displayRangeStats(stats) {
        const detailsContainer = this.container.querySelector('#range-details');
        if (!detailsContainer) return;
        
        const statsHtml = Object.entries(stats).map(([technique, stat]) => `
            <div class="range-stat-item">
                <strong>${technique.replace('_', ' ').toUpperCase()}</strong>
                <div>Mean: ${stat.mean.toFixed(3)}, Max: ${stat.max.toFixed(3)}, Std: ${stat.std.toFixed(3)}</div>
            </div>
        `).join('');
        
        detailsContainer.innerHTML += `
            <div class="range-statistics">
                <h5>Range Statistics</h5>
                ${statsHtml}
            </div>
        `;
    }
    
    focusOnEvidence(evidence) {
        // Switch to timeline view and focus on the evidence
        this.switchView('timeline');
        
        setTimeout(() => {
            if (this.timelineChart) {
                this.timelineChart.zoomToTimeRange(evidence.start_time, evidence.end_time);
                this.timelineChart.highlightTimeRange(evidence.start_time, evidence.end_time);
            }
        }, 100);
    }
    
    applyFilters() {
        const startTime = parseFloat(this.container.querySelector('#start-time')?.value || 0);
        const endTime = parseFloat(this.container.querySelector('#end-time')?.value || Infinity);
        const sensitivity = parseFloat(this.container.querySelector('#sensitivity-slider')?.value || 1.0);
        
        // Apply filters to the analysis
        this.filterAnalysisData(startTime, endTime, sensitivity);
    }
    
    resetFilters() {
        // Reset all filter controls
        const startTimeInput = this.container.querySelector('#start-time');
        const endTimeInput = this.container.querySelector('#end-time');
        const sensitivitySlider = this.container.querySelector('#sensitivity-slider');
        
        if (startTimeInput) startTimeInput.value = '';
        if (endTimeInput) endTimeInput.value = '';
        if (sensitivitySlider) sensitivitySlider.value = '1.0';
        
        // Reload original data
        this.updateDashboard();
    }
    
    filterAnalysisData(startTime, endTime, sensitivity) {
        // Implementation for filtering analysis data
        console.log('Applying filters:', { startTime, endTime, sensitivity });
    }
    
    updateSensitivity(sensitivity) {
        // Update analysis sensitivity
        console.log('Sensitivity updated:', sensitivity);
    }
    
    exportChart() {
        if (this.timelineChart) {
            this.timelineChart.exportChart();
        }
    }
    
    exportReport() {
        // Generate and download a comprehensive report
        const report = this.generateReport();
        this.downloadReport(report);
    }
    
    generateReport() {
        if (!this.analysisData) return null;
        
        const report = {
            title: 'Forensic Video Analysis Report',
            timestamp: new Date().toISOString(),
            summary: this.analysisData.summary,
            evidence: this.analysisData.splice_evidence,
            metadata: this.analysisData.metadata
        };
        
        return report;
    }
    
    downloadReport(report) {
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = 'forensic-analysis-report.json';
        link.click();
        
        URL.revokeObjectURL(url);
    }
    
    formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours}h ${minutes}m ${secs}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    }
    
    startAutoUpdate() {
        // Implement auto-update functionality if needed
        setInterval(() => {
            // Check for new analysis data
        }, 5000);
    }
}

// Export for use in other modules
window.EvidenceDashboard = EvidenceDashboard;

