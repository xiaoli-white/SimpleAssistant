import asyncio
import multiprocessing
import platform
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime

import streamlit as st
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession

from config import loadConfig, Model, Config

config_path: str = 'config.yaml'

db_path: str = "sessions.sqlite"


def start_builtin_mcp_tools():
    result: subprocess.CompletedProcess = subprocess.run([sys.executable, "./builtin_mcp_tools.py"],
                                                         capture_output=True,
                                                         text=True, encoding=sys.stdout.encoding)
    return result

def getSystemPrompt(config: Config)->str:
    return config["systemPrompt"] + f"\nSystem: {platform.platform()}"

def getNewSessionId()->str:
    return str(uuid.uuid4())

async def main():
    if "conn" not in st.session_state:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        st.session_state.conn = conn
        cursor = conn.cursor()
        st.session_state.cursor = cursor
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
    else:
        conn = st.session_state.conn
        cursor = st.session_state.cursor

    if "config" not in st.session_state:
        config: Config = loadConfig(config_path)
        st.session_state.config = config
        clientObjects = [mcpServer.getClient() for mcpServer in config["mcpServers"].values()]
        st.session_state.clientObjects = clientObjects
        clients = []
        for clientObject in clientObjects:
            try:
                clients.append(await clientObject.__aenter__())
            except Exception as e:
                print(e)
        st.session_state.clients = clients
        sessionObjects = []
        for client in clients:
            reader, writer = client
            sessionObjects.append(ClientSession(reader, writer))
        st.session_state.sessionObjects = sessionObjects
        sessions = []
        for sessionObject in sessionObjects:
            session = await sessionObject.__aenter__()
            await session.initialize()
            sessions.append(session)
        st.session_state.sessions = sessions
        tools = []
        for session in sessions:
            tools.extend(await load_mcp_tools(session))
        st.session_state.tools = tools
    else:
        config: Config = st.session_state.config
        clients = st.session_state.clients
        sessions = st.session_state.sessions
        tools = st.session_state.tools

    cursor.execute('SELECT DISTINCT session_id FROM conversations ORDER BY timestamp DESC')
    session_ids_tmp = cursor.fetchall()
    session_ids = [row[0] for row in session_ids_tmp]
    if not session_ids:
        new_session_id = getNewSessionId()
        session_ids.append(new_session_id)
        cursor.execute('INSERT INTO conversations (session_id, role, content) VALUES (?, ?, ?)',
                       (new_session_id, "system", getSystemPrompt(config)))
        conn.commit()

    with st.sidebar:
        modelName = st.selectbox("Model", list(config["models"].keys()))
        selected_session_id = st.sidebar.selectbox("Choose a session", session_ids, index=0)
        cursor.execute('SELECT role, content FROM conversations WHERE session_id=? ORDER BY timestamp ASC',
                   (selected_session_id,))
        messages_tmp = cursor.fetchall()
        messages = [{"role": row[0], "content": row[1]} for row in messages_tmp]
        if st.button("Create new session"):
            new_session_id = getNewSessionId()
            cursor.execute('INSERT INTO conversations (session_id, role, content) VALUES (?, ?, ?)',
                           (new_session_id, "system", getSystemPrompt(config)))
            conn.commit()
            st.rerun()
        if st.button("Delete session"):
            cursor.execute('DELETE FROM conversations WHERE session_id=?', (selected_session_id,))
            conn.commit()
            st.rerun()
    if "lastModelName" not in st.session_state or modelName != st.session_state.lastModelName:
        model: Model = config["models"][modelName]
        st.session_state.model = model
        chatModel = model.getChatModel(config["providers"][model.provider])
        st.session_state.chatModel = chatModel
        agent = create_react_agent(chatModel, tools)
        st.session_state.agent = agent
        st.session_state.lastModelName = modelName
    else:
        model: Model = st.session_state.model
        chatModel = st.session_state.chatModel
        agent = st.session_state.agent

    for msg in messages:
        st.chat_message(msg["role"]).markdown(msg["content"], unsafe_allow_html=True)

    prompt = st.chat_input("What is up?")
    if prompt is not None:
        messages.append({"role": "user", "content": prompt})
        cursor.execute('INSERT INTO conversations (session_id, role, content) VALUES (?, ?, ?)',
                       (selected_session_id, "user", prompt))
        conn.commit()

        st.chat_message("user").write(prompt)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            async for event in agent.astream_events({"messages": messages}):
                event_type = event["event"]
                data = event["data"]
                match event_type:
                    case "on_chat_model_stream":
                        full_response += data["chunk"].content
                    case "on_tool_start":
                        full_response += f"""\n<details>
<summary><b>Call tool:</b> {event['name']}</summary>
<b>Arguments:</b>
{data['input']}"""
                    case "on_tool_end":
                        full_response += f"""<br><b>Result:</b>
{data['output']}
</details>"""
                message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
            message_placeholder.markdown(full_response, unsafe_allow_html=True)
            cursor.execute('INSERT INTO conversations (session_id, role, content) VALUES (?, ?, ?)',
                           (selected_session_id, "assistant", full_response))
            conn.commit()


if __name__ == '__main__':
    st.title("Simple Assistant")

    if "process" not in st.session_state:
        process: multiprocessing.Process = multiprocessing.Process(target=start_builtin_mcp_tools)
        process.daemon = True
        st.session_state.process = process
        process.start()
    if "loop" not in st.session_state:
        loop = asyncio.ProactorEventLoop()
        st.session_state.loop = loop
        asyncio.set_event_loop(loop)
    else:
        loop = st.session_state.loop

    loop.run_until_complete(main())
