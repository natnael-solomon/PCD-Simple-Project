from parsing_core import is_terminal_symbol, is_nonterminal_symbol


def build_precedence_table(grammar):
    precedence_relations = {}
    
    leading_sets = compute_leading_sets(grammar)
    trailing_sets = compute_trailing_sets(grammar)
    
    build_relations_from_productions(grammar, leading_sets, trailing_sets, precedence_relations)
    add_start_end_relations(grammar, leading_sets, trailing_sets, precedence_relations)
    
    return precedence_relations


def build_relations_from_productions(grammar, leading_sets, trailing_sets, precedence_relations):
    for production in grammar.production_list:
        right_side_symbols = production.right_side
        
        for symbol_index in range(len(right_side_symbols)):
            process_adjacent_symbols(grammar, right_side_symbols, symbol_index, leading_sets, trailing_sets, precedence_relations)
            process_triple_symbols(grammar, right_side_symbols, symbol_index, precedence_relations)


def process_adjacent_symbols(grammar, symbols, index, leading_sets, trailing_sets, precedence_relations):
    if index + 1 < len(symbols):
        first_symbol = symbols[index]
        second_symbol = symbols[index + 1]
        
        first_is_terminal = is_terminal_symbol(first_symbol, grammar)
        second_is_terminal = is_terminal_symbol(second_symbol, grammar)
        second_is_nonterminal = is_nonterminal_symbol(second_symbol, grammar)
        first_is_nonterminal = is_nonterminal_symbol(first_symbol, grammar)
        
        if first_is_terminal and second_is_terminal:
            set_precedence_relation(first_symbol, second_symbol, "=", precedence_relations)
        
        if first_is_terminal and second_is_nonterminal:
            if second_symbol in leading_sets:
                for terminal in leading_sets[second_symbol]:
                    set_precedence_relation(first_symbol, terminal, "<", precedence_relations)
        
        if first_is_nonterminal and second_is_terminal:
            if first_symbol in trailing_sets:
                for terminal in trailing_sets[first_symbol]:
                    set_precedence_relation(terminal, second_symbol, ">", precedence_relations)


def process_triple_symbols(grammar, symbols, index, precedence_relations):
    if index + 2 < len(symbols):
        first_symbol = symbols[index]
        middle_symbol = symbols[index + 1]
        third_symbol = symbols[index + 2]
        
        first_is_terminal = is_terminal_symbol(first_symbol, grammar)
        middle_is_nonterminal = is_nonterminal_symbol(middle_symbol, grammar)
        third_is_terminal = is_terminal_symbol(third_symbol, grammar)
        
        if first_is_terminal and middle_is_nonterminal and third_is_terminal:
            set_precedence_relation(first_symbol, third_symbol, "=", precedence_relations)


def add_start_end_relations(grammar, leading_sets, trailing_sets, precedence_relations):
    start_symbol = grammar.start_symbol
    
    if start_symbol in leading_sets:
        for terminal in leading_sets[start_symbol]:
            set_precedence_relation("$", terminal, "<", precedence_relations)
    
    if start_symbol in trailing_sets:
        for terminal in trailing_sets[start_symbol]:
            set_precedence_relation(terminal, "$", ">", precedence_relations)


def compute_leading_sets(grammar):
    leading_sets = {}
    
    for nonterminal in grammar.non_terminal_symbols:
        leading_sets[nonterminal] = []
    
    add_direct_leading_terminals(grammar, leading_sets)
    propagate_leading_sets(grammar, leading_sets)
    
    return leading_sets


def add_direct_leading_terminals(grammar, leading_sets):
    for production in grammar.production_list:
        if len(production.right_side) > 0:
            first_symbol = production.right_side[0]
            
            if is_terminal_symbol(first_symbol, grammar):
                if first_symbol not in leading_sets[production.left_side]:
                    leading_sets[production.left_side].append(first_symbol)
            
            if len(production.right_side) > 1:
                first_is_nonterminal = is_nonterminal_symbol(first_symbol, grammar)
                second_is_terminal = is_terminal_symbol(production.right_side[1], grammar)
                if first_is_nonterminal and second_is_terminal:
                    second_symbol = production.right_side[1]
                    if second_symbol not in leading_sets[production.left_side]:
                        leading_sets[production.left_side].append(second_symbol)


def propagate_leading_sets(grammar, leading_sets):
    something_changed = True
    while something_changed:
        something_changed = False
        
        for production in grammar.production_list:
            if len(production.right_side) > 0:
                first_symbol = production.right_side[0]
                if is_nonterminal_symbol(first_symbol, grammar):
                    old_count = len(leading_sets[production.left_side])
                    
                    for terminal in leading_sets[first_symbol]:
                        if terminal not in leading_sets[production.left_side]:
                            leading_sets[production.left_side].append(terminal)
                    
                    new_count = len(leading_sets[production.left_side])
                    if new_count > old_count:
                        something_changed = True


def compute_trailing_sets(grammar):
    trailing_sets = {}
    
    for nonterminal in grammar.non_terminal_symbols:
        trailing_sets[nonterminal] = []
    
    add_direct_trailing_terminals(grammar, trailing_sets)
    propagate_trailing_sets(grammar, trailing_sets)
    
    return trailing_sets


def add_direct_trailing_terminals(grammar, trailing_sets):
    for production in grammar.production_list:
        if len(production.right_side) > 0:
            last_symbol = production.right_side[-1]
            
            if is_terminal_symbol(last_symbol, grammar):
                if last_symbol not in trailing_sets[production.left_side]:
                    trailing_sets[production.left_side].append(last_symbol)
            
            if len(production.right_side) > 1:
                last_is_nonterminal = is_nonterminal_symbol(last_symbol, grammar)
                second_last_is_terminal = is_terminal_symbol(production.right_side[-2], grammar)
                if last_is_nonterminal and second_last_is_terminal:
                    second_last_symbol = production.right_side[-2]
                    if second_last_symbol not in trailing_sets[production.left_side]:
                        trailing_sets[production.left_side].append(second_last_symbol)


def propagate_trailing_sets(grammar, trailing_sets):
    something_changed = True
    while something_changed:
        something_changed = False
        
        for production in grammar.production_list:
            if len(production.right_side) > 0:
                last_symbol = production.right_side[-1]
                if is_nonterminal_symbol(last_symbol, grammar):
                    old_count = len(trailing_sets[production.left_side])
                    
                    for terminal in trailing_sets[last_symbol]:
                        if terminal not in trailing_sets[production.left_side]:
                            trailing_sets[production.left_side].append(terminal)
                    
                    new_count = len(trailing_sets[production.left_side])
                    if new_count > old_count:
                        something_changed = True


def set_precedence_relation(symbol_a, symbol_b, relation_type, precedence_relations):
    relation_key = (symbol_a, symbol_b)
    if relation_key in precedence_relations:
        existing_relation = precedence_relations[relation_key]
        if existing_relation != relation_type:
            error_message = "Conflict: " + symbol_a + " and " + symbol_b + " have both '" + existing_relation + "' and '" + relation_type + "'"
            raise Exception(error_message)
    precedence_relations[relation_key] = relation_type