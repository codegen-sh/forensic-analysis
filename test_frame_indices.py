#!/usr/bin/env python3
"""
Test script to verify that frame indices are calculated correctly.
"""

from epstein_video_analyzer import EpsteinVideoAnalyzer

def test_frame_index_calculation():
    """Test the frame index calculation logic."""
    analyzer = EpsteinVideoAnalyzer()
    
    # Simulate video metadata
    analyzer.fps = 29.97  # Common video frame rate
    
    # Test timestamp formatting
    test_cases = [
        (23759, "6h35m59s"),
        (23760, "6h36m00s"),
        (3661, "1h01m01s"),
        (0, "0h00m00s"),
        (3600, "1h00m00s")
    ]
    
    print("Testing timestamp formatting:")
    for seconds, expected in test_cases:
        result = analyzer._format_timestamp(seconds)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {seconds}s -> {result} (expected: {expected})")
    
    # Test file size formatting
    print("\nTesting file size formatting:")
    size_cases = [
        (2155188, "2,155,188 bytes"),
        (2263396, "2,263,396 bytes"),
        (1000, "1,000 bytes"),
        (999, "999 bytes")
    ]
    
    for size, expected in size_cases:
        result = analyzer._format_file_size(size)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {size} -> {result} (expected: {expected})")
    
    # Test video frame calculation
    print("\nTesting video frame calculation:")
    frame_cases = [
        (23759, 712095),  # 23759 * 29.97 ≈ 712095
        (23760, 712125),  # 23760 * 29.97 ≈ 712125
        (0, 0),
        (1, 30)  # 1 * 29.97 ≈ 30
    ]
    
    for timestamp, expected_frame in frame_cases:
        calculated_frame = int(timestamp * analyzer.fps)
        status = "✅" if abs(calculated_frame - expected_frame) < 2 else "❌"
        print(f"  {status} {timestamp}s -> frame {calculated_frame} (expected: ~{expected_frame})")

if __name__ == "__main__":
    test_frame_index_calculation()
