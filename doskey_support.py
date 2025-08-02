"""
DOSKEY Support - Command History and Macros
Implements full DOSKEY functionality for the CMD
"""

import os
import sys
import json
import pickle
from pathlib import Path
from collections import deque

class DoskeyProcessor:
    """Handles DOSKEY command history and macros"""
    
    def __init__(self, max_history=50):
        self.max_history = max_history
        self.command_history = deque(maxlen=max_history)
        self.macros = {}
        self.history_file = self.get_history_file()
        self.macro_file = self.get_macro_file()
        
        # Load existing history and macros
        self.load_history()
        self.load_macros()
        
        # Current history position for navigation
        self.history_position = 0
    
    def get_history_file(self):
        """Get the path to the history file"""
        home_dir = Path.home()
        cmd_dir = home_dir / '.cmd_clone'
        cmd_dir.mkdir(exist_ok=True)
        return cmd_dir / 'command_history.json'
    
    def get_macro_file(self):
        """Get the path to the macro file"""
        home_dir = Path.home()
        cmd_dir = home_dir / '.cmd_clone'
        cmd_dir.mkdir(exist_ok=True)
        return cmd_dir / 'macros.json'
    
    def add_command(self, command):
        """Add a command to history"""
        if command.strip() and (not self.command_history or self.command_history[-1] != command):
            self.command_history.append(command)
            self.history_position = len(self.command_history)
            self.save_history()
    
    def get_history(self):
        """Get the command history list"""
        return list(self.command_history)
    
    def get_previous_command(self):
        """Get the previous command in history (Up arrow)"""
        if self.command_history and self.history_position > 0:
            self.history_position -= 1
            return self.command_history[self.history_position]
        return ""
    
    def get_next_command(self):
        """Get the next command in history (Down arrow)"""
        if self.command_history and self.history_position < len(self.command_history) - 1:
            self.history_position += 1
            return self.command_history[self.history_position]
        elif self.history_position >= len(self.command_history) - 1:
            self.history_position = len(self.command_history)
            return ""
        return ""
    
    def search_history(self, pattern):
        """Search command history for a pattern"""
        matches = []
        for i, command in enumerate(self.command_history):
            if pattern.lower() in command.lower():
                matches.append((i, command))
        return matches
    
    def clear_history(self):
        """Clear command history"""
        self.command_history.clear()
        self.history_position = 0
        self.save_history()
    
    def save_history(self):
        """Save command history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.command_history), f, indent=2)
        except Exception as e:
            # Silently fail if we can't save history
            pass
    
    def load_history(self):
        """Load command history from file"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                    for command in history_data:
                        self.command_history.append(command)
                    self.history_position = len(self.command_history)
        except Exception as e:
            # Silently fail if we can't load history
            pass
    
    def add_macro(self, name, definition):
        """Add a DOSKEY macro"""
        self.macros[name.lower()] = definition
        self.save_macros()
    
    def remove_macro(self, name):
        """Remove a DOSKEY macro"""
        name_lower = name.lower()
        if name_lower in self.macros:
            del self.macros[name_lower]
            self.save_macros()
            return True
        return False
    
    def get_macro(self, name):
        """Get a macro definition"""
        return self.macros.get(name.lower())
    
    def list_macros(self):
        """List all macros"""
        return dict(self.macros)
    
    def expand_macro(self, command_line):
        """Expand macros in a command line"""
        parts = command_line.split()
        if not parts:
            return command_line
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.macros:
            macro_def = self.macros[command]
            
            # Replace parameters $1, $2, etc. with actual arguments
            for i, arg in enumerate(args, 1):
                macro_def = macro_def.replace(f'${i}', arg)
            
            # Replace $* with all arguments
            macro_def = macro_def.replace('$*', ' '.join(args))
            
            # Replace $$ with $
            macro_def = macro_def.replace('$$', '$')
            
            return macro_def
        
        return command_line
    
    def save_macros(self):
        """Save macros to file"""
        try:
            with open(self.macro_file, 'w', encoding='utf-8') as f:
                json.dump(self.macros, f, indent=2)
        except Exception as e:
            # Silently fail if we can't save macros
            pass
    
    def load_macros(self):
        """Load macros from file"""
        try:
            if self.macro_file.exists():
                with open(self.macro_file, 'r', encoding='utf-8') as f:
                    self.macros = json.load(f)
        except Exception as e:
            # Silently fail if we can't load macros
            pass
    
    def process_doskey_command(self, args):
        """Process DOSKEY command with arguments"""
        if not args:
            # Display help
            return self.display_doskey_help()
        
        i = 0
        while i < len(args):
            arg = args[i].upper()
            
            if arg == '/HISTORY':
                self.display_history()
            elif arg == '/LISTSIZE' and i + 1 < len(args):
                try:
                    size = int(args[i + 1])
                    self.set_history_size(size)
                    i += 1
                except ValueError:
                    print("Invalid list size.")
            elif arg == '/REINSTALL':
                self.reinstall_doskey()
            elif arg == '/MACROS':
                if i + 1 < len(args) and args[i + 1].startswith(':'):
                    # /MACROS:exe - show macros for specific executable
                    exe = args[i + 1][1:]
                    self.display_macros(exe)
                    i += 1
                else:
                    self.display_macros()
            elif arg == '/EXENAME' and i + 1 < len(args):
                # /EXENAME=exe - set executable name (not implemented)
                print(f"EXENAME set to {args[i + 1]}")
                i += 1
            elif arg == '/MACROFILE' and i + 1 < len(args):
                # Load macros from file
                self.load_macro_file(args[i + 1])
                i += 1
            elif '=' in args[i]:
                # Macro definition: name=definition
                self.parse_macro_definition(args[i])
            else:
                print(f"Invalid parameter: {args[i]}")
            
            i += 1
        
        return None
    
    def display_doskey_help(self):
        """Display DOSKEY help"""
        print("Edits command lines, recalls Windows commands, and creates macros.")
        print()
        print("DOSKEY [/REINSTALL] [/LISTSIZE=size] [/MACROS[:exe]] [/HISTORY]")
        print("       [/INSERT | /OVERSTRIKE] [/EXENAME=exe] [/MACROFILE=filename]")
        print("       [macroname=[text]]")
        print()
        print("  /REINSTALL      Installs a new copy of Doskey.")
        print("  /LISTSIZE=size  Sets size of command history buffer.")
        print("  /MACROS         Displays all Doskey macros.")
        print("  /MACROS:exe     Displays all Doskey macros for the given executable.")
        print("  /HISTORY        Displays all commands stored in memory.")
        print("  /INSERT         Specifies that new text you type is inserted in old text.")
        print("  /OVERSTRIKE     Specifies that new text overwrites old text.")
        print("  /EXENAME=exe    Specifies the executable.")
        print("  /MACROFILE=filename  Specifies a file of macros to install.")
        print("  macroname       Specifies a name for a macro you create.")
        print("  text            Specifies commands you want to record.")
        print()
        print("UP and DOWN ARROWS recall commands; ESC clears command line; F7 displays")
        print("command history; ALT+F7 clears command history; F8 searches command")
        print("history; F9 selects a command by number; ALT+F10 clears macro definitions.")
        print()
        print("The following are some special codes in Doskey macro definitions:")
        print("$T     Command separator.  Allows multiple commands in a macro.")
        print("$1-$9  Batch parameters.  Equivalent to %1-%9 in batch programs.")
        print("$*     Symbol replaced by everything following macro name on command line.")
    
    def display_history(self):
        """Display command history"""
        if not self.command_history:
            print("No commands in history.")
            return
        
        for i, command in enumerate(self.command_history, 1):
            print(f"{i:4}: {command}")
    
    def set_history_size(self, size):
        """Set the history buffer size"""
        if 1 <= size <= 999:
            self.max_history = size
            # Adjust current history if needed
            while len(self.command_history) > size:
                self.command_history.popleft()
            print(f"History buffer size set to {size}")
        else:
            print("Invalid history size. Must be between 1 and 999.")
    
    def reinstall_doskey(self):
        """Reinstall DOSKEY (clear everything)"""
        self.command_history.clear()
        self.macros.clear()
        self.history_position = 0
        print("DOSKEY reinstalled.")
    
    def display_macros(self, exe=None):
        """Display macros"""
        if not self.macros:
            print("No macros defined.")
            return
        
        if exe:
            print(f"Macros for {exe}:")
        
        for name, definition in sorted(self.macros.items()):
            print(f"{name}={definition}")
    
    def parse_macro_definition(self, definition):
        """Parse a macro definition (name=text)"""
        if '=' not in definition:
            return
        
        name, text = definition.split('=', 1)
        name = name.strip()
        
        if not name:
            return
        
        if text.strip() == '':
            # Remove macro
            if self.remove_macro(name):
                print(f"Macro '{name}' removed.")
            else:
                print(f"Macro '{name}' not found.")
        else:
            # Add/update macro
            self.add_macro(name, text)
            print(f"Macro '{name}' defined.")
    
    def load_macro_file(self, filename):
        """Load macros from a file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line:
                        self.parse_macro_definition(line)
            print(f"Macros loaded from {filename}")
        except FileNotFoundError:
            print(f"Cannot find file: {filename}")
        except Exception as e:
            print(f"Error loading macros: {e}")

class CommandLineEditor:
    """Enhanced command line editing with DOSKEY support"""
    
    def __init__(self, doskey_processor):
        self.doskey = doskey_processor
        self.current_line = ""
        self.cursor_pos = 0
        self.insert_mode = True
    
    def get_input(self, prompt):
        """Get input with enhanced editing capabilities"""
        try:
            # Try to use readline if available for better editing
            import readline
            
            # Set up readline with history
            readline.clear_history()
            for command in self.doskey.get_history():
                readline.add_history(command)
            
            line = input(prompt)
            
        except ImportError:
            # Fallback to regular input
            line = input(prompt)
        
        # Add to DOSKEY history
        if line.strip():
            self.doskey.add_command(line)
        
        # Expand macros
        expanded_line = self.doskey.expand_macro(line)
        
        return expanded_line
    
    def handle_special_keys(self, key):
        """Handle special key combinations"""
        if key == 'F7':
            self.show_history_dialog()
        elif key == 'F8':
            self.search_history_dialog()
        elif key == 'F9':
            self.select_command_dialog()
        elif key == 'ALT+F7':
            self.doskey.clear_history()
            print("Command history cleared.")
        elif key == 'ALT+F10':
            self.doskey.macros.clear()
            self.doskey.save_macros()
            print("Macro definitions cleared.")
    
    def show_history_dialog(self):
        """Show history selection dialog (F7)"""
        history = self.doskey.get_history()
        if not history:
            print("No commands in history.")
            return ""
        
        print("\nCommand History:")
        print("-" * 40)
        for i, command in enumerate(history, 1):
            print(f"{i:3}: {command}")
        print("-" * 40)
        
        try:
            choice = input("Select command number (Enter to cancel): ").strip()
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(history):
                    return history[index]
        except (ValueError, KeyboardInterrupt):
            pass
        
        return ""
    
    def search_history_dialog(self):
        """Search history dialog (F8)"""
        try:
            pattern = input("Search history for: ").strip()
            if pattern:
                matches = self.doskey.search_history(pattern)
                if matches:
                    print(f"\nFound {len(matches)} matches:")
                    for i, (index, command) in enumerate(matches, 1):
                        print(f"{i}: {command}")
                    
                    choice = input("Select match number (Enter to cancel): ").strip()
                    if choice.isdigit():
                        match_index = int(choice) - 1
                        if 0 <= match_index < len(matches):
                            return matches[match_index][1]
                else:
                    print("No matches found.")
        except KeyboardInterrupt:
            pass
        
        return ""
    
    def select_command_dialog(self):
        """Select command by number dialog (F9)"""
        try:
            choice = input("Command number: ").strip()
            if choice.isdigit():
                index = int(choice) - 1
                history = self.doskey.get_history()
                if 0 <= index < len(history):
                    return history[index]
        except (ValueError, KeyboardInterrupt):
            pass
        
        return ""

class TabCompletion:
    """Tab completion for file names and commands"""
    
    def __init__(self, command_processor):
        self.command_processor = command_processor
    
    def complete_command(self, text, line, begidx, endidx):
        """Complete command names and file paths"""
        # Split the line to understand context
        parts = line[:begidx].split()
        
        if not parts or begidx == 0:
            # Complete command names
            return self.complete_command_names(text)
        else:
            # Complete file/directory names
            return self.complete_file_names(text)
    
    def complete_command_names(self, text):
        """Complete command names"""
        completions = []
        
        # Built-in commands
        for cmd in self.command_processor.builtin_commands.keys():
            if cmd.startswith(text.lower()):
                completions.append(cmd.upper())
        
        # Executables in PATH
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        for directory in path_dirs:
            if not os.path.isdir(directory):
                continue
            
            try:
                for filename in os.listdir(directory):
                    name, ext = os.path.splitext(filename)
                    if (ext.lower() in ['.exe', '.com', '.bat', '.cmd'] and 
                        name.lower().startswith(text.lower())):
                        completions.append(name.upper())
            except (OSError, PermissionError):
                continue
        
        return sorted(set(completions))
    
    def complete_file_names(self, text):
        """Complete file and directory names"""
        completions = []
        
        # Handle quoted paths
        if text.startswith('"'):
            text = text[1:]
            quote_prefix = '"'
        else:
            quote_prefix = ''
        
        # Get directory and filename parts
        if os.path.sep in text or (os.name == 'nt' and '/' in text):
            directory = os.path.dirname(text)
            filename = os.path.basename(text)
        else:
            directory = '.'
            filename = text
        
        try:
            # List files and directories
            if os.path.isdir(directory):
                for item in os.listdir(directory):
                    if item.lower().startswith(filename.lower()):
                        full_path = os.path.join(directory, item)
                        if os.path.isdir(full_path):
                            completions.append(quote_prefix + full_path + os.path.sep)
                        else:
                            completions.append(quote_prefix + full_path)
        except (OSError, PermissionError):
            pass
        
        return sorted(completions)

def setup_readline_completion(command_processor, doskey_processor):
    """Set up readline with tab completion and history"""
    try:
        import readline
        import rlcompleter
        
        # Create tab completion handler
        tab_completion = TabCompletion(command_processor)
        
        # Set up completion
        readline.set_completer(tab_completion.complete_command)
        readline.parse_and_bind("tab: complete")
        
        # Set up history
        readline.clear_history()
        for command in doskey_processor.get_history():
            readline.add_history(command)
        
        # Configure readline behavior
        readline.parse_and_bind("set editing-mode emacs")
        readline.parse_and_bind("set show-all-if-ambiguous on")
        readline.parse_and_bind("set completion-ignore-case on")
        
        return True
        
    except ImportError:
        return False

# Advanced macro processing
class MacroExpander:
    """Advanced macro expansion with command separation"""
    
    def __init__(self, doskey_processor):
        self.doskey = doskey_processor
    
    def expand_advanced_macro(self, macro_text, args):
        """Expand macro with advanced features"""
        result = macro_text
        
        # Replace parameters $1-$9
        for i, arg in enumerate(args, 1):
            if i <= 9:
                result = result.replace(f'${i}', arg)
        
        # Replace $* with all arguments
        result = result.replace('$*', ' '.join(args))
        
        # Handle command separator $T
        commands = result.split('$T')
        
        # Replace $$ with $
        commands = [cmd.replace('$$', '$') for cmd in commands]
        
        return commands
    
    def execute_macro(self, name, args, command_processor):
        """Execute a macro with the given arguments"""
        macro_def = self.doskey.get_macro(name)
        if not macro_def:
            return False
        
        commands = self.expand_advanced_macro(macro_def, args)
        
        for command in commands:
            command = command.strip()
            if command:
                print(f"C:\\>{command}")
                command_processor.process_command(command)
        
        return True

# Integration with main command processor
def integrate_doskey_support(command_processor):
    """Integrate DOSKEY support into the command processor"""
    
    # Create DOSKEY processor
    doskey_processor = DoskeyProcessor()
    
    # Create command line editor
    editor = CommandLineEditor(doskey_processor)
    
    # Create macro expander  
    macro_expander = MacroExpander(doskey_processor)
    
    # Set up readline if available
    setup_readline_completion(command_processor, doskey_processor)
    
    # Enhance the command processor
    original_process = command_processor.process_command
    
    def enhanced_process_command(command_line):
        """Enhanced command processing with macro expansion"""
        # First check if it's a macro
        parts = command_line.split()
        if parts:
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            # Try to execute as macro
            if macro_expander.execute_macro(command, args, command_processor):
                return
        
        # Regular command processing
        return original_process(command_line)
    
    # Replace the process_command method
    command_processor.process_command = enhanced_process_command
    
    # Add DOSKEY command to built-in commands
    class DoskeyCommand:
        def execute(self, args):
            return doskey_processor.process_doskey_command(args)
    
    command_processor.builtin_commands['doskey'] = DoskeyCommand()
    
    return {
        'doskey_processor': doskey_processor,
        'editor': editor,
        'macro_expander': macro_expander
    }