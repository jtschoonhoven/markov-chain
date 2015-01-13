
# coding: utf-8

# In[1]:

import pykov
import re


# In[112]:

class Markov:


    def __init__(self, text, match_n_words):
        self.match  = match_n_words
        word_list   = self.make_word_list(text.lower())
        phrase_dict = self.make_phrase_dict(word_list)
        self.chain  = self.make_markov_chain(phrase_dict)


    # Split text on word and punctuation.
    def make_word_list(self, text):
        return re.findall(r"[\w']+|[.,!?;]", text)


    # A "phrase" is a tuple of length "match_n_words".
    # The phrase_dict maps phrases with a count of words that follow.
    # E.g. dict = { ('Hello', 'world'): {'!': .9, '.': .1} }

    def make_phrase_dict(self, word_list):
        phrase_dict = {}

        # For each word in list, less the number of matches...
        for i in range(len(word_list) - self.match):

            # Get phrase and next word at current index.
            phrase = tuple(word_list[i:(i + self.match)])
            next_word = word_list[i + self.match]
            
            # If phrase not yet in dict, add phrase and next word.
            if phrase not in phrase_dict:
                phrase_dict[phrase] = { next_word: 1 }
            
            # If phrase exists but not next word, add word.
            elif next_word not in phrase_dict[phrase]:
                phrase_dict[phrase][next_word] = 1
                
            # Else increment the number of times word has been used.
            else:
                phrase_dict[phrase][next_word] += 1
                
        return phrase_dict


    # Return an instance of pykov.Chain.
    def make_markov_chain(self, phrase_dict):
        mapping = {}

        # Sum number of times each phrase appears.
        for phrase in phrase_dict:
            next_words  = phrase_dict[phrase]
            denominator = sum(next_words.values())

            # Get probability that each word follows a phrase.
            for word in next_words:
                count = next_words[word]
                prob  = count/float(denominator)
                
                # Format for pykov. Reads, "phrase" is followed by "word" "prob" % of the time.
                mapping[(phrase, word)] = prob
                
        return pykov.Chain(mapping)
    
    
    # Give a prompt on which to build a sentence of length "word_count".
    # Prompt must be at least "match_n_words" in length and exist in dict.
    
    def prompt(self, prompt, word_count):
        word_list = self.make_word_list(prompt)
        
        for i in range(word_count):
            last_n_words = word_list[-self.match:]
            phrase_key   = tuple(last_n_words)
            next_word    = self.chain.move(phrase_key)
            word_list.append(next_word)
        
        # Return formatted output.
        self.output = self.list_to_sentence(word_list)
        print self.output
        
    
    # A reducer function that concatentates word_list.
    def list_to_sentence(self, word_list):
        string = word_list[0].capitalize()
        
        for i in range(len(word_list)-1):
            sep = ' '
            
            a = word_list[i]
            b = word_list[i+1]
            
            if a in '.!?': b = b.capitalize()
            if b in '.,!?;': sep = ''
            
            string += sep + b
        
        return string
    


# In[113]:

text = open('/Users/jonathanschoonhoven/Desktop/ummm.txt').read() #.decode('UTF-8', 'string-escape')

m = Markov(text, 1)

m.prompt('wesley', 100)


# In[103]:




# In[ ]:



