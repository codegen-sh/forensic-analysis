# Enhanced Forensic Video Analysis Framework

## 🔍 Advanced Multi-Dimensional Splice Detection

This enhanced framework provides comprehensive forensic analysis of video files using multiple computer vision techniques to detect splicing, editing, and manipulation with high statistical confidence.

## 🚀 New Features

### 📊 Time-Series Analysis
- **Whole-video compression analysis** with interactive timeline visualization
- **Anomaly detection** using statistical thresholds and confidence intervals
- **Interactive charts** with zoom, pan, and brush selection capabilities
- **Real-time progress tracking** for large video files

### 👁️ Multi-Dimensional Analysis
- **Compression Analysis**: File size discontinuities, quality metrics, DCT coefficient analysis
- **Optical Flow Detection**: Motion vector analysis, temporal consistency checking
- **Color Histogram Analysis**: Lighting changes, camera switches, color temperature variations
- **Noise Pattern Detection**: Encoding signatures, compression artifacts, texture analysis

### 🎯 Advanced Evidence Aggregation
- **Confidence scoring** with statistical significance testing
- **Multi-technique evidence fusion** for robust detection
- **Visual artifact identification** with specific anomaly descriptions
- **Automated report generation** with exportable results

### 🖥️ Interactive Dashboard
- **Multi-view interface** with overview, timeline, evidence, and comparison panels
- **Real-time filtering** and sensitivity adjustment
- **Frame-by-frame comparison** at splice points
- **Export capabilities** for charts and comprehensive reports

## 📋 Installation

### Prerequisites
```bash
# Install system dependencies
sudo apt update
sudo apt install ffmpeg exiftool python3-dev build-essential

# For macOS
brew install ffmpeg exiftool
```

### Python Dependencies
```bash
# Install enhanced requirements
pip install -r enhanced_requirements.txt

# Or install specific packages
pip install numpy opencv-python scipy scikit-image ffmpeg-python matplotlib pandas
```

## 🎮 Usage

### Quick Start - Interactive Demo
```bash
# Open the enhanced web interface
python -m http.server 3000
# Navigate to http://localhost:3000/enhanced_index.html
```

### Command Line Analysis
```bash
# Run comprehensive analysis on a video file
python enhanced_analyzer.py path/to/video.mp4

# With custom configuration
python enhanced_analyzer.py path/to/video.mp4 --config config/analysis_settings.json

# Specify output directory
python enhanced_analyzer.py path/to/video.mp4 --output enhanced_analysis_output
```

### Python API
```python
from enhanced_analyzer import EnhancedVideoAnalyzer

# Initialize analyzer
analyzer = EnhancedVideoAnalyzer("video.mp4", output_dir="analysis_results")

# Run comprehensive analysis
def progress_callback(progress, message):
    print(f"Progress: {progress*100:.1f}% - {message}")

report = analyzer.analyze_video(progress_callback)

# Access results
print(f"Detected {len(report['splice_evidence'])} splice points")
for evidence in report['splice_evidence']:
    print(f"Splice at {evidence['start_time']:.1f}s with {evidence['confidence']:.2f} confidence")
```

## 🔧 Configuration

### Analysis Settings
Edit `config/analysis_settings.json` to customize:

```json
{
  "analysis_config": {
    "sampling_rate": 1.0,          // Seconds between samples
    "confidence_threshold": 0.7,    // Minimum confidence for detection
    "anomaly_threshold": 2.0,       // Standard deviations for anomaly
    "parallel_workers": 4           // Number of parallel analysis threads
  },
  "compression_analysis": {
    "jpeg_quality": 95,             // Quality for compression testing
    "dct_analysis": true,           // Enable DCT coefficient analysis
    "entropy_calculation": true     // Calculate image entropy
  },
  "optical_flow_analysis": {
    "method": "lucas_kanade",       // Optical flow method
    "window_size": [15, 15],        // Analysis window size
    "enable_dense_flow": true       // Enable dense flow analysis
  }
}
```

## 📊 Analysis Techniques

### 1. Compression Analysis
- **File Size Discontinuities**: Detects sudden changes in frame compression
- **Quality Metrics**: BRISQUE, Laplacian variance, gradient magnitude
- **DCT Coefficient Analysis**: Examines frequency domain characteristics
- **Compression Artifacts**: Blocking and ringing artifact detection

### 2. Optical Flow Analysis
- **Lucas-Kanade Method**: Sparse feature tracking
- **Dense Flow Analysis**: Pixel-level motion estimation
- **Motion Consistency**: Direction and magnitude consistency checking
- **Temporal Discontinuities**: Frame-to-frame motion analysis

### 3. Color Histogram Analysis
- **Multi-Color Space**: RGB, HSV, LAB analysis
- **Dominant Color Extraction**: K-means clustering for color identification
- **Lighting Change Detection**: Brightness and contrast analysis
- **Color Temperature Estimation**: White balance consistency checking

### 4. Noise Pattern Analysis
- **Noise Variance Estimation**: Laplacian-based noise measurement
- **Texture Analysis**: GLCM and LBP feature extraction
- **Frequency Domain Analysis**: FFT-based signature detection
- **Compression Artifact Detection**: JPEG blocking and ringing

## 📈 Visualization Features

### Interactive Timeline Chart
- **Multi-layer visualization** showing all analysis techniques
- **Anomaly highlighting** with confidence indicators
- **Zoom and pan** for detailed examination
- **Brush selection** for time range analysis
- **Export capabilities** (SVG, PNG)

### Evidence Dashboard
- **Overview panel** with summary statistics
- **Timeline analysis** with interactive controls
- **Evidence details** with confidence scoring
- **Frame comparison** at splice points

### Statistical Analysis
- **Confidence intervals** for all measurements
- **Statistical significance** testing (σ values)
- **Correlation analysis** between techniques
- **Anomaly scoring** with threshold adjustment

## 🎯 Performance Optimization

### Caching System
- **Frame caching** to avoid re-extraction
- **Analysis result caching** for incremental processing
- **Configurable cache size** with automatic cleanup

### Parallel Processing
- **Multi-threaded analysis** across timeline
- **Technique parallelization** for simultaneous processing
- **Progress tracking** with real-time updates
- **Memory management** for large video files

### GPU Acceleration (Optional)
- **OpenCV GPU support** for optical flow
- **CUDA-accelerated** image processing
- **Configurable GPU usage** in settings

## 📋 Output Formats

### Analysis Report (JSON)
```json
{
  "metadata": {
    "video_path": "video.mp4",
    "analysis_timestamp": "2025-01-13T20:53:00Z",
    "video_info": { "duration": 3600, "fps": 30 }
  },
  "summary": {
    "total_samples": 3600,
    "splice_points_detected": 3,
    "highest_confidence": 0.94
  },
  "splice_evidence": [
    {
      "start_time": 23755,
      "end_time": 23765,
      "confidence": 0.94,
      "evidence_types": ["compression_discontinuity", "motion_discontinuity"],
      "statistical_significance": 4.2,
      "visual_artifacts": ["Compression discontinuity: 5.8%"]
    }
  ],
  "timeseries_data": { ... }
}
```

### Time-Series Data (CSV)
```csv
timestamp,compression,optical_flow,histogram,noise,anomaly_score
0.0,0.12,0.08,0.05,0.10,0.09
1.0,0.15,0.09,0.06,0.11,0.10
23760.0,2.85,2.12,0.08,0.15,1.30
```

### HTML Report
- **Interactive visualization** embedded in HTML
- **Self-contained** with all assets included
- **Print-friendly** formatting for documentation
- **Shareable** results with stakeholders

## 🔬 Advanced Features

### Custom Analysis Modules
```python
# Create custom analyzer
class CustomAnalyzer:
    def __init__(self, config):
        self.config = config
    
    def analyze_frame(self, frame, timestamp):
        # Custom analysis logic
        return {
            'confidence': 0.8,
            'evidence_type': 'custom_anomaly',
            'anomaly_score': 1.5,
            'details': { ... }
        }

# Register with framework
analyzer.analyzers['custom'] = CustomAnalyzer(config)
```

### Batch Processing
```python
# Process multiple videos
videos = ['video1.mp4', 'video2.mp4', 'video3.mp4']
results = []

for video in videos:
    analyzer = EnhancedVideoAnalyzer(video)
    result = analyzer.analyze_video()
    results.append(result)

# Generate comparative report
generate_batch_report(results)
```

### Real-time Analysis
```python
# Analyze video stream in real-time
from enhanced_analyzer import StreamAnalyzer

stream_analyzer = StreamAnalyzer()
stream_analyzer.start_analysis('rtmp://stream.url')

# Get real-time alerts
stream_analyzer.on_anomaly_detected(lambda evidence: 
    print(f"Anomaly detected: {evidence}")
)
```

## 🧪 Testing and Validation

### Test Suite
```bash
# Run comprehensive tests
pytest tests/ -v --cov=enhanced_analyzer

# Test specific modules
pytest tests/test_compression_analyzer.py
pytest tests/test_optical_flow_analyzer.py
pytest tests/test_histogram_analyzer.py
pytest tests/test_noise_analyzer.py
```

### Validation Datasets
- **Synthetic splice videos** with known ground truth
- **Real-world manipulation** examples
- **Benchmark comparisons** with existing tools
- **Performance metrics** (precision, recall, F1-score)

## 📚 Documentation

### API Reference
- **Complete function documentation** with examples
- **Parameter descriptions** and valid ranges
- **Return value specifications** with data types
- **Error handling** and exception descriptions

### Tutorials
- **Getting started** guide with examples
- **Advanced usage** patterns and best practices
- **Custom module development** tutorial
- **Performance optimization** guide

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone https://github.com/codegen-sh/forensic-analysis.git
cd forensic-analysis

# Install development dependencies
pip install -r enhanced_requirements.txt
pip install -e .

# Run tests
pytest tests/
```

### Code Style
- **Black** formatting for Python code
- **Flake8** linting for code quality
- **MyPy** type checking for reliability
- **Comprehensive** docstrings and comments

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenCV** community for computer vision tools
- **SciPy** ecosystem for scientific computing
- **D3.js** for interactive visualizations
- **FFmpeg** for video processing capabilities

## 📞 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Comprehensive guides and API reference
- **Community**: Join discussions and share experiences
- **Professional**: Contact for enterprise support and consulting

---

**Enhanced Forensic Video Analysis Framework** - Advancing the state of digital forensics through multi-dimensional analysis and statistical rigor.

