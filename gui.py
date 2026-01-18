import tkinter as tk
from tkinter import scrolledtext, Canvas, font
from parsing_core import parse_grammar_text
from backtracking_parser import BacktrackingParser
from operator_precedence_parser import OperatorPrecedenceParser


class ParserGUI:
    ERROR_TYPES = ["LEFT RECURSION ERROR", "RECURSION DEPTH ERROR", "PRECEDENCE CONFLICT ERROR", "CYCLIC PRECEDENCE ERROR", "PARSING STEPS ERROR"]
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_window.title("Parsing Visualizer")
        self.main_window.geometry("1200x800")
        
        self.current_grammar = None
        self.parsing_steps = []
        self.current_step_index = 0
        self.current_parser_type = None
        self.parse_tree_nodes = []
        self.parse_tree_root = None
        self.partial_tree_stack = []
        
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
        
        viz_label = tk.Label(self.main_window, text="Visualization:")
        viz_label.pack(anchor="w", padx=10)
        
        self.viz_container = tk.Frame(self.main_window, bg="white", relief="solid", borderwidth=1)
        self.viz_container.pack(padx=10, pady=5, fill="both", expand=True)
        
        self.tree_scroll_frame = tk.Frame(self.viz_container, bg="white")
        
        self.tree_v_scrollbar = tk.Scrollbar(self.tree_scroll_frame, orient="vertical")
        self.tree_h_scrollbar = tk.Scrollbar(self.tree_scroll_frame, orient="horizontal")
        
        self.parse_tree_canvas = Canvas(
            self.tree_scroll_frame, 
            bg="white", 
            highlightthickness=0,
            yscrollcommand=self.tree_v_scrollbar.set,
            xscrollcommand=self.tree_h_scrollbar.set
        )
        
        self.tree_v_scrollbar.config(command=self.parse_tree_canvas.yview)
        self.tree_h_scrollbar.config(command=self.parse_tree_canvas.xview)
        
        self.parse_tree_canvas.grid(row=0, column=0, sticky="nsew")
        self.tree_v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree_h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.tree_scroll_frame.grid_rowconfigure(0, weight=1)
        self.tree_scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.tree_scroll_frame.pack_forget()
        
        self.table_container = tk.Frame(self.viz_container, bg="white")
        self.table_scrollbar = tk.Scrollbar(self.table_container)
        self.table_scrollbar.pack(side="right", fill="y")
        
        self.table_canvas = Canvas(self.table_container, bg="white", highlightthickness=0, 
                                   yscrollcommand=self.table_scrollbar.set)
        self.table_canvas.pack(side="left", fill="both", expand=True)
        self.table_scrollbar.config(command=self.table_canvas.yview)
        
        self.table_frame = tk.Frame(self.table_canvas, bg="white")
        self.table_canvas_window = self.table_canvas.create_window((0, 0), window=self.table_frame, anchor="n")
        
        self.table_container.pack_forget()
        
        self.table_canvas.bind('<Configure>', self.on_table_canvas_configure)
        
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
    
    def _handle_error_step(self, step_description):
        for error_type in self.ERROR_TYPES:
            if error_type in step_description:
                self.current_step_label.config(text=error_type, fg="red")
                break
        
        error_detail = step_description.split(": ", 1)[1] if ": " in step_description else step_description
        self.final_result_label.config(text=error_detail, fg="red")
    
    def _extract_precedence_relation(self, description):
        """Extract precedence relation symbol from description"""
        if " < " in description or " ⋖ " in description:
            return "⋖"
        elif " > " in description or " ⋗ " in description:
            return "⋗"
        elif " = " in description or " ≐ " in description:
            return "≐"
        return ""
    
    def _check_for_parser_errors(self, parsing_steps):
        """Check if first step contains an error and handle it"""
        if len(parsing_steps) == 0:
            return False
        
        error_msg = parsing_steps[0].description
        for error_type in self.ERROR_TYPES:
            if error_type in error_msg:
                self.current_step_label.config(text=error_type, fg="red")
                error_detail = error_msg.split(": ", 1)[1] if ": " in error_msg else error_msg
                self.final_result_label.config(text=error_detail, fg="red")
                self.next_step_button.config(state="disabled")
                self.reset_button.config(state="normal")
                return True
        return False
    
    def start_backtracking_parser(self):
        if not self.check_if_ready_to_parse():
            return
        
        self.reset_parsing()
        self.current_parser_type = 'backtracking'
        
        try:
            backtracking_parser = BacktrackingParser(self.current_grammar)
            input_string = self.input_text_box.get()
            self.parsing_steps = backtracking_parser.parse_input(input_string)
            self.parse_tree_root = backtracking_parser.parse_tree
            
            if len(self.parsing_steps) == 0:
                self.current_step_label.config(text="No steps generated", fg="orange")
                return
            
            if self._check_for_parser_errors(self.parsing_steps):
                return
            
            self.enable_step_controls()
            self.current_step_label.config(text="Backtracking Parser - Ready (Press Next Step to begin)", fg="black")
        except Exception as error:
            self.handle_parsing_error(error, "Parsing failed")
    
    def start_op_precedence_parser(self):
        if not self.check_if_ready_to_parse():
            return
        
        self.reset_parsing()
        self.current_parser_type = 'op_precedence'
        
        try:
            op_precedence_parser = OperatorPrecedenceParser(self.current_grammar)
            input_string = self.input_text_box.get()
            self.parsing_steps = op_precedence_parser.parse_input(input_string)
            
            if len(self.parsing_steps) == 0:
                self.current_step_label.config(text="No steps generated", fg="orange")
                return
            
            if self._check_for_parser_errors(self.parsing_steps):
                return
            
            self.enable_step_controls()
            self.current_step_label.config(text="Operator Precedence Parser - Ready (Press Next Step to begin)", fg="black")
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
        
        if self.current_step_index == 0:
            if self.current_parser_type == 'backtracking':
                self.tree_scroll_frame.pack(fill="both", expand=True)
                self.table_container.pack_forget()
                self.partial_tree_stack = []
            elif self.current_parser_type == 'op_precedence':
                self.table_container.pack(fill="both", expand=True)
                self.tree_scroll_frame.pack_forget()
                self.initialize_op_table()
        
        current_step = self.parsing_steps[self.current_step_index]
        self.current_step_index = self.current_step_index + 1
        
        step_number = str(current_step.number)
        step_action = current_step.action.upper()
        step_description = current_step.description
        
        step_label_text = "Step " + step_number + ": [" + step_action + "] " + step_description
        
        is_error = any(error_type in step_description for error_type in self.ERROR_TYPES)
        
        if is_error:
            self._handle_error_step(step_description)
        else:
            self.current_step_label.config(text=step_label_text)
        
        if self.current_parser_type == 'backtracking':
            self.update_parse_tree(current_step)
        elif self.current_parser_type == 'op_precedence':
            self.update_op_table(current_step)
        
        if current_step.action == "accept":
            self.final_result_label.config(text="ACCEPTED", fg="green")
            self.next_step_button.config(state="disabled")
        elif current_step.action == "reject":
            if not any(error_type in step_description for error_type in self.ERROR_TYPES):
                self.final_result_label.config(text="REJECTED", fg="red")
            self.next_step_button.config(state="disabled")
    
    def reset_parsing(self):
        self.parsing_steps = []
        self.current_step_index = 0
        self.current_step_label.config(text="")
        self.final_result_label.config(text="")
        self.next_step_button.config(state="disabled")
        self.reset_button.config(state="disabled")
        self.parse_tree_nodes = []
        self.partial_tree_stack = []
        self.parse_tree_canvas.delete("all")
        self.tree_scroll_frame.pack_forget()
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.table_container.pack_forget()
    
    def enable_step_controls(self):
        self.next_step_button.config(state="normal")
        self.reset_button.config(state="normal")
    
    def on_table_canvas_configure(self, event):
        self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))
        canvas_width = event.width
        frame_width = self.table_frame.winfo_reqwidth()
        x_position = max(0, (canvas_width - frame_width) // 2)
        self.table_canvas.coords(self.table_canvas_window, x_position, 0)
    
    def update_parse_tree(self, step):
        if step.action == "accept" and self.parse_tree_root is not None:
            self.draw_complete_tree(self.parse_tree_root)
        else:
            self.show_parsing_progress(step)
    
    def draw_incremental_tree(self):
        self.parse_tree_canvas.delete("all")
        
        if len(self.partial_tree_stack) == 0:
            return
        
        root = self.partial_tree_stack[0]['node']
        
        self.node_radius = 30
        self.vertical_spacing = 80
        self.horizontal_spacing = 70
        
        self._next_x = self.horizontal_spacing
        self._assign_positions_incremental(root, 0)
        
        self._center_tree(root)
        
        self._draw_node_recursive(root)
        
        bbox = self.parse_tree_canvas.bbox("all")
        if bbox:
            self.parse_tree_canvas.configure(scrollregion=bbox)
    
    def show_parsing_progress(self, step):
        self.parse_tree_canvas.delete("all")
        
        canvas_width = self.parse_tree_canvas.winfo_width()
        canvas_height = self.parse_tree_canvas.winfo_height()
        if canvas_width <= 1:
            canvas_width = 760
        if canvas_height <= 1:
            canvas_height = 300
        
        center_x = canvas_width / 2
        center_y = canvas_height / 2
        
        action_text = step.action.upper()
        color_map = {
            "try": "#4A90E2",
            "match": "#7ED321",
            "fail": "#F5A623",
            "backtrack": "#BD10E0"
        }
        color = color_map.get(step.action, "#9B9B9B")
        
        self.parse_tree_canvas.create_text(
            center_x, center_y - 30,
            text=f"Step {step.number}: {action_text}",
            font=("Arial", 14, "bold"),
            fill=color
        )
        
        desc = step.description
        if len(desc) > 60:
            desc = desc[:57] + "..."
        
        self.parse_tree_canvas.create_text(
            center_x, center_y + 10,
            text=desc,
            font=("Arial", 10),
            fill="#333333"
        )
        
        self.parse_tree_canvas.create_text(
            center_x, center_y + 40,
            text="(Tree will appear when parsing completes)",
            font=("Arial", 9, "italic"),
            fill="#999999"
        )
    
    def draw_complete_tree(self, root):
        self.parse_tree_canvas.delete("all")
        
        if root is None:
            return
        
        self.node_radius = 30
        self.vertical_spacing = 80
        self.horizontal_spacing = 70
        
        self._next_x = self.horizontal_spacing
        self._assign_positions_complete(root, 0)
        
        self._center_tree(root)
        
        self._draw_node_recursive(root)
        
        bbox = self.parse_tree_canvas.bbox("all")
        if bbox:
            self.parse_tree_canvas.configure(scrollregion=bbox)
    
    def _assign_positions_complete(self, node, depth):
        if node is None:
            return 0
        
        node.y = 50 + depth * self.vertical_spacing
        
        if node.is_leaf():
            node.x = self._next_x
            self._next_x += self.horizontal_spacing
            return node.x
        else:
            child_positions = []
            for child in node.children:
                child_x = self._assign_positions_complete(child, depth + 1)
                child_positions.append(child_x)
            
            if child_positions:
                node.x = (child_positions[0] + child_positions[-1]) / 2
            else:
                node.x = self._next_x
                self._next_x += self.horizontal_spacing
            
            return node.x
    
    def _center_tree(self, root):
        def find_bounds(node):
            if node is None:
                return (float('inf'), float('-inf'))
            min_x, max_x = node.x, node.x
            for child in node.children:
                child_min, child_max = find_bounds(child)
                min_x = min(min_x, child_min)
                max_x = max(max_x, child_max)
            return (min_x, max_x)
        
        min_x, max_x = find_bounds(root)
        tree_width = max_x - min_x
        
        canvas_width = self.parse_tree_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 760
        
        offset = max(0, (canvas_width - tree_width) / 2 - min_x)
        
        def apply_offset(node):
            if node is None:
                return
            node.x += offset
            for child in node.children:
                apply_offset(child)
        
        if offset > 0:
            apply_offset(root)
    
    def _draw_node_recursive(self, node, parent_x=None, parent_y=None):
        if node is None:
            return
        
        if parent_x is not None and parent_y is not None:
            self.parse_tree_canvas.create_line(
                parent_x, parent_y + self.node_radius,
                node.x, node.y - self.node_radius,
                width=2, fill="#757575", smooth=True
            )
        
        if node.is_leaf():
            color = "#9B9B9B" if node.symbol == "ε" else "#7ED321"
        else:
            color = "#4A90E2"
        
        self.parse_tree_canvas.create_oval(
            node.x - self.node_radius + 3, node.y - self.node_radius + 3,
            node.x + self.node_radius + 3, node.y + self.node_radius + 3,
            fill="#E0E0E0", outline=""
        )
        
        self.parse_tree_canvas.create_oval(
            node.x - self.node_radius, node.y - self.node_radius,
            node.x + self.node_radius, node.y + self.node_radius,
            fill=color, outline="#333333", width=2
        )
        
        font_size = 11 if len(node.symbol) <= 2 else 9
        self.parse_tree_canvas.create_text(
            node.x, node.y, text=node.symbol,
            font=("Arial", font_size, "bold"),
            fill="white"
        )
        
        for child in node.children:
            self._draw_node_recursive(child, node.x, node.y)
    
    def initialize_op_table(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        header_card = tk.Frame(self.table_frame, bg="#2C3E50", relief="flat", borderwidth=0)
        header_card.pack(pady=(10, 5), padx=20)
        
        col_widths = [60, 200, 180, 100, 220]
        headers = ["Step", "Stack", "Input", "Relation", "Action"]
        
        for i, (header_text, width) in enumerate(zip(headers, col_widths)):
            frame = tk.Frame(header_card, bg="#2C3E50", width=width, height=40)
            frame.pack(side="left", padx=2)
            frame.pack_propagate(False)
            
            label = tk.Label(
                frame, 
                text=header_text, 
                font=("Arial", 11, "bold"),
                fg="white",
                bg="#2C3E50",
                anchor="center"
            )
            label.pack(fill="both", expand=True)
        
        self.table_canvas.update_idletasks()
        self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))
    
    def update_op_table(self, step):
        description = step.description
        action = step.action.upper()
        
        stack = ""
        input_str = ""
        relation = ""
        action_text = action
        
        if "stack=" in description:
            stack_start = description.find("stack=")
            if ", input=" in description:
                stack_end = description.find(", input=")
                stack = description[stack_start + 6:stack_end].strip()
            else:
                stack = description[stack_start + 6:].strip()
        
        if "input=" in description:
            input_start = description.find("input=")
            input_str = description[input_start + 6:].strip()
        
        relation = self._extract_precedence_relation(description)
        
        if action == "SHIFT":
            if "Shift '" in description:
                parts = description.split("'")
                if len(parts) >= 2:
                    action_text = "SHIFT " + parts[1]
            else:
                action_text = "SHIFT"
        elif action == "REDUCE":
            if "Reduce " in description:
                reduce_part = description.split("Reduce ")[1]
                if ", stack=" in reduce_part:
                    reduce_part = reduce_part.split(", stack=")[0]
                action_text = "REDUCE " + reduce_part
        elif action == "ACCEPT":
            action_text = "ACCEPT"
            relation = "≐"
        
        if action == "SHIFT":
            card_bg = "#E3F2FD"
            text_color = "#1565C0"
        elif action == "REDUCE":
            card_bg = "#F3E5F5"  # Light purple
            text_color = "#6A1B9A"
        elif action == "ACCEPT":
            card_bg = "#E8F5E9"  # Light green
            text_color = "#2E7D32"
        elif action == "REJECT":
            card_bg = "#FFEBEE"  # Light red
            text_color = "#C62828"
        else:
            card_bg = "#F5F5F5"  # Light gray
            text_color = "#424242"
        
        step_card = tk.Frame(self.table_frame, bg=card_bg, relief="raised", borderwidth=1)
        step_card.pack(pady=2, padx=20, fill="x")
        
        def on_enter(e):
            step_card.config(relief="solid", borderwidth=2)
        
        def on_leave(e):
            step_card.config(relief="raised", borderwidth=1)
        
        step_card.bind("<Enter>", on_enter)
        step_card.bind("<Leave>", on_leave)
        
        col_widths = [60, 200, 180, 100, 220]
        columns = [
            str(step.number),
            stack,
            input_str,
            relation,
            action_text
        ]
        
        for i, (col_text, width) in enumerate(zip(columns, col_widths)):
            col_frame = tk.Frame(step_card, bg=card_bg, width=width, height=35)
            col_frame.pack(side="left", padx=2)
            col_frame.pack_propagate(False)
            
            display_text = col_text
            max_chars = width // 8
            if len(col_text) > max_chars:
                display_text = col_text[:max_chars - 3] + "..."
            
            label = tk.Label(
                col_frame,
                text=display_text,
                font=("Courier", 9),
                fg=text_color,
                bg=card_bg,
                anchor="center"
            )
            label.pack(fill="both", expand=True)
        
        self.table_frame.update_idletasks()
        self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))
        self.table_canvas.yview_moveto(1.0)
    
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