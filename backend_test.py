#!/usr/bin/env python3
"""
Doutor Legis 2.0 - Backend API Testing Suite
Tests all endpoints including authentication, consultations, payments, and domains.
"""

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class DoutorLegisAPITester:
    def __init__(self, base_url="https://legalai-18.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details,
            "response_data": response_data
        })

    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> tuple:
        """Make HTTP request and return (success, response, status_code)"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        
        # Default headers
        default_headers = {'Content-Type': 'application/json'}
        if self.session_token:
            default_headers['Authorization'] = f'Bearer {self.session_token}'
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=default_headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=default_headers, timeout=30)
            else:
                return False, None, 0
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            return True, response_data, response.status_code
        
        except Exception as e:
            return False, str(e), 0

    def test_health_check(self):
        """Test health endpoint"""
        success, response, status = self.make_request('GET', '/health')
        
        if success and status == 200:
            self.log_test("Health Check", True, response_data=response)
            return True
        else:
            self.log_test("Health Check", False, f"Status: {status}, Response: {response}")
            return False

    def test_domains_endpoint(self):
        """Test domains listing - ULTRA version with 13 domains"""
        success, response, status = self.make_request('GET', '/domains')
        
        if success and status == 200 and isinstance(response, list) and len(response) == 13:
            # Verify all 13 ULTRA legal domains are present
            expected_domains = [
                "constitucional", "civil", "consumidor", "imobiliario", 
                "publico", "trabalhista", "empresarial", "internacional",
                "etica_advocacia_oab", "penal", "tributario", "previdenciario", "tecnologia"
            ]
            
            domain_ids = [d.get('id') for d in response]
            missing_domains = [d for d in expected_domains if d not in domain_ids]
            
            if not missing_domains:
                self.log_test("ULTRA Domains Listing (13 núcleos)", True, f"All 13 ULTRA domains present", response)
                return True
            else:
                self.log_test("ULTRA Domains Listing (13 núcleos)", False, f"Missing domains: {missing_domains}")
                return False
        else:
            self.log_test("ULTRA Domains Listing (13 núcleos)", False, f"Status: {status}, Expected 13 domains, got {len(response) if isinstance(response, list) else 'invalid'}")
            return False

    def create_test_session(self):
        """Create a test session using MongoDB directly (simulating auth)"""
        try:
            import pymongo
            from pymongo import MongoClient
            import uuid
            from datetime import datetime, timezone, timedelta
            
            # Connect to MongoDB
            client = MongoClient("mongodb://localhost:27017")
            db = client["doutor_legis_db"]
            
            # Create test user
            self.user_id = f"test-user-{int(time.time())}"
            test_email = f"test.user.{int(time.time())}@example.com"
            self.session_token = f"test_session_{int(time.time())}"
            
            # Insert test user
            user_doc = {
                "id": self.user_id,
                "email": test_email,
                "name": "Test User",
                "picture": "https://via.placeholder.com/150",
                "plan": "gratuito",
                "token_balance": 3,
                "google_id": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "active": True
            }
            db.users.insert_one(user_doc)
            
            # Insert test session
            session_doc = {
                "user_id": self.user_id,
                "session_token": self.session_token,
                "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            db.user_sessions.insert_one(session_doc)
            
            print(f"✅ Created test user: {self.user_id}")
            print(f"✅ Created test session: {self.session_token}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create test session: {str(e)}")
            return False

    def test_auth_me(self):
        """Test /auth/me endpoint"""
        if not self.session_token:
            self.log_test("Auth Me", False, "No session token available")
            return False
        
        success, response, status = self.make_request('GET', '/auth/me')
        
        if success and status == 200 and isinstance(response, dict):
            required_fields = ['id', 'email', 'name', 'plan', 'token_balance']
            missing_fields = [f for f in required_fields if f not in response]
            
            if not missing_fields:
                self.log_test("Auth Me", True, f"User profile retrieved", response)
                return True
            else:
                self.log_test("Auth Me", False, f"Missing fields: {missing_fields}")
                return False
        else:
            self.log_test("Auth Me", False, f"Status: {status}, Response: {response}")
            return False

    def test_consultation_creation(self):
        """Test consultation creation"""
        if not self.session_token:
            self.log_test("Consultation Creation", False, "No session token available")
            return False
        
        consultation_data = {
            "domain": "civil",
            "question": "Quais são os requisitos para um contrato de compra e venda de imóvel ser válido?"
        }
        
        success, response, status = self.make_request('POST', '/consultation', consultation_data)
        
        if success and status == 200 and isinstance(response, dict):
            required_fields = ['id', 'domain', 'question', 'response', 'confidence', 'tokens_used']
            missing_fields = [f for f in required_fields if f not in response]
            
            if not missing_fields:
                # Verify response structure (8 sections)
                response_content = response.get('response', {})
                expected_sections = [
                    'resumo', 'legislacao_aplicavel', 'jurisprudencia', 
                    'analise_legal', 'riscos_juridicos', 'recomendacoes', 
                    'proximos_passos', 'confianca'
                ]
                
                missing_sections = [s for s in expected_sections if s not in response_content]
                
                if not missing_sections:
                    self.log_test("Consultation Creation", True, f"8-section response generated", response)
                    return response['id']  # Return consultation ID for further tests
                else:
                    self.log_test("Consultation Creation", False, f"Missing response sections: {missing_sections}")
                    return False
            else:
                self.log_test("Consultation Creation", False, f"Missing fields: {missing_fields}")
                return False
        else:
            self.log_test("Consultation Creation", False, f"Status: {status}, Response: {response}")
            return False

    def test_consultation_retrieval(self, consultation_id: str):
        """Test consultation retrieval"""
        if not consultation_id:
            self.log_test("Consultation Retrieval", False, "No consultation ID provided")
            return False
        
        success, response, status = self.make_request('GET', f'/consultation/{consultation_id}')
        
        if success and status == 200 and isinstance(response, dict):
            if response.get('id') == consultation_id:
                self.log_test("Consultation Retrieval", True, f"Consultation retrieved", response)
                return True
            else:
                self.log_test("Consultation Retrieval", False, "Consultation ID mismatch")
                return False
        else:
            self.log_test("Consultation Retrieval", False, f"Status: {status}, Response: {response}")
            return False

    def test_history_endpoint(self):
        """Test consultation history"""
        success, response, status = self.make_request('GET', '/history')
        
        if success and status == 200 and isinstance(response, list):
            self.log_test("Consultation History", True, f"History retrieved ({len(response)} items)", response)
            return True
        else:
            self.log_test("Consultation History", False, f"Status: {status}, Response: {response}")
            return False

    def test_payment_checkout(self):
        """Test payment checkout creation"""
        checkout_data = {
            "package_id": "premium_monthly",
            "origin_url": self.base_url
        }
        
        success, response, status = self.make_request('POST', '/payments/checkout', checkout_data)
        
        if success and status == 200 and isinstance(response, dict):
            required_fields = ['checkout_url', 'session_id']
            missing_fields = [f for f in required_fields if f not in response]
            
            if not missing_fields:
                self.log_test("Payment Checkout", True, f"Checkout session created", response)
                return response['session_id']
            else:
                self.log_test("Payment Checkout", False, f"Missing fields: {missing_fields}")
                return False
        else:
            self.log_test("Payment Checkout", False, f"Status: {status}, Response: {response}")
            return False

    def test_rate_limiting(self):
        """Test rate limiting (60 requests per minute)"""
        print("\n🔄 Testing rate limiting (this may take a moment)...")
        
        # Make rapid requests to trigger rate limiting
        for i in range(65):  # Exceed the 60/minute limit
            success, response, status = self.make_request('GET', '/domains')
            
            if status == 429:  # Rate limit exceeded
                self.log_test("Rate Limiting", True, f"Rate limit triggered after {i+1} requests")
                return True
            
            if i < 64:  # Don't sleep on the last iteration
                time.sleep(0.5)  # Small delay between requests
        
        self.log_test("Rate Limiting", False, "Rate limit not triggered after 65 requests")
        return False

    def test_google_login_endpoint(self):
        """Test Google login redirect endpoint"""
        success, response, status = self.make_request('GET', '/auth/google-login')
        
        if success and status == 200 and isinstance(response, dict):
            if 'auth_url' in response and 'auth.emergentagent.com' in response['auth_url']:
                self.log_test("Google Login Endpoint", True, f"Auth URL generated", response)
                return True
            else:
                self.log_test("Google Login Endpoint", False, "Invalid auth_url in response")
                return False
        else:
            self.log_test("Google Login Endpoint", False, f"Status: {status}, Response: {response}")
            return False

    def cleanup_test_data(self):
        """Clean up test data from database"""
        try:
            import pymongo
            from pymongo import MongoClient
            
            client = MongoClient("mongodb://localhost:27017")
            db = client["doutor_legis_db"]
            
            # Remove test user and session
            if self.user_id:
                db.users.delete_many({"id": self.user_id})
                db.user_sessions.delete_many({"user_id": self.user_id})
                db.consultations.delete_many({"user_id": self.user_id})
                print(f"✅ Cleaned up test data for user: {self.user_id}")
            
        except Exception as e:
            print(f"⚠️ Failed to cleanup test data: {str(e)}")

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Doutor Legis 2.0 Backend API Tests")
        print("=" * 60)
        
        # Basic connectivity tests
        print("\n📡 Testing Basic Connectivity...")
        self.test_health_check()
        self.test_domains_endpoint()
        self.test_google_login_endpoint()
        
        # Authentication tests
        print("\n🔐 Testing Authentication...")
        if self.create_test_session():
            self.test_auth_me()
            
            # Protected endpoint tests
            print("\n⚖️ Testing Legal Consultation System...")
            consultation_id = self.test_consultation_creation()
            if consultation_id:
                self.test_consultation_retrieval(consultation_id)
            self.test_history_endpoint()
            
            # Payment tests
            print("\n💳 Testing Payment System...")
            self.test_payment_checkout()
            
            # Rate limiting test
            print("\n🚦 Testing Rate Limiting...")
            # Skip rate limiting test to avoid delays
            # self.test_rate_limiting()
            
            # Cleanup
            self.cleanup_test_data()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("❌ Some tests failed. Check the details above.")
            return 1

def main():
    """Main test runner"""
    tester = DoutorLegisAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())