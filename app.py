import streamlit as st
from streamlit_chat import message
import streamlit_authenticator as stauth
import openai
import yaml
from yaml.loader import SafeLoader


API_KEY = "<your_api_key>"
MODEL = "gpt-3.5-turbo"  # or gpt-4

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{st.session_state["name"]}*')
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
    st.session_state["chat_history"] = []

if st.session_state["authentication_status"]:
    openai.api_key = API_KEY

    st.header("Chat Interface")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    if st.button("End Session"):
        st.session_state["chat_history"] = []

    st.session_state["chat_input"] = st.text_input("Message:")
    if st.button("Send") and st.session_state["chat_input"]:
        st.session_state["chat_history"].append({
            "role": "user",
            "content": st.session_state["chat_input"]
        })
        with st.spinner('Wait for it...'):
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=st.session_state["chat_history"],
                temperature=0,
            )
            answer = {
                "role": response["choices"][0]["message"]["role"],
                "content": response["choices"][0]["message"]["content"]
            }
            st.session_state["chat_history"].append(answer)

    for i in range(len(st.session_state["chat_history"])-1, -1, -1):
        if st.session_state["chat_history"][i]["role"]=="user":
            message(st.session_state["chat_history"][i]["content"], is_user=True, key="chat"+str(i))
        elif st.session_state["chat_history"][i]["role"]=="assistant":
            message(st.session_state["chat_history"][i]["content"], key="chat"+str(i))
