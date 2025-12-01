# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "Plataforma SaaS de IA jurídica Doutor Legis 2.0 com arquitetura ULTRA de 13 Núcleos Especializados. Sistema de administrador master fundador com acesso pleno."

backend:
  - task: "Sistema de Role Administrador Master Fundador"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implementado campo role no User model, funções is_admin_master() e is_founder_email(), atualização automática de role para email amaurifernandes1975@gmail.com. Bypass de limites de consultas e domínios para admin_master."

  - task: "Arquitetura ULTRA - 13 Núcleos Jurídicos"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "13 domínios implementados (constitucional, civil, consumidor, imobiliario, publico, trabalhista, empresarial, internacional, etica_advocacia_oab, penal, tributario, previdenciario, tecnologia). Integração com router_inteligente, meta_nucleo e nucleos_especializados."

  - task: "Router Inteligente"
    implemented: true
    working: "NA"
    file: "/app/backend/router_inteligente.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Sistema de classificação de perguntas com keywords e patterns. Endpoint /api/domains/classificar funcionando."

  - task: "Meta-Núcleo Analytics"
    implemented: true
    working: "NA"
    file: "/app/backend/meta_nucleo.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Sistema de monitoramento e aprendizado contínuo. Endpoint /api/analytics/performance com acesso para plano avançado e admin_master."

  - task: "Endpoint /api/auth/admin-status"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Novo endpoint para verificar status e privilégios de administrador master."

  - task: "Endpoint /api/planos/meu-plano com privilégios admin"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Atualizado para retornar mensagem especial e privilégios plenos para admin_master."

  - task: "Endpoint /api/consultation com bypass de limites"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Consultas ilimitadas para admin_master. Não incrementa contador de uso. Acesso a todos os 13 domínios."

  - task: "Sistema de Planos com 13 domínios"
    implemented: true
    working: "NA"
    file: "/app/backend/planos_config.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Atualizado DOMINIOS_POR_PLANO para incluir os 4 novos domínios (penal, tributario, previdenciario, tecnologia) nos planos intermediario e avancado."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "Sistema de Role Administrador Master Fundador"
    - "Arquitetura ULTRA - 13 Núcleos Jurídicos"
    - "Router Inteligente"
    - "Endpoint /api/auth/admin-status"
    - "Endpoint /api/planos/meu-plano com privilégios admin"
    - "Endpoint /api/consultation com bypass de limites"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "Implementei sistema completo de Administrador Master Fundador com acesso pleno. Email amaurifernandes1975@gmail.com tem role admin_master com bypass de todos os limites. Também finalizei a integração da arquitetura ULTRA com 13 núcleos jurídicos especializados. Preciso que teste: 1) Health check e endpoints de domínios, 2) Sistema de admin (endpoints /api/auth/admin-status e /api/planos/meu-plano), 3) Router inteligente (/api/domains/classificar), 4) Consulta jurídica completa end-to-end. Credenciais: usar email amaurifernandes1975@gmail.com para testes de admin."
