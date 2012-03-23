import re
'''
Comparison Engine for -X
'''
class Comparator(object):
    def __init__(self, env):
        self.env = env


class Rule(object):
    '''
    Rules are used by the Matcher to determine if prefix matches
    '''
    def __init__(self, regex, action):
        self.regex = re.compile(regex)
        self.action = action

    def prefix(self, inpt):
        match = self.regex.match(inpt)
        if match:
            return match.group(0)
        else:
            return False

class Matcher(object):
    def __init__(self, rules = []):
        self.rules = rules

    def add_rule(self, regex, action):
        '''
        Add a rule to the matcher
        '''
        self.rules.append(Rule(regex, action))

    def prefixes(self, inpt):
        '''
        Get the longest matching prefix for each rule
        '''
        prefixen = []
        for rule in self.rules:
            prefixen.insert(0, {'rule': rule, 'prefix': rule.prefix(inpt)})
        return prefixen

    def winner(self, inpt):
        '''
        Find winning rule for the provided input
        '''
        prefixen = self.prefixes(inpt)

        maxP = 0
        winner = None

        for prefix in prefixen:
            if prefix['prefix'] and len(prefix['prefix']) >= maxP:
                maxP = len(prefix['prefix'])
                winner = prefix

        return winner

class Tokenizer(object):
    '''
    This is a Tokenizer without need for Tokens, just provides the basic
    lexical needs of skip, peek, next and eat.
    '''
    def __init__(self):
        self.next_token = None
        self.next_text = None
        self.matcher = Matcher()

    def set_input(self, inpt = ''):
        self.inpt = inpt
        self.matcher = Matcher()
        self.next_token = None
        self.next_text = None

    def skip(self, matched):
        '''
        Skips current character
        '''
        self.inpt = self.inpt[len(matched)::]
        self.next_token = None
        self.next_text = None

    def token(self, matched):
        self.inpt = self.inpt[len(matched)::]
        self.next_token = matched
        self.next_text = matched

    def peek(self):
        '''
        Returns next char without consuming it
        '''
        if self.next_token:
            return self.next_token

        while (self.next_token == None) and (self.inpt != ''):
            winner = self.matcher.winner(self.inpt)
            if not winner:
                raise ValueError("No rule matching {0}".format(self.inpt))
            winner['rule'].action(winner['prefix'])

        return self.next_token

    def next(self):
        '''
        Returns and consumes next text
        '''
        if not self.next_token:
            self.peek()
        t = self.next_token
        self.next_token = None
        return t

    def eat(self, text):
        '''
        Consumes text without returning it, throwing an error if incorrect
        syntax
        '''
        c = self.next()
        if self.next_text != text:
            raise ValueError("Parse error: expected {0}, got {1}".format(text,
                self.next_text))

    def add_rule(self, regex, action):
        self.matcher.add_rule(regex, action)



class Parser(object):
    '''
    Parser will parse expressions passed in -X with the following grammar:

    <Exp>       ::= <Term> <Symbol> <Exp> | <Term>
    <Term>      ::= ( <Exp> )
                 |  <Factor>
    <Factor>    ::= <Grain>
                 |  <Primitive>
                 |  <Module>
                 |  <Pillar>
    <Symbol>    ::= '>'
                 |  '<'
                 |  '>='
                 |  '<='
                 |  'and'
                 |  'or'
                 |  '=='
                 |  '=~'
    <Grain>     ::= grains[<String>]
    <Module>    ::= salt[<String>.<String>]
    <Pillar>    ::= pillar[<String>]
    <Primitive> ::= Int
                 |  String
    '''
    def __init__(self):
        t = Tokenizer()
        t.add_rule(r'[A-Za-z0-9]+', t.token)
        t.add_rule(r'\b(?:grains|salt|pillar)\[[^\]]+\]', t.token)
        t.add_rule(r'[()\']', t.token)
        t.add_rule(r'>=?|<=?|and|or|==', t.token)
        t.add_rule(r'[ \n\t\r]+', t.skip)
        self.t = t

    def parse(self, inpt):
        self.t.set_input(inpt)
        return self.parse_exp()

    def eval_tree(self, tree):
        if tree['op'] == '>':
            return tree

    def parse_exp(self):
        term = self.parse_term()
        symbol = self.parse_symbol()

        # <Term>
        if not symbol:
            return term

        # <Term> <Symbol> <Exp>
        return eval("{0} {1} {2}".format(term, symbol, self.parse_exp()))

    def parse_term(self):
        c = self.t.peek()
        if c == '(':
            self.t.eat(c)
            exp = self.parse_exp()
            self.t.eat(')')
            return exp
        if c in ["'", '"']:
            self.t.eat(c)
            exp = self.parse_primitive()
            self.t.eat(c)
            return "'{0}'".format(exp)
        return self.parse_factor()

    def parse_symbol(self):
        symbol = self.t.peek()
        if symbol not in ['>', '<', '>=', '<=', '==', 'and', 'or', '=~']:
            return None
        self.t.eat(symbol)
        return symbol

    def parse_factor(self):
        factor = self.t.next()
        return factor
        if factor.startswith('grains'):
            return self.parse_grain()
        elif factor.startswith('salt'):
            return self.parse_module()
        elif factor.startswith('pillar'):
            return self.parse_pillar()
        else:
            return self.parse_primitive()

    def parse_grain(self):
        return self.t.next()

    def parse_module(self):
        return self.t.next()

    def parse_pillar(self):
        return self.t.next()

    def parse_primitive(self):
        return self.t.next()

