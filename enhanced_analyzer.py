#!/usr/bin/env python3
"""
Enhanced Forensic Video Analysis Framework
==========================================

Advanced multi-dimensional analysis system for detecting video splicing and manipulation
using comprehensive computer vision techniques and time-series analysis.

Features:
- Whole-video compression analysis with time-series visualization
- Optical flow discontinuity detection
- Color histogram analysis for lighting/camera changes
- Noise pattern analysis for encoding source detection
- Interactive timeline visualization with anomaly highlighting
- Confidence scoring and evidence aggregation

Author: Computational Forensics Analysis
Version: 2.0
Date: January 2025
"""

import os
import sys
import json
import subprocess
import numpy as np
import cv2
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Data structure for storing analysis results with metadata."""
    timestamp: float
    frame_number: int
    technique: str
    confidence: float
    evidence_type: str
    details: Dict[str, Any]
    anomaly_score: float = 0.0

@dataclass
class SpliceEvidence:
    """Comprehensive evidence structure for splice detection."""
    start_time: float
    end_time: float
    confidence: float
    evidence_types: List[str]
    analysis_results: List[AnalysisResult]
    statistical_significance: float
    visual_artifacts: List[str]

class EnhancedVideoAnalyzer:
    """Advanced forensic video analysis system."""
    
    def __init__(self, video_path: str, output_dir: str = "enhanced_analysis"):
        self.video_path = video_path
        self.output_dir = output_dir
        self.cache_dir = os.path.join(output_dir, "cache")
        self.data_dir = os.path.join(output_dir, "data")
        
        # Analysis configuration
        self.config = {
            "sampling_rate": 1.0,  # seconds between samples
            "analysis_window": 10.0,  # seconds around splice points
            "confidence_threshold": 0.7,
            "anomaly_threshold": 2.0,  # standard deviations
            "parallel_workers": 4
        }
        
        # Analysis modules
        self.analyzers = {}
        self.results = []
        self.splice_evidence = []
        
        # Video metadata
        self.video_info = None
        self.total_frames = 0
        self.fps = 0
        self.duration = 0
        
        self._setup_directories()
        self._initialize_analyzers()
    
    def _setup_directories(self):
        """Create necessary directories for analysis output."""
        for directory in [self.output_dir, self.cache_dir, self.data_dir]:
            os.makedirs(directory, exist_ok=True)
        logger.info(f"Analysis directories created: {self.output_dir}")
    
    def _initialize_analyzers(self):
        """Initialize all analysis modules."""
        from analysis_modules.compression_analyzer import CompressionAnalyzer
        from analysis_modules.optical_flow_analyzer import OpticalFlowAnalyzer
        from analysis_modules.histogram_analyzer import HistogramAnalyzer
        from analysis_modules.noise_analyzer import NoiseAnalyzer
        
        self.analyzers = {
            'compression': CompressionAnalyzer(self.config),
            'optical_flow': OpticalFlowAnalyzer(self.config),
            'histogram': HistogramAnalyzer(self.config),
            'noise': NoiseAnalyzer(self.config)
        }
        logger.info(f"Initialized {len(self.analyzers)} analysis modules")
    
    def analyze_video(self, progress_callback=None) -> Dict[str, Any]:
        """
        Perform comprehensive video analysis.
        
        Args:
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dictionary containing all analysis results and evidence
        """
        logger.info(f"Starting comprehensive analysis of {self.video_path}")
        
        # Step 1: Extract video metadata
        self._extract_video_metadata()
        
        # Step 2: Generate analysis timeline
        timeline = self._generate_analysis_timeline()
        
        # Step 3: Run parallel analysis
        analysis_results = self._run_parallel_analysis(timeline, progress_callback)
        
        # Step 4: Detect anomalies and splice points
        splice_evidence = self._detect_splice_points(analysis_results)
        
        # Step 5: Generate comprehensive report
        report = self._generate_analysis_report(analysis_results, splice_evidence)
        
        # Step 6: Save results
        self._save_analysis_results(report)
        
        logger.info("Analysis complete")
        return report
    
    def _extract_video_metadata(self):
        """Extract comprehensive video metadata using ffprobe."""
        logger.info("Extracting video metadata...")
        
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', self.video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            metadata = json.loads(result.stdout)
            
            # Extract video stream info
            video_stream = next(s for s in metadata['streams'] if s['codec_type'] == 'video')
            
            self.video_info = {
                'duration': float(metadata['format']['duration']),
                'size': int(metadata['format']['size']),
                'bitrate': int(metadata['format'].get('bit_rate', 0)),
                'fps': eval(video_stream['r_frame_rate']),
                'width': int(video_stream['width']),
                'height': int(video_stream['height']),
                'codec': video_stream['codec_name'],
                'pixel_format': video_stream['pix_fmt']
            }
            
            self.duration = self.video_info['duration']
            self.fps = self.video_info['fps']
            self.total_frames = int(self.duration * self.fps)
            
            logger.info(f"Video: {self.duration:.1f}s, {self.total_frames} frames, {self.fps:.2f} fps")
            
        except Exception as e:
            logger.error(f"Failed to extract video metadata: {e}")
            raise
    
    def _generate_analysis_timeline(self) -> List[float]:
        """Generate timestamps for analysis sampling."""
        sampling_rate = self.config['sampling_rate']
        timeline = []
        
        current_time = 0.0
        while current_time < self.duration:
            timeline.append(current_time)
            current_time += sampling_rate
        
        logger.info(f"Generated timeline with {len(timeline)} sample points")
        return timeline
    
    def _run_parallel_analysis(self, timeline: List[float], progress_callback=None) -> List[AnalysisResult]:
        """Run all analysis modules in parallel across the timeline."""
        logger.info("Starting parallel analysis...")
        
        all_results = []
        total_tasks = len(timeline) * len(self.analyzers)
        completed_tasks = 0
        
        with ThreadPoolExecutor(max_workers=self.config['parallel_workers']) as executor:
            # Submit all analysis tasks
            future_to_info = {}
            
            for timestamp in timeline:
                for analyzer_name, analyzer in self.analyzers.items():
                    future = executor.submit(self._analyze_timestamp, analyzer_name, analyzer, timestamp)
                    future_to_info[future] = (analyzer_name, timestamp)
            
            # Collect results as they complete
            for future in as_completed(future_to_info):
                analyzer_name, timestamp = future_to_info[future]
                
                try:
                    result = future.result()
                    if result:
                        all_results.append(result)
                    
                    completed_tasks += 1
                    if progress_callback:
                        progress = completed_tasks / total_tasks
                        progress_callback(progress, f"Analyzing {analyzer_name} at {timestamp:.1f}s")
                        
                except Exception as e:
                    logger.error(f"Analysis failed for {analyzer_name} at {timestamp:.1f}s: {e}")
        
        logger.info(f"Parallel analysis complete: {len(all_results)} results")
        return sorted(all_results, key=lambda x: x.timestamp)
    
    def _analyze_timestamp(self, analyzer_name: str, analyzer, timestamp: float) -> Optional[AnalysisResult]:
        """Analyze a single timestamp with a specific analyzer."""
        try:
            # Extract frame at timestamp
            frame = self._extract_frame_at_timestamp(timestamp)
            if frame is None:
                return None
            
            # Run analysis
            result = analyzer.analyze_frame(frame, timestamp)
            
            if result:
                return AnalysisResult(
                    timestamp=timestamp,
                    frame_number=int(timestamp * self.fps),
                    technique=analyzer_name,
                    confidence=result.get('confidence', 0.0),
                    evidence_type=result.get('evidence_type', 'unknown'),
                    details=result.get('details', {}),
                    anomaly_score=result.get('anomaly_score', 0.0)
                )
            
        except Exception as e:
            logger.error(f"Error analyzing {analyzer_name} at {timestamp:.1f}s: {e}")
        
        return None
    
    def _extract_frame_at_timestamp(self, timestamp: float) -> Optional[np.ndarray]:
        """Extract a single frame at the specified timestamp."""
        cache_key = f"frame_{timestamp:.3f}.npy"
        cache_path = os.path.join(self.cache_dir, cache_key)
        
        # Check cache first
        if os.path.exists(cache_path):
            return np.load(cache_path)
        
        # Extract frame using ffmpeg
        cmd = [
            'ffmpeg', '-ss', str(timestamp), '-i', self.video_path,
            '-vframes', '1', '-f', 'image2pipe', '-pix_fmt', 'rgb24',
            '-vcodec', 'rawvideo', '-'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, check=True)
            
            # Convert raw bytes to numpy array
            width, height = self.video_info['width'], self.video_info['height']
            frame_data = np.frombuffer(result.stdout, dtype=np.uint8)
            frame = frame_data.reshape((height, width, 3))
            
            # Cache the frame
            np.save(cache_path, frame)
            
            return frame
            
        except Exception as e:
            logger.error(f"Failed to extract frame at {timestamp:.1f}s: {e}")
            return None
    
    def _detect_splice_points(self, results: List[AnalysisResult]) -> List[SpliceEvidence]:
        """Detect splice points using statistical analysis of anomaly scores."""
        logger.info("Detecting splice points...")
        
        # Group results by timestamp
        timestamp_groups = {}
        for result in results:
            ts = result.timestamp
            if ts not in timestamp_groups:
                timestamp_groups[ts] = []
            timestamp_groups[ts].append(result)
        
        # Calculate aggregate anomaly scores
        timeline_anomalies = []
        for timestamp in sorted(timestamp_groups.keys()):
            group_results = timestamp_groups[timestamp]
            
            # Weighted average of anomaly scores
            total_weight = 0
            weighted_score = 0
            
            for result in group_results:
                weight = result.confidence
                weighted_score += result.anomaly_score * weight
                total_weight += weight
            
            if total_weight > 0:
                avg_anomaly = weighted_score / total_weight
                timeline_anomalies.append((timestamp, avg_anomaly, group_results))
        
        # Detect anomalies using statistical thresholds
        anomaly_scores = [score for _, score, _ in timeline_anomalies]
        mean_score = np.mean(anomaly_scores)
        std_score = np.std(anomaly_scores)
        threshold = mean_score + (self.config['anomaly_threshold'] * std_score)
        
        # Find splice evidence
        splice_evidence = []
        for timestamp, anomaly_score, group_results in timeline_anomalies:
            if anomaly_score > threshold:
                # Create splice evidence
                evidence_types = list(set(r.evidence_type for r in group_results))
                confidence = min(1.0, anomaly_score / threshold)
                
                splice_evidence.append(SpliceEvidence(
                    start_time=max(0, timestamp - self.config['analysis_window'] / 2),
                    end_time=min(self.duration, timestamp + self.config['analysis_window'] / 2),
                    confidence=confidence,
                    evidence_types=evidence_types,
                    analysis_results=group_results,
                    statistical_significance=(anomaly_score - mean_score) / std_score,
                    visual_artifacts=self._identify_visual_artifacts(group_results)
                ))
        
        logger.info(f"Detected {len(splice_evidence)} potential splice points")
        return splice_evidence
    
    def _identify_visual_artifacts(self, results: List[AnalysisResult]) -> List[str]:
        """Identify specific visual artifacts from analysis results."""
        artifacts = []
        
        for result in results:
            details = result.details
            
            if result.technique == 'compression' and details.get('size_change_percent', 0) > 5:
                artifacts.append(f"Compression discontinuity: {details['size_change_percent']:.1f}%")
            
            if result.technique == 'optical_flow' and details.get('flow_discontinuity', False):
                artifacts.append("Motion vector discontinuity")
            
            if result.technique == 'histogram' and details.get('color_shift', False):
                artifacts.append("Color histogram shift")
            
            if result.technique == 'noise' and details.get('noise_pattern_change', False):
                artifacts.append("Noise pattern inconsistency")
        
        return artifacts
    
    def _generate_analysis_report(self, results: List[AnalysisResult], evidence: List[SpliceEvidence]) -> Dict[str, Any]:
        """Generate comprehensive analysis report."""
        logger.info("Generating analysis report...")
        
        # Calculate overall statistics
        technique_stats = {}
        for result in results:
            technique = result.technique
            if technique not in technique_stats:
                technique_stats[technique] = {
                    'count': 0,
                    'avg_confidence': 0,
                    'avg_anomaly': 0,
                    'max_anomaly': 0
                }
            
            stats = technique_stats[technique]
            stats['count'] += 1
            stats['avg_confidence'] += result.confidence
            stats['avg_anomaly'] += result.anomaly_score
            stats['max_anomaly'] = max(stats['max_anomaly'], result.anomaly_score)
        
        # Finalize averages
        for stats in technique_stats.values():
            if stats['count'] > 0:
                stats['avg_confidence'] /= stats['count']
                stats['avg_anomaly'] /= stats['count']
        
        # Generate time-series data for visualization
        timeseries_data = self._generate_timeseries_data(results)
        
        report = {
            'metadata': {
                'video_path': self.video_path,
                'analysis_timestamp': datetime.now().isoformat(),
                'video_info': self.video_info,
                'config': self.config
            },
            'summary': {
                'total_samples': len(set(r.timestamp for r in results)),
                'splice_points_detected': len(evidence),
                'highest_confidence': max((e.confidence for e in evidence), default=0),
                'technique_stats': technique_stats
            },
            'splice_evidence': [asdict(e) for e in evidence],
            'timeseries_data': timeseries_data,
            'analysis_results': [asdict(r) for r in results]
        }
        
        return report
    
    def _generate_timeseries_data(self, results: List[AnalysisResult]) -> Dict[str, List]:
        """Generate time-series data optimized for visualization."""
        timeseries = {
            'timestamps': [],
            'compression': [],
            'optical_flow': [],
            'histogram': [],
            'noise': [],
            'anomaly_scores': []
        }
        
        # Group by timestamp
        timestamp_data = {}
        for result in results:
            ts = result.timestamp
            if ts not in timestamp_data:
                timestamp_data[ts] = {}
            timestamp_data[ts][result.technique] = result
        
        # Generate series data
        for timestamp in sorted(timestamp_data.keys()):
            data = timestamp_data[timestamp]
            
            timeseries['timestamps'].append(timestamp)
            
            # Extract values for each technique
            for technique in ['compression', 'optical_flow', 'histogram', 'noise']:
                if technique in data:
                    timeseries[technique].append(data[technique].anomaly_score)
                else:
                    timeseries[technique].append(0)
            
            # Calculate aggregate anomaly score
            anomaly_scores = [data[t].anomaly_score for t in data.keys()]
            timeseries['anomaly_scores'].append(np.mean(anomaly_scores) if anomaly_scores else 0)
        
        return timeseries
    
    def _save_analysis_results(self, report: Dict[str, Any]):
        """Save analysis results to files."""
        # Save main report
        report_path = os.path.join(self.data_dir, 'analysis_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save timeseries data separately for visualization
        timeseries_path = os.path.join(self.data_dir, 'timeseries_data.json')
        with open(timeseries_path, 'w') as f:
            json.dump(report['timeseries_data'], f, indent=2)
        
        logger.info(f"Analysis results saved to {self.data_dir}")

def main():
    """Main entry point for enhanced analysis."""
    if len(sys.argv) < 2:
        print("Usage: python enhanced_analyzer.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)
    
    # Initialize analyzer
    analyzer = EnhancedVideoAnalyzer(video_path)
    
    # Run analysis with progress reporting
    def progress_callback(progress, message):
        print(f"\rProgress: {progress*100:.1f}% - {message}", end='', flush=True)
    
    try:
        report = analyzer.analyze_video(progress_callback)
        print(f"\n\nAnalysis complete!")
        print(f"Detected {len(report['splice_evidence'])} potential splice points")
        print(f"Results saved to: {analyzer.data_dir}")
        
    except Exception as e:
        print(f"\nError during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

