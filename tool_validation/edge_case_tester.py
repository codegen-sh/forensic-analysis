#!/usr/bin/env python3
"""
Edge Case and Corrupted File Testing for Forensic Tools
======================================================

This module tests forensic tools (ffmpeg and exiftool) against edge cases,
corrupted files, and unusual video formats to assess their robustness
and reliability in forensic contexts.

Key Features:
- Corrupted file handling tests
- Unusual format compatibility tests
- Edge case scenario validation
- Error handling assessment
- Robustness scoring

Author: Forensic Analysis Team
Version: 1.0
Date: July 2025
"""

import os
import sys
import json
import subprocess
import tempfile
import random
import struct
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class EdgeCaseResult:
    """Result of an edge case test."""
    test_name: str
    tool_name: str
    test_type: str
    input_description: str
    expected_behavior: str
    actual_behavior: str
    success: bool
    error_message: Optional[str]
    robustness_score: float
    metadata: Dict[str, Any]

class EdgeCaseTester:
    """
    Test forensic tools against edge cases and corrupted files.
    
    This class creates various problematic video files and tests
    how well forensic tools handle them.
    """
    
    def __init__(self, output_dir: str = "edge_case_results"):
        """Initialize the edge case tester."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Test files directory
        self.test_files_dir = self.output_dir / "test_files"
        self.test_files_dir.mkdir(exist_ok=True)
        
        # Results storage
        self.edge_case_results: List[EdgeCaseResult] = []
        
        logger.info(f"Edge Case Tester initialized. Output directory: {self.output_dir}")
    
    def create_corrupted_video(self, corruption_type: str) -> Optional[str]:
        """Create a corrupted video file for testing."""
        try:
            # First create a valid test video
            base_video = self.test_files_dir / "base_test.mp4"
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", "testsrc=duration=5:size=640x480:rate=30",
                "-c:v", "libx264", "-preset", "ultrafast",
                str(base_video)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                logger.error(f"Failed to create base video: {result.stderr}")
                return None
            
            # Now corrupt it based on type
            corrupted_file = self.test_files_dir / f"corrupted_{corruption_type}.mp4"
            
            if corruption_type == "header_corruption":
                return self._corrupt_header(str(base_video), str(corrupted_file))
            elif corruption_type == "metadata_corruption":
                return self._corrupt_metadata(str(base_video), str(corrupted_file))
            elif corruption_type == "partial_truncation":
                return self._truncate_file(str(base_video), str(corrupted_file))
            elif corruption_type == "random_bytes":
                return self._inject_random_bytes(str(base_video), str(corrupted_file))
            elif corruption_type == "invalid_atoms":
                return self._corrupt_atoms(str(base_video), str(corrupted_file))
            
        except Exception as e:
            logger.error(f"Failed to create corrupted video ({corruption_type}): {e}")
        
        return None
    
    def _corrupt_header(self, source: str, target: str) -> Optional[str]:
        """Corrupt the file header."""
        try:
            with open(source, 'rb') as src, open(target, 'wb') as dst:
                data = src.read()
                # Corrupt first 32 bytes
                corrupted_header = bytearray(data[:32])
                for i in range(0, 32, 4):
                    corrupted_header[i:i+4] = b'\x00\x00\x00\x00'
                dst.write(corrupted_header + data[32:])
            return target
        except Exception as e:
            logger.error(f"Header corruption failed: {e}")
            return None
    
    def _corrupt_metadata(self, source: str, target: str) -> Optional[str]:
        """Corrupt metadata sections."""
        try:
            with open(source, 'rb') as src, open(target, 'wb') as dst:
                data = bytearray(src.read())
                # Find and corrupt 'moov' atom
                moov_pos = data.find(b'moov')
                if moov_pos > 0:
                    # Corrupt 100 bytes after moov
                    for i in range(moov_pos + 4, min(moov_pos + 104, len(data))):
                        data[i] = random.randint(0, 255)
                dst.write(data)
            return target
        except Exception as e:
            logger.error(f"Metadata corruption failed: {e}")
            return None
    
    def _truncate_file(self, source: str, target: str) -> Optional[str]:
        """Truncate file at random position."""
        try:
            with open(source, 'rb') as src:
                data = src.read()
            
            # Truncate at 70% of original size
            truncate_pos = int(len(data) * 0.7)
            
            with open(target, 'wb') as dst:
                dst.write(data[:truncate_pos])
            
            return target
        except Exception as e:
            logger.error(f"File truncation failed: {e}")
            return None
    
    def _inject_random_bytes(self, source: str, target: str) -> Optional[str]:
        """Inject random bytes throughout the file."""
        try:
            with open(source, 'rb') as src:
                data = bytearray(src.read())
            
            # Inject random bytes at 10 random positions
            for _ in range(10):
                pos = random.randint(100, len(data) - 100)
                data[pos:pos+4] = bytes([random.randint(0, 255) for _ in range(4)])
            
            with open(target, 'wb') as dst:
                dst.write(data)
            
            return target
        except Exception as e:
            logger.error(f"Random byte injection failed: {e}")
            return None
    
    def _corrupt_atoms(self, source: str, target: str) -> Optional[str]:
        """Corrupt MP4 atom structure."""
        try:
            with open(source, 'rb') as src:
                data = bytearray(src.read())
            
            # Find and corrupt atom size fields
            pos = 0
            while pos < len(data) - 8:
                # Read atom size (first 4 bytes)
                atom_size = struct.unpack('>I', data[pos:pos+4])[0]
                if atom_size > 8 and pos + atom_size <= len(data):
                    # Corrupt the size field
                    corrupted_size = atom_size + random.randint(-1000, 1000)
                    data[pos:pos+4] = struct.pack('>I', max(8, corrupted_size))
                    pos += atom_size
                else:
                    break
            
            with open(target, 'wb') as dst:
                dst.write(data)
            
            return target
        except Exception as e:
            logger.error(f"Atom corruption failed: {e}")
            return None
    
    def test_ffmpeg_robustness(self) -> List[EdgeCaseResult]:
        """Test ffmpeg's robustness against corrupted files."""
        results = []
        
        corruption_types = [
            "header_corruption",
            "metadata_corruption", 
            "partial_truncation",
            "random_bytes",
            "invalid_atoms"
        ]
        
        for corruption_type in corruption_types:
            logger.info(f"Testing ffmpeg with {corruption_type}")
            
            # Create corrupted file
            corrupted_file = self.create_corrupted_video(corruption_type)
            if not corrupted_file:
                continue
            
            # Test ffprobe analysis
            result = self._test_ffprobe_on_corrupted(corrupted_file, corruption_type)
            if result:
                results.append(result)
            
            # Test ffmpeg processing
            result = self._test_ffmpeg_processing_corrupted(corrupted_file, corruption_type)
            if result:
                results.append(result)
        
        return results
    
    def _test_ffprobe_on_corrupted(self, file_path: str, corruption_type: str) -> Optional[EdgeCaseResult]:
        """Test ffprobe on corrupted file."""
        try:
            cmd = [
                "ffprobe", "-v", "quiet",
                "-show_entries", "format=duration,size",
                "-of", "json",
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Analyze behavior
            if result.returncode == 0:
                # Tool handled corruption gracefully
                try:
                    data = json.loads(result.stdout)
                    behavior = "Graceful handling - extracted partial data"
                    success = True
                    robustness_score = 0.8
                except json.JSONDecodeError:
                    behavior = "Returned data but invalid JSON"
                    success = False
                    robustness_score = 0.4
            else:
                # Tool failed
                if "Invalid data" in result.stderr or "corrupt" in result.stderr.lower():
                    behavior = "Proper error detection"
                    success = True
                    robustness_score = 0.6
                else:
                    behavior = "Unexpected failure"
                    success = False
                    robustness_score = 0.2
            
            return EdgeCaseResult(
                test_name=f"ffprobe_{corruption_type}",
                tool_name="ffmpeg",
                test_type="corruption_handling",
                input_description=f"Video with {corruption_type}",
                expected_behavior="Graceful error handling or partial data extraction",
                actual_behavior=behavior,
                success=success,
                error_message=result.stderr if result.stderr else None,
                robustness_score=robustness_score,
                metadata={
                    "corruption_type": corruption_type,
                    "return_code": result.returncode,
                    "stdout_length": len(result.stdout),
                    "stderr_length": len(result.stderr)
                }
            )
        
        except subprocess.TimeoutExpired:
            return EdgeCaseResult(
                test_name=f"ffprobe_{corruption_type}",
                tool_name="ffmpeg",
                test_type="corruption_handling",
                input_description=f"Video with {corruption_type}",
                expected_behavior="Graceful error handling or partial data extraction",
                actual_behavior="Timeout - tool hung",
                success=False,
                error_message="Process timeout",
                robustness_score=0.1,
                metadata={"corruption_type": corruption_type, "timeout": True}
            )
        except Exception as e:
            logger.error(f"ffprobe test failed: {e}")
            return None
    
    def _test_ffmpeg_processing_corrupted(self, file_path: str, corruption_type: str) -> Optional[EdgeCaseResult]:
        """Test ffmpeg processing of corrupted file."""
        try:
            output_file = self.test_files_dir / f"processed_{corruption_type}.mp4"
            cmd = [
                "ffmpeg", "-y", "-v", "quiet",
                "-i", file_path,
                "-c:v", "libx264", "-t", "1",  # Only process 1 second
                str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Analyze behavior
            if result.returncode == 0 and os.path.exists(output_file):
                behavior = "Successfully processed corrupted input"
                success = True
                robustness_score = 0.9
            elif result.returncode != 0 and "corrupt" in result.stderr.lower():
                behavior = "Proper corruption detection"
                success = True
                robustness_score = 0.7
            else:
                behavior = "Failed to handle corruption properly"
                success = False
                robustness_score = 0.3
            
            return EdgeCaseResult(
                test_name=f"ffmpeg_process_{corruption_type}",
                tool_name="ffmpeg",
                test_type="corruption_processing",
                input_description=f"Video with {corruption_type}",
                expected_behavior="Graceful processing or proper error detection",
                actual_behavior=behavior,
                success=success,
                error_message=result.stderr if result.stderr else None,
                robustness_score=robustness_score,
                metadata={
                    "corruption_type": corruption_type,
                    "return_code": result.returncode,
                    "output_created": os.path.exists(output_file)
                }
            )
        
        except subprocess.TimeoutExpired:
            return EdgeCaseResult(
                test_name=f"ffmpeg_process_{corruption_type}",
                tool_name="ffmpeg",
                test_type="corruption_processing",
                input_description=f"Video with {corruption_type}",
                expected_behavior="Graceful processing or proper error detection",
                actual_behavior="Timeout - processing hung",
                success=False,
                error_message="Process timeout",
                robustness_score=0.1,
                metadata={"corruption_type": corruption_type, "timeout": True}
            )
        except Exception as e:
            logger.error(f"ffmpeg processing test failed: {e}")
            return None
    
    def test_exiftool_robustness(self) -> List[EdgeCaseResult]:
        """Test exiftool's robustness against corrupted files."""
        results = []
        
        corruption_types = [
            "header_corruption",
            "metadata_corruption",
            "partial_truncation",
            "random_bytes"
        ]
        
        for corruption_type in corruption_types:
            logger.info(f"Testing exiftool with {corruption_type}")
            
            # Create corrupted file
            corrupted_file = self.create_corrupted_video(corruption_type)
            if not corrupted_file:
                continue
            
            # Test metadata extraction
            result = self._test_exiftool_on_corrupted(corrupted_file, corruption_type)
            if result:
                results.append(result)
        
        return results
    
    def _test_exiftool_on_corrupted(self, file_path: str, corruption_type: str) -> Optional[EdgeCaseResult]:
        """Test exiftool on corrupted file."""
        try:
            cmd = ["exiftool", "-j", "-q", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Analyze behavior
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    if data and len(data) > 0:
                        behavior = "Extracted partial metadata despite corruption"
                        success = True
                        robustness_score = 0.8
                    else:
                        behavior = "No metadata extracted"
                        success = False
                        robustness_score = 0.4
                except json.JSONDecodeError:
                    behavior = "Invalid JSON output"
                    success = False
                    robustness_score = 0.3
            else:
                if result.stderr and ("corrupt" in result.stderr.lower() or "invalid" in result.stderr.lower()):
                    behavior = "Proper corruption detection"
                    success = True
                    robustness_score = 0.6
                else:
                    behavior = "Unexpected failure"
                    success = False
                    robustness_score = 0.2
            
            return EdgeCaseResult(
                test_name=f"exiftool_{corruption_type}",
                tool_name="exiftool",
                test_type="corruption_handling",
                input_description=f"Video with {corruption_type}",
                expected_behavior="Graceful error handling or partial metadata extraction",
                actual_behavior=behavior,
                success=success,
                error_message=result.stderr if result.stderr else None,
                robustness_score=robustness_score,
                metadata={
                    "corruption_type": corruption_type,
                    "return_code": result.returncode,
                    "stdout_length": len(result.stdout),
                    "stderr_length": len(result.stderr)
                }
            )
        
        except subprocess.TimeoutExpired:
            return EdgeCaseResult(
                test_name=f"exiftool_{corruption_type}",
                tool_name="exiftool",
                test_type="corruption_handling",
                input_description=f"Video with {corruption_type}",
                expected_behavior="Graceful error handling or partial metadata extraction",
                actual_behavior="Timeout - tool hung",
                success=False,
                error_message="Process timeout",
                robustness_score=0.1,
                metadata={"corruption_type": corruption_type, "timeout": True}
            )
        except Exception as e:
            logger.error(f"exiftool test failed: {e}")
            return None
    
    def test_unusual_formats(self) -> List[EdgeCaseResult]:
        """Test tools with unusual but valid video formats."""
        results = []
        
        # Test with very short video
        result = self._test_minimal_duration_video()
        if result:
            results.extend(result)
        
        # Test with unusual resolutions
        result = self._test_unusual_resolutions()
        if result:
            results.extend(result)
        
        # Test with unusual frame rates
        result = self._test_unusual_framerates()
        if result:
            results.extend(result)
        
        return results
    
    def _test_minimal_duration_video(self) -> List[EdgeCaseResult]:
        """Test with extremely short video."""
        results = []
        
        try:
            # Create 0.1 second video
            test_file = self.test_files_dir / "minimal_duration.mp4"
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", "testsrc=duration=0.1:size=320x240:rate=30",
                "-c:v", "libx264", str(test_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return results
            
            # Test ffprobe
            cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(test_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            success = result.returncode == 0 and result.stdout.strip()
            robustness_score = 0.9 if success else 0.3
            
            results.append(EdgeCaseResult(
                test_name="minimal_duration_ffprobe",
                tool_name="ffmpeg",
                test_type="unusual_format",
                input_description="0.1 second video",
                expected_behavior="Accurate duration measurement",
                actual_behavior="Success" if success else "Failed",
                success=success,
                error_message=result.stderr if result.stderr else None,
                robustness_score=robustness_score,
                metadata={"duration": result.stdout.strip() if success else None}
            ))
            
            # Test exiftool
            cmd = ["exiftool", "-j", "-q", str(test_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            success = result.returncode == 0
            robustness_score = 0.9 if success else 0.3
            
            results.append(EdgeCaseResult(
                test_name="minimal_duration_exiftool",
                tool_name="exiftool",
                test_type="unusual_format",
                input_description="0.1 second video",
                expected_behavior="Metadata extraction",
                actual_behavior="Success" if success else "Failed",
                success=success,
                error_message=result.stderr if result.stderr else None,
                robustness_score=robustness_score,
                metadata={"metadata_extracted": bool(result.stdout.strip())}
            ))
        
        except Exception as e:
            logger.error(f"Minimal duration test failed: {e}")
        
        return results
    
    def _test_unusual_resolutions(self) -> List[EdgeCaseResult]:
        """Test with unusual video resolutions."""
        results = []
        
        unusual_resolutions = [
            (1, 1),      # Minimal resolution
            (3840, 2160), # 4K
            (7680, 4320), # 8K
            (1920, 1),    # Extreme aspect ratio
        ]
        
        for width, height in unusual_resolutions:
            try:
                test_file = self.test_files_dir / f"resolution_{width}x{height}.mp4"
                cmd = [
                    "ffmpeg", "-y", "-f", "lavfi",
                    "-i", f"testsrc=duration=1:size={width}x{height}:rate=30",
                    "-c:v", "libx264", "-preset", "ultrafast",
                    str(test_file)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if result.returncode != 0:
                    continue
                
                # Test resolution detection
                cmd = ["ffprobe", "-v", "quiet", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(test_file)]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                success = result.returncode == 0
                if success:
                    detected = result.stdout.strip().split(',')
                    accuracy = detected == [str(width), str(height)]
                    robustness_score = 0.9 if accuracy else 0.6
                else:
                    robustness_score = 0.3
                
                results.append(EdgeCaseResult(
                    test_name=f"unusual_resolution_{width}x{height}",
                    tool_name="ffmpeg",
                    test_type="unusual_format",
                    input_description=f"{width}x{height} resolution video",
                    expected_behavior="Accurate resolution detection",
                    actual_behavior=f"Detected: {result.stdout.strip()}" if success else "Failed",
                    success=success,
                    error_message=result.stderr if result.stderr else None,
                    robustness_score=robustness_score,
                    metadata={"expected_resolution": (width, height), "detected_resolution": detected if success else None}
                ))
            
            except Exception as e:
                logger.error(f"Unusual resolution test failed for {width}x{height}: {e}")
        
        return results
    
    def _test_unusual_framerates(self) -> List[EdgeCaseResult]:
        """Test with unusual frame rates."""
        results = []
        
        unusual_framerates = [0.5, 1, 120, 240]  # Very low and very high frame rates
        
        for fps in unusual_framerates:
            try:
                test_file = self.test_files_dir / f"framerate_{fps}fps.mp4"
                cmd = [
                    "ffmpeg", "-y", "-f", "lavfi",
                    "-i", f"testsrc=duration=2:size=320x240:rate={fps}",
                    "-c:v", "libx264", "-preset", "ultrafast",
                    str(test_file)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if result.returncode != 0:
                    continue
                
                # Test frame rate detection
                cmd = ["ffprobe", "-v", "quiet", "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", str(test_file)]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                success = result.returncode == 0
                robustness_score = 0.9 if success else 0.3
                
                results.append(EdgeCaseResult(
                    test_name=f"unusual_framerate_{fps}fps",
                    tool_name="ffmpeg",
                    test_type="unusual_format",
                    input_description=f"{fps} FPS video",
                    expected_behavior="Accurate frame rate detection",
                    actual_behavior=f"Detected: {result.stdout.strip()}" if success else "Failed",
                    success=success,
                    error_message=result.stderr if result.stderr else None,
                    robustness_score=robustness_score,
                    metadata={"expected_fps": fps, "detected_fps": result.stdout.strip() if success else None}
                ))
            
            except Exception as e:
                logger.error(f"Unusual framerate test failed for {fps}fps: {e}")
        
        return results
    
    def run_comprehensive_edge_case_testing(self) -> Dict[str, List[EdgeCaseResult]]:
        """Run comprehensive edge case testing."""
        logger.info("Starting comprehensive edge case testing...")
        
        all_results = {
            "ffmpeg_corruption": self.test_ffmpeg_robustness(),
            "exiftool_corruption": self.test_exiftool_robustness(),
            "unusual_formats": self.test_unusual_formats()
        }
        
        # Flatten results for storage
        for category_results in all_results.values():
            self.edge_case_results.extend(category_results)
        
        # Save results
        self.save_edge_case_results(all_results)
        
        logger.info("Edge case testing completed")
        return all_results
    
    def save_edge_case_results(self, results: Dict[str, List[EdgeCaseResult]]):
        """Save edge case test results."""
        results_file = self.output_dir / "edge_case_results.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                "edge_case_results": {
                    category: [asdict(r) for r in category_results]
                    for category, category_results in results.items()
                },
                "summary": {
                    "total_tests": len(self.edge_case_results),
                    "successful_tests": sum(1 for r in self.edge_case_results if r.success),
                    "average_robustness": sum(r.robustness_score for r in self.edge_case_results) / len(self.edge_case_results) if self.edge_case_results else 0
                }
            }, f, indent=2)
        
        logger.info(f"Edge case results saved to {results_file}")
        
        # Generate summary report
        self.generate_edge_case_report(results)
    
    def generate_edge_case_report(self, results: Dict[str, List[EdgeCaseResult]]):
        """Generate edge case testing report."""
        report_file = self.output_dir / "edge_case_report.md"
        
        with open(report_file, 'w') as f:
            f.write("# Edge Case and Robustness Testing Report\n\n")
            f.write(f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for category, category_results in results.items():
                f.write(f"## {category.replace('_', ' ').title()}\n\n")
                
                if category_results:
                    success_rate = sum(1 for r in category_results if r.success) / len(category_results)
                    avg_robustness = sum(r.robustness_score for r in category_results) / len(category_results)
                    
                    f.write(f"**Success Rate**: {success_rate:.2%}\n")
                    f.write(f"**Average Robustness Score**: {avg_robustness:.2f}\n\n")
                    
                    f.write("### Test Results\n\n")
                    for result in category_results:
                        status = "✅" if result.success else "❌"
                        f.write(f"- {status} **{result.test_name}**: {result.actual_behavior} (Score: {result.robustness_score:.2f})\n")
                    
                    f.write("\n")
                else:
                    f.write("No test results available.\n\n")
        
        logger.info(f"Edge case report generated: {report_file}")


def main():
    """Main function to run edge case testing."""
    print("🧪 Edge Case and Robustness Testing")
    print("=" * 40)
    
    tester = EdgeCaseTester()
    
    try:
        results = tester.run_comprehensive_edge_case_testing()
        
        print("\n📊 Edge Case Testing Summary:")
        print("-" * 30)
        
        for category, category_results in results.items():
            if category_results:
                success_rate = sum(1 for r in category_results if r.success) / len(category_results)
                avg_robustness = sum(r.robustness_score for r in category_results) / len(category_results)
                
                print(f"\n{category.replace('_', ' ').title()}:")
                print(f"  Success Rate: {success_rate:.2%}")
                print(f"  Average Robustness: {avg_robustness:.2f}")
        
        print(f"\n📁 Detailed results saved to: {tester.output_dir}")
        print("✅ Edge case testing completed!")
        
    except Exception as e:
        logger.error(f"Edge case testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
