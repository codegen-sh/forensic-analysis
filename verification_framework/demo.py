#!/usr/bin/env python3
"""
Independent Verification and Chain of Custody Framework Demo

This script demonstrates the key features of the verification framework
including source authentication, chain of custody, and validation protocols.
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import the framework
sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_framework import (
    SourceAuthenticator,
    ChainOfCustodyManager,
    CryptographicVerifier,
    ValidationProtocols
)


def create_demo_video_file():
    """Create a demo video file for testing purposes."""
    demo_file = "demo_video.mp4"
    
    # Create a simple demo file with some content
    with open(demo_file, 'wb') as f:
        f.write(b"DEMO VIDEO FILE - This is a test file for verification framework demonstration")
    
    print(f"✅ Created demo video file: {demo_file}")
    return demo_file


def demo_source_authentication():
    """Demonstrate source authentication capabilities."""
    print("\n" + "="*60)
    print("🔍 SOURCE AUTHENTICATION DEMO")
    print("="*60)
    
    # Create demo file
    demo_file = create_demo_video_file()
    
    # Initialize source authenticator
    authenticator = SourceAuthenticator()
    
    # Add the demo file as a known source
    metadata = {
        "description": "Demo video for verification framework testing",
        "case_number": "DEMO-001",
        "created_by": "Verification Framework Demo"
    }
    
    success = authenticator.add_verified_source(
        file_path=demo_file,
        source_type="demo_source",
        metadata=metadata
    )
    
    if success:
        print("✅ Added demo file as verified source")
    
    # Verify the file against known sources
    verification_result = authenticator.verify_against_doj_source(demo_file)
    print(f"📋 Verification Status: {verification_result['verification_status']}")
    print(f"🔒 File Hash (SHA256): {verification_result['file_hash_sha256'][:16]}...")
    
    # Generate comprehensive verification report
    report = authenticator.generate_verification_report(demo_file)
    print(f"📊 Generated verification report with {len(report['verification_report']['recommendations'])} recommendations")
    
    # Clean up
    os.remove(demo_file)
    print(f"🧹 Cleaned up demo file: {demo_file}")


def demo_chain_of_custody():
    """Demonstrate chain of custody management."""
    print("\n" + "="*60)
    print("📋 CHAIN OF CUSTODY DEMO")
    print("="*60)
    
    # Create demo file
    demo_file = create_demo_video_file()
    
    # Initialize custody manager
    custody_manager = ChainOfCustodyManager()
    
    # Create evidence item
    source_info = {
        "description": "Demo surveillance video for testing",
        "source_type": "demo_evidence",
        "acquisition_method": "file_system_copy",
        "case_number": "DEMO-CUSTODY-001"
    }
    
    custodian_info = {
        "name": "Demo Forensic Analyst",
        "organization": "Verification Framework Demo Lab",
        "contact": "demo@verification-framework.org",
        "badge_number": "DEMO-001"
    }
    
    evidence_id = custody_manager.create_evidence_item(
        file_path=demo_file,
        source_info=source_info,
        custodian_info=custodian_info
    )
    
    print(f"📝 Created evidence item: {evidence_id[:8]}...")
    
    # Add integrity check
    integrity_result = {
        "status": "PASS",
        "hash_sha256": "demo_hash_value",
        "verification_method": "multi_algorithm_verification"
    }
    
    custody_manager.add_integrity_check(
        evidence_id=evidence_id,
        check_type="cryptographic_verification",
        check_result=integrity_result,
        performed_by={"name": "Automated Verification System", "timestamp": "2024-01-15T10:00:00Z"}
    )
    
    print("🔍 Added integrity check to evidence record")
    
    # Log access
    custody_manager.log_access(
        evidence_id=evidence_id,
        accessor_info={"name": "Demo Analyst", "role": "Forensic Examiner"},
        access_purpose="Demonstration of verification framework",
        access_notes="Accessed for framework demonstration purposes"
    )
    
    print("📊 Logged evidence access")
    
    # Generate custody report
    custody_report = custody_manager.generate_custody_report(evidence_id)
    summary = custody_report["custody_report"]["summary"]
    
    print(f"📋 Custody Report Summary:")
    print(f"   - Total Events: {summary['total_events']}")
    print(f"   - Integrity Checks: {summary['total_integrity_checks']}")
    print(f"   - Access Logs: {summary['total_access_logs']}")
    print(f"   - Current Status: {summary['current_status']}")
    
    # Clean up
    os.remove(demo_file)
    print(f"🧹 Cleaned up demo file: {demo_file}")


def demo_cryptographic_verification():
    """Demonstrate cryptographic verification capabilities."""
    print("\n" + "="*60)
    print("🔐 CRYPTOGRAPHIC VERIFICATION DEMO")
    print("="*60)
    
    # Create demo file
    demo_file = create_demo_video_file()
    
    # Initialize cryptographic verifier
    verifier = CryptographicVerifier()
    
    # Calculate multiple hashes
    hashes = verifier.calculate_multiple_hashes(demo_file)
    print("🔢 Calculated multiple hashes:")
    for algorithm, hash_value in hashes.items():
        print(f"   - {algorithm.upper()}: {hash_value[:16]}...")
    
    # Create integrity manifest
    manifest = verifier.create_integrity_manifest(demo_file, {
        "purpose": "Verification framework demonstration",
        "analyst": "Demo User"
    })
    
    print(f"📄 Created integrity manifest (version {manifest['manifest_version']})")
    
    # Verify integrity
    verification = verifier.verify_integrity_manifest(demo_file, manifest)
    print(f"✅ Integrity verification: {verification['verification_status']}")
    print(f"🎯 Overall integrity: {verification['overall_integrity']}")
    
    # Create verification chain
    chain_entry = verifier.create_verification_chain(demo_file)
    print(f"⛓️ Created verification chain entry: {chain_entry['chain_id']}")
    
    # Generate comprehensive verification report
    verification_report = verifier.create_verification_report(demo_file)
    assessment = verification_report["verification_report"]["overall_assessment"]
    
    print(f"📊 Verification Report:")
    print(f"   - Success Rate: {assessment['success_rate']:.2%}")
    print(f"   - Overall Status: {assessment['overall_status']}")
    
    # Clean up
    os.remove(demo_file)
    print(f"🧹 Cleaned up demo file: {demo_file}")


def demo_validation_protocols():
    """Demonstrate validation protocols and compliance checking."""
    print("\n" + "="*60)
    print("✅ VALIDATION PROTOCOLS DEMO")
    print("="*60)
    
    # Create demo file
    demo_file = create_demo_video_file()
    
    # Initialize validation protocols
    validator = ValidationProtocols()
    
    # Test different validation levels
    validation_levels = ["basic", "standard", "forensic"]
    
    for level in validation_levels:
        print(f"\n🔍 Testing {level.upper()} validation level:")
        
        result = validator.validate_evidence_package(demo_file, level)
        
        print(f"   - Status: {result['overall_status']}")
        print(f"   - Confidence Score: {result['confidence_score']:.2%}")
        print(f"   - Checks Performed: {len(result['validation_checks'])}")
        
        # Show compliance status
        compliance = result['compliance_status']
        compliant_standards = sum(1 for k, v in compliance.items() 
                                if isinstance(v, bool) and v)
        total_standards = sum(1 for k, v in compliance.items() 
                            if isinstance(v, bool))
        
        print(f"   - Compliance: {compliant_standards}/{total_standards} standards")
        
        # Show top recommendations
        recommendations = result['recommendations'][:2]  # Show first 2
        if recommendations:
            print(f"   - Key Recommendations:")
            for rec in recommendations:
                print(f"     • {rec}")
    
    # Export validation report
    final_result = validator.validate_evidence_package(demo_file, "forensic")
    report_path = validator.export_validation_report(final_result, "json")
    
    print(f"\n📄 Exported validation report: {report_path}")
    
    # Show report summary
    with open(report_path, 'r') as f:
        report_data = json.load(f)
    
    print(f"📊 Report Summary:")
    print(f"   - Validation ID: {report_data['validation_id']}")
    print(f"   - Evidence Path: {report_data['evidence_path']}")
    print(f"   - Overall Status: {report_data['overall_status']}")
    
    # Clean up
    os.remove(demo_file)
    os.remove(report_path)
    print(f"🧹 Cleaned up demo files")


def demo_complete_workflow():
    """Demonstrate a complete verification workflow."""
    print("\n" + "="*60)
    print("🚀 COMPLETE VERIFICATION WORKFLOW DEMO")
    print("="*60)
    
    # Create demo file
    demo_file = create_demo_video_file()
    
    print("📋 Step 1: Source Authentication")
    authenticator = SourceAuthenticator()
    auth_result = authenticator.verify_against_doj_source(demo_file)
    print(f"   ✅ Authentication completed: {auth_result['verification_status']}")
    
    print("\n📋 Step 2: Chain of Custody Establishment")
    custody_manager = ChainOfCustodyManager()
    evidence_id = custody_manager.create_evidence_item(
        file_path=demo_file,
        source_info={"description": "Complete workflow demo", "type": "demo"},
        custodian_info={"name": "Demo Workflow", "org": "Framework Demo"}
    )
    print(f"   ✅ Evidence item created: {evidence_id[:8]}...")
    
    print("\n📋 Step 3: Cryptographic Verification")
    verifier = CryptographicVerifier()
    crypto_report = verifier.create_verification_report(demo_file)
    crypto_status = crypto_report["verification_report"]["overall_assessment"]["overall_status"]
    print(f"   ✅ Cryptographic verification: {crypto_status}")
    
    print("\n📋 Step 4: Comprehensive Validation")
    validator = ValidationProtocols()
    validation_result = validator.validate_evidence_package(demo_file, "forensic")
    print(f"   ✅ Validation completed: {validation_result['overall_status']}")
    print(f"   📊 Confidence Score: {validation_result['confidence_score']:.2%}")
    
    print("\n📋 Step 5: Compliance Assessment")
    compliance = validation_result['compliance_status']
    if compliance['overall_compliant']:
        print("   ✅ All compliance standards met")
    else:
        print("   ⚠️ Some compliance issues found:")
        for issue in compliance['compliance_issues']:
            print(f"      - {issue}")
    
    print("\n📋 Step 6: Report Generation")
    report_path = validator.export_validation_report(validation_result, "html")
    print(f"   ✅ HTML report generated: {report_path}")
    
    # Final summary
    print(f"\n🎉 WORKFLOW COMPLETE!")
    print(f"   - Evidence verified and documented")
    print(f"   - Chain of custody established")
    print(f"   - Cryptographic integrity confirmed")
    print(f"   - Compliance standards checked")
    print(f"   - Professional report generated")
    
    # Clean up
    os.remove(demo_file)
    os.remove(report_path)
    print(f"\n🧹 Demo cleanup completed")


def main():
    """Run the complete verification framework demonstration."""
    print("🔬 INDEPENDENT VERIFICATION AND CHAIN OF CUSTODY FRAMEWORK")
    print("🎯 Comprehensive Demonstration")
    print("=" * 80)
    
    try:
        # Run individual component demos
        demo_source_authentication()
        demo_chain_of_custody()
        demo_cryptographic_verification()
        demo_validation_protocols()
        
        # Run complete workflow demo
        demo_complete_workflow()
        
        print("\n" + "="*80)
        print("✅ ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("📚 Review the output above to understand framework capabilities")
        print("🔗 See verification_framework/README.md for detailed documentation")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("🔧 Please check the framework installation and dependencies")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
