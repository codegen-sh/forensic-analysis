"""
Source Video Authentication Module

This module provides tools for verifying the authenticity of source videos
against original DOJ releases and establishing cryptographic integrity.
"""

import hashlib
import json
import requests
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SourceAuthenticator:
    """
    Handles authentication and verification of source video files against
    official DOJ releases and other authoritative sources.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the source authenticator.
        
        Args:
            config_path: Path to configuration file with known source hashes
        """
        self.config_path = config_path or "verification_framework/known_sources.json"
        self.known_sources = self._load_known_sources()
        
    def _load_known_sources(self) -> Dict:
        """Load known source video hashes and metadata."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load known sources: {e}")
        
        return {
            "doj_releases": {},
            "verified_sources": {},
            "metadata": {
                "last_updated": None,
                "verification_protocol_version": "1.0"
            }
        }
    
    def calculate_file_hash(self, file_path: str, algorithm: str = "sha256") -> str:
        """
        Calculate cryptographic hash of a file.
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm to use (sha256, md5, sha1)
            
        Returns:
            Hexadecimal hash string
        """
        hash_func = getattr(hashlib, algorithm)()
        
        try:
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large videos
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            raise
    
    def verify_against_doj_source(self, file_path: str) -> Dict:
        """
        Verify a video file against known DOJ release hashes.
        
        Args:
            file_path: Path to video file to verify
            
        Returns:
            Verification result dictionary
        """
        file_hash = self.calculate_file_hash(file_path)
        file_size = os.path.getsize(file_path)
        
        verification_result = {
            "file_path": file_path,
            "file_hash_sha256": file_hash,
            "file_size_bytes": file_size,
            "verification_timestamp": datetime.utcnow().isoformat(),
            "doj_match_found": False,
            "verification_status": "UNVERIFIED",
            "matched_source": None,
            "confidence_level": "LOW"
        }
        
        # Check against known DOJ releases
        for source_id, source_data in self.known_sources.get("doj_releases", {}).items():
            if source_data.get("sha256") == file_hash:
                verification_result.update({
                    "doj_match_found": True,
                    "verification_status": "VERIFIED_DOJ_MATCH",
                    "matched_source": source_id,
                    "confidence_level": "HIGH",
                    "source_metadata": source_data
                })
                break
        
        # Check against other verified sources
        if not verification_result["doj_match_found"]:
            for source_id, source_data in self.known_sources.get("verified_sources", {}).items():
                if source_data.get("sha256") == file_hash:
                    verification_result.update({
                        "verification_status": "VERIFIED_SECONDARY_SOURCE",
                        "matched_source": source_id,
                        "confidence_level": "MEDIUM",
                        "source_metadata": source_data
                    })
                    break
        
        return verification_result
    
    def add_verified_source(self, file_path: str, source_type: str, 
                          metadata: Dict) -> bool:
        """
        Add a new verified source to the database.
        
        Args:
            file_path: Path to the verified source file
            source_type: Type of source (doj_release, court_filing, etc.)
            metadata: Additional metadata about the source
            
        Returns:
            True if successfully added
        """
        try:
            file_hash = self.calculate_file_hash(file_path)
            file_size = os.path.getsize(file_path)
            
            source_entry = {
                "sha256": file_hash,
                "file_size_bytes": file_size,
                "source_type": source_type,
                "added_timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata
            }
            
            # Generate unique source ID
            source_id = f"{source_type}_{file_hash[:16]}"
            
            # Add to appropriate category
            if source_type == "doj_release":
                self.known_sources["doj_releases"][source_id] = source_entry
            else:
                self.known_sources["verified_sources"][source_id] = source_entry
            
            # Update metadata
            self.known_sources["metadata"]["last_updated"] = datetime.utcnow().isoformat()
            
            # Save to file
            self._save_known_sources()
            
            logger.info(f"Added verified source: {source_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding verified source: {e}")
            return False
    
    def _save_known_sources(self):
        """Save known sources to configuration file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.known_sources, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving known sources: {e}")
    
    def generate_verification_report(self, file_path: str) -> Dict:
        """
        Generate a comprehensive verification report for a video file.
        
        Args:
            file_path: Path to video file
            
        Returns:
            Comprehensive verification report
        """
        verification_result = self.verify_against_doj_source(file_path)
        
        # Add additional file metadata
        file_stat = os.stat(file_path)
        
        report = {
            "verification_report": {
                "report_id": f"VR_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "generated_timestamp": datetime.utcnow().isoformat(),
                "file_information": {
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "file_size_bytes": verification_result["file_size_bytes"],
                    "file_size_mb": round(verification_result["file_size_bytes"] / (1024*1024), 2),
                    "creation_time": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                    "modification_time": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                },
                "cryptographic_verification": {
                    "sha256_hash": verification_result["file_hash_sha256"],
                    "md5_hash": self.calculate_file_hash(file_path, "md5"),
                    "sha1_hash": self.calculate_file_hash(file_path, "sha1")
                },
                "source_verification": verification_result,
                "recommendations": self._generate_recommendations(verification_result)
            }
        }
        
        return report
    
    def _generate_recommendations(self, verification_result: Dict) -> List[str]:
        """Generate recommendations based on verification results."""
        recommendations = []
        
        if verification_result["verification_status"] == "VERIFIED_DOJ_MATCH":
            recommendations.append("✅ File verified against official DOJ release - proceed with analysis")
            recommendations.append("📋 Document this verification in chain of custody")
        elif verification_result["verification_status"] == "VERIFIED_SECONDARY_SOURCE":
            recommendations.append("⚠️ File matches secondary source - consider additional verification")
            recommendations.append("🔍 Seek independent confirmation from DOJ source if possible")
        else:
            recommendations.append("❌ File could not be verified against known sources")
            recommendations.append("🚨 CRITICAL: Establish source authenticity before analysis")
            recommendations.append("📞 Contact DOJ or court records for official copy")
            recommendations.append("🔒 Do not proceed with forensic analysis until verified")
        
        return recommendations
    
    def batch_verify_files(self, file_paths: List[str]) -> Dict:
        """
        Verify multiple files in batch.
        
        Args:
            file_paths: List of file paths to verify
            
        Returns:
            Batch verification results
        """
        results = {
            "batch_id": f"BV_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "total_files": len(file_paths),
            "verified_files": 0,
            "unverified_files": 0,
            "results": []
        }
        
        for file_path in file_paths:
            try:
                verification = self.verify_against_doj_source(file_path)
                results["results"].append(verification)
                
                if verification["verification_status"].startswith("VERIFIED"):
                    results["verified_files"] += 1
                else:
                    results["unverified_files"] += 1
                    
            except Exception as e:
                logger.error(f"Error verifying {file_path}: {e}")
                results["results"].append({
                    "file_path": file_path,
                    "verification_status": "ERROR",
                    "error_message": str(e)
                })
                results["unverified_files"] += 1
        
        return results
