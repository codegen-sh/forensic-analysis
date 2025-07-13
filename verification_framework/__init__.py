"""
Independent Verification and Chain of Custody Framework

This module provides tools and protocols for establishing independent verification
of source video authenticity and maintaining proper chain of custody documentation
for forensic analysis.
"""

from .source_authenticator import SourceAuthenticator
from .chain_of_custody import ChainOfCustodyManager
from .cryptographic_verifier import CryptographicVerifier
from .validation_protocols import ValidationProtocols

__version__ = "1.0.0"
__author__ = "Forensic Analysis Team"

__all__ = [
    "SourceAuthenticator",
    "ChainOfCustodyManager", 
    "CryptographicVerifier",
    "ValidationProtocols"
]
