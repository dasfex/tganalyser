#! /usr/bin/python3

import sys
from lxml import etree
from io import StringIO


class Normalizer:
    @staticmethod
    def make_login(s: str):
        i = len(s) - 1
        while not s[i].isalpha():
            i -= 1
        s = s[:i + 1]
        return s

    @staticmethod
    def make_from_right_side(s: str):
        i = len(s) - 1
        while i >= 0 and s[i] in [',', '.', ':', ';', '!', '?', ')', '(', '-', '\'', '\"', '<<', '>>']:
            i -= 1
        s = s[:i + 1]
        return s

    @staticmethod
    def make_text(s: str):
        s = Normalizer.make_from_right_side(s)
        s = Normalizer.make_from_right_side(s[::-1])
        return s[::-1].lower()


def unpack(element, unpacked, parent_div=False):
    if element.tag == 'div':
        if 'class' in element.attrib:
            val = element.attrib['class']
            if val == 'from_name':
                nickname = element.text.strip()
                unpacked.append((1, nickname))
            elif val == 'text':
                text = element.text.strip()
                if text != '':
                    unpacked.append((2, text))
    if element.tag == 'a' and parent_div:
        unpacked.append((2, element.text.strip()))
    for new_el in element:
        if element.tag == 'div' and \
                'class' in element.attrib and \
                element.attrib['class'] == 'text':
            unpack(new_el, unpacked, True)
        else:
            unpack(new_el, unpacked, False)

def analyze(files):
    users_count, words_count = {}, {}
    messages_count = 0
    parser = etree.HTMLParser()
    last_user = ''
    for filename in files:
        with open(filename) as file:
            tree = etree.parse(StringIO(file.read()), parser)
            root = tree.getroot()
            unpacked = []
            unpack(root, unpacked)

            for pair in unpacked:
                if pair[0] == 1:
                    last_user = pair[1]
                    if pair[1] not in users_count:
                        users_count.update([(last_user, 0)])
                elif pair[0] == 2:
                    messages_count += 1
                    users_count[last_user] += 1
                    words = pair[1].split()
                    for word in words:
                        word = Normalizer.make_text(s=word)
                        if word != '':
                            if word not in words_count:
                                words_count.update([(word, 1)])
                            else:
                                words_count[word] += 1

    users = []
    for key, value in users_count.items():
        users.append((key, value))
    users = sorted(users, key=lambda x: x[1], reverse=True)
    words = []
    for key, value in words_count.items():
        words.append((key, value))
    words = sorted(words, key=lambda x: x[1], reverse=True)

    return messages_count, users, words


if __name__ == '__main__':
    c, u, w = analyze([sys.argv[i] for i in range(1, len(sys.argv))])
#    print(c)
#    print(u)
    print(w)
