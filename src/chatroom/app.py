import streamlit as st
from agent import agent

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
            result = agent.invoke(
                {"messages": st.session_state.messages},
                config={"configurable": {"thread_id": "streamlit_session"}}
            )
            ai_reply = result["messages"][-1].content
            st.markdown(ai_reply)
    
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})