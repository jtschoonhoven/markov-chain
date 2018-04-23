# coding: utf-8
import random
import re
from bisect import bisect_left
from collections import Counter, defaultdict

from typing import NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Set, Tuple  # noqa


WordChoice = NamedTuple('WordChoice', [('word', str), ('range', float)])


class MarkovChain(object):

    END_MARKS = frozenset(['.', '!', '?'])
    PUNCTUATION = frozenset(['.', '!', '?', ',', ';'])

    def __init__(self, text, match_n_words=2):
        # type: (str, int) -> None
        """
        Initialize a markov chain based on an input text.

        :param text: input text from which to generate markov chain
        :param match_n_words: num previous words to consider when choosing next
        """
        self.match_n_words = match_n_words
        self.words = self._make_word_list(text)
        self.should_capitalize = self.get_capitalized_words()
        self.phrase_dict = self._make_phrase_dict(self.words)

    def _make_word_list(self, text):
        # type: (str) -> List[str]
        """
        Split text into a list of words, numbers, and punctuation.

        :param text: input text from which to generate markov chain
        :return: list of all words, numbers, and punctuation in text
        """
        return re.findall(r"[\w']+|[.,!?;]", text)

    def _make_phrase_dict(self, word_list):
        # type: (List[str]) -> Dict[str, Dict[str, float]]
        """
        A "phrase" is one or more words that appear together in the text
        The phrase dict matches a phrase with all possible words that might
        follow and their frequency.
        e.g. result = {'Hello': {'world': .7, 'Harry': .2, ',': .1}}

        :param word_list: input text split into list of words
        :return: dictionary of phrases with frequency of possible next words
        """
        phrase_freq = defaultdict(Counter)  # type: Dict[Tuple[str, ...], Dict[str, int]]  # noqa
        phrase_dict = defaultdict(list)  # type: Dict[Tuple[str, ...], List[Tuple[str, float]]]  # noqa
        word_list = [word.lower() for word in word_list]  # make lowercase

        # For each word in list, less the number of matches...
        for i in range(len(word_list) - self.match_n_words):
            phrase = tuple(word_list[i:(i + self.match_n_words)])
            next_word = word_list[i + self.match_n_words].lower()
            phrase_freq[phrase][next_word] += 1

        for phrase, word_choices in phrase_freq.items():
            word_weight_range = 0
            sum_frequency = sum(word_choices.values())

            for next_word in word_choices:
                word_weight = word_choices[next_word] / float(sum_frequency)
                word_weight_range += word_weight
                word_choice = WordChoice(next_word, word_weight_range)
                phrase_dict[phrase].append(word_choice)

        return phrase_dict

    def get_capitalized_words(self, threshold=0.9):
        # type: (float) -> Set[str]
        """
        Return a list of words that should be capitalized. Simple and hacky.
        If a word is capitalized at least `threshold` % of the time in input,
        capitalize it in output also.
        """
        should_capitalize = set()  # type: Set[str]
        lowercase = Counter()  # type: Dict[str, int]
        uppercase = Counter()  # type: Dict[str, int]

        for word in self.words:
            if any(letter.isupper() for letter in word):
                uppercase[word.lower()] += 1
            else:
                lowercase[word] += 1

        for word in uppercase:
            if lowercase[word] / float(uppercase[word]) < 1 - threshold:
                should_capitalize.add(word)

        return should_capitalize

    def prompt(self, prompt, word_count=30):
        # type: (str, int) -> str
        """
        Give a prompt on which to build a sentence of length "word_count".
        Prompt must be at least "match_n_words" in length and exist in dict.

        :param prompt: seed text from which to generate string
        :param word_count: minimum length of generated string
        """
        word_list = self._make_word_list(prompt.lower())

        while True:
            if len(word_list) >= word_count:
                if word_list[-1] in self.END_MARKS:
                    return self.list_to_sentence(word_list)

            next_word = self.choose_next_word(word_list)
            word_list.append(next_word)

    def choose_next_word(self, word_list):
        # type: (List[str]) -> str
        """
        Choose next word based on a list of previous words.
        """
        phrase = tuple(x.lower() for x in word_list[-self.match_n_words:])

        # choose a random starting point if prompt does not match
        if not self.phrase_dict[phrase]:
            end_mark_idxs = []  # type: List[int]
            start_idxs = []  # type: List[int]

            for idx, word in enumerate(self.words):
                if word in self.END_MARKS:
                    end_mark_idxs.append(idx)

            for idx in end_mark_idxs:
                if idx < len(self.words) - (self.match_n_words + 1):
                    start_idxs.append(idx)

            word_idx = random.choice(start_idxs)
            words = self.words[word_idx:word_idx + self.match_n_words]
            phrase = tuple(x.lower() for x in words)

        next_word_choices = self.phrase_dict[phrase]
        next_word_ranges = [word.range for word in next_word_choices]
        next_word_idx = bisect_left(next_word_ranges, random.random())
        return next_word_choices[next_word_idx].word

    def list_to_sentence(self, word_list):
        # type: (List[str]) -> str
        """
        A reducer function that concatentates word_list.
        """
        string = word_list[0].capitalize()

        for idx, word in enumerate(word_list):
            sep = ' '
            next_word = word_list[idx + 1]

            if word in self.END_MARKS:
                next_word = next_word.capitalize()
            elif next_word in self.should_capitalize:
                next_word = next_word.capitalize()
            elif next_word in self.PUNCTUATION:
                sep = ''

            string += sep + next_word

            if idx == len(word_list) - 2:
                return string


if __name__ == '__main__':
    with open('./tao_te_ching.txt') as file_obj:
        text = file_obj.read()
        markov_chain = MarkovChain(text)
