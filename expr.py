import math

class Expression:
    OPERATORS = {
        '^': 3,
        '*': 2,
        '/': 2,
        '+': 1,
        '-': 1
    }

    FUNCTIONS = {
        'sqrt': math.sqrt,
        'sin': lambda x: math.sin(math.radians(x)),
        'cos': lambda x: math.cos(math.radians(x)),
        'tan': lambda x: math.tan(math.radians(x)),
        'cot': lambda x: 1 / math.tan(math.radians(x)),
        'deg': math.degrees,
        'rad': math.radians,
        'fact': lambda x: math.factorial(int(x))
    }

    CONSTANTS = {
        'pi': math.pi,
        'e': math.e,
        'tau': math.tau,
        'ans': 0
    }

    class TYPES:
        Number = 'Number'
        Parenthesis = 'Parenthesis'
        Function = 'Function'
        Operator = 'Operator'
        Constant = 'Constant'

    class RawToken:
        def __init__(self, value, type) -> None:
            self.value = value
            self.type = type
        def getToken(self):
            pass

    class NumberToken(RawToken):
        def __init__(self, value) -> None:
            super().__init__(value, Expression.TYPES.Number)

        def getToken(self):
            return {'Type': Expression.TYPES.Number, 'Value': self.value}

    class OperatorToken(RawToken):
        def __init__(self, value) -> None:
            super().__init__(value, Expression.TYPES.Operator)
            
        def getToken(self):
            return {'Type': Expression.TYPES.Operator, 'Value': self.value, 'Priority': Expression.OPERATORS[self.value]}

    class ParenthesisToken(RawToken):
        def __init__(self, value) -> None:
            super().__init__(value, Expression.TYPES.Parenthesis)
        
        def getToken(self):
            return {'Type': Expression.TYPES.Parenthesis, 'Value': self.value}

    class FunctionToken(RawToken):
        def __init__(self, value) -> None:
            super().__init__(value, Expression.TYPES.Function)

            if self.value not in Expression.FUNCTIONS and self.value not in Expression.CONSTANTS:
                raise Exception(f'Function \'{self.value}\' doesn\'t exists!')

        def getToken(self):
            return {'Type': Expression.TYPES.Function, 'Value': Expression.FUNCTIONS[self.value]}

    class ConstantToken(RawToken):
        def __init__(self, value) -> None:
            super().__init__(value, Expression.TYPES.Constant)

            if self.value not in Expression.CONSTANTS:
                raise Exception(f'Constant \'{self.value}\' doesn\'t exists!') 

        def getToken(self):
            return {'Type': Expression.TYPES.Constant, 'Value': Expression.CONSTANTS[self.value]}

    def __init__(self, txt: str, addMissingBrackets = True):
        if addMissingBrackets:
            txt = txt.lower()
            if len(txt) == 0:
                raise Exception('The expression is empty!')
            count = 0
            for t in txt:
                if t == '(':
                    count += 1
                elif t == ')':
                    count -= 1
            if count < 0:
                raise Exception('Incorrect amount of parentheses!')
            elif count > 0:
                for i in range(count):
                    txt += ')'
                    
        self.txt = txt
        self.pIndex = -1

        txt += ' '
        tokens = []
        prev = txt[0]
        currentType = self.getType(txt[0])
        lastParenthesis = 0

        for i, v in enumerate(txt[1:], 1):
            if i <= lastParenthesis:
                continue
            if v == ')':
                if currentType != None:
                    tokens.append(self.autoCreateToken(currentType, prev))

                self.tokens = tokens
                self.pIndex = i
                return
            if self.getType(v) != currentType or currentType == Expression.TYPES.Parenthesis:
                if currentType == Expression.TYPES.Parenthesis:
                    par = Expression(txt[i:-1], False)
                    p = par.tokens
                    l = par.pIndex
                    lastParenthesis = l+i
                    tokens.append(self.autoCreateToken(currentType, p))
                    prev = ''
                    currentType = None
                    continue

                if currentType != None:
                    tokens.append(self.autoCreateToken(currentType, prev))

                prev = v
                currentType = self.getType(v)
                continue

            if currentType == None and prev == ' ':
                continue

            if currentType == Expression.TYPES.Operator:
                tokens.append(self.autoCreateToken(currentType, prev))
                continue
            
            prev += v
            continue

        self.tokens = tokens
        self.operatorCheck()

    @staticmethod
    def getType(s: str):
        if s == ' ':
            return None
        if s in Expression.OPERATORS:
            return Expression.TYPES.Operator
        if s.isdigit() or s == '.':
            return Expression.TYPES.Number
        if s == '(':
            return Expression.TYPES.Parenthesis
        return Expression.TYPES.Function

    def autoCreateToken(self, type, value):
        if type == Expression.TYPES.Number:
            return Expression.NumberToken(float(value))
        elif type == Expression.TYPES.Operator:
            return Expression.OperatorToken(value)
        elif type == Expression.TYPES.Parenthesis:
            return Expression.ParenthesisToken(value)
        elif type == Expression.TYPES.Function:
            return Expression.FunctionToken(value)
        elif type == Expression.TYPES.Constant:
            return Expression.ConstantToken(value)

    def __operatorCheck(self, raw : list[RawToken]):
        tokens = list(raw)
        i = 0

        while i < len(tokens):
            if tokens[i].type == Expression.TYPES.Parenthesis:
                if i+1 < len(tokens) and tokens[i+1].type == Expression.TYPES.Parenthesis:
                    tokens.insert(i+1, Expression.OperatorToken('*'))

                tokens[i].value = self.__operatorCheck(tokens[i].value)

            if tokens[i].type == Expression.TYPES.Function and tokens[i].value in Expression.CONSTANTS:
                tokens[i] = Expression.ConstantToken(tokens[i].value)

            if i+1 < len(tokens) and tokens[i].type in [Expression.TYPES.Number, Expression.TYPES.Constant] and tokens[i+1].type in [Expression.TYPES.Parenthesis, Expression.TYPES.Function, Expression.TYPES.Constant]:
                tokens.insert(i+1, Expression.OperatorToken('*'))
            i += 1

        if tokens[0].type == Expression.TYPES.Operator and tokens[0].value == '-':
            tokens.insert(0, Expression.NumberToken(0))

        return tokens

    def operatorCheck(self):
        self.tokens = self.__operatorCheck(self.tokens)

    def __calculate(self, tok : list[RawToken]):
        operators : list[list[Expression.OperatorToken]] = [[] for _ in range(3)]
        functions : list[Expression.FunctionToken] = []
        tokens = list(tok)

        if len(tokens) == 1:
            if tokens[0].type == Expression.TYPES.Number:
                return tokens[0].value
            elif tokens[0].type == Expression.TYPES.Parenthesis:
                return self.__calculate(tokens[0].value)
            elif tokens[0].type == Expression.TYPES.Constant:
                return Expression.CONSTANTS[tokens[0].value]
            else:
                raise Exception('Invalid expression!')

        for i in range(len(tokens)):
            if tokens[i].type == Expression.TYPES.Operator:
                operators[3 - Expression.OPERATORS[tokens[i].value]].append(tokens[i])
            elif tokens[i].type == Expression.TYPES.Function:
                functions.append(tokens[i])

        if operators == [[],[],[]] and functions == []:
            raise Exception('Invalid expression!')

        for f in functions:
            index = tokens.index(f)

            if index+1 >= len(tokens):
                raise Exception(f'Function \'{f.value}\' doesn\'t have body!')

            right = tokens[index+1]
            if right.type != Expression.TYPES.Parenthesis:
                raise Exception(f'The argument of function \'{f.value}\' must be enclosed in parentheses!')

            res = self.__calculate(right.value)
            res = Expression.FUNCTIONS[f.value](res)
            tokens.pop(index+1)
            tokens[index] = Expression.NumberToken(res)

        for op in operators:
            for o in op:
                index = tokens.index(o)

                if index-1 == -1 or index+1 >= len(tokens):
                    raise Exception('Every operator must have an expression on both sides!')

                left = tokens[index-1]
                right = tokens[index+1]
                l = r = 0
                
                if left.type == Expression.TYPES.Number:
                    l = left.value
                elif left.type == Expression.TYPES.Parenthesis:
                    l = self.__calculate(left.value)
                elif left.type == Expression.TYPES.Constant:
                    l = Expression.CONSTANTS[left.value]
                else:
                    raise Exception('Invalid expression!')

                if right.type == Expression.TYPES.Number:
                    r = right.value
                elif right.type == Expression.TYPES.Parenthesis:
                    r = self.__calculate(right.value)
                elif right.type == Expression.TYPES.Constant:
                    r = Expression.CONSTANTS[right.value]
                else:
                    raise Exception('Invalid expression!')


                res = 0
                if o.value == '^':
                    res = l**r
                elif o.value == '*':
                    res = l*r
                elif o.value == '/':
                    res = l/r
                elif o.value == '+':
                    res = l+r
                elif o.value == '-':
                    res = l-r

                tokens.pop(index+1)
                tokens[index] = Expression.NumberToken(res)
                tokens.pop(index-1)
        if tokens[0].type != Expression.TYPES.Number:
            raise Exception('Invalid expression!')
        return round(tokens[0].value, 16)

    def calculate(self):
        res = self.__calculate(self.tokens)
        Expression.CONSTANTS['ans'] = res
        return res
