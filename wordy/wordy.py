from math import log10
from csv import DictReader
from statistics import mean, median


def get_data():
    """
    Get the word frequency data
    :return:
    """
    file = 'data/unigram_freq.csv'
    return [dict(i) for i in DictReader(open(file, 'r'))]


def get_test_data(num=1):
    """
    Get a test data file
    :param num: number, 1 or 2
    :return:
    """
    file = 'data/test_data_%s.txt' % num
    return open(file, 'r').read()


def get_word_freq():
    """
    Get a word frequency dictionary
    :return: dict word -> relative frequency
    """
    data = get_data()
    count_max = float(data[0]['count'])
    counts = {i['word']: float(i['count'])/count_max for i in data}
    return counts


def med_filt(data, n, agg='median'):
    """
    Median filter or other aggregates
    :param data: list of numbers
    :param n: size of window, odd number is best
    :param agg: 'median', 'mean' or 'max'
    :return:
    """
    result = []
    num = len(data)
    for i in range(num):
        i_min = max(i-n, 0)
        i_max = min(i+n, num-1)
        subset = data[i_min: i_max]
        if agg == 'median':
            value = median(subset)
        elif agg == 'mean':
            value = mean(subset)
        elif agg == 'max':
            value = max(subset)
        else:
            raise ValueError("agg must be 'median', 'mean' or 'max' ")

        result.append(value)

    return result


class Highlighter:
    """
    Highlight or mask natural text within a larger document filled
    with other stuff
    """
    def __init__(self):
        """
        Load the data
        """
        self._data = get_word_freq()

    def get(self, word):
        """
        :param word: string
        :return: (count, relative frequency) tuple
        """
        return self._data.get(word)

    def __call__(self, word):
        """
        Log10(relative frequency)
        goes from 0 to 10
        :param word: string
        :return: log10 relative frequency + 10
        """
        word = word.strip().lower()
        rem_chars = ['.', ',', '?', '!', "'",
                     '"', '(', ')']
        for char in rem_chars:
            word = word.replace(char, '')

        res = self.get(word)
        if res is None:
            return 0

        return log10(res)+10

    def f(self, word):
        """
        An alias for __call__
        :param word:
        :return:
        """
        return self.__call__(word)

    def freq_list(self, text, n=3):
        """
        Get a list of words, frequency and smoothed frequency
        :param text: string of text
        :param n: window size, odd number is best
        :return: list of word, frequency, smoothed frequency
        """
        words = text.split()
        freq = [self.f(word) for word in words]
        smooth_med = med_filt(freq, n, agg='median')
        smooth_mean = med_filt(freq, n, agg='mean')
        smooth_max = med_filt(freq, n, agg='max')
        smooth = [0.4*i + 0.2*j + 0.2*k + 0.2*l for i, j, k, l in
                  zip(smooth_med, smooth_mean, smooth_max, freq)]

        result = list(zip(words, freq, smooth))
        return result

    def word_mask(self, text, n=3, thresh=4.5):
        """
        :param text: string of text
        :param n: window size, odd number is best
        :param thresh: threshold for masking
        :return: list of (word, mask)
            where mask is 1 if marked text and 0 otherwise
        """
        freq = self.freq_list(text, n=n)
        mask = [(x[0], x[2] >= thresh) for x in freq]
        return mask

    def get_highlight(self, text, n=3, thresh=4.5, mask_out=None, color='cyan'):
        """
        :param text: string of text
        :param n: window size, odd number is best
        :param thresh: thresh: threshold for masking
        :param mask_out: if provided will replace masked out
            text with this character, otherwise will just color
        :return: marked up string to be printed
        """

        # terminal text colors
        # see here https://ozzmaker.com/add-colour-to-text-in-python/

        colors = {
            'ENDC': "\033[0m",
            'green': "\033[1;32;40m",
            'magenta': "\033[1;35;40m",
            'cyan': "\033[1;36;40m"}

        start = colors[color]
        end = colors['ENDC']

        mask = self.word_mask(text, n=n, thresh=thresh)
        new_text = ""
        state = 0
        for word, mask_val in mask:
            if state == 0:
                if mask_val:
                    state = 1
                    new_text += start
            else:
                if not mask_val:
                    state = 0
                    new_text += end

            if mask_out is not None and state == 0:
                new_text += mask_out
            else:
                new_text += (" " + word)

        return new_text

    def highlight(self, text, n=3, thresh=4.5, mask_out=None):
        """
        Print the marked up text in color
        :param text: string of text
        :param n: window size, odd number is best
        :param thresh: thresh: threshold for masking
        :param mask_out: if provided will replace masked out
                text with this character, otherwise will just color
        :return: marked up string to be printed
        """

        highlighted = self.get_highlight(text, n=n, thresh=thresh,
                                         mask_out=mask_out)
        print(highlighted)
