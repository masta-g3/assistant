import streamlit as st
import time, os
from dotenv import load_dotenv

load_dotenv()

from chatbot import Manager

# from callbacks import NewStreamlitCallbackHandler


def message_bubble(msg: str, is_user: bool = False, idx: int = 0):
    if is_user:
        user_msg = f"#### Q{idx}: {msg}"
        st.markdown(user_msg, unsafe_allow_html=True)
    else:
        manager_msg = f"{msg}"
        st.markdown(manager_msg, unsafe_allow_html=True)


st.set_page_config(
    layout="wide",
    page_title="Manager",
    page_icon="",
    initial_sidebar_state="expanded",
)

if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []

if "manager" not in st.session_state:
    st.session_state["manager"] = None

if "handler" not in st.session_state:
    st.session_state["handler"] = None

if "openai_key" not in st.session_state:
    st.session_state["openai_key"] = None

#############
## SIDEBAR ##
#############
## centered title on sidebar
st.sidebar.markdown(
    "<h1 style='text-align: center;'>Ask Manager</h1>",
    unsafe_allow_html=True,
)

sidebar_tabs = st.sidebar.tabs(["⚙️ Customization", "💾 Data", "🐛 Steps"])
with sidebar_tabs[0]:
    ## API key input.
    openai_key = st.text_input(
        "OpenAI API Key", type="password", value=os.environ.get("OPENAI_API_KEY", "")
    )

    ## Form to customize Manager.
    customize_form = st.form(key="customize_form")
    customize_form.markdown("### Customize Manager")
    llm_model = customize_form.selectbox(
        "LLM", ["gpt-3.5-turbo-0613", "gpt-4-0613"], index=0
    )
    system_message = customize_form.text_area(
        "System Message",
        value="You are a smart AI assistant that uses markdown and emojis to communicate. When asked a question, you reply as a great spiritual master in a clear and simple way, leveraging your knowledge on science, the Buddhist texts, the Tao Te Ching, Platonic texts, Bhagavad Gita, the Bible, and the Quran.",
        help="Provide a custom system prompt to define Manager's personality.",
        height=10,
    )
    agent_tools = customize_form.multiselect(
        "Tools", ["Python", "Web Search"], default=["Python", "Web Search"]
    )
    tool_dict = {
        "Python": "python_repl",
        "Web Search": "search_api",
    }
    tool_list = [tool_dict[tool] for tool in agent_tools]

    if "Web Search" in agent_tools:
        serp_api_key = customize_form.text_input(
            "SerpAPI Key (Web Search)",
            type="password",
            value=os.environ.get("SERPAPI_API_KEY", ""),
        )

    if st.session_state["manager"] is None:
        reset_manager = customize_form.form_submit_button("Load Manager")
    else:
        reset_manager = customize_form.form_submit_button("Reset Manager")

    if reset_manager:
        if len(openai_key) == 0:
            err_msg = st.error("Please provide an OpenAI API key.")
            time.sleep(2)
            err_msg.empty()
            st.experimental_rerun()
        else:
            st.session_state["openai_key"] = openai_key
        if "Web Search" in agent_tools:
            if len(serp_api_key) == 0:
                err_msg = st.error("Please provide a SerpAPI API key.")
                time.sleep(2)
                err_msg.empty()
                st.experimental_rerun()
            else:
                os.environ["SERPAPI_API_KEY"] = serp_api_key
        manager = Manager(
            model_name=llm_model,
            openai_api_key=openai_key,
            system_message=system_message,
            tool_list=tool_list,
        )
        st.session_state["manager"] = manager

with sidebar_tabs[1]:
    ## Form to upload dataset and its description.
    upload_form = st.form(key="upload_form")
    uploader_title = upload_form.markdown("### 📤 Chat with a Dataset")
    file_uploader = upload_form.file_uploader(
        "Chat with your data.", label_visibility="collapsed", type="csv"
    )
    desc_help = "Provide a description of the data you are uploading. What is it about, is it a time series, etc."
    file_description = upload_form.text_input("Description", help=desc_help)
    file_submit = upload_form.form_submit_button("Submit")

with sidebar_tabs[2]:
    st.markdown("### Thought Process")
    thought_process_placeholder = st.empty()

##############
## MAIN APP ##
##############

# st.markdown("# Chat with Manger")
text_input_placeholder = st.empty()


def query(message):
    manager = st.session_state["manager"]
    response = manager.run(message)  # , callbacks=[st.session_state["handler"]])
    # st.write(st.session_state['handler'].code_stream)
    # st.write(st.session_state['handler'].thought_stream)
    # response = "Hello! I am GPT Bento, I am here to help you with your data needs."
    return response


def get_text():
    input_text = text_input_placeholder.text_input(
        "You: ", "Provide inspiration to achieve my goals today.", key="input"
    )
    return input_text


def main():
    if st.session_state["manager"] is None:
        st.markdown("# 🤖 Add OpenAI API key & load Manager")
        return

    user_input = get_text()

    if user_input:
        output = query(user_input)

        st.session_state.past.append(user_input)
        st.session_state.generated.append(output)

    if st.session_state["generated"]:
        for i in range(len(st.session_state["generated"]) - 1, -1, -1):
            st.markdown("---")
            message_bubble(st.session_state["past"][i], is_user=True, idx=i)
            message_bubble(st.session_state["generated"][i], is_user=False, idx=i)


if __name__ == "__main__":
    # if not st.session_state["agent"]:
    # agent_manager = Manager(llm_model)
    # handler = NewStreamlitCallbackHandler(st.empty(), thought_process_placeholder)
    # st.session_state["handler"] = handler
    # st.session_state["agent"] = agent_manager
    main()
