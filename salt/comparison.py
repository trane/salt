import re
'''
Comparison Engine for -X
'''
class Comparator(object):
    def __init__(self, env):
        self.env = env


class Rule(Comparator):
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

class Matcher(Comparator):
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

class Tokenizer(Comparator):
    '''
    This is a Tokenizer without need for Tokens, just provides the basic
    lexical needs of skip, peek, next and eat.
    '''
    def __init__(self, inpt = ''):
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

        while (self.next_token == None) and (self.inpt != ""):
            winner = self.matcher.winner(self.inpt)
            if not winner:
                return "No rule matching {0}".format(self.inpt)
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
        self.next()
        if self.next_text != text:
            return "Parse error: expected {0}, got {1}".format(text, self.next_text)

    def add_rule(self, regex, action):
        self.matcher.add_rule(regex, action)



class Parser(Comparator):
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
                 |  '&&'
                 |  '||'
                 |  '=='
                 |  '=~'
    <Grain>     ::= grains[<String>]
    <Module>    ::= salt[<String>.<String>]
    <Pillar>    ::= pillar[<String>]
    <Primitive> ::= Int
                 |  String
    '''
    def parse(self, inpt):
        t = Tokenizer(inpt)
        t.add_rule(r'[A-Za-z0-9]+', t.token)
        t.add_rule(r'\b(?:grains|salt|pillar)\[[^\]]+\]', t.token)
        t.add_rule(r'[()]', t.token)
        t.add_rule(r'>=?|<=?|&&|\|\|', t.token)
        t.add_rule(r'[ \n\t\r]', t.skip)
        self.t = t

    def parse_exp(self):
        term = self.parse_term()
        symbol = self.parse_symbol()

        # <Term>
        if not symbol:
            return term

        # <Term> <Symbol> <Exp>
        if symbol == '>':
            self.t.eat(symbol)
            s = self.parse_exp()
            print "{0} {1} {2}".format(term,symbol,s)
            return term > self.parse_exp()
        elif symbol == '<':
            self.t.eat(symbol)
            return term < self.parse_exp()
        elif symbol == '>=':
            self.t.eat(symbol)
            return term >= self.parse_exp()
        elif symbol == '<=':
            self.t.eat(symbol)
            return term <= self.parse_exp()
        elif symbol == '&&':
            self.t.eat(symbol)
            return term and self.parse_exp()
        elif symbol == '||':
            self.t.eat(symbol)
            return term or self.parse_exp()
        elif symbol == '==':
            self.t.eat(symbol)
            return term or self.parse_exp()
        elif symbol == '=~':
            self.t.eat(symbol)
            return term or self.parse_exp()
        else:
            return "Undefined symbol {0}".format(symbol)

    def parse_term(self):
        if self.t.peek() == '(':
            self.t.eat('(')
            exp = self.parse_exp()
            self.t.eat(')')
            return exp
        return self.parse_factor()

    def parse_symbol(self):
        return self.t.next()

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

