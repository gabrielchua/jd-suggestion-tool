import openai
import urllib3
import json
import re

def get_embedding(text, engine="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   embeddings = openai.Embedding.create(input = [text], engine=engine)['data'][0]['embedding']
   return embeddings

def search_vec_db(text, collection):
    query_embedding = get_embedding(text)
    result = collection.query(
        query_embeddings=query_embedding,
        n_results = 3)
    return result['documents'][0]

def get_mcf_job(mcf_url, http):
    regex_matches = re.search('\\-{1}([a-z0-9]{32})\\?', mcf_url + "?")
    mcf_uuid = regex_matches.group(1)
    resp = http.request('GET',f'https://api.mycareersfuture.gov.sg/v2/jobs/{mcf_uuid}')
    return json.loads(resp.data)

def clean_html(text):
    # Remove HTML tags
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', text)
    
    # Replace HTML escape entities with their characters
    cleantext = cleantext.replace('&amp;', '&')
    cleantext = cleantext.replace('&lt;', '<')
    cleantext = cleantext.replace('&gt;', '>')
    cleantext = cleantext.replace('&quot;', '"')
    cleantext = cleantext.replace('&#39;', "'")
    
    # Remove line breaks
    cleantext = cleantext.replace('\n', ' ')  # Replace with space. If you prefer no space, replace with ''
    
    # Remove full HTTP links
    cleantext = re.sub(r'http\S+', '', cleantext)
    
    return cleantext