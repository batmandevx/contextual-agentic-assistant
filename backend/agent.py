"""
Enhanced LangGraph agent with Gmail, Calendar, and Memory integration.
Provides contextual, intelligent assistance as a "Chief of Staff".
"""
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage
import logging
import json

from config import settings
from memory_brain import memory_brain, MemoryCategory
from gmail_tools import gmail_tools
from calendar_tools import calendar_tools

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
    tool_action: str
    tool_params: Dict[str, Any]
    tool_result: Any


class AgenticAssistant:
    """Enhanced LangGraph-based agentic assistant with tools and memory."""
    
    def __init__(self):
        """Initialize the agent with LLM and tools."""
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            temperature=0.7,
            google_api_key=settings.GOOGLE_API_KEY,
            max_retries=1,
            timeout=30
        )
        self.graph = self._build_graph()
        
        # Tool definitions for the agent
        self.tools = {
            "gmail": {
                "fetch_emails": gmail_tools.fetch_emails,
                "search_emails": gmail_tools.search_emails,
                "get_email_details": gmail_tools.get_email_details,
                "send_email": gmail_tools.send_email,
                "get_important_emails": gmail_tools.get_important_emails,
            },
            "calendar": {
                "get_upcoming_events": calendar_tools.get_upcoming_events,
                "get_today_schedule": calendar_tools.get_today_schedule,
                "check_availability": calendar_tools.check_availability,
                "get_next_meeting": calendar_tools.get_next_meeting,
            }
        }
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("retrieve_memory", self._retrieve_memory)
        workflow.add_node("analyze_intent", self._analyze_intent)
        workflow.add_node("execute_tool", self._execute_tool)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("extract_memory", self._extract_memory)
        
        # Add edges
        workflow.set_entry_point("retrieve_memory")
        workflow.add_edge("retrieve_memory", "analyze_intent")
        workflow.add_conditional_edges(
            "analyze_intent",
            self._should_use_tool,
            {
                "execute_tool": "execute_tool",
                "generate_response": "generate_response"
            }
        )
        workflow.add_edge("execute_tool", "generate_response")
        workflow.add_edge("generate_response", "extract_memory")
        workflow.add_edge("extract_memory", END)
        
        return workflow.compile()
    
    async def _retrieve_memory(self, state: AgentState) -> AgentState:
        """Retrieve relevant memory context."""
        try:
            user_message = state["messages"][-1]["content"] if state["messages"] else ""
            
            # Get relevant memories based on context
            memories = await memory_brain.retrieve_relevant_memories(
                user_id=state["user_id"],
                context=user_message,
                limit=5
            )
            
            state["memory_context"] = memories
            logger.info(f"Retrieved {len(memories)} relevant memories for user {state['user_id']}")
            
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}")
            state["memory_context"] = []
        
        return state
    
    async def _analyze_intent(self, state: AgentState) -> AgentState:
        """Analyze user intent and determine if tools are needed."""
        user_message = state["messages"][-1]["content"].lower() if state["messages"] else ""
        
        # Gmail intent detection
        gmail_keywords = {
            "inbox": ("gmail", "fetch_emails", {}),
            "email": ("gmail", "fetch_emails", {}),
            "mail": ("gmail", "fetch_emails", {}),
            "unread": ("gmail", "get_important_emails", {}),
            "important emails": ("gmail", "get_important_emails", {}),
            "send email": ("gmail", "send_email", {}),
            "reply": ("gmail", "send_email", {}),
        }
        
        # Calendar intent detection
        calendar_keywords = {
            "calendar": ("calendar", "get_upcoming_events", {}),
            "schedule": ("calendar", "get_today_schedule", {}),
            "today": ("calendar", "get_today_schedule", {}),
            "meetings": ("calendar", "get_upcoming_events", {}),
            "events": ("calendar", "get_upcoming_events", {}),
            "next meeting": ("calendar", "get_next_meeting", {}),
            "available": ("calendar", "check_availability", {}),
            "free": ("calendar", "check_availability", {}),
        }
        
        # Check for tool matches
        state["needs_tool"] = False
        
        for keyword, (tool, action, params) in gmail_keywords.items():
            if keyword in user_message:
                state["needs_tool"] = True
                state["tool_name"] = tool
                state["tool_action"] = action
                state["tool_params"] = params
                logger.info(f"Detected Gmail intent: {action}")
                break
        
        if not state["needs_tool"]:
            for keyword, (tool, action, params) in calendar_keywords.items():
                if keyword in user_message:
                    state["needs_tool"] = True
                    state["tool_name"] = tool
                    state["tool_action"] = action
                    state["tool_params"] = params
                    logger.info(f"Detected Calendar intent: {action}")
                    break
        
        return state
    
    def _should_use_tool(self, state: AgentState) -> str:
        """Decide if tool execution is needed."""
        if state.get("needs_tool", False):
            return "execute_tool"
        return "generate_response"
    
    async def _execute_tool(self, state: AgentState) -> AgentState:
        """Execute the appropriate tool."""
        try:
            tool_name = state.get("tool_name", "")
            tool_action = state.get("tool_action", "")
            tool_params = state.get("tool_params", {})
            
            if tool_name and tool_action:
                tool_func = self.tools.get(tool_name, {}).get(tool_action)
                
                if tool_func:
                    # Execute the tool
                    result = await tool_func(
                        user_id=state["user_id"],
                        **tool_params
                    )
                    state["tool_result"] = result
                    logger.info(f"Tool {tool_name}.{tool_action} executed successfully")
                else:
                    state["tool_result"] = {"error": "Tool not found"}
                    logger.warning(f"Tool not found: {tool_name}.{tool_action}")
            else:
                state["tool_result"] = None
                
        except Exception as e:
            logger.error(f"Error executing tool: {e}")
            state["tool_result"] = {"error": str(e)}
        
        return state
    
    async def _generate_response(self, state: AgentState) -> AgentState:
        """Generate response using LLM with context."""
        try:
            messages = []
            
            # Build enhanced system prompt
            system_prompt = """You are an intelligent AI assistant acting as a personal "Chief of Staff". 
You help users manage their day by accessing their Gmail and Calendar when needed.

Your capabilities:
- Read and summarize emails from the user's inbox
- Check calendar events and schedules
- Help draft and send email replies
- Remember user preferences and context

Be concise, professional, and proactive. Provide actionable insights."""
            
            # Add memory context
            if state.get("memory_context"):
                memory_text = "\n".join([
                    f"• {mem['content']} (confidence: {mem['confidence']:.0%})"
                    for mem in state["memory_context"]
                ])
                system_prompt += f"\n\n📝 What I remember about you:\n{memory_text}"
            
            # Add tool results if available
            if state.get("tool_result"):
                result = state["tool_result"]
                if isinstance(result, list):
                    if result and not result[0].get('error'):
                        # Format tool results
                        formatted = self._format_tool_results(state["tool_name"], result)
                        system_prompt += f"\n\n📊 Data retrieved:\n{formatted}"
                    elif result and result[0].get('error'):
                        system_prompt += f"\n\n⚠️ Could not access data: {result[0]['error']}"
                elif isinstance(result, dict):
                    if result.get('error'):
                        system_prompt += f"\n\n⚠️ Error: {result['error']}"
                    else:
                        formatted = json.dumps(result, indent=2, default=str)
                        system_prompt += f"\n\n📊 Data retrieved:\n{formatted}"
            
            messages.append(HumanMessage(content=f"System Instructions: {system_prompt}"))
            
            # Add conversation history
            for msg in state["messages"]:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
            
            # Generate response
            logger.info(f"Generating response with {len(messages)} messages...")
            response = self.llm.invoke(messages)
            state["response"] = response.content
            logger.info("Response generated successfully")
            
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            state["response"] = "I apologize, but I encountered an error processing your request. Please try again."
        
        return state
    
    def _format_tool_results(self, tool_name: str, results: List[Dict]) -> str:
        """Format tool results for the prompt."""
        if tool_name == "gmail":
            formatted = []
            for email in results[:5]:
                formatted.append(
                    f"• From: {email.get('from', 'Unknown')}\n"
                    f"  Subject: {email.get('subject', 'No subject')}\n"
                    f"  Preview: {email.get('snippet', '')[:80]}..."
                )
            return "\n".join(formatted)
        
        elif tool_name == "calendar":
            formatted = []
            for event in results[:5]:
                formatted.append(
                    f"• {event.get('title', 'No title')}\n"
                    f"  Time: {event.get('start', 'Unknown')}\n"
                    f"  Location: {event.get('location', 'No location')}"
                )
            return "\n".join(formatted)
        
        return json.dumps(results, indent=2, default=str)
    
    async def _extract_memory(self, state: AgentState) -> AgentState:
        """Extract and store facts from the conversation."""
        try:
            # Extract facts from conversation
            facts = await memory_brain.extract_facts_from_conversation(
                messages=state["messages"],
                user_id=state["user_id"]
            )
            
            if facts:
                logger.info(f"Extracted {len(facts)} facts from conversation")
                
        except Exception as e:
            logger.error(f"Error extracting memory: {e}")
        
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
                tool_action="",
                tool_params={},
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
