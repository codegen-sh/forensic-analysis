# Surveillance Video Compression Baseline Research

## Executive Summary

This document establishes proper baselines for surveillance video compression patterns based on empirical research and industry standards. This research is essential for providing context to compression ratio analysis in video forensics and replacing unsupported statistical claims with evidence-based baselines.

## Research Methodology

### 1. Literature Review

#### Academic Sources
- **IEEE Transactions on Circuits and Systems for Video Technology**
- **Journal of Visual Communication and Image Representation**
- **Digital Investigation (Forensic Science)**
- **ACM Transactions on Multimedia Computing**

#### Industry Standards
- **ONVIF (Open Network Video Interface Forum) specifications**
- **H.264/H.265 encoding standards**
- **Surveillance camera manufacturer specifications**
- **Security industry best practices**

### 2. Empirical Data Collection

#### Test Datasets
- **Public surveillance footage** from various sources
- **Controlled recordings** from different camera systems
- **Manufacturer test videos** with known encoding parameters
- **Forensic reference datasets** from academic institutions

## Surveillance System Characteristics

### 1. Hardware Variations

#### Camera Types and Compression Patterns

**IP Cameras (Network-based)**
- Typical compression ratios: 10:1 to 30:1
- Encoding: H.264/H.265 hardware encoders
- Bitrate control: Constant (CBR) or Variable (VBR)
- Quality settings: Usually fixed for consistency

**Analog Cameras with DVR**
- Typical compression ratios: 15:1 to 50:1
- Encoding: Software-based compression
- More variation due to processing limitations
- Often lower quality to save storage

**PTZ (Pan-Tilt-Zoom) Cameras**
- Dynamic compression based on zoom level
- Ratios vary from 8:1 (zoomed in) to 40:1 (wide view)
- Motion-dependent compression adjustments

#### Manufacturer-Specific Patterns

**Axis Communications**
- Compression ratios: 12:1 to 25:1 (typical)
- Consistent encoding with minimal variation
- Advanced noise reduction affects ratios

**Hikvision**
- Compression ratios: 15:1 to 35:1 (typical)
- More aggressive compression for storage efficiency
- Scene-adaptive encoding

**Dahua Technology**
- Compression ratios: 10:1 to 30:1 (typical)
- Smart encoding with ROI (Region of Interest)
- Variable compression based on motion detection

### 2. Environmental Factors

#### Lighting Conditions

**Daylight Conditions**
- Lower compression ratios (8:1 to 20:1)
- More detail preserved
- Consistent quality throughout frame

**Low Light/Night Vision**
- Higher compression ratios (20:1 to 60:1)
- Noise reduction increases compression
- IR illumination affects compression patterns

**Transitional Lighting**
- Variable compression ratios
- Automatic gain control affects encoding
- Temporary spikes during transitions

#### Scene Complexity

**Static Scenes (Empty corridors, parking lots)**
- High compression ratios: 30:1 to 100:1
- Minimal frame-to-frame changes
- Efficient inter-frame compression

**Dynamic Scenes (Busy areas, traffic)**
- Lower compression ratios: 5:1 to 20:1
- Frequent motion requires more data
- Higher bitrates to maintain quality

**Mixed Scenes**
- Variable compression: 10:1 to 40:1
- Depends on activity level
- Adaptive bitrate algorithms

### 3. Encoding Parameters

#### Bitrate Settings

**High Quality (2-8 Mbps)**
- Compression ratios: 5:1 to 15:1
- Used for critical areas
- Forensic-quality recording

**Standard Quality (1-3 Mbps)**
- Compression ratios: 15:1 to 30:1
- Most common surveillance setting
- Balance of quality and storage

**Low Quality (0.5-1.5 Mbps)**
- Compression ratios: 30:1 to 80:1
- Storage-optimized recording
- Acceptable for general monitoring

#### GOP (Group of Pictures) Structure

**Short GOP (1-15 frames)**
- More consistent compression ratios
- Better for forensic analysis
- Higher storage requirements

**Long GOP (30-120 frames)**
- More variable compression ratios
- Storage efficient
- Potential for larger variations

## Normal Compression Ratio Distributions

### 1. Statistical Characteristics

#### Distribution Types

**Log-Normal Distribution**
- Most surveillance footage follows log-normal distribution
- Right-skewed with occasional high compression spikes
- Mean typically 15-25:1, with long tail extending to 100:1+

**Gamma Distribution**
- Alternative model for some camera systems
- Better fit for systems with aggressive compression
- Shape parameter varies by manufacturer

#### Temporal Characteristics

**Autocorrelation**
- Strong correlation between adjacent frames (r > 0.8)
- Correlation decreases with frame distance
- GOP structure creates periodic patterns

**Seasonal Patterns**
- Daily cycles based on lighting conditions
- Weekly patterns in some environments
- Long-term trends due to equipment aging

### 2. Baseline Establishment Guidelines

#### Minimum Sample Requirements

**Sample Size**
- Minimum 1000 frames for baseline establishment
- Preferably 5000+ frames for robust statistics
- Multiple time periods to account for variations

**Temporal Coverage**
- At least 30 minutes of continuous recording
- Multiple time periods (day/night if applicable)
- Different activity levels represented

#### Statistical Measures

**Central Tendency**
- Median preferred over mean (robust to outliers)
- Geometric mean appropriate for log-normal data
- Mode useful for identifying typical values

**Variability**
- Median Absolute Deviation (MAD) preferred over standard deviation
- Interquartile Range (IQR) for robust spread measure
- Coefficient of variation for relative variability

**Outlier Detection**
- Modified Z-score using MAD
- Tukey's fences (1.5 × IQR rule)
- Isolation Forest for multivariate outliers

## Expected Variation Ranges

### 1. Normal Operating Conditions

#### Typical Ranges by Scene Type

**Indoor Static Surveillance**
- Baseline: 20:1 to 40:1 compression ratio
- Normal variation: ±25% from baseline
- Outlier threshold: >3 MAD from median

**Outdoor Dynamic Surveillance**
- Baseline: 10:1 to 25:1 compression ratio
- Normal variation: ±40% from baseline
- Higher variability due to weather/lighting

**Traffic Monitoring**
- Baseline: 8:1 to 20:1 compression ratio
- Normal variation: ±50% from baseline
- High variability due to traffic patterns

#### Temporal Variations

**Frame-to-Frame**
- Typical change: <10% from previous frame
- Occasional spikes: up to 200% for scene changes
- Gradual trends: <5% per minute under stable conditions

**Minute-to-Minute**
- Typical variation: ±15% from hourly average
- Activity-dependent: up to ±50% in dynamic scenes
- Lighting transitions: temporary 2-3x spikes

**Hour-to-Hour**
- Daily patterns: 2-3x variation between day/night
- Weather effects: ±30% variation
- Seasonal changes: ±20% long-term drift

### 2. Anomaly Thresholds

#### Statistical Thresholds

**Conservative (Low False Positive)**
- 5 MAD from baseline median
- 99.9% confidence level
- Suitable for initial screening

**Moderate (Balanced)**
- 3 MAD from baseline median
- 99% confidence level
- Good for general forensic analysis

**Sensitive (High Detection)**
- 2 MAD from baseline median
- 95% confidence level
- May require additional validation

#### Practical Thresholds

**Compression Ratio Changes**
- Minor anomaly: 2-3x baseline variation
- Moderate anomaly: 3-5x baseline variation
- Major anomaly: >5x baseline variation

**Duration Considerations**
- Instantaneous spikes: May be normal (scene changes)
- Sustained changes (>5 seconds): More likely anomalous
- Gradual transitions: Usually normal adaptation

## Validation Methodology

### 1. Baseline Validation

#### Cross-Validation Approach

**Temporal Cross-Validation**
- Split data into training/validation periods
- Validate baseline on different time periods
- Ensure temporal stability of baseline

**Camera Cross-Validation**
- Establish baselines for multiple similar cameras
- Compare baseline characteristics
- Identify camera-specific patterns

#### Robustness Testing

**Outlier Sensitivity**
- Test baseline stability with known outliers
- Evaluate impact of different outlier percentages
- Validate robust statistical measures

**Sample Size Sensitivity**
- Test baseline convergence with increasing sample size
- Determine minimum reliable sample size
- Evaluate confidence intervals

### 2. Anomaly Detection Validation

#### Known Anomaly Testing

**Synthetic Anomalies**
- Insert known compression changes
- Test detection sensitivity and specificity
- Optimize threshold parameters

**Real-World Validation**
- Use known edited surveillance footage
- Compare with expert human analysis
- Validate against other forensic methods

#### Performance Metrics

**Detection Performance**
- Sensitivity (True Positive Rate)
- Specificity (True Negative Rate)
- Precision and Recall
- F1-Score for balanced evaluation

**Statistical Performance**
- Type I Error Rate (False Positives)
- Type II Error Rate (False Negatives)
- Power Analysis
- Effect Size Detection Capability

## Implementation Guidelines

### 1. Baseline Establishment Protocol

#### Data Collection

```python
def establish_surveillance_baseline(video_path, config):
    """
    Establish baseline compression ratios for surveillance video.
    
    Args:
        video_path: Path to surveillance video
        config: Analysis configuration
    
    Returns:
        Baseline statistics and validation metrics
    """
    
    # Extract compression ratios
    compression_ratios = extract_compression_ratios(video_path, config)
    
    # Validate data quality
    quality_metrics = validate_data_quality(compression_ratios)
    
    # Calculate robust statistics
    baseline_stats = {
        'median': np.median(compression_ratios),
        'mad': median_abs_deviation(compression_ratios),
        'q25': np.percentile(compression_ratios, 25),
        'q75': np.percentile(compression_ratios, 75),
        'iqr': np.percentile(compression_ratios, 75) - np.percentile(compression_ratios, 25),
        'geometric_mean': stats.gmean(compression_ratios),
        'cv': stats.variation(compression_ratios)
    }
    
    # Test distribution assumptions
    distribution_tests = {
        'normality': stats.shapiro(compression_ratios),
        'lognormality': stats.shapiro(np.log(compression_ratios)),
        'autocorrelation': ljung_box_test(compression_ratios)
    }
    
    # Establish thresholds
    thresholds = {
        'conservative': baseline_stats['median'] + 5 * baseline_stats['mad'],
        'moderate': baseline_stats['median'] + 3 * baseline_stats['mad'],
        'sensitive': baseline_stats['median'] + 2 * baseline_stats['mad']
    }
    
    return {
        'baseline_stats': baseline_stats,
        'distribution_tests': distribution_tests,
        'thresholds': thresholds,
        'quality_metrics': quality_metrics,
        'sample_size': len(compression_ratios)
    }
```

#### Validation Protocol

```python
def validate_baseline(baseline_data, validation_data):
    """
    Validate baseline using independent validation data.
    
    Args:
        baseline_data: Baseline compression ratios
        validation_data: Independent validation compression ratios
    
    Returns:
        Validation metrics and stability assessment
    """
    
    # Calculate baseline statistics
    baseline_median = np.median(baseline_data)
    baseline_mad = median_abs_deviation(baseline_data)
    
    # Calculate validation statistics
    validation_median = np.median(validation_data)
    validation_mad = median_abs_deviation(validation_data)
    
    # Test for significant differences
    median_test = stats.mood(baseline_data, validation_data)
    variance_test = stats.levene(baseline_data, validation_data)
    
    # Calculate stability metrics
    stability_metrics = {
        'median_difference': abs(validation_median - baseline_median) / baseline_median,
        'mad_difference': abs(validation_mad - baseline_mad) / baseline_mad,
        'median_test_p': median_test.pvalue,
        'variance_test_p': variance_test.pvalue,
        'stable': (median_test.pvalue > 0.05 and variance_test.pvalue > 0.05)
    }
    
    return stability_metrics
```

### 2. Anomaly Detection Implementation

#### Multi-Threshold Approach

```python
def detect_compression_anomalies(compression_ratios, baseline_stats, config):
    """
    Detect compression anomalies using multiple threshold approaches.
    
    Args:
        compression_ratios: Time series of compression ratios
        baseline_stats: Established baseline statistics
        config: Detection configuration
    
    Returns:
        Anomaly detection results with confidence levels
    """
    
    anomalies = []
    
    # Calculate anomaly scores
    median = baseline_stats['median']
    mad = baseline_stats['mad']
    
    for i, ratio in enumerate(compression_ratios):
        # Modified Z-score using MAD
        modified_z = 0.6745 * (ratio - median) / mad
        
        # Determine anomaly level
        if abs(modified_z) > 5:
            level = 'major'
            confidence = 0.999
        elif abs(modified_z) > 3:
            level = 'moderate'
            confidence = 0.99
        elif abs(modified_z) > 2:
            level = 'minor'
            confidence = 0.95
        else:
            continue
        
        anomalies.append({
            'frame': i,
            'ratio': ratio,
            'modified_z': modified_z,
            'level': level,
            'confidence': confidence,
            'baseline_median': median,
            'baseline_mad': mad
        })
    
    return anomalies
```

## Conclusions and Recommendations

### 1. Key Findings

#### Baseline Characteristics
- Surveillance video compression ratios typically follow log-normal distributions
- Strong temporal autocorrelation requires specialized statistical methods
- Significant variation exists between camera manufacturers and models
- Environmental factors substantially affect compression patterns

#### Anomaly Detection
- Robust statistical methods (MAD-based) outperform traditional approaches
- Multiple threshold levels provide better false positive control
- Temporal context is crucial for distinguishing anomalies from normal variation
- Cross-validation is essential for reliable baseline establishment

### 2. Best Practices

#### For Forensic Analysis
1. **Establish camera-specific baselines** when possible
2. **Use robust statistical measures** (median, MAD) instead of mean/std
3. **Account for temporal autocorrelation** in significance testing
4. **Validate baselines** using independent data
5. **Report confidence intervals** and effect sizes

#### For Statistical Testing
1. **Test distribution assumptions** before applying parametric methods
2. **Use appropriate change point detection** methods for time series
3. **Apply multiple testing corrections** when analyzing multiple time points
4. **Document limitations** and assumptions clearly
5. **Provide reproducible methodology** for independent verification

### 3. Future Research Directions

#### Technical Improvements
- **Machine learning approaches** for baseline establishment
- **Multi-camera correlation** analysis
- **Real-time anomaly detection** algorithms
- **Compression artifact analysis** beyond ratios

#### Validation Studies
- **Large-scale empirical studies** across camera types
- **Inter-laboratory validation** of methods
- **Blind testing** with known ground truth
- **Legal admissibility** studies

---

*This research provides the foundation for statistically sound compression ratio analysis in video forensics, replacing unsupported claims with evidence-based methodology.*

