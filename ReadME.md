# 🤖 Turing Machine Palindrome Checker (CLI + GUI)

A sophisticated, educational Turing Machine simulator that checks if strings from the alphabet {a, b} are palindromes. This enhanced version features a command-line interface with multiple visualization modes AND a user-friendly Graphical User Interface (GUI). It also includes interactive modes, batch processing, and comprehensive logging capabilities.

## 🎯 Features

### Core Functionality

  - **Dual Interface**: Run via an advanced **Command-Line Interface (CLI)** or an intuitive **Graphical User Interface (GUI)**.
  - **Palindrome Detection**: Determines if input strings are palindromes using formal Turing Machine logic.
  - **Educational Visualization**: Step-by-step execution showing state transitions, tape operations, and head movements.

### CLI Features

  - **Multiple Display Modes**: Choose from `fancy`, `matrix`, or `compact` visualization styles.
  - **Real-time Animation**: Watch the computation unfold with customizable delays.
  - **Interactive Mode**: A menu-driven interface for easy exploration from the terminal.
  - **Batch Processing**: Test multiple strings simultaneously.
  - **Execution Logging**: Save detailed JSON logs with complete execution traces.
  - **ASCII Art Interface**: A retro-futuristic visual design for the terminal.

### GUI Features

  - **Dynamic Tape Display**: A visual, animated tape that scrolls and stays centered on the head.
  - **Interactive Controls**: Run, reset, and adjust simulation speed with buttons and sliders.
  - **Real-Time Status**: Instantly see the current state and step count update live.

## 🚀 Quick Start

### Launch the GUI

For a user-friendly graphical experience, use the `--gui` flag.

```bash
python Turing.py --gui
```

### Basic CLI Usage

```bash
# Simple palindrome check
python Turing.py "abba"

# Verbose mode with step-by-step visualization
python Turing.py "abba" -v

# Different display styles
python Turing.py "abba" -v -s matrix
python Turing.py "abba" -v -s fancy
python Turing.py "abba" -v -s compact
```

### Interactive CLI Mode

```bash
# Launch interactive menu in the terminal
python Turing.py -i
```

### CLI Batch Processing

```bash
# Test multiple strings at once
python Turing.py -b "a" "aa" "aba" "abba" "abab"
```

## 💻 Graphical User Interface (GUI)

The GUI provides an easy-to-use, visual way to interact with the Turing Machine.

### GUI Features

  - **Dynamic Tape Visualization**: An animated tape that centers on the head and scrolls automatically during execution.
  - **Real-time Status Display**: The current state and step count are updated live as the simulation runs.
  - **Interactive Controls**: Buttons to `Run` and `Reset` the simulation.
  - **Speed Adjustment**: A slider allows you to control the animation speed from 10 to 500 milliseconds per step.
  - **Easy Input**: A simple text box to enter the string you want to test.

## 📋 Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--gui` | | Run the graphical user interface version. |
| `--verbose` | `-v` | Show step-by-step execution (CLI). |
| `--delay` | `-d` | Set animation delay in seconds (CLI). |
| `--style` | `-s` | Display style: `fancy`, `matrix`, `compact` (CLI). |
| `--quiet` | `-q` | Show only the final result (CLI). |
| `--interactive` | `-i` | Launch interactive mode (CLI). |
| `--log` | `-l` | Save execution log to a JSON file. |
| `--batch` | `-b` | Process multiple strings in batch mode (CLI). |

## 🎨 CLI Display Styles

### Fancy Mode (`-s fancy`)

  - ASCII art header with retro styling and progress bar.
  - Clear state transition information and color-coded tape with a head pointer.

### Matrix Mode (`-s matrix`)

  - A futuristic grid-based layout with a system status panel and transition preview.

### Compact Mode (`-s compact`)

  - A minimal, single-line display perfect for batch operations or small terminals.

## 🔧 Installation & Requirements

### Dependencies

The CLI requires `colorama`. The GUI requires `tkinter`.

```bash
pip install colorama
```

### Python Version

  - Python 3.6 or higher.

### `tkinter` Installation (If Needed)

`tkinter` is included with most Python installations on Windows and macOS. On some Linux distributions, you may need to install it separately.

**For Debian/Ubuntu:**

```bash
sudo apt-get install python3-tk
```

**For Fedora:**

```bash
sudo dnf install python3-tkinter
```

## 📖 How It Works

### Turing Machine States

  - **q0**: Initial state - reads the first character.
  - **q1, q2**: Scanning states after reading an 'a' or 'b'.
  - **q3, q4**: End-checking states expecting matching characters.
  - **q5**: Return-to-start state.
  - **q\_yes/q\_no**: Accept/reject states.
  - **qy1-qy3, qn1-qn2**: States for writing the final "YES" or "NO" on the tape.

### Algorithm Overview

1.  **Read** the leftmost unprocessed character and mark it as processed (write a blank).
2.  **Scan** right to find the rightmost unprocessed character.
3.  **Compare** the characters. If they match, continue; if not, reject.
4.  **Return** to the leftmost unprocessed character and repeat.
5.  **Accept** if all character pairs match, otherwise **reject**.

## 🎮 Interactive Mode (CLI)

The interactive command-line mode provides a simple menu for users not familiar with CLI flags.

### Main Menu Options

1.  **Check Palindrome**: Analyze a single string with full visualization options.
2.  **Batch Test**: Run a set of predefined test cases.
3.  **Exit**: Terminate the program.

## 📊 Example CLI Session

### Verbose Palindrome Check

```bash
$ python Turing.py "aba" -v

╔══════════════════════════════════════════════════════════╗
║                    TURING MACHINE                        ║
║                 PALINDROME ANALYZER                      ║
║                    v3.0 (CLI+GUI)                      ║
╚══════════════════════════════════════════════════════════╝
Progress: [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0.0%
Current State: q0           Step:      0
Reading Symbol: 'a' at position 0
Next Action: Write 'B', Move R, Go to q1
════════════════════════════════════════════════════════════════════════════════
 [a]  b   a 
  ↑   
════════════════════════════════════════════════════════════════════════════════
```

## 📁 File Outputs

### Execution Logs

When using the `-l` flag, a detailed JSON log is saved.

```json
{
  "timestamp": "2025-06-26T19:14:00.123456",
  "input_string": "aba",
  "total_steps": 25,
  "execution_time": 0.123,
  "final_result": "YES",
  "execution_log": [
    {
      "step": 0,
      "state": "q0",
      "position": 0,
      "read": "a",
      "write": "B",
      "move": "R",
      "new_state": "q1"
    }
    // ... more steps
  ]
}
```

## 🐛 Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| **GUI won't start** | Missing `tkinter` package | Install `python3-tk` (or equivalent) for your OS. See Installation section. |
| **Colors not displaying** | Terminal doesn't support ANSI | Use the GUI or the `--style compact` in the CLI. |
| **Animation too fast/slow** | Default delay isn't suitable | In CLI, use `-d <seconds>`. In GUI, use the speed slider. |
| **Import errors** | Missing dependencies | Run `pip install colorama`. |

## 🤝 Contributing

Feature requests and contributions are welcome\! Please feel free to fork the repository, make changes, and submit a pull request.

## 📄 License

This project is released under the MIT License. Feel free to use, modify, and distribute it for educational or personal purposes.

## 🙏 Acknowledgments

  - Alan Turing for the theoretical foundation of modern computing.
  - The open-source community for providing the tools and inspiration.

-----

**Happy Computing\!** 🎉

*"We can only see a short distance ahead, but we can see plenty there that needs to be done."* - Alan Turing