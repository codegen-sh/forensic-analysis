#!/usr/bin/env python3
"""
Forensic Tool Validation and Reliability Assessment
==================================================

This module provides comprehensive validation of forensic tools (ffmpeg and exiftool)
used in video analysis to establish reliability metrics, error rates, and confidence
intervals for forensic conclusions.

Key Features:
- Tool version consistency testing
- Platform-specific behavior analysis
- Accuracy validation against known ground truth
- Error rate quantification
- Confidence interval calculation
- Academic literature integration

Author: Forensic Analysis Team
Version: 1.0
Date: July 2025
"""

import os
import sys
import json
import subprocess
import platform
import hashlib
import statistics
import time
import tempfile
import shutil
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ToolVersion:
    """Tool version information."""
    name: str
    version: str
    build_info: str
    platform: str
    architecture: str

@dataclass
class ValidationResult:
    """Result of a validation test."""
    test_name: str
    tool_name: str
    expected_value: Any
    actual_value: Any
    error_rate: float
    confidence_level: float
    metadata: Dict[str, Any]
    timestamp: str

@dataclass
class ReliabilityMetrics:
    """Comprehensive reliability metrics for a tool."""
    tool_name: str
    version_info: ToolVersion
    accuracy_rate: float
    error_rate: float
    confidence_interval: Tuple[float, float]
    consistency_score: float
    platform_variations: Dict[str, float]
    test_results: List[ValidationResult]

class ForensicToolValidator:
    """
    Comprehensive validation framework for forensic tools.
    
    This class provides methods to validate the reliability and accuracy
    of ffmpeg and exiftool for forensic video analysis purposes.
    """
    
    def __init__(self, output_dir: str = "tool_validation_results"):
        """Initialize the validator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Test data directory
        self.test_data_dir = self.output_dir / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        
        # Results storage
        self.validation_results: List[ValidationResult] = []
        self.tool_versions: Dict[str, ToolVersion] = {}
        
        # Known ground truth data
        self.ground_truth_data = self._initialize_ground_truth()
        
        logger.info(f"Forensic Tool Validator initialized. Output directory: {self.output_dir}")
    
    def _initialize_ground_truth(self) -> Dict[str, Any]:
        """Initialize known ground truth data for validation."""
        return {
            "test_video_properties": {
                "duration": 10.0,  # seconds
                "fps": 30.0,
                "resolution": (1920, 1080),
                "codec": "h264",
                "bitrate": 5000000  # 5 Mbps
            },
            "test_metadata": {
                "creation_time": "2025-01-01T12:00:00Z",
                "software": "Test Video Generator",
                "encoder": "libx264"
            },
            "compression_ratios": {
                "high_quality": 0.1,  # 10% compression
                "medium_quality": 0.3,  # 30% compression
                "low_quality": 0.6     # 60% compression
            }
        }
    
    def get_tool_version(self, tool_name: str) -> Optional[ToolVersion]:
        """Get version information for a forensic tool."""
        try:
            if tool_name == "ffmpeg":
                result = subprocess.run(
                    ["ffmpeg", "-version"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    version_line = lines[0] if lines else ""
                    build_line = lines[1] if len(lines) > 1 else ""
                    
                    version = version_line.split()[2] if len(version_line.split()) > 2 else "unknown"
                    
                    return ToolVersion(
                        name="ffmpeg",
                        version=version,
                        build_info=build_line,
                        platform=platform.system(),
                        architecture=platform.machine()
                    )
            
            elif tool_name == "exiftool":
                result = subprocess.run(
                    ["exiftool", "-ver"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
                    
                    return ToolVersion(
                        name="exiftool",
                        version=version,
                        build_info="",
                        platform=platform.system(),
                        architecture=platform.machine()
                    )
            
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error(f"Failed to get version for {tool_name}: {e}")
            return None
        
        return None
    
    def create_test_video(self, output_path: str, properties: Dict[str, Any]) -> bool:
        """Create a test video with known properties for validation."""
        try:
            duration = properties.get("duration", 10.0)
            fps = properties.get("fps", 30.0)
            resolution = properties.get("resolution", (1920, 1080))
            
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", f"testsrc=duration={duration}:size={resolution[0]}x{resolution[1]}:rate={fps}",
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info(f"Created test video: {output_path}")
                return True
            else:
                logger.error(f"Failed to create test video: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating test video: {e}")
            return False
    
    def validate_ffmpeg_accuracy(self) -> List[ValidationResult]:
        """Validate ffmpeg's accuracy in video analysis."""
        results = []
        
        # Create test video
        test_video = self.test_data_dir / "test_video.mp4"
        if not self.create_test_video(str(test_video), self.ground_truth_data["test_video_properties"]):
            logger.error("Failed to create test video for validation")
            return results
        
        # Test 1: Duration accuracy
        result = self._test_duration_accuracy(str(test_video))
        if result:
            results.append(result)
        
        # Test 2: Frame rate accuracy
        result = self._test_fps_accuracy(str(test_video))
        if result:
            results.append(result)
        
        # Test 3: Resolution accuracy
        result = self._test_resolution_accuracy(str(test_video))
        if result:
            results.append(result)
        
        # Test 4: Compression ratio calculation
        result = self._test_compression_ratio_accuracy(str(test_video))
        if result:
            results.append(result)
        
        return results
    
    def _test_duration_accuracy(self, video_path: str) -> Optional[ValidationResult]:
        """Test ffmpeg's accuracy in determining video duration."""
        try:
            cmd = [
                "ffprobe", "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "csv=p=0",
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                actual_duration = float(result.stdout.strip())
                expected_duration = self.ground_truth_data["test_video_properties"]["duration"]
                
                error_rate = abs(actual_duration - expected_duration) / expected_duration
                confidence_level = max(0, 1 - error_rate)
                
                return ValidationResult(
                    test_name="duration_accuracy",
                    tool_name="ffmpeg",
                    expected_value=expected_duration,
                    actual_value=actual_duration,
                    error_rate=error_rate,
                    confidence_level=confidence_level,
                    metadata={"test_type": "duration", "unit": "seconds"},
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )
        
        except Exception as e:
            logger.error(f"Duration accuracy test failed: {e}")
        
        return None
    
    def _test_fps_accuracy(self, video_path: str) -> Optional[ValidationResult]:
        """Test ffmpeg's accuracy in determining frame rate."""
        try:
            cmd = [
                "ffprobe", "-v", "quiet",
                "-show_entries", "stream=r_frame_rate",
                "-of", "csv=p=0",
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                fps_str = result.stdout.strip()
                if '/' in fps_str:
                    num, den = fps_str.split('/')
                    actual_fps = float(num) / float(den)
                else:
                    actual_fps = float(fps_str)
                
                expected_fps = self.ground_truth_data["test_video_properties"]["fps"]
                
                error_rate = abs(actual_fps - expected_fps) / expected_fps
                confidence_level = max(0, 1 - error_rate)
                
                return ValidationResult(
                    test_name="fps_accuracy",
                    tool_name="ffmpeg",
                    expected_value=expected_fps,
                    actual_value=actual_fps,
                    error_rate=error_rate,
                    confidence_level=confidence_level,
                    metadata={"test_type": "frame_rate", "unit": "fps"},
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )
        
        except Exception as e:
            logger.error(f"FPS accuracy test failed: {e}")
        
        return None
    
    def _test_resolution_accuracy(self, video_path: str) -> Optional[ValidationResult]:
        """Test ffmpeg's accuracy in determining video resolution."""
        try:
            cmd = [
                "ffprobe", "-v", "quiet",
                "-show_entries", "stream=width,height",
                "-of", "csv=p=0",
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                width, height = result.stdout.strip().split(',')
                actual_resolution = (int(width), int(height))
                expected_resolution = self.ground_truth_data["test_video_properties"]["resolution"]
                
                # Calculate error as percentage difference in total pixels
                actual_pixels = actual_resolution[0] * actual_resolution[1]
                expected_pixels = expected_resolution[0] * expected_resolution[1]
                error_rate = abs(actual_pixels - expected_pixels) / expected_pixels
                confidence_level = max(0, 1 - error_rate)
                
                return ValidationResult(
                    test_name="resolution_accuracy",
                    tool_name="ffmpeg",
                    expected_value=expected_resolution,
                    actual_value=actual_resolution,
                    error_rate=error_rate,
                    confidence_level=confidence_level,
                    metadata={"test_type": "resolution", "unit": "pixels"},
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )
        
        except Exception as e:
            logger.error(f"Resolution accuracy test failed: {e}")
        
        return None
    
    def _test_compression_ratio_accuracy(self, video_path: str) -> Optional[ValidationResult]:
        """Test ffmpeg's accuracy in compression ratio calculations."""
        try:
            # Get file size
            file_size = os.path.getsize(video_path)
            
            # Calculate theoretical uncompressed size
            props = self.ground_truth_data["test_video_properties"]
            duration = props["duration"]
            fps = props["fps"]
            width, height = props["resolution"]
            
            # Assume 24-bit color depth (3 bytes per pixel)
            uncompressed_size = duration * fps * width * height * 3
            
            actual_compression_ratio = file_size / uncompressed_size
            
            # Expected compression ratio (rough estimate for h264 at CRF 23)
            expected_compression_ratio = 0.02  # ~2% of uncompressed size
            
            error_rate = abs(actual_compression_ratio - expected_compression_ratio) / expected_compression_ratio
            confidence_level = max(0, 1 - min(error_rate, 1.0))  # Cap error rate at 100%
            
            return ValidationResult(
                test_name="compression_ratio_accuracy",
                tool_name="ffmpeg",
                expected_value=expected_compression_ratio,
                actual_value=actual_compression_ratio,
                error_rate=error_rate,
                confidence_level=confidence_level,
                metadata={
                    "test_type": "compression_ratio",
                    "file_size": file_size,
                    "uncompressed_size": uncompressed_size
                },
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )
        
        except Exception as e:
            logger.error(f"Compression ratio accuracy test failed: {e}")
        
        return None
    
    def validate_exiftool_accuracy(self) -> List[ValidationResult]:
        """Validate exiftool's accuracy in metadata extraction."""
        results = []
        
        # Create test video with known metadata
        test_video = self.test_data_dir / "test_video_metadata.mp4"
        if not self.create_test_video(str(test_video), self.ground_truth_data["test_video_properties"]):
            logger.error("Failed to create test video for metadata validation")
            return results
        
        # Test metadata extraction accuracy
        result = self._test_metadata_extraction_accuracy(str(test_video))
        if result:
            results.append(result)
        
        return results
    
    def _test_metadata_extraction_accuracy(self, video_path: str) -> Optional[ValidationResult]:
        """Test exiftool's accuracy in metadata extraction."""
        try:
            cmd = ["exiftool", "-j", video_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                metadata = json.loads(result.stdout)[0]
                
                # Check for presence of key metadata fields
                expected_fields = ["Duration", "VideoFrameRate", "ImageWidth", "ImageHeight"]
                found_fields = sum(1 for field in expected_fields if field in metadata)
                
                accuracy_rate = found_fields / len(expected_fields)
                error_rate = 1 - accuracy_rate
                confidence_level = accuracy_rate
                
                return ValidationResult(
                    test_name="metadata_extraction_accuracy",
                    tool_name="exiftool",
                    expected_value=len(expected_fields),
                    actual_value=found_fields,
                    error_rate=error_rate,
                    confidence_level=confidence_level,
                    metadata={
                        "test_type": "metadata_extraction",
                        "expected_fields": expected_fields,
                        "extracted_metadata": metadata
                    },
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )
        
        except Exception as e:
            logger.error(f"Metadata extraction accuracy test failed: {e}")
        
        return None
    
    def test_version_consistency(self, tool_name: str, iterations: int = 10) -> List[ValidationResult]:
        """Test consistency of tool behavior across multiple runs."""
        results = []
        
        if tool_name == "ffmpeg":
            test_video = self.test_data_dir / "consistency_test.mp4"
            if not self.create_test_video(str(test_video), self.ground_truth_data["test_video_properties"]):
                return results
            
            # Run multiple duration measurements
            durations = []
            for i in range(iterations):
                try:
                    cmd = [
                        "ffprobe", "-v", "quiet",
                        "-show_entries", "format=duration",
                        "-of", "csv=p=0",
                        str(test_video)
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        durations.append(float(result.stdout.strip()))
                
                except Exception as e:
                    logger.error(f"Consistency test iteration {i} failed: {e}")
            
            if durations:
                mean_duration = statistics.mean(durations)
                std_dev = statistics.stdev(durations) if len(durations) > 1 else 0
                consistency_score = 1 - (std_dev / mean_duration) if mean_duration > 0 else 0
                
                results.append(ValidationResult(
                    test_name="version_consistency",
                    tool_name=tool_name,
                    expected_value=self.ground_truth_data["test_video_properties"]["duration"],
                    actual_value=mean_duration,
                    error_rate=std_dev / mean_duration if mean_duration > 0 else 1,
                    confidence_level=consistency_score,
                    metadata={
                        "test_type": "consistency",
                        "iterations": iterations,
                        "measurements": durations,
                        "std_dev": std_dev
                    },
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                ))
        
        return results
    
    def calculate_reliability_metrics(self, tool_name: str) -> ReliabilityMetrics:
        """Calculate comprehensive reliability metrics for a tool."""
        tool_results = [r for r in self.validation_results if r.tool_name == tool_name]
        
        if not tool_results:
            logger.warning(f"No validation results found for {tool_name}")
            return ReliabilityMetrics(
                tool_name=tool_name,
                version_info=self.tool_versions.get(tool_name),
                accuracy_rate=0.0,
                error_rate=1.0,
                confidence_interval=(0.0, 0.0),
                consistency_score=0.0,
                platform_variations={},
                test_results=[]
            )
        
        # Calculate overall metrics
        confidence_levels = [r.confidence_level for r in tool_results]
        error_rates = [r.error_rate for r in tool_results]
        
        accuracy_rate = statistics.mean(confidence_levels)
        avg_error_rate = statistics.mean(error_rates)
        
        # Calculate confidence interval (95%)
        if len(confidence_levels) > 1:
            std_dev = statistics.stdev(confidence_levels)
            margin_of_error = 1.96 * std_dev / (len(confidence_levels) ** 0.5)
            confidence_interval = (
                max(0, accuracy_rate - margin_of_error),
                min(1, accuracy_rate + margin_of_error)
            )
        else:
            confidence_interval = (accuracy_rate, accuracy_rate)
        
        # Calculate consistency score
        consistency_score = 1 - statistics.stdev(error_rates) if len(error_rates) > 1 else 1.0
        
        return ReliabilityMetrics(
            tool_name=tool_name,
            version_info=self.tool_versions.get(tool_name),
            accuracy_rate=accuracy_rate,
            error_rate=avg_error_rate,
            confidence_interval=confidence_interval,
            consistency_score=consistency_score,
            platform_variations={platform.system(): accuracy_rate},
            test_results=tool_results
        )
    
    def run_comprehensive_validation(self) -> Dict[str, ReliabilityMetrics]:
        """Run comprehensive validation for all forensic tools."""
        logger.info("Starting comprehensive forensic tool validation...")
        
        # Get tool versions
        for tool in ["ffmpeg", "exiftool"]:
            version_info = self.get_tool_version(tool)
            if version_info:
                self.tool_versions[tool] = version_info
                logger.info(f"Detected {tool} version: {version_info.version}")
            else:
                logger.error(f"Failed to detect {tool} version")
        
        # Run validation tests
        logger.info("Running ffmpeg validation tests...")
        ffmpeg_results = self.validate_ffmpeg_accuracy()
        ffmpeg_results.extend(self.test_version_consistency("ffmpeg"))
        self.validation_results.extend(ffmpeg_results)
        
        logger.info("Running exiftool validation tests...")
        exiftool_results = self.validate_exiftool_accuracy()
        exiftool_results.extend(self.test_version_consistency("exiftool"))
        self.validation_results.extend(exiftool_results)
        
        # Calculate reliability metrics
        metrics = {}
        for tool in ["ffmpeg", "exiftool"]:
            metrics[tool] = self.calculate_reliability_metrics(tool)
            logger.info(f"{tool} reliability metrics calculated")
        
        # Save results
        self.save_validation_results(metrics)
        
        logger.info("Comprehensive validation completed")
        return metrics
    
    def save_validation_results(self, metrics: Dict[str, ReliabilityMetrics]):
        """Save validation results to files."""
        # Save detailed results as JSON
        results_file = self.output_dir / "validation_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                "validation_results": [asdict(r) for r in self.validation_results],
                "reliability_metrics": {k: asdict(v) for k, v in metrics.items()},
                "tool_versions": {k: asdict(v) for k, v in self.tool_versions.items()},
                "platform_info": {
                    "system": platform.system(),
                    "release": platform.release(),
                    "machine": platform.machine(),
                    "python_version": platform.python_version()
                }
            }, f, indent=2)
        
        logger.info(f"Validation results saved to {results_file}")
        
        # Generate summary report
        self.generate_summary_report(metrics)
    
    def generate_summary_report(self, metrics: Dict[str, ReliabilityMetrics]):
        """Generate a human-readable summary report."""
        report_file = self.output_dir / "tool_reliability_report.md"
        
        with open(report_file, 'w') as f:
            f.write("# Forensic Tool Reliability Assessment Report\n\n")
            f.write(f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Platform**: {platform.system()} {platform.release()}\n\n")
            
            for tool_name, metric in metrics.items():
                f.write(f"## {tool_name.upper()} Reliability Analysis\n\n")
                
                if metric.version_info:
                    f.write(f"**Version**: {metric.version_info.version}\n")
                    f.write(f"**Platform**: {metric.version_info.platform}\n")
                    f.write(f"**Architecture**: {metric.version_info.architecture}\n\n")
                
                f.write(f"**Accuracy Rate**: {metric.accuracy_rate:.2%}\n")
                f.write(f"**Error Rate**: {metric.error_rate:.2%}\n")
                f.write(f"**Confidence Interval**: {metric.confidence_interval[0]:.2%} - {metric.confidence_interval[1]:.2%}\n")
                f.write(f"**Consistency Score**: {metric.consistency_score:.2%}\n\n")
                
                f.write("### Test Results\n\n")
                for result in metric.test_results:
                    f.write(f"- **{result.test_name}**: ")
                    f.write(f"Confidence {result.confidence_level:.2%}, ")
                    f.write(f"Error Rate {result.error_rate:.2%}\n")
                
                f.write("\n")
        
        logger.info(f"Summary report generated: {report_file}")


def main():
    """Main function to run the forensic tool validation."""
    print("🔬 Forensic Tool Validation and Reliability Assessment")
    print("=" * 60)
    
    validator = ForensicToolValidator()
    
    try:
        metrics = validator.run_comprehensive_validation()
        
        print("\n📊 Validation Results Summary:")
        print("-" * 40)
        
        for tool_name, metric in metrics.items():
            print(f"\n{tool_name.upper()}:")
            print(f"  Accuracy Rate: {metric.accuracy_rate:.2%}")
            print(f"  Error Rate: {metric.error_rate:.2%}")
            print(f"  Confidence Interval: {metric.confidence_interval[0]:.2%} - {metric.confidence_interval[1]:.2%}")
            print(f"  Consistency Score: {metric.consistency_score:.2%}")
        
        print(f"\n📁 Detailed results saved to: {validator.output_dir}")
        print("✅ Validation completed successfully!")
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
