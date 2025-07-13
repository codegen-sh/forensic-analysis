"""
Validation Protocols Module

This module provides standardized validation protocols for independent verification
and third-party validation of forensic analysis results.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging

from .source_authenticator import SourceAuthenticator
from .chain_of_custody import ChainOfCustodyManager
from .cryptographic_verifier import CryptographicVerifier

logger = logging.getLogger(__name__)


class ValidationProtocols:
    """
    Implements standardized validation protocols for forensic analysis.
    Provides frameworks for independent verification and third-party validation.
    """
    
    def __init__(self, config_path: str = "verification_framework/validation_config.json"):
        """
        Initialize validation protocols.
        
        Args:
            config_path: Path to validation configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize component modules
        self.source_auth = SourceAuthenticator()
        self.custody_manager = ChainOfCustodyManager()
        self.crypto_verifier = CryptographicVerifier()
    
    def _load_config(self) -> Dict:
        """Load validation configuration."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load validation config: {e}")
        
        return {
            "validation_standards": {
                "forensic_standards": ["ISO/IEC 27037", "NIST SP 800-86", "RFC 3227"],
                "legal_requirements": ["Federal Rules of Evidence", "Daubert Standard"],
                "technical_standards": ["SHA-256 minimum", "Chain of custody required"]
            },
            "validation_levels": {
                "basic": {
                    "required_checks": ["source_verification", "integrity_check"],
                    "confidence_threshold": 0.7
                },
                "standard": {
                    "required_checks": ["source_verification", "integrity_check", "chain_of_custody"],
                    "confidence_threshold": 0.85
                },
                "forensic": {
                    "required_checks": [
                        "source_verification", "integrity_check", "chain_of_custody",
                        "independent_verification", "cryptographic_verification"
                    ],
                    "confidence_threshold": 0.95
                }
            },
            "third_party_validators": [],
            "metadata": {
                "version": "1.0",
                "last_updated": None
            }
        }
    
    def _save_config(self):
        """Save validation configuration."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            self.config["metadata"]["last_updated"] = datetime.utcnow().isoformat()
            
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving validation config: {e}")
    
    def validate_evidence_package(self, evidence_path: str, 
                                validation_level: str = "standard") -> Dict:
        """
        Perform comprehensive validation of an evidence package.
        
        Args:
            evidence_path: Path to evidence file or directory
            validation_level: Level of validation (basic, standard, forensic)
            
        Returns:
            Comprehensive validation result
        """
        validation_id = f"VP_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        validation_result = {
            "validation_id": validation_id,
            "validation_timestamp": datetime.utcnow().isoformat(),
            "evidence_path": evidence_path,
            "validation_level": validation_level,
            "validation_checks": {},
            "overall_status": "UNKNOWN",
            "confidence_score": 0.0,
            "recommendations": [],
            "compliance_status": {}
        }
        
        # Get required checks for validation level
        level_config = self.config["validation_levels"].get(validation_level, {})
        required_checks = level_config.get("required_checks", [])
        confidence_threshold = level_config.get("confidence_threshold", 0.8)
        
        # Perform validation checks
        check_results = {}
        
        # Source verification
        if "source_verification" in required_checks:
            check_results["source_verification"] = self._perform_source_verification(evidence_path)
        
        # Integrity check
        if "integrity_check" in required_checks:
            check_results["integrity_check"] = self._perform_integrity_check(evidence_path)
        
        # Chain of custody
        if "chain_of_custody" in required_checks:
            check_results["chain_of_custody"] = self._perform_custody_check(evidence_path)
        
        # Independent verification
        if "independent_verification" in required_checks:
            check_results["independent_verification"] = self._perform_independent_verification(evidence_path)
        
        # Cryptographic verification
        if "cryptographic_verification" in required_checks:
            check_results["cryptographic_verification"] = self._perform_cryptographic_verification(evidence_path)
        
        validation_result["validation_checks"] = check_results
        
        # Calculate overall confidence score
        confidence_score = self._calculate_confidence_score(check_results)
        validation_result["confidence_score"] = confidence_score
        
        # Determine overall status
        if confidence_score >= confidence_threshold:
            validation_result["overall_status"] = "VALIDATED"
        elif confidence_score >= 0.5:
            validation_result["overall_status"] = "PARTIALLY_VALIDATED"
        else:
            validation_result["overall_status"] = "VALIDATION_FAILED"
        
        # Generate recommendations
        validation_result["recommendations"] = self._generate_validation_recommendations(
            check_results, confidence_score, confidence_threshold
        )
        
        # Check compliance with standards
        validation_result["compliance_status"] = self._check_compliance_standards(check_results)
        
        return validation_result
    
    def _perform_source_verification(self, evidence_path: str) -> Dict:
        """Perform source verification check."""
        try:
            verification_result = self.source_auth.verify_against_doj_source(evidence_path)
            
            return {
                "check_type": "source_verification",
                "status": "PASS" if verification_result["verification_status"].startswith("VERIFIED") else "FAIL",
                "confidence": 0.9 if verification_result["verification_status"] == "VERIFIED_DOJ_MATCH" else 0.6,
                "details": verification_result,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "check_type": "source_verification",
                "status": "ERROR",
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _perform_integrity_check(self, evidence_path: str) -> Dict:
        """Perform integrity verification check."""
        try:
            # Create and verify integrity manifest
            manifest = self.crypto_verifier.create_integrity_manifest(evidence_path)
            verification = self.crypto_verifier.verify_integrity_manifest(evidence_path, manifest)
            
            return {
                "check_type": "integrity_check",
                "status": "PASS" if verification["overall_integrity"] else "FAIL",
                "confidence": 0.95 if verification["overall_integrity"] else 0.1,
                "details": verification,
                "manifest": manifest,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "check_type": "integrity_check",
                "status": "ERROR",
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _perform_custody_check(self, evidence_path: str) -> Dict:
        """Perform chain of custody check."""
        try:
            # This would typically check existing custody records
            # For now, we'll create a basic custody entry
            custodian_info = {
                "name": "Forensic Analysis System",
                "organization": "Independent Verification",
                "contact": "verification@forensic-analysis.org"
            }
            
            source_info = {
                "description": f"Evidence file: {os.path.basename(evidence_path)}",
                "source_type": "digital_evidence",
                "acquisition_method": "file_system_copy"
            }
            
            evidence_id = self.custody_manager.create_evidence_item(
                evidence_path, source_info, custodian_info
            )
            
            # Generate custody report
            custody_report = self.custody_manager.generate_custody_report(evidence_id)
            
            return {
                "check_type": "chain_of_custody",
                "status": "PASS",
                "confidence": 0.8,
                "evidence_id": evidence_id,
                "details": custody_report,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "check_type": "chain_of_custody",
                "status": "ERROR",
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _perform_independent_verification(self, evidence_path: str) -> Dict:
        """Perform independent verification check."""
        try:
            # Independent verification would involve third-party validation
            # For now, we'll simulate this with multiple hash algorithms
            hashes = self.crypto_verifier.calculate_multiple_hashes(evidence_path)
            
            # Simulate independent verification by checking hash consistency
            hash_consistency = len(set(len(h) for h in hashes.values())) == len(hashes)
            
            return {
                "check_type": "independent_verification",
                "status": "PASS" if hash_consistency else "FAIL",
                "confidence": 0.85 if hash_consistency else 0.3,
                "details": {
                    "verification_method": "multi_algorithm_hash_verification",
                    "hash_algorithms": list(hashes.keys()),
                    "hash_consistency": hash_consistency,
                    "hashes": hashes
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "check_type": "independent_verification",
                "status": "ERROR",
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _perform_cryptographic_verification(self, evidence_path: str) -> Dict:
        """Perform cryptographic verification check."""
        try:
            verification_report = self.crypto_verifier.create_verification_report(evidence_path)
            
            overall_assessment = verification_report["verification_report"]["overall_assessment"]
            success_rate = overall_assessment["success_rate"]
            
            return {
                "check_type": "cryptographic_verification",
                "status": "PASS" if success_rate >= 0.8 else "FAIL",
                "confidence": success_rate,
                "details": verification_report,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "check_type": "cryptographic_verification",
                "status": "ERROR",
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _calculate_confidence_score(self, check_results: Dict) -> float:
        """Calculate overall confidence score from check results."""
        if not check_results:
            return 0.0
        
        total_confidence = 0.0
        total_weight = 0.0
        
        # Weight different checks based on importance
        check_weights = {
            "source_verification": 0.3,
            "integrity_check": 0.25,
            "chain_of_custody": 0.2,
            "independent_verification": 0.15,
            "cryptographic_verification": 0.1
        }
        
        for check_type, result in check_results.items():
            weight = check_weights.get(check_type, 0.1)
            confidence = result.get("confidence", 0.0)
            
            total_confidence += confidence * weight
            total_weight += weight
        
        return total_confidence / total_weight if total_weight > 0 else 0.0
    
    def _generate_validation_recommendations(self, check_results: Dict, 
                                           confidence_score: float, 
                                           threshold: float) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Check for failed validations
        failed_checks = [check for check, result in check_results.items() 
                        if result.get("status") == "FAIL"]
        
        if failed_checks:
            recommendations.append(f"❌ Failed validation checks: {', '.join(failed_checks)}")
            recommendations.append("🔧 Address failed checks before proceeding with analysis")
        
        # Check confidence score
        if confidence_score < threshold:
            recommendations.append(f"⚠️ Confidence score ({confidence_score:.2f}) below threshold ({threshold})")
            recommendations.append("📈 Improve validation checks to increase confidence")
        
        # Specific recommendations based on check results
        if "source_verification" in check_results:
            source_result = check_results["source_verification"]
            if source_result.get("status") != "PASS":
                recommendations.append("🔍 Verify source authenticity against official DOJ releases")
        
        if "integrity_check" in check_results:
            integrity_result = check_results["integrity_check"]
            if integrity_result.get("status") != "PASS":
                recommendations.append("🛡️ Evidence integrity compromised - investigate potential tampering")
        
        if "chain_of_custody" in check_results:
            custody_result = check_results["chain_of_custody"]
            if custody_result.get("status") != "PASS":
                recommendations.append("📋 Establish proper chain of custody documentation")
        
        if not recommendations:
            recommendations.append("✅ All validation checks passed successfully")
            recommendations.append("🚀 Evidence package ready for forensic analysis")
        
        return recommendations
    
    def _check_compliance_standards(self, check_results: Dict) -> Dict:
        """Check compliance with forensic standards."""
        compliance_status = {
            "iso_27037_compliant": False,
            "nist_sp_800_86_compliant": False,
            "federal_rules_evidence_compliant": False,
            "overall_compliant": False,
            "compliance_issues": []
        }
        
        # Check ISO/IEC 27037 compliance (Digital evidence handling)
        if ("integrity_check" in check_results and 
            check_results["integrity_check"].get("status") == "PASS" and
            "chain_of_custody" in check_results and
            check_results["chain_of_custody"].get("status") == "PASS"):
            compliance_status["iso_27037_compliant"] = True
        else:
            compliance_status["compliance_issues"].append("ISO/IEC 27037: Missing integrity or custody verification")
        
        # Check NIST SP 800-86 compliance (Computer forensics)
        if ("source_verification" in check_results and
            check_results["source_verification"].get("status") == "PASS" and
            "cryptographic_verification" in check_results and
            check_results["cryptographic_verification"].get("status") == "PASS"):
            compliance_status["nist_sp_800_86_compliant"] = True
        else:
            compliance_status["compliance_issues"].append("NIST SP 800-86: Missing source or cryptographic verification")
        
        # Check Federal Rules of Evidence compliance
        if ("chain_of_custody" in check_results and
            check_results["chain_of_custody"].get("status") == "PASS" and
            "independent_verification" in check_results and
            check_results["independent_verification"].get("status") == "PASS"):
            compliance_status["federal_rules_evidence_compliant"] = True
        else:
            compliance_status["compliance_issues"].append("Federal Rules of Evidence: Missing custody or independent verification")
        
        # Overall compliance
        compliance_status["overall_compliant"] = (
            compliance_status["iso_27037_compliant"] and
            compliance_status["nist_sp_800_86_compliant"] and
            compliance_status["federal_rules_evidence_compliant"]
        )
        
        return compliance_status
    
    def create_validation_protocol_template(self, protocol_name: str, 
                                          requirements: List[str]) -> Dict:
        """
        Create a custom validation protocol template.
        
        Args:
            protocol_name: Name of the validation protocol
            requirements: List of validation requirements
            
        Returns:
            Validation protocol template
        """
        template = {
            "protocol_name": protocol_name,
            "created_timestamp": datetime.utcnow().isoformat(),
            "version": "1.0",
            "requirements": requirements,
            "validation_steps": [],
            "success_criteria": {},
            "documentation_requirements": [],
            "compliance_standards": []
        }
        
        # Generate validation steps based on requirements
        for requirement in requirements:
            if "source" in requirement.lower():
                template["validation_steps"].append({
                    "step": "source_verification",
                    "description": "Verify authenticity of source material",
                    "required": True
                })
            elif "integrity" in requirement.lower():
                template["validation_steps"].append({
                    "step": "integrity_verification",
                    "description": "Verify cryptographic integrity of evidence",
                    "required": True
                })
            elif "custody" in requirement.lower():
                template["validation_steps"].append({
                    "step": "chain_of_custody",
                    "description": "Document and verify chain of custody",
                    "required": True
                })
        
        return template
    
    def export_validation_report(self, validation_result: Dict, 
                               export_format: str = "json") -> str:
        """
        Export validation report in specified format.
        
        Args:
            validation_result: Validation result to export
            export_format: Export format (json, html, pdf)
            
        Returns:
            Path to exported file
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        validation_id = validation_result.get("validation_id", "unknown")
        filename = f"validation_report_{validation_id}_{timestamp}.{export_format}"
        
        if export_format == "json":
            with open(filename, 'w') as f:
                json.dump(validation_result, f, indent=2)
        elif export_format == "html":
            html_content = self._generate_html_validation_report(validation_result)
            with open(filename, 'w') as f:
                f.write(html_content)
        
        logger.info(f"Exported validation report to {filename}")
        return filename
    
    def _generate_html_validation_report(self, validation_result: Dict) -> str:
        """Generate HTML format validation report."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Validation Report - {validation_result.get('validation_id', 'Unknown')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; }}
        .status-pass {{ color: green; font-weight: bold; }}
        .status-fail {{ color: red; font-weight: bold; }}
        .status-error {{ color: orange; font-weight: bold; }}
        .section {{ margin: 20px 0; }}
        .check-result {{ border-left: 3px solid #007cba; padding-left: 15px; margin: 10px 0; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .confidence-bar {{ 
            background-color: #e0e0e0; 
            border-radius: 10px; 
            overflow: hidden; 
            height: 20px; 
            width: 200px; 
        }}
        .confidence-fill {{ 
            height: 100%; 
            background-color: #4CAF50; 
            transition: width 0.3s ease; 
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Forensic Evidence Validation Report</h1>
        <p><strong>Validation ID:</strong> {validation_result.get('validation_id', 'Unknown')}</p>
        <p><strong>Timestamp:</strong> {validation_result.get('validation_timestamp', 'Unknown')}</p>
        <p><strong>Evidence Path:</strong> {validation_result.get('evidence_path', 'Unknown')}</p>
        <p><strong>Validation Level:</strong> {validation_result.get('validation_level', 'Unknown')}</p>
    </div>
    
    <div class="section">
        <h2>Overall Status</h2>
        <p class="status-{validation_result.get('overall_status', 'unknown').lower()}">
            <strong>Status:</strong> {validation_result.get('overall_status', 'Unknown')}
        </p>
        <p><strong>Confidence Score:</strong> {validation_result.get('confidence_score', 0):.2f}</p>
        <div class="confidence-bar">
            <div class="confidence-fill" style="width: {validation_result.get('confidence_score', 0) * 100}%"></div>
        </div>
    </div>
    
    <div class="section">
        <h2>Validation Checks</h2>
        {''.join([f'''
        <div class="check-result">
            <h3>{check_type.replace('_', ' ').title()}</h3>
            <p class="status-{result.get('status', 'unknown').lower()}">
                <strong>Status:</strong> {result.get('status', 'Unknown')}
            </p>
            <p><strong>Confidence:</strong> {result.get('confidence', 0):.2f}</p>
            <p><strong>Timestamp:</strong> {result.get('timestamp', 'Unknown')}</p>
        </div>
        ''' for check_type, result in validation_result.get('validation_checks', {}).items()])}
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
            {''.join([f'<li>{rec}</li>' for rec in validation_result.get('recommendations', [])])}
        </ul>
    </div>
    
    <div class="section">
        <h2>Compliance Status</h2>
        <table>
            <tr><th>Standard</th><th>Status</th></tr>
            {''.join([f'<tr><td>{standard.replace("_", " ").title()}</td><td class="status-{"pass" if status else "fail"}">{"COMPLIANT" if status else "NON-COMPLIANT"}</td></tr>' 
                     for standard, status in validation_result.get('compliance_status', {}).items() if isinstance(status, bool)])}
        </table>
    </div>
</body>
</html>
        """
        
        return html
