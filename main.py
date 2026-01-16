class Production:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def __str__(self):
        if self.right:
            return self.left + " -> " + " ".join(self.right)
        else:
            return self.left + " -> ε"


class Grammar:
    def __init__(self):
        self.productions = []
        self.start_symbol = ""
        self.terminals = set()
        self.non_terminals = set()
    
    def get_productions_for(self, symbol):
        result = []
        for p in self.productions:
            if p.left == symbol:
                result.append(p)
        return result


class ParseStep:
    def __init__(self, number, action, description):
        self.number = number
        self.action = action
        self.description = description


def parse_grammar(text):
    if not text.strip():
        raise Exception("Grammar is empty!")
    
    grammar = Grammar()
    lines = text.strip().split("\n")
    
    for line_num, line in enumerate(lines):
        line = line.strip()
        
        if not line or line.startswith("#"):
            continue
        
        if "->" not in line:
            raise Exception(f"Line {line_num + 1}: Missing '->' in rule")
        
        parts = line.split("->")
        left = parts[0].strip()
        right = parts[1].strip()
        
        if not left:
            raise Exception(f"Line {line_num + 1}: Left side is empty")
        if not left[0].isupper():
            raise Exception(f"Line {line_num + 1}: '{left}' should start with uppercase")
        
        alternatives = right.split("|")
        
        for alt in alternatives:
            alt = alt.strip()
            if not alt:
                raise Exception(f"Line {line_num + 1}: Empty alternative")
            
            if alt == "ε" or alt == "epsilon":
                symbols = []
            else:
                symbols = alt.split()
            
            prod = Production(left, symbols)
            grammar.productions.append(prod)
            
            grammar.non_terminals.add(left)
            for s in symbols:
                if s[0].isupper():
                    grammar.non_terminals.add(s)
                else:
                    grammar.terminals.add(s)
    
    if not grammar.productions:
        raise Exception("No valid rules found!")
    
    grammar.start_symbol = grammar.productions[0].left
    
    return grammar


if __name__ == "__main__":
    from gui import start_app
    start_app()
