"""
Chain of Custody Management Module

This module provides comprehensive chain of custody documentation and tracking
for digital evidence in forensic analysis.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ChainOfCustodyManager:
    """
    Manages chain of custody documentation for digital evidence.
    Ensures proper tracking of evidence handling, transfers, and analysis.
    """
    
    def __init__(self, custody_db_path: str = "verification_framework/custody_records.json"):
        """
        Initialize the chain of custody manager.
        
        Args:
            custody_db_path: Path to the custody records database
        """
        self.custody_db_path = custody_db_path
        self.custody_records = self._load_custody_records()
    
    def _load_custody_records(self) -> Dict:
        """Load existing custody records from database."""
        try:
            if Path(self.custody_db_path).exists():
                with open(self.custody_db_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load custody records: {e}")
        
        return {
            "evidence_items": {},
            "custody_chains": {},
            "metadata": {
                "database_version": "1.0",
                "created": datetime.utcnow().isoformat(),
                "last_updated": None
            }
        }
    
    def _save_custody_records(self):
        """Save custody records to database."""
        try:
            Path(self.custody_db_path).parent.mkdir(parents=True, exist_ok=True)
            self.custody_records["metadata"]["last_updated"] = datetime.utcnow().isoformat()
            
            with open(self.custody_db_path, 'w') as f:
                json.dump(self.custody_records, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving custody records: {e}")
    
    def create_evidence_item(self, file_path: str, source_info: Dict, 
                           custodian_info: Dict) -> str:
        """
        Create a new evidence item in the chain of custody.
        
        Args:
            file_path: Path to the evidence file
            source_info: Information about the source of the evidence
            custodian_info: Information about the initial custodian
            
        Returns:
            Evidence item ID
        """
        evidence_id = str(uuid.uuid4())
        
        evidence_item = {
            "evidence_id": evidence_id,
            "file_path": file_path,
            "file_name": Path(file_path).name,
            "creation_timestamp": datetime.utcnow().isoformat(),
            "source_information": source_info,
            "initial_custodian": custodian_info,
            "current_custodian": custodian_info,
            "status": "ACTIVE",
            "integrity_checks": [],
            "access_log": []
        }
        
        self.custody_records["evidence_items"][evidence_id] = evidence_item
        
        # Create initial custody chain entry
        self._add_custody_event(evidence_id, "EVIDENCE_CREATED", custodian_info, {
            "action": "Initial evidence registration",
            "source": source_info.get("description", "Unknown source")
        })
        
        self._save_custody_records()
        logger.info(f"Created evidence item: {evidence_id}")
        
        return evidence_id
    
    def transfer_custody(self, evidence_id: str, new_custodian: Dict, 
                        transfer_reason: str, transfer_notes: str = "") -> bool:
        """
        Transfer custody of evidence to a new custodian.
        
        Args:
            evidence_id: ID of the evidence item
            new_custodian: Information about the new custodian
            transfer_reason: Reason for the transfer
            transfer_notes: Additional notes about the transfer
            
        Returns:
            True if transfer successful
        """
        if evidence_id not in self.custody_records["evidence_items"]:
            logger.error(f"Evidence item {evidence_id} not found")
            return False
        
        evidence_item = self.custody_records["evidence_items"][evidence_id]
        previous_custodian = evidence_item["current_custodian"]
        
        # Update current custodian
        evidence_item["current_custodian"] = new_custodian
        
        # Add custody transfer event
        self._add_custody_event(evidence_id, "CUSTODY_TRANSFER", new_custodian, {
            "previous_custodian": previous_custodian,
            "transfer_reason": transfer_reason,
            "transfer_notes": transfer_notes
        })
        
        self._save_custody_records()
        logger.info(f"Transferred custody of {evidence_id} to {new_custodian.get('name', 'Unknown')}")
        
        return True
    
    def add_integrity_check(self, evidence_id: str, check_type: str, 
                          check_result: Dict, performed_by: Dict) -> bool:
        """
        Add an integrity check record to the evidence item.
        
        Args:
            evidence_id: ID of the evidence item
            check_type: Type of integrity check (hash, signature, etc.)
            check_result: Results of the integrity check
            performed_by: Information about who performed the check
            
        Returns:
            True if check added successfully
        """
        if evidence_id not in self.custody_records["evidence_items"]:
            logger.error(f"Evidence item {evidence_id} not found")
            return False
        
        integrity_check = {
            "check_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "check_type": check_type,
            "performed_by": performed_by,
            "result": check_result,
            "status": check_result.get("status", "UNKNOWN")
        }
        
        self.custody_records["evidence_items"][evidence_id]["integrity_checks"].append(integrity_check)
        
        # Add custody event
        self._add_custody_event(evidence_id, "INTEGRITY_CHECK", performed_by, {
            "check_type": check_type,
            "check_status": integrity_check["status"],
            "check_id": integrity_check["check_id"]
        })
        
        self._save_custody_records()
        logger.info(f"Added integrity check for {evidence_id}: {check_type}")
        
        return True
    
    def log_access(self, evidence_id: str, accessor_info: Dict, 
                  access_purpose: str, access_notes: str = "") -> bool:
        """
        Log access to evidence item.
        
        Args:
            evidence_id: ID of the evidence item
            accessor_info: Information about who accessed the evidence
            access_purpose: Purpose of the access
            access_notes: Additional notes about the access
            
        Returns:
            True if access logged successfully
        """
        if evidence_id not in self.custody_records["evidence_items"]:
            logger.error(f"Evidence item {evidence_id} not found")
            return False
        
        access_entry = {
            "access_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "accessor": accessor_info,
            "purpose": access_purpose,
            "notes": access_notes
        }
        
        self.custody_records["evidence_items"][evidence_id]["access_log"].append(access_entry)
        
        # Add custody event
        self._add_custody_event(evidence_id, "EVIDENCE_ACCESS", accessor_info, {
            "access_purpose": access_purpose,
            "access_id": access_entry["access_id"]
        })
        
        self._save_custody_records()
        logger.info(f"Logged access to {evidence_id} by {accessor_info.get('name', 'Unknown')}")
        
        return True
    
    def _add_custody_event(self, evidence_id: str, event_type: str, 
                          actor: Dict, event_data: Dict):
        """Add an event to the custody chain."""
        if evidence_id not in self.custody_records["custody_chains"]:
            self.custody_records["custody_chains"][evidence_id] = []
        
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "actor": actor,
            "event_data": event_data
        }
        
        self.custody_records["custody_chains"][evidence_id].append(event)
    
    def generate_custody_report(self, evidence_id: str) -> Dict:
        """
        Generate a comprehensive chain of custody report.
        
        Args:
            evidence_id: ID of the evidence item
            
        Returns:
            Comprehensive custody report
        """
        if evidence_id not in self.custody_records["evidence_items"]:
            return {"error": f"Evidence item {evidence_id} not found"}
        
        evidence_item = self.custody_records["evidence_items"][evidence_id]
        custody_chain = self.custody_records["custody_chains"].get(evidence_id, [])
        
        report = {
            "custody_report": {
                "report_id": f"CR_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "generated_timestamp": datetime.utcnow().isoformat(),
                "evidence_information": evidence_item,
                "custody_chain": custody_chain,
                "summary": {
                    "total_events": len(custody_chain),
                    "total_transfers": len([e for e in custody_chain if e["event_type"] == "CUSTODY_TRANSFER"]),
                    "total_integrity_checks": len(evidence_item["integrity_checks"]),
                    "total_access_logs": len(evidence_item["access_log"]),
                    "current_status": evidence_item["status"],
                    "current_custodian": evidence_item["current_custodian"]
                },
                "integrity_status": self._assess_integrity_status(evidence_item),
                "compliance_check": self._check_compliance(evidence_item, custody_chain)
            }
        }
        
        return report
    
    def _assess_integrity_status(self, evidence_item: Dict) -> Dict:
        """Assess the integrity status of evidence based on checks."""
        integrity_checks = evidence_item["integrity_checks"]
        
        if not integrity_checks:
            return {
                "status": "NO_CHECKS",
                "message": "No integrity checks performed",
                "recommendation": "Perform integrity verification immediately"
            }
        
        latest_check = max(integrity_checks, key=lambda x: x["timestamp"])
        
        if latest_check["status"] == "PASS":
            return {
                "status": "VERIFIED",
                "message": "Latest integrity check passed",
                "last_check": latest_check["timestamp"],
                "recommendation": "Evidence integrity verified"
            }
        else:
            return {
                "status": "COMPROMISED",
                "message": "Latest integrity check failed",
                "last_check": latest_check["timestamp"],
                "recommendation": "CRITICAL: Evidence integrity compromised - investigate immediately"
            }
    
    def _check_compliance(self, evidence_item: Dict, custody_chain: List) -> Dict:
        """Check compliance with chain of custody requirements."""
        compliance_issues = []
        
        # Check for gaps in custody chain
        if len(custody_chain) < 2:
            compliance_issues.append("Insufficient custody chain documentation")
        
        # Check for recent integrity verification
        integrity_checks = evidence_item["integrity_checks"]
        if not integrity_checks:
            compliance_issues.append("No integrity verification performed")
        else:
            latest_check = max(integrity_checks, key=lambda x: x["timestamp"])
            check_time = datetime.fromisoformat(latest_check["timestamp"])
            if (datetime.utcnow() - check_time).days > 30:
                compliance_issues.append("Integrity verification older than 30 days")
        
        # Check for proper documentation
        if not evidence_item.get("source_information", {}).get("description"):
            compliance_issues.append("Insufficient source documentation")
        
        return {
            "compliant": len(compliance_issues) == 0,
            "issues": compliance_issues,
            "recommendations": self._generate_compliance_recommendations(compliance_issues)
        }
    
    def _generate_compliance_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on compliance issues."""
        recommendations = []
        
        for issue in issues:
            if "integrity verification" in issue.lower():
                recommendations.append("🔍 Perform immediate integrity verification")
            elif "custody chain" in issue.lower():
                recommendations.append("📋 Document all custody transfers and access")
            elif "source documentation" in issue.lower():
                recommendations.append("📝 Obtain and document complete source information")
        
        if not issues:
            recommendations.append("✅ Chain of custody meets compliance requirements")
        
        return recommendations
    
    def export_custody_documentation(self, evidence_id: str, 
                                   export_format: str = "json") -> str:
        """
        Export chain of custody documentation in specified format.
        
        Args:
            evidence_id: ID of the evidence item
            export_format: Export format (json, pdf, html)
            
        Returns:
            Path to exported file
        """
        report = self.generate_custody_report(evidence_id)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"custody_report_{evidence_id[:8]}_{timestamp}.{export_format}"
        
        if export_format == "json":
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
        elif export_format == "html":
            html_content = self._generate_html_report(report)
            with open(filename, 'w') as f:
                f.write(html_content)
        
        logger.info(f"Exported custody documentation to {filename}")
        return filename
    
    def _generate_html_report(self, report: Dict) -> str:
        """Generate HTML format custody report."""
        custody_data = report["custody_report"]
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Chain of Custody Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .event {{ border-left: 3px solid #007cba; padding-left: 10px; margin: 10px 0; }}
        .compliance-pass {{ color: green; }}
        .compliance-fail {{ color: red; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Chain of Custody Report</h1>
        <p><strong>Report ID:</strong> {custody_data['report_id']}</p>
        <p><strong>Generated:</strong> {custody_data['generated_timestamp']}</p>
    </div>
    
    <div class="section">
        <h2>Evidence Information</h2>
        <table>
            <tr><th>Evidence ID</th><td>{custody_data['evidence_information']['evidence_id']}</td></tr>
            <tr><th>File Name</th><td>{custody_data['evidence_information']['file_name']}</td></tr>
            <tr><th>Status</th><td>{custody_data['evidence_information']['status']}</td></tr>
            <tr><th>Current Custodian</th><td>{custody_data['evidence_information']['current_custodian'].get('name', 'Unknown')}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Compliance Status</h2>
        <p class="{'compliance-pass' if custody_data['compliance_check']['compliant'] else 'compliance-fail'}">
            <strong>Status:</strong> {'COMPLIANT' if custody_data['compliance_check']['compliant'] else 'NON-COMPLIANT'}
        </p>
        <p><strong>Integrity Status:</strong> {custody_data['integrity_status']['status']}</p>
    </div>
    
    <div class="section">
        <h2>Custody Chain Events</h2>
        {''.join([f'<div class="event"><strong>{event["event_type"]}</strong> - {event["timestamp"]}<br>Actor: {event["actor"].get("name", "Unknown")}</div>' for event in custody_data['custody_chain']])}
    </div>
</body>
</html>
        """
        
        return html
