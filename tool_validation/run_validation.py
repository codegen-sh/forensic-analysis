#!/usr/bin/env python3
"""
Tool Validation Runner
=====================

Simple runner script for the forensic tool validation framework.
This script provides an easy way to run different validation components.

Usage:
    python run_validation.py --all                    # Run comprehensive validation
    python run_validation.py --tool ffmpeg            # Validate specific tool
    python run_validation.py --edge-cases             # Run edge case testing only
    python run_validation.py --academic               # Run academic research only

Author: Forensic Analysis Team
Version: 1.0
Date: July 2025
"""

import argparse
import sys
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from comprehensive_validator import ComprehensiveValidator
from forensic_tool_validator import ForensicToolValidator
from edge_case_tester import EdgeCaseTester
from academic_research import AcademicResearcher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function to parse arguments and run validation."""
    parser = argparse.ArgumentParser(
        description="Forensic Tool Validation Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_validation.py --all                    # Run comprehensive validation
  python run_validation.py --tool ffmpeg            # Validate specific tool
  python run_validation.py --edge-cases             # Run edge case testing only
  python run_validation.py --academic               # Run academic research only
  python run_validation.py --output-dir ./results   # Specify output directory
        """
    )
    
    # Main operation modes
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true',
                      help='Run comprehensive validation for all tools')
    group.add_argument('--tool', choices=['ffmpeg', 'exiftool'],
                      help='Run validation for specific tool')
    group.add_argument('--edge-cases', action='store_true',
                      help='Run edge case testing only')
    group.add_argument('--academic', action='store_true',
                      help='Run academic research analysis only')
    
    # Optional arguments
    parser.add_argument('--output-dir', default='validation_results',
                       help='Output directory for results (default: validation_results)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    try:
        if args.all:
            print("🔬 Running Comprehensive Forensic Tool Validation")
            print("=" * 50)
            
            validator = ComprehensiveValidator(str(output_dir))
            results = validator.run_comprehensive_validation()
            
            print("\n📊 Validation Summary:")
            for tool_name, report in results.items():
                print(f"  {tool_name}: {report.overall_confidence:.2%} confidence")
            
            print(f"\n📁 Results saved to: {output_dir}")
            print("📋 See FORENSIC_TOOL_VALIDATION_REPORT.md for detailed analysis")
            
        elif args.tool:
            print(f"🔧 Running Validation for {args.tool.upper()}")
            print("=" * 40)
            
            validator = ForensicToolValidator(str(output_dir / "tool_validation"))
            
            # Get tool version
            version_info = validator.get_tool_version(args.tool)
            if version_info:
                print(f"Tool Version: {version_info.version}")
                print(f"Platform: {version_info.platform}")
            
            # Run validation
            if args.tool == "ffmpeg":
                results = validator.validate_ffmpeg_accuracy()
                results.extend(validator.test_version_consistency("ffmpeg"))
            else:  # exiftool
                results = validator.validate_exiftool_accuracy()
                results.extend(validator.test_version_consistency("exiftool"))
            
            validator.validation_results.extend(results)
            metrics = validator.calculate_reliability_metrics(args.tool)
            
            print(f"\n📊 {args.tool.upper()} Validation Results:")
            print(f"  Accuracy Rate: {metrics.accuracy_rate:.2%}")
            print(f"  Error Rate: {metrics.error_rate:.2%}")
            print(f"  Consistency Score: {metrics.consistency_score:.2%}")
            print(f"  Tests Performed: {len(results)}")
            
            # Save results
            validator.save_validation_results({args.tool: metrics})
            print(f"\n📁 Results saved to: {validator.output_dir}")
            
        elif args.edge_cases:
            print("🧪 Running Edge Case Testing")
            print("=" * 30)
            
            tester = EdgeCaseTester(str(output_dir / "edge_cases"))
            results = tester.run_comprehensive_edge_case_testing()
            
            print("\n📊 Edge Case Testing Summary:")
            for category, category_results in results.items():
                if category_results:
                    success_rate = sum(1 for r in category_results if r.success) / len(category_results)
                    print(f"  {category.replace('_', ' ').title()}: {success_rate:.2%} success rate")
            
            print(f"\n📁 Results saved to: {tester.output_dir}")
            
        elif args.academic:
            print("📚 Running Academic Research Analysis")
            print("=" * 35)
            
            researcher = AcademicResearcher(str(output_dir / "academic_research"))
            results = researcher.generate_comprehensive_research_report()
            
            print("\n📊 Academic Research Summary:")
            for topic, findings in results.items():
                print(f"  {topic.replace('_', ' ').title()}: {findings.confidence_level:.2%} confidence")
                print(f"    Sources: {len(findings.sources)}, Standards: {len(findings.standards)}")
            
            print(f"\n📁 Results saved to: {researcher.output_dir}")
        
        print("\n✅ Validation completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        print(f"\n❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
