"""
Batch File Support for Command Prompt Clone
Handles .bat and .cmd file execution
"""

import os
import sys
import re
import subprocess
from pathlib import Path

class BatchProcessor:
    """Processes batch files (.bat, .cmd)"""
    
    def __init__(self, command_processor):
        self.command_processor = command_processor
        self.variables = {}
        self.echo_on = True
        self.goto_labels = {}
        self.call_stack = []
        
    def execute_batch_file(self, filename, args=None):
        """Execute a batch file"""
        if args is None:
            args = []
            
        try:
            with open(filename, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                
            # Parse labels first
            self.parse_labels(lines)
            
            # Set batch parameters
            self.set_batch_parameters(args)
            
            # Execute lines
            self.execute_batch_lines(lines, filename)
            
        except FileNotFoundError:
            print(f"The system cannot find the file {filename}.")
        except Exception as e:
            print(f"Error executing batch file: {e}")
    
    def parse_labels(self, lines):
        """Parse :label definitions"""
        self.goto_labels.clear()
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith(':') and not line.startswith('::'):
                label = line[1:].strip()
                self.goto_labels[label.upper()] = i
    
    def set_batch_parameters(self, args):
        """Set %0, %1, %2, etc. parameters"""
        # %0 is the batch file name
        self.variables['0'] = args[0] if args else ''
        
        # %1, %2, etc. are the arguments
        for i, arg in enumerate(args[1:], 1):
            self.variables[str(i)] = arg
        
        # Clear higher numbered parameters
        for i in range(len(args), 10):
            self.variables[str(i)] = ''
        
        # %* represents all arguments
        self.variables['*'] = ' '.join(args[1:]) if args else ''
    
    def execute_batch_lines(self, lines, filename, start_line=0):
        """Execute batch file lines"""
        i = start_line
        
        while i < len(lines):
            line = lines[i].rstrip()
            original_line = line
            
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('::'):
                i += 1
                continue
            
            # Handle labels
            if line.strip().startswith(':'):
                i += 1
                continue
            
            # Handle @ prefix (suppress echo for this command)
            suppress_echo = False
            if line.strip().startswith('@'):
                suppress_echo = True
                line = line.strip()[1:].strip()
            
            # Echo the command if echo is on and not suppressed
            if self.echo_on and not suppress_echo:
                print(f"C:\\>{line}")
            
            # Expand variables
            line = self.expand_batch_variables(line)
            
            # Handle batch-specific commands
            result = self.handle_batch_command(line, lines, i, filename)
            
            if isinstance(result, int):
                # GOTO command returns new line number
                i = result
                continue
            elif result == 'EXIT':
                break
            elif result == 'CALL_RETURN':
                break
            
            i += 1
    
    def expand_batch_variables(self, line):
        """Expand batch variables like %VAR%, %1, %2, etc."""
        # Handle %n parameters (0-9)
        for i in range(10):
            param = f'%{i}'
            if param in line:
                value = self.variables.get(str(i), '')
                line = line.replace(param, value)
        
        # Handle %* (all parameters)
        if '%*' in line:
            line = line.replace('%*', self.variables.get('*', ''))
        
        # Handle custom variables %VAR%
        import re
        pattern = r'%([A-Za-z_][A-Za-z0-9_]*)%'
        
        def replace_var(match):
            var_name = match.group(1)
            return self.variables.get(var_name, os.environ.get(var_name, ''))
        
        line = re.sub(pattern, replace_var, line)
        
        return line
    
    def handle_batch_command(self, line, lines, current_line, filename):
        """Handle batch-specific commands"""
        parts = line.split()
        if not parts:
            return None
        
        command = parts[0].upper()
        args = parts[1:] if len(parts) > 1 else []
        
        # Batch-specific commands
        if command == 'ECHO':
            return self.handle_echo(args)
        elif command == 'SET':
            return self.handle_set(args)
        elif command == 'IF':
            return self.handle_if(args, lines, current_line)
        elif command == 'FOR':
            return self.handle_for(args, lines, current_line)
        elif command == 'GOTO':
            return self.handle_goto(args)
        elif command == 'CALL':
            return self.handle_call(args)
        elif command == 'SHIFT':
            return self.handle_shift(args)
        elif command == 'EXIT':
            return self.handle_exit(args)
        elif command == 'PAUSE':
            return self.handle_pause(args)
        elif command == 'REM':
            return None  # Comment - do nothing
        elif command == 'SETLOCAL':
            return self.handle_setlocal(args)
        elif command == 'ENDLOCAL':
            return self.handle_endlocal(args)
        else:
            # Regular command - pass to command processor
            return self.command_processor.process_command(line)
    
    def handle_echo(self, args):
        """Handle ECHO command in batch context"""
        if not args:
            print(f"ECHO is {'on' if self.echo_on else 'off'}.")
        elif len(args) == 1:
            if args[0].upper() == 'ON':
                self.echo_on = True
            elif args[0].upper() == 'OFF':
                self.echo_on = False
            else:
                print(' '.join(args))
        else:
            print(' '.join(args))
        
        return None
    
    def handle_set(self, args):
        """Handle SET command in batch context"""
        if not args:
            # Display all variables
            for key, value in sorted(self.variables.items()):
                print(f"{key}={value}")
            for key, value in sorted(os.environ.items()):
                print(f"{key}={value}")
        else:
            assignment = ' '.join(args)
            if '=' in assignment:
                key, value = assignment.split('=', 1)
                self.variables[key.strip()] = value.strip()
            else:
                # Display specific variable
                key = assignment.strip()
                value = self.variables.get(key, os.environ.get(key, ''))
                if value:
                    print(f"{key}={value}")
                else:
                    print(f"Environment variable {key} not defined")
        
        return None
    
    def handle_if(self, args, lines, current_line):
        """Handle IF command (simplified)"""
        if len(args) < 3:
            return None
        
        # Simple IF implementation
        # IF condition command
        condition_met = False
        
        # Handle IF EXIST filename
        if args[0].upper() == 'EXIST':
            filename = args[1]
            condition_met = os.path.exists(filename)
            command = ' '.join(args[2:])
        
        # Handle IF string1==string2
        elif '==' in ' '.join(args):
            parts = ' '.join(args).split('==', 1)
            if len(parts) == 2:
                left = parts[0].strip().strip('"')
                right_and_command = parts[1].strip()
                
                # Find where the command starts
                right_parts = right_and_command.split()
                if right_parts:
                    right = right_parts[0].strip('"')
                    command = ' '.join(right_parts[1:])
                    condition_met = (left == right)
        
        # Handle IF ERRORLEVEL n
        elif args[0].upper() == 'ERRORLEVEL':
            try:
                level = int(args[1])
                # In a real implementation, this would check last command's error level
                condition_met = False  # Simplified
                command = ' '.join(args[2:])
            except (ValueError, IndexError):
                return None
        
        # Handle IF NOT
        elif args[0].upper() == 'NOT':
            # Recursive call with NOT removed
            result = self.handle_if(args[1:], lines, current_line)
            # Invert the condition (simplified)
            return result
        
        # Execute command if condition is met
        if condition_met and 'command' in locals():
            return self.command_processor.process_command(command)
        
        return None
    
    def handle_for(self, args, lines, current_line):
        """Handle FOR command (simplified)"""
        # FOR %variable IN (set) DO command
        # This is a simplified implementation
        print("FOR command in batch files is not fully implemented.")
        return None
    
    def handle_goto(self, args):
        """Handle GOTO command"""
        if not args:
            return None
        
        label = args[0].upper()
        if label in self.goto_labels:
            return self.goto_labels[label]
        else:
            print(f"The system cannot find the batch label specified - {args[0]}")
            return 'EXIT'
    
    def handle_call(self, args):
        """Handle CALL command"""
        if not args:
            return None
        
        # CALL can call another batch file or a label in current file
        target = args[0]
        call_args = args[1:] if len(args) > 1 else []
        
        if target.startswith(':'):
            # Call label in current file
            label = target[1:].upper()
            if label in self.goto_labels:
                # Save current state
                self.call_stack.append({
                    'variables': self.variables.copy(),
                    'return_line': current_line + 1
                })
                return self.goto_labels[label]
        else:
            # Call external batch file
            if os.path.exists(target):
                saved_vars = self.variables.copy()
                self.execute_batch_file(target, [target] + call_args)
                self.variables = saved_vars
        
        return None
    
    def handle_shift(self, args):
        """Handle SHIFT command"""
        # Shift parameters %1->%0, %2->%1, etc.
        new_vars = {}
        
        # Shift numbered parameters
        for i in range(9):
            next_param = str(i + 1)
            if next_param in self.variables:
                new_vars[str(i)] = self.variables[next_param]
            else:
                new_vars[str(i)] = ''
        
        # Update variables
        for i in range(9):
            self.variables[str(i)] = new_vars[str(i)]
        
        return None
    
    def handle_exit(self, args):
        """Handle EXIT command"""
        if args and args[0].upper() == '/B':
            # Exit batch file only
            return 'CALL_RETURN'
        else:
            # Exit entire command processor
            return 'EXIT'
    
    def handle_pause(self, args):
        """Handle PAUSE command"""
        print("Press any key to continue . . . ", end='')
        try:
            input()
        except KeyboardInterrupt:
            pass
        return None
    
    def handle_setlocal(self, args):
        """Handle SETLOCAL command"""
        # Save current environment
        self.call_stack.append({
            'variables': self.variables.copy(),
            'environment': dict(os.environ)
        })
        return None
    
    def handle_endlocal(self, args):
        """Handle ENDLOCAL command"""
        # Restore previous environment
        if self.call_stack:
            saved_state = self.call_stack.pop()
            self.variables = saved_state.get('variables', {})
            # Note: In a real implementation, this would restore os.environ too
        return None

class BatchFileDetector:
    """Detects and handles batch file execution"""
    
    @staticmethod
    def is_batch_file(filename):
        """Check if file is a batch file"""
        if not os.path.isfile(filename):
            return False
        
        _, ext = os.path.splitext(filename.lower())
        return ext in ['.bat', '.cmd']
    
    @staticmethod
    def find_batch_file(command):
        """Find batch file in current directory or PATH"""
        # Check current directory first
        for ext in ['.bat', '.cmd']:
            filepath = command + ext
            if os.path.isfile(filepath):
                return filepath
        
        # Check PATH directories
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        for directory in path_dirs:
            if not directory:
                continue
            
            for ext in ['.bat', '.cmd']:
                filepath = os.path.join(directory, command + ext)
                if os.path.isfile(filepath):
                    return filepath
        
        return None