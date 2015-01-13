# Based on agiliq.com/blog/2009/06/generating-pseudo-random-text-with-markov-chains-u/
import pykov

class Markov:
    def __init__(self, file_location, phrase_len):
        self.phrase_len = phrase_len
        words = self.open_file(file_location)
        phrase_dict = self.make_phrases(words)
        self.chain = self.map_chain(phrase_dict)
    
    def open_file(self, file_location):
        text = open(file_location).read() #.decode('UTF-8', 'string-escape')
        words = text.split()
        return words
    
    def make_phrases(self, words):
        phrase_dict = {}
        for index, word in enumerate(words[:len(words)-self.phrase_len]):
            phrase = tuple(words[index : (index + self.phrase_len)])
            next_word = words[index + self.phrase_len]
            if phrase not in phrase_dict:
                phrase_dict[phrase] = { next_word: 1 }
            else:
                if next_word not in phrase_dict[phrase]:
                    phrase_dict[phrase][next_word] = 1
                else:
                    phrase_dict[phrase][next_word] += 1
        return phrase_dict
                    
    def map_chain(self, phrase_dict):
        mapping = {}
        for phrase in phrase_dict:
            next_words = phrase_dict[phrase]
            vector = pykov.Vector(next_words)
            vector.normalize()
            for word in vector:
                p = vector[word]
                tup = (phrase, word)
                mapping[tup] = p
        return pykov.Chain(mapping)
        
    def write(self, opening_remarks, word_count):
        chain = self.chain
        output_list = []
        seed = opening_remarks.split()
        output_list.append(seed)
        this_word = tuple(seed[len(seed)-self.phrase_len:])
        for i in range(word_count):
            next_word = chain.move(this_word)
            output_list.append(next_word)
            this_word = next_word
        print output_list


m = Markov('/Users/jonathanschoonhoven/Desktop/ummm.txt', 1)
m.write('THE LOVE', 4)


