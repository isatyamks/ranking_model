import nltk
from nltk.corpus import stopwords
import string

def remove_stop_words (text):
    
    def remove_stopwords(text, stopwords_file):
        with open(stopwords_file, 'r', encoding='utf-8') as file:
            stop_words = set(file.read().splitlines())
        words = nltk.word_tokenize(text)
        filtered_words = [word for word in words if word.lower() not in stop_words and word not in string.punctuation]
        return ' '.join(filtered_words)
    stopwords_file = 'stopwords.txt'
    clean_text = remove_stopwords(text, stopwords_file)
    return clean_text

