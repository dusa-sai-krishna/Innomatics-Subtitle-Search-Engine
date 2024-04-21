import pandas as pd
import chromadb
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import collections
import google.generativeai as genai
import json
# Download NLTK resources if not already downloaded
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('stopwords')

with open(r'C:\Users\dsai9\Projects\Semantic Search Engine\GEMINI_API_KEY.txt', 'r') as f:
    api_key = f.read().strip()

sys_instruction='''
    for the given list of strings. You should be able to parse following things
    
    1.name of the show not the episode name(remember it can be a tv show or a movie or an anime) 
    2.Type(movie or tv show or anime)
    3.year
    4.season(return blank if it's a movie)
    5. episode(return blank if it's a movie)
    5. language
    
    I always want response to be in json format. So crosscheck this instruction twice.
    
'''
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro-latest',system_instruction=sys_instruction)

def getDetails(lst):

    prompt=sys_instruction+f'Instruction: List of strings are:\n{lst}'
    
    response=model.generate_content(prompt)
    
    markdown_content=response.text
    print(markdown_content)
    try:
        # Extract JSON content from the Markdown file (assuming JSON content is enclosed in ```json ... ```)
        json_start = markdown_content.find('```json') + len('```json')
        json_end = markdown_content.find('```', json_start)
        json_content = markdown_content[json_start:json_end]
    except Exception as e:
        print(e)
        json_content=markdown_content[1:-1]#removing quotations

    # Parse the extracted JSON content
    data = json.loads(json_content)
    
    result_df=pd.DataFrame(data,index=[i+1 for i in range(len(data))])
    
    return result_df
    





def text_preprocessing(corpus, flag):
    # Compiled regular expressions for patterns
    pattern1 = re.compile(r'\d+\r\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}')
    pattern2 = re.compile(r'\r\nWatch any video online with Open-SUBTITLES\r\nFree Browser extension: osdb.link/ext\r\n\r\n\r\n')
    pattern3 = re.compile(r'Please rate this subtitle at www.osdb.link/agwma\r\nHelp other users to choose the best subtitles')
    pattern4 = re.compile(r'(\r\n)+')
    pattern5 = re.compile(r'<[/]?\w+>')
    # Stopwords
    stop_words = set(stopwords.words('english'))

    # remove timestamps
    corpus = re.sub(pattern1, '', corpus)

    # remov header and footer
    corpus = re.sub(pattern2, '', corpus)
    corpus = re.sub(pattern3, '', corpus)

    # remove extra line breaks
    corpus = re.sub(pattern4, '\r\n', corpus)

    # remove html tags
    corpus = re.sub(pattern5, '', corpus)

    # change  of numbers
    #p = inflect.engine()
    #corpus = re.sub(r'\d+', lambda x: p.number_to_words(x.group(0)), corpus)

    # remove special characters
    corpus = re.sub('[^a-zA-Z]', ' ', corpus)

    # convert to lower case
    corpus = corpus.lower()

    # removal of whitespaces
    corpus = ' '.join(corpus.split())

    # tokenize
    words = word_tokenize(corpus)

    # Stemming or Lemmatization
    if flag == "stemming":
        # stemming
        stemmer = SnowballStemmer(language='english')
        return ' '.join(stemmer.stem(word) for word in words if word not in stop_words)
    else:
        # lemmatization
        lemmatizer = WordNetLemmatizer()
        return ' '.join(lemmatizer.lemmatize(word) for word in words if word not in stop_words)




# create a function where user query returns top 10 relevant searches
def getResults(query,flag):
    
    # Pre process the query
    text=text_preprocessing(query, flag)
    print(text)
    

    #create a persistentClient
    client=chromadb.PersistentClient(path=r"C:\Users\dsai9\Projects\Semantic Search Engine\data\ChromaDB")
     #create or get a collection
    collection=client.get_or_create_collection(name='transcripts',metadata={"hnsw:space": "cosine"})

    #read the names file
    df=pd.read_csv(r'C:\Users\dsai9\Projects\Semantic Search Engine\data\names.csv', index_col=0)
    
    #query with Chroma DB
    results = collection.query(
        query_texts=[text],
        n_results=20
    )
    
    
    #get distinct names
    ids=results['ids'][0]
    names=[]
    hashmap=collections.defaultdict()
    for i in ids:
        parent_id=i.split('-')[0]
        df.loc[int(parent_id),'name']
        if parent_id not in hashmap:
            hashmap[parent_id]=1
            names.append(df.loc[int(parent_id),'name'])
    
    return names[:10]




