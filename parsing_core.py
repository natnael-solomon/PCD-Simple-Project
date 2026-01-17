class Production:
    def __init__(self, left_side, right_side):
        self.left_side = left_side
        self.right_side = right_side
    
    def __str__(self):
        if len(self.right_side) > 0:
            return self.left_side + " -> " + " ".join(self.right_side)
        else:
            return self.left_side + " -> ε"


class Grammar:
    def __init__(self):
        self.production_list = []
        self.start_symbol = ""
        self.terminal_symbols = []
        self.non_terminal_symbols = []
    
    def get_productions_for_symbol(self, symbol):
        matching_productions = []
        for production in self.production_list:
            if production.left_side == symbol:
                matching_productions.append(production)
        return matching_productions


class ParseStep:
    def __init__(self, step_number, step_action, step_description):
        self.number = step_number
        self.action = step_action
        self.description = step_description


def parse_grammar_text(grammar_text):
    if grammar_text.strip() == "":
        raise Exception("Grammar is empty!")
    
    new_grammar = Grammar()
    text_lines = grammar_text.strip().split("\n")
    
    for line_counter, line in enumerate(text_lines):
        line_number = line_counter + 1
        current_line = line.strip()
        
        if current_line == "" or current_line.startswith("#"):
            continue
        
        if "->" not in current_line:
            raise Exception("Line " + str(line_number) + ": Missing '->' in rule")
        
        line_parts = current_line.split("->")
        left_part = line_parts[0].strip()
        right_part = line_parts[1].strip()
        
        if left_part == "":
            raise Exception("Line " + str(line_number) + ": Left side is empty")
        if not left_part[0].isupper():
            raise Exception("Line " + str(line_number) + ": '" + left_part + "' should start with uppercase")
        
        alternative_parts = right_part.split("|")
        
        for alternative in alternative_parts:
            alternative = alternative.strip()
            if alternative == "":
                raise Exception("Line " + str(line_number) + ": Empty alternative")
            
            if alternative == "ε" or alternative == "epsilon":
                symbol_list = []
            else:
                symbol_list = alternative.split()
            
            new_production = Production(left_part, symbol_list)
            new_grammar.production_list.append(new_production)
            
            if left_part not in new_grammar.non_terminal_symbols:
                new_grammar.non_terminal_symbols.append(left_part)
            
            for symbol in symbol_list:
                if symbol[0].isupper():
                    if symbol not in new_grammar.non_terminal_symbols:
                        new_grammar.non_terminal_symbols.append(symbol)
                else:
                    if symbol not in new_grammar.terminal_symbols:
                        new_grammar.terminal_symbols.append(symbol)
    
    if len(new_grammar.production_list) == 0:
        raise Exception("No valid rules found!")
    
    new_grammar.start_symbol = new_grammar.production_list[0].left_side
    return new_grammar


def create_parsing_step(step_number, action_type, description_text):
    return ParseStep(step_number, action_type, description_text)


def add_parsing_step_to_list(parsing_steps, step_counter, action_type, description_text):
    step_counter = step_counter + 1
    new_step = create_parsing_step(step_counter, action_type, description_text)
    parsing_steps.append(new_step)
    return step_counter


def tokenize_input_string(input_string):
    if " " in input_string:
        return input_string.split()
    else:
        return list(input_string)


def is_terminal_symbol(symbol, grammar):
    return symbol in grammar.terminal_symbols


def is_nonterminal_symbol(symbol, grammar):
    return symbol in grammar.non_terminal_symbols


def check_for_epsilon_productions(grammar):
    for production in grammar.production_list:
        if len(production.right_side) == 0:
            raise Exception("Epsilon not allowed: " + str(production))


def check_for_adjacent_nonterminals(grammar):
    for production in grammar.production_list:
        for i in range(len(production.right_side) - 1):
            current_symbol = production.right_side[i]
            next_symbol = production.right_side[i + 1]
            
            if is_nonterminal_symbol(current_symbol, grammar) and is_nonterminal_symbol(next_symbol, grammar):
                raise Exception("Adjacent non-terminals not allowed: " + str(production))


def tokenize_with_grammar_terminals(input_text, grammar):
    token_list = []
    text_position = 0
    
    sorted_terminals = sorted(grammar.terminal_symbols, key=len, reverse=True)
    
    while text_position < len(input_text):
        if input_text[text_position].isspace():
            text_position = text_position + 1
            continue
        
        token_matched = False
        for terminal in sorted_terminals:
            terminal_length = len(terminal)
            
            if text_position + terminal_length <= len(input_text):
                text_slice = input_text[text_position:text_position + terminal_length]
                if text_slice == terminal:
                    token_list.append(terminal)
                    text_position = text_position + terminal_length
                    token_matched = True
                    break
        
        if not token_matched:
            token_list.append(input_text[text_position])
            text_position = text_position + 1
    
    return token_list