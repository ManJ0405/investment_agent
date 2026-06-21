import sys
from pathlib import Path

project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.agent.graph import agent
import subprocess
from langchain_core.messages import HumanMessage, AIMessage
from IPython.display import Image, display
import time
import logging
import os

# Setting
logging.basicConfig(
    level=logging.INFO,                         # Show INFO
    format='%(asctime)s [%(levelname)s] %(message)s',  # time + level + messages
    handlers=[
        logging.StreamHandler(sys.stdout),                # Ouput to terminal
        logging.FileHandler("agent.log")        
    ]
)

logger = logging.getLogger(__name__)


def _extract_ai_reply(messages) -> str:
    for message in reversed(messages or []):
        if isinstance(message, AIMessage) or getattr(message, "type", None) == "ai":
            content = message.content
            if isinstance(content, list):
                return str(content)
            return content or ""
    return "Sorry, I could not generate a response."


def pull_model():
    model_name = "gemma4:e4b"
    logger.info(f'Pulling model {model_name}...')
    try:
        subprocess.run(["ollama", "pull",  model_name])
        logger.info(f'Success')
    except subprocess.CalledProcessError as e:
        logger.error(f'Error: {e}')
        
def run_agent():
    logger.info("Starting agent...")
    config = {"configurable": {"thread_id": "terminal_1"}}
    display(Image(agent.get_graph(xray=True).draw_mermaid_png()))
    chat_history: list = []

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            logger.info("AI: Bye")
            break
        if not user_input:
            continue
        try:
            chat_history.append(HumanMessage(content=user_input))
            result = agent.invoke(
                {"messages": chat_history},
                config={**config, "recursion_limit": 25},
            )
            chat_history = list(result.get("messages") or chat_history)
            final_text = _extract_ai_reply(chat_history)
            print(f"AI: {final_text}")
            logger.info("AI: %s", final_text)
        except Exception as e:
            logger.error("Error: %s", e)
            
def streamlit_playground() -> None:
    """Start Streamlit in the background without blocking terminal stdin."""
    logger.info("Starting Streamlit Playground...")

    streamlit_script = os.path.join(os.path.dirname(__file__), "src", "chatroom", "app.py")
    env = os.environ.copy()
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    env["STREAMLIT_SERVER_HEADLESS"] = "true"

    subprocess.Popen(
        [
            "streamlit",
            "run",
            streamlit_script,
            "--server.headless",
            "true",
            "--browser.gatherUsageStats",
            "false",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
        start_new_session=True,
    )

    time.sleep(3)
    logger.info("Started Playground on http://localhost:8501")
            
            
if __name__ == "__main__":
    pull_model()
    
    streamlit_playground()
    
    run_agent()
