"""
Optical Flow Analysis Module
===========================

Detects motion discontinuities and temporal inconsistencies that may indicate
video splicing through optical flow analysis and motion vector examination.
"""

import numpy as np
import cv2
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class OpticalFlowAnalyzer:
    """Analyzes optical flow patterns to detect temporal discontinuities."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.previous_frame = None
        self.flow_history = []
        self.max_history = 5
        
        # Lucas-Kanade parameters
        self.lk_params = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        )
        
        # Feature detection parameters
        self.feature_params = dict(
            maxCorners=100,
            qualityLevel=0.3,
            minDistance=7,
            blockSize=7
        )
    
    def analyze_frame(self, frame: np.ndarray, timestamp: float) -> Optional[Dict[str, Any]]:
        """
        Analyze optical flow characteristics of a frame.
        
        Args:
            frame: RGB frame data as numpy array
            timestamp: Frame timestamp in seconds
            
        Returns:
            Dictionary containing optical flow analysis results
        """
        try:
            # Convert to grayscale for optical flow
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            
            if self.previous_frame is None:
                self.previous_frame = gray
                return self._create_baseline_result()
            
            # Calculate optical flow
            flow_metrics = self._calculate_optical_flow(self.previous_frame, gray)
            
            # Detect motion discontinuities
            discontinuity_info = self._detect_motion_discontinuities(flow_metrics)
            
            # Calculate anomaly score
            anomaly_score = self._calculate_flow_anomaly_score(flow_metrics)
            
            # Update history
            self._update_flow_history(flow_metrics, timestamp)
            
            # Update previous frame
            self.previous_frame = gray
            
            result = {
                'confidence': min(1.0, anomaly_score / 3.0),
                'evidence_type': 'motion_discontinuity' if discontinuity_info['flow_discontinuity'] else 'normal',
                'anomaly_score': anomaly_score,
                'details': {
                    'flow_magnitude_mean': flow_metrics['magnitude_mean'],
                    'flow_magnitude_std': flow_metrics['magnitude_std'],
                    'flow_direction_consistency': flow_metrics['direction_consistency'],
                    'motion_vector_count': flow_metrics['vector_count'],
                    'flow_discontinuity': discontinuity_info['flow_discontinuity'],
                    'magnitude_change_percent': discontinuity_info.get('magnitude_change_percent', 0),
                    'direction_change_score': discontinuity_info.get('direction_change_score', 0)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Optical flow analysis failed at {timestamp:.1f}s: {e}")
            return None
    
    def _create_baseline_result(self) -> Dict[str, Any]:
        """Create baseline result for first frame."""
        return {
            'confidence': 0.0,
            'evidence_type': 'baseline',
            'anomaly_score': 0.0,
            'details': {
                'flow_magnitude_mean': 0.0,
                'flow_magnitude_std': 0.0,
                'flow_direction_consistency': 1.0,
                'motion_vector_count': 0,
                'flow_discontinuity': False,
                'magnitude_change_percent': 0.0,
                'direction_change_score': 0.0
            }
        }
    
    def _calculate_optical_flow(self, prev_gray: np.ndarray, curr_gray: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive optical flow metrics."""
        # Method 1: Dense optical flow (Farneback)
        dense_flow = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, None, None, **self.lk_params)
        
        # Method 2: Sparse optical flow (Lucas-Kanade)
        sparse_metrics = self._calculate_sparse_flow(prev_gray, curr_gray)
        
        # Method 3: Dense flow analysis
        dense_metrics = self._calculate_dense_flow(prev_gray, curr_gray)
        
        # Combine metrics
        combined_metrics = {
            **sparse_metrics,
            **dense_metrics,
            'flow_method': 'combined'
        }
        
        return combined_metrics
    
    def _calculate_sparse_flow(self, prev_gray: np.ndarray, curr_gray: np.ndarray) -> Dict[str, float]:
        """Calculate sparse optical flow using Lucas-Kanade method."""
        try:
            # Detect features in previous frame
            p0 = cv2.goodFeaturesToTrack(prev_gray, mask=None, **self.feature_params)
            
            if p0 is None or len(p0) == 0:
                return self._get_empty_flow_metrics()
            
            # Calculate optical flow
            p1, status, error = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, p0, None, **self.lk_params)
            
            # Select good points
            good_new = p1[status == 1]
            good_old = p0[status == 1]
            
            if len(good_new) == 0:
                return self._get_empty_flow_metrics()
            
            # Calculate flow vectors
            flow_vectors = good_new - good_old
            
            # Calculate metrics
            magnitudes = np.sqrt(flow_vectors[:, 0]**2 + flow_vectors[:, 1]**2)
            angles = np.arctan2(flow_vectors[:, 1], flow_vectors[:, 0])
            
            # Direction consistency (circular variance)
            direction_consistency = self._calculate_direction_consistency(angles)
            
            return {
                'magnitude_mean': np.mean(magnitudes),
                'magnitude_std': np.std(magnitudes),
                'magnitude_max': np.max(magnitudes),
                'direction_consistency': direction_consistency,
                'vector_count': len(flow_vectors),
                'tracking_success_rate': len(good_new) / len(p0)
            }
            
        except Exception as e:
            logger.error(f"Sparse flow calculation failed: {e}")
            return self._get_empty_flow_metrics()
    
    def _calculate_dense_flow(self, prev_gray: np.ndarray, curr_gray: np.ndarray) -> Dict[str, float]:
        """Calculate dense optical flow using Farneback method."""
        try:
            # Calculate dense optical flow
            flow = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, 0.5, 3, 15, 3, 5, 1.2, 0)
            
            # Calculate magnitude and angle
            magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            
            # Calculate metrics
            magnitude_flat = magnitude.flatten()
            angle_flat = angle.flatten()
            
            # Filter out very small movements (noise)
            significant_motion = magnitude_flat > 0.5
            if np.sum(significant_motion) == 0:
                return self._get_empty_dense_metrics()
            
            sig_magnitudes = magnitude_flat[significant_motion]
            sig_angles = angle_flat[significant_motion]
            
            # Direction consistency for dense flow
            direction_consistency = self._calculate_direction_consistency(sig_angles)
            
            return {
                'dense_magnitude_mean': np.mean(sig_magnitudes),
                'dense_magnitude_std': np.std(sig_magnitudes),
                'dense_direction_consistency': direction_consistency,
                'motion_coverage': np.sum(significant_motion) / len(magnitude_flat),
                'flow_uniformity': 1.0 - (np.std(sig_magnitudes) / (np.mean(sig_magnitudes) + 1e-6))
            }
            
        except Exception as e:
            logger.error(f"Dense flow calculation failed: {e}")
            return self._get_empty_dense_metrics()
    
    def _calculate_direction_consistency(self, angles: np.ndarray) -> float:
        """Calculate direction consistency using circular statistics."""
        if len(angles) == 0:
            return 1.0
        
        # Convert to unit vectors
        x_components = np.cos(angles)
        y_components = np.sin(angles)
        
        # Calculate mean direction
        mean_x = np.mean(x_components)
        mean_y = np.mean(y_components)
        
        # Calculate resultant vector length (consistency measure)
        resultant_length = np.sqrt(mean_x**2 + mean_y**2)
        
        return resultant_length
    
    def _get_empty_flow_metrics(self) -> Dict[str, float]:
        """Return empty metrics for sparse flow."""
        return {
            'magnitude_mean': 0.0,
            'magnitude_std': 0.0,
            'magnitude_max': 0.0,
            'direction_consistency': 1.0,
            'vector_count': 0,
            'tracking_success_rate': 0.0
        }
    
    def _get_empty_dense_metrics(self) -> Dict[str, float]:
        """Return empty metrics for dense flow."""
        return {
            'dense_magnitude_mean': 0.0,
            'dense_magnitude_std': 0.0,
            'dense_direction_consistency': 1.0,
            'motion_coverage': 0.0,
            'flow_uniformity': 1.0
        }
    
    def _detect_motion_discontinuities(self, flow_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Detect motion discontinuities in flow patterns."""
        if len(self.flow_history) == 0:
            return {'flow_discontinuity': False}
        
        # Compare with previous flow
        prev_metrics = self.flow_history[-1]['metrics']
        
        # Calculate changes
        magnitude_change = 0
        direction_change = 0
        
        if prev_metrics['magnitude_mean'] > 0:
            magnitude_change = abs(flow_metrics['magnitude_mean'] - prev_metrics['magnitude_mean']) / prev_metrics['magnitude_mean']
        
        direction_change = abs(flow_metrics['direction_consistency'] - prev_metrics['direction_consistency'])
        
        # Detect discontinuities
        magnitude_discontinuity = magnitude_change > 0.5  # 50% change
        direction_discontinuity = direction_change > 0.3   # 30% change in consistency
        
        flow_discontinuity = magnitude_discontinuity or direction_discontinuity
        
        return {
            'flow_discontinuity': flow_discontinuity,
            'magnitude_change_percent': magnitude_change * 100,
            'direction_change_score': direction_change,
            'magnitude_discontinuity': magnitude_discontinuity,
            'direction_discontinuity': direction_discontinuity
        }
    
    def _calculate_flow_anomaly_score(self, flow_metrics: Dict[str, float]) -> float:
        """Calculate anomaly score based on flow characteristics."""
        anomaly_score = 0.0
        
        # High magnitude changes indicate potential splicing
        if flow_metrics['magnitude_mean'] > 10.0:
            anomaly_score += 1.0
        
        # Low direction consistency indicates chaotic motion
        if flow_metrics['direction_consistency'] < 0.5:
            anomaly_score += 1.0
        
        # Very low or very high vector counts are suspicious
        vector_count = flow_metrics['vector_count']
        if vector_count < 10 or vector_count > 200:
            anomaly_score += 0.5
        
        # Low tracking success rate indicates frame inconsistency
        if flow_metrics.get('tracking_success_rate', 1.0) < 0.5:
            anomaly_score += 1.0
        
        return anomaly_score
    
    def _update_flow_history(self, flow_metrics: Dict[str, float], timestamp: float):
        """Update flow history for temporal analysis."""
        self.flow_history.append({
            'timestamp': timestamp,
            'metrics': flow_metrics
        })
        
        # Keep only recent history
        if len(self.flow_history) > self.max_history:
            self.flow_history.pop(0)

