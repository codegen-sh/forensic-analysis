/**
 * Interactive Timeline Chart for Forensic Video Analysis
 * =====================================================
 * 
 * Advanced time-series visualization showing compression changes,
 * anomaly detection, and multi-dimensional analysis results.
 */

class ForensicTimelineChart {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            width: options.width || 1200,
            height: options.height || 600,
            margin: { top: 20, right: 80, bottom: 60, left: 80 },
            showLegend: options.showLegend !== false,
            enableZoom: options.enableZoom !== false,
            enableBrush: options.enableBrush !== false,
            ...options
        };
        
        this.data = null;
        this.chart = null;
        this.scales = {};
        this.axes = {};
        this.lines = {};
        this.brushSelection = null;
        
        this.init();
    }
    
    init() {
        // Create main SVG
        this.svg = d3.select(this.container)
            .append('svg')
            .attr('width', this.options.width)
            .attr('height', this.options.height)
            .attr('class', 'forensic-timeline-chart');
        
        // Create chart group
        this.chartGroup = this.svg.append('g')
            .attr('transform', `translate(${this.options.margin.left}, ${this.options.margin.top})`);
        
        // Calculate chart dimensions
        this.chartWidth = this.options.width - this.options.margin.left - this.options.margin.right;
        this.chartHeight = this.options.height - this.options.margin.top - this.options.margin.bottom;
        
        // Create scales
        this.setupScales();
        
        // Create axes
        this.setupAxes();
        
        // Create line generators
        this.setupLineGenerators();
        
        // Setup interactions
        this.setupInteractions();
        
        // Create legend
        if (this.options.showLegend) {
            this.createLegend();
        }
    }
    
    setupScales() {
        this.scales.x = d3.scaleLinear()
            .range([0, this.chartWidth]);
        
        this.scales.y = d3.scaleLinear()
            .range([this.chartHeight, 0]);
        
        this.scales.color = d3.scaleOrdinal()
            .domain(['compression', 'optical_flow', 'histogram', 'noise', 'anomaly_scores'])
            .range(['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57']);
    }
    
    setupAxes() {
        // X-axis (time)
        this.axes.x = d3.axisBottom(this.scales.x)
            .tickFormat(d => this.formatTime(d));
        
        this.chartGroup.append('g')
            .attr('class', 'x-axis')
            .attr('transform', `translate(0, ${this.chartHeight})`);
        
        // Y-axis (anomaly score)
        this.axes.y = d3.axisLeft(this.scales.y);
        
        this.chartGroup.append('g')
            .attr('class', 'y-axis');
        
        // Add axis labels
        this.svg.append('text')
            .attr('class', 'axis-label')
            .attr('text-anchor', 'middle')
            .attr('x', this.options.width / 2)
            .attr('y', this.options.height - 10)
            .text('Time (seconds)');
        
        this.svg.append('text')
            .attr('class', 'axis-label')
            .attr('text-anchor', 'middle')
            .attr('transform', 'rotate(-90)')
            .attr('x', -this.options.height / 2)
            .attr('y', 20)
            .text('Anomaly Score');
    }
    
    setupLineGenerators() {
        this.lineGenerator = d3.line()
            .x(d => this.scales.x(d.timestamp))
            .y(d => this.scales.y(d.value))
            .curve(d3.curveMonotoneX);
    }
    
    setupInteractions() {
        // Zoom behavior
        if (this.options.enableZoom) {
            this.zoom = d3.zoom()
                .scaleExtent([1, 50])
                .extent([[0, 0], [this.chartWidth, this.chartHeight]])
                .on('zoom', (event) => this.handleZoom(event));
            
            this.svg.call(this.zoom);
        }
        
        // Brush for selection
        if (this.options.enableBrush) {
            this.brush = d3.brushX()
                .extent([[0, 0], [this.chartWidth, this.chartHeight]])
                .on('brush end', (event) => this.handleBrush(event));
            
            this.brushGroup = this.chartGroup.append('g')
                .attr('class', 'brush');
        }
        
        // Tooltip
        this.tooltip = d3.select('body').append('div')
            .attr('class', 'forensic-tooltip')
            .style('opacity', 0);
    }
    
    loadData(timeseriesData) {
        this.data = timeseriesData;
        this.processData();
        this.updateChart();
    }
    
    processData() {
        if (!this.data || !this.data.timestamps) {
            console.error('Invalid data format');
            return;
        }
        
        // Convert data to chart format
        this.chartData = {};
        const techniques = ['compression', 'optical_flow', 'histogram', 'noise', 'anomaly_scores'];
        
        techniques.forEach(technique => {
            this.chartData[technique] = this.data.timestamps.map((timestamp, i) => ({
                timestamp: timestamp,
                value: this.data[technique] ? this.data[technique][i] || 0 : 0
            }));
        });
        
        // Update scales
        const timeExtent = d3.extent(this.data.timestamps);
        this.scales.x.domain(timeExtent);
        
        const allValues = techniques.flatMap(technique => 
            this.data[technique] || []
        );
        const valueExtent = d3.extent(allValues);
        this.scales.y.domain([0, Math.max(valueExtent[1] * 1.1, 1)]);
    }
    
    updateChart() {
        // Update axes
        this.chartGroup.select('.x-axis')
            .transition()
            .duration(750)
            .call(this.axes.x);
        
        this.chartGroup.select('.y-axis')
            .transition()
            .duration(750)
            .call(this.axes.y);
        
        // Draw lines for each technique
        Object.keys(this.chartData).forEach(technique => {
            this.drawLine(technique, this.chartData[technique]);
        });
        
        // Add anomaly markers
        this.addAnomalyMarkers();
        
        // Add brush if enabled
        if (this.options.enableBrush) {
            this.brushGroup.call(this.brush);
        }
    }
    
    drawLine(technique, data) {
        const lineGroup = this.chartGroup.selectAll(`.line-group-${technique}`)
            .data([data]);
        
        const lineGroupEnter = lineGroup.enter()
            .append('g')
            .attr('class', `line-group line-group-${technique}`);
        
        // Draw line
        lineGroupEnter.append('path')
            .attr('class', `line line-${technique}`)
            .attr('fill', 'none')
            .attr('stroke', this.scales.color(technique))
            .attr('stroke-width', 2)
            .attr('opacity', 0.8);
        
        // Update line
        lineGroup.select(`.line-${technique}`)
            .datum(data)
            .transition()
            .duration(750)
            .attr('d', this.lineGenerator);
        
        // Add data points
        const circles = lineGroup.selectAll(`.point-${technique}`)
            .data(data);
        
        circles.enter()
            .append('circle')
            .attr('class', `point point-${technique}`)
            .attr('r', 3)
            .attr('fill', this.scales.color(technique))
            .attr('opacity', 0.7)
            .on('mouseover', (event, d) => this.showTooltip(event, d, technique))
            .on('mouseout', () => this.hideTooltip())
            .on('click', (event, d) => this.handlePointClick(event, d, technique));
        
        circles.transition()
            .duration(750)
            .attr('cx', d => this.scales.x(d.timestamp))
            .attr('cy', d => this.scales.y(d.value));
        
        circles.exit().remove();
    }
    
    addAnomalyMarkers() {
        if (!this.data.anomaly_scores) return;
        
        // Find significant anomalies
        const threshold = d3.mean(this.data.anomaly_scores) + 2 * d3.deviation(this.data.anomaly_scores);
        const anomalies = this.data.timestamps
            .map((timestamp, i) => ({
                timestamp,
                value: this.data.anomaly_scores[i],
                isAnomaly: this.data.anomaly_scores[i] > threshold
            }))
            .filter(d => d.isAnomaly);
        
        // Draw anomaly markers
        const markers = this.chartGroup.selectAll('.anomaly-marker')
            .data(anomalies);
        
        markers.enter()
            .append('line')
            .attr('class', 'anomaly-marker')
            .attr('stroke', '#ff4757')
            .attr('stroke-width', 2)
            .attr('stroke-dasharray', '5,5')
            .attr('opacity', 0.8);
        
        markers
            .attr('x1', d => this.scales.x(d.timestamp))
            .attr('x2', d => this.scales.x(d.timestamp))
            .attr('y1', 0)
            .attr('y2', this.chartHeight);
        
        markers.exit().remove();
        
        // Add anomaly labels
        const labels = this.chartGroup.selectAll('.anomaly-label')
            .data(anomalies);
        
        labels.enter()
            .append('text')
            .attr('class', 'anomaly-label')
            .attr('fill', '#ff4757')
            .attr('font-size', '12px')
            .attr('text-anchor', 'middle')
            .text('SPLICE');
        
        labels
            .attr('x', d => this.scales.x(d.timestamp))
            .attr('y', -5);
        
        labels.exit().remove();
    }
    
    createLegend() {
        const legend = this.svg.append('g')
            .attr('class', 'legend')
            .attr('transform', `translate(${this.options.width - 150}, 30)`);
        
        const techniques = ['compression', 'optical_flow', 'histogram', 'noise', 'anomaly_scores'];
        const labels = {
            'compression': 'Compression',
            'optical_flow': 'Optical Flow',
            'histogram': 'Color Histogram',
            'noise': 'Noise Pattern',
            'anomaly_scores': 'Combined Score'
        };
        
        const legendItems = legend.selectAll('.legend-item')
            .data(techniques)
            .enter()
            .append('g')
            .attr('class', 'legend-item')
            .attr('transform', (d, i) => `translate(0, ${i * 20})`);
        
        legendItems.append('line')
            .attr('x1', 0)
            .attr('x2', 15)
            .attr('y1', 0)
            .attr('y2', 0)
            .attr('stroke', d => this.scales.color(d))
            .attr('stroke-width', 2);
        
        legendItems.append('text')
            .attr('x', 20)
            .attr('y', 0)
            .attr('dy', '0.35em')
            .attr('font-size', '12px')
            .text(d => labels[d]);
    }
    
    showTooltip(event, data, technique) {
        const formatValue = d3.format('.2f');
        
        this.tooltip.transition()
            .duration(200)
            .style('opacity', 0.9);
        
        this.tooltip.html(`
            <div class="tooltip-header">${technique.replace('_', ' ').toUpperCase()}</div>
            <div class="tooltip-content">
                <div>Time: ${this.formatTime(data.timestamp)}</div>
                <div>Value: ${formatValue(data.value)}</div>
            </div>
        `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px');
    }
    
    hideTooltip() {
        this.tooltip.transition()
            .duration(500)
            .style('opacity', 0);
    }
    
    handlePointClick(event, data, technique) {
        // Emit custom event for point selection
        const customEvent = new CustomEvent('pointSelected', {
            detail: { timestamp: data.timestamp, technique, value: data.value }
        });
        this.container.dispatchEvent(customEvent);
    }
    
    handleZoom(event) {
        const newXScale = event.transform.rescaleX(this.scales.x);
        
        // Update axes
        this.chartGroup.select('.x-axis').call(this.axes.x.scale(newXScale));
        
        // Update lines
        Object.keys(this.chartData).forEach(technique => {
            this.chartGroup.select(`.line-${technique}`)
                .attr('d', this.lineGenerator.x(d => newXScale(d.timestamp)));
            
            this.chartGroup.selectAll(`.point-${technique}`)
                .attr('cx', d => newXScale(d.timestamp));
        });
        
        // Update anomaly markers
        this.chartGroup.selectAll('.anomaly-marker')
            .attr('x1', d => newXScale(d.timestamp))
            .attr('x2', d => newXScale(d.timestamp));
        
        this.chartGroup.selectAll('.anomaly-label')
            .attr('x', d => newXScale(d.timestamp));
    }
    
    handleBrush(event) {
        if (!event.selection) return;
        
        const [x0, x1] = event.selection;
        const timeRange = [this.scales.x.invert(x0), this.scales.x.invert(x1)];
        
        // Emit custom event for brush selection
        const customEvent = new CustomEvent('timeRangeSelected', {
            detail: { timeRange }
        });
        this.container.dispatchEvent(customEvent);
        
        this.brushSelection = timeRange;
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
    
    // Public methods for external control
    zoomToTimeRange(startTime, endTime) {
        const x0 = this.scales.x(startTime);
        const x1 = this.scales.x(endTime);
        const scale = this.chartWidth / (x1 - x0);
        const translate = -x0 * scale;
        
        this.svg.transition()
            .duration(750)
            .call(this.zoom.transform, d3.zoomIdentity.translate(translate, 0).scale(scale));
    }
    
    highlightTimeRange(startTime, endTime) {
        // Remove existing highlights
        this.chartGroup.selectAll('.time-highlight').remove();
        
        // Add new highlight
        this.chartGroup.append('rect')
            .attr('class', 'time-highlight')
            .attr('x', this.scales.x(startTime))
            .attr('y', 0)
            .attr('width', this.scales.x(endTime) - this.scales.x(startTime))
            .attr('height', this.chartHeight)
            .attr('fill', 'yellow')
            .attr('opacity', 0.2);
    }
    
    exportChart() {
        // Create a new SVG for export
        const exportSvg = this.svg.node().cloneNode(true);
        const serializer = new XMLSerializer();
        const svgString = serializer.serializeToString(exportSvg);
        
        // Create download link
        const blob = new Blob([svgString], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = 'forensic-timeline-chart.svg';
        link.click();
        
        URL.revokeObjectURL(url);
    }
}

// Export for use in other modules
window.ForensicTimelineChart = ForensicTimelineChart;

