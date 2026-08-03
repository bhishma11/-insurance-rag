import json
from typing import Dict, Any, AsyncGenerator

from app.core.langgraph_agent import InsuranceAgent
from app.core.vector_search import VectorSearch
from app.core.langchain_rag import LangChainRAG
from app.core.smart_router import SmartRouter
from app.database import db
from app.database_chat import chat_db  # ← NEW: SQLite chat history


class RAGService:
    def __init__(self):
        self.vector_search = VectorSearch()
        self.vector_search.load_index()
        print("✅ Vector index loaded")
        
        self.langchain_rag = LangChainRAG(self.vector_search)
        
        # Initialize Smart Router for hybrid LLM selection
        self.smart_router = SmartRouter()
        print("✅ Smart Router initialized")
        
        self.agent = InsuranceAgent(
            rag_search_function=self.vector_search.hybrid_search,
            llm_function=self.langchain_rag.ask
        )
        print("✅ RAG Service initialized")
    
    async def process_query(
        self,
        query: str,
        session_id: str,
        user_id: str = "anonymous",  # ← Added user_id
        use_hyde: bool = True,
        use_memory: bool = True,
        temperature: float = 0.7,
        use_deepseek_only: bool = False
    ) -> Dict[str, Any]:
        """Process a query through the RAG pipeline"""
        
        # Search for relevant documents
        if use_hyde:
            search_results = self.vector_search.hybrid_search_with_hyde(
                query=query,
                k=5,
                use_hyde=True,
                use_rewrite=True
            )
        else:
            search_results = self.vector_search.hybrid_search(
                query=query,
                k=5
            )
        
        # Build context
        context = self._build_context(search_results)
        
        # Generate response using Smart Router
        answer, model_used, premium_data = self.smart_router.ask(query, use_deepseek_only=use_deepseek_only)
        print(f"📌 Used model: {model_used} for query: {query[:50]}...")
        
        # ✅ SAVE TO POSTGRES (for existing functionality)
        try:
            sources_list = []
            for r in search_results[:3]:
                if isinstance(r, dict):
                    sources_list.append(r)
                else:
                    sources_list.append({"text": str(r)})
            
            await db.save_conversation(
                session_id=session_id,
                user_id=user_id,  # ← Pass user_id
                query=query,
                response=answer,
                sources=json.dumps(sources_list) if sources_list else None
            )
            print(f"✅ Saved conversation to PostgreSQL: {session_id}")
        except Exception as e:
            print(f"⚠️ Could not save to PostgreSQL: {e}")
        
        # ✅ NEW: SAVE TO SQLITE CHAT HISTORY (always works, no Docker needed!)
        try:
            await chat_db.save_chat(session_id, query, answer)
            print(f"✅ Saved conversation to SQLite: {session_id}")
        except Exception as e:
            print(f"⚠️ Could not save to SQLite: {e}")
        
        result = {
            "response": answer,
            "model_used": model_used,
            "sources": [{"text": str(r)} for r in search_results[:3]] if search_results else [],
            "calculation_steps": []
        }
        
        # Add premium data if available
        if premium_data:
            result["premium_data"] = premium_data
        
        return result
    
    async def process_query_streaming(
        self, 
        query: str, 
        session_id: str, 
        user_id: str = "anonymous"  # ← Added user_id
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process a query with streaming response"""
        print(f"[STREAMING] Starting for query: {query}")
        try:
            print("[STREAMING] Sending start message")
            yield {"type": "start", "message": "Processing..."}
            
            print("[STREAMING] Calling process_query")
            result = await self.process_query(query, session_id, user_id)  # ← Pass user_id
            print(f"[STREAMING] Process query result: {result}")
            
            # If there's premium data, send it as a separate event first
            if result.get("premium_data"):
                print("[STREAMING] Sending premium calculation")
                yield {
                    "type": "premium_calculation",
                    "data": result["premium_data"]
                }
            
            print("[STREAMING] Sending final response")
            yield {
                "type": "final", 
                "response": result["response"],
                "model_used": result.get("model_used", "unknown"),
                "sources": result.get("sources", []),
                "calculation_steps": result.get("calculation_steps", [])
            }
            
            print("[STREAMING] Sending done")
            yield {"type": "done"}
            print("[STREAMING] Done")
            
        except Exception as e:
            print(f"[ERROR] Streaming error: {e}")
            import traceback
            traceback.print_exc()
            yield {
                "type": "error",
                "message": f"Error processing query: {str(e)}"
            }
            yield {"type": "done"}
    
    def _build_context(self, search_results: list) -> str:
        """Build context from search results"""
        context_parts = []
        for i, result in enumerate(search_results):
            if isinstance(result, dict):
                text = result.get('text', str(result))
            else:
                text = str(result)
            context_parts.append(f"[{i+1}] {text}")
        return "\n\n".join(context_parts)