import sys
from pathlib import Path

project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

from langchain_core.runnables.history import MessagesOrDictWithMessages
from src.agent.graph import agent
import subprocess
from langchain_core.messages import HumanMessage
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


def pull_model():
    model_name = "gemma4:e4b"
    logger.info(f'Pulling model {model_name}...')
    try:
        subprocess.run(["ollama", "pull",  model_name])
        logger.info(f'Success')
    except subprocess.CalledProcessError as e:
        logger.error(f'Error: {e}')
        
def run_agent():
    logger.info(f'Starting agent...')
    config = {"configurable": {"thread_id": "terminal_1"}}
    display(Image(agent.get_graph(xray=True).draw_mermaid_png()))
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            logger.info(f'AI: Bye')
            break
        try:
            messages = HumanMessage(content= user_input)
            result = agent.invoke(
                {"messages": messages},
                config={**config, "recursion_limit": 25},
            )
            for i, m in enumerate(result.get("messages") or []):
                preview = m.content
                if isinstance(preview, list):
                    preview = str(preview)
                if isinstance(preview, str) and len(preview) > 500:
                    preview = preview[:500] + "…"
                logger.info(
                    "  msg[%d] %s: %r",
                    i,
                    getattr(m, "type", type(m).__name__),
                    preview,
                )
            last = (result.get("messages") or [])[-1] if result.get("messages") else None
            final_text = last.content if last and hasattr(last, "content") else ""
            if isinstance(final_text, list):
                final_text = str(final_text)
            logger.info("AI: %s", final_text)
                
        except Exception as e:
            logger.error(f'Error: {e}')
            
def streamlit_playground() :
    logger.info(f'Starting Streamlit Playground...')
    
    streamlit_script = os.path.join(os.path.dirname(__file__), "src", "chatroom", "app.py")
    subprocess.Popen(["streamlit", "run", streamlit_script])
    
    time.sleep(3)
    logger.info(f'Started Playground on http://localhost:8501')
    logger.info(f'Network url: http://172.18.249.174:8501')
            
            
if __name__ == "__main__":
    pull_model()
    
    streamlit_playground()
    
    run_agent()
