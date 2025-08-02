#!/usr/bin/env python3
"""
Command Prompt - Main Entry Point
Windows Command Prompt written in Python
"""

import sys
import os
from command_processor import CommandProcessor
from utils import Utils

class CommandPrompt:
    def __init__(self):
        try:
            self.processor = CommandProcessor()
            self.utils = Utils()
            self.running = True
        except Exception as e:
            print(f"Error initializing command processor: {e}")
            print("Starting with basic functionality...")
            self.processor = self._create_basic_processor()
            self.utils = Utils()
            self.running = True
        
    def _create_basic_processor(self):
        """Create a basic command processor as fallback"""
        # Import specific commands instead of using import *
        from commands import (CDCommand, DirCommand, ClsCommand, EchoCommand, 
                            ExitCommand, HelpCommand, VerCommand, DateCommand, 
                            TimeCommand, CopyCommand, DelCommand, MkdirCommand, 
                            RmdirCommand, TypeCommand)
        
        class BasicCommandProcessor:
            def __init__(self):
                self.builtin_commands = {
                    'cd': CDCommand(), 'dir': DirCommand(), 'cls': ClsCommand(),
                    'echo': EchoCommand(), 'exit': ExitCommand(), 'help': HelpCommand(),
                    'ver': VerCommand(), 'date': DateCommand(), 'time': TimeCommand(),
                    'copy': CopyCommand(), 'del': DelCommand(), 'md': MkdirCommand(),
                    'rd': RmdirCommand(), 'type': TypeCommand()
                }
                self.env_vars = dict(os.environ)
            
            def process_command(self, command_line):
                parts = command_line.split()
                if not parts:
                    return
                
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if command in self.builtin_commands:
                    try:
                        return self.builtin_commands[command].execute(args)
                    except Exception as e:
                        print(f"Command failed: {e}")
                else:
                    print(f"'{command}' is not recognized as an internal or external command.")
        
        return BasicCommandProcessor()
        
    def display_banner(self):
        """Display the initial banner like real CMD"""
        print("Microsoft Windows [Version 10.0.26100.4061]")
        print("(c) Microsoft Corporation. All rights reserved.")
        print()
        
    def get_prompt(self):
        """Generate the command prompt string"""
        current_dir = os.getcwd()
        return f"{current_dir}>"
        
    def run(self):
        """Main command loop with enhanced input handling"""
        self.display_banner()
        
        # Get DOSKEY editor if available
        editor = None
        if hasattr(self.processor, 'doskey_components') and self.processor.doskey_components:
            editor = self.processor.doskey_components.get('editor')
        
        while self.running:
            try:
                # Display prompt and get user input
                prompt = self.get_prompt()
                
                if editor:
                    # Use enhanced input with DOSKEY support
                    try:
                        user_input = editor.get_input(prompt).strip()
                    except:
                        # Fallback to regular input if DOSKEY fails
                        user_input = input(prompt).strip()
                else:
                    # Fallback to regular input
                    user_input = input(prompt).strip()
                
                # Skip empty commands
                if not user_input:
                    continue
                
                # Check for exit command first
                if user_input.lower() in ['exit', 'quit']:
                    self.running = False
                    continue
                    
                # Process the command
                try:
                    result = self.processor.process_command(user_input)
                    
                    # Handle exit command
                    if result == "EXIT":
                        self.running = False
                except RecursionError:
                    print("Error: Command caused infinite recursion. Command ignored.")
                except Exception as e:
                    print(f"Error processing command: {e}")
                    
            except KeyboardInterrupt:
                print("^C")
                continue
            except EOFError:
                # Handle Ctrl+Z
                self.running = False
            except Exception as e:
                print(f"An error occurred: {e}")
                
        print("Goodbye!")

def main():
    """Entry point of the application"""
    try:
        cmd = CommandPrompt()
        cmd.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()