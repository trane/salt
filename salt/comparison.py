'''
Comparison Engine for -X
'''
class Comparitor(object):
    class Rule(Comparitor):
        '''
        Rules are used by the Matcher to determine if prefix matches
        '''
        def __init__(self, regex, action):
            self.regex = re.compile(regex)
            self.action = action

        def prefix(self, inpt):
            match = re.match(self.regex, inpt)
            if match:
                return match.group(1)
            else:
                return False

    class Matcher(Comparitor):
        def __init__(self, rules = []):
            self.rules = rules

        def add_rule(self, regex, action):
            '''
            Add a rule to the matcher
            '''
            self.rules.append(new Rule(regex, action))

        def prefixes(self, inpt):
            '''
            Get the longest matching prefix for each rule
            '''
            prefixen = []
            for rule in range(len(self.rules)):
                prefixen.insert(0, {'rule': rule, 'prefix': rule.prefix(inpt)})
            return prefixen

        def winner(self, inpt):
            '''
            Find winning rule for the provided input
            '''
            prefixen = self.prefixes(inpt)

            maxP = 0
            winner = None

            for prefix in range(len(prefixen)):
                if prefix and len(prefix['prefix']) >= maxP:
                    maxP = len(prefix['prefix'])
                    winner = prefix

            return winner

    class Tokenizer(Comparitor):
        '''
        This is a Tokenizer without need for Tokens, just provides the basic
        lexical needs of skip, peek, next and eat.
        '''
        def __init__(self, inpt = ''):
            self.inpt = inpt
            self.matcher = new Matcher()
            self.next_token = None
            self.next_text = None

        def skip(self, matched):
            '''
            Skips current character
            '''
            self.inpt = self.inpt[:len(matched):]
            self.next_token = None
            self.next_text = None

        def token(self, matched):
            inpt = self.inpt[:len(matched):]
            next_token = matched
            next_text = matched

        def peek(self):
            '''
            Returns next char without consuming it
            '''
            if self.inpt is '':
                return None
            else:
                return inpt[:1:]

        def next(self):
            '''
            Returns and consumes next char
            '''
            char = self.peek()
            if char:
                self.inpt = self.inpt[1::]
            return char

        def eat(self, char):
            '''
            Consumes char without returning it, throwing an error if incorrect
            syntax
            '''
            next_char = self.next()
            if next_char is not char:
                except ValueError:
                    return "Parse error: expected {0}, got {1}".format(char,
                            next_char)



    class Parser(Comparitor):
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
        <Grain>     ::= grains[<String>]
        <Module>    ::= salt[<String>.<String>]
        <Pillar>    ::= pillar[<String>]
        <Primitive> ::= Int
                     |  String
        '''
        def __init__(self, tokenizer):
            self.tokenizer = new Tokenizer()

        def parse_exp(self):
            term = self.parse_term()

        def parse_term(self):



