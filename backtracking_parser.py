from parsing_core import create_parsing_step, add_parsing_step_to_list, tokenize_input_string, is_terminal_symbol, is_nonterminal_symbol


class BacktrackingParser:
    def __init__(self, input_grammar):
        self.grammar = input_grammar
        self.input_tokens = []
        self.parsing_steps = []
        self.step_counter = 0
        self.maximum_steps = 100
        self.maximum_depth = 50
        self.is_too_deep = False
        self.call_stack = []
    
    def parse_input(self, input_string):
        self.input_tokens = tokenize_input_string(input_string)
        self.parsing_steps = []
        self.step_counter = 0
        self.is_too_deep = False
        self.call_stack = []
        
        if self.detect_left_recursion():
            self.add_parsing_step("reject", "LEFT RECURSION ERROR: Grammar contains left recursion - backtracking will loop forever trying the same productions")
            return self.parsing_steps
        
        parsing_result = self.match_grammar_symbol(self.grammar.start_symbol, 0, 0)
        
        if parsing_result is not None and parsing_result == len(self.input_tokens):
            self.add_parsing_step("accept", "Input accepted!")
        elif self.step_counter >= self.maximum_steps or self.is_too_deep:
            self.add_parsing_step("reject", "RECURSION DEPTH ERROR: Exceeded step limit - likely caused by left recursion or deep grammar nesting")
        else:
            self.add_parsing_step("reject", "Input rejected - no valid parse found")
        
        return self.parsing_steps
    
    def detect_left_recursion(self):
        for production in self.grammar.production_list:
            if len(production.right_side) > 0:
                first_symbol = production.right_side[0]
                if first_symbol == production.left_side:
                    return True
                
                visited = set()
                if self.has_left_recursive_cycle(production.left_side, first_symbol, visited):
                    return True
        return False
    
    def has_left_recursive_cycle(self, start_symbol, current_symbol, visited):
        if current_symbol == start_symbol:
            return True
        if current_symbol in visited or not is_nonterminal_symbol(current_symbol, self.grammar):
            return False
        
        visited.add(current_symbol)
        for production in self.grammar.get_productions_for_symbol(current_symbol):
            if len(production.right_side) > 0:
                first_symbol = production.right_side[0]
                if self.has_left_recursive_cycle(start_symbol, first_symbol, visited):
                    return True
        visited.remove(current_symbol)
        return False
    
    def match_grammar_symbol(self, symbol, position, recursion_depth):
        if self.step_counter >= self.maximum_steps:
            return None
        
        if recursion_depth > self.maximum_depth:
            self.is_too_deep = True
            return None
        
        if is_terminal_symbol(symbol, self.grammar):
            return self.match_terminal_symbol(symbol, position)
        else:
            return self.try_all_productions(symbol, position, recursion_depth)
    
    def match_terminal_symbol(self, terminal, position):
        if position < len(self.input_tokens) and self.input_tokens[position] == terminal:
            step_description = "Matched '" + terminal + "' at position " + str(position)
            self.add_parsing_step("match", step_description)
            return position + 1
        else:
            if position < len(self.input_tokens):
                got_token = self.input_tokens[position]
            else:
                got_token = "end"
            step_description = "Failed to match '" + terminal + "' at position " + str(position) + " (got '" + got_token + "')"
            self.add_parsing_step("fail", step_description)
            return None
    
    def try_all_productions(self, symbol, position, recursion_depth):
        matching_productions = self.grammar.get_productions_for_symbol(symbol)
        
        for i, production in enumerate(matching_productions):
            step_description = "Trying: " + str(production)
            self.add_parsing_step("try", step_description)
            
            production_result = self.try_single_production(production, position, recursion_depth + 1)
            
            if production_result is not None:
                return production_result
            
            if self.is_too_deep:
                return None
            
            if i < len(matching_productions) - 1:
                step_description = "Backtracking from " + str(production)
                self.add_parsing_step("backtrack", step_description)
        
        return None
    
    def try_single_production(self, production, position, recursion_depth):
        current_position = position
        
        if len(production.right_side) == 0:
            step_description = "Matched epsilon: " + str(production)
            self.add_parsing_step("match", step_description)
            return position
        
        for symbol in production.right_side:
            symbol_result = self.match_grammar_symbol(symbol, current_position, recursion_depth)
            if symbol_result is None:
                return None
            current_position = symbol_result
        
        return current_position
    
    def add_parsing_step(self, action_type, description_text):
        self.step_counter = add_parsing_step_to_list(self.parsing_steps, self.step_counter, action_type, description_text)