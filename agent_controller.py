"""
Simple Agent Controller - Easy way to task and control agents
"""

import requests
import json
from typing import Dict, Any, Optional

class AgentController:
    """Simple interface to control and task agents"""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.available_agents = {
            "business_advisor": "ceo",
            "research_expert": "research", 
            "performance_analyst": "performance",
            "team_coach": "coaching",
            "code_expert": "code_analyzer",
            "debugger": "code_debugger",
            "code_repair": "code_repair",
            "test_generator": "test_generator",
            "profiler": "performance_profiler",
            "auto_select": "auto"
        }
    
    def task_agent(self, task: str, agent_type: str = "auto_select", use_documents: bool = True) -> Dict[str, Any]:
        """
        Task an agent with a specific job
        
        Args:
            task: What you want the agent to do (in plain English)
            agent_type: Which expert to use (business_advisor, research_expert, etc.)
            use_documents: Whether to use your uploaded documents for context
        """
        
        agent_name = self.available_agents.get(agent_type, "research")
        
        print(f"🤖 Tasking {agent_type.replace('_', ' ').title()}: {task[:50]}...")
        
        try:
            response = requests.post(f"{self.base_url}/api/agents/query", 
                json={
                    "query": task,
                    "agent_type": agent_name,
                    "use_rag": use_documents
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    print("✅ Task completed successfully")
                    agent_response = result.get("response", {})
                    return {
                        "success": True,
                        "agent": agent_response.get("agent_name", agent_type),
                        "response": agent_response.get("result", ""),
                        "task": task,
                        "execution_time": agent_response.get("execution_time", 0)
                    }
                else:
                    print(f"❌ Task failed: {result.get('message', 'Unknown error')}")
                    return {"success": False, "error": result.get("message")}
            else:
                print(f"❌ Request failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"success": False, "error": str(e)}
    
    def upload_document(self, file_path: str) -> bool:
        """Upload a document to the knowledge base"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.base_url}/api/rag/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✅ Uploaded: {file_path}")
                    return True
                    
            print(f"❌ Upload failed: {response.text}")
            return False
            
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
    
    def list_agents(self):
        """Show available agents and their capabilities"""
        print("\n🤖 Available Agents:")
        capabilities = {
            "business_advisor": "Strategic decisions, business planning, executive insights",
            "research_expert": "Data analysis, research, pattern identification", 
            "performance_analyst": "Performance optimization, bottleneck analysis",
            "team_coach": "Team development, motivation, coaching guidance",
            "code_expert": "Code review, analysis, best practices",
            "debugger": "Bug fixing, troubleshooting, error resolution",
            "auto_select": "Automatically picks the best agent for your task"
        }
        
        for agent, description in capabilities.items():
            print(f"   • {agent.replace('_', ' ').title()}: {description}")
    
    def check_knowledge_base(self):
        """Check what's in your knowledge base"""
        try:
            response = requests.get(f"{self.base_url}/api/rag/knowledge_base/status")
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    kb = result.get("knowledge_base", {})
                    print(f"\n📚 Your Knowledge Base:")
                    print(f"   Documents: {kb.get('document_count', 0)}")
                    print(f"   Status: {'Ready' if kb.get('initialized') else 'Not Ready'}")
                    return kb.get('document_count', 0)
            
            print("❌ Could not check knowledge base")
            return 0
            
        except Exception as e:
            print(f"❌ Error checking knowledge base: {e}")
            return 0

# Create global controller instance
controller = AgentController()

# Convenience functions for easy use
def task(description: str, agent: str = "auto_select", use_docs: bool = True):
    """Quick way to task an agent"""
    return controller.task_agent(description, agent, use_docs)

def upload(file_path: str):
    """Quick way to upload a document"""
    return controller.upload_document(file_path)

def agents():
    """Show available agents"""
    controller.list_agents()

def status():
    """Check system status"""
    controller.check_knowledge_base()

def interactive_mode():
    """Interactive agent control interface"""
    print("🎯 Interactive Agent Controller")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Task an agent")
        print("2. List available agents")
        print("3. Check knowledge base status")
        print("4. Upload document")
        print("5. Chat with agent (continuous)")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            print("\n📋 Task an Agent")
            task_desc = input("What do you want the agent to do? ").strip()
            if not task_desc:
                continue
                
            print("\nAvailable agents:")
            controller.list_agents()
            agent = input("\nWhich agent? (or 'auto' for auto-select): ").strip()
            if not agent:
                agent = "auto_select"
            elif agent == "auto":
                agent = "auto_select"
            
            use_docs = input("Use your documents for context? (y/n): ").strip().lower()
            use_docs = use_docs in ["y", "yes", ""]
            
            print("\n🤖 Processing...")
            result = controller.task_agent(task_desc, agent, use_docs)
            
            if result.get('success'):
                print(f"\n✅ Response:\n{result['response']}")
            else:
                print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        
        elif choice == "2":
            controller.list_agents()
        
        elif choice == "3":
            doc_count = controller.check_knowledge_base()
            print(f"\n📊 Knowledge Base: {doc_count} documents")
        
        elif choice == "4":
            file_path = input("Enter file path to upload: ").strip()
            if file_path:
                success = controller.upload_document(file_path)
                if success:
                    print("✅ Document uploaded successfully")
                else:
                    print("❌ Failed to upload document")
        
        elif choice == "5":
            print("\n💬 Chat Mode (type 'exit' to stop)")
            agent = input("Which agent? (or 'auto'): ").strip()
            if agent == "auto" or not agent:
                agent = "auto_select"
            
            while True:
                message = input("\n👤 You: ").strip()
                if message.lower() in ['exit', 'quit', 'stop']:
                    break
                
                if message:
                    result = controller.task_agent(message, agent, True)
                    if result.get('success'):
                        print(f"\n🤖 Agent: {result['response']}")
                    else:
                        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        
        elif choice == "6":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    print("🎯 Agent Controller - Simple Agent Management")
    print("\nOptions:")
    print("   Interactive mode: python agent_controller.py")
    print("   Quick commands in Python:")
    print("     agents()     - Show available agents")
    print("     status()     - Check knowledge base")
    print("     upload('file.txt') - Upload document")
    print("     task('analyze sales data') - Task an agent")
    
    interactive_mode()
    status()
