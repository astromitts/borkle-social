from namer.words import adjectives, nouns
import random


class RandomName(object):
    def __init__(self):
        self.name = '{}-{}'.format(self.adjective(), self.noun())

    def adjective(self):
        return random.choice(adjectives)


    def noun(self):
        return random.choice(nouns)


def get_random_name():
    rn = RandomName()
    return rn.name
