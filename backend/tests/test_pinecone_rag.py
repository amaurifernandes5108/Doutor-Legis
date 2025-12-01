#!/usr/bin/env python3
"""
Teste completo da integração Pinecone RAG para Doutor Legis 2.0 ULTRA
Testa sistema RAG end-to-end conforme especificado no test_result.md
"""

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class PineconeRAGTester:
    def __init__(self, base_url="https://legalai-18.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_session_token = None
        self.admin_user_id = None
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
        
        if response_data and isinstance(response_data, dict):
            print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
        
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
        if self.admin_session_token:
            default_headers['Authorization'] = f'Bearer {self.admin_session_token}'
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=default_headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=30)
            else:
                return False, None, 0
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            return True, response_data, response.status_code
        
        except Exception as e:
            return False, str(e), 0

    def create_admin_master_session(self):
        """Create session for admin master founder (amaurifernandes1975@gmail.com)"""
        try:
            import pymongo
            from pymongo import MongoClient
            from datetime import datetime, timezone, timedelta
            
            # Connect to MongoDB
            client = MongoClient("mongodb://localhost:27017")
            db = client["doutor_legis_db"]
            
            # Check if founder user exists
            founder_user = db.users.find_one({"email": "amaurifernandes1975@gmail.com"})
            if not founder_user:
                # Create founder user if not exists
                founder_user = {
                    "id": f"admin-master-{int(time.time())}",
                    "email": "amaurifernandes1975@gmail.com",
                    "name": "Admin Master Founder",
                    "picture": None,
                    "plan": "avancado",
                    "role": "admin_master",
                    "token_balance": 999999,
                    "consultas_mes_atual": 0,
                    "pdfs_mes_atual": 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "active": True
                }
                db.users.insert_one(founder_user)
                print(f"✅ Created founder user: {founder_user['email']}")
            
            # Create admin session
            self.admin_user_id = founder_user["id"]
            self.admin_session_token = f"admin_rag_test_{int(time.time())}"
            
            # Insert admin session
            admin_session_doc = {
                "user_id": self.admin_user_id,
                "session_token": self.admin_session_token,
                "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            db.user_sessions.insert_one(admin_session_doc)
            
            print(f"✅ Created admin master session for: {founder_user['email']}")
            print(f"✅ Admin role: {founder_user.get('role', 'not set')}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create admin session: {str(e)}")
            return False

    def test_health_check(self):
        """Test 1: Health Check - Sistema deve estar ativo"""
        success, response, status = self.make_request('GET', '/health')
        
        if success and status == 200 and isinstance(response, dict):
            # Check required fields for ULTRA version
            required_fields = ["status", "version", "nucleos_ativos", "router_inteligente", "meta_nucleo"]
            missing_fields = [f for f in required_fields if f not in response]
            
            if not missing_fields and response.get("status") == "healthy":
                self.log_test("Health Check", True, "Sistema ativo com todos os componentes ULTRA", response)
                return True
            else:
                self.log_test("Health Check", False, f"Missing fields: {missing_fields} or status not healthy")
                return False
        else:
            self.log_test("Health Check", False, f"Status: {status}, Response: {response}")
            return False

    def test_pinecone_stats_admin(self):
        """Test 2: Stats Pinecone (como Admin Master) - Verificar configuração RAG"""
        if not self.admin_session_token:
            self.log_test("Pinecone Stats (Admin)", False, "No admin session available")
            return False
        
        success, response, status = self.make_request('GET', '/analytics/pinecone-stats')
        
        if success and status == 200 and isinstance(response, dict):
            # Verificar campos obrigatórios
            required_fields = ["status", "total_vectors", "rag_enabled"]
            missing_fields = [f for f in required_fields if f not in response]
            
            if not missing_fields:
                # Verificar valores esperados
                total_vectors = response.get("total_vectors", 0)
                rag_enabled = response.get("rag_enabled", False)
                namespaces_populated = response.get("namespaces_populated", 0)
                
                # Conforme contexto: 7 vetores de exemplo, 3+ namespaces populados
                if total_vectors >= 7 and rag_enabled and namespaces_populated >= 3:
                    self.log_test("Pinecone Stats (Admin)", True, 
                                f"RAG ativo: {total_vectors} vetores, {namespaces_populated} namespaces", response)
                    return True
                else:
                    self.log_test("Pinecone Stats (Admin)", False, 
                                f"Valores incorretos: vectors={total_vectors}, rag={rag_enabled}, ns={namespaces_populated}")
                    return False
            else:
                self.log_test("Pinecone Stats (Admin)", False, f"Missing fields: {missing_fields}")
                return False
        else:
            self.log_test("Pinecone Stats (Admin)", False, f"Status: {status}, Response: {response}")
            return False

    def test_rag_consultation_constitucional(self):
        """Test 3: Consulta RAG End-to-End - Domínio Constitucional (com dados)"""
        if not self.admin_session_token:
            self.log_test("RAG Consultation (Constitucional)", False, "No admin session available")
            return False
        
        consultation_data = {
            "domain": "constitucional",
            "question": "Quais são os direitos fundamentais garantidos pela Constituição Federal de 1988?"
        }
        
        success, response, status = self.make_request('POST', '/consultation', consultation_data)
        
        if success and status == 200 and isinstance(response, dict):
            # Verificar estrutura da resposta
            required_fields = ['id', 'domain', 'question', 'response']
            missing_fields = [f for f in required_fields if f not in response]
            
            if not missing_fields:
                response_content = response.get('response', {})
                
                # Verificar se RAG foi usado
                rag_used = response_content.get('rag_used', False) or response_content.get('rag_enabled', False)
                documents_found = response_content.get('documents_found', 0) or response_content.get('documents_used', 0)
                
                # Verificar estrutura JSON da resposta
                expected_sections = ['resumo', 'legislacao_aplicavel', 'analise_legal', 'recomendacoes']
                response_sections = [s for s in expected_sections if s in response_content]
                
                if rag_used and documents_found > 0 and len(response_sections) >= 3:
                    self.log_test("RAG Consultation (Constitucional)", True, 
                                f"RAG ativo: {documents_found} docs, {len(response_sections)} seções", response)
                    return response['id']
                else:
                    self.log_test("RAG Consultation (Constitucional)", False, 
                                f"RAG não usado ou resposta incompleta: rag={rag_used}, docs={documents_found}")
                    return False
            else:
                self.log_test("RAG Consultation (Constitucional)", False, f"Missing fields: {missing_fields}")
                return False
        else:
            self.log_test("RAG Consultation (Constitucional)", False, f"Status: {status}, Response: {response}")
            return False

    def test_rag_consultation_consumidor(self):
        """Test 4: Consulta RAG End-to-End - Domínio Consumidor (com dados)"""
        if not self.admin_session_token:
            self.log_test("RAG Consultation (Consumidor)", False, "No admin session available")
            return False
        
        consultation_data = {
            "domain": "consumidor",
            "question": "Quais são os direitos básicos do consumidor segundo o CDC?"
        }
        
        success, response, status = self.make_request('POST', '/consultation', consultation_data)
        
        if success and status == 200 and isinstance(response, dict):
            required_fields = ['id', 'domain', 'question', 'response']
            missing_fields = [f for f in required_fields if f not in response]
            
            if not missing_fields:
                response_content = response.get('response', {})
                
                # Verificar se RAG foi usado
                rag_used = response_content.get('rag_used', False) or response_content.get('rag_enabled', False)
                documents_found = response_content.get('documents_found', 0) or response_content.get('documents_used', 0)
                
                # Verificar estrutura JSON da resposta
                expected_sections = ['resumo', 'legislacao_aplicavel', 'analise_legal', 'recomendacoes']
                response_sections = [s for s in expected_sections if s in response_content]
                
                if rag_used and documents_found > 0 and len(response_sections) >= 3:
                    self.log_test("RAG Consultation (Consumidor)", True, 
                                f"RAG ativo: {documents_found} docs, {len(response_sections)} seções", response)
                    return response['id']
                else:
                    self.log_test("RAG Consultation (Consumidor)", False, 
                                f"RAG não usado ou resposta incompleta: rag={rag_used}, docs={documents_found}")
                    return False
            else:
                self.log_test("RAG Consultation (Consumidor)", False, f"Missing fields: {missing_fields}")
                return False
        else:
            self.log_test("RAG Consultation (Consumidor)", False, f"Status: {status}, Response: {response}")
            return False

    def test_rag_consultation_trabalhista(self):
        """Test 5: Consulta RAG End-to-End - Domínio Trabalhista (com dados)"""
        if not self.admin_session_token:
            self.log_test("RAG Consultation (Trabalhista)", False, "No admin session available")
            return False
        
        consultation_data = {
            "domain": "trabalhista",
            "question": "Quais são os direitos trabalhistas básicos garantidos pela CLT?"
        }
        
        success, response, status = self.make_request('POST', '/consultation', consultation_data)
        
        if success and status == 200 and isinstance(response, dict):
            required_fields = ['id', 'domain', 'question', 'response']
            missing_fields = [f for f in required_fields if f not in response]
            
            if not missing_fields:
                response_content = response.get('response', {})
                
                # Verificar se RAG foi usado
                rag_used = response_content.get('rag_used', False) or response_content.get('rag_enabled', False)
                documents_found = response_content.get('documents_found', 0) or response_content.get('documents_used', 0)
                
                # Verificar estrutura JSON da resposta
                expected_sections = ['resumo', 'legislacao_aplicavel', 'analise_legal', 'recomendacoes']
                response_sections = [s for s in expected_sections if s in response_content]
                
                if rag_used and documents_found > 0 and len(response_sections) >= 3:
                    self.log_test("RAG Consultation (Trabalhista)", True, 
                                f"RAG ativo: {documents_found} docs, {len(response_sections)} seções", response)
                    return response['id']
                else:
                    self.log_test("RAG Consultation (Trabalhista)", False, 
                                f"RAG não usado ou resposta incompleta: rag={rag_used}, docs={documents_found}")
                    return False
            else:
                self.log_test("RAG Consultation (Trabalhista)", False, f"Missing fields: {missing_fields}")
                return False
        else:
            self.log_test("RAG Consultation (Trabalhista)", False, f"Status: {status}, Response: {response}")
            return False

    def test_fallback_consultation_penal(self):
        """Test 6: Consulta Fallback - Domínio Penal (sem dados RAG)"""
        if not self.admin_session_token:
            self.log_test("Fallback Consultation (Penal)", False, "No admin session available")
            return False
        
        consultation_data = {
            "domain": "penal",
            "question": "Quais são os elementos do crime segundo o Código Penal?"
        }
        
        success, response, status = self.make_request('POST', '/consultation', consultation_data)
        
        if success and status == 200 and isinstance(response, dict):
            required_fields = ['id', 'domain', 'question', 'response']
            missing_fields = [f for f in required_fields if f not in response]
            
            if not missing_fields:
                response_content = response.get('response', {})
                
                # Verificar se funcionou sem RAG (fallback)
                rag_used = response_content.get('rag_used', False) or response_content.get('rag_enabled', False)
                
                # Verificar estrutura JSON da resposta (deve funcionar mesmo sem RAG)
                expected_sections = ['resumo', 'legislacao_aplicavel', 'analise_legal', 'recomendacoes']
                response_sections = [s for s in expected_sections if s in response_content]
                
                # Deve funcionar sem RAG (fallback)
                if len(response_sections) >= 3:
                    fallback_msg = "com RAG" if rag_used else "fallback (sem RAG)"
                    self.log_test("Fallback Consultation (Penal)", True, 
                                f"Consulta funcionou {fallback_msg}, {len(response_sections)} seções", response)
                    return response['id']
                else:
                    self.log_test("Fallback Consultation (Penal)", False, 
                                f"Resposta incompleta: {len(response_sections)} seções")
                    return False
            else:
                self.log_test("Fallback Consultation (Penal)", False, f"Missing fields: {missing_fields}")
                return False
        else:
            self.log_test("Fallback Consultation (Penal)", False, f"Status: {status}, Response: {response}")
            return False

    def cleanup_test_data(self):
        """Clean up test data from database"""
        try:
            import pymongo
            from pymongo import MongoClient
            
            client = MongoClient("mongodb://localhost:27017")
            db = client["doutor_legis_db"]
            
            # Remove admin test session (but keep the user)
            if self.admin_session_token:
                db.user_sessions.delete_many({"session_token": self.admin_session_token})
                print(f"✅ Cleaned up admin test session")
            
        except Exception as e:
            print(f"⚠️ Failed to cleanup test data: {str(e)}")

    def run_pinecone_rag_tests(self):
        """Run all Pinecone RAG tests"""
        print("🚀 Starting Pinecone RAG Integration Tests")
        print("=" * 60)
        
        # Setup admin session
        print("\n👑 Setting up Admin Master session...")
        if not self.create_admin_master_session():
            print("❌ Cannot proceed without admin session")
            return 1
        
        # Test 1: Health Check
        print("\n📡 Test 1: Health Check...")
        self.test_health_check()
        
        # Test 2: Pinecone Stats (Admin only)
        print("\n📊 Test 2: Pinecone Stats (Admin Master)...")
        self.test_pinecone_stats_admin()
        
        # Test 3-5: RAG Consultations (domains with data)
        print("\n🔍 Test 3: RAG Consultation - Constitucional...")
        consultation_id_1 = self.test_rag_consultation_constitucional()
        
        print("\n🔍 Test 4: RAG Consultation - Consumidor...")
        consultation_id_2 = self.test_rag_consultation_consumidor()
        
        print("\n🔍 Test 5: RAG Consultation - Trabalhista...")
        consultation_id_3 = self.test_rag_consultation_trabalhista()
        
        # Test 6: Fallback consultation (domain without data)
        print("\n🔄 Test 6: Fallback Consultation - Penal (sem dados RAG)...")
        consultation_id_4 = self.test_fallback_consultation_penal()
        
        # Cleanup
        print("\n🧹 Cleaning up test data...")
        self.cleanup_test_data()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Pinecone RAG Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All Pinecone RAG tests passed!")
            print("\n✅ Sistema RAG Pinecone está funcionando corretamente:")
            print("   - Health check ativo")
            print("   - Stats Pinecone acessíveis (admin)")
            print("   - RAG funcionando em domínios com dados")
            print("   - Fallback funcionando em domínios sem dados")
            return 0
        else:
            print("❌ Some RAG tests failed. Check the details above.")
            return 1

def main():
    """Main test runner"""
    tester = PineconeRAGTester()
    return tester.run_pinecone_rag_tests()

if __name__ == "__main__":
    sys.exit(main())