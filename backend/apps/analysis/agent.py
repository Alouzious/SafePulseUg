import logging
import time
from django.conf            import settings
from langchain_groq         import ChatGroq
from langgraph.prebuilt     import create_react_agent

# ── Gemini imports — commented out (backup) ─────────────────
# from langchain_google_genai import ChatGoogleGenerativeAI

from .prompts   import SYSTEM_PROMPT
from .tools     import ALL_TOOLS

logger = logging.getLogger('apps.analysis')


# ─────────────────────────────────────────────────────────────
# BUILD LLM — Groq (Primary: Free & Fast)
# ─────────────────────────────────────────────────────────────
def get_llm():
    return ChatGroq(
        api_key     = settings.GROQ_API_KEY,
        model_name  = settings.GROQ_MODEL,
        temperature = 0.3,
        max_tokens  = 4096,
    )


# ── Gemini LLM — commented out (re-enable if switching back) ─
# def get_llm():
#     return ChatGoogleGenerativeAI(
#         model                           = settings.GEMINI_MODEL,
#         google_api_key                  = settings.GEMINI_API_KEY,
#         temperature                     = 0.3,
#         convert_system_message_to_human = True,
#     )


# ─────────────────────────────────────────────────────────────
# HELPER — Run with retry on rate limit
# ─────────────────────────────────────────────────────────────
def invoke_with_retry(agent, messages, max_retries=3, wait_seconds=30):
    """
    Invoke the agent with automatic retry on rate limit (429) errors.
    """
    for attempt in range(1, max_retries + 1):
        try:
            return agent.invoke({"messages": messages})

        except Exception as e:
            error_str = str(e)

            is_rate_limit = (
                '429'                in error_str or
                'rate_limit'         in error_str.lower() or
                'RESOURCE_EXHAUSTED' in error_str or
                'Too Many Requests'  in error_str
            )

            if is_rate_limit and attempt < max_retries:
                logger.warning(
                    f"Rate limit hit (attempt {attempt}/{max_retries}). "
                    f"Waiting {wait_seconds}s before retry..."
                )
                time.sleep(wait_seconds)
                continue

            elif is_rate_limit and attempt == max_retries:
                raise Exception(
                    f"Rate limit exceeded after {max_retries} attempts. "
                    f"Please wait a minute and try again."
                )
            else:
                raise e

    raise Exception("Max retries reached.")


# ──────────────────────────────────────────���──────────────────
# RUN AGENT — Single prompt, no history
# ─────────────────────────────────────────────────────────────
def run_agent(prompt: str) -> dict:
    """
    Run the Groq AI agent with a single prompt.
    Returns dict with 'success', 'response', 'error'.
    """
    try:
        logger.info(f"Running Groq agent | model: {settings.GROQ_MODEL} | prompt: {prompt[:80]}...")

        llm   = get_llm()
        agent = create_react_agent(llm, ALL_TOOLS)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ]

        result   = invoke_with_retry(agent, messages)
        response = result["messages"][-1].content

        logger.info("✅ Groq agent completed successfully.")
        return {
            "success":  True,
            "response": response,
            "error":    None,
        }

    except Exception as e:
        logger.error(f"Groq agent error: {e}")
        return {
            "success":  False,
            "response": None,
            "error":    str(e),
        }


# ─────────────────────────────────────────────────────────────
# RUN AGENT — With conversation history
# ─────────────────────────────────────────────────────────────
def run_agent_with_history(prompt: str, history: list) -> dict:
    """
    Run the Groq AI agent with full conversation history.
    history: list of {'role': 'user'|'assistant', 'content': '...'} dicts
    """
    try:
        logger.info(f"Running Groq agent with {len(history)} history messages...")

        llm   = get_llm()
        agent = create_react_agent(llm, ALL_TOOLS)

        # System prompt first
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add history
        for msg in history:
            if msg['role'] in ('user', 'assistant'):
                messages.append({
                    "role":    msg['role'],
                    "content": msg['content'],
                })

        # Current message
        messages.append({"role": "user", "content": prompt})

        result   = invoke_with_retry(agent, messages)
        response = result["messages"][-1].content

        logger.info("✅ Groq agent with history completed successfully.")
        return {
            "success":  True,
            "response": response,
            "error":    None,
        }

    except Exception as e:
        logger.error(f"Groq agent with history error: {e}")
        return {
            "success":  False,
            "response": None,
            "error":    str(e),
        }