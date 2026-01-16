from main import ParseStep


class BacktrackingParser:
    def __init__(self, grammar):
        self.grammar = grammar
        self.tokens = []
        self.pos = 0
        self.steps = []
        self.step_num = 0
        self.max_steps = 500
        self.max_depth = 200
        self.too_deep = False
    
    def parse(self, input_text):
        if " " in input_text:
            self.tokens = input_text.split()
        else:
            self.tokens = list(input_text)
        
        self.pos = 0
        self.steps = []
        self.step_num = 0
        self.too_deep = False
        
        result = self.match_symbol(self.grammar.start_symbol, 0, 0)
        
        if result is not None and result == len(self.tokens):
            self.add_step("accept", "Input accepted!")
        elif self.step_num >= self.max_steps or self.too_deep:
            self.add_step("reject", "Too many steps - possible infinite loop (left-recursive grammar?)")
        else:
            self.add_step("reject", "Input rejected - no valid parse found")
        
        return self.steps
    
    def match_symbol(self, symbol, pos, depth):
        if self.step_num >= self.max_steps:
            return None
        
        if depth > self.max_depth:
            self.too_deep = True
            return None
        
        if symbol in self.grammar.terminals:
            return self.match_terminal(symbol, pos)
        else:
            return self.try_productions(symbol, pos, depth)
    
    def match_terminal(self, terminal, pos):
        if pos < len(self.tokens) and self.tokens[pos] == terminal:
            self.add_step("match", f"Matched '{terminal}' at position {pos}")
            return pos + 1
        else:
            got = self.tokens[pos] if pos < len(self.tokens) else "end"
            self.add_step("fail", f"Failed to match '{terminal}' at position {pos} (got '{got}')")
            return None
    
    def try_productions(self, symbol, pos, depth):
        productions = self.grammar.get_productions_for(symbol)
        
        for i, prod in enumerate(productions):
            self.add_step("try", f"Trying: {prod}")
            
            result = self.try_production(prod, pos, depth + 1)
            
            if result is not None:
                return result
            
            if self.too_deep:
                return None
            
            if i < len(productions) - 1:
                self.add_step("backtrack", f"Backtracking from {prod}")
        
        return None
    
    def try_production(self, prod, pos, depth):
        current_pos = pos
        
        if not prod.right:
            self.add_step("match", f"Matched epsilon: {prod}")
            return pos
        
        for symbol in prod.right:
            result = self.match_symbol(symbol, current_pos, depth)
            if result is None:
                return None
            current_pos = result
        
        return current_pos
    
    def add_step(self, action, description):
        self.step_num += 1
        step = ParseStep(self.step_num, action, description)
        self.steps.append(step)
