#!/usr/bin/env python
"""
Test scenario for code-review-agent

This file demonstrates a sample implementation that the code-review-agent
would evaluate. It contains both good practices and intentional issues
for the agent to identify during review.
"""

import hashlib  # Wrong: Should use bcrypt for passwords
from typing import Dict, Optional


class AuthService:
    """Service for handling user authentication."""
    
    def __init__(self):
        self.users = {}  # In-memory storage for demo
        self.tokens = {}
    
    def register_user(self, email: str, password: str) -> Dict:
        """Register a new user."""
        # Missing: Email validation
        # Missing: Password strength validation
        
        if email in self.users:
            return {"error": "User exists"}  # Wrong: Inconsistent error format
        
        # Critical Issue: Using MD5 instead of bcrypt
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        
        self.users[email] = {
            "email": email,
            "password": hashed_password  # Security issue: weak hashing
        }
        
        return {"success": True}
    
    def login(self, email, password):  # Missing type hints
        """Authenticate user and generate token."""
        if email not in self.users:
            return None  # Wrong: Should return consistent error format
        
        # Security issue: MD5 comparison
        hashed = hashlib.md5(password.encode()).hexdigest()
        
        if self.users[email]["password"] != hashed:
            print(f"Login failed for {email}")  # Security: Logging sensitive info
            return None
        
        # Missing: Proper JWT implementation
        token = f"token_{email}_{hashed[:8]}"  # Insecure token generation
        self.tokens[token] = email
        
        # Missing: Token expiration
        return {"token": token}
    
    def validate_token(self, token: str) -> Optional[str]:
        """Validate authentication token."""
        # Missing: Token expiration check
        # Missing: Proper JWT validation
        return self.tokens.get(token)
    
    # Missing: Logout functionality
    # Missing: Rate limiting
    # Missing: Error handling
    # Missing: Logging


def test_auth_service():
    """Basic tests for AuthService."""
    service = AuthService()
    
    # Test registration
    result = service.register_user("test@example.com", "password123")
    assert result["success"] == True
    
    # Test duplicate registration
    result = service.register_user("test@example.com", "password123")
    assert "error" in result
    
    # Test login
    result = service.login("test@example.com", "password123")
    assert "token" in result
    
    # Test invalid login
    result = service.login("test@example.com", "wrongpassword")
    assert result is None  # Inconsistent with registration error handling
    
    print("All tests passed!")  # Should use proper test framework


if __name__ == "__main__":
    test_auth_service()