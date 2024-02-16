import streamlit as st
from PIL import Image
from streamlit_chat import message

import utils

def initialize_session_state():
    """
    Session state is a way to share variables between runs, for each user session.
    """
    
    st.session_state.setdefault('history', [])
    st.session_state.setdefault('generated', ["Hello, I am here to provide answers to questions fetched from Database."])
    st.session_state.setdefault('past', ["Hello Buddy!"])

def display_chat(conversation_chain,chain):
    """
    Streamlit relatde code wher we are passing conversation_chain instance created earlier
    It creates two containers
    container: To group our chat input form
    reply_container: To group the generated chat response

    Args:
    - conversation_chain: Instance of LangChain ConversationalRetrievalChain
    """
    #In Streamlit, a container is an invisible element that can hold multiple 
    #elements together. The st.container function allows you to group multiple 
    #elements together. For example, you can use a container to insert multiple 
    #elements into your app out of order.
    
    reply_container = st.container()
    container = st.container()
    
    with container:
        with st.form(key='chat_form', clear_on_submit=True):
            user_input = st.text_input("Question", placeholder="Ask me a question from uploaded database history", key='input')
            submit_button = st.form_submit_button(label='Send ⬆️')
        
        if submit_button and user_input:
            generate_response(user_input, conversation_chain, chain)
        
    display_generated_response(reply_container)

def generate_response(user_input, conversation_chain, chain):
    
    with st.spinner('Generating response...'):
        # Generate response
        response = conversation_chat(user_input, conversation_chain, chain, st.session_state['history'])
        
        
        # Update session state
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(response)
        ## st.session_state.past.append(response)
def conversation_chat(user_input, conversation_chain, chain, history):
    
    response = conversation_chain.invoke(user_input)
    final_response = chain.invoke(f"Based on the following information generate human redable response: {response['query']},  {response['result']}")

    history.append((user_input, final_response))
    return final_response
def display_generated_response(reply_container):
        
    if st.session_state['generated'])):
           with reply_container:
              for i in range(len(st.session_state)['generated'])):
                  message(st.session_state['past'][i), is_user=True, key=f'{i}_user',avatar_style='adventurer')
                  message(st.session_state['generated'][i], is_user=True, key=f'{i}_user',avatar_style='bottts')
                  
                  
def main():
    # Step 1 
    initialize_session_state()
    
    st.title("Genie")
    
    image = Image.open('chatbotsolo_150x154.jpg')
    st.image(image, width=208)

    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Step 2
    conversation_chain, chain = utils.create_conversational_chain()
    
    # Step 3
    display_chat(conversation_chain, chain)
    
    if __name__ == "__main__":
        main()
    