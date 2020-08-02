import pandas as pd
import numpy as np
import re
import nltk
import matplotlib.pyplot as plt
import logging
import gensim
from gensim.utils import simple_preprocess
from collections import Counter
from spacy.lang.fr.stop_words import STOP_WORDS as fr_stop
from spacy.lang.en.stop_words import STOP_WORDS as en_stop
from spacy.lang.es.stop_words import STOP_WORDS as es_stop

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s[%(name)s][%(levelname)s] %(message)s',
                    datefmt='[%Y-%m-%d][%H:%M:%S]')


logger = logging.getLogger(__name__)

stopwords = list(fr_stop) + list(en_stop)+ list(es_stop)

class Preprocces():
    def __init__(self,data):
        self.data = data
    
    def clean_dataframe(self):
        df = pd.read_csv(self.data)
        logger.info('Remove column :' + df.columns[0])
        df = df[df.columns[1:]]
        logger.info('Shape of dataframe:'+ str(df.shape))
        logger.info('Checking is there is null values')
        
        if len(df[df.isna().any(axis=1)]):
            logger.info('Remove null values: '+ str(len(df[df.isna().any(axis=1)])))
            df.dropna(inplace=True) 

        logger.info('Remove digits and digits with words example : 460bc --> ""')
        df['Cleaned_text']=df['Text'].apply(lambda x: re.sub('\w*\d\w*','', x))
        df['Cleaned_text']=df['Text'].apply(lambda x: re.sub('http','', x))

        logger.info('Transform words to lowercase example: Electronics --> electronics')
        logger.info('Remove special characters example : $# -->"" ')
        df['Cleaned_text']=df['Cleaned_text'].apply(lambda x: " ".join(gensim.utils.simple_preprocess(x)))

        logger.info('Remove words with lenght less than three example : for --> "" ')
        df['Cleaned_text'] = df['Cleaned_text'].apply(lambda x: self.remove_words_l3(x))
        
        logger.info('Remove stop words in any language example : para --> "" ')
        pattern = re.compile(r'\b(' + r'|'.join(stopwords) + r')\b\s*')
        df['Cleaned_text'] = df['Cleaned_text'].apply(lambda x: pattern.sub('', x))

        if len(df[df.duplicated(subset=['Cleaned_text'])])>1:
            logger.info('Remove duplicates values: '+ str(len(df[df.duplicated(subset=['Cleaned_text'])])))
            df.drop_duplicates(subset =['Cleaned_text'], inplace = True)

        logger.info('Dataframe is cleaned')
        logger.info('Shape of dataframe:'+ str(df.shape))

        unique_words = set()
        df['Cleaned_text'].str.split().apply(unique_words.update)
        
        logger.info('Total of Unique words in text :' + str(len(unique_words)))

        count_words = Counter()
        df['Cleaned_text'].str.split().apply(count_words.update)

        values =count_words.values()

        total = sum(values)
        logger.info('Total of words in text :'+ str(total))
        stats_data = {'unique_words':unique_words,'count_words':count_words}
        
        return df, stats_data

    def remove_words_l3(self,text):

        token_text = text.split()
        
        clean_text = " ".join([word for word in token_text if len(word)>3])
            
        return clean_text

    def plot_categories(self,df):
        df_category = pd.DataFrame({'Category':df.label.value_counts().index, 'Number_of_documents':df.label.value_counts().values})
        df_category.plot(x='Category', y='Number_of_documents', kind='bar', legend=False, grid=True, figsize=(8, 5))
        plt.title("Number of documents per category")
        plt.ylabel('# of Documents', fontsize=12)
        plt.xlabel('Category', fontsize=12)

        return 

    def plot_common_words(self,count_words):
        sort_words = sorted(count_words.items(), key=lambda x: x[1], reverse=True)
        data = sort_words[:20]
        n_groups = len(data)
        values = [x[1] for x in data]
        words = [x[0] for x in data]
        plt.figure(figsize=(8, 5))
        plt.xticks(rotation=90)
        plt.bar(range(n_groups),values,tick_label=words)
        plt.title("Twenty most common words")
        plt.ylabel('# Ocurrences', fontsize=12)
        plt.xlabel('Word', fontsize=12)
        return 
    
    def plot_less_common_words(self,count_words):
        sort_words = sorted(count_words.items(), key=lambda x: x[1], reverse=False)
        data = sort_words[:20]
        n_groups = len(data)
        values = [x[1] for x in data]
        words = [x[0] for x in data]
        plt.figure(figsize=(8, 5))
        plt.xticks(rotation=90)
        plt.bar(range(n_groups),values,tick_label=words)
        plt.title("Twenty less common words")
        plt.ylabel('# Ocurrences', fontsize=12)
        plt.xlabel('Word', fontsize=12)
        return 

    def plot_language_category(self,df):
        values = dict()
        data = []
        for label in set(df.label):
            for language in set(df.language):
                try :
                    df[(df.label==label)& (df.language==language)].label.value_counts().values[0]
                    values['value']=df[(df.label==label)& (df.language==language)].label.value_counts().values[0]
                    
                except Exception:
                    values['value'] = 0
                    
                values['label']= label
                values['language']=language
                    
                
                data.append(values)
                values = {}
        
        df_language = pd.DataFrame(data)
        pd.pivot_table(df_language, index='language', columns='label', values='value').plot(kind='bar',grid=True, figsize=(8, 5))
        plt.title("Number of documents per category and Language")
        plt.ylabel('# of Documents', fontsize=12)
        plt.xlabel('Languages', fontsize=12)
        plt.legend(bbox_to_anchor=(1.04,1), borderaxespad=0)

        return 



    











