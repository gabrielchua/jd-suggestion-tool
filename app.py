import streamlit as st

import openai
import chromadb
import urllib3
import json
import re

import utils


##############################
st.set_page_config(
    page_title="JD Suggestion Tool",
    page_icon="✨")


st.title("JD Suggestion Tool 🔎")

st.write("_Prototype is currently scoped only for financial services jobs_")

mcf_url = st.text_input("Enter MCF url")


###############################
openai.api_type = 'azure'
openai.api_base = st.secrets["API_BASE"]
openai.api_version = '2023-03-15-preview'
openai.api_key = st.secrets["API_KEY"]

###############################
http = urllib3.PoolManager()

###############################
chroma_client = chromadb.PersistentClient()

try: 
    collection = chroma_client.create_collection(name="JTMs")
    print("new chroma db")
except:
    collection = chroma_client.get_collection(name="JTMs")
    print("load existing chroma db")

################################
if st.button("Enter"): 

    if mcf_url == "":
        st.warning("⚠️ Please enter the url for a MCF job posting")

    else:
        mcf_data = utils.get_mcf_job(mcf_url, http)
        mcf_desc = mcf_data['description']
        mcf_desc = utils.clean_html(mcf_desc)

        ################################
        jtm_extracts = utils.search_vec_db(mcf_desc, collection)

        #################################
        system_message = """

        You are a job re-design consultant in Singapore helping company. increase their productivity and increase talent attraction.
        You will receive a job description and extracts from Singapore's Job Transformation Map reports. The reports outline how jobs will need to evolve in the future.
        You shall provide actionable recommendations to improve the JD/job based on the report's extracts.
        You will provide at least 5 suggestions, and always format them as a JSON with this format

        {
        "recommendations": [
            {
            "title": "4-5 word summary of Recommendation 1",
            "description": Description of Recommendation 1
            }
        ]
        }

        If you receive a job description that is not a financial services job, return "Not Financial Services".

        """

        prompt = f"""

        The job description is delimited by "###", and report extracts delimited by "%%%"

        ###
        {mcf_desc}

        %%%
        {jtm_extracts[0]}
        {jtm_extracts[1]}
        {jtm_extracts[2]}

        """

        #################################

        with st.spinner('Generating Recommendations...'):
            gpt_response = openai.ChatCompletion.create(
            engine="gpt-4-32k",
            messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ]
            )

        recommendations = gpt_response["choices"][0]["message"]["content"]

        st.json(recommendations)
