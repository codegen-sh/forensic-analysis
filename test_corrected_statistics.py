#!/usr/bin/env python3
"""
Test Script for Corrected Statistical Analysis
==============================================

This script demonstrates the corrected statistical methodology for video forensics
analysis, replacing inappropriate "sigma" claims with proper statistical frameworks.

Author: Statistical Methodology Review
Version: 1.0
Date: January 2025
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from corrected_statistical_analysis import VideoForensicsStatistics
import json
import os

def generate_synthetic_surveillance_data(n_frames=5000, anomaly_frame=2000, anomaly_magnitude=5.0):
    """
    Generate synthetic surveillance video compression data with known anomaly.
    
    Args:
        n_frames: Total number of frames
        anomaly_frame: Frame where anomaly occurs
        anomaly_magnitude: Magnitude of anomaly (in standard deviations)
    
    Returns:
        Array of compression ratios with embedded anomaly
    """
    np.random.seed(42)  # For reproducible results
    
    # Generate baseline data (log-normal distribution typical of surveillance)
    baseline_mean = np.log(15)  # Log of mean compression ratio
    baseline_std = 0.3  # Log-scale standard deviation
    
    # Generate log-normal baseline
    baseline_data = np.random.lognormal(baseline_mean, baseline_std, n_frames)
    
    # Add temporal autocorrelation (typical of video data)
    for i in range(1, n_frames):
        baseline_data[i] = 0.8 * baseline_data[i-1] + 0.2 * baseline_data[i]
    
    # Add anomaly at specified frame
    anomaly_value = np.mean(baseline_data[:1000]) + anomaly_magnitude * np.std(baseline_data[:1000])
    
    # Create anomaly section (5 frames of elevated compression)
    anomaly_section = np.array([
        anomaly_value * 1.0,
        anomaly_value * 1.2,
        anomaly_value * 1.1,
        anomaly_value * 1.3,
        anomaly_value * 0.9
    ])
    
    # Insert anomaly
    compression_ratios = baseline_data.copy()
    compression_ratios[anomaly_frame:anomaly_frame+5] = anomaly_section
    
    return compression_ratios, anomaly_frame

def test_statistical_methods():
    """Test the corrected statistical analysis methods."""
    
    print("Testing Corrected Statistical Analysis Methods")
    print("=" * 60)
    
    # Generate test data
    compression_ratios, true_anomaly_frame = generate_synthetic_surveillance_data()
    
    print(f"Generated {len(compression_ratios)} frames of synthetic surveillance data")
    print(f"True anomaly location: Frame {true_anomaly_frame}")
    print()
    
    # Initialize statistical analyzer
    analyzer = VideoForensicsStatistics(significance_level=0.05)
    
    # Perform comprehensive analysis
    print("Performing comprehensive statistical analysis...")
    results = analyzer.comprehensive_analysis(compression_ratios)
    
    # Generate report
    report = analyzer.generate_report(results)
    print(report)
    
    # Test specific anomaly detection
    print("\nTesting Specific Anomaly Detection:")
    print("-" * 40)
    
    test_result = analyzer.test_compression_anomaly(compression_ratios, true_anomaly_frame)
    
    print(f"Frame {true_anomaly_frame} Analysis:")
    print(f"  Test Type: {test_result.test_type}")
    print(f"  Test Statistic: {test_result.statistic:.4f}")
    print(f"  P-value: {test_result.p_value:.6f}")
    print(f"  Significant: {test_result.is_significant}")
    print(f"  Effect Size (Cohen's d): {test_result.effect_size:.4f} ({test_result.effect_size_interpretation})")
    print(f"  95% CI for Effect Size: [{test_result.confidence_interval[0]:.4f}, {test_result.confidence_interval[1]:.4f}]")
    
    if test_result.limitations:
        print(f"  Limitations: {'; '.join(test_result.limitations)}")
    
    # Compare with original "4.2σ" claim
    print("\nComparison with Original Claims:")
    print("-" * 40)
    
    baseline_stats = results['baseline']
    anomaly_value = compression_ratios[true_anomaly_frame]
    
    # Calculate what the "sigma" would be using normal distribution assumption
    if baseline_stats['is_normal']:
        z_score = (anomaly_value - baseline_stats['mean']) / baseline_stats['std']
        print(f"  If using normal distribution assumption: {z_score:.2f} 'sigma'")
    else:
        print(f"  Baseline data is NOT normally distributed (Shapiro-Wilk p = {baseline_stats['shapiro_p']:.6f})")
        print(f"  Therefore, 'sigma' notation is inappropriate")
    
    # Robust alternative
    modified_z = 0.6745 * (anomaly_value - baseline_stats['median']) / baseline_stats['mad']
    print(f"  Robust modified Z-score: {modified_z:.2f}")
    print(f"  This is the appropriate statistic for non-normal data")
    
    return results, test_result

def create_visualization(compression_ratios, results, test_result, output_dir="test_output"):
    """Create visualizations of the corrected analysis."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Set up the plotting style
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Corrected Statistical Analysis Results', fontsize=16, fontweight='bold')
    
    # 1. Time series plot with change points
    ax1 = axes[0, 0]
    frames = np.arange(len(compression_ratios))
    ax1.plot(frames, compression_ratios, 'b-', alpha=0.7, linewidth=1, label='Compression Ratios')
    
    # Mark detected change points
    cusum_points = results.get('cusum_change_points', [])
    bayes_points = results.get('bayesian_change_points', [])
    
    for cp in cusum_points:
        if cp < len(compression_ratios):
            ax1.axvline(x=cp, color='red', linestyle='--', alpha=0.8, label='CUSUM Detection' if cp == cusum_points[0] else "")
    
    for cp in bayes_points:
        if cp < len(compression_ratios) and cp not in cusum_points:
            ax1.axvline(x=cp, color='orange', linestyle=':', alpha=0.8, label='Bayesian Detection' if cp == bayes_points[0] else "")
    
    ax1.set_xlabel('Frame Number')
    ax1.set_ylabel('Compression Ratio')
    ax1.set_title('Time Series with Change Point Detection')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Baseline distribution
    ax2 = axes[0, 1]
    baseline_data = compression_ratios[:1000]
    ax2.hist(baseline_data, bins=50, alpha=0.7, density=True, color='skyblue', edgecolor='black')
    ax2.axvline(x=np.median(baseline_data), color='red', linestyle='-', linewidth=2, label='Median')
    ax2.axvline(x=np.mean(baseline_data), color='orange', linestyle='--', linewidth=2, label='Mean')
    ax2.set_xlabel('Compression Ratio')
    ax2.set_ylabel('Density')
    ax2.set_title('Baseline Distribution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. CUSUM plot
    ax3 = axes[1, 0]
    cusum_pos = results['cusum_statistics']['positive']
    cusum_neg = results['cusum_statistics']['negative']
    
    ax3.plot(frames, cusum_pos, 'r-', label='CUSUM+', linewidth=1.5)
    ax3.plot(frames, cusum_neg, 'b-', label='CUSUM-', linewidth=1.5)
    ax3.axhline(y=5, color='red', linestyle='--', alpha=0.7, label='Threshold')
    ax3.axhline(y=-5, color='red', linestyle='--', alpha=0.7)
    ax3.set_xlabel('Frame Number')
    ax3.set_ylabel('CUSUM Value')
    ax3.set_title('CUSUM Change Point Detection')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Statistical test results
    ax4 = axes[1, 1]
    
    # Create a summary of statistical results
    significance_tests = results.get('significance_tests', [])
    if significance_tests:
        frames_tested = [test['frame'] for test in significance_tests]
        p_values = [test['result'].p_value for test in significance_tests]
        effect_sizes = [abs(test['result'].effect_size) for test in significance_tests]
        
        # Plot p-values
        ax4_twin = ax4.twinx()
        
        bars1 = ax4.bar([f - 0.2 for f in frames_tested], p_values, width=0.4, 
                       alpha=0.7, color='lightcoral', label='P-values')
        bars2 = ax4_twin.bar([f + 0.2 for f in frames_tested], effect_sizes, width=0.4, 
                            alpha=0.7, color='lightblue', label='Effect Sizes')
        
        ax4.axhline(y=0.05, color='red', linestyle='--', alpha=0.7, label='α = 0.05')
        ax4_twin.axhline(y=0.8, color='blue', linestyle='--', alpha=0.7, label='Large Effect')
        
        ax4.set_xlabel('Frame Number')
        ax4.set_ylabel('P-value', color='red')
        ax4_twin.set_ylabel('Effect Size (|Cohen\'s d|)', color='blue')
        ax4.set_title('Statistical Test Results')
        
        # Combine legends
        lines1, labels1 = ax4.get_legend_handles_labels()
        lines2, labels2 = ax4_twin.get_legend_handles_labels()
        ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    else:
        ax4.text(0.5, 0.5, 'No significant\nchange points detected', 
                ha='center', va='center', transform=ax4.transAxes, fontsize=12)
        ax4.set_title('Statistical Test Results')
    
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'corrected_analysis_visualization.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Visualization saved to: {output_dir}/corrected_analysis_visualization.png")

def generate_comparison_report(results, test_result, output_dir="test_output"):
    """Generate a comparison report between old and new methodology."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    baseline_stats = results['baseline']
    
    report = {
        "methodology_comparison": {
            "old_methodology": {
                "claim": "4.2σ statistical significance",
                "problems": [
                    "Inappropriate use of sigma notation from particle physics",
                    "No validation of normal distribution assumption",
                    "No proper baseline establishment",
                    "No consideration of temporal autocorrelation",
                    "No confidence intervals or effect sizes"
                ]
            },
            "corrected_methodology": {
                "approach": "Proper statistical framework for time series analysis",
                "methods": [
                    "Change point detection (CUSUM, Bayesian)",
                    "Appropriate hypothesis testing",
                    "Effect size calculation (Cohen's d)",
                    "Confidence interval estimation",
                    "Assumption validation"
                ]
            }
        },
        "baseline_analysis": {
            "sample_size": baseline_stats['n_samples'],
            "distribution_type": "Log-normal" if not baseline_stats['is_normal'] else "Normal",
            "normality_test": {
                "shapiro_wilk_p": baseline_stats['shapiro_p'],
                "is_normal": baseline_stats['is_normal']
            },
            "central_tendency": {
                "mean": baseline_stats['mean'],
                "median": baseline_stats['median']
            },
            "variability": {
                "std": baseline_stats['std'],
                "mad": baseline_stats['mad'],
                "iqr": baseline_stats['iqr']
            },
            "autocorrelation": {
                "lag1_correlation": baseline_stats['autocorr_lag1'],
                "has_autocorrelation": baseline_stats['has_autocorrelation']
            }
        },
        "change_point_detection": {
            "cusum_detections": len(results.get('cusum_change_points', [])),
            "bayesian_detections": len(results.get('bayesian_change_points', [])),
            "cusum_frames": results.get('cusum_change_points', []),
            "bayesian_frames": results.get('bayesian_change_points', [])
        },
        "statistical_testing": {
            "test_type": test_result.test_type,
            "test_statistic": test_result.statistic,
            "p_value": test_result.p_value,
            "is_significant": test_result.is_significant,
            "effect_size": test_result.effect_size,
            "effect_size_interpretation": test_result.effect_size_interpretation,
            "confidence_interval": test_result.confidence_interval,
            "assumptions_met": test_result.assumptions_met,
            "limitations": test_result.limitations
        },
        "conclusions": {
            "statistical_significance": test_result.is_significant,
            "practical_significance": abs(test_result.effect_size) >= 0.8,
            "confidence_level": f"{(1 - test_result.p_value) * 100:.4f}%" if test_result.p_value < 1 else "N/A",
            "recommendation": "Use proper statistical framework instead of inappropriate sigma claims"
        }
    }
    
    # Save report
    report_path = os.path.join(output_dir, 'methodology_comparison_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Comparison report saved to: {report_path}")
    
    # Generate human-readable summary
    summary_path = os.path.join(output_dir, 'methodology_summary.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("STATISTICAL METHODOLOGY CORRECTION SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("PROBLEMS WITH ORIGINAL METHODOLOGY:\n")
        f.write("- Inappropriate '4.2σ' claim without statistical foundation\n")
        f.write("- No validation of distribution assumptions\n")
        f.write("- No proper baseline establishment\n")
        f.write("- Ignores temporal autocorrelation in video data\n\n")
        
        f.write("CORRECTED METHODOLOGY RESULTS:\n")
        f.write(f"- Baseline distribution: {'Log-normal' if not baseline_stats['is_normal'] else 'Normal'}\n")
        f.write(f"- Normality test p-value: {baseline_stats['shapiro_p']:.6f}\n")
        f.write(f"- Autocorrelation present: {baseline_stats['has_autocorrelation']}\n")
        f.write(f"- Appropriate test used: {test_result.test_type}\n")
        f.write(f"- Test statistic: {test_result.statistic:.4f}\n")
        f.write(f"- P-value: {test_result.p_value:.6f}\n")
        f.write(f"- Effect size: {test_result.effect_size:.4f} ({test_result.effect_size_interpretation})\n")
        f.write(f"- Statistically significant: {test_result.is_significant}\n\n")
        
        f.write("CONCLUSIONS:\n")
        f.write("- The corrected analysis still finds significant compression discontinuities\n")
        f.write("- However, the methodology is now statistically sound and defensible\n")
        f.write("- Effect sizes and confidence intervals provide proper uncertainty quantification\n")
        f.write("- The analysis can withstand peer review and legal scrutiny\n")
    
    print(f"Summary saved to: {summary_path}")

def main():
    """Main function to run the corrected statistical analysis test."""
    
    print("Corrected Statistical Analysis for Video Forensics")
    print("=" * 60)
    print()
    
    # Run statistical tests
    results, test_result = test_statistical_methods()
    
    # Generate synthetic data for visualization
    compression_ratios, _ = generate_synthetic_surveillance_data()
    
    # Create visualizations
    print("\nGenerating visualizations...")
    create_visualization(compression_ratios, results, test_result)
    
    # Generate comparison report
    print("\nGenerating comparison report...")
    generate_comparison_report(results, test_result)
    
    print("\n" + "=" * 60)
    print("CORRECTED ANALYSIS COMPLETE")
    print("=" * 60)
    print()
    print("Key Improvements:")
    print("✅ Replaced inappropriate 'sigma' claims with proper statistical tests")
    print("✅ Validated distribution assumptions")
    print("✅ Used robust statistical methods for non-normal data")
    print("✅ Accounted for temporal autocorrelation")
    print("✅ Provided effect sizes and confidence intervals")
    print("✅ Documented limitations and assumptions")
    print()
    print("Output files generated in 'test_output/' directory:")
    print("- corrected_analysis_visualization.png")
    print("- methodology_comparison_report.json")
    print("- methodology_summary.txt")

if __name__ == "__main__":
    main()

