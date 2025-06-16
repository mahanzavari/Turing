import time
import os
import tkinter as tk
from tkinter import font , messagebox
class TuringMachine:
    """
    A class to simulate a Turing Machine for palindrome checking.
    The machine's logic is separated from the GUI.
    """

    def __init__(self):
        """
        Initializes the Turing Machine with its states and transition function.
        """
        self.blank_symbol = 'B'
        self.halt_state = 'q_halt'
        self.transitions = {
            'q0': {
                'a': {'newState': 'q1', 'write': self.blank_symbol, 'move': 'R'},
                'b': {'newState': 'q2', 'write': self.blank_symbol, 'move': 'R'},
                self.blank_symbol: {'newState': 'q_yes', 'write': self.blank_symbol, 'move': 'L'}
            },
            'q1': { # Saw 'a', scanning right
                'a': {'newState': 'q1', 'write': 'a', 'move': 'R'},
                'b': {'newState': 'q1', 'write': 'b', 'move': 'R'},
                self.blank_symbol: {'newState': 'q3', 'write': self.blank_symbol, 'move': 'L'}
            },
            'q2': { # Saw 'b', scanning right
                'a': {'newState': 'q2', 'write': 'a', 'move': 'R'},
                'b': {'newState': 'q2', 'write': 'b', 'move': 'R'},
                self.blank_symbol: {'newState': 'q4', 'write': self.blank_symbol, 'move': 'L'}
            },
            'q3': { # Expect 'a' at the end
                'a': {'newState': 'q5', 'write': self.blank_symbol, 'move': 'L'},
                'b': {'newState': 'q_no', 'write': 'b', 'move': 'L'},
                self.blank_symbol: {'newState': 'q_yes', 'write': self.blank_symbol, 'move': 'L'}
            },
            'q4': { # Expect 'b' at the end
                'b': {'newState': 'q5', 'write': self.blank_symbol, 'move': 'L'},
                'a': {'newState': 'q_no', 'write': 'a', 'move': 'L'},
                self.blank_symbol: {'newState': 'q_yes', 'write': self.blank_symbol, 'move': 'L'}
            },
            'q5': { # Return left
                'a': {'newState': 'q5', 'write': 'a', 'move': 'L'},
                'b': {'newState': 'q5', 'write': 'b', 'move': 'L'},
                self.blank_symbol: {'newState': 'q0', 'write': self.blank_symbol, 'move': 'R'}
            },
            'q_yes': { # Start Accept Sequence
                'a': {'newState': 'q_yes', 'write': self.blank_symbol, 'move': 'L'},
                'b': {'newState': 'q_yes', 'write': self.blank_symbol, 'move': 'L'},
                self.blank_symbol: {'newState': 'qy1', 'write': self.blank_symbol, 'move': 'R'}
            },
            'qy1': {self.blank_symbol: {'newState': 'qy2', 'write': 'Y', 'move': 'R'}},
            'qy2': {self.blank_symbol: {'newState': 'qy3', 'write': 'E', 'move': 'R'}},
            'qy3': {self.blank_symbol: {'newState': self.halt_state, 'write': 'S', 'move': 'S'}},
            'q_no': { # Start Reject Sequence
                'a': {'newState': 'q_no', 'write': self.blank_symbol, 'move': 'L'},
                'b': {'newState': 'q_no', 'write': self.blank_symbol, 'move': 'L'},
                self.blank_symbol: {'newState': 'qn1', 'write': self.blank_symbol, 'move': 'R'}
            },
            'qn1': {self.blank_symbol: {'newState': 'qn2', 'write': 'N', 'move': 'R'}},
            'qn2': {self.blank_symbol: {'newState': self.halt_state, 'write': 'O', 'move': 'S'}}
        }
        self.tape = {}
        self.head_position = 0
        self.current_state = 'q0'
        self.step_count = 0

    def initialize(self, input_string):
        """Resets the machine's state for a new run."""
        self.tape = {i: char for i, char in enumerate(input_string)}
        self.head_position = 0
        self.current_state = 'q0'
        self.step_count = 0
        return all(c in 'ab' for c in input_string)

    def step(self):
        """Performs a single step of the Turing Machine computation."""
        if self.current_state == self.halt_state:
            return False

        read_symbol = self.tape.get(self.head_position, self.blank_symbol)
        
        if self.current_state not in self.transitions or read_symbol not in self.transitions[self.current_state]:
            # This case indicates an incomplete transition function, which is an error.
            print(f"Error: No transition for state '{self.current_state}' and symbol '{read_symbol}'")
            self.current_state = self.halt_state # Force halt on error
            return False

        rule = self.transitions[self.current_state][read_symbol]
        
        # Apply the transition rule
        self.tape[self.head_position] = rule['write']
        if rule['move'] == 'R':
            self.head_position += 1
        elif rule['move'] == 'L':
            self.head_position -= 1
        
        self.current_state = rule['newState']
        self.step_count += 1
        
        return self.current_state != self.halt_state


class TuringMachineGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Turing Machine Palindrome Checker")
        self.master.geometry("800x450")
        
        self.tm = TuringMachine()
        self.simulation_id = None
        self.cell_width = 40
        self.cell_height = 40

        # Define fonts
        self.control_font = font.Font(family="Helvetica", size=10)
        self.tape_font = font.Font(family="Courier New", size=14, weight="bold")
        self.status_font = font.Font(family="Helvetica", size=12, weight="bold")

        # --- Setup Widgets ---
        self.setup_widgets()

    def setup_widgets(self):
        # --- Control Frame ---
        control_frame = tk.Frame(self.master, pady=10)
        control_frame.pack(fill=tk.X)

        tk.Label(control_frame, text="Input String:", font=self.control_font).pack(side=tk.LEFT, padx=(10, 5))
        self.input_entry = tk.Entry(control_frame, width=30, font=self.control_font)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        self.input_entry.insert(0, "ababa")

        self.run_button = tk.Button(control_frame, text="Run", command=self.start_simulation, font=self.control_font)
        self.run_button.pack(side=tk.LEFT, padx=5)
        self.reset_button = tk.Button(control_frame, text="Reset", command=self.reset_simulation, font=self.control_font)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        tk.Label(control_frame, text="Speed (ms/step):", font=self.control_font).pack(side=tk.LEFT, padx=(20, 5))
        self.speed_scale = tk.Scale(control_frame, from_=500, to=10, orient=tk.HORIZONTAL, length=150)
        self.speed_scale.set(200)
        self.speed_scale.pack(side=tk.LEFT, padx=5)

        # --- Status Frame ---
        status_frame = tk.Frame(self.master, pady=5)
        status_frame.pack(fill=tk.X)
        self.status_label_var = tk.StringVar(value="State: q0")
        tk.Label(status_frame, textvariable=self.status_label_var, font=self.status_font).pack(side=tk.LEFT, padx=10)
        self.step_label_var = tk.StringVar(value="Step: 0")
        tk.Label(status_frame, textvariable=self.step_label_var, font=self.status_font).pack(side=tk.RIGHT, padx=10)

        # --- Canvas for Tape ---
        self.tape_canvas = tk.Canvas(self.master, bg="white", scrollregion=(-5000, 0, 5000, 200))
        self.tape_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.draw_tape()

    def start_simulation(self):
        input_string = self.input_entry.get()
        if not self.tm.initialize(input_string):
            messagebox.showerror("Invalid Input", "Input string can only contain 'a' and 'b'.")
            return

        self.reset_simulation() # Clear previous state before starting
        self.tm.initialize(input_string) # Re-initialize with the new string
        
        self.run_button.config(state=tk.DISABLED)
        self.input_entry.config(state=tk.DISABLED)
        
        self.run_step()

    def run_step(self):
        # Update labels before the step for initial state (q0) display
        self.status_label_var.set(f"State: {self.tm.current_state}")
        self.step_label_var.set(f"Step: {self.tm.step_count}")
        self.draw_tape()

        if self.tm.step(): # Perform one step
            delay = self.speed_scale.get()
            self.simulation_id = self.master.after(delay, self.run_step)
        else:
            # Halted, redraw final state
            self.draw_tape()
            self.run_button.config(state=tk.NORMAL)
            self.input_entry.config(state=tk.NORMAL)


    def reset_simulation(self):
        if self.simulation_id:
            self.master.after_cancel(self.simulation_id)
            self.simulation_id = None
        
        self.tm.initialize("") # Reset TM to initial state with empty tape
        self.status_label_var.set("State: q0")
        self.step_label_var.set("Step: 0")
        self.draw_tape()
        self.run_button.config(state=tk.NORMAL)
        self.input_entry.config(state=tk.NORMAL)

    def draw_tape(self):
        self.tape_canvas.delete("all")
        canvas_width = self.tape_canvas.winfo_width()
        canvas_height = self.tape_canvas.winfo_height()
        
        # Calculate the starting cell index to draw to center the head
        center_x = canvas_width / 2
        start_cell_index = self.tm.head_position - int(center_x / self.cell_width)
        end_cell_index = self.tm.head_position + int(center_x / self.cell_width) + 2

        for i in range(start_cell_index, end_cell_index):
            symbol = self.tm.tape.get(i, self.tm.blank_symbol)
            
            # Calculate position for each cell
            x0 = center_x + (i - self.tm.head_position) * self.cell_width - (self.cell_width / 2)
            y0 = canvas_height / 2 - self.cell_height / 2
            x1 = x0 + self.cell_width
            y1 = y0 + self.cell_height
            
            # Draw cell and symbol
            self.tape_canvas.create_rectangle(x0, y0, x1, y1, outline="black", fill="lightblue")
            self.tape_canvas.create_text(x0 + self.cell_width/2, y0 + self.cell_height/2,
                                         text=symbol, font=self.tape_font, fill="black")

            # Draw head indicator
            if i == self.tm.head_position:
                head_x = x0 + self.cell_width / 2
                head_y = y1 + 5
                self.tape_canvas.create_text(head_x, head_y, text="^", font=("Helvetica", 16, "bold"), anchor=tk.N, fill="red")


if __name__ == "__main__":
    root = tk.Tk()
    app = TuringMachineGUI(root)
    root.mainloop()
