import time
import os
import argparse
import json
from datetime import datetime
from colorama import Fore, Style, init
import threading
import sys
import tkinter as tk
from tkinter import font, messagebox

# Initialize colorama for the CLI
init(autoreset=True)

class TuringMachine:
    """
    A class to simulate a Turing Machine for palindrome checking.
    The machine's logic is consolidated to support both CLI and GUI execution.
    The machine checks if a string from the alphabet {a, b} is a palindrome.
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
        # --- Dynamic State Attributes ---
        self.tape = {}
        self.head_position = 0
        self.current_state = 'q0'
        self.step_count = 0
        self.execution_log = []
        self.start_time = None
        self.animation_running = False
        self.original_input = ""
        self.error_message = ""

    def initialize(self, input_string):
        """Resets the machine's state for a new run. For GUI and CLI."""
        if not all(c in 'ab' for c in input_string):
            return False
        self.original_input = input_string
        self.tape = {i: char for i, char in enumerate(input_string)}
        self.head_position = 0
        self.current_state = 'q0'
        self.step_count = 0
        self.execution_log = []
        self.start_time = time.time()
        self.error_message = ""
        return True

    def step(self):
        """
        Performs a single computation step. Used by the GUI.
        Returns 'CONTINUE', 'HALT', or 'ERROR'.
        """
        if self.current_state == self.halt_state:
            return 'HALT'

        read_symbol = self.tape.get(self.head_position, self.blank_symbol)
        
        step_info = {'step': self.step_count, 'state': self.current_state, 'position': self.head_position, 'read': read_symbol}

        if self.current_state not in self.transitions or read_symbol not in self.transitions[self.current_state]:
            self.error_message = f"No transition for state '{self.current_state}' and symbol '{read_symbol}'"
            print(f"\n{Fore.RED}Error: {self.error_message}{Style.RESET_ALL}")
            self.current_state = self.halt_state
            return 'ERROR'

        rule = self.transitions[self.current_state][read_symbol]
        step_info.update({'write': rule['write'], 'move': rule['move'], 'new_state': rule['newState']})
        self.execution_log.append(step_info)

        self.tape[self.head_position] = rule['write']
        if rule['move'] == 'R': self.head_position += 1
        elif rule['move'] == 'L': self.head_position -= 1
        self.current_state = rule['newState']
        self.step_count += 1
        
        return 'CONTINUE' if self.current_state != self.halt_state else 'HALT'

    def run(self, input_string, verbose=False, delay=0.1, style='fancy', save_log=False):
        """Runs the entire simulation. Used by the CLI."""
        if not self.initialize(input_string):
            return f"{Fore.RED}Error: Input string contains invalid characters."

        if verbose and style != 'compact':
            self.animation_running = True
            spinner_thread = threading.Thread(target=self._animate_loading, args=("Initializing Turing Machine",))
            spinner_thread.start()
            time.sleep(2); self.animation_running = False; spinner_thread.join()
            print(f"\r{' ' * 50}\r", end="")

        if verbose:
            self._display_step(style)
            time.sleep(delay)

        while True:
            status = self.step()
            if status != 'CONTINUE':
                break
            if verbose:
                self._display_step(style)
                time.sleep(delay)

        execution_time = time.time() - self.start_time
        final_content = self.get_tape_content()
        if save_log: self.save_execution_log()

        if verbose and style != 'compact':
            print(f"\n{Fore.GREEN}{'='*20} COMPUTATION COMPLETE {'='*20}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Execution time: {execution_time:.3f} seconds{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Total steps: {self.step_count}{Style.RESET_ALL}")
        
        return final_content

    # --- CLI Display and Helper Methods ---
    def _display_step(self, style):
        if style == 'matrix': self._display_tape_matrix()
        elif style == 'fancy': self._display_tape_fancy()
        elif style == 'compact': self._display_tape_compact()

    def _animate_loading(self, message="Computing"):
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        while self.animation_running:
            for char in chars:
                if not self.animation_running: break
                sys.stdout.write(f'\r{Fore.CYAN}{char} {message}...{Style.RESET_ALL}'); sys.stdout.flush()
                time.sleep(0.1)

    def _get_ascii_art_header(self):
        return f"""{Style.BRIGHT}{Fore.MAGENTA}
╔══════════════════════════════════════════════════════════╗
║                    TURING MACHINE                        ║
║                 PALINDROME ANALYZER                      ║
║                    v3.0 (CLI+GUI)                      ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    def _display_tape_matrix(self, tape_width=50):
        os.system('cls' if os.name == 'nt' else 'clear'); print(self._get_ascii_art_header())
        tape_indices = sorted(self.tape.keys()) if self.tape else [0]
        min_idx, max_idx = min(tape_indices), max(tape_indices)
        start = min(self.head_position - tape_width // 2, min_idx - 5)
        end = max(self.head_position + tape_width // 2, max_idx + 5)
        read_symbol = self.tape.get(self.head_position, self.blank_symbol)
        next_action = "HALT"
        if (self.current_state in self.transitions and read_symbol in self.transitions[self.current_state]):
            rule = self.transitions[self.current_state][read_symbol]
            next_action = f"Write: {rule['write']}, Move: {rule['move']}, → {rule['newState']}"
        print(f"┌─ SYSTEM STATUS ─────────────────────────────────────────┐")
        print(f"│ Current State: {Fore.GREEN}{self.current_state:<15}{Style.RESET_ALL} Step: {Fore.YELLOW}{self.step_count:>8}{Style.RESET_ALL} │")
        print(f"│ Head Position: {Fore.CYAN}{self.head_position:<15}{Style.RESET_ALL} Time: {Fore.MAGENTA}{time.time() - self.start_time:.2f}s{Style.RESET_ALL} │")
        print(f"│ Reading: {Fore.YELLOW}{read_symbol:<20}{Style.RESET_ALL}                      │")
        print(f"└────────────────────────────────────────────────────────┘")
        print(f"┌─ NEXT TRANSITION ───────────────────────────────────────┐")
        print(f"│ {Fore.CYAN}{next_action:<56}{Style.RESET_ALL} │")
        print(f"└────────────────────────────────────────────────────────┘")
        print("┌─ TAPE CONTENTS ─────────────────────────────────────────┐")
        pos_str = "│ "; tape_str = "│ "
        for i in range(start, end + 1):
            pos_str += f"{Fore.RED}{i:^3}{Style.RESET_ALL}" if i == self.head_position else f"{i:^3}"
            symbol = self.tape.get(i, self.blank_symbol)
            if i == self.head_position: tape_str += f"{Style.BRIGHT}{Fore.RED}[{symbol}]{Style.RESET_ALL}"
            else: tape_str += f" {Fore.CYAN}{symbol}{Style.RESET_ALL} " if symbol != self.blank_symbol else f" {Fore.WHITE}·{Style.RESET_ALL} "
        print(pos_str + "│\n" + tape_str + "│")
        print("└────────────────────────────────────────────────────────┘")

    def _display_tape_fancy(self, tape_width=40):
        os.system('cls' if os.name == 'nt' else 'clear'); print(self._get_ascii_art_header())
        tape_indices = sorted(self.tape.keys()) if self.tape else [0]; min_idx, max_idx = min(tape_indices), max(tape_indices)
        start = min(self.head_position - tape_width // 2, min_idx - 5); end = max(self.head_position + tape_width // 2, max_idx + 5)
        read_symbol = self.tape.get(self.head_position, self.blank_symbol); next_action = "HALT - No more transitions"
        if (self.current_state in self.transitions and read_symbol in self.transitions[self.current_state]):
            rule = self.transitions[self.current_state][read_symbol]; next_action = f"Write '{rule['write']}', Move {rule['move']}, Go to {rule['newState']}"
        progress = min(100, (self.step_count / (len(self.original_input) * 10)) * 100) if self.original_input else 0
        bar = "█" * int(progress / 2) + "░" * (50 - int(progress / 2))
        print(f"Progress: {Fore.CYAN}[{bar}]{Style.RESET_ALL} {progress:.1f}%")
        print(f"Current State: {Fore.YELLOW}{self.current_state:<12}{Style.RESET_ALL} Step: {Fore.YELLOW}{self.step_count:>6}{Style.RESET_ALL}"); print(f"Reading Symbol: {Fore.CYAN}'{read_symbol}'{Style.RESET_ALL} at position {Fore.CYAN}{self.head_position}{Style.RESET_ALL}"); print(f"Next Action: {Fore.GREEN}{next_action}{Style.RESET_ALL}"); print("═" * 80)
        tape_str = ""; head_str = ""
        for i in range(start, end + 1):
            symbol = self.tape.get(i, self.blank_symbol)
            if i == self.head_position: tape_str += f"{Style.BRIGHT}{Fore.RED}[{symbol}]{Style.RESET_ALL}"; head_str += f"{Fore.RED} ↑ "
            else: tape_str += f"{Fore.CYAN} {symbol} {Style.RESET_ALL}" if symbol != self.blank_symbol else f"{Fore.WHITE} · {Style.RESET_ALL}"; head_str += "   "
        print(tape_str); print(head_str); print("═" * 80)

    def _display_tape_compact(self):
        tape_content = []; min_key, max_key = (min(self.tape.keys()), max(self.tape.keys())) if self.tape else (0,0)
        for i in range(min_key, max_key + 1): tape_content.append(self.tape.get(i, self.blank_symbol))
        tape_str = "".join(tape_content) if tape_content else self.blank_symbol
        head_indicator = " " * (self.head_position - min_key) + f"{Fore.RED}↑{Style.RESET_ALL}" if self.tape else ""
        read_symbol = self.tape.get(self.head_position, self.blank_symbol); next_action = "HALT"
        if (self.current_state in self.transitions and read_symbol in self.transitions[self.current_state]):
            rule = self.transitions[self.current_state][read_symbol]; next_action = f"R:{read_symbol}→W:{rule['write']},{rule['move']},{rule['newState']}"
        print(f"\r{Fore.MAGENTA}Step {self.step_count:4d}{Style.RESET_ALL} │ {Fore.YELLOW}{self.current_state:8}{Style.RESET_ALL} │ {Fore.CYAN}{tape_str}{Style.RESET_ALL}\n         │          │ {head_indicator}\n         │ {Fore.GREEN}{next_action:<20}{Style.RESET_ALL}\n" + "─" * 50)

    def save_execution_log(self, filename=None):
        if filename is None: filename = f"turing_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_data = {"timestamp": datetime.now().isoformat(), "input_string": self.original_input, "total_steps": self.step_count, "execution_time": time.time() - self.start_time, "final_result": self.get_tape_content(), "execution_log": self.execution_log[-100:]}
        with open(filename, 'w') as f: json.dump(log_data, f, indent=2)
        print(f"{Fore.GREEN}Execution log saved to: {filename}{Style.RESET_ALL}")

    def get_tape_content(self):
        if not self.tape: return ""
        return "".join(self.tape[key] for key in sorted(self.tape.keys()) if self.tape[key] != self.blank_symbol)

    def interactive_mode(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear'); print(self._get_ascii_art_header()); print(f"{Style.BRIGHT}INTERACTIVE MODE{Style.RESET_ALL}\n" + "═" * 50 + "\n1. Check palindrome\n2. Batch test\n3. Exit\n" + "═" * 50)
            choice = input(f"{Fore.YELLOW}Select option (1-3): {Style.RESET_ALL}")
            if choice == '1':
                test_string = input(f"{Fore.CYAN}Enter string to test: {Style.RESET_ALL}")
                style = input(f"{Fore.CYAN}Display style (fancy/matrix/compact): {Style.RESET_ALL}") or 'fancy'
                delay = float(input(f"{Fore.CYAN}Animation delay (seconds): {Style.RESET_ALL}") or "0.2")
                result = self.run(test_string, verbose=True, delay=delay, style=style, save_log=True)
                final_message = f"\nResult for '{test_string}': "
                if "YES" in result: final_message += f"{Fore.GREEN}{result} ✓{Style.RESET_ALL}"
                elif "NO" in result: final_message += f"{Fore.RED}{result} ✗{Style.RESET_ALL}"
                else: final_message += f"{Fore.YELLOW}{result}{Style.RESET_ALL}"
                print(final_message); input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '2':
                test_cases = ["a", "aa", "ab", "aba", "abba", "abab", "aabaa", "b", "bb", "bab"]
                print(f"{Fore.CYAN}Running batch test...{Style.RESET_ALL}")
                for test in test_cases:
                    result = self.run(test, verbose=False)
                    status = "✓" if "YES" in result else "✗"; color = Fore.GREEN if "YES" in result else Fore.RED
                    print(f"{test:>8} → {color}{result} {status}{Style.RESET_ALL}")
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '3': print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}"); break

class TuringMachineGUI:
    """The Tkinter-based GUI for the Turing Machine."""
    def __init__(self, master):
        self.master = master
        self.master.title("Turing Machine Palindrome Checker")
        self.master.geometry("800x450")
        self.tm = TuringMachine()
        self.simulation_id = None
        self.cell_width, self.cell_height = 40, 40
        self.control_font = font.Font(family="Helvetica", size=10)
        self.tape_font = font.Font(family="Courier New", size=14, weight="bold")
        self.status_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.setup_widgets()

    def setup_widgets(self):
        control_frame = tk.Frame(self.master, pady=10); control_frame.pack(fill=tk.X)
        tk.Label(control_frame, text="Input String:", font=self.control_font).pack(side=tk.LEFT, padx=(10, 5))
        self.input_entry = tk.Entry(control_frame, width=30, font=self.control_font); self.input_entry.pack(side=tk.LEFT, padx=5); self.input_entry.insert(0, "ababa")
        self.run_button = tk.Button(control_frame, text="Run", command=self.start_simulation, font=self.control_font); self.run_button.pack(side=tk.LEFT, padx=5)
        self.reset_button = tk.Button(control_frame, text="Reset", command=self.reset_simulation, font=self.control_font); self.reset_button.pack(side=tk.LEFT, padx=5)
        tk.Label(control_frame, text="Speed (ms/step):", font=self.control_font).pack(side=tk.LEFT, padx=(20, 5))
        self.speed_scale = tk.Scale(control_frame, from_=500, to=10, orient=tk.HORIZONTAL, length=150); self.speed_scale.set(200); self.speed_scale.pack(side=tk.LEFT, padx=5)
        status_frame = tk.Frame(self.master, pady=5); status_frame.pack(fill=tk.X)
        self.status_label_var = tk.StringVar(value="State: q0"); tk.Label(status_frame, textvariable=self.status_label_var, font=self.status_font).pack(side=tk.LEFT, padx=10)
        self.step_label_var = tk.StringVar(value="Step: 0"); tk.Label(status_frame, textvariable=self.step_label_var, font=self.status_font).pack(side=tk.RIGHT, padx=10)
        self.tape_canvas = tk.Canvas(self.master, bg="white"); self.tape_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.draw_tape()

    def start_simulation(self):
        input_string = self.input_entry.get()
        if not self.tm.initialize(input_string):
            messagebox.showerror("Invalid Input", "Input string can only contain 'a' and 'b'.")
            return
        self.reset_simulation()
        self.tm.initialize(input_string)
        self.run_button.config(state=tk.DISABLED); self.input_entry.config(state=tk.DISABLED)
        self.run_step()

    def run_step(self):
        self.status_label_var.set(f"State: {self.tm.current_state}"); self.step_label_var.set(f"Step: {self.tm.step_count}")
        self.draw_tape()
        status = self.tm.step()
        if status == 'CONTINUE':
            delay = self.speed_scale.get()
            self.simulation_id = self.master.after(delay, self.run_step)
        else:
            self.draw_tape() # Redraw final state
            self.run_button.config(state=tk.NORMAL); self.input_entry.config(state=tk.NORMAL)
            if status == 'ERROR':
                messagebox.showerror("Simulation Error", self.tm.error_message)

    def reset_simulation(self):
        if self.simulation_id: self.master.after_cancel(self.simulation_id); self.simulation_id = None
        self.tm.initialize(self.input_entry.get() or "")
        self.status_label_var.set("State: q0"); self.step_label_var.set("Step: 0")
        self.draw_tape(); self.run_button.config(state=tk.NORMAL); self.input_entry.config(state=tk.NORMAL)

    def draw_tape(self):
        self.tape_canvas.delete("all"); canvas_width, canvas_height = self.tape_canvas.winfo_width(), self.tape_canvas.winfo_height()
        center_x = canvas_width / 2
        start_cell_idx = self.tm.head_position - int(center_x / self.cell_width)
        end_cell_idx = self.tm.head_position + int(center_x / self.cell_width) + 2
        for i in range(start_cell_idx, end_cell_idx):
            symbol = self.tm.tape.get(i, self.tm.blank_symbol)
            x0 = center_x + (i - self.tm.head_position) * self.cell_width - (self.cell_width / 2)
            y0 = canvas_height / 2 - self.cell_height / 2
            self.tape_canvas.create_rectangle(x0, y0, x0 + self.cell_width, y0 + self.cell_height, outline="black", fill="lightblue")
            self.tape_canvas.create_text(x0 + self.cell_width/2, y0 + self.cell_height/2, text=symbol, font=self.tape_font, fill="black")
            if i == self.tm.head_position:
                self.tape_canvas.create_text(x0 + self.cell_width / 2, y0 + self.cell_height + 5, text="▼", font=("Helvetica", 16, "bold"), anchor=tk.N, fill="red")

# --- Main execution block ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Turing Machine simulator for checking palindromes over {a, b}.")
    parser.add_argument("input_string", nargs='?', default=None, help="The string to check for palindrome (e.g., abba).")
    parser.add_argument("--gui", action="store_true", help="Run the graphical user interface version.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode to see each step of the simulation.")
    parser.add_argument("-d", "--delay", type=float, default=0.2, help="Set the delay between steps in verbose mode.")
    parser.add_argument("-s", "--style", choices=['fancy', 'compact', 'matrix'], default='fancy', help="Set the display style for verbose mode.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Run in quiet mode (only show the final result).")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode.")
    parser.add_argument("-l", "--log", action="store_true", help="Save execution log to file.")
    parser.add_argument("-b", "--batch", nargs='+', help="Run batch test on multiple strings.")
    
    args = parser.parse_args()

    # --- GUI Mode ---
    if args.gui:
        root = tk.Tk()
        app = TuringMachineGUI(root)
        root.mainloop()
        sys.exit(0)

    # --- CLI Mode ---
    if args.quiet: args.verbose = False
    tm = TuringMachine()
    
    if args.interactive:
        tm.interactive_mode()
        sys.exit(0)
    
    if args.batch:
        print(tm._get_ascii_art_header()); print(f"{Style.BRIGHT}BATCH PROCESSING MODE{Style.RESET_ALL}\n" + "═" * 60)
        for test_string in args.batch:
            result = tm.run(test_string, verbose=False, save_log=args.log)
            status = "✓" if "YES" in result else "✗"; color = Fore.GREEN if "YES" in result else Fore.RED
            print(f"{test_string:>10} → {color}{result:>8} {status}{Style.RESET_ALL}")
        sys.exit(0)
    
    test_string = args.input_string
    if test_string is None:
        print(tm._get_ascii_art_header())
        test_string = input(f"{Fore.CYAN}Enter a string to check for palindrome: {Style.RESET_ALL}")

    print(f"\n{Style.BRIGHT}Running simulation for '{test_string}'{Style.RESET_ALL}")
    if args.verbose: input(f"{Fore.YELLOW}Press Enter to start...{Style.RESET_ALL}")

    result = tm.run(test_string, verbose=args.verbose, delay=args.delay, style=args.style, save_log=args.log)
    
    final_message = f"\nFinal result for '{test_string}': "
    if "YES" in result: final_message += f"{Fore.GREEN}{result} ✓{Style.RESET_ALL}"
    elif "NO" in result: final_message += f"{Fore.RED}{result} ✗{Style.RESET_ALL}"
    else: final_message += f"{Fore.YELLOW}{result}{Style.RESET_ALL}"
    
    print(final_message); print("═" * 60)