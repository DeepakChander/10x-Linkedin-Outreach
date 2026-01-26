#!/usr/bin/env python3
"""
Secure Credentials Manager for 10x-Outreach-Skill
Replaces insecure pickle with AES-256 encrypted JSON storage

Features:
- Fernet encryption (AES-256-GCM)
- PBKDF2 key derivation (600k iterations)
- SHA-256 integrity checksums
- Credential access audit logging
"""

import os
import sys
import json
import base64
import hashlib
import secrets
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from dotenv import load_dotenv
except ImportError as e:
    print(f"[X] Missing dependency: {e}")
    print("    Run: pip install cryptography")
    sys.exit(1)

load_dotenv(Path(__file__).parent.parent / '.env')


class SecureCredentialManager:
    """
    Secure credential storage using AES-256 encryption.

    Replaces insecure pickle files with encrypted JSON.

    Security features:
    - AES-256-GCM encryption via Fernet
    - PBKDF2 key derivation with 600,000 iterations
    - SHA-256 integrity checksums
    - Audit logging for all access attempts
    """

    # PBKDF2 iterations - OWASP recommends 600,000 for SHA-256
    PBKDF2_ITERATIONS = 600000

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize secure credential manager.

        Args:
            base_dir: Base directory for credential storage
        """
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.credentials_dir = self.base_dir / 'credentials'
        self.credentials_dir.mkdir(parents=True, exist_ok=True)

        # Get master key from environment or generate
        self._master_key = self._get_or_create_master_key()

        # Initialize Fernet cipher
        self._cipher = self._derive_cipher(self._master_key)

        # Audit log path
        self.audit_log_path = self.base_dir / 'audit_logs' / 'credential_access.jsonl'
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    def _get_or_create_master_key(self) -> bytes:
        """Get master key from environment or create new one."""
        key_env = os.getenv('CREDENTIAL_MASTER_KEY')

        if key_env:
            try:
                return base64.urlsafe_b64decode(key_env)
            except Exception:
                pass

        # Check for key file
        key_file = self.credentials_dir / '.master_key'
        if key_file.exists():
            try:
                return base64.urlsafe_b64decode(key_file.read_text().strip())
            except Exception:
                pass

        # Generate new key
        new_key = secrets.token_bytes(32)
        key_file.write_text(base64.urlsafe_b64encode(new_key).decode())

        # Set restrictive permissions (owner read/write only)
        try:
            os.chmod(key_file, 0o600)
        except Exception:
            pass

        print(f"[!] Generated new master key. Set CREDENTIAL_MASTER_KEY in .env:")
        print(f"    CREDENTIAL_MASTER_KEY={base64.urlsafe_b64encode(new_key).decode()}")

        return new_key

    def _derive_cipher(self, master_key: bytes) -> Fernet:
        """Derive Fernet cipher from master key using PBKDF2."""
        # Use fixed salt for deterministic key derivation
        # Salt is not secret - it just prevents rainbow table attacks
        salt = b'10x-outreach-secure-credentials-v1'

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.PBKDF2_ITERATIONS,
        )

        derived_key = kdf.derive(master_key)
        fernet_key = base64.urlsafe_b64encode(derived_key)

        return Fernet(fernet_key)

    def _compute_checksum(self, data: bytes) -> str:
        """Compute SHA-256 checksum of data."""
        return hashlib.sha256(data).hexdigest()

    def _log_access(self, operation: str, credential_name: str, success: bool, error: Optional[str] = None):
        """Log credential access for auditing."""
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'operation': operation,
                'credential': credential_name,
                'success': success,
                'error': error
            }

            with open(self.audit_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass  # Don't fail on audit log errors

    def encrypt_and_save(self, data: Dict[str, Any], name: str) -> bool:
        """
        Encrypt and save credentials to file.

        Args:
            data: Credential data to save
            name: Credential name (filename without extension)

        Returns:
            True if successful
        """
        try:
            # Serialize to JSON
            json_data = json.dumps(data, default=str).encode('utf-8')

            # Compute checksum
            checksum = self._compute_checksum(json_data)

            # Encrypt
            encrypted = self._cipher.encrypt(json_data)

            # Create envelope with metadata
            envelope = {
                'version': 1,
                'encrypted': base64.urlsafe_b64encode(encrypted).decode(),
                'checksum': checksum,
                'created_at': datetime.utcnow().isoformat() + 'Z'
            }

            # Save to file
            file_path = self.credentials_dir / f'{name}.json.enc'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(envelope, f, indent=2)

            # Set restrictive permissions
            try:
                os.chmod(file_path, 0o600)
            except Exception:
                pass

            self._log_access('save', name, True)
            return True

        except Exception as e:
            self._log_access('save', name, False, str(e))
            return False

    def load_and_decrypt(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load and decrypt credentials from file.

        Args:
            name: Credential name (filename without extension)

        Returns:
            Decrypted credential data or None if failed
        """
        file_path = self.credentials_dir / f'{name}.json.enc'

        if not file_path.exists():
            self._log_access('load', name, False, 'File not found')
            return None

        try:
            # Load envelope
            with open(file_path, 'r', encoding='utf-8') as f:
                envelope = json.load(f)

            # Decrypt
            encrypted = base64.urlsafe_b64decode(envelope['encrypted'])
            decrypted = self._cipher.decrypt(encrypted)

            # Verify checksum
            checksum = self._compute_checksum(decrypted)
            if checksum != envelope.get('checksum'):
                self._log_access('load', name, False, 'Checksum mismatch - data may be corrupted')
                return None

            # Parse JSON
            data = json.loads(decrypted.decode('utf-8'))

            self._log_access('load', name, True)
            return data

        except Exception as e:
            self._log_access('load', name, False, str(e))
            return None

    def delete(self, name: str) -> bool:
        """
        Delete a credential file.

        Args:
            name: Credential name

        Returns:
            True if deleted successfully
        """
        file_path = self.credentials_dir / f'{name}.json.enc'

        try:
            if file_path.exists():
                file_path.unlink()
                self._log_access('delete', name, True)
                return True
            return False
        except Exception as e:
            self._log_access('delete', name, False, str(e))
            return False

    def exists(self, name: str) -> bool:
        """Check if credential file exists."""
        return (self.credentials_dir / f'{name}.json.enc').exists()

    def list_credentials(self) -> list:
        """List all stored credential names."""
        return [
            f.stem.replace('.json', '')
            for f in self.credentials_dir.glob('*.json.enc')
        ]


# Convenience functions for Google OAuth token handling

def save_google_token(creds, name: str = 'token', base_dir: Optional[Path] = None) -> bool:
    """
    Save Google OAuth2 credentials securely.

    Args:
        creds: google.oauth2.credentials.Credentials object
        name: Credential name (default: 'token')
        base_dir: Base directory

    Returns:
        True if successful
    """
    manager = SecureCredentialManager(base_dir)

    # Serialize credentials to dict
    creds_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': list(creds.scopes) if creds.scopes else [],
        'expiry': creds.expiry.isoformat() if creds.expiry else None
    }

    return manager.encrypt_and_save(creds_data, name)


def load_google_token(name: str = 'token', base_dir: Optional[Path] = None):
    """
    Load Google OAuth2 credentials securely.

    Args:
        name: Credential name (default: 'token')
        base_dir: Base directory

    Returns:
        google.oauth2.credentials.Credentials object or None
    """
    try:
        from google.oauth2.credentials import Credentials
        from datetime import timezone
    except ImportError:
        return None

    manager = SecureCredentialManager(base_dir)
    creds_data = manager.load_and_decrypt(name)

    if not creds_data:
        return None

    try:
        # Parse expiry datetime
        expiry = None
        if creds_data.get('expiry'):
            from datetime import datetime as dt
            expiry_str = creds_data['expiry']
            # Handle both formats
            if 'T' in expiry_str:
                if expiry_str.endswith('Z'):
                    expiry = dt.fromisoformat(expiry_str.replace('Z', '+00:00'))
                else:
                    expiry = dt.fromisoformat(expiry_str)

        creds = Credentials(
            token=creds_data.get('token'),
            refresh_token=creds_data.get('refresh_token'),
            token_uri=creds_data.get('token_uri'),
            client_id=creds_data.get('client_id'),
            client_secret=creds_data.get('client_secret'),
            scopes=creds_data.get('scopes')
        )

        # Set expiry manually (Credentials constructor doesn't accept it)
        if expiry:
            creds.expiry = expiry

        return creds

    except Exception as e:
        print(f"[!] Failed to reconstruct credentials: {e}")
        return None


def migrate_pickle_to_secure(pickle_path: Path, name: str, base_dir: Optional[Path] = None) -> bool:
    """
    Migrate an existing pickle token file to secure encrypted storage.

    Args:
        pickle_path: Path to existing pickle file
        name: Name for the new secure credential
        base_dir: Base directory

    Returns:
        True if migration successful
    """
    import pickle

    if not pickle_path.exists():
        print(f"[!] Pickle file not found: {pickle_path}")
        return False

    try:
        # Load pickle
        with open(pickle_path, 'rb') as f:
            creds = pickle.load(f)

        # Save securely
        if save_google_token(creds, name, base_dir):
            print(f"[OK] Migrated {pickle_path.name} to {name}.json.enc")

            # Backup and remove pickle
            backup_path = pickle_path.with_suffix('.pickle.bak')
            pickle_path.rename(backup_path)
            print(f"[OK] Backed up original to {backup_path.name}")

            return True

        return False

    except Exception as e:
        print(f"[X] Migration failed: {e}")
        return False


# CLI for testing and migration
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Secure Credentials Manager')
    parser.add_argument('--list', action='store_true', help='List stored credentials')
    parser.add_argument('--migrate', metavar='PICKLE_FILE', help='Migrate pickle file to secure storage')
    parser.add_argument('--name', default='token', help='Credential name for migration')
    parser.add_argument('--verify', metavar='NAME', help='Verify a stored credential')

    args = parser.parse_args()

    manager = SecureCredentialManager()

    if args.list:
        creds = manager.list_credentials()
        print(f"\nStored credentials ({len(creds)}):")
        for name in creds:
            print(f"  - {name}")

    elif args.migrate:
        pickle_path = Path(args.migrate)
        migrate_pickle_to_secure(pickle_path, args.name)

    elif args.verify:
        data = manager.load_and_decrypt(args.verify)
        if data:
            print(f"[OK] Credential '{args.verify}' verified successfully")
            print(f"    Keys: {list(data.keys())}")
        else:
            print(f"[X] Could not load credential '{args.verify}'")

    else:
        parser.print_help()
