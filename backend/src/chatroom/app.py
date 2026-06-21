import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]  # chatroom/app.py → src → backend
sys.path.insert(0, str(project_root))


import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from src.agent import agent

st.set_page_config(page_title="AI Investment Agent", page_icon="💹")

st.title("AI Investment Agent 💹")
st.caption("Professional stock analysis assistant")
st.caption("I am able to get stock fundamential information, ohlcv data and analyze stock")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask me something about stock and investment analysis!")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            langchain_messages = []
            for m in st.session_state.messages:
                if m["role"] == "user":
                    langchain_messages.append(HumanMessage(content=m["content"]))
                elif m["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=m["content"]))

            result = agent.invoke(
                {"messages": langchain_messages},
                config={
                    "configurable": {"thread_id": "streamlit_session"},
                    "recursion_limit": 25,
                },
            )
            ai_messages = [
                m for m in result.get("messages", [])
                if getattr(m, "type", None) == "ai"
            ]
            ai_reply = ai_messages[-1].content if ai_messages else "Sorry, I could not generate a reply."
            st.markdown(ai_reply)
            
    
    
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})