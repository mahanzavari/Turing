import time
import os
import argparse
import json
from datetime import datetime
from colorama import Fore, Style, init
import threading
import sys

# Initialize colorama
init(autoreset=True)

class TuringMachine:
    """
    A class to simulate a Turing Machine for palindrome checking.
    The machine checks if a string from the alphabet {a, b} is a palindrome.
    """

    def __init__(self):
        """
        Initializes the Turing Machine with its states and transition function.
        """
        self.blank_symbol = 'B'
        self.halt_state = 'q_halt'
        # The transition function is defined as a dictionary.
        # Format: { 'state': { 'read_symbol': { 'newState': ..., 'write': ..., 'move': ... } } }
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
                'b': {'newState': 'q_no', 'write': self.blank_symbol, 'move': 'L'},
                self.blank_symbol: {'newState': 'q_yes', 'write': self.blank_symbol, 'move': 'L'}
            },
            'q4': { # Expect 'b' at the end
                'b': {'newState': 'q5', 'write': self.blank_symbol, 'move': 'L'},
                'a': {'newState': 'q_no', 'write': self.blank_symbol, 'move': 'L'},
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
        # Machine's dynamic state
        self.tape = {}
        self.head_position = 0
        self.current_state = 'q0'
        self.step_count = 0
        self.execution_log = []
        self.start_time = None
        self.animation_running = False

    def _animate_loading(self, message="Computing"):
        """Animated loading spinner"""
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        while self.animation_running:
            for char in chars:
                if not self.animation_running:
                    break
                sys.stdout.write(f'\r{Fore.CYAN}{char} {message}...{Style.RESET_ALL}')
                sys.stdout.flush()
                time.sleep(0.1)

    def _get_ascii_art_header(self):
        """Returns cool ASCII art header"""
        return f"""{Style.BRIGHT}{Fore.MAGENTA}
╔══════════════════════════════════════════════════════════╗
║                    TURING MACHINE                        ║
║                 PALINDROME ANALYZER                      ║
║                      v2.0 ENHANCED                      ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""

    def _display_tape_matrix(self, tape_width=50):
        """Futuristic matrix-style display"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(self._get_ascii_art_header())
        
        tape_indices = sorted(self.tape.keys()) if self.tape else [0]
        min_idx = min(tape_indices)
        max_idx = max(tape_indices)
        
        start = min(self.head_position - tape_width // 2, min_idx - 5)
        end = max(self.head_position + tape_width // 2, max_idx + 5)

        # Current read symbol and next action
        read_symbol = self.tape.get(self.head_position, self.blank_symbol)
        next_action = "HALT"
        if (self.current_state in self.transitions and 
            read_symbol in self.transitions[self.current_state]):
            rule = self.transitions[self.current_state][read_symbol]
            next_action = f"Write: {rule['write']}, Move: {rule['move']}, → {rule['newState']}"

        # State info box
        print(f"┌─ SYSTEM STATUS ─────────────────────────────────────────┐")
        print(f"│ Current State: {Fore.GREEN}{self.current_state:<15}{Style.RESET_ALL} Step: {Fore.YELLOW}{self.step_count:>8}{Style.RESET_ALL} │")
        print(f"│ Head Position: {Fore.CYAN}{self.head_position:<15}{Style.RESET_ALL} Time: {Fore.MAGENTA}{time.time() - self.start_time:.2f}s{Style.RESET_ALL} │")
        print(f"│ Reading: {Fore.YELLOW}{read_symbol:<20}{Style.RESET_ALL}                      │")
        print(f"└────────────────────────────────────────────────────────┘")
        print(f"┌─ NEXT TRANSITION ───────────────────────────────────────┐")
        print(f"│ {Fore.CYAN}{next_action:<56}{Style.RESET_ALL} │")
        print(f"└────────────────────────────────────────────────────────┘")
        
        # Tape display with grid
        print("┌─ TAPE CONTENTS ─────────────────────────────────────────┐")
        
        # Position numbers
        pos_str = "│ "
        for i in range(start, end + 1):
            if i == self.head_position:
                pos_str += f"{Fore.RED}{i:2d}{Style.RESET_ALL}"
            else:
                pos_str += f"{i:2d}"
        print(pos_str + " │")
        
        # Tape symbols
        tape_str = "│ "
        for i in range(start, end + 1):
            symbol = self.tape.get(i, self.blank_symbol)
            if i == self.head_position:
                tape_str += f"{Style.BRIGHT}{Fore.RED}[{symbol}]{Style.RESET_ALL}"
            else:
                if symbol == self.blank_symbol:
                    tape_str += f"{Fore.WHITE}·{Style.RESET_ALL} "
                else:
                    tape_str += f"{Fore.CYAN}{symbol}{Style.RESET_ALL} "
        print(tape_str + " │")
        
        print("└────────────────────────────────────────────────────────┘")

    def _display_tape_fancy(self, tape_width=40):
        """Enhanced fancy display with more visual elements"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(self._get_ascii_art_header())
        
        tape_indices = sorted(self.tape.keys()) if self.tape else [0]
        min_idx = min(tape_indices)
        max_idx = max(tape_indices)
        
        start = min(self.head_position - tape_width // 2, min_idx - 5)
        end = max(self.head_position + tape_width // 2, max_idx + 5)

        # Current read symbol and next action
        read_symbol = self.tape.get(self.head_position, self.blank_symbol)
        next_action = "HALT - No more transitions"
        if (self.current_state in self.transitions and 
            read_symbol in self.transitions[self.current_state]):
            rule = self.transitions[self.current_state][read_symbol]
            next_action = f"Write '{rule['write']}', Move {rule['move']}, Go to {rule['newState']}"

        # Progress bar
        if hasattr(self, 'input_length') and self.input_length > 0:
            progress = min(100, (self.step_count / (self.input_length * 10)) * 100)
            filled = int(progress / 2)
            bar = "█" * filled + "░" * (50 - filled)
            print(f"Progress: {Fore.CYAN}[{bar}]{Style.RESET_ALL} {progress:.1f}%")
        
        # State and transition info
        print(f"Current State: {Fore.YELLOW}{self.current_state:<12}{Style.RESET_ALL} Step: {Fore.YELLOW}{self.step_count:>6}{Style.RESET_ALL}")
        print(f"Reading Symbol: {Fore.CYAN}'{read_symbol}'{Style.RESET_ALL} at position {Fore.CYAN}{self.head_position}{Style.RESET_ALL}")
        print(f"Next Action: {Fore.GREEN}{next_action}{Style.RESET_ALL}")
        print("═" * 80)
        
        tape_str = ""
        head_str = ""
        for i in range(start, end + 1):
            symbol = self.tape.get(i, self.blank_symbol)
            if i == self.head_position:
                tape_str += f"{Style.BRIGHT}{Fore.RED}[{symbol}]{Style.RESET_ALL}"
                head_str += f"{Fore.RED} ↑ "
            else:
                if symbol == self.blank_symbol:
                    tape_str += f"{Fore.WHITE} · {Style.RESET_ALL}"
                else:
                    tape_str += f"{Fore.CYAN} {symbol} {Style.RESET_ALL}"
                head_str += "   "
        
        print(tape_str)
        print(head_str)
        print("═" * 80)

    def _display_tape_compact(self):
        """Enhanced compact display with state transition info"""
        tape_content = []
        if self.tape:
            min_key = min(self.tape.keys())
            max_key = max(self.tape.keys())
            for i in range(min_key, max_key + 1):
                tape_content.append(self.tape.get(i, self.blank_symbol))
        
        tape_str = "".join(tape_content) if tape_content else self.blank_symbol
        
        # Create visual head pointer
        head_indicator = ""
        if self.tape:
            head_pos_relative = self.head_position - min(self.tape.keys())
            head_indicator = " " * head_pos_relative + f"{Fore.RED}↑{Style.RESET_ALL}"
        
        # Get current symbol and next action
        read_symbol = self.tape.get(self.head_position, self.blank_symbol)
        next_action = "HALT"
        if (self.current_state in self.transitions and 
            read_symbol in self.transitions[self.current_state]):
            rule = self.transitions[self.current_state][read_symbol]
            next_action = f"R:{read_symbol}→W:{rule['write']},{rule['move']},{rule['newState']}"

        print(f"\r{Fore.MAGENTA}Step {self.step_count:4d}{Style.RESET_ALL} │ "
              f"{Fore.YELLOW}{self.current_state:8}{Style.RESET_ALL} │ "
              f"{Fore.CYAN}{tape_str}{Style.RESET_ALL}")
        print(f"         │          │ {head_indicator}")
        print(f"         │ {Fore.GREEN}{next_action:<20}{Style.RESET_ALL}")
        print("─" * 50)

    def save_execution_log(self, filename=None):
        """Save execution log to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"turing_log_{timestamp}.json"
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "input_string": getattr(self, 'original_input', ''),
            "total_steps": self.step_count,
            "execution_time": time.time() - self.start_time if self.start_time else 0,
            "final_result": self.get_tape_content(),
            "execution_log": self.execution_log[-100:]  # Keep last 100 steps
        }
        
        with open(filename, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"{Fore.GREEN}Execution log saved to: {filename}{Style.RESET_ALL}")

    def get_tape_content(self):
        """Get current tape content as string"""
        if not self.tape:
            return ""
        sorted_keys = sorted(self.tape.keys())
        return "".join(self.tape[key] for key in sorted_keys if self.tape[key] != self.blank_symbol)

    def run(self, input_string, verbose=False, delay=0.1, style='fancy', save_log=False):
        """
        Runs the Turing Machine on a given input string with enhanced features.
        """
        # --- 1. Initialization ---
        if not all(c in 'ab' for c in input_string):
            return f"{Fore.RED}Error: Input string contains invalid characters."

        self.original_input = input_string
        self.input_length = len(input_string)
        self.tape = {i: char for i, char in enumerate(input_string)}
        self.head_position = 0
        self.current_state = 'q0'
        self.step_count = 0
        self.execution_log = []
        self.start_time = time.time()

        # Cool startup animation
        if verbose and style != 'compact':
            self.animation_running = True
            spinner_thread = threading.Thread(target=self._animate_loading, args=("Initializing Turing Machine",))
            spinner_thread.start()
            time.sleep(2)
            self.animation_running = False
            spinner_thread.join()
            print(f"\r{' ' * 50}\r", end="")

        if verbose:
            if style == 'matrix':
                self._display_tape_matrix()
            elif style == 'fancy':
                self._display_tape_fancy()
            elif style == 'compact':
                print(f"\n{Fore.CYAN}Starting computation...{Style.RESET_ALL}")
            time.sleep(delay)

        # --- 2. Execution Loop ---
        while self.current_state != self.halt_state:
            read_symbol = self.tape.get(self.head_position, self.blank_symbol)

            # Log the step
            step_info = {
                'step': self.step_count,
                'state': self.current_state,
                'position': self.head_position,
                'read': read_symbol,
                'tape_snapshot': dict(self.tape)
            }

            if self.current_state not in self.transitions or read_symbol not in self.transitions[self.current_state]:
                error_msg = f"\n{Fore.RED}Error: No transition for state '{self.current_state}' and symbol '{read_symbol}'{Style.RESET_ALL}"
                print(error_msg)
                if save_log:
                    self.save_execution_log()
                return error_msg
            
            rule = self.transitions[self.current_state][read_symbol]
            
            # Add transition info to log
            step_info.update({
                'write': rule['write'],
                'move': rule['move'],
                'new_state': rule['newState']
            })
            self.execution_log.append(step_info)
            
            self.tape[self.head_position] = rule['write']
            
            if rule['move'] == 'R':
                self.head_position += 1
            elif rule['move'] == 'L':
                self.head_position -= 1
            
            self.current_state = rule['newState']
            self.step_count += 1

            if verbose:
                if style == 'matrix':
                    self._display_tape_matrix()
                elif style == 'fancy':
                    self._display_tape_fancy()
                elif style == 'compact':
                    self._display_tape_compact()
                time.sleep(delay)

        # --- 3. Final Result ---
        execution_time = time.time() - self.start_time
        final_content = self.get_tape_content()
        
        if save_log:
            self.save_execution_log()
        
        # Cool completion animation
        if verbose and style != 'compact':
            print(f"\n{Fore.GREEN}{'='*20} COMPUTATION COMPLETE {'='*20}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Execution time: {execution_time:.3f} seconds{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Total steps: {self.step_count}{Style.RESET_ALL}")
        
        return final_content

    def interactive_mode(self):
        """Enhanced interactive mode with menu"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(self._get_ascii_art_header())
            print(f"{Style.BRIGHT}INTERACTIVE MODE{Style.RESET_ALL}")
            print("═" * 50)
            print("1. Check palindrome")
            print("2. Batch test")
            print("3. View execution stats")
            print("4. Export logs")
            print("5. Exit")
            print("═" * 50)
            
            choice = input(f"{Fore.YELLOW}Select option (1-5): {Style.RESET_ALL}")
            
            if choice == '1':
                test_string = input(f"{Fore.CYAN}Enter string to test: {Style.RESET_ALL}")
                style = input(f"{Fore.CYAN}Display style (fancy/matrix/compact): {Style.RESET_ALL}") or 'fancy'
                delay = float(input(f"{Fore.CYAN}Animation delay (seconds): {Style.RESET_ALL}") or "0.2")
                
                result = self.run(test_string, verbose=True, delay=delay, style=style, save_log=True)
                
                final_message = f"\nResult for '{test_string}': "
                if "YES" in result:
                    final_message += f"{Fore.GREEN}{result} ✓{Style.RESET_ALL}"
                elif "NO" in result:
                    final_message += f"{Fore.RED}{result} ✗{Style.RESET_ALL}"
                else:
                    final_message += f"{Fore.YELLOW}{result}{Style.RESET_ALL}"
                
                print(final_message)
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                
            elif choice == '2':
                test_cases = ["a", "aa", "ab", "aba", "abba", "abab", "aabaa", "abcba"]
                print(f"{Fore.CYAN}Running batch test...{Style.RESET_ALL}")
                for test in test_cases:
                    result = self.run(test, verbose=False)
                    status = "✓" if "YES" in result else "✗"
                    color = Fore.GREEN if "YES" in result else Fore.RED
                    print(f"{test:>8} → {color}{result} {status}{Style.RESET_ALL}")
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                
            elif choice == '5':
                print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
                break

# --- Main execution block ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enhanced Turing Machine simulator for checking palindromes.")
    parser.add_argument("input_string", nargs='?', default=None, help="The string to check for palindrome (e.g., abba).")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode to see each step of the simulation.")
    parser.add_argument("-d", "--delay", type=float, default=0.2, help="Set the delay between steps in verbose mode.")
    parser.add_argument("-s", "--style", choices=['fancy', 'compact', 'matrix'], default='fancy', help="Set the display style for verbose mode.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Run in quiet mode (only show the final result).")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode.")
    parser.add_argument("-l", "--log", action="store_true", help="Save execution log to file.")
    parser.add_argument("-b", "--batch", nargs='+', help="Run batch test on multiple strings.")
    
    args = parser.parse_args()

    # If verbose is on, quiet is ignored.
    if args.quiet:
        args.verbose = False
    
    tm = TuringMachine()
    
    if args.interactive:
        tm.interactive_mode()
        sys.exit(0)
    
    if args.batch:
        print(f"{tm._get_ascii_art_header()}")
        print(f"{Style.BRIGHT}BATCH PROCESSING MODE{Style.RESET_ALL}")
        print("═" * 60)
        for test_string in args.batch:
            result = tm.run(test_string, verbose=False, save_log=args.log)
            status = "✓" if "YES" in result else "✗"
            color = Fore.GREEN if "YES" in result else Fore.RED
            print(f"{test_string:>10} → {color}{result:>8} {status}{Style.RESET_ALL}")
        sys.exit(0)
    
    test_string = args.input_string
    if test_string is None:
        print(tm._get_ascii_art_header())
        test_string = input(f"{Fore.CYAN}Enter a string to check for palindrome: {Style.RESET_ALL}")

    print(f"\n{Style.BRIGHT}Running simulation for '{test_string}'{Style.RESET_ALL}")
    if args.verbose:
        input(f"{Fore.YELLOW}Press Enter to start...{Style.RESET_ALL}")

    result = tm.run(test_string, verbose=args.verbose, delay=args.delay, style=args.style, save_log=args.log)
    
    final_message = f"\nFinal result for '{test_string}': "
    if "YES" in result:
        final_message += f"{Fore.GREEN}{result} ✓{Style.RESET_ALL}"
    elif "NO" in result:
        final_message += f"{Fore.RED}{result} ✗{Style.RESET_ALL}"
    else:
        final_message += f"{Fore.YELLOW}{result}{Style.RESET_ALL}"
        
    print(final_message)
    print("═" * 60)