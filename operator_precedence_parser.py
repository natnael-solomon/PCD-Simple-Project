from parsing_core import create_parsing_step, add_parsing_step_to_list, tokenize_with_grammar_terminals, is_terminal_symbol, is_nonterminal_symbol, check_for_epsilon_productions, check_for_adjacent_nonterminals
from precedence_table import build_precedence_table


class OperatorPrecedenceParser:
    def __init__(self, input_grammar):
        self.grammar = input_grammar
        self.precedence_relations = {}
        self.parsing_steps = []
        self.step_counter = 0
        self.maximum_steps = 100
    
    def parse_input(self, input_string):
        try:
            self.build_precedence_table()
        except Exception as e:
            error_message = str(e)
            if "Conflict" in error_message:
                self.parsing_steps = []
                self.step_counter = 0
                self.add_parsing_step("reject", "PRECEDENCE CONFLICT ERROR: Grammar has precedence conflicts - parser cannot determine shift/reduce actions")
                return self.parsing_steps
            else:
                raise e
        

        self.parsing_steps = []
        self.step_counter = 0
        
        input_tokens = self.prepare_input_tokens(input_string)
        parsing_stack = ["$"]
        input_position = 0
        
        start_message = "Start: stack=" + str(parsing_stack) + ", input=" + str(input_tokens)
        self.add_parsing_step("shift", start_message)
        
        while True:
            if self.check_for_acceptance(parsing_stack, input_position, input_tokens):
                return self.parsing_steps
            
            if self.try_unit_reduction_if_needed(parsing_stack, input_position, input_tokens):
                continue
            
            parsing_action = self.determine_parsing_action(parsing_stack, input_tokens, input_position)
            
            if parsing_action == "error":
                return self.parsing_steps
            elif parsing_action == "shift":
                input_position = self.perform_shift_action(parsing_stack, input_tokens, input_position)
            elif parsing_action == "reduce":
                self.perform_reduce_action(parsing_stack, input_tokens, input_position)
            
            if self.step_counter > self.maximum_steps:
                self.add_parsing_step("reject", "PARSING STEPS ERROR: Exceeded parsing steps - likely caused by reduce-reduce conflicts or malformed precedence table")
                return self.parsing_steps
        
        return self.parsing_steps
    
    def detect_infinite_loop_patterns(self):
        terminal_symbols = self.grammar.terminal_symbols + ["$"]
        for symbol_a in terminal_symbols:
            for symbol_b in terminal_symbols:
                if symbol_a != symbol_b:
                    relation_ab = self.get_precedence_relation(symbol_a, symbol_b)
                    relation_ba = self.get_precedence_relation(symbol_b, symbol_a)
                    
                    if relation_ab == ">" and relation_ba == ">":
                        return True
        
        return False
    
    def build_precedence_table(self):
        check_for_epsilon_productions(self.grammar)
        check_for_adjacent_nonterminals(self.grammar)
        
        self.precedence_relations = build_precedence_table(self.grammar)
    
    def prepare_input_tokens(self, input_string):
        if " " in input_string:
            input_tokens = input_string.split()
        else:
            input_tokens = tokenize_with_grammar_terminals(input_string, self.grammar)
        
        input_tokens.append("$")
        return input_tokens
    
    def check_for_acceptance(self, parsing_stack, input_position, input_tokens):
        stack_length = len(parsing_stack)
        if stack_length == 2 and parsing_stack[0] == "$" and parsing_stack[1] == self.grammar.start_symbol:
            if input_position >= len(input_tokens) - 1:
                self.add_parsing_step("accept", "Input accepted!")
                return True
        return False
    
    def try_unit_reduction_if_needed(self, parsing_stack, input_position, input_tokens):
        stack_length = len(parsing_stack)
        if stack_length == 2 and parsing_stack[0] == "$":
            stack_top = parsing_stack[1]
            if is_nonterminal_symbol(stack_top, self.grammar):
                if input_position >= len(input_tokens) - 1:
                    return self.try_unit_reduction(parsing_stack, input_tokens, input_position)
        return False
    
    def determine_parsing_action(self, parsing_stack, input_tokens, input_position):
        top_terminal = self.get_top_terminal_from_stack(parsing_stack)
        if input_position < len(input_tokens):
            current_input = input_tokens[input_position]
        else:
            current_input = "$"
        
        precedence_relation = self.get_precedence_relation(top_terminal, current_input)
        
        if precedence_relation is None:
            error_message = "No relation between '" + top_terminal + "' and '" + current_input + "'"
            self.add_parsing_step("reject", error_message)
            return "error"
        elif precedence_relation == "<" or precedence_relation == "=":
            return "shift"
        elif precedence_relation == ">":
            return "reduce"
    
    def perform_shift_action(self, parsing_stack, input_tokens, input_position):
        current_input = input_tokens[input_position]
        top_terminal = self.get_top_terminal_from_stack(parsing_stack)
        precedence_relation = self.get_precedence_relation(top_terminal, current_input)
        
        parsing_stack.append(current_input)
        
        remaining_input = input_tokens[input_position + 1:]
        
        step_message = "Shift '" + current_input + "' (" + top_terminal + " " + precedence_relation + " " + current_input + "), stack=" + str(parsing_stack) + ", input=" + str(remaining_input)
        self.add_parsing_step("shift", step_message)
        
        return input_position + 1
    
    def perform_reduce_action(self, parsing_stack, input_tokens, input_position):
        handle_start_position = self.find_handle_start_position(parsing_stack)
        
        if handle_start_position is None:
            self.add_parsing_step("reject", "Cannot find handle start (no '<' found)")
            return
        
        handle_symbols = self.extract_handle_from_stack(parsing_stack, handle_start_position)
        matching_production = self.find_production_for_handle(handle_symbols)
        
        if matching_production is None:
            error_message = "No production matches handle: " + str(handle_symbols)
            self.add_parsing_step("reject", error_message)
            return
        
        self.replace_handle_with_nonterminal(parsing_stack, handle_symbols, matching_production, input_tokens, input_position)
    
    def extract_handle_from_stack(self, parsing_stack, handle_start_position):
        return parsing_stack[handle_start_position:]
    
    def replace_handle_with_nonterminal(self, parsing_stack, handle_symbols, matching_production, input_tokens, input_position):
        for _ in range(len(handle_symbols)):
            parsing_stack.pop()
        
        parsing_stack.append(matching_production.left_side)
        
        remaining_input = input_tokens[input_position:]
        
        handle_string = " ".join(handle_symbols)
        step_message = "Reduce " + handle_string + " -> " + matching_production.left_side + ", stack=" + str(parsing_stack) + ", input=" + str(remaining_input)
        self.add_parsing_step("reduce", step_message)
    
    def try_unit_reduction(self, parsing_stack, input_tokens, input_position):
        current_symbol = parsing_stack[1]
        
        remaining_input = input_tokens[input_position:]
        
        for production in self.grammar.production_list:
            if len(production.right_side) == 1 and production.right_side[0] == current_symbol:
                parsing_stack[1] = production.left_side
                step_message = "Reduce " + current_symbol + " -> " + production.left_side + " (unit), stack=" + str(parsing_stack) + ", input=" + str(remaining_input)
                self.add_parsing_step("reduce", step_message)
                return True
        
        return False
    
    def _find_terminal_in_stack(self, parsing_stack, start_index=None):
        if start_index is None:
            start_index = len(parsing_stack) - 1
        
        stack_index = start_index
        while stack_index >= 0:
            current_symbol = parsing_stack[stack_index]
            if is_terminal_symbol(current_symbol, self.grammar) or current_symbol == "$":
                return stack_index
            stack_index = stack_index - 1
        return None
    
    def get_top_terminal_from_stack(self, parsing_stack):
        terminal_index = self._find_terminal_in_stack(parsing_stack)
        if terminal_index is not None:
            return parsing_stack[terminal_index]
        return "$"
    
    def find_handle_start_position(self, parsing_stack):
        top_terminal_position = self._find_terminal_in_stack(parsing_stack)
        
        if top_terminal_position is None:
            return None
        
        previous_terminal_position = top_terminal_position
        check_index = top_terminal_position - 1
        while check_index >= 0:
            current_symbol = parsing_stack[check_index]
            if is_terminal_symbol(current_symbol, self.grammar) or current_symbol == "$":
                relation = self.get_precedence_relation(current_symbol, parsing_stack[previous_terminal_position])
                if relation == "<":
                    return check_index + 1
                previous_terminal_position = check_index
            check_index = check_index - 1
        
        return 1
    
    def find_production_for_handle(self, handle_symbols):
        for production in self.grammar.production_list:
            if self.does_handle_match_production(handle_symbols, production):
                return production
        return None
    
    def does_handle_match_production(self, handle_symbols, production):
        if len(handle_symbols) != len(production.right_side):
            return False
        
        for i in range(len(handle_symbols)):
            handle_symbol = handle_symbols[i]
            production_symbol = production.right_side[i]
            
            if is_terminal_symbol(production_symbol, self.grammar):
                if handle_symbol != production_symbol:
                    return False
            else:
                if not is_nonterminal_symbol(handle_symbol, self.grammar):
                    return False
        
        return True
    
    def get_precedence_relation(self, symbol_a, symbol_b):
        relation_key = (symbol_a, symbol_b)
        if relation_key in self.precedence_relations:
            return self.precedence_relations[relation_key]
        else:
            return None
    
    def add_parsing_step(self, action_type, description_text):
        self.step_counter = add_parsing_step_to_list(self.parsing_steps, self.step_counter, action_type, description_text)