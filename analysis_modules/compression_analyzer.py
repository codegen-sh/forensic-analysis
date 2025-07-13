"""
Compression Analysis Module
==========================

Advanced compression analysis for detecting video splice points through
file size discontinuities, quality metrics, and encoding parameter changes.
"""

import os
import tempfile
import subprocess
import numpy as np
import cv2
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CompressionAnalyzer:
    """Analyzes compression artifacts and discontinuities in video frames."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.baseline_metrics = None
        self.frame_history = []
        self.max_history = 10
    
    def analyze_frame(self, frame: np.ndarray, timestamp: float) -> Optional[Dict[str, Any]]:
        """
        Analyze compression characteristics of a single frame.
        
        Args:
            frame: RGB frame data as numpy array
            timestamp: Frame timestamp in seconds
            
        Returns:
            Dictionary containing compression analysis results
        """
        try:
            # Calculate multiple compression metrics
            metrics = self._calculate_compression_metrics(frame)
            
            # Detect anomalies compared to baseline
            anomaly_score = self._calculate_anomaly_score(metrics)
            
            # Update frame history
            self._update_frame_history(metrics, timestamp)
            
            # Detect discontinuities
            discontinuity_info = self._detect_discontinuities()
            
            result = {
                'confidence': min(1.0, anomaly_score / 2.0),  # Normalize to 0-1
                'evidence_type': 'compression_discontinuity' if anomaly_score > 1.0 else 'normal',
                'anomaly_score': anomaly_score,
                'details': {
                    'file_size': metrics['file_size'],
                    'quality_score': metrics['quality_score'],
                    'compression_ratio': metrics['compression_ratio'],
                    'entropy': metrics['entropy'],
                    'edge_density': metrics['edge_density'],
                    'size_change_percent': discontinuity_info.get('size_change_percent', 0),
                    'quality_change_percent': discontinuity_info.get('quality_change_percent', 0),
                    'discontinuity_detected': discontinuity_info.get('discontinuity_detected', False)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Compression analysis failed at {timestamp:.1f}s: {e}")
            return None
    
    def _calculate_compression_metrics(self, frame: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive compression metrics for a frame."""
        # Convert to BGR for OpenCV
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # 1. File size metric (compress frame as JPEG)
        file_size = self._get_compressed_size(frame_bgr)
        
        # 2. Quality score using BRISQUE (if available) or simple metrics
        quality_score = self._calculate_quality_score(frame_bgr)
        
        # 3. Compression ratio estimate
        raw_size = frame.shape[0] * frame.shape[1] * frame.shape[2]
        compression_ratio = raw_size / file_size if file_size > 0 else 0
        
        # 4. Image entropy (information content)
        entropy = self._calculate_entropy(frame_bgr)
        
        # 5. Edge density (detail level)
        edge_density = self._calculate_edge_density(frame_bgr)
        
        # 6. DCT coefficient analysis
        dct_metrics = self._analyze_dct_coefficients(frame_bgr)
        
        return {
            'file_size': file_size,
            'quality_score': quality_score,
            'compression_ratio': compression_ratio,
            'entropy': entropy,
            'edge_density': edge_density,
            **dct_metrics
        }
    
    def _get_compressed_size(self, frame_bgr: np.ndarray, quality: int = 95) -> int:
        """Get the compressed file size of a frame as JPEG."""
        try:
            # Encode frame as JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            _, encoded_img = cv2.imencode('.jpg', frame_bgr, encode_param)
            return len(encoded_img.tobytes())
        except Exception:
            return 0
    
    def _calculate_quality_score(self, frame_bgr: np.ndarray) -> float:
        """Calculate image quality score using multiple metrics."""
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            
            # 1. Laplacian variance (sharpness)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # 2. Sobel gradient magnitude
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            sobel_magnitude = np.sqrt(sobelx**2 + sobely**2).mean()
            
            # 3. Standard deviation (contrast)
            std_dev = np.std(gray)
            
            # Combine metrics into quality score
            quality_score = (laplacian_var * 0.4 + sobel_magnitude * 0.4 + std_dev * 0.2) / 100
            
            return min(100.0, quality_score)
            
        except Exception:
            return 0.0
    
    def _calculate_entropy(self, frame_bgr: np.ndarray) -> float:
        """Calculate image entropy (information content)."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            
            # Calculate histogram
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = hist.flatten()
            
            # Normalize histogram
            hist = hist / hist.sum()
            
            # Calculate entropy
            entropy = -np.sum(hist * np.log2(hist + 1e-10))
            
            return entropy
            
        except Exception:
            return 0.0
    
    def _calculate_edge_density(self, frame_bgr: np.ndarray) -> float:
        """Calculate edge density using Canny edge detection."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            
            # Apply Canny edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Calculate edge density
            edge_pixels = np.sum(edges > 0)
            total_pixels = edges.shape[0] * edges.shape[1]
            edge_density = edge_pixels / total_pixels
            
            return edge_density * 100  # Convert to percentage
            
        except Exception:
            return 0.0
    
    def _analyze_dct_coefficients(self, frame_bgr: np.ndarray) -> Dict[str, float]:
        """Analyze DCT coefficients for compression artifacts."""
        try:
            # Convert to grayscale and float
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
            
            # Divide into 8x8 blocks and analyze DCT
            h, w = gray.shape
            block_size = 8
            
            dc_coeffs = []
            ac_energy = []
            
            for i in range(0, h - block_size + 1, block_size):
                for j in range(0, w - block_size + 1, block_size):
                    block = gray[i:i+block_size, j:j+block_size]
                    
                    # Apply DCT
                    dct_block = cv2.dct(block)
                    
                    # Extract DC coefficient
                    dc_coeffs.append(dct_block[0, 0])
                    
                    # Calculate AC energy
                    ac_block = dct_block.copy()
                    ac_block[0, 0] = 0  # Remove DC component
                    ac_energy.append(np.sum(ac_block**2))
            
            return {
                'dc_variance': np.var(dc_coeffs),
                'ac_energy_mean': np.mean(ac_energy),
                'ac_energy_std': np.std(ac_energy)
            }
            
        except Exception:
            return {
                'dc_variance': 0.0,
                'ac_energy_mean': 0.0,
                'ac_energy_std': 0.0
            }
    
    def _calculate_anomaly_score(self, metrics: Dict[str, float]) -> float:
        """Calculate anomaly score based on deviation from baseline."""
        if self.baseline_metrics is None:
            # First frame becomes baseline
            self.baseline_metrics = metrics.copy()
            return 0.0
        
        # Calculate normalized deviations
        deviations = []
        
        for key, value in metrics.items():
            if key in self.baseline_metrics:
                baseline_value = self.baseline_metrics[key]
                if baseline_value > 0:
                    deviation = abs(value - baseline_value) / baseline_value
                    deviations.append(deviation)
        
        # Return weighted average of deviations
        if deviations:
            return np.mean(deviations) * 10  # Scale for visibility
        
        return 0.0
    
    def _update_frame_history(self, metrics: Dict[str, float], timestamp: float):
        """Update frame history for discontinuity detection."""
        self.frame_history.append({
            'timestamp': timestamp,
            'metrics': metrics
        })
        
        # Keep only recent frames
        if len(self.frame_history) > self.max_history:
            self.frame_history.pop(0)
    
    def _detect_discontinuities(self) -> Dict[str, Any]:
        """Detect compression discontinuities in recent frame history."""
        if len(self.frame_history) < 2:
            return {}
        
        # Compare current frame with previous
        current = self.frame_history[-1]['metrics']
        previous = self.frame_history[-2]['metrics']
        
        # Calculate percentage changes
        size_change = 0
        quality_change = 0
        
        if previous['file_size'] > 0:
            size_change = ((current['file_size'] - previous['file_size']) / 
                          previous['file_size']) * 100
        
        if previous['quality_score'] > 0:
            quality_change = ((current['quality_score'] - previous['quality_score']) / 
                             previous['quality_score']) * 100
        
        # Detect significant discontinuities
        discontinuity_detected = (abs(size_change) > 5.0 or abs(quality_change) > 10.0)
        
        return {
            'size_change_percent': size_change,
            'quality_change_percent': quality_change,
            'discontinuity_detected': discontinuity_detected
        }

