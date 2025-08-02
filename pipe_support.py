"""
Pipeline Support for Command Prompt Clone
Handles command piping (|) and advanced redirection
"""

import os
import sys
import subprocess
import tempfile
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

class PipelineProcessor:
    """Processes command pipelines and redirection"""
    
    def __init__(self, command_processor):
        self.command_processor = command_processor
    
    def process_pipeline(self, command_line):
        """Process a command pipeline (commands separated by |)"""
        # Split by pipe character
        commands = [cmd.strip() for cmd in command_line.split('|')]
        
        if len(commands) == 1:
            # No pipe, process normally
            return self.command_processor.process_command(commands[0])
        
        # Process pipeline
        return self.execute_pipeline(commands)
    
    def execute_pipeline(self, commands):
        """Execute a series of piped commands"""
        current_input = None
        
        for i, command in enumerate(commands):
            if i == 0:
                # First command - capture its output
                current_input = self.capture_command_output(command)
            elif i == len(commands) - 1:
                # Last command - use input from previous command
                self.execute_command_with_input(command, current_input)
            else:
                # Middle command - take input and produce output
                current_input = self.capture_command_output_with_input(command, current_input)
    
    def capture_command_output(self, command):
        """Capture the output of a command"""
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            self.command_processor.process_command(command)
            output = captured_output.getvalue()
        finally:
            sys.stdout = old_stdout
        
        return output
    
    def capture_command_output_with_input(self, command, input_text):
        """Capture command output while providing input"""
        old_stdout = sys.stdout
        old_stdin = sys.stdin
        
        sys.stdout = captured_output = StringIO()
        sys.stdin = StringIO(input_text)
        
        try:
            self.command_processor.process_command(command)
            output = captured_output.getvalue()
        finally:
            sys.stdout = old_stdout
            sys.stdin = old_stdin
        
        return output
    
    def execute_command_with_input(self, command, input_text):
        """Execute a command with provided input"""
        old_stdin = sys.stdin
        sys.stdin = StringIO(input_text)
        
        try:
            self.command_processor.process_command(command)
        finally:
            sys.stdin = old_stdin

class RedirectionProcessor:
    """Handles advanced redirection operations"""
    
    def __init__(self, command_processor):
        self.command_processor = command_processor
    
    def process_redirection(self, command_line):
        """Process command with redirection"""
        # Handle different types of redirection
        if '>>' in command_line:
            return self.handle_append_redirect(command_line)
        elif '>' in command_line:
            return self.handle_output_redirect(command_line)
        elif '<' in command_line:
            return self.handle_input_redirect(command_line)
        elif '2>' in command_line:
            return self.handle_error_redirect(command_line)
        elif '2>&1' in command_line:
            return self.handle_combined_redirect(command_line)
        else:
            return self.command_processor.process_command(command_line)
    
    def handle_output_redirect(self, command_line):
        """Handle output redirection (>)"""
        parts = command_line.split('>', 1)
        if len(parts) != 2:
            return self.command_processor.process_command(command_line)
        
        command = parts[0].strip()
        output_file = parts[1].strip()
        
        # Capture command output
        old_stdout = sys.stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            self.command_processor.process_command(command)
            output = captured_output.getvalue()
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
                
        except Exception as e:
            print(f"Redirection failed: {e}")
        finally:
            sys.stdout = old_stdout
    
    def handle_append_redirect(self, command_line):
        """Handle append redirection (>>)"""
        parts = command_line.split('>>', 1)
        if len(parts) != 2:
            return self.command_processor.process_command(command_line)
        
        command = parts[0].strip()
        output_file = parts[1].strip()
        
        # Capture command output
        old_stdout = sys.stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            self.command_processor.process_command(command)
            output = captured_output.getvalue()
            
            # Append to file
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(output)
                
        except Exception as e:
            print(f"Redirection failed: {e}")
        finally:
            sys.stdout = old_stdout
    
    def handle_input_redirect(self, command_line):
        """Handle input redirection (<)"""
        parts = command_line.split('<', 1)
        if len(parts) != 2:
            return self.command_processor.process_command(command_line)
        
        command = parts[0].strip()
        input_file = parts[1].strip()
        
        try:
            # Read input file
            with open(input_file, 'r', encoding='utf-8') as f:
                input_content = f.read()
            
            # Provide input to command
            old_stdin = sys.stdin
            sys.stdin = StringIO(input_content)
            
            try:
                self.command_processor.process_command(command)
            finally:
                sys.stdin = old_stdin
                
        except FileNotFoundError:
            print(f"The system cannot find the file {input_file}.")
        except Exception as e:
            print(f"Input redirection failed: {e}")
    
    def handle_error_redirect(self, command_line):
        """Handle error redirection (2>)"""
        parts = command_line.split('2>', 1)
        if len(parts) != 2:
            return self.command_processor.process_command(command_line)
        
        command = parts[0].strip()
        error_file = parts[1].strip()
        
        # Capture command stderr
        old_stderr = sys.stderr
        captured_error = StringIO()
        sys.stderr = captured_error
        
        try:
            self.command_processor.process_command(command)
            error_output = captured_error.getvalue()
            
            # Write errors to file
            if error_output:
                with open(error_file, 'w', encoding='utf-8') as f:
                    f.write(error_output)
                    
        except Exception as e:
            print(f"Error redirection failed: {e}")
        finally:
            sys.stderr = old_stderr
    
    def handle_combined_redirect(self, command_line):
        """Handle combined stdout/stderr redirection (2>&1)"""
        parts = command_line.split('2>&1', 1)
        if len(parts) != 2:
            return self.command_processor.process_command(command_line)
        
        command = parts[0].strip()
        
        # Capture both stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        captured_output = StringIO()
        sys.stdout = captured_output
        sys.stderr = captured_output
        
        try:
            self.command_processor.process_command(command)
            combined_output = captured_output.getvalue()
            print(combined_output, end='')
            
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

class AdvancedCommandProcessor:
    """Enhanced command processor with full pipeline and redirection support"""
    
    def __init__(self, base_processor):
        self.base_processor = base_processor
        self.pipeline_processor = PipelineProcessor(base_processor)
        self.redirection_processor = RedirectionProcessor(base_processor)
    
    def process_command(self, command_line):
        """Process command with full pipeline and redirection support"""
        # Check for pipes first
        if '|' in command_line:
            return self.pipeline_processor.process_pipeline(command_line)
        
        # Check for redirection
        if any(redirect in command_line for redirect in ['>', '<', '2>', '2>&1']):
            return self.redirection_processor.process_redirection(command_line)
        
        # Regular command processing
        return self.base_processor.process_command(command_line)

class FilterCommands:
    """Built-in filter commands for pipeline processing"""
    
    @staticmethod
    def more_filter(input_text):
        """Implement MORE command functionality"""
        lines = input_text.split('\n')
        
        for i, line in enumerate(lines):
            print(line)
            
            # Pause every 24 lines (typical screen height)
            if (i + 1) % 24 == 0 and i < len(lines) - 1:
                try:
                    response = input("-- More --")
                    if response.lower() == 'q':
                        break
                except KeyboardInterrupt:
                    break
    
    @staticmethod
    def sort_filter(input_text, reverse=False):
        """Implement SORT command functionality"""
        lines = input_text.strip().split('\n')
        sorted_lines = sorted(lines, reverse=reverse)
        
        for line in sorted_lines:
            print(line)
    
    @staticmethod
    def find_filter(input_text, search_string, case_sensitive=True):
        """Implement FIND command functionality"""
        lines = input_text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if case_sensitive:
                if search_string in line:
                    print(f"---------- STDIN: {line_num}")
                    print(line)
            else:
                if search_string.lower() in line.lower():
                    print(f"---------- STDIN: {line_num}")
                    print(line)
    
    @staticmethod
    def findstr_filter(input_text, pattern, options=None):
        """Implement FINDSTR command functionality"""
        import re
        
        lines = input_text.split('\n')
        flags = 0
        
        if options:
            if '/I' in options:  # Case insensitive
                flags |= re.IGNORECASE
            if '/R' in options:  # Regular expression
                pass  # Default behavior
            if '/L' in options:  # Literal string
                pattern = re.escape(pattern)
        
        try:
            regex = re.compile(pattern, flags)
            
            for line_num, line in enumerate(lines, 1):
                if regex.search(line):
                    if '/N' in (options or []):
                        print(f"{line_num}:{line}")
                    else:
                        print(line)
                        
        except re.error as e:
            print(f"FINDSTR: Invalid regular expression: {e}")

# Enhanced command implementations that work with pipes
class PipeAwareCommands:
    """Commands that can handle piped input"""
    
    @staticmethod
    def dir_command_with_pipe():
        """DIR command that can be piped"""
        # This would be integrated with the main DIR command
        pass
    
    @staticmethod
    def type_command_with_pipe(filename=None):
        """TYPE command that can handle stdin"""
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read()
            except FileNotFoundError:
                print("The system cannot find the file specified.")
                return ""
        else:
            # Read from stdin if no filename provided
            return sys.stdin.read()

# Integration helper
def integrate_pipeline_support(command_processor):
    """Integrate pipeline support into existing command processor"""
    try:
        # Create enhanced processor
        enhanced_processor = AdvancedCommandProcessor(command_processor)
        
        # Store original method to avoid recursion
        if not hasattr(command_processor, '_original_process_command_pipe'):
            command_processor._original_process_command_pipe = command_processor.process_command
        
        def enhanced_process_command_with_pipes(command_line):
            """Enhanced command processing with full pipeline and redirection support"""
            # Check for pipes first
            if '|' in command_line:
                return enhanced_processor.pipeline_processor.process_pipeline(command_line)
            
            # Check for redirection
            if any(redirect in command_line for redirect in ['>', '<', '2>', '2>&1']):
                return enhanced_processor.redirection_processor.process_redirection(command_line)
            
            # Regular command processing using original method
            return command_processor._original_process_command_pipe(command_line)
        
        # Replace the process_command method only if not already replaced
        if not hasattr(command_processor, '_pipe_integrated'):
            command_processor.process_command = enhanced_process_command_with_pipes
            command_processor._pipe_integrated = True
        
        return enhanced_processor
        
    except Exception as e:
        print(f"Warning: Failed to integrate pipeline support: {e}")
        return command_processor