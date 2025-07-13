"""
Histogram Analysis Module
========================

Detects color and lighting discontinuities that may indicate video splicing
through comprehensive histogram analysis and color distribution examination.
"""

import numpy as np
import cv2
from typing import Dict, Any, Optional, List
import logging
from scipy import stats

logger = logging.getLogger(__name__)

class HistogramAnalyzer:
    """Analyzes color histograms to detect lighting and camera changes."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.baseline_histograms = None
        self.histogram_history = []
        self.max_history = 10
        
        # Histogram parameters
        self.hist_bins = 64  # Reduced bins for better stability
        self.hist_range = [0, 256]
    
    def analyze_frame(self, frame: np.ndarray, timestamp: float) -> Optional[Dict[str, Any]]:
        """
        Analyze color histogram characteristics of a frame.
        
        Args:
            frame: RGB frame data as numpy array
            timestamp: Frame timestamp in seconds
            
        Returns:
            Dictionary containing histogram analysis results
        """
        try:
            # Calculate comprehensive histogram metrics
            hist_metrics = self._calculate_histogram_metrics(frame)
            
            # Detect color shifts and lighting changes
            color_analysis = self._analyze_color_changes(hist_metrics)
            
            # Calculate anomaly score
            anomaly_score = self._calculate_histogram_anomaly_score(hist_metrics, color_analysis)
            
            # Update history
            self._update_histogram_history(hist_metrics, timestamp)
            
            result = {
                'confidence': min(1.0, anomaly_score / 2.5),
                'evidence_type': 'color_shift' if color_analysis['significant_shift'] else 'normal',
                'anomaly_score': anomaly_score,
                'details': {
                    'brightness_mean': hist_metrics['brightness_mean'],
                    'contrast_std': hist_metrics['contrast_std'],
                    'color_temperature': hist_metrics['color_temperature'],
                    'saturation_mean': hist_metrics['saturation_mean'],
                    'histogram_correlation': color_analysis.get('histogram_correlation', 1.0),
                    'brightness_change_percent': color_analysis.get('brightness_change_percent', 0),
                    'color_shift': color_analysis['significant_shift'],
                    'dominant_color_change': color_analysis.get('dominant_color_change', False),
                    'lighting_change_score': color_analysis.get('lighting_change_score', 0)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Histogram analysis failed at {timestamp:.1f}s: {e}")
            return None
    
    def _calculate_histogram_metrics(self, frame: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive histogram and color metrics."""
        # Convert to different color spaces for analysis
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame_hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        frame_lab = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2LAB)
        frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        
        # 1. Basic brightness and contrast
        brightness_mean = np.mean(frame_gray)
        contrast_std = np.std(frame_gray)
        
        # 2. Color temperature estimation
        color_temperature = self._estimate_color_temperature(frame_bgr)
        
        # 3. Saturation analysis
        saturation_mean = np.mean(frame_hsv[:, :, 1])
        
        # 4. RGB histograms
        rgb_histograms = self._calculate_rgb_histograms(frame)
        
        # 5. HSV histograms
        hsv_histograms = self._calculate_hsv_histograms(frame_hsv)
        
        # 6. LAB histograms
        lab_histograms = self._calculate_lab_histograms(frame_lab)
        
        # 7. Dominant colors
        dominant_colors = self._extract_dominant_colors(frame_bgr)
        
        # 8. Color distribution metrics
        color_distribution = self._analyze_color_distribution(frame_bgr)
        
        return {
            'brightness_mean': brightness_mean,
            'contrast_std': contrast_std,
            'color_temperature': color_temperature,
            'saturation_mean': saturation_mean,
            **rgb_histograms,
            **hsv_histograms,
            **lab_histograms,
            **dominant_colors,
            **color_distribution
        }
    
    def _calculate_rgb_histograms(self, frame: np.ndarray) -> Dict[str, np.ndarray]:
        """Calculate RGB channel histograms."""
        histograms = {}
        
        for i, channel in enumerate(['r', 'g', 'b']):
            hist = cv2.calcHist([frame], [i], None, [self.hist_bins], self.hist_range)
            hist = hist.flatten() / hist.sum()  # Normalize
            histograms[f'{channel}_hist'] = hist
            histograms[f'{channel}_hist_mean'] = np.mean(hist)
            histograms[f'{channel}_hist_std'] = np.std(hist)
        
        return histograms
    
    def _calculate_hsv_histograms(self, frame_hsv: np.ndarray) -> Dict[str, Any]:
        """Calculate HSV channel histograms."""
        histograms = {}
        
        # Hue histogram (circular)
        h_hist = cv2.calcHist([frame_hsv], [0], None, [180], [0, 180])
        h_hist = h_hist.flatten() / h_hist.sum()
        
        # Saturation histogram
        s_hist = cv2.calcHist([frame_hsv], [1], None, [self.hist_bins], self.hist_range)
        s_hist = s_hist.flatten() / s_hist.sum()
        
        # Value histogram
        v_hist = cv2.calcHist([frame_hsv], [2], None, [self.hist_bins], self.hist_range)
        v_hist = v_hist.flatten() / v_hist.sum()
        
        histograms.update({
            'h_hist': h_hist,
            's_hist': s_hist,
            'v_hist': v_hist,
            'h_hist_entropy': self._calculate_histogram_entropy(h_hist),
            's_hist_entropy': self._calculate_histogram_entropy(s_hist),
            'v_hist_entropy': self._calculate_histogram_entropy(v_hist)
        })
        
        return histograms
    
    def _calculate_lab_histograms(self, frame_lab: np.ndarray) -> Dict[str, Any]:
        """Calculate LAB channel histograms."""
        histograms = {}
        
        for i, channel in enumerate(['l', 'a', 'b']):
            hist = cv2.calcHist([frame_lab], [i], None, [self.hist_bins], self.hist_range)
            hist = hist.flatten() / hist.sum()
            histograms[f'{channel}_lab_hist'] = hist
            histograms[f'{channel}_lab_entropy'] = self._calculate_histogram_entropy(hist)
        
        return histograms
    
    def _calculate_histogram_entropy(self, histogram: np.ndarray) -> float:
        """Calculate entropy of a histogram."""
        # Add small epsilon to avoid log(0)
        histogram = histogram + 1e-10
        entropy = -np.sum(histogram * np.log2(histogram))
        return entropy
    
    def _estimate_color_temperature(self, frame_bgr: np.ndarray) -> float:
        """Estimate color temperature using RGB ratios."""
        try:
            # Calculate mean RGB values
            b_mean = np.mean(frame_bgr[:, :, 0])
            g_mean = np.mean(frame_bgr[:, :, 1])
            r_mean = np.mean(frame_bgr[:, :, 2])
            
            # Avoid division by zero
            if b_mean == 0:
                return 5500  # Default daylight temperature
            
            # Simple color temperature estimation
            # Based on the ratio of red to blue
            rb_ratio = r_mean / b_mean
            
            # Map ratio to approximate color temperature (Kelvin)
            if rb_ratio > 1.5:
                temp = 2000 + (rb_ratio - 1.5) * 2000  # Warm light
            else:
                temp = 6500 - (1.5 - rb_ratio) * 2000  # Cool light
            
            return max(2000, min(10000, temp))  # Clamp to reasonable range
            
        except Exception:
            return 5500  # Default daylight temperature
    
    def _extract_dominant_colors(self, frame_bgr: np.ndarray, k: int = 5) -> Dict[str, Any]:
        """Extract dominant colors using K-means clustering."""
        try:
            # Reshape frame for clustering
            data = frame_bgr.reshape((-1, 3))
            data = np.float32(data)
            
            # Apply K-means
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Calculate color percentages
            unique, counts = np.unique(labels, return_counts=True)
            percentages = counts / len(labels)
            
            # Sort by percentage
            sorted_indices = np.argsort(percentages)[::-1]
            
            dominant_colors = []
            for i in sorted_indices:
                color = centers[i].astype(int)
                percentage = percentages[i]
                dominant_colors.append({
                    'color': color.tolist(),
                    'percentage': float(percentage)
                })
            
            return {
                'dominant_colors': dominant_colors,
                'color_diversity': len(unique),
                'primary_color_dominance': float(percentages[sorted_indices[0]])
            }
            
        except Exception:
            return {
                'dominant_colors': [],
                'color_diversity': 0,
                'primary_color_dominance': 0.0
            }
    
    def _analyze_color_distribution(self, frame_bgr: np.ndarray) -> Dict[str, float]:
        """Analyze overall color distribution characteristics."""
        try:
            # Convert to different color spaces
            frame_hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
            
            # Color variance
            color_variance = np.var(frame_bgr, axis=(0, 1))
            
            # Hue distribution
            hue_std = np.std(frame_hsv[:, :, 0])
            
            # Color uniformity (inverse of variance)
            color_uniformity = 1.0 / (1.0 + np.mean(color_variance))
            
            return {
                'color_variance_mean': float(np.mean(color_variance)),
                'hue_std': float(hue_std),
                'color_uniformity': float(color_uniformity)
            }
            
        except Exception:
            return {
                'color_variance_mean': 0.0,
                'hue_std': 0.0,
                'color_uniformity': 1.0
            }
    
    def _analyze_color_changes(self, hist_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze color changes compared to baseline and history."""
        if self.baseline_histograms is None:
            # First frame becomes baseline
            self.baseline_histograms = hist_metrics.copy()
            return {'significant_shift': False}
        
        # Calculate histogram correlations
        correlations = self._calculate_histogram_correlations(hist_metrics)
        
        # Calculate brightness changes
        brightness_change = self._calculate_brightness_change(hist_metrics)
        
        # Calculate color temperature change
        temp_change = self._calculate_temperature_change(hist_metrics)
        
        # Detect dominant color changes
        dominant_color_change = self._detect_dominant_color_change(hist_metrics)
        
        # Calculate overall lighting change score
        lighting_change_score = self._calculate_lighting_change_score(hist_metrics)
        
        # Determine if there's a significant shift
        significant_shift = (
            correlations['min_correlation'] < 0.8 or
            abs(brightness_change) > 15 or
            abs(temp_change) > 500 or
            dominant_color_change or
            lighting_change_score > 0.3
        )
        
        return {
            'significant_shift': significant_shift,
            'histogram_correlation': correlations['avg_correlation'],
            'min_correlation': correlations['min_correlation'],
            'brightness_change_percent': brightness_change,
            'temperature_change': temp_change,
            'dominant_color_change': dominant_color_change,
            'lighting_change_score': lighting_change_score
        }
    
    def _calculate_histogram_correlations(self, hist_metrics: Dict[str, Any]) -> Dict[str, float]:
        """Calculate correlations between current and baseline histograms."""
        correlations = []
        
        # Compare RGB histograms
        for channel in ['r', 'g', 'b']:
            current_hist = hist_metrics[f'{channel}_hist']
            baseline_hist = self.baseline_histograms[f'{channel}_hist']
            correlation = np.corrcoef(current_hist, baseline_hist)[0, 1]
            if not np.isnan(correlation):
                correlations.append(correlation)
        
        # Compare HSV histograms
        for channel in ['h', 's', 'v']:
            current_hist = hist_metrics[f'{channel}_hist']
            baseline_hist = self.baseline_histograms[f'{channel}_hist']
            correlation = np.corrcoef(current_hist, baseline_hist)[0, 1]
            if not np.isnan(correlation):
                correlations.append(correlation)
        
        if correlations:
            return {
                'avg_correlation': np.mean(correlations),
                'min_correlation': np.min(correlations)
            }
        else:
            return {'avg_correlation': 1.0, 'min_correlation': 1.0}
    
    def _calculate_brightness_change(self, hist_metrics: Dict[str, Any]) -> float:
        """Calculate percentage change in brightness."""
        current_brightness = hist_metrics['brightness_mean']
        baseline_brightness = self.baseline_histograms['brightness_mean']
        
        if baseline_brightness > 0:
            return ((current_brightness - baseline_brightness) / baseline_brightness) * 100
        return 0.0
    
    def _calculate_temperature_change(self, hist_metrics: Dict[str, Any]) -> float:
        """Calculate change in color temperature."""
        current_temp = hist_metrics['color_temperature']
        baseline_temp = self.baseline_histograms['color_temperature']
        
        return current_temp - baseline_temp
    
    def _detect_dominant_color_change(self, hist_metrics: Dict[str, Any]) -> bool:
        """Detect significant changes in dominant colors."""
        try:
            current_colors = hist_metrics['dominant_colors']
            baseline_colors = self.baseline_histograms['dominant_colors']
            
            if not current_colors or not baseline_colors:
                return False
            
            # Compare primary dominant colors
            current_primary = current_colors[0]['color']
            baseline_primary = baseline_colors[0]['color']
            
            # Calculate color distance
            color_distance = np.sqrt(np.sum((np.array(current_primary) - np.array(baseline_primary))**2))
            
            # Significant change if distance > threshold
            return color_distance > 50  # Threshold for significant color change
            
        except Exception:
            return False
    
    def _calculate_lighting_change_score(self, hist_metrics: Dict[str, Any]) -> float:
        """Calculate overall lighting change score."""
        try:
            # Combine multiple lighting indicators
            brightness_change = abs(self._calculate_brightness_change(hist_metrics)) / 100
            contrast_change = abs(hist_metrics['contrast_std'] - self.baseline_histograms['contrast_std']) / 50
            saturation_change = abs(hist_metrics['saturation_mean'] - self.baseline_histograms['saturation_mean']) / 100
            
            # Weighted combination
            lighting_score = (brightness_change * 0.4 + contrast_change * 0.3 + saturation_change * 0.3)
            
            return min(1.0, lighting_score)
            
        except Exception:
            return 0.0
    
    def _calculate_histogram_anomaly_score(self, hist_metrics: Dict[str, Any], color_analysis: Dict[str, Any]) -> float:
        """Calculate anomaly score based on histogram characteristics."""
        anomaly_score = 0.0
        
        # Low correlation indicates significant change
        if color_analysis.get('min_correlation', 1.0) < 0.7:
            anomaly_score += 2.0
        
        # Large brightness changes
        brightness_change = abs(color_analysis.get('brightness_change_percent', 0))
        if brightness_change > 20:
            anomaly_score += 1.5
        
        # Color temperature changes
        temp_change = abs(color_analysis.get('temperature_change', 0))
        if temp_change > 1000:
            anomaly_score += 1.0
        
        # Dominant color changes
        if color_analysis.get('dominant_color_change', False):
            anomaly_score += 1.0
        
        # High lighting change score
        lighting_score = color_analysis.get('lighting_change_score', 0)
        anomaly_score += lighting_score * 2.0
        
        return anomaly_score
    
    def _update_histogram_history(self, hist_metrics: Dict[str, Any], timestamp: float):
        """Update histogram history for temporal analysis."""
        self.histogram_history.append({
            'timestamp': timestamp,
            'metrics': hist_metrics
        })
        
        # Keep only recent history
        if len(self.histogram_history) > self.max_history:
            self.histogram_history.pop(0)

