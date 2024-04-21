import streamlit as st
import streamlit_scrollable_textbox as stx 
from utils import text_preprocessing, getResults, getDetails
import re
import numpy as np
#setting pageconfig
st.set_page_config(
    page_title="Search Subs",
    page_icon='🔎'
)

#title
st.title("Subtitle Search Engine")

#taking query
query=st.text_area("Describe characters of a show with their names to get subtitles ")
submit=st.button("Search")

#Initializing session state
if 'search_state' not in st.session_state:
    st.session_state['search_state'] = False

if (submit or st.session_state['search_state']) and re.search(r'\w+', query):
    
    st.session_state.search_state=True
    
    # Pre process the query
    text=text_preprocessing(query, 'stemming')
    
    #get results
    names=getResults(text,'stemming')
    #st.write(names)
    
    #get information
    information=getDetails(names)
    
    st.write(information)
    
    
    selected_name=st.selectbox(label="Select a Name",options=names,placeholder="Select a name",index=None)
    flag=st.button('Select')
    if flag==True:
        st.write(selected_name)
    
        if re.search(r'\w+', selected_name):
            with open(r'C:\Users\dsai9\Projects\Semantic Search Engine\data\transcripts\{}.srt'.format(selected_name),'r',encoding='utf-8') as file:
                
                # Read the file and convert its content to a string
                content = file.read()

                # Decode the string using the unicode_escape encoding
                #decoded_content = content.encode('utf-8').decode('unicode_escape')

            stx.scrollableTextbox(content,height=500)
            
            st.download_button(
                label="Download Transcript",data=content,file_name=selected_name,mime="text/plain",help='click on this button to download above transcript'
            )
