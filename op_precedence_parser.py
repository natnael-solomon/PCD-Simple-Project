from main import ParseStep


class OperatorPrecedenceParser:
    def __init__(self, grammar):
        self.grammar = grammar
        self.relations = {}
        self.steps = []
        self.step_num = 0
    
    def build_table(self):
        self.check_grammar()
        leading = self.compute_leading()
        trailing = self.compute_trailing()
        
        for prod in self.grammar.productions:
            right = prod.right
            
            for i in range(len(right)):
                if i + 1 < len(right):
                    a = right[i]
                    b = right[i + 1]
                    
                    if a in self.grammar.terminals and b in self.grammar.terminals:
                        self.set_relation(a, b, "=")
                    
                    if a in self.grammar.terminals and b in self.grammar.non_terminals:
                        for x in leading.get(b, []):
                            self.set_relation(a, x, "<")
                    
                    if a in self.grammar.non_terminals and b in self.grammar.terminals:
                        for x in trailing.get(a, []):
                            self.set_relation(x, b, ">")
                
                if i + 2 < len(right):
                    a = right[i]
                    b = right[i + 1]
                    c = right[i + 2]
                    
                    if a in self.grammar.terminals and b in self.grammar.non_terminals and c in self.grammar.terminals:
                        self.set_relation(a, c, "=")
        
        start = self.grammar.start_symbol
        for x in leading.get(start, []):
            self.set_relation("$", x, "<")
        for x in trailing.get(start, []):
            self.set_relation(x, "$", ">")
    
    def check_grammar(self):
        for prod in self.grammar.productions:
            if not prod.right:
                raise Exception(f"Epsilon not allowed: {prod}")
            
            for i in range(len(prod.right) - 1):
                a = prod.right[i]
                b = prod.right[i + 1]
                if a in self.grammar.non_terminals and b in self.grammar.non_terminals:
                    raise Exception(f"Adjacent non-terminals not allowed: {prod}")
    
    def compute_leading(self):
        leading = {}
        for nt in self.grammar.non_terminals:
            leading[nt] = set()
        
        for prod in self.grammar.productions:
            if prod.right:
                first = prod.right[0]
                if first in self.grammar.terminals:
                    leading[prod.left].add(first)
                if len(prod.right) > 1:
                    if first in self.grammar.non_terminals and prod.right[1] in self.grammar.terminals:
                        leading[prod.left].add(prod.right[1])
        
        changed = True
        while changed:
            changed = False
            for prod in self.grammar.productions:
                if prod.right and prod.right[0] in self.grammar.non_terminals:
                    first_nt = prod.right[0]
                    before = len(leading[prod.left])
                    leading[prod.left].update(leading[first_nt])
                    if len(leading[prod.left]) > before:
                        changed = True
        
        return leading
    
    def compute_trailing(self):
        trailing = {}
        for nt in self.grammar.non_terminals:
            trailing[nt] = set()
        
        for prod in self.grammar.productions:
            if prod.right:
                last = prod.right[-1]
                if last in self.grammar.terminals:
                    trailing[prod.left].add(last)
                if len(prod.right) > 1:
                    if last in self.grammar.non_terminals and prod.right[-2] in self.grammar.terminals:
                        trailing[prod.left].add(prod.right[-2])
        
        changed = True
        while changed:
            changed = False
            for prod in self.grammar.productions:
                if prod.right and prod.right[-1] in self.grammar.non_terminals:
                    last_nt = prod.right[-1]
                    before = len(trailing[prod.left])
                    trailing[prod.left].update(trailing[last_nt])
                    if len(trailing[prod.left]) > before:
                        changed = True
        
        return trailing
    
    def set_relation(self, a, b, rel):
        key = (a, b)
        if key in self.relations and self.relations[key] != rel:
            raise Exception(f"Conflict: {a} and {b} have both '{self.relations[key]}' and '{rel}'")
        self.relations[key] = rel
    
    def get_relation(self, a, b):
        return self.relations.get((a, b))
    
    def parse(self, input_text):
        self.build_table()
        self.steps = []
        self.step_num = 0
        
        if " " in input_text:
            tokens = input_text.split()
        else:
            tokens = self.tokenize(input_text)
        
        tokens.append("$")
        stack = ["$"]
        pos = 0
        
        self.add_step("shift", f"Start: stack={stack}, input={tokens}")
        
        while True:
            if len(stack) == 2 and stack[0] == "$" and stack[1] == self.grammar.start_symbol:
                if pos >= len(tokens) - 1:
                    self.add_step("accept", "Input accepted!")
                    return self.steps
            
            top = self.get_top_terminal(stack)
            current = tokens[pos] if pos < len(tokens) else "$"
            rel = self.get_relation(top, current)
            
            if rel is None and len(stack) == 2 and stack[0] == "$" and stack[1] in self.grammar.non_terminals:
                if pos >= len(tokens) - 1:
                    if self.try_unit_reductions(stack):
                        continue
            
            if rel is None:
                self.add_step("reject", f"No relation between '{top}' and '{current}'")
                return self.steps
            
            if rel == "<" or rel == "=":
                stack.append(current)
                self.add_step("shift", f"Shift '{current}' ({top} {rel} {current}), stack={stack}")
                pos += 1
            
            elif rel == ">":
                handle_start = self.find_handle_start(stack)
                
                if handle_start is None:
                    self.add_step("reject", "Cannot find handle start (no '<' found)")
                    return self.steps
                
                handle = stack[handle_start:]
                prod = self.find_matching_production(handle)
                
                if prod is None:
                    self.add_step("reject", f"No production matches handle: {handle}")
                    return self.steps
                
                for _ in range(len(handle)):
                    stack.pop()
                stack.append(prod.left)
                
                self.add_step("reduce", f"Reduce {' '.join(handle)} -> {prod.left}, stack={stack}")
            
            if self.step_num > 500:
                self.add_step("reject", "Too many steps - possible infinite loop")
                return self.steps
        
        return self.steps
    
    def try_unit_reductions(self, stack):
        current = stack[1]
        for prod in self.grammar.productions:
            if len(prod.right) == 1 and prod.right[0] == current:
                stack[1] = prod.left
                self.add_step("reduce", f"Reduce {current} -> {prod.left} (unit), stack={stack}")
                return True
        return False
    
    def get_top_terminal(self, stack):
        for i in range(len(stack) - 1, -1, -1):
            if stack[i] in self.grammar.terminals or stack[i] == "$":
                return stack[i]
        return "$"
    
    def find_handle_start(self, stack):
        top_term_pos = None
        for i in range(len(stack) - 1, -1, -1):
            if stack[i] in self.grammar.terminals or stack[i] == "$":
                top_term_pos = i
                break
        
        if top_term_pos is None:
            return None
        
        prev_term_pos = top_term_pos
        for i in range(top_term_pos - 1, -1, -1):
            if stack[i] in self.grammar.terminals or stack[i] == "$":
                rel = self.get_relation(stack[i], stack[prev_term_pos])
                if rel == "<":
                    return i + 1
                prev_term_pos = i
        
        return 1
    
    def find_matching_production(self, handle):
        for prod in self.grammar.productions:
            if self.matches(handle, prod):
                return prod
        return None
    
    def matches(self, segment, prod):
        if len(segment) != len(prod.right):
            return False
        
        for i in range(len(segment)):
            stack_sym = segment[i]
            prod_sym = prod.right[i]
            
            if prod_sym in self.grammar.terminals:
                if stack_sym != prod_sym:
                    return False
            else:
                if stack_sym not in self.grammar.non_terminals:
                    return False
        
        return True
    
    def tokenize(self, text):
        tokens = []
        pos = 0
        terminals = sorted(self.grammar.terminals, key=len, reverse=True)
        
        while pos < len(text):
            if text[pos].isspace():
                pos += 1
                continue
            
            matched = False
            for t in terminals:
                if text[pos:pos+len(t)] == t:
                    tokens.append(t)
                    pos += len(t)
                    matched = True
                    break
            
            if not matched:
                tokens.append(text[pos])
                pos += 1
        
        return tokens
    
    def add_step(self, action, description):
        self.step_num += 1
        step = ParseStep(self.step_num, action, description)
        self.steps.append(step)
