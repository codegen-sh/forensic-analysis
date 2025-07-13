#!/usr/bin/env python3
"""
Corrected Statistical Analysis for Video Forensics
=================================================

This module provides statistically sound methods for analyzing compression ratio
discontinuities in video forensics, replacing the inappropriate "4.2σ" claims
with proper statistical frameworks.

Author: Statistical Methodology Review
Version: 1.0
Date: January 2025
"""

import numpy as np
import scipy.stats as stats
from scipy import signal
from typing import Dict, List, Tuple, Optional
import warnings
from dataclasses import dataclass

@dataclass
class StatisticalResult:
    """Container for statistical analysis results."""
    test_type: str
    statistic: float
    p_value: float
    effect_size: float
    effect_size_interpretation: str
    confidence_interval: Tuple[float, float]
    is_significant: bool
    baseline_properties: Dict
    assumptions_met: Dict[str, bool]
    limitations: List[str]

class VideoForensicsStatistics:
    """
    Statistically sound methods for video forensics analysis.
    
    This class implements proper statistical frameworks for detecting
    compression ratio discontinuities without inappropriate sigma claims.
    """
    
    def __init__(self, significance_level: float = 0.05):
        """
        Initialize the statistical analysis framework.
        
        Args:
            significance_level: Alpha level for hypothesis testing (default: 0.05)
        """
        self.significance_level = significance_level
        self.baseline_frames = 1000  # Number of frames to use for baseline
        
    def establish_baseline(self, compression_ratios: np.ndarray) -> Dict:
        """
        Establish statistical baseline for compression ratios.
        
        Args:
            compression_ratios: Array of compression ratios
            
        Returns:
            Dictionary containing baseline statistics and properties
        """
        if len(compression_ratios) < self.baseline_frames:
            raise ValueError(f"Need at least {self.baseline_frames} frames for baseline")
            
        baseline_data = compression_ratios[:self.baseline_frames]
        
        # Test for normality
        shapiro_stat, shapiro_p = stats.shapiro(baseline_data)
        anderson_stat, anderson_critical, anderson_significance = stats.anderson(baseline_data, dist='norm')
        
        # Calculate descriptive statistics
        mean = np.mean(baseline_data)
        std = np.std(baseline_data, ddof=1)  # Sample standard deviation
        median = np.median(baseline_data)
        mad = stats.median_abs_deviation(baseline_data)
        
        # Calculate percentiles
        q25, q75 = np.percentile(baseline_data, [25, 75])
        iqr = q75 - q25
        
        # Test for autocorrelation
        autocorr_lag1 = np.corrcoef(baseline_data[:-1], baseline_data[1:])[0, 1]
        
        # Ljung-Box test for autocorrelation
        ljung_box_stat, ljung_box_p = self._ljung_box_test(baseline_data, lags=10)
        
        return {
            'n_samples': len(baseline_data),
            'mean': mean,
            'std': std,
            'median': median,
            'mad': mad,
            'q25': q25,
            'q75': q75,
            'iqr': iqr,
            'min': np.min(baseline_data),
            'max': np.max(baseline_data),
            'skewness': stats.skew(baseline_data),
            'kurtosis': stats.kurtosis(baseline_data),
            'shapiro_stat': shapiro_stat,
            'shapiro_p': shapiro_p,
            'is_normal': shapiro_p > self.significance_level,
            'anderson_stat': anderson_stat,
            'anderson_critical_5pct': anderson_critical[2],  # 5% critical value
            'autocorr_lag1': autocorr_lag1,
            'ljung_box_stat': ljung_box_stat,
            'ljung_box_p': ljung_box_p,
            'has_autocorrelation': ljung_box_p < self.significance_level
        }
    
    def _ljung_box_test(self, data: np.ndarray, lags: int = 10) -> Tuple[float, float]:
        """
        Ljung-Box test for autocorrelation.
        
        Args:
            data: Time series data
            lags: Number of lags to test
            
        Returns:
            Test statistic and p-value
        """
        n = len(data)
        autocorrs = []
        
        for lag in range(1, lags + 1):
            if lag < n:
                autocorr = np.corrcoef(data[:-lag], data[lag:])[0, 1]
                autocorrs.append(autocorr)
            else:
                autocorrs.append(0)
        
        autocorrs = np.array(autocorrs)
        
        # Ljung-Box statistic
        lb_stat = n * (n + 2) * np.sum([(autocorrs[i]**2) / (n - i - 1) for i in range(len(autocorrs))])
        
        # Chi-square test
        p_value = 1 - stats.chi2.cdf(lb_stat, df=lags)
        
        return lb_stat, p_value
    
    def detect_change_points_cusum(self, data: np.ndarray, threshold: float = 5.0) -> Tuple[List[int], np.ndarray, np.ndarray]:
        """
        Detect change points using CUSUM (Cumulative Sum) method.
        
        Args:
            data: Time series data
            threshold: Detection threshold
            
        Returns:
            Tuple of (change_points, cusum_positive, cusum_negative)
        """
        n = len(data)
        baseline_stats = self.establish_baseline(data)
        
        # Standardize data using baseline statistics
        if baseline_stats['is_normal']:
            standardized = (data - baseline_stats['mean']) / baseline_stats['std']
        else:
            # Use robust standardization for non-normal data
            standardized = (data - baseline_stats['median']) / baseline_stats['mad']
        
        # CUSUM calculation
        cusum_pos = np.zeros(n)
        cusum_neg = np.zeros(n)
        
        for i in range(1, n):
            cusum_pos[i] = max(0, cusum_pos[i-1] + standardized[i] - 0.5)
            cusum_neg[i] = min(0, cusum_neg[i-1] + standardized[i] + 0.5)
        
        # Detect change points
        change_points = []
        for i in range(self.baseline_frames, n):  # Start after baseline period
            if abs(cusum_pos[i]) > threshold or abs(cusum_neg[i]) > threshold:
                change_points.append(i)
        
        return change_points, cusum_pos, cusum_neg
    
    def bayesian_change_point_detection(self, data: np.ndarray, prior_prob: float = 1/250) -> Tuple[List[int], np.ndarray]:
        """
        Bayesian online change point detection.
        
        Args:
            data: Time series data
            prior_prob: Prior probability of change point
            
        Returns:
            Tuple of (change_points, change_probabilities)
        """
        n = len(data)
        R = np.zeros((n + 1, n + 1))
        R[0, 0] = 1
        
        change_points = []
        change_probabilities = np.zeros(n)
        
        baseline_stats = self.establish_baseline(data)
        
        for t in range(1, min(n + 1, self.baseline_frames + 1000)):  # Limit computation
            # Predictive probabilities
            pred_probs = np.zeros(t + 1)
            
            for r in range(t):
                if R[r, t-1] > 1e-10:  # Avoid numerical issues
                    run_length = t - r
                    if run_length > 1:
                        data_subset = data[r:t]
                        if len(data_subset) > 1:
                            subset_mean = np.mean(data_subset)
                            subset_std = np.std(data_subset, ddof=1)
                            if subset_std > 0:
                                pred_probs[r] = stats.norm.pdf(data[t-1], subset_mean, subset_std)
            
            # Update run length distribution
            if np.sum(pred_probs) > 0:
                R[1:t+1, t] = R[0:t, t-1] * pred_probs[0:t] * (1 - prior_prob)
                R[0, t] = np.sum(R[0:t, t-1] * pred_probs[0:t] * prior_prob)
                
                # Normalize
                total = np.sum(R[:, t])
                if total > 0:
                    R[:, t] = R[:, t] / total
                
                # Store change probability
                if t <= n:
                    change_probabilities[t-1] = R[0, t]
                
                # Check for change point
                if R[0, t] > 0.5 and t > self.baseline_frames:
                    change_points.append(t-1)
        
        return change_points, change_probabilities
    
    def test_compression_anomaly(self, compression_ratios: np.ndarray, anomaly_frame: int) -> StatisticalResult:
        """
        Perform proper statistical significance testing for compression anomaly.
        
        Args:
            compression_ratios: Array of compression ratios
            anomaly_frame: Frame index of suspected anomaly
            
        Returns:
            StatisticalResult object with complete analysis
        """
        if anomaly_frame >= len(compression_ratios):
            raise ValueError("Anomaly frame index out of bounds")
        
        # Establish baseline
        baseline_stats = self.establish_baseline(compression_ratios)
        baseline_data = compression_ratios[:self.baseline_frames]
        anomaly_value = compression_ratios[anomaly_frame]
        
        # Check assumptions
        assumptions_met = {
            'normality': baseline_stats['is_normal'],
            'independence': not baseline_stats['has_autocorrelation'],
            'sufficient_sample_size': baseline_stats['n_samples'] >= 30
        }
        
        # Choose appropriate test based on assumptions
        if baseline_stats['is_normal'] and assumptions_met['independence']:
            # Use parametric Z-test
            z_score = (anomaly_value - baseline_stats['mean']) / baseline_stats['std']
            p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))  # Two-tailed test
            test_type = "Z-test (parametric)"
            statistic = z_score
            
        else:
            # Use robust non-parametric approach
            # Modified Z-score using median and MAD
            modified_z = 0.6745 * (anomaly_value - baseline_stats['median']) / baseline_stats['mad']
            
            # Bootstrap for p-value calculation
            n_bootstrap = 10000
            bootstrap_stats = []
            
            for _ in range(n_bootstrap):
                bootstrap_sample = np.random.choice(baseline_data, size=len(baseline_data), replace=True)
                bootstrap_median = np.median(bootstrap_sample)
                bootstrap_mad = stats.median_abs_deviation(bootstrap_sample)
                if bootstrap_mad > 0:
                    bootstrap_z = 0.6745 * (np.random.choice(bootstrap_sample) - bootstrap_median) / bootstrap_mad
                    bootstrap_stats.append(abs(bootstrap_z))
            
            p_value = np.mean(np.array(bootstrap_stats) >= abs(modified_z))
            test_type = "Modified Z-test with bootstrap (non-parametric)"
            statistic = modified_z
        
        # Calculate effect size (Cohen's d)
        if baseline_stats['is_normal']:
            cohens_d = (anomaly_value - baseline_stats['mean']) / baseline_stats['std']
        else:
            # Robust effect size using MAD
            cohens_d = (anomaly_value - baseline_stats['median']) / baseline_stats['mad']
        
        # Interpret effect size
        if abs(cohens_d) < 0.2:
            effect_size_interpretation = "negligible"
        elif abs(cohens_d) < 0.5:
            effect_size_interpretation = "small"
        elif abs(cohens_d) < 0.8:
            effect_size_interpretation = "medium"
        else:
            effect_size_interpretation = "large"
        
        # Calculate confidence interval for effect size
        # Using bootstrap for robust CI
        bootstrap_effects = []
        for _ in range(1000):
            bootstrap_sample = np.random.choice(baseline_data, size=len(baseline_data), replace=True)
            if baseline_stats['is_normal']:
                boot_mean = np.mean(bootstrap_sample)
                boot_std = np.std(bootstrap_sample, ddof=1)
                if boot_std > 0:
                    boot_effect = (anomaly_value - boot_mean) / boot_std
                    bootstrap_effects.append(boot_effect)
            else:
                boot_median = np.median(bootstrap_sample)
                boot_mad = stats.median_abs_deviation(bootstrap_sample)
                if boot_mad > 0:
                    boot_effect = (anomaly_value - boot_median) / boot_mad
                    bootstrap_effects.append(boot_effect)
        
        if bootstrap_effects:
            ci_lower = np.percentile(bootstrap_effects, 2.5)
            ci_upper = np.percentile(bootstrap_effects, 97.5)
            confidence_interval = (ci_lower, ci_upper)
        else:
            confidence_interval = (np.nan, np.nan)
        
        # Identify limitations
        limitations = []
        if not assumptions_met['normality']:
            limitations.append("Baseline data is not normally distributed")
        if not assumptions_met['independence']:
            limitations.append("Data shows significant autocorrelation")
        if anomaly_frame < self.baseline_frames * 2:
            limitations.append("Anomaly occurs too close to baseline period")
        if baseline_stats['std'] == 0 or baseline_stats['mad'] == 0:
            limitations.append("Baseline shows no variation")
        
        return StatisticalResult(
            test_type=test_type,
            statistic=statistic,
            p_value=p_value,
            effect_size=cohens_d,
            effect_size_interpretation=effect_size_interpretation,
            confidence_interval=confidence_interval,
            is_significant=p_value < self.significance_level,
            baseline_properties=baseline_stats,
            assumptions_met=assumptions_met,
            limitations=limitations
        )
    
    def comprehensive_analysis(self, compression_ratios: np.ndarray) -> Dict:
        """
        Perform comprehensive statistical analysis of compression ratios.
        
        Args:
            compression_ratios: Array of compression ratios
            
        Returns:
            Dictionary containing all analysis results
        """
        results = {}
        
        # Establish baseline
        results['baseline'] = self.establish_baseline(compression_ratios)
        
        # Change point detection
        cusum_points, cusum_pos, cusum_neg = self.detect_change_points_cusum(compression_ratios)
        results['cusum_change_points'] = cusum_points
        results['cusum_statistics'] = {
            'positive': cusum_pos,
            'negative': cusum_neg
        }
        
        # Bayesian change point detection
        bayes_points, bayes_probs = self.bayesian_change_point_detection(compression_ratios)
        results['bayesian_change_points'] = bayes_points
        results['bayesian_probabilities'] = bayes_probs
        
        # Statistical testing for detected change points
        results['significance_tests'] = []
        
        # Test CUSUM detected points
        for point in cusum_points[:5]:  # Limit to first 5 points
            if point < len(compression_ratios):
                test_result = self.test_compression_anomaly(compression_ratios, point)
                results['significance_tests'].append({
                    'frame': point,
                    'method': 'CUSUM',
                    'result': test_result
                })
        
        # Test Bayesian detected points
        for point in bayes_points[:5]:  # Limit to first 5 points
            if point < len(compression_ratios) and point not in cusum_points:
                test_result = self.test_compression_anomaly(compression_ratios, point)
                results['significance_tests'].append({
                    'frame': point,
                    'method': 'Bayesian',
                    'result': test_result
                })
        
        return results
    
    def generate_report(self, analysis_results: Dict) -> str:
        """
        Generate a comprehensive statistical report.
        
        Args:
            analysis_results: Results from comprehensive_analysis
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("CORRECTED STATISTICAL ANALYSIS REPORT")
        report.append("=" * 50)
        report.append("")
        
        # Baseline properties
        baseline = analysis_results['baseline']
        report.append("BASELINE PROPERTIES:")
        report.append(f"  Sample size: {baseline['n_samples']}")
        report.append(f"  Mean: {baseline['mean']:.4f}")
        report.append(f"  Standard deviation: {baseline['std']:.4f}")
        report.append(f"  Median: {baseline['median']:.4f}")
        report.append(f"  MAD: {baseline['mad']:.4f}")
        report.append(f"  Normality (Shapiro-Wilk p-value): {baseline['shapiro_p']:.6f}")
        report.append(f"  Is normal: {baseline['is_normal']}")
        report.append(f"  Autocorrelation (lag-1): {baseline['autocorr_lag1']:.4f}")
        report.append(f"  Has autocorrelation: {baseline['has_autocorrelation']}")
        report.append("")
        
        # Change point detection
        report.append("CHANGE POINT DETECTION:")
        report.append(f"  CUSUM detected points: {len(analysis_results['cusum_change_points'])}")
        if analysis_results['cusum_change_points']:
            report.append(f"    Frames: {analysis_results['cusum_change_points'][:10]}")  # Show first 10
        
        report.append(f"  Bayesian detected points: {len(analysis_results['bayesian_change_points'])}")
        if analysis_results['bayesian_change_points']:
            report.append(f"    Frames: {analysis_results['bayesian_change_points'][:10]}")  # Show first 10
        report.append("")
        
        # Significance tests
        report.append("SIGNIFICANCE TESTING:")
        for i, test in enumerate(analysis_results['significance_tests']):
            result = test['result']
            report.append(f"  Test {i+1} - Frame {test['frame']} ({test['method']}):")
            report.append(f"    Test type: {result.test_type}")
            report.append(f"    Statistic: {result.statistic:.4f}")
            report.append(f"    P-value: {result.p_value:.6f}")
            report.append(f"    Significant: {result.is_significant}")
            report.append(f"    Effect size (Cohen's d): {result.effect_size:.4f} ({result.effect_size_interpretation})")
            report.append(f"    95% CI for effect size: [{result.confidence_interval[0]:.4f}, {result.confidence_interval[1]:.4f}]")
            
            if result.limitations:
                report.append(f"    Limitations: {'; '.join(result.limitations)}")
            report.append("")
        
        return "\n".join(report)

def main():
    """
    Example usage of the corrected statistical analysis.
    """
    # Generate example data with a change point
    np.random.seed(42)
    
    # Baseline data (normal compression ratios)
    baseline = np.random.normal(15, 2, 1000)
    
    # Anomaly data (sudden spike)
    anomaly_section = np.array([85, 87, 83, 89, 86])  # 5 frames of high compression
    
    # Return to baseline
    post_anomaly = np.random.normal(15.5, 2.1, 500)
    
    # Combine data
    compression_ratios = np.concatenate([baseline, anomaly_section, post_anomaly])
    
    # Perform analysis
    analyzer = VideoForensicsStatistics()
    results = analyzer.comprehensive_analysis(compression_ratios)
    
    # Generate report
    report = analyzer.generate_report(results)
    print(report)
    
    # Test specific anomaly
    anomaly_frame = 1002  # Frame in the anomaly section
    test_result = analyzer.test_compression_anomaly(compression_ratios, anomaly_frame)
    
    print("\nDETAILED ANOMALY TEST:")
    print(f"Frame {anomaly_frame} analysis:")
    print(f"  Test: {test_result.test_type}")
    print(f"  Statistic: {test_result.statistic:.4f}")
    print(f"  P-value: {test_result.p_value:.6f}")
    print(f"  Effect size: {test_result.effect_size:.4f} ({test_result.effect_size_interpretation})")
    print(f"  Significant: {test_result.is_significant}")

if __name__ == "__main__":
    main()

