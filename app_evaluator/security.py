import os
from cryptography.fernet import Fernet
import streamlit as st

class SecureVault:
    def __init__(self):
        # Get encryption key from Streamlit secrets or environment
        self.key = None
        try:
            self.key = st.secrets.get("QV_DATA_ENCRYPTION_KEY")
        except:
            pass
            
        if not self.key:
            self.key = os.getenv("QV_DATA_ENCRYPTION_KEY")
            
        self.fernet = None
        
        if self.key:
            try:
                self.fernet = Fernet(self.key.encode() if isinstance(self.key, str) else self.key)
            except Exception as e:
                print(f"[SecureVault] Error initializing Fernet: {str(e)}")
                self.fernet = None

    def encrypt(self, data):
        """Encrypts data if a key is available; otherwise returns raw data."""
        if not self.fernet or not data:
            return data
        
        try:
            if isinstance(data, str):
                data = data.encode()
            return self.fernet.encrypt(data).decode()
        except Exception as e:
            print(f"[SecureVault] Encryption error: {str(e)}")
            return data

    def decrypt(self, encrypted_data):
        """Decrypts data if a key is available; otherwise returns raw data."""
        if not self.fernet or not encrypted_data:
            return encrypted_data
            
        try:
            return self.fernet.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            print(f"[SecureVault] Decryption error: {str(e)}")
            return encrypted_data

    @staticmethod
    def generate_key():
        """Helper to generate a new key for the user to set in their secrets."""
        return Fernet.generate_key().decode()
