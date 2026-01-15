"""
LangGraph agent for processing user messages with memory and tools.
"""
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import logging

from config import settings

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the agent graph."""
    messages: List[Dict[str, str]]
    user_id: str
    conversation_id: str
    memory_context: List[Dict[str, Any]]
    response: str
    needs_tool: bool
    tool_name: str
    tool_result: Any


class AgenticAssistant:
    """LangGraph-based agentic assistant."""
    
    def __init__(self):
        """Initialize the agent."""
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("retrieve_memory", self._retrieve_memory)
        workflow.add_node("call_llm", self._call_llm)
        workflow.add_node("execute_tool", self._execute_tool)
        workflow.add_node("extract_memory", self._extract_memory)
        
        # Add edges
        workflow.set_entry_point("retrieve_memory")
        workflow.add_edge("retrieve_memory", "call_llm")
        workflow.add_conditional_edges(
            "call_llm",
            self._should_use_tool,
            {
                "execute_tool": "execute_tool",
                "extract_memory": "extract_memory"
            }
        )
        workflow.add_edge("execute_tool", "extract_memory")
        workflow.add_edge("extract_memory", END)
        
        return workflow.compile()
    
    def _retrieve_memory(self, state: AgentState) -> AgentState:
        """Retrieve relevant memory context."""
        # TODO: Implement memory retrieval in Phase 3
        # For now, just pass through
        logger.info(f"Retrieving memory for user {state['user_id']}")
        state["memory_context"] = []
        return state
    
    def _call_llm(self, state: AgentState) -> AgentState:
        """Call LLM to generate response."""
        try:
            # Build message history
            messages = []
            
            # System message
            system_prompt = """You are a helpful AI assistant acting as a personal Chief of Staff. 
You help users manage their day by accessing their Gmail and Calendar when needed.
Be concise, professional, and proactive in offering assistance."""
            
            # Add memory context if available
            if state.get("memory_context"):
                memory_text = "\n".join([
                    f"- {mem['content']}" for mem in state["memory_context"]
                ])
                system_prompt += f"\n\nRelevant context about the user:\n{memory_text}"
            
            messages.append(SystemMessage(content=system_prompt))
            
            # Add conversation history
            for msg in state["messages"]:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
            
            # Get response
            response = self.llm.invoke(messages)
            state["response"] = response.content
            
            # Check if tool is needed (simple keyword detection for now)
            content_lower = state["messages"][-1]["content"].lower()
            if any(word in content_lower for word in ["email", "inbox", "mail", "gmail"]):
                state["needs_tool"] = True
                state["tool_name"] = "gmail"
            elif any(word in content_lower for word in ["calendar", "meeting", "schedule", "event"]):
                state["needs_tool"] = True
                state["tool_name"] = "calendar"
            else:
                state["needs_tool"] = False
            
            logger.info(f"LLM response generated, needs_tool: {state['needs_tool']}")
            return state
            
        except Exception as e:
            logger.error(f"Error calling LLM: {e}", exc_info=True)
            state["response"] = "I apologize, but I encountered an error processing your request. Please try again."
            state["needs_tool"] = False
            return state
    
    def _should_use_tool(self, state: AgentState) -> str:
        """Decide if tool execution is needed."""
        if state.get("needs_tool", False):
            return "execute_tool"
        return "extract_memory"
    
    def _execute_tool(self, state: AgentState) -> AgentState:
        """Execute tool if needed."""
        # TODO: Implement tool execution in Phase 2
        logger.info(f"Tool execution requested: {state.get('tool_name')}")
        state["tool_result"] = None
        return state
    
    def _extract_memory(self, state: AgentState) -> AgentState:
        """Extract and store memory from conversation."""
        # TODO: Implement memory extraction in Phase 3
        logger.info("Memory extraction step")
        return state
    
    async def process_message(
        self,
        message: str,
        user_id: str,
        conversation_id: str,
        message_history: List[Dict[str, str]]
    ) -> str:
        """Process a user message and return response."""
        try:
            # Prepare initial state
            initial_state = AgentState(
                messages=message_history + [{"role": "user", "content": message}],
                user_id=user_id,
                conversation_id=conversation_id,
                memory_context=[],
                response="",
                needs_tool=False,
                tool_name="",
                tool_result=None
            )
            
            # Run the graph
            final_state = await self.graph.ainvoke(initial_state)
            
            return final_state["response"]
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return "I apologize, but I encountered an error. Please try again."


# Global agent instance
agent = AgenticAssistant()
