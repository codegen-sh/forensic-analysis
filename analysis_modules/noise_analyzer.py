"""
Noise Pattern Analysis Module
============================

Detects encoding source changes and compression artifacts through noise pattern
analysis, frequency domain examination, and statistical texture analysis.
"""

import numpy as np
import cv2
from typing import Dict, Any, Optional
import logging
from scipy import ndimage, fft
from skimage import feature, filters

logger = logging.getLogger(__name__)

class NoiseAnalyzer:
    """Analyzes noise patterns to detect encoding source changes."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.baseline_noise = None
        self.noise_history = []
        self.max_history = 8
    
    def analyze_frame(self, frame: np.ndarray, timestamp: float) -> Optional[Dict[str, Any]]:
        """
        Analyze noise pattern characteristics of a frame.
        
        Args:
            frame: RGB frame data as numpy array
            timestamp: Frame timestamp in seconds
            
        Returns:
            Dictionary containing noise analysis results
        """
        try:
            # Convert to grayscale for noise analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            
            # Calculate comprehensive noise metrics
            noise_metrics = self._calculate_noise_metrics(gray, frame)
            
            # Detect noise pattern changes
            pattern_analysis = self._analyze_noise_patterns(noise_metrics)
            
            # Calculate anomaly score
            anomaly_score = self._calculate_noise_anomaly_score(noise_metrics, pattern_analysis)
            
            # Update history
            self._update_noise_history(noise_metrics, timestamp)
            
            result = {
                'confidence': min(1.0, anomaly_score / 2.0),
                'evidence_type': 'noise_pattern_change' if pattern_analysis['pattern_change'] else 'normal',
                'anomaly_score': anomaly_score,
                'details': {
                    'noise_variance': noise_metrics['noise_variance'],
                    'noise_entropy': noise_metrics['noise_entropy'],
                    'frequency_signature': noise_metrics['frequency_signature'],
                    'texture_energy': noise_metrics['texture_energy'],
                    'compression_artifacts': noise_metrics['compression_artifacts'],
                    'noise_pattern_change': pattern_analysis['pattern_change'],
                    'variance_change_percent': pattern_analysis.get('variance_change_percent', 0),
                    'frequency_correlation': pattern_analysis.get('frequency_correlation', 1.0),
                    'texture_consistency': pattern_analysis.get('texture_consistency', 1.0)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Noise analysis failed at {timestamp:.1f}s: {e}")
            return None
    
    def _calculate_noise_metrics(self, gray: np.ndarray, color_frame: np.ndarray) -> Dict[str, Any]:
        """Calculate comprehensive noise and texture metrics."""
        # 1. Basic noise estimation
        noise_variance = self._estimate_noise_variance(gray)
        
        # 2. Noise entropy
        noise_entropy = self._calculate_noise_entropy(gray)
        
        # 3. Frequency domain analysis
        frequency_metrics = self._analyze_frequency_domain(gray)
        
        # 4. Texture analysis
        texture_metrics = self._analyze_texture_patterns(gray)
        
        # 5. Compression artifact detection
        compression_artifacts = self._detect_compression_artifacts(gray)
        
        # 6. Color noise analysis
        color_noise_metrics = self._analyze_color_noise(color_frame)
        
        # 7. Local noise patterns
        local_noise_metrics = self._analyze_local_noise_patterns(gray)
        
        return {
            'noise_variance': noise_variance,
            'noise_entropy': noise_entropy,
            'frequency_signature': frequency_metrics['signature'],
            'high_freq_energy': frequency_metrics['high_freq_energy'],
            'texture_energy': texture_metrics['energy'],
            'texture_homogeneity': texture_metrics['homogeneity'],
            'compression_artifacts': compression_artifacts,
            **color_noise_metrics,
            **local_noise_metrics
        }
    
    def _estimate_noise_variance(self, gray: np.ndarray) -> float:
        """Estimate noise variance using Laplacian method."""
        try:
            # Apply Laplacian filter to estimate noise
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            
            # Estimate noise variance
            noise_variance = np.var(laplacian) / 6.0  # Normalize
            
            return float(noise_variance)
            
        except Exception:
            return 0.0
    
    def _calculate_noise_entropy(self, gray: np.ndarray) -> float:
        """Calculate entropy of noise patterns."""
        try:
            # Apply high-pass filter to isolate noise
            kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
            noise_image = cv2.filter2D(gray, cv2.CV_64F, kernel)
            
            # Calculate histogram of noise
            noise_hist, _ = np.histogram(noise_image.flatten(), bins=64, density=True)
            noise_hist = noise_hist + 1e-10  # Avoid log(0)
            
            # Calculate entropy
            entropy = -np.sum(noise_hist * np.log2(noise_hist))
            
            return float(entropy)
            
        except Exception:
            return 0.0
    
    def _analyze_frequency_domain(self, gray: np.ndarray) -> Dict[str, float]:
        """Analyze frequency domain characteristics."""
        try:
            # Apply FFT
            f_transform = fft.fft2(gray)
            f_shift = fft.fftshift(f_transform)
            magnitude_spectrum = np.abs(f_shift)
            
            # Calculate frequency signature
            h, w = magnitude_spectrum.shape
            center_h, center_w = h // 2, w // 2
            
            # High frequency energy (outer regions)
            mask = np.zeros((h, w), dtype=bool)
            y, x = np.ogrid[:h, :w]
            mask_inner = (x - center_w)**2 + (y - center_h)**2 <= (min(h, w) // 4)**2
            mask[~mask_inner] = True
            
            high_freq_energy = np.mean(magnitude_spectrum[mask])
            total_energy = np.mean(magnitude_spectrum)
            
            frequency_signature = high_freq_energy / (total_energy + 1e-10)
            
            return {
                'signature': float(frequency_signature),
                'high_freq_energy': float(high_freq_energy),
                'total_energy': float(total_energy)
            }
            
        except Exception:
            return {
                'signature': 0.0,
                'high_freq_energy': 0.0,
                'total_energy': 0.0
            }
    
    def _analyze_texture_patterns(self, gray: np.ndarray) -> Dict[str, float]:
        """Analyze texture patterns using GLCM and LBP."""
        try:
            # Gray Level Co-occurrence Matrix (GLCM) properties
            glcm_props = self._calculate_glcm_properties(gray)
            
            # Local Binary Patterns (LBP)
            lbp_props = self._calculate_lbp_properties(gray)
            
            return {
                'energy': glcm_props['energy'],
                'homogeneity': glcm_props['homogeneity'],
                'contrast': glcm_props['contrast'],
                'lbp_uniformity': lbp_props['uniformity'],
                'lbp_variance': lbp_props['variance']
            }
            
        except Exception:
            return {
                'energy': 0.0,
                'homogeneity': 0.0,
                'contrast': 0.0,
                'lbp_uniformity': 0.0,
                'lbp_variance': 0.0
            }
    
    def _calculate_glcm_properties(self, gray: np.ndarray) -> Dict[str, float]:
        """Calculate GLCM texture properties."""
        try:
            # Reduce image size for faster computation
            small_gray = cv2.resize(gray, (128, 128))
            
            # Calculate GLCM using skimage
            from skimage.feature import graycomatrix, graycoprops
            
            # Quantize to reduce computation
            quantized = (small_gray // 32).astype(np.uint8)
            
            # Calculate GLCM
            glcm = graycomatrix(quantized, [1], [0, np.pi/4, np.pi/2, 3*np.pi/4], 
                              levels=8, symmetric=True, normed=True)
            
            # Calculate properties
            energy = np.mean(graycoprops(glcm, 'energy'))
            homogeneity = np.mean(graycoprops(glcm, 'homogeneity'))
            contrast = np.mean(graycoprops(glcm, 'contrast'))
            
            return {
                'energy': float(energy),
                'homogeneity': float(homogeneity),
                'contrast': float(contrast)
            }
            
        except Exception:
            return {'energy': 0.0, 'homogeneity': 0.0, 'contrast': 0.0}
    
    def _calculate_lbp_properties(self, gray: np.ndarray) -> Dict[str, float]:
        """Calculate Local Binary Pattern properties."""
        try:
            # Reduce image size for faster computation
            small_gray = cv2.resize(gray, (128, 128))
            
            # Calculate LBP
            from skimage.feature import local_binary_pattern
            
            radius = 3
            n_points = 8 * radius
            lbp = local_binary_pattern(small_gray, n_points, radius, method='uniform')
            
            # Calculate LBP histogram
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=n_points + 2, 
                                     range=(0, n_points + 2), density=True)
            
            # Calculate uniformity and variance
            uniformity = np.sum(lbp_hist**2)
            variance = np.var(lbp_hist)
            
            return {
                'uniformity': float(uniformity),
                'variance': float(variance)
            }
            
        except Exception:
            return {'uniformity': 0.0, 'variance': 0.0}
    
    def _detect_compression_artifacts(self, gray: np.ndarray) -> float:
        """Detect compression artifacts like blocking and ringing."""
        try:
            # Detect blocking artifacts (8x8 DCT blocks)
            blocking_score = self._detect_blocking_artifacts(gray)
            
            # Detect ringing artifacts
            ringing_score = self._detect_ringing_artifacts(gray)
            
            # Combine scores
            artifact_score = (blocking_score + ringing_score) / 2.0
            
            return float(artifact_score)
            
        except Exception:
            return 0.0
    
    def _detect_blocking_artifacts(self, gray: np.ndarray) -> float:
        """Detect DCT blocking artifacts."""
        try:
            h, w = gray.shape
            
            # Calculate horizontal and vertical differences at block boundaries
            horizontal_diffs = []
            vertical_diffs = []
            
            # Check 8-pixel boundaries (typical DCT block size)
            for i in range(8, h, 8):
                if i < h - 1:
                    diff = np.mean(np.abs(gray[i, :] - gray[i-1, :]))
                    horizontal_diffs.append(diff)
            
            for j in range(8, w, 8):
                if j < w - 1:
                    diff = np.mean(np.abs(gray[:, j] - gray[:, j-1]))
                    vertical_diffs.append(diff)
            
            # Calculate blocking score
            if horizontal_diffs and vertical_diffs:
                avg_block_diff = (np.mean(horizontal_diffs) + np.mean(vertical_diffs)) / 2.0
                
                # Compare with overall image variation
                overall_variation = np.std(gray)
                blocking_score = avg_block_diff / (overall_variation + 1e-10)
                
                return min(1.0, blocking_score)
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _detect_ringing_artifacts(self, gray: np.ndarray) -> float:
        """Detect ringing artifacts around edges."""
        try:
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Dilate edges to create a mask
            kernel = np.ones((5, 5), np.uint8)
            edge_mask = cv2.dilate(edges, kernel, iterations=1)
            
            # Calculate gradient magnitude
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Calculate ringing score in edge regions
            if np.sum(edge_mask) > 0:
                edge_gradient = gradient_magnitude[edge_mask > 0]
                ringing_score = np.std(edge_gradient) / (np.mean(edge_gradient) + 1e-10)
                return min(1.0, ringing_score / 10.0)  # Normalize
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _analyze_color_noise(self, color_frame: np.ndarray) -> Dict[str, float]:
        """Analyze noise patterns in color channels."""
        try:
            # Calculate noise in each color channel
            channel_noise = []
            
            for i in range(3):  # RGB channels
                channel = color_frame[:, :, i]
                noise_var = self._estimate_noise_variance(channel)
                channel_noise.append(noise_var)
            
            # Calculate color noise metrics
            color_noise_variance = np.var(channel_noise)
            color_noise_mean = np.mean(channel_noise)
            
            return {
                'color_noise_variance': float(color_noise_variance),
                'color_noise_mean': float(color_noise_mean),
                'r_noise': float(channel_noise[0]),
                'g_noise': float(channel_noise[1]),
                'b_noise': float(channel_noise[2])
            }
            
        except Exception:
            return {
                'color_noise_variance': 0.0,
                'color_noise_mean': 0.0,
                'r_noise': 0.0,
                'g_noise': 0.0,
                'b_noise': 0.0
            }
    
    def _analyze_local_noise_patterns(self, gray: np.ndarray) -> Dict[str, float]:
        """Analyze local noise patterns across the image."""
        try:
            # Divide image into blocks
            h, w = gray.shape
            block_size = 32
            local_variances = []
            
            for i in range(0, h - block_size, block_size):
                for j in range(0, w - block_size, block_size):
                    block = gray[i:i+block_size, j:j+block_size]
                    block_noise = self._estimate_noise_variance(block)
                    local_variances.append(block_noise)
            
            if local_variances:
                local_noise_uniformity = 1.0 / (1.0 + np.std(local_variances))
                local_noise_mean = np.mean(local_variances)
                
                return {
                    'local_noise_uniformity': float(local_noise_uniformity),
                    'local_noise_mean': float(local_noise_mean)
                }
            
            return {'local_noise_uniformity': 1.0, 'local_noise_mean': 0.0}
            
        except Exception:
            return {'local_noise_uniformity': 1.0, 'local_noise_mean': 0.0}
    
    def _analyze_noise_patterns(self, noise_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze noise pattern changes compared to baseline."""
        if self.baseline_noise is None:
            # First frame becomes baseline
            self.baseline_noise = noise_metrics.copy()
            return {'pattern_change': False}
        
        # Calculate changes in key noise metrics
        variance_change = self._calculate_variance_change(noise_metrics)
        frequency_correlation = self._calculate_frequency_correlation(noise_metrics)
        texture_consistency = self._calculate_texture_consistency(noise_metrics)
        
        # Detect significant pattern changes
        pattern_change = (
            abs(variance_change) > 30 or  # 30% change in noise variance
            frequency_correlation < 0.8 or  # Low frequency correlation
            texture_consistency < 0.7  # Low texture consistency
        )
        
        return {
            'pattern_change': pattern_change,
            'variance_change_percent': variance_change,
            'frequency_correlation': frequency_correlation,
            'texture_consistency': texture_consistency
        }
    
    def _calculate_variance_change(self, noise_metrics: Dict[str, Any]) -> float:
        """Calculate percentage change in noise variance."""
        current_variance = noise_metrics['noise_variance']
        baseline_variance = self.baseline_noise['noise_variance']
        
        if baseline_variance > 0:
            return ((current_variance - baseline_variance) / baseline_variance) * 100
        return 0.0
    
    def _calculate_frequency_correlation(self, noise_metrics: Dict[str, Any]) -> float:
        """Calculate correlation between frequency signatures."""
        current_sig = noise_metrics['frequency_signature']
        baseline_sig = self.baseline_noise['frequency_signature']
        
        # Simple correlation for scalar values
        if baseline_sig > 0:
            return min(current_sig, baseline_sig) / max(current_sig, baseline_sig)
        return 1.0
    
    def _calculate_texture_consistency(self, noise_metrics: Dict[str, Any]) -> float:
        """Calculate texture consistency score."""
        # Compare texture energy and homogeneity
        current_energy = noise_metrics['texture_energy']
        baseline_energy = self.baseline_noise['texture_energy']
        
        current_homogeneity = noise_metrics['texture_homogeneity']
        baseline_homogeneity = self.baseline_noise['texture_homogeneity']
        
        # Calculate consistency scores
        energy_consistency = 1.0
        homogeneity_consistency = 1.0
        
        if baseline_energy > 0:
            energy_diff = abs(current_energy - baseline_energy) / baseline_energy
            energy_consistency = max(0.0, 1.0 - energy_diff)
        
        if baseline_homogeneity > 0:
            homogeneity_diff = abs(current_homogeneity - baseline_homogeneity) / baseline_homogeneity
            homogeneity_consistency = max(0.0, 1.0 - homogeneity_diff)
        
        return (energy_consistency + homogeneity_consistency) / 2.0
    
    def _calculate_noise_anomaly_score(self, noise_metrics: Dict[str, Any], pattern_analysis: Dict[str, Any]) -> float:
        """Calculate anomaly score based on noise characteristics."""
        anomaly_score = 0.0
        
        # Large variance changes
        variance_change = abs(pattern_analysis.get('variance_change_percent', 0))
        if variance_change > 50:
            anomaly_score += 2.0
        elif variance_change > 25:
            anomaly_score += 1.0
        
        # Low frequency correlation
        freq_correlation = pattern_analysis.get('frequency_correlation', 1.0)
        if freq_correlation < 0.6:
            anomaly_score += 1.5
        elif freq_correlation < 0.8:
            anomaly_score += 0.5
        
        # Low texture consistency
        texture_consistency = pattern_analysis.get('texture_consistency', 1.0)
        if texture_consistency < 0.5:
            anomaly_score += 1.5
        elif texture_consistency < 0.7:
            anomaly_score += 0.5
        
        # High compression artifacts
        compression_artifacts = noise_metrics.get('compression_artifacts', 0)
        if compression_artifacts > 0.5:
            anomaly_score += 1.0
        
        return anomaly_score
    
    def _update_noise_history(self, noise_metrics: Dict[str, Any], timestamp: float):
        """Update noise history for temporal analysis."""
        self.noise_history.append({
            'timestamp': timestamp,
            'metrics': noise_metrics
        })
        
        # Keep only recent history
        if len(self.noise_history) > self.max_history:
            self.noise_history.pop(0)

