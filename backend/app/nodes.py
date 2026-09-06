import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.config import settings
from app.state import AgentState
from app.tools import VERIFIED_LINKS, submit_contact
from app.rag import portfolio_rag
from app.prompts import PORTFOLIO_SYSTEM_PROMPT, CONTACT_PARSER_SYSTEM_PROMPT

logger = logging.getLogger("neeraj_portfolio_assistant.nodes")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def get_llm():
    """Initializes and returns the ChatGoogleGenerativeAI instance."""
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return None
    model_name = settings.GEMINI_MODEL or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.2,
        max_retries=2
    )

def understand_query_node(state: AgentState) -> Dict[str, Any]:
    """Classifies user intent and sets routing direction."""
    query = (state.get("query") or "").strip()
    contact_step = state.get("contact_step") or "idle"

    # If already inside an active contact conversation flow, stay in contact
    if contact_step not in ["idle", "submitted"]:
        return {"intent": "contact"}

    q_lower = query.lower()

    # Direct contact intent triggers
    if any(phrase in q_lower for phrase in [
        "contact", "send message", "send a message", "reach out", "hire", "email neeraj",
        "connect with neeraj", "get in touch", "message neeraj"
    ]):
        return {"intent": "contact"}

    # Resume intent triggers
    if any(phrase in q_lower for phrase in [
        "resume", "cv", "download resume", "view resume", "curriculum vitae"
    ]):
        return {"intent": "resume"}

    # GitHub intent triggers
    if any(phrase in q_lower for phrase in ["github", "git repo", "repository", "repositories"]) and not any(p in q_lower for p in ["amrit", "kidney", "quiz", "whatsapp"]):
        return {"intent": "github"}

    # Kaggle intent triggers
    if "kaggle" in q_lower:
        return {"intent": "kaggle"}

    # LinkedIn intent triggers
    if "linkedin" in q_lower:
        return {"intent": "linkedin"}

    # Default to portfolio information query
    return {"intent": "portfolio_info"}

def resume_node(state: AgentState) -> Dict[str, Any]:
    """Provides verified resume download and view link."""
    link_info = VERIFIED_LINKS["resume"]
    response_text = (
        "Here is Neeraj Kumar's resume. You can view or download it directly via Google Drive:"
    )
    return {
        "response": response_text,
        "response_type": "link",
        "url": link_info["url"],
        "quick_actions": ["About Neeraj", "Projects", "Skills", "Contact Neeraj"]
    }

def social_links_node(state: AgentState) -> Dict[str, Any]:
    """Provides verified social profiles (GitHub, LinkedIn, Kaggle)."""
    intent = state.get("intent", "github")
    if intent not in VERIFIED_LINKS:
        intent = "github"

    link_info = VERIFIED_LINKS[intent]
    title = link_info["title"]
    url = link_info["url"]

    response_text = f"Here is {title}:\n{url}"
    return {
        "response": response_text,
        "response_type": "link",
        "url": url,
        "quick_actions": ["Projects", "Skills", "Resume", "Contact Neeraj"]
    }

def rag_retrieval_node(state: AgentState) -> Dict[str, Any]:
    """Retrieves relevant chunks from markdown knowledge base."""
    query = state.get("query", "")
    context = portfolio_rag.get_context_for_query(query, top_k=4)
    return {"portfolio_context": context}

def gemini_answer_node(state: AgentState) -> Dict[str, Any]:
    """Generates grounded answer using Google Gemini with retrieved portfolio context."""
    query = state.get("query", "")
    context = state.get("portfolio_context", "")
    messages_history = state.get("messages", [])

    llm = get_llm()
    if llm is None:
        # Graceful fallback when API key is not yet set in environment
        logger.warning("GEMINI_API_KEY is not configured.")
        # Check if query matches common direct questions
        q_lower = query.lower()
        if "who is neeraj" in q_lower or "about" in q_lower:
            return {
                "response": "Neeraj Kumar is a Data Scientist and AI/ML Engineer pursuing dual degrees at IIT Madras (BS in Data Science) and REC Bijnor (B.Tech in IT). He is GATE 2026 Qualified in Computer Science & Engineering.",
                "response_type": "text",
                "quick_actions": ["Projects", "Skills", "Resume", "Contact Neeraj"]
            }
        if "skill" in q_lower:
            return {
                "response": "Neeraj specializes in Python, Machine Learning (Scikit-learn), Deep Learning (CNNs, VGG16), NLP, LangChain/RAG, Data Analytics (Pandas, NumPy, Power BI), and Backend development (Flask, Redis, Celery).",
                "response_type": "text",
                "quick_actions": ["Projects", "Resume", "Contact Neeraj"]
            }
        return {
            "response": "Neeraj's AI Assistant is currently awaiting the GEMINI_API_KEY configuration in the environment. Please check the backend server settings.",
            "response_type": "text",
            "quick_actions": ["About Neeraj", "Skills", "Projects", "Resume"]
        }

    try:
        system_content = f"{PORTFOLIO_SYSTEM_PROMPT}\n\n=== PORTFOLIO CONTEXT ===\n{context}\n========================="
        prompt_messages = [SystemMessage(content=system_content)]

        # Include last 6 turns of conversation history for multi-turn reasoning
        recent_history = messages_history[-6:]
        for m in recent_history:
            role = m.get("role")
            content = m.get("content", "")
            if role == "user":
                prompt_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                prompt_messages.append(AIMessage(content=content))

        # Add current query
        prompt_messages.append(HumanMessage(content=query))

        ai_response = llm.invoke(prompt_messages)
        content_val = ai_response.content if hasattr(ai_response, "content") else ai_response
        if isinstance(content_val, str):
            response_text = content_val
        elif isinstance(content_val, list):
            text_blocks = []
            for item in content_val:
                if isinstance(item, dict) and "text" in item:
                    text_blocks.append(item["text"])
                elif isinstance(item, str):
                    text_blocks.append(item)
                else:
                    text_blocks.append(str(item))
            response_text = "\n".join(text_blocks)
        else:
            response_text = str(content_val)

        return {
            "response": response_text,
            "response_type": "text",
            "quick_actions": ["Projects", "Skills", "Resume", "Contact Neeraj"]
        }
    except Exception as e:
        logger.error(f"Error during Gemini generation: {e}")
        return {
            "response": "I encountered an issue processing your request with the AI service. Please try again shortly.",
            "response_type": "text"
        }

def contact_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Stateful multi-turn contact collector with validation and explicit confirmation.
    """
    query = (state.get("query") or "").strip()
    q_lower = query.lower()

    step = state.get("contact_step") or "idle"
    name = state.get("name")
    email = state.get("email")
    subject = state.get("subject")
    message = state.get("message")

    # Check for cancellation
    if any(w in q_lower for w in ["cancel", "abort", "stop contact", "nevermind", "quit"]):
        return {
            "response": "Contact request cancelled. How else may I help you?",
            "response_type": "text",
            "contact_step": "idle",
            "name": None,
            "email": None,
            "subject": None,
            "message": None,
            "quick_actions": ["About Neeraj", "Projects", "Skills", "Resume"]
        }

    # If first time entering contact workflow
    if step == "idle":
        # Check if user provided all or some information directly in the first prompt
        # e.g., "My name is John, email john@example.com, subject Job, message hello"
        step = "asking_name"
        return {
            "response": "Sure! I can help you send a message directly to Neeraj.\nWhat is your name?",
            "response_type": "contact_prompt",
            "contact_step": "asking_name"
        }

    if step == "asking_name":
        # Extract name from input
        clean_name = query
        # Remove common preamble like "My name is", "I am", "I'm"
        clean_name = re.sub(r"^(my name is|i am|i'm|this is)\s+", "", clean_name, flags=re.IGNORECASE).strip()
        if not clean_name:
            return {
                "response": "Please provide a valid name so Neeraj knows who is reaching out.",
                "response_type": "contact_prompt",
                "contact_step": "asking_name"
            }
        name = clean_name
        step = "asking_email"
        return {
            "response": f"Thanks {name}! What is your email address?",
            "response_type": "contact_prompt",
            "contact_step": "asking_email",
            "name": name
        }

    if step == "asking_email":
        # Look for email pattern in query
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", query)
        if not email_match:
            return {
                "response": "Please enter a valid email address (e.g., name@example.com) so Neeraj can reply to you.",
                "response_type": "contact_prompt",
                "contact_step": "asking_email",
                "name": name
            }
        email = email_match.group(0).lower()
        step = "asking_subject"
        return {
            "response": "Got it. What is the subject or topic of your message?",
            "response_type": "contact_prompt",
            "contact_step": "asking_subject",
            "name": name,
            "email": email
        }

    if step == "asking_subject":
        clean_subject = query
        clean_subject = re.sub(r"^(subject is|subject:|topic is|regarding)\s+", "", clean_subject, flags=re.IGNORECASE).strip()
        if not clean_subject:
            return {
                "response": "Please provide a subject for your message.",
                "response_type": "contact_prompt",
                "contact_step": "asking_subject",
                "name": name,
                "email": email
            }
        subject = clean_subject
        step = "asking_message"
        return {
            "response": "Please enter the message you would like to send:",
            "response_type": "contact_prompt",
            "contact_step": "asking_message",
            "name": name,
            "email": email,
            "subject": subject
        }

    if step == "asking_message":
        if not query:
            return {
                "response": "Please write your message for Neeraj:",
                "response_type": "contact_prompt",
                "contact_step": "asking_message",
                "name": name,
                "email": email,
                "subject": subject
            }
        message = query
        step = "asking_confirmation"
        
        confirmation_prompt = (
            f"Please confirm the following details before sending:\n\n"
            f"• **Name**: {name}\n"
            f"• **Email**: {email}\n"
            f"• **Subject**: {subject}\n"
            f"• **Message**: {message}\n\n"
            f"Should I send this message to Neeraj now? (Reply **Yes** to send, or **No** / **Cancel**)"
        )
        return {
            "response": confirmation_prompt,
            "response_type": "contact_prompt",
            "contact_step": "asking_confirmation",
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
            "quick_actions": ["Yes, send it", "Cancel"]
        }

    if step == "asking_confirmation":
        if any(w in q_lower for w in ["yes", "send", "confirm", "proceed", "sure", "ok", "yep", "yeah"]):
            # Deliver message via tools
            is_success = submit_contact(name=name, email=email, subject=subject, message=message)
            if is_success:
                return {
                    "response": f"Your message has been sent successfully to Neeraj. Thanks for reaching out!",
                    "response_type": "contact_success",
                    "contact_step": "submitted",
                    "contact_submission_status": "success",
                    "name": None,
                    "email": None,
                    "subject": None,
                    "message": None,
                    "quick_actions": ["About Neeraj", "Projects", "Skills", "Resume"]
                }
            else:
                return {
                    "response": "I couldn't send your message right now due to a network connection issue. Please use the Contact Us form directly on the website.",
                    "response_type": "contact_error",
                    "contact_step": "idle",
                    "contact_submission_status": "failed",
                    "name": None,
                    "email": None,
                    "subject": None,
                    "message": None,
                    "quick_actions": ["About Neeraj", "Projects", "Skills"]
                }
        elif any(w in q_lower for w in ["no", "cancel", "don't send", "stop"]):
            return {
                "response": "Message sending cancelled. What else can I help you with?",
                "response_type": "text",
                "contact_step": "idle",
                "name": None,
                "email": None,
                "subject": None,
                "message": None,
                "quick_actions": ["About Neeraj", "Projects", "Skills", "Resume"]
            }
        else:
            return {
                "response": "Please reply **Yes** to confirm and send your message, or **No** / **Cancel** to abort.",
                "response_type": "contact_prompt",
                "contact_step": "asking_confirmation",
                "name": name,
                "email": email,
                "subject": subject,
                "message": message,
                "quick_actions": ["Yes, send it", "Cancel"]
            }

    return {
        "response": "How can I help you with Neeraj's portfolio?",
        "response_type": "text",
        "contact_step": "idle"
    }
