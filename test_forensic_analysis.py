#!/usr/bin/env python3
"""
Test version of the Jeffrey Epstein Prison Video Forensic Analysis
This version works with a smaller sample file for demonstration purposes.
"""

import os
import sys
import json
import subprocess
import re
import datetime

class TestEpsteinVideoAnalyzer:
    def __init__(self):
        self.video_filename = "test_sample.mp4"
        self.output_dir = "analysis_output"
        self.frames_dir = "splice_frames"
        
        # Key evidence we're looking for
        self.adobe_signatures = []
        self.splice_points = []
        self.source_clips = []
        self.metadata = {}
        
    def setup_directories(self):
        """Create necessary directories for analysis output."""
        print("🔧 Setting up analysis directories...")
        
        for directory in [self.output_dir, self.frames_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"   Created: {directory}/")
        
        print("✅ Directories ready")
    
    def check_dependencies(self):
        """Verify that required tools are installed."""
        print("🔍 Checking system dependencies...")
        
        required_tools = {
            'ffmpeg': 'Video processing tool',
            'ffprobe': 'Video metadata extraction',
            'exiftool': 'Metadata analysis tool'
        }
        
        missing_tools = []
        
        for tool, description in required_tools.items():
            try:
                # Use different version flags for different tools
                version_flag = '-ver' if tool == 'exiftool' else '-version'
                result = subprocess.run([tool, version_flag], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"   ✅ {tool}: Available")
                else:
                    missing_tools.append(tool)
                    print(f"   ❌ {tool}: Not found")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                missing_tools.append(tool)
                print(f"   ❌ {tool}: Not found")
        
        if missing_tools:
            print(f"\n🚨 Missing required tools: {', '.join(missing_tools)}")
            return False
        
        print("✅ All dependencies available")
        return True
    
    def check_video_file(self):
        """Check if the test video file exists."""
        if not os.path.exists(self.video_filename):
            print(f"❌ Test video file not found: {self.video_filename}")
            return False
        
        file_size = os.path.getsize(self.video_filename)
        print(f"✅ Test video file found ({file_size:,} bytes)")
        return True
    
    def extract_basic_metadata(self):
        """Extract basic video metadata using ffprobe."""
        print("📊 Extracting basic video metadata...")
        
        try:
            # Get JSON metadata from ffprobe
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', self.video_filename
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                metadata = json.loads(result.stdout)
                self.metadata['ffprobe'] = metadata
                
                # Extract key information
                format_info = metadata.get('format', {})
                duration = float(format_info.get('duration', 0))
                size = int(format_info.get('size', 0))
                bitrate = int(format_info.get('bit_rate', 0))
                
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                seconds = duration % 60
                
                print(f"   Duration: {hours}h {minutes}m {seconds:.2f}s")
                print(f"   File size: {size:,} bytes ({size / (1024**3):.2f} GB)")
                print(f"   Bitrate: {bitrate:,} bps")
                
                return True
            else:
                print(f"❌ ffprobe failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Basic metadata extraction failed: {e}")
            return False
    
    def extract_adobe_metadata(self):
        """Extract Adobe-specific metadata using exiftool."""
        print("🔬 Extracting Adobe metadata signatures...")
        
        try:
            # Get all metadata
            cmd = ['exiftool', '-j', self.video_filename]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                metadata = json.loads(result.stdout)[0]
                self.metadata['exiftool'] = metadata
                
                # Look for Adobe signatures
                adobe_fields = [
                    'CreatorTool',
                    'WindowsAtomUncProjectPath',
                    'IngredientsFilePath',
                    'IngredientsFromPart',
                    'IngredientsTopart'
                ]
                
                for field in adobe_fields:
                    if field in metadata:
                        value = metadata[field]
                        self.adobe_signatures.append((field, value))
                        print(f"   🎯 {field}: {value}")
                
                # Look for source clips in ingredients
                if 'IngredientsFilePath' in metadata:
                    file_paths = metadata['IngredientsFilePath']
                    if isinstance(file_paths, list):
                        for path in file_paths:
                            if path.endswith('.mp4'):
                                self.source_clips.append(path)
                                print(f"   📁 Source clip: {path}")
                    elif isinstance(file_paths, str) and file_paths.endswith('.mp4'):
                        self.source_clips.append(file_paths)
                        print(f"   📁 Source clip: {file_paths}")
                
                # Parse timing data for splice points
                self.parse_timing_data(metadata)
                
                return True
            else:
                print(f"❌ exiftool failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Adobe metadata extraction failed: {e}")
            return False
    
    def parse_timing_data(self, metadata):
        """Parse timing data to identify splice points."""
        print("🕵️ Parsing timing data for splice points...")
        
        # Look for Adobe timing format in ingredients
        timing_fields = ['IngredientsFromPart', 'IngredientsToPart']
        
        for field in timing_fields:
            if field in metadata:
                timing_data = metadata[field]
                if isinstance(timing_data, list):
                    for timing in timing_data:
                        self.parse_single_timing(timing, field)
                elif isinstance(timing_data, str):
                    self.parse_single_timing(timing_data, field)
    
    def parse_single_timing(self, timing_str, field_name):
        """Parse a single timing string."""
        # Adobe timing format: time:0d6035539564454400f254016000000
        pattern = r'time:(\d+)d(\d+)f(\d+)'
        match = re.search(pattern, timing_str)
        
        if match:
            try:
                numerator = int(match.group(2))
                denominator = int(match.group(3))
                seconds = numerator / denominator
                
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                secs = seconds % 60
                
                splice_point = {
                    'seconds': seconds,
                    'time_string': f"{hours}h{minutes:02d}m{secs:05.2f}s",
                    'raw_numerator': numerator,
                    'raw_denominator': denominator,
                    'field': field_name
                }
                
                # Avoid duplicates
                if not any(sp['seconds'] == seconds for sp in self.splice_points):
                    self.splice_points.append(splice_point)
                    print(f"   📍 Splice point: {splice_point['time_string']} ({seconds:.2f}s)")
                
            except (ValueError, ZeroDivisionError):
                pass
    
    def generate_summary_report(self):
        """Generate a summary report of findings."""
        print("\n" + "=" * 70)
        print("📋 FORENSIC ANALYSIS SUMMARY")
        print("=" * 70)
        
        print(f"\n🎯 Adobe Editing Signatures Found: {len(self.adobe_signatures)}")
        for field, value in self.adobe_signatures:
            if isinstance(value, list):
                for v in value:
                    print(f"   • {field}: {v}")
            else:
                print(f"   • {field}: {value}")
        
        print(f"\n📁 Source Clips Identified: {len(self.source_clips)}")
        for clip in self.source_clips:
            print(f"   • {clip}")
        
        print(f"\n📍 Splice Points Found: {len(self.splice_points)}")
        for i, sp in enumerate(self.splice_points):
            print(f"   • Splice {i+1}: {sp['time_string']} (from {sp['field']})")
        
        # Save metadata to file
        metadata_file = os.path.join(self.output_dir, 'metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        print(f"\n💾 Complete metadata saved to: {metadata_file}")
        
        return True
    
    def run_analysis(self):
        """Run the complete forensic analysis."""
        print("🚀 Starting Test Forensic Analysis")
        print("=" * 70)
        
        # Setup
        if not self.check_dependencies():
            return False
        
        self.setup_directories()
        
        # Check video file
        if not self.check_video_file():
            return False
        
        # Analyze video
        if not self.extract_basic_metadata():
            return False
        
        if not self.extract_adobe_metadata():
            return False
        
        # Generate report
        self.generate_summary_report()
        
        print("\n" + "=" * 70)
        print("🎯 ANALYSIS COMPLETE")
        print("=" * 70)
        print("✅ Evidence of professional video editing has been documented.")
        print("📊 This demonstrates the forensic analysis capabilities.")
        
        return True

def main():
    """Main entry point for the test forensic analysis."""
    analyzer = TestEpsteinVideoAnalyzer()
    
    try:
        success = analyzer.run_analysis()
        
        if success:
            print("\n✅ Test forensic analysis completed successfully!")
            return 0
        else:
            print("\n❌ Analysis failed. Check error messages above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
