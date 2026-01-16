import tkinter as tk
from tkinter import scrolledtext
from main import parse_grammar
from backtracking_parser import BacktrackingParser
from op_precedence_parser import OperatorPrecedenceParser


COLORS = {
    "try": "blue",
    "match": "green",
    "fail": "red",
    "backtrack": "orange",
    "shift": "blue",
    "reduce": "purple",
    "accept": "green",
    "reject": "red"
}


class ParserGUI:
    def __init__(self, window):
        self.window = window
        self.window.title("Parsing Visualizer")
        self.window.geometry("800x600")
        
        self.grammar = None
        self.steps = []
        self.current_step = 0
        
        self.create_widgets()
        self.load_example()
    
    def create_widgets(self):
        tk.Label(self.window, text="Grammar (format: A -> x y | z)").pack(anchor="w", padx=10, pady=(10,0))
        
        self.grammar_box = scrolledtext.ScrolledText(self.window, height=6, width=60, font=("Courier", 10))
        self.grammar_box.pack(padx=10, pady=5)
        
        tk.Button(self.window, text="Load Grammar", command=self.load_grammar).pack(pady=5)
        
        self.grammar_status = tk.Label(self.window, text="", fg="gray")
        self.grammar_status.pack()
        
        tk.Label(self.window, text="Input String:").pack(anchor="w", padx=10, pady=(10,0))
        
        self.input_box = tk.Entry(self.window, width=50, font=("Courier", 12))
        self.input_box.pack(padx=10, pady=5)
        
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Backtracking Parse", command=self.start_backtracking).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Operator Precedence Parse", command=self.start_op_precedence).pack(side="left", padx=5)
        
        btn_frame2 = tk.Frame(self.window)
        btn_frame2.pack(pady=5)
        
        self.next_btn = tk.Button(btn_frame2, text="Next Step", command=self.next_step, state="disabled")
        self.next_btn.pack(side="left", padx=5)
        
        self.reset_btn = tk.Button(btn_frame2, text="Reset", command=self.reset, state="disabled")
        self.reset_btn.pack(side="left", padx=5)
        
        self.step_label = tk.Label(self.window, text="", font=("Arial", 11, "bold"))
        self.step_label.pack(pady=5)
        
        tk.Label(self.window, text="Steps:").pack(anchor="w", padx=10)
        
        self.history_box = tk.Listbox(self.window, height=12, width=80, font=("Courier", 9))
        self.history_box.pack(padx=10, pady=5, fill="both", expand=True)
        
        self.result_label = tk.Label(self.window, text="", font=("Arial", 12, "bold"))
        self.result_label.pack(pady=5)
    
    def load_grammar(self):
        text = self.grammar_box.get("1.0", "end").strip()
        
        if not text:
            self.grammar = None
            self.grammar_status.config(text="Please enter a grammar", fg="orange")
            return
        
        try:
            self.grammar = parse_grammar(text)
            self.grammar_status.config(
                text=f"Loaded {len(self.grammar.productions)} rules. Terminals: {self.grammar.terminals}",
                fg="green"
            )
        except Exception as e:
            self.grammar = None
            error_msg = str(e) if str(e) else "Invalid grammar format"
            self.grammar_status.config(text=f"Error: {error_msg}", fg="red")
    
    def start_backtracking(self):
        if not self.check_ready():
            return
        
        self.reset()
        
        try:
            parser = BacktrackingParser(self.grammar)
            input_text = self.input_box.get()
            self.steps = parser.parse(input_text)
            
            if not self.steps:
                self.step_label.config(text="No steps generated", fg="orange")
                return
            
            self.enable_controls()
            self.step_label.config(text="Backtracking Parser - Ready", fg="black")
        except Exception as e:
            error_msg = str(e) if str(e) else "Parsing failed"
            self.step_label.config(text=f"Error: {error_msg}", fg="red")
    
    def start_op_precedence(self):
        if not self.check_ready():
            return
        
        self.reset()
        
        try:
            parser = OperatorPrecedenceParser(self.grammar)
            input_text = self.input_box.get()
            self.steps = parser.parse(input_text)
            
            if not self.steps:
                self.step_label.config(text="No steps generated", fg="orange")
                return
            
            self.enable_controls()
            self.step_label.config(text="Operator Precedence Parser - Ready", fg="black")
        except Exception as e:
            error_msg = str(e) if str(e) else "Parsing failed"
            if "epsilon" in error_msg.lower():
                error_msg = "Grammar has epsilon - not allowed for OP parser"
            elif "adjacent" in error_msg.lower():
                error_msg = "Grammar has adjacent non-terminals - not allowed for OP parser"
            elif "conflict" in error_msg.lower():
                error_msg = "Grammar has precedence conflicts - try a simpler grammar"
            self.step_label.config(text=f"Error: {error_msg}", fg="red")
    
    def check_ready(self):
        if self.grammar is None:
            self.step_label.config(text="Please load a grammar first!", fg="orange")
            return False
        
        if not self.input_box.get().strip():
            self.step_label.config(text="Please enter an input string!", fg="orange")
            return False
        
        return True
    
    def next_step(self):
        if self.current_step >= len(self.steps):
            return
        
        step = self.steps[self.current_step]
        self.current_step += 1
        
        self.step_label.config(text=f"Step {step.number}: [{step.action.upper()}] {step.description}")
        
        text = f"{step.number}. [{step.action}] {step.description}"
        self.history_box.insert("end", text)
        
        color = COLORS.get(step.action, "black")
        self.history_box.itemconfig("end", fg=color)
        self.history_box.see("end")
        
        if step.action == "accept":
            self.result_label.config(text="ACCEPTED", fg="green")
            self.next_btn.config(state="disabled")
        elif step.action == "reject":
            self.result_label.config(text="REJECTED", fg="red")
            self.next_btn.config(state="disabled")
    
    def reset(self):
        self.steps = []
        self.current_step = 0
        self.history_box.delete(0, "end")
        self.step_label.config(text="")
        self.result_label.config(text="")
        self.next_btn.config(state="disabled")
        self.reset_btn.config(state="disabled")
    
    def enable_controls(self):
        self.next_btn.config(state="normal")
        self.reset_btn.config(state="normal")
    
    def load_example(self):
        example_grammar = """S -> a A b
A -> c | d"""
        self.grammar_box.insert("1.0", example_grammar)
        self.input_box.insert(0, "a c b")


def start_app():
    window = tk.Tk()
    app = ParserGUI(window)
    window.mainloop()


if __name__ == "__main__":
    start_app()
