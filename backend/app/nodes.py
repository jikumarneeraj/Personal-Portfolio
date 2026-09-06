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
    contact_keywords = [
        "contact", "send message", "send a message", "send msg", "send a msg", "send msg to neeraj",
        "reach out", "hire", "email neeraj", "connect with neeraj", "get in touch",
        "message neeraj", "msg to neeraj", "message to neeraj", "msg neeraj",
        "talk to neeraj", "speak to neeraj", "meet neeraj", "meeting with neeraj",
        "meet him", "message him", "msg him", "email him", "contact him",
        "send email", "send an email", "drop a message", "drop a msg", "send a mail",
        "send him a message", "send him a msg", "write to neeraj"
    ]
    if any(phrase in q_lower for phrase in contact_keywords):
        return {"intent": "contact"}

    # Also detect if email address or send intent is in query
    if EMAIL_REGEX.search(query) or "@" in query:
        if any(w in q_lower for w in ["send", "msg", "message", "neeraj", "meet", "reach", "email", "name", "hello", "hi", "want to", "podcast"]):
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

def extract_contact_info(query: str, current_name=None, current_email=None, current_subject=None, current_message=None):
    name = current_name
    email = current_email
    subject = current_subject
    message = current_message

    # 1. Email extraction (regex)
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}", query)
    if email_match and not email:
        email = email_match.group(0).lower()

    # 2. Name extraction
    if not name:
        name_match = re.search(
            r"(?:my name is|i am|i'm|name is|name[:=]|this is)\s+([a-zA-Z0-9_\s]{2,30}?)(?=\s+(?:and|with|email|regarding|subject|my|\.|$|,))",
            query,
            re.IGNORECASE
        )
        if name_match:
            cand = name_match.group(1).strip()
            if cand.lower() not in ["neeraj", "interested", "writing", "sending", "looking", "a", "an"]:
                name = cand

    # 3. Subject extraction
    if not subject:
        subj_match = re.search(
            r"(?:subject is|subject[:=]|regarding|related to|topic is)\s+([a-zA-Z0-9_\s]{2,60}?)(?=\s+(?:and|with|message|\.|$|,))",
            query,
            re.IGNORECASE
        )
        if subj_match:
            extracted_sub = subj_match.group(1).strip()
            if extracted_sub:
                if "related to" in query.lower() or "regarding" in query.lower():
                    subject = f"Discussion related to {extracted_sub}"
                else:
                    subject = extracted_sub.capitalize()

    # 4. Message extraction
    if not message:
        msg_match = re.search(
            r"(?:message is|message[:=]|i want to|i would like to|looking to)\s+([^.]+)",
            query,
            re.IGNORECASE
        )
        if msg_match:
            extracted_msg = msg_match.group(0).strip()
            cleaned_msg = re.sub(r"^(message is|message[:=])\s*", "", extracted_msg, flags=re.IGNORECASE).strip()
            if cleaned_msg:
                message = cleaned_msg[0].upper() + cleaned_msg[1:]

    # Fallback subject if message is present but subject is still empty
    if message and not subject:
        m_lower = message.lower()
        if "podcast" in m_lower:
            subject = "Podcast Discussion / Collaboration"
        elif "intern" in m_lower:
            subject = "Internship Inquiry"
        elif "job" in m_lower or "hire" in m_lower or "position" in m_lower:
            subject = "Career / Hiring Inquiry"
        elif "meet" in m_lower or "call" in m_lower:
            subject = "Meeting Inquiry"
        else:
            subject = "Portfolio Inquiry"

    return name, email, subject, message

def contact_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Stateful multi-turn contact collector with validation and explicit confirmation.
    Intelligently extracts whatever fields the user has already provided in natural language.
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

    # If currently waiting for user confirmation
    if step == "asking_confirmation":
        if any(w in q_lower for w in ["yes", "send", "confirm", "proceed", "sure", "ok", "yep", "yeah"]):
            is_success = submit_contact(name=name, email=email, subject=subject, message=message)
            if is_success:
                return {
                    "response": "Your message has been sent successfully to Neeraj. Thanks for reaching out!",
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

    # Extract any fields provided in the query
    name, email, subject, message = extract_contact_info(query, name, email, subject, message)

    # Specific step overrides when user directly replies to a single-step question:
    if step == "asking_name" and not name:
        clean_name = re.sub(r"^(my name is|i am|i'm|this is)\s+", "", query, flags=re.IGNORECASE).strip()
        if clean_name:
            name = clean_name
    elif step == "asking_email" and not email:
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", query)
        if email_match:
            email = email_match.group(0).lower()
        else:
            return {
                "response": "Please enter a valid email address (e.g., name@example.com) so Neeraj can reply to you.",
                "response_type": "contact_prompt",
                "contact_step": "asking_email",
                "name": name
            }
    elif step == "asking_subject" and not subject:
        clean_sub = re.sub(r"^(subject is|subject:|topic is|regarding)\s+", "", query, flags=re.IGNORECASE).strip()
        if clean_sub:
            subject = clean_sub
    elif step == "asking_message" and not message:
        if query:
            message = query

    # Now evaluate what is missing and ask only for missing information:
    if not name:
        return {
            "response": "Sure! I can help you send a message directly to Neeraj.\nWhat is your name?",
            "response_type": "contact_prompt",
            "contact_step": "asking_name",
            "name": name,
            "email": email,
            "subject": subject,
            "message": message
        }

    if not email:
        return {
            "response": f"Thanks {name}! What is your email address?",
            "response_type": "contact_prompt",
            "contact_step": "asking_email",
            "name": name,
            "email": email,
            "subject": subject,
            "message": message
        }

    if not subject:
        return {
            "response": f"Got it. What is the subject or topic of your message for Neeraj?",
            "response_type": "contact_prompt",
            "contact_step": "asking_subject",
            "name": name,
            "email": email,
            "subject": subject,
            "message": message
        }

    if not message:
        return {
            "response": "Please enter the message you would like to send:",
            "response_type": "contact_prompt",
            "contact_step": "asking_message",
            "name": name,
            "email": email,
            "subject": subject,
            "message": message
        }

    # All fields (name, email, subject, message) are now collected!
    confirmation_prompt = (
        f"Please confirm the following details before sending:\n\n"
        f"- **Name**: {name}\n"
        f"- **Email**: {email}\n"
        f"- **Subject**: {subject}\n"
        f"- **Message**: {message}\n\n"
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

    return {
        "response": "How can I help you with Neeraj's portfolio?",
        "response_type": "text",
        "contact_step": "idle"
    }
