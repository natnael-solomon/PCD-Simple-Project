import tkinter as tk
from tkinter import scrolledtext
from parsing_core import parse_grammar_text
from backtracking_parser import BacktrackingParser
from operator_precedence_parser import OperatorPrecedenceParser


step_colors = {
    "try": "blue",
    "match": "green",
    "fail": "red",
    "backtrack": "orange",
    "shift": "blue",
    "reduce": "purple",
    "accept": "green",
    "reject": "red",
    "infinite": "red"
}


class ParserGUI:
    ERROR_TYPES = ["LEFT RECURSION ERROR", "RECURSION DEPTH ERROR", "PRECEDENCE CONFLICT ERROR", "CYCLIC PRECEDENCE ERROR", "PARSING STEPS ERROR"]
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_window.title("Parsing Visualizer")
        self.main_window.geometry("800x600")
        
        self.current_grammar = None
        self.parsing_steps = []
        self.current_step_index = 0
        
        self.setup_gui_widgets()
        self.load_example_grammar()
    
    def setup_gui_widgets(self):
        grammar_label = tk.Label(self.main_window, text="Grammar (format: A -> x y | z)")
        grammar_label.pack(anchor="w", padx=10, pady=(10,0))
        
        self.grammar_text_box = scrolledtext.ScrolledText(self.main_window, height=6, width=60, font=("Courier", 10))
        self.grammar_text_box.pack(padx=10, pady=5)
        
        load_grammar_button = tk.Button(self.main_window, text="Load Grammar", command=self.load_grammar_from_text)
        load_grammar_button.pack(pady=5)
        
        self.grammar_status_label = tk.Label(self.main_window, text="", fg="gray")
        self.grammar_status_label.pack()
        
        input_label = tk.Label(self.main_window, text="Input String:")
        input_label.pack(anchor="w", padx=10, pady=(10,0))
        
        self.input_text_box = tk.Entry(self.main_window, width=50, font=("Courier", 12))
        self.input_text_box.pack(padx=10, pady=5)
        
        button_frame_1 = tk.Frame(self.main_window)
        button_frame_1.pack(pady=10)
        
        backtracking_button = tk.Button(button_frame_1, text="Backtracking Parse", command=self.start_backtracking_parser)
        backtracking_button.pack(side="left", padx=5)
        
        op_precedence_button = tk.Button(button_frame_1, text="Operator Precedence Parse", command=self.start_op_precedence_parser)
        op_precedence_button.pack(side="left", padx=5)
        
        button_frame_2 = tk.Frame(self.main_window)
        button_frame_2.pack(pady=5)
        
        self.next_step_button = tk.Button(button_frame_2, text="Next Step", command=self.show_next_step, state="disabled")
        self.next_step_button.pack(side="left", padx=5)
        
        self.reset_button = tk.Button(button_frame_2, text="Reset", command=self.reset_parsing, state="disabled")
        self.reset_button.pack(side="left", padx=5)
        
        self.current_step_label = tk.Label(self.main_window, text="", font=("Arial", 11, "bold"))
        self.current_step_label.pack(pady=5)
        
        steps_label = tk.Label(self.main_window, text="Steps:")
        steps_label.pack(anchor="w", padx=10)
        
        self.steps_history_box = tk.Listbox(self.main_window, height=12, width=80, font=("Courier", 9))
        self.steps_history_box.pack(padx=10, pady=5, fill="both", expand=True)
        
        self.final_result_label = tk.Label(self.main_window, text="", font=("Arial", 12, "bold"))
        self.final_result_label.pack(pady=5)
    
    def load_grammar_from_text(self):
        grammar_text = self.grammar_text_box.get("1.0", "end").strip()
        
        if grammar_text == "":
            self.current_grammar = None
            self.grammar_status_label.config(text="Please enter a grammar", fg="orange")
            return
        
        try:
            self.current_grammar = parse_grammar_text(grammar_text)
            
            production_count = len(self.current_grammar.production_list)
            terminal_list = str(self.current_grammar.terminal_symbols)
            status_message = "Loaded " + str(production_count) + " rules. Terminals: " + terminal_list
            
            self.grammar_status_label.config(text=status_message, fg="green")
        except Exception as error:
            self.current_grammar = None
            if str(error) != "":
                error_message = str(error)
            else:
                error_message = "Invalid grammar format"
            self.grammar_status_label.config(text="Error: " + error_message, fg="red")
    
    def handle_parsing_error(self, error, default_message="Parsing failed"):
        error_message = str(error) if str(error) != "" else default_message
        self.current_step_label.config(text="Error: " + error_message, fg="red")
    
    def start_backtracking_parser(self):
        if not self.check_if_ready_to_parse():
            return
        
        self.reset_parsing()
        
        try:
            backtracking_parser = BacktrackingParser(self.current_grammar)
            input_string = self.input_text_box.get()
            self.parsing_steps = backtracking_parser.parse_input(input_string)
            
            if len(self.parsing_steps) == 0:
                self.current_step_label.config(text="No steps generated", fg="orange")
                return
            
            if len(self.parsing_steps) > 0:
                error_msg = self.parsing_steps[0].description
                if "LEFT RECURSION ERROR" in error_msg:
                    self.current_step_label.config(text="LEFT RECURSION ERROR", fg="red")
                    error_detail = error_msg.split(": ", 1)[1]
                    self.final_result_label.config(text=error_detail, fg="red")
                    self.next_step_button.config(state="disabled")
                    self.reset_button.config(state="normal")
                    return
                elif "RECURSION DEPTH ERROR" in error_msg:
                    self.current_step_label.config(text="RECURSION DEPTH ERROR", fg="red")
                    error_detail = error_msg.split(": ", 1)[1]
                    self.final_result_label.config(text=error_detail, fg="red")
                    self.next_step_button.config(state="disabled")
                    self.reset_button.config(state="normal")
                    return
            
            self.enable_step_controls()
            self.current_step_label.config(text="Backtracking Parser - Ready", fg="black")
        except Exception as error:
            self.handle_parsing_error(error, "Parsing failed")
    
    def start_op_precedence_parser(self):
        if not self.check_if_ready_to_parse():
            return
        
        self.reset_parsing()
        
        try:
            op_precedence_parser = OperatorPrecedenceParser(self.current_grammar)
            input_string = self.input_text_box.get()
            self.parsing_steps = op_precedence_parser.parse_input(input_string)
            
            if len(self.parsing_steps) == 0:
                self.current_step_label.config(text="No steps generated", fg="orange")
                return
            
            if len(self.parsing_steps) > 0:
                error_msg = self.parsing_steps[0].description
                if "PRECEDENCE CONFLICT ERROR" in error_msg:
                    self.current_step_label.config(text="PRECEDENCE CONFLICT ERROR", fg="red")
                    error_detail = error_msg.split(": ", 1)[1]
                    self.final_result_label.config(text=error_detail, fg="red")
                    self.next_step_button.config(state="disabled")
                    self.reset_button.config(state="normal")
                    return
                elif "CYCLIC PRECEDENCE ERROR" in error_msg:
                    self.current_step_label.config(text="CYCLIC PRECEDENCE ERROR", fg="red")
                    error_detail = error_msg.split(": ", 1)[1]
                    self.final_result_label.config(text=error_detail, fg="red")
                    self.next_step_button.config(state="disabled")
                    self.reset_button.config(state="normal")
                    return
                elif "PARSING STEPS ERROR" in error_msg:
                    self.current_step_label.config(text="PARSING STEPS ERROR", fg="red")
                    error_detail = error_msg.split(": ", 1)[1]
                    self.final_result_label.config(text=error_detail, fg="red")
                    self.next_step_button.config(state="disabled")
                    self.reset_button.config(state="normal")
                    return
            
            self.enable_step_controls()
            self.current_step_label.config(text="Operator Precedence Parser - Ready", fg="black")
        except Exception as error:
            error_message = str(error) if str(error) != "" else "Parsing failed"
            
            error_lower = error_message.lower()
            if "epsilon" in error_lower:
                error_message = "Grammar has epsilon - not allowed for OP parser"
            elif "adjacent" in error_lower:
                error_message = "Grammar has adjacent non-terminals - not allowed for OP parser"
            elif "conflict" in error_lower:
                error_message = "PRECEDENCE CONFLICT ERROR"
                self.current_step_label.config(text="PRECEDENCE CONFLICT ERROR", fg="red")
                self.final_result_label.config(text="Grammar has precedence conflicts - parser cannot determine shift/reduce actions", fg="red")
                self.next_step_button.config(state="disabled")
                self.reset_button.config(state="normal")
                return
            
            self.handle_parsing_error(Exception(error_message), "Parsing failed")
    
    def check_if_ready_to_parse(self):
        if self.current_grammar is None:
            self.current_step_label.config(text="Please load a grammar first!", fg="orange")
            return False
        
        input_string = self.input_text_box.get().strip()
        if input_string == "":
            self.current_step_label.config(text="Please enter an input string!", fg="orange")
            return False
        
        return True
    
    def show_next_step(self):
        if self.current_step_index >= len(self.parsing_steps):
            return
        
        current_step = self.parsing_steps[self.current_step_index]
        self.current_step_index = self.current_step_index + 1
        
        step_number = str(current_step.number)
        step_action = current_step.action.upper()
        step_description = current_step.description
        
        step_label_text = "Step " + step_number + ": [" + step_action + "] " + step_description
        
        is_error = any(error_type in step_description for error_type in self.ERROR_TYPES)
        
        if is_error:
            for error_type in self.ERROR_TYPES:
                if error_type in step_description:
                    self.current_step_label.config(text=error_type, fg="red")
                    break
            
            error_detail = step_description.split(": ", 1)[1] if ": " in step_description else step_description
            self.final_result_label.config(text=error_detail, fg="red")
        else:
            self.current_step_label.config(text=step_label_text)
        
        history_text = step_number + ". [" + current_step.action + "] " + step_description
        self.steps_history_box.insert("end", history_text)
        
        if any(error_type in step_description for error_type in self.ERROR_TYPES):
            step_color = "red"
        elif current_step.action in step_colors:
            step_color = step_colors[current_step.action]
        else:
            step_color = "black"
        
        self.steps_history_box.itemconfig("end", fg=step_color)
        self.steps_history_box.see("end")
        
        if current_step.action == "accept":
            self.final_result_label.config(text="ACCEPTED", fg="green")
            self.next_step_button.config(state="disabled")
        elif current_step.action == "reject":
            error_types = ["LEFT RECURSION ERROR", "RECURSION DEPTH ERROR", "PRECEDENCE CONFLICT ERROR", "CYCLIC PRECEDENCE ERROR", "PARSING STEPS ERROR"]
            if not any(error_type in step_description for error_type in error_types):
                self.final_result_label.config(text="REJECTED", fg="red")
            self.next_step_button.config(state="disabled")
    
    def reset_parsing(self):
        self.parsing_steps = []
        self.current_step_index = 0
        self.steps_history_box.delete(0, "end")
        self.current_step_label.config(text="")
        self.final_result_label.config(text="")
        self.next_step_button.config(state="disabled")
        self.reset_button.config(state="disabled")
    
    def enable_step_controls(self):
        self.next_step_button.config(state="normal")
        self.reset_button.config(state="normal")
    
    def load_example_grammar(self):
        example_grammar_text = """S -> a A b
A -> c | d"""
        self.grammar_text_box.insert("1.0", example_grammar_text)
        self.input_text_box.insert(0, "a c b")


def start_gui_application():
    main_window = tk.Tk()
    gui_application = ParserGUI(main_window)
    main_window.mainloop()


if __name__ == "__main__":
    start_gui_application()