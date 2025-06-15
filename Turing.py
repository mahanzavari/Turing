import time
import os

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
        # Machine's dynamic state
        self.tape = {}
        self.head_position = 0
        self.current_state = 'q0'
        self.step_count = 0

    def _display_tape(self, tape_width=40):
        """Helper function to print the current state of the tape."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Determine the range of the tape to display
        tape_indices = sorted(self.tape.keys())
        min_idx = min(tape_indices) if tape_indices else 0
        max_idx = max(tape_indices) if tape_indices else 0
        start = min(self.head_position - tape_width // 2, min_idx - 2)
        end = max(self.head_position + tape_width // 2, max_idx + 2)

        # Build tape string
        tape_str = ""
        head_str = ""
        for i in range(start, end + 1):
            symbol = self.tape.get(i, self.blank_symbol)
            tape_str += f" {symbol} "
            if i == self.head_position:
                head_str += " ^ "
            else:
                head_str += "   "
        
        print(f"State: {self.current_state:<10} Step: {self.step_count}")
        print("-" * (len(tape_str)))
        print(tape_str)
        print(head_str)
        print("-" * (len(tape_str)))

    def run(self, input_string, verbose=False, delay=0.1):
        """
        Runs the Turing Machine on a given input string.

        Args:
            input_string (str): The string to process.
            verbose (bool): If True, prints the state of the machine at each step.
            delay (float): Delay in seconds between steps when verbose is True.
        
        Returns:
            str: The final content of the tape after halting.
        """
        # --- 1. Initialization ---
        # Validate input
        if not all(c in 'ab' for c in input_string):
            return "Error: Input string contains invalid characters."

        # Reset machine state for a new run
        self.tape = {i: char for i, char in enumerate(input_string)}
        self.head_position = 0
        self.current_state = 'q0'
        self.step_count = 0

        if verbose:
            self._display_tape()
            time.sleep(delay)

        # --- 2. Execution Loop ---
        while self.current_state != self.halt_state:
            # Read the symbol under the tape head
            read_symbol = self.tape.get(self.head_position, self.blank_symbol)

            # Find the transition rule for the current state and symbol
            if self.current_state not in self.transitions or read_symbol not in self.transitions[self.current_state]:
                print(f"Error: No transition for state '{self.current_state}' and symbol '{read_symbol}'")
                break
            
            rule = self.transitions[self.current_state][read_symbol]
            
            # --- 3. Apply Transition Rule ---
            # Write the new symbol to the tape
            self.tape[self.head_position] = rule['write']
            
            # Move the head
            if rule['move'] == 'R':
                self.head_position += 1
            elif rule['move'] == 'L':
                self.head_position -= 1
            # 'S' (Stay) means no change in head position
            
            # Update the current state
            self.current_state = rule['newState']
            self.step_count += 1

            if verbose:
                self._display_tape()
                time.sleep(delay)

        # --- 4. Final Result ---
        # Sort keys to read the tape in order
        sorted_keys = sorted(self.tape.keys())
        final_tape_content = "".join(self.tape[key] for key in sorted_keys if self.tape[key] != self.blank_symbol)
        
        return final_tape_content

# --- Main execution block ---
if __name__ == "__main__":
    tm = TuringMachine()
    
    # Get a single string from the user to test
    test_string = input("Enter a string to check for palindrome (e.g., abba or ababa): ")
    
    # --- Run with detailed verbose output for the user's string ---
    print(f"\n--- Running detailed simulation for '{test_string}' ---")
    input("Press Enter to start...")
    result_verbose = tm.run(test_string, verbose=True, delay=0.2)
    print(f"\nFinal tape content for '{test_string}': {result_verbose}\n")
    print("-" * 40)
