import nospam.engine.rule as rule
import nospam.mail as mail
from typing import List
import re


class Engine(object):
    def __init__(self, rules: List[rule.Rule], p_s_w: float, p_h_w: float):
        '''
        Initialize engine with rules.
        :param rules: A set of rules used to initialize engine.
        :param p_s_w: spam_file_count / file_count
        :param p_h_w: ham_file_count / file_count
        :returns: Engine object.
        '''

        # Different rules.
        self.match_rules = dict()
        self.eq_rules = dict()
        self.contain_rules = dict()
        self.p_s_w = p_s_w
        self.p_h_w = p_h_w

        # Rearrange rules.
        for r in rules:
            if r.scope == rule.RULE_SCOPE_SUBJECT and not r.rule_type == rule.RULE_TYPE_EQ and not r.rule_type == rule.RULE_TYPE_MATCH:
                r.pattern = '*subject*' + r.pattern

            if r.rule_type == rule.RULE_TYPE_EQ:
                self.eq_rules[r.pattern] = r
            elif r.rule_type == rule.RULE_TYPE_HAVE:
                self.contain_rules[r.pattern] = r
            elif r.rule_type == rule.RULE_TYPE_MATCH:
                self.match_rules[r.pattern] = r

    def load_rules(self, rules: rule.Rule):
        self.match_rules = dict()
        self.eq_rules = dict()
        self.contain_rules = dict()

        for r in rules:
            if r.scope == rule.RULE_SCOPE_SUBJECT and not r.rule_type == rule.RULE_TYPE_EQ and not r.rule_type == rule.RULE_TYPE_MATCH:
                r.pattern = '*subject*' + r.pattern

            if r.rule_type == rule.RULE_TYPE_EQ:
                self.eq_rules[r.pattern] = r
            elif r.rule_type == rule.RULE_TYPE_HAVE:
                self.contain_rules[r.pattern] = r
            elif r.rule_type == rule.RULE_TYPE_MATCH:
                self.match_rules[r.pattern] = r

    def add_rule(self, r: rule.Rule):
        # Different scope should have different prefix.
        if r.scope == rule.RULE_SCOPE_SUBJECT and not r.rule_type == rule.RULE_TYPE_EQ and not r.rule_type == rule.RULE_TYPE_MATCH:
            r.pattern = '*subject*' + r.pattern

        if r.rule_type == rule.RULE_TYPE_EQ:
            self.eq_rules[r.pattern] = r
        elif r.rule_type == rule.RULE_TYPE_HAVE:
            self.contain_rules[r.pattern] = r
        elif r.rule_type == rule.RULE_TYPE_MATCH:
            self.match_rules[r.pattern] = r

    def test_mail(self, email: mail.Mail, ignore_low: int = 3, ignore_high: int = 20) -> (bool, float, List[rule.Rule]):
        '''
        :param email: email.Email object
        :param ignore_low: TODO
        :param ignore_high: TODO
        :returns: (is_spam?, probability)
        '''
        p_s_w = self.p_s_w
        p_h_w = self.p_h_w

        hit_rules = []

        for k in self.eq_rules:
            r = self.eq_rules[k]
            if (r.scope == rule.RULE_SCOPE_SENDER and r.pattern == email.sender) or \
                (r.scope == rule.RULE_SCOPE_SUBJECT and r.pattern == email.subject) or \
                (r.scope == rule.RULE_SCOPE_RECEIVER and r.pattern == email.receiver) or \
                    (r.scope == rule.RULE_SCOPE_CONTENT and r.pattern == email.content):
                p_s_w = 1000.0 * p_s_w * (r.spam_tf)
                p_h_w = 1000.0 * p_h_w * (r.ham_tf)
                hit_rules.append(r)

        for k in self.match_rules:
            r = self.match_rules[k]
            if (r.scope == rule.RULE_SCOPE_SENDER and not len(re.findall(k, email.sender)) == 0) or \
                (r.scope == rule.RULE_SCOPE_SUBJECT and not len(re.findall(k, email.subject)) == 0) or \
                (r.scope == rule.RULE_SCOPE_RECEIVER and not len(re.findall(k, email.receiver)) == 0) or \
                    (r.scope == rule.RULE_SCOPE_CONTENT and not len(re.findall(k, email.content)) == 0):
                p_s_w = 1000.0 * p_s_w * (r.spam_tf)
                p_h_w = 1000.0 * p_h_w * (r.ham_tf)
                hit_rules.append(r)

        # Test contents
        words = email.tokenify()
        word_set = set()

        for word in words:
            # Ignore invalid words
            if len(word) < ignore_low or len(word) > ignore_high:
                continue

            word = word.lower()

            # Test if it is spam
            if (word in self.contain_rules) and not (word in word_set):
                word_set.add(word)
                p_s_w = 1000.0 * p_s_w * (self.contain_rules[word].spam_tf)
                p_h_w = 1000.0 * p_h_w * (self.contain_rules[word].ham_tf)
                hit_rules.append(self.contain_rules[word])

            if p_s_w == 0.0:
                return (False, 0.0, hit_rules)

        # Calculate results
        result = p_s_w / (p_s_w + p_h_w)

        if result > 0.9:
            return (True, result, hit_rules)
        return (False, result, hit_rules)
