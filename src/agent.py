from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START
import os
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# 1. Define the shared state schema
class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class UserProfile(BaseModel):
    proficiency_level: str
    learning_goals: List[str]

class QuizResult(BaseModel):
    quiz_id: str
    score: float
    details: Dict[str, Any]

class AgentState(BaseModel):
    messages: List[Message] = Field(default_factory=list)
    user_profile: UserProfile
    quiz_history: List[QuizResult] = Field(default_factory=list)
    grammar_feedback: List[str] = Field(default_factory=list)
    vocabulary_feedback: List[str] = Field(default_factory=list)
    pronunciation_feedback: List[str] = Field(default_factory=list)
    cultural_context_feedback: List[str] = Field(default_factory=list)

# 2. Implement the LangGraph node function

def english_buddy_agent(state: AgentState) -> AgentState:
    """
    LangGraph node: Accepts AgentState, generates a conversational reply and detailed feedback using LangChain chat model,
    updates state, and returns new AgentState.
    """
    llm = ChatOpenAI(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        model='gpt-4.1',
        temperature=0.3,
    )

    # Compose conversation history for the model
    chat_history = []
    for msg in state.messages:
        if msg.role == 'user':
            chat_history.append(HumanMessage(content=msg.content))
        else:
            chat_history.append(AIMessage(content=msg.content))

    if not state.messages or state.messages[-1].role != 'user':
        raise ValueError('Last message must be from user.')
    user_input = state.messages[-1].content

    # System prompt for two-part output: reply and feedback
    system_prompt = (
        "You are English Buddy, an expert, friendly English teacher and conversation partner. "
        "For every user message, generate two outputs:\n"
        "1. A natural, conversational reply that continues the discussion, asks follow-up questions, and encourages the user.\n"
        "2. A detailed feedback section that analyzes the user's English, provides grammar corrections, vocabulary suggestions, and explanations.\n"
        "Format your response as follows:\n"
        "---\n"
        "Reply: <your conversational reply>\n"
        "---\n"
        "Feedback:\n"
        "**Corrections:** <corrections or 'No corrections needed.'>\n"
        "**Explanation:** <explanation or 'No explanation needed.'>\n"
        "**Vocabulary Suggestion:** <suggestions or 'No suggestions needed.'>\n"
        "---\n"
        "Always fill in every section, even if there are no corrections or suggestions needed."
    )

    # Add system prompt as context
    chat_history = [HumanMessage(content=system_prompt)] + chat_history

    # Generate response
    response = llm(chat_history)
    agent_output = response.content

    # Parse the two sections from the output
    reply = ""
    feedback = ""
    grammar_fb = []
    vocab_fb = []
    if '---' in agent_output:
        sections = agent_output.split('---')
        for section in sections:
            if section.strip().startswith('Reply:'):
                reply = section.strip()[len('Reply:'):].strip()
            elif section.strip().startswith('Feedback:'):
                feedback = section.strip()[len('Feedback:'):].strip()
    else:
        reply = agent_output.strip()
    # Improved feedback extraction using regex
    if feedback:
        corrections = re.search(r'\*\*Corrections:\*\*(.*?)(\*\*|$)', feedback, re.DOTALL)
        explanation = re.search(r'\*\*Explanation:\*\*(.*?)(\*\*|$)', feedback, re.DOTALL)
        vocab_suggestion = re.search(r'\*\*Vocabulary Suggestion:\*\*(.*?)(\*\*|$)', feedback, re.DOTALL)
        corrections_text = corrections.group(1).strip() if corrections else ''
        explanation_text = explanation.group(1).strip() if explanation else ''
        vocab_text = vocab_suggestion.group(1).strip() if vocab_suggestion else ''
        # Only add if not the default 'No ... needed.'
        if corrections_text and corrections_text.lower() != 'no corrections needed.':
            grammar_fb.append(f"Corrections: {corrections_text}")
        if explanation_text and explanation_text.lower() != 'no explanation needed.':
            grammar_fb.append(f"Explanation: {explanation_text}")
        if vocab_text and vocab_text.lower() != 'no suggestions needed.':
            vocab_fb.append(f"Vocabulary Suggestion: {vocab_text}")
        # If all are default, still show at least one
        if not grammar_fb and not vocab_fb:
            grammar_fb.append("No corrections or suggestions needed.")

    # Update state
    new_state = state.model_copy(deep=True)
    new_state.messages.append(Message(role='assistant', content=reply))
    new_state.grammar_feedback.extend(grammar_fb)
    new_state.vocabulary_feedback.extend(vocab_fb)
    return new_state

# 3. Create the LangGraph StateGraph

graph = StateGraph(AgentState)
graph.add_node('english_buddy_agent', english_buddy_agent)
graph.add_edge(START, 'english_buddy_agent')
compiled_graph = graph.compile()

