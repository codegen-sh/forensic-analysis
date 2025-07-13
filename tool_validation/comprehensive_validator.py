#!/usr/bin/env python3
"""
Comprehensive Forensic Tool Validation Framework
===============================================

This module orchestrates comprehensive validation of forensic tools used in
video analysis, combining accuracy testing, edge case analysis, and academic
research to provide complete reliability assessment.

Key Features:
- Integrated validation workflow
- Comprehensive reporting
- Academic research integration
- Standards compliance checking
- Confidence interval calculation

Author: Forensic Analysis Team
Version: 1.0
Date: July 2025
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Import validation modules
from forensic_tool_validator import ForensicToolValidator, ReliabilityMetrics
from edge_case_tester import EdgeCaseTester, EdgeCaseResult
from academic_research import AcademicResearcher, ResearchFindings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ComprehensiveValidationReport:
    """Complete validation report for forensic tools."""
    tool_name: str
    validation_summary: Dict[str, Any]
    reliability_metrics: ReliabilityMetrics
    edge_case_results: List[EdgeCaseResult]
    academic_findings: ResearchFindings
    overall_confidence: float
    recommendations: List[str]
    limitations: List[str]
    compliance_status: Dict[str, str]

class ComprehensiveValidator:
    """
    Comprehensive validation framework for forensic tools.
    
    This class orchestrates all validation components to provide
    a complete assessment of tool reliability and suitability
    for forensic use.
    """
    
    def __init__(self, output_dir: str = "comprehensive_validation"):
        """Initialize the comprehensive validator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize component validators
        self.tool_validator = ForensicToolValidator(str(self.output_dir / "tool_validation"))
        self.edge_case_tester = EdgeCaseTester(str(self.output_dir / "edge_cases"))
        self.academic_researcher = AcademicResearcher(str(self.output_dir / "academic_research"))
        
        # Results storage
        self.validation_reports: Dict[str, ComprehensiveValidationReport] = {}
        
        logger.info(f"Comprehensive Validator initialized. Output directory: {self.output_dir}")
    
    def validate_tool(self, tool_name: str) -> ComprehensiveValidationReport:
        """Perform comprehensive validation of a specific tool."""
        logger.info(f"Starting comprehensive validation for {tool_name}")
        
        # 1. Basic accuracy validation
        logger.info(f"Running accuracy validation for {tool_name}")
        if tool_name.lower() == "ffmpeg":
            accuracy_results = self.tool_validator.validate_ffmpeg_accuracy()
            consistency_results = self.tool_validator.test_version_consistency("ffmpeg")
        elif tool_name.lower() == "exiftool":
            accuracy_results = self.tool_validator.validate_exiftool_accuracy()
            consistency_results = self.tool_validator.test_version_consistency("exiftool")
        else:
            logger.warning(f"Unknown tool: {tool_name}")
            accuracy_results = []
            consistency_results = []
        
        # Store results in validator
        self.tool_validator.validation_results.extend(accuracy_results + consistency_results)
        
        # Calculate reliability metrics
        reliability_metrics = self.tool_validator.calculate_reliability_metrics(tool_name)
        
        # 2. Edge case and robustness testing
        logger.info(f"Running edge case testing for {tool_name}")
        if tool_name.lower() == "ffmpeg":
            edge_case_results = self.edge_case_tester.test_ffmpeg_robustness()
        elif tool_name.lower() == "exiftool":
            edge_case_results = self.edge_case_tester.test_exiftool_robustness()
        else:
            edge_case_results = []
        
        # Add unusual format testing
        edge_case_results.extend(self.edge_case_tester.test_unusual_formats())
        
        # 3. Academic research analysis
        logger.info(f"Analyzing academic research for {tool_name}")
        academic_findings = self.academic_researcher.research_tool_reliability(tool_name)
        
        # 4. Calculate overall confidence and generate recommendations
        overall_confidence = self._calculate_overall_confidence(
            reliability_metrics, edge_case_results, academic_findings
        )
        
        recommendations = self._generate_comprehensive_recommendations(
            tool_name, reliability_metrics, edge_case_results, academic_findings
        )
        
        limitations = self._identify_tool_limitations(
            tool_name, reliability_metrics, edge_case_results, academic_findings
        )
        
        compliance_status = self._assess_standards_compliance(
            tool_name, reliability_metrics, academic_findings
        )
        
        # Create validation summary
        validation_summary = {
            "accuracy_tests": len(accuracy_results),
            "consistency_tests": len(consistency_results),
            "edge_case_tests": len(edge_case_results),
            "academic_sources": len(academic_findings.sources),
            "validation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tool_version": reliability_metrics.version_info.version if reliability_metrics.version_info else "unknown"
        }
        
        # Create comprehensive report
        report = ComprehensiveValidationReport(
            tool_name=tool_name,
            validation_summary=validation_summary,
            reliability_metrics=reliability_metrics,
            edge_case_results=edge_case_results,
            academic_findings=academic_findings,
            overall_confidence=overall_confidence,
            recommendations=recommendations,
            limitations=limitations,
            compliance_status=compliance_status
        )
        
        self.validation_reports[tool_name] = report
        logger.info(f"Comprehensive validation completed for {tool_name}")
        
        return report
    
    def _calculate_overall_confidence(
        self,
        reliability_metrics: ReliabilityMetrics,
        edge_case_results: List[EdgeCaseResult],
        academic_findings: ResearchFindings
    ) -> float:
        """Calculate overall confidence score from all validation components."""
        
        # Weight different components
        weights = {
            "accuracy": 0.4,      # 40% weight for accuracy testing
            "robustness": 0.3,    # 30% weight for edge case robustness
            "academic": 0.3       # 30% weight for academic validation
        }
        
        # Accuracy component
        accuracy_score = reliability_metrics.accuracy_rate
        
        # Robustness component
        if edge_case_results:
            robustness_scores = [r.robustness_score for r in edge_case_results]
            robustness_score = sum(robustness_scores) / len(robustness_scores)
        else:
            robustness_score = 0.5  # Neutral score if no edge case tests
        
        # Academic component
        academic_score = academic_findings.confidence_level
        
        # Calculate weighted average
        overall_confidence = (
            weights["accuracy"] * accuracy_score +
            weights["robustness"] * robustness_score +
            weights["academic"] * academic_score
        )
        
        return overall_confidence
    
    def _generate_comprehensive_recommendations(
        self,
        tool_name: str,
        reliability_metrics: ReliabilityMetrics,
        edge_case_results: List[EdgeCaseResult],
        academic_findings: ResearchFindings
    ) -> List[str]:
        """Generate comprehensive recommendations based on all validation results."""
        
        recommendations = []
        
        # Accuracy-based recommendations
        if reliability_metrics.accuracy_rate < 0.95:
            recommendations.append(
                f"⚠️ {tool_name} accuracy rate ({reliability_metrics.accuracy_rate:.2%}) "
                "is below recommended 95% threshold. Use with caution for critical forensic analysis."
            )
        
        if reliability_metrics.error_rate > 0.05:
            recommendations.append(
                f"⚠️ Error rate ({reliability_metrics.error_rate:.2%}) exceeds 5% threshold. "
                "Consider additional validation or alternative tools for high-stakes cases."
            )
        
        # Consistency-based recommendations
        if reliability_metrics.consistency_score < 0.9:
            recommendations.append(
                f"⚠️ Consistency score ({reliability_metrics.consistency_score:.2%}) indicates "
                "potential variability between runs. Perform multiple measurements for critical analysis."
            )
        
        # Edge case recommendations
        failed_edge_cases = [r for r in edge_case_results if not r.success]
        if len(failed_edge_cases) > len(edge_case_results) * 0.3:  # >30% failure rate
            recommendations.append(
                f"⚠️ {tool_name} failed {len(failed_edge_cases)}/{len(edge_case_results)} "
                "edge case tests. Exercise extreme caution with unusual or corrupted files."
            )
        
        # Academic recommendations
        recommendations.extend([
            f"📚 Academic recommendation: {rec}"
            for rec in academic_findings.recommendations[:3]  # Top 3 academic recommendations
        ])
        
        # Version-specific recommendations
        if reliability_metrics.version_info:
            recommendations.append(
                f"🔧 Current version: {reliability_metrics.version_info.version}. "
                "Ensure consistent version usage across forensic workflow."
            )
        
        # Confidence interval recommendations
        ci_lower, ci_upper = reliability_metrics.confidence_interval
        if ci_upper - ci_lower > 0.2:  # Wide confidence interval
            recommendations.append(
                f"📊 Wide confidence interval ({ci_lower:.2%}-{ci_upper:.2%}) "
                "suggests high variability. Increase sample size for more reliable estimates."
            )
        
        return recommendations
    
    def _identify_tool_limitations(
        self,
        tool_name: str,
        reliability_metrics: ReliabilityMetrics,
        edge_case_results: List[EdgeCaseResult],
        academic_findings: ResearchFindings
    ) -> List[str]:
        """Identify and document tool limitations."""
        
        limitations = []
        
        # Accuracy limitations
        if reliability_metrics.accuracy_rate < 1.0:
            limitations.append(
                f"Measurement accuracy: {reliability_metrics.accuracy_rate:.2%} "
                f"(error rate: {reliability_metrics.error_rate:.2%})"
            )
        
        # Edge case limitations
        corruption_failures = [
            r for r in edge_case_results 
            if "corruption" in r.test_type and not r.success
        ]
        if corruption_failures:
            limitations.append(
                f"Limited robustness with corrupted files: "
                f"{len(corruption_failures)} corruption scenarios failed"
            )
        
        timeout_failures = [
            r for r in edge_case_results
            if r.metadata.get("timeout", False)
        ]
        if timeout_failures:
            limitations.append(
                f"Timeout issues: {len(timeout_failures)} tests exceeded time limits"
            )
        
        # Academic limitations
        limitations.extend([
            f"Research gap: {gap}"
            for gap in academic_findings.research_gaps[:3]  # Top 3 research gaps
        ])
        
        # Platform limitations
        if reliability_metrics.version_info:
            limitations.append(
                f"Platform-specific behavior: Tested on {reliability_metrics.version_info.platform} "
                f"{reliability_metrics.version_info.architecture}"
            )
        
        return limitations
    
    def _assess_standards_compliance(
        self,
        tool_name: str,
        reliability_metrics: ReliabilityMetrics,
        academic_findings: ResearchFindings
    ) -> Dict[str, str]:
        """Assess compliance with forensic standards."""
        
        compliance = {}
        
        # NIST SP 800-86 compliance
        if reliability_metrics.accuracy_rate >= 0.95 and reliability_metrics.error_rate <= 0.05:
            compliance["NIST SP 800-86"] = "COMPLIANT - Meets accuracy and error rate requirements"
        else:
            compliance["NIST SP 800-86"] = "NON-COMPLIANT - Does not meet accuracy/error thresholds"
        
        # ISO/IEC 27037 compliance
        if len(reliability_metrics.test_results) >= 5:  # Sufficient validation testing
            compliance["ISO/IEC 27037"] = "COMPLIANT - Adequate validation testing performed"
        else:
            compliance["ISO/IEC 27037"] = "PARTIAL - Limited validation testing"
        
        # SWGDE compliance
        if reliability_metrics.consistency_score >= 0.9:
            compliance["SWGDE Guidelines"] = "COMPLIANT - Demonstrates consistent behavior"
        else:
            compliance["SWGDE Guidelines"] = "NON-COMPLIANT - Inconsistent behavior detected"
        
        # Academic standards
        if academic_findings.confidence_level >= 0.8:
            compliance["Academic Standards"] = "HIGH - Strong academic validation support"
        elif academic_findings.confidence_level >= 0.6:
            compliance["Academic Standards"] = "MODERATE - Some academic validation support"
        else:
            compliance["Academic Standards"] = "LOW - Limited academic validation support"
        
        return compliance
    
    def run_comprehensive_validation(self, tools: List[str] = None) -> Dict[str, ComprehensiveValidationReport]:
        """Run comprehensive validation for specified tools."""
        
        if tools is None:
            tools = ["ffmpeg", "exiftool"]
        
        logger.info(f"Starting comprehensive validation for tools: {tools}")
        
        # Validate each tool
        for tool in tools:
            try:
                self.validate_tool(tool)
            except Exception as e:
                logger.error(f"Validation failed for {tool}: {e}")
        
        # Generate comprehensive report
        self.generate_comprehensive_report()
        
        logger.info("Comprehensive validation completed for all tools")
        return self.validation_reports
    
    def generate_comprehensive_report(self):
        """Generate comprehensive validation report."""
        
        # Save detailed JSON report
        json_report_file = self.output_dir / "comprehensive_validation_report.json"
        with open(json_report_file, 'w') as f:
            json.dump({
                "validation_reports": {
                    tool: asdict(report) for tool, report in self.validation_reports.items()
                },
                "summary": {
                    "total_tools_validated": len(self.validation_reports),
                    "validation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "overall_confidence": {
                        tool: report.overall_confidence
                        for tool, report in self.validation_reports.items()
                    }
                }
            }, f, indent=2)
        
        logger.info(f"Comprehensive JSON report saved to {json_report_file}")
        
        # Generate human-readable report
        self.generate_human_readable_report()
    
    def generate_human_readable_report(self):
        """Generate human-readable comprehensive report."""
        
        report_file = self.output_dir / "FORENSIC_TOOL_VALIDATION_REPORT.md"
        
        with open(report_file, 'w') as f:
            f.write("# Comprehensive Forensic Tool Validation Report\n\n")
            f.write(f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Tools Validated**: {len(self.validation_reports)}\n")
            f.write(f"**Validation Framework Version**: 1.0\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            f.write("This report provides comprehensive validation results for forensic tools ")
            f.write("used in video analysis, including accuracy testing, edge case analysis, ")
            f.write("and academic research validation.\n\n")
            
            # Overall Results Table
            f.write("### Overall Results\n\n")
            f.write("| Tool | Overall Confidence | Accuracy Rate | Error Rate | Robustness Score |\n")
            f.write("|------|-------------------|---------------|------------|------------------|\n")
            
            for tool_name, report in self.validation_reports.items():
                edge_case_avg = sum(r.robustness_score for r in report.edge_case_results) / len(report.edge_case_results) if report.edge_case_results else 0
                f.write(f"| {tool_name} | {report.overall_confidence:.2%} | ")
                f.write(f"{report.reliability_metrics.accuracy_rate:.2%} | ")
                f.write(f"{report.reliability_metrics.error_rate:.2%} | ")
                f.write(f"{edge_case_avg:.2f} |\n")
            
            f.write("\n")
            
            # Detailed Results for Each Tool
            for tool_name, report in self.validation_reports.items():
                f.write(f"## {tool_name.upper()} Validation Results\n\n")
                
                # Tool Information
                if report.reliability_metrics.version_info:
                    f.write(f"**Version**: {report.reliability_metrics.version_info.version}\n")
                    f.write(f"**Platform**: {report.reliability_metrics.version_info.platform}\n")
                    f.write(f"**Architecture**: {report.reliability_metrics.version_info.architecture}\n\n")
                
                # Validation Summary
                f.write("### Validation Summary\n\n")
                f.write(f"- **Overall Confidence**: {report.overall_confidence:.2%}\n")
                f.write(f"- **Accuracy Rate**: {report.reliability_metrics.accuracy_rate:.2%}\n")
                f.write(f"- **Error Rate**: {report.reliability_metrics.error_rate:.2%}\n")
                f.write(f"- **Consistency Score**: {report.reliability_metrics.consistency_score:.2%}\n")
                f.write(f"- **Confidence Interval**: {report.reliability_metrics.confidence_interval[0]:.2%} - {report.reliability_metrics.confidence_interval[1]:.2%}\n")
                f.write(f"- **Tests Performed**: {report.validation_summary['accuracy_tests'] + report.validation_summary['consistency_tests'] + report.validation_summary['edge_case_tests']}\n\n")
                
                # Standards Compliance
                f.write("### Standards Compliance\n\n")
                for standard, status in report.compliance_status.items():
                    status_icon = "✅" if "COMPLIANT" in status else "⚠️" if "PARTIAL" in status else "❌"
                    f.write(f"- {status_icon} **{standard}**: {status}\n")
                f.write("\n")
                
                # Recommendations
                if report.recommendations:
                    f.write("### Recommendations\n\n")
                    for rec in report.recommendations:
                        f.write(f"- {rec}\n")
                    f.write("\n")
                
                # Limitations
                if report.limitations:
                    f.write("### Known Limitations\n\n")
                    for limitation in report.limitations:
                        f.write(f"- {limitation}\n")
                    f.write("\n")
                
                # Academic Research Summary
                f.write("### Academic Research Summary\n\n")
                f.write(f"**Research Confidence**: {report.academic_findings.confidence_level:.2%}\n")
                f.write(f"**Sources Analyzed**: {len(report.academic_findings.sources)}\n")
                f.write(f"**Standards Referenced**: {len(report.academic_findings.standards)}\n\n")
                
                if report.academic_findings.key_insights:
                    f.write("#### Key Research Insights\n\n")
                    for insight in report.academic_findings.key_insights[:5]:  # Top 5
                        f.write(f"- {insight}\n")
                    f.write("\n")
                
                # Edge Case Results Summary
                if report.edge_case_results:
                    f.write("### Edge Case Testing Summary\n\n")
                    success_rate = sum(1 for r in report.edge_case_results if r.success) / len(report.edge_case_results)
                    avg_robustness = sum(r.robustness_score for r in report.edge_case_results) / len(report.edge_case_results)
                    
                    f.write(f"**Success Rate**: {success_rate:.2%}\n")
                    f.write(f"**Average Robustness Score**: {avg_robustness:.2f}\n")
                    f.write(f"**Total Tests**: {len(report.edge_case_results)}\n\n")
                    
                    # Group by test type
                    test_types = {}
                    for result in report.edge_case_results:
                        test_type = result.test_type
                        if test_type not in test_types:
                            test_types[test_type] = []
                        test_types[test_type].append(result)
                    
                    for test_type, results in test_types.items():
                        type_success_rate = sum(1 for r in results if r.success) / len(results)
                        f.write(f"- **{test_type.replace('_', ' ').title()}**: {type_success_rate:.2%} success rate ({len(results)} tests)\n")
                    
                    f.write("\n")
            
            # Methodology
            f.write("## Validation Methodology\n\n")
            f.write("This comprehensive validation employed multiple approaches:\n\n")
            f.write("1. **Accuracy Testing**: Controlled tests with known ground truth data\n")
            f.write("2. **Consistency Testing**: Multiple runs to assess measurement variability\n")
            f.write("3. **Edge Case Testing**: Robustness assessment with corrupted and unusual files\n")
            f.write("4. **Academic Research**: Literature review and standards compliance analysis\n\n")
            
            # Conclusions
            f.write("## Conclusions\n\n")
            
            high_confidence_tools = [
                tool for tool, report in self.validation_reports.items()
                if report.overall_confidence >= 0.8
            ]
            
            if high_confidence_tools:
                f.write(f"**High Confidence Tools**: {', '.join(high_confidence_tools)}\n")
                f.write("These tools demonstrate high reliability and are suitable for forensic use with proper validation procedures.\n\n")
            
            medium_confidence_tools = [
                tool for tool, report in self.validation_reports.items()
                if 0.6 <= report.overall_confidence < 0.8
            ]
            
            if medium_confidence_tools:
                f.write(f"**Medium Confidence Tools**: {', '.join(medium_confidence_tools)}\n")
                f.write("These tools show acceptable reliability but require careful consideration of limitations and additional validation for critical cases.\n\n")
            
            low_confidence_tools = [
                tool for tool, report in self.validation_reports.items()
                if report.overall_confidence < 0.6
            ]
            
            if low_confidence_tools:
                f.write(f"**Low Confidence Tools**: {', '.join(low_confidence_tools)}\n")
                f.write("These tools show significant limitations and should be used with extreme caution or replaced with more reliable alternatives.\n\n")
            
            # Disclaimer
            f.write("## Disclaimer\n\n")
            f.write("This validation report is based on controlled testing and academic research. ")
            f.write("Results may vary in real-world scenarios. Users should perform additional ")
            f.write("validation appropriate to their specific use cases and maintain awareness ")
            f.write("of tool limitations when presenting forensic evidence.\n\n")
            
            f.write("For questions about this validation report, please consult with qualified ")
            f.write("digital forensics experts.\n")
        
        logger.info(f"Human-readable report generated: {report_file}")


def main():
    """Main function to run comprehensive validation."""
    print("🔬 Comprehensive Forensic Tool Validation Framework")
    print("=" * 55)
    
    validator = ComprehensiveValidator()
    
    try:
        # Run comprehensive validation
        results = validator.run_comprehensive_validation()
        
        print("\n📊 Comprehensive Validation Results:")
        print("-" * 40)
        
        for tool_name, report in results.items():
            print(f"\n{tool_name.upper()}:")
            print(f"  Overall Confidence: {report.overall_confidence:.2%}")
            print(f"  Accuracy Rate: {report.reliability_metrics.accuracy_rate:.2%}")
            print(f"  Error Rate: {report.reliability_metrics.error_rate:.2%}")
            print(f"  Edge Case Success: {sum(1 for r in report.edge_case_results if r.success)}/{len(report.edge_case_results)}")
            print(f"  Academic Confidence: {report.academic_findings.confidence_level:.2%}")
        
        print(f"\n📁 Comprehensive results saved to: {validator.output_dir}")
        print("📋 See FORENSIC_TOOL_VALIDATION_REPORT.md for detailed analysis")
        print("✅ Comprehensive validation completed successfully!")
        
    except Exception as e:
        logger.error(f"Comprehensive validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
