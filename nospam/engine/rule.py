from lark import Lark, Transformer, v_args

# Some static variables
RULE_TYPE_MATCH = 0x01
RULE_TYPE_EQ = 0x02
RULE_TYPE_HAVE = 0x03

RULE_SCOPE_SENDER = 0x11
RULE_SCOPE_RECEIVER = 0x12
RULE_SCOPE_SUBJECT = 0x13
RULE_SCOPE_CONTENT = 0x14

RULE_GRAMMER = r'''
        start: rule*
        rule: "if" condition "then" assignment_block "end"
        condition: mail_field operator pattern
        mail_field: "[" field "]"
        field: /\w+\.\w+/
        operator: /\w+/
        pattern: string
        string: ESCAPED_STRING
        assignment_block: block_1 | block_2
        block_1: ham_tf spam_tf
        block_2: spam_tf ham_tf
        ham_tf: "HAM_TF" "=" signed_number
        spam_tf: "SPAM_TF" "=" signed_number
        signed_number: SIGNED_NUMBER

        %import common.ESCAPED_STRING
        %import common.SIGNED_NUMBER
        %import common.WORD
        %import common.WS

        %ignore WS
'''


class Rule(object):
    def __init__(self, rule_type: int, scope: int, pattern: str, ham_tf: float, spam_tf: float):
        '''
        :param pattern: Pattern from email.
        :param ham_tf: Probability of appearancing of pattern.
        :param spam_tf: Probability of appearancing of pattern.
        :returns: Rule object.
        '''
        self.rule_type = rule_type
        self.scope = scope
        self.pattern = pattern
        self.ham_tf = ham_tf
        self.spam_tf = spam_tf

    def __str__(self):
        scope = ''
        pattern = self.pattern
        rule_type = ''

        if self.scope == RULE_SCOPE_SUBJECT:
            scope = 'mail.subject'
            if self.rule_type == RULE_TYPE_HAVE:
                pattern = pattern[9:]
        elif self.scope == RULE_SCOPE_SENDER:
            scope = 'mail.from'
        elif self.scope == RULE_SCOPE_RECEIVER:
            scope = 'mail.to'
        elif self.scope == RULE_SCOPE_CONTENT:
            scope = 'mail.content'

        if self.rule_type == RULE_TYPE_EQ:
            rule_type = '=='
        elif self.rule_type == RULE_TYPE_HAVE:
            rule_type = 'contain'
        elif self.rule_type == RULE_TYPE_MATCH:
            rule_type = 'match'

        return 'if' + ' [' + scope + '] ' + rule_type + ' "' + pattern + '" ' + 'then\n' + \
            '    ' + 'SPAM_TF = ' + str(self.spam_tf) + '\n' + \
            '    ' + 'HAM_TF  = ' + str(self.ham_tf) + '\n'


class RuleParser(object):
    def __init__(self):
        self.rules_parser = Lark(RULE_GRAMMER, parser='lalr',
                                 # Using the standard lexer isn't required, and isn't usually recommended.
                                 lexer='standard',
                                 # Disabling propagate_positions and placeholders slightly improves speed
                                 propagate_positions=False,
                                 maybe_placeholders=False).parser

    def parse(self, rules_str: str):
        rules = []
        parsed_result = self.rules_parser.parse(rules_str)

        for r in parsed_result.children:
            mail_field = r.children[0].children[0].children[0].children[0]
            operator = r.children[0].children[1].children[0]
            pattern = r.children[0].children[2].children[0].children[0][1:-1]
            spam_tf = 0.0
            ham_tf = 0.0
            for tf in r.children[1].children[0].children:
                if tf.data == 'spam_tf':
                    spam_tf = float(tf.children[0].children[0])
                elif tf.data == 'ham_tf':
                    ham_tf = float(tf.children[0].children[0])

            rule_type = 0x00
            rule_scope = 0x00

            if mail_field == 'mail.subject':
                rule_scope = RULE_SCOPE_SUBJECT
            elif mail_field == 'mail.sender':
                rule_scope = RULE_SCOPE_SENDER
            elif mail_field == 'mail.content':
                rule_scope = RULE_SCOPE_CONTENT

            if operator == 'equal':
                rule_type = RULE_TYPE_EQ
            elif operator == 'contain':
                rule_type = RULE_TYPE_HAVE
            elif operator == 'match':
                rule_type = RULE_TYPE_MATCH

            rules.append(Rule(rule_type, rule_scope, pattern, ham_tf, spam_tf))
        
        return rules
