"""
Cryptographic Verification Module

This module provides cryptographic tools for verifying video integrity,
digital signatures, and implementing blockchain-based verification.
"""

import hashlib
import hmac
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

logger = logging.getLogger(__name__)


class CryptographicVerifier:
    """
    Provides cryptographic verification tools for digital evidence integrity.
    Supports multiple hash algorithms, digital signatures, and verification chains.
    """
    
    def __init__(self, key_store_path: str = "verification_framework/keys"):
        """
        Initialize the cryptographic verifier.
        
        Args:
            key_store_path: Path to store cryptographic keys
        """
        self.key_store_path = Path(key_store_path)
        self.key_store_path.mkdir(parents=True, exist_ok=True)
        
        if not CRYPTO_AVAILABLE:
            logger.warning("Cryptography library not available. Some features will be limited.")
    
    def calculate_multiple_hashes(self, file_path: str) -> Dict[str, str]:
        """
        Calculate multiple cryptographic hashes for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary of hash algorithm names to hash values
        """
        algorithms = ['md5', 'sha1', 'sha256', 'sha512']
        hash_objects = {alg: getattr(hashlib, alg)() for alg in algorithms}
        
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    for hash_obj in hash_objects.values():
                        hash_obj.update(chunk)
            
            return {alg: hash_obj.hexdigest() for alg, hash_obj in hash_objects.items()}
        
        except Exception as e:
            logger.error(f"Error calculating hashes for {file_path}: {e}")
            raise
    
    def create_integrity_manifest(self, file_path: str, metadata: Dict = None) -> Dict:
        """
        Create a comprehensive integrity manifest for a file.
        
        Args:
            file_path: Path to the file
            metadata: Additional metadata to include
            
        Returns:
            Integrity manifest dictionary
        """
        file_stat = os.stat(file_path)
        hashes = self.calculate_multiple_hashes(file_path)
        
        manifest = {
            "manifest_version": "1.0",
            "created_timestamp": datetime.utcnow().isoformat(),
            "file_information": {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "file_size_bytes": file_stat.st_size,
                "creation_time": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                "modification_time": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
            },
            "cryptographic_hashes": hashes,
            "verification_metadata": metadata or {},
            "verification_timestamp": datetime.utcnow().isoformat()
        }
        
        # Add manifest hash (hash of the manifest itself)
        manifest_json = json.dumps(manifest, sort_keys=True)
        manifest["manifest_hash"] = hashlib.sha256(manifest_json.encode()).hexdigest()
        
        return manifest
    
    def verify_integrity_manifest(self, file_path: str, manifest: Dict) -> Dict:
        """
        Verify a file against its integrity manifest.
        
        Args:
            file_path: Path to the file to verify
            manifest: Integrity manifest to verify against
            
        Returns:
            Verification result dictionary
        """
        verification_result = {
            "verification_timestamp": datetime.utcnow().isoformat(),
            "file_path": file_path,
            "manifest_version": manifest.get("manifest_version"),
            "verification_status": "UNKNOWN",
            "hash_verifications": {},
            "file_size_match": False,
            "overall_integrity": False
        }
        
        try:
            # Verify file exists
            if not os.path.exists(file_path):
                verification_result["verification_status"] = "FILE_NOT_FOUND"
                return verification_result
            
            # Verify file size
            current_size = os.path.getsize(file_path)
            expected_size = manifest["file_information"]["file_size_bytes"]
            verification_result["file_size_match"] = current_size == expected_size
            
            # Verify hashes
            current_hashes = self.calculate_multiple_hashes(file_path)
            expected_hashes = manifest["cryptographic_hashes"]
            
            all_hashes_match = True
            for algorithm, expected_hash in expected_hashes.items():
                current_hash = current_hashes.get(algorithm)
                hash_match = current_hash == expected_hash
                
                verification_result["hash_verifications"][algorithm] = {
                    "expected": expected_hash,
                    "current": current_hash,
                    "match": hash_match
                }
                
                if not hash_match:
                    all_hashes_match = False
            
            # Overall integrity assessment
            verification_result["overall_integrity"] = (
                verification_result["file_size_match"] and all_hashes_match
            )
            
            if verification_result["overall_integrity"]:
                verification_result["verification_status"] = "INTEGRITY_VERIFIED"
            else:
                verification_result["verification_status"] = "INTEGRITY_COMPROMISED"
        
        except Exception as e:
            logger.error(f"Error verifying integrity: {e}")
            verification_result["verification_status"] = "VERIFICATION_ERROR"
            verification_result["error_message"] = str(e)
        
        return verification_result
    
    def create_verification_chain(self, file_path: str, previous_hash: str = None) -> Dict:
        """
        Create a verification chain entry linking to previous verifications.
        
        Args:
            file_path: Path to the file
            previous_hash: Hash of the previous verification in the chain
            
        Returns:
            Verification chain entry
        """
        manifest = self.create_integrity_manifest(file_path)
        
        chain_entry = {
            "chain_id": f"VC_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.utcnow().isoformat(),
            "file_manifest": manifest,
            "previous_verification_hash": previous_hash,
            "verification_method": "cryptographic_hash_chain"
        }
        
        # Create chain hash
        chain_data = json.dumps(chain_entry, sort_keys=True)
        chain_entry["chain_hash"] = hashlib.sha256(chain_data.encode()).hexdigest()
        
        return chain_entry
    
    def generate_hmac_signature(self, file_path: str, secret_key: bytes) -> str:
        """
        Generate HMAC signature for a file.
        
        Args:
            file_path: Path to the file
            secret_key: Secret key for HMAC
            
        Returns:
            HMAC signature as hexadecimal string
        """
        hmac_obj = hmac.new(secret_key, digestmod=hashlib.sha256)
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hmac_obj.update(chunk)
        
        return hmac_obj.hexdigest()
    
    def verify_hmac_signature(self, file_path: str, signature: str, secret_key: bytes) -> bool:
        """
        Verify HMAC signature for a file.
        
        Args:
            file_path: Path to the file
            signature: Expected HMAC signature
            secret_key: Secret key for HMAC
            
        Returns:
            True if signature is valid
        """
        try:
            current_signature = self.generate_hmac_signature(file_path, secret_key)
            return hmac.compare_digest(signature, current_signature)
        except Exception as e:
            logger.error(f"Error verifying HMAC signature: {e}")
            return False
    
    def create_digital_signature(self, file_path: str, private_key_path: str = None) -> Dict:
        """
        Create a digital signature for a file using RSA.
        
        Args:
            file_path: Path to the file to sign
            private_key_path: Path to private key (will generate if not provided)
            
        Returns:
            Digital signature information
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available for digital signatures")
        
        # Generate or load private key
        if private_key_path and os.path.exists(private_key_path):
            with open(private_key_path, 'rb') as f:
                private_key = serialization.load_pem_private_key(f.read(), password=None)
        else:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # Save private key
            if not private_key_path:
                private_key_path = self.key_store_path / f"private_key_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pem"
            
            with open(private_key_path, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
        
        # Calculate file hash
        file_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                file_hash.update(chunk)
        
        # Create signature
        signature = private_key.sign(
            file_hash.digest(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Get public key
        public_key = private_key.public_key()
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return {
            "signature": signature.hex(),
            "public_key_pem": public_key_pem.decode(),
            "file_hash": file_hash.hexdigest(),
            "signature_algorithm": "RSA-PSS-SHA256",
            "created_timestamp": datetime.utcnow().isoformat(),
            "private_key_path": str(private_key_path)
        }
    
    def verify_digital_signature(self, file_path: str, signature_info: Dict) -> bool:
        """
        Verify a digital signature for a file.
        
        Args:
            file_path: Path to the file
            signature_info: Signature information from create_digital_signature
            
        Returns:
            True if signature is valid
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available for signature verification")
        
        try:
            # Load public key
            public_key = serialization.load_pem_public_key(
                signature_info["public_key_pem"].encode()
            )
            
            # Calculate current file hash
            file_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    file_hash.update(chunk)
            
            # Verify file hash matches
            if file_hash.hexdigest() != signature_info["file_hash"]:
                return False
            
            # Verify signature
            signature_bytes = bytes.fromhex(signature_info["signature"])
            
            public_key.verify(
                signature_bytes,
                file_hash.digest(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Error verifying digital signature: {e}")
            return False
    
    def create_verification_report(self, file_path: str, verification_methods: List[str] = None) -> Dict:
        """
        Create a comprehensive cryptographic verification report.
        
        Args:
            file_path: Path to the file to verify
            verification_methods: List of verification methods to use
            
        Returns:
            Comprehensive verification report
        """
        if verification_methods is None:
            verification_methods = ["hashes", "manifest", "chain"]
        
        report = {
            "verification_report": {
                "report_id": f"CVR_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "generated_timestamp": datetime.utcnow().isoformat(),
                "file_path": file_path,
                "verification_methods": verification_methods,
                "results": {}
            }
        }
        
        # Multiple hash verification
        if "hashes" in verification_methods:
            try:
                hashes = self.calculate_multiple_hashes(file_path)
                report["verification_report"]["results"]["hash_verification"] = {
                    "status": "SUCCESS",
                    "hashes": hashes
                }
            except Exception as e:
                report["verification_report"]["results"]["hash_verification"] = {
                    "status": "ERROR",
                    "error": str(e)
                }
        
        # Integrity manifest
        if "manifest" in verification_methods:
            try:
                manifest = self.create_integrity_manifest(file_path)
                report["verification_report"]["results"]["integrity_manifest"] = {
                    "status": "SUCCESS",
                    "manifest": manifest
                }
            except Exception as e:
                report["verification_report"]["results"]["integrity_manifest"] = {
                    "status": "ERROR",
                    "error": str(e)
                }
        
        # Verification chain
        if "chain" in verification_methods:
            try:
                chain_entry = self.create_verification_chain(file_path)
                report["verification_report"]["results"]["verification_chain"] = {
                    "status": "SUCCESS",
                    "chain_entry": chain_entry
                }
            except Exception as e:
                report["verification_report"]["results"]["verification_chain"] = {
                    "status": "ERROR",
                    "error": str(e)
                }
        
        # Overall assessment
        successful_methods = sum(1 for result in report["verification_report"]["results"].values() 
                               if result["status"] == "SUCCESS")
        total_methods = len(verification_methods)
        
        report["verification_report"]["overall_assessment"] = {
            "successful_verifications": successful_methods,
            "total_verifications": total_methods,
            "success_rate": successful_methods / total_methods if total_methods > 0 else 0,
            "overall_status": "VERIFIED" if successful_methods == total_methods else "PARTIAL_VERIFICATION"
        }
        
        return report
    
    def export_verification_data(self, verification_data: Dict, 
                               export_path: str = None) -> str:
        """
        Export verification data to a file.
        
        Args:
            verification_data: Verification data to export
            export_path: Path to export file (auto-generated if not provided)
            
        Returns:
            Path to exported file
        """
        if not export_path:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            export_path = f"verification_data_{timestamp}.json"
        
        with open(export_path, 'w') as f:
            json.dump(verification_data, f, indent=2)
        
        logger.info(f"Exported verification data to {export_path}")
        return export_path
