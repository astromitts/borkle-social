class Score(object):
    score = 0
    score_type = 'borkle!'

    def get_sets(self):
        sets = {}
        for d in self.selection:
            sets[d] = sets.get(d, 0)
            sets[d] += 1
        return sets

    @property
    def has_any_of_a_kind(self):
        sets = self.get_sets()
        for idx, count in sets.items():
            if count >= 3:
                return True
        return False

    @property
    def has_one_or_five(self):
        return 1 in self.selection or 5 in self.selection

    @property
    def is_three_of_a_kind(self):
        return len(self.selection) == 3 and len(set(self.selection)) == 1

    @property
    def is_four_of_a_kind(self):
        return len(self.selection) == 4 and len(set(self.selection)) == 1

    @property
    def is_five_of_a_kind(self):
        return len(self.selection) == 5 and len(set(self.selection)) == 1

    @property
    def is_six_of_a_kind(self):
        return len(self.selection) == 6 and len(set(self.selection)) == 1

    @property
    def is_a_straight(self):
        return len(self.selection) == 6 and len(set(self.selection)) == 6

    @property
    def is_three_pairs(self):
        if len(self.selection) == 6:
            sets = self.get_sets()
            num_of_pairs = 0
            for k, amount in sets.items():
                if amount == 2:
                    num_of_pairs += 1
            return num_of_pairs == 3
        return False


    @property
    def is_two_triplets(self):
        if len(self.selection) == 6:
            sets = self.get_sets()
            num_of_trips = 0
            for k, amount in sets.items():
                if amount == 3:
                    num_of_trips += 1
            return num_of_trips == 2
        return False

    @property
    def is_four_of_kind_and_pair(self):
        if len(self.selection) == 6:
            sets = self.get_sets()
            has_a_four = False
            has_a_pair = False
            if len(sets) == 2:
                for k, amount in sets.items():
                    if amount == 4:
                        has_a_four = True
                    if amount == 2:
                        has_a_pair = True
                return has_a_pair and has_a_four
        return False

    @property
    def is_all_fives(self):
        return len(set(self.selection)) == 1 and self.selection[0] ==  5

    @property
    def is_all_ones(self):
        return len(set(self.selection)) == 1 and self.selection[0] == 1

    @property
    def is_all_ones_or_fives(self):
        if len(self.selection) > 0:
            for dice in self.selection:
                if dice not in[1, 5]:
                    return False
            return True
        return False


    @property
    def has_score(self):
        has_score = False
        if self.has_one_or_five:
            has_score = True
        if self.is_all_ones_or_fives:
            has_score = True
        if self.has_any_of_a_kind:
            has_score = True
        if self.is_a_straight:
            has_score = True
        if self.is_two_triplets:
            has_score = True
        if self.is_three_pairs:
            has_score = True
        if self.is_four_of_kind_and_pair:
            has_score = True
        return has_score

    def __init__(self, selection):
        self.selection = selection
        if self.is_four_of_kind_and_pair:
            self.score = 2500
            self.score_type = 'Four of a kind & a pair'
        elif self.is_two_triplets:
            self.score = 2500
            self.score_type = 'Two triplets'
        elif self.is_a_straight:
            self.score = 1500
            self.score_type = 'Straight'
        elif self.is_three_pairs:
            self.score = 1500
            self.score_type = 'Three pairs'
        elif self.is_three_of_a_kind and self.is_all_ones:
            self.score = 300
            self.score_type = 'Three ones'
        elif self.is_three_of_a_kind:
            self.score = self.selection[0] * 100
            self.score_type = 'Three of a kind'
        elif self.is_four_of_a_kind:
            self.score = 1000
            self.score_type = 'Four of a kind'
        elif self.is_five_of_a_kind:
            self.score = 2000
            self.score_type = 'Five of a kind'
        elif self.is_six_of_a_kind:
            self.score = 3000
            self.score_type = 'Flush'
        elif self.is_all_fives:
            self.score = len(self.selection) * 50
            self.score_type = 'Fives'
        elif self.is_all_ones:
            self.score = len(self.selection) * 100
            self.score_type = 'Ones'
        elif self.is_all_ones_or_fives:
            self.score_type = 'Ones and Fives'
            self.score = 0
            for dice in self.selection:
                if dice == 5:
                    self.score += 50
                elif dice == 1:
                    self.score += 100
        else:
            self.score = 0
            self.score_type = 'borkle!'
