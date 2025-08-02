"""
Command Processor - Handles command parsing and execution
"""

import os
import sys
import shlex
import subprocess
from pathlib import Path
from commands import *
from full_commands import *
from batch_support import BatchProcessor, BatchFileDetector
from pipe_support import integrate_pipeline_support
from doskey_support import integrate_doskey_support

class CommandProcessor:
    def __init__(self):
        # Initialize built-in commands
        self.builtin_commands = {
            # File and Directory Operations
            'cd': CDCommand(), 'chdir': CDCommand(),
            'dir': DirCommand(), 'ls': DirCommand(),
            'copy': CopyCommand(), 'xcopy': XCopyCommand(), 'robocopy': RobocopyCommand(),
            'move': MoveCommand(), 'ren': RenameCommand(), 'rename': RenameCommand(),
            'del': DelCommand(), 'erase': DelCommand(), 'rd': RmdirCommand(), 'rmdir': RmdirCommand(),
            'md': MkdirCommand(), 'mkdir': MkdirCommand(),
            'type': TypeCommand(), 'more': MoreCommand(), 'edit': EditCommand(),
            'notepad': NotepadCommand(), 'wordpad': WordpadCommand(),
            'attrib': AttribCommand(), 'comp': CompCommand(), 'fc': FcCommand(),
            'replace': ReplaceCommand(), 'subst': SubstCommand(),
            
            # Text Processing
            'find': FindCommand(), 'findstr': FindStrCommand(), 'sort': SortCommand(),
            'clip': ClipCommand(), 'print': PrintCommand(),
            
            # System Information
            'ver': VerCommand(), 'date': DateCommand(), 'time': TimeCommand(),
            'systeminfo': SystemInfoCommand(), 'hostname': HostnameCommand(),
            'whoami': WhoamiCommand(), 'logoff': LogoffCommand(),
            
            # Process Management
            'tasklist': TaskListCommand(), 'taskkill': TaskKillCommand(),
            'start': StartCommand(), 'call': CallCommand(), 'timeout': TimeoutCommand(),
            
            # Network Commands
            'ping': PingCommand(), 'tracert': TracertCommand(), 'pathping': PathpingCommand(),
            'ipconfig': IpConfigCommand(), 'nslookup': NslookupCommand(), 'arp': ArpCommand(),
            'netstat': NetstatCommand(), 'route': RouteCommand(), 'telnet': TelnetCommand(),
            'ftp': FtpCommand(), 'netsh': NetshCommand(),
            
            # Disk and Volume Management
            'vol': VolCommand(), 'label': LabelCommand(), 'chkdsk': ChkDskCommand(),
            'format': FormatCommand(), 'diskpart': DiskPartCommand(), 'fsutil': FsutilCommand(),
            'defrag': DefragCommand(), 'cipher': CipherCommand(),
            
            # Registry Operations
            'reg': RegCommand(), 'regedit': RegeditCommand(),
            
            # Service Management
            'sc': ScCommand(), 'net': NetCommand(),
            
            # System Utilities
            'sfc': SfcCommand(), 'dism': DismCommand(), 'powercfg': PowercfgCommand(),
            'msconfig': MsconfigCommand(), 'msinfo32': Msinfo32Command(),
            'eventvwr': EventvwrCommand(), 'perfmon': PerfmonCommand(),
            
            # Environment and Settings
            'set': SetCommand(), 'setx': SetxCommand(), 'path': PathCommand(),
            'prompt': PromptCommand(), 'title': TitleCommand(), 'color': ColorCommand(),
            'mode': ModeCommand(), 'chcp': ChcpCommand(),
            
            # Console Operations
            'echo': EchoCommand(), 'cls': ClsCommand(), 'clear': ClsCommand(),
            'pause': PauseCommand(), 'choice': ChoiceCommand(),
            
            # Batch Operations
            'if': IfCommand(), 'for': ForCommand(), 'goto': GotoCommand(),
            'shift': ShiftCommand(), 'exit': ExitCommand(), 'endlocal': EndlocalCommand(),
            'setlocal': SetlocalCommand(), 'rem': RemCommand(),
            
            # Archive and Compression
            'expand': ExpandCommand(), 'makecab': MakecabCommand(), 'compact': CompactCommand(),
            
            # Security
            'cipher': CipherCommand(), 'cacls': CaclsCommand(), 'icacls': IcaclsCommand(),
            'takeown': TakeownCommand(), 'runas': RunasCommand(),
            
            # Advanced System Tools
            'wmic': WmicCommand(), 'powershell': PowershellCommand(), 'cmd': CmdCommand(),
            'help': HelpCommand(), 'where': WhereCommand(), 'which': WhereCommand(),
            'tree': TreeCommand(), 'doskey': DoskeyCommand(),
            
            # Scheduling
            'at': AtCommand(), 'schtasks': SchtasksCommand(),
            
            # Hardware and Drivers
            'driverquery': DriverqueryCommand(), 'pnputil': PnputilCommand(),
            
            # Memory and Performance
            'mem': MemCommand(), 'taskmgr': TaskmgrCommand(),
            
            # File Associations
            'assoc': AssocCommand(), 'ftype': FtypeCommand(),
            
            # Miscellaneous
            'calc': CalcCommand(), 'explorer': ExplorerCommand(), 'mspaint': MspaintCommand(),
            'control': ControlCommand(), 'appwiz.cpl': AppwizCommand(),
        }
        
        # Environment variables
        self.env_vars = dict(os.environ)
        
        # Batch processor
        self.batch_processor = BatchProcessor(self)
        
        # Initialize components safely to avoid recursion
        self.enhanced_processor = None
        self.doskey_components = None
        
        # Initialize integrations after basic setup
        self._initialize_integrations()
        
    def _initialize_integrations(self):
        """Initialize pipeline and DOSKEY support safely"""
        try:
            # Integrate pipeline support
            self.enhanced_processor = integrate_pipeline_support(self)
            
            # Integrate DOSKEY support
            self.doskey_components = integrate_doskey_support(self)
        except Exception as e:
            print(f"Warning: Failed to initialize advanced features: {e}")
            
    def parse_command(self, command_line):
        """Parse command line into command and arguments"""
        try:
            # Handle special characters and quotes properly
            parts = shlex.split(command_line, posix=False)
            if not parts:
                return None, []
            
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            return command, args
        except ValueError:
            # Handle unmatched quotes
            parts = command_line.split()
            command = parts[0].lower() if parts else ""
            args = parts[1:] if len(parts) > 1 else []
            return command, args
            
    def expand_variables(self, text):
        """Expand environment variables in text"""
        if '%' not in text:
            return text
            
        # Simple variable expansion
        for var, value in self.env_vars.items():
            text = text.replace(f'%{var}%', value)
            text = text.replace(f'%{var.lower()}%', value)
            
        return text
        
    def process_command(self, command_line):
        """Process a single command line"""
        # Expand environment variables
        command_line = self.expand_variables(command_line)
        
        # Handle multiple commands separated by &, &&, ||
        if '&' in command_line or '||' in command_line:
            return self.process_compound_command(command_line)
            
        # Handle redirection
        if '>' in command_line or '<' in command_line or '>>' in command_line:
            return self.process_redirected_command(command_line)
            
        # Parse command
        command, args = self.parse_command(command_line)
        
        if not command:
            return
            
        # Check for built-in commands
        if command in self.builtin_commands:
            try:
                result = self.builtin_commands[command].execute(args)
                return result
            except Exception as e:
                print(f"'{command}' command failed: {e}")
                return
        
        # Check for batch files
        batch_file = BatchFileDetector.find_batch_file(command)
        if batch_file:
            try:
                self.batch_processor.execute_batch_file(batch_file, [command] + args)
                return
            except Exception as e:
                print(f"Error executing batch file: {e}")
                return
                
        # Try to execute as external command
        return self.execute_external_command(command, args)
        
    def process_compound_command(self, command_line):
        """Handle compound commands with &, &&, ||"""
        # This is a simplified implementation
        # Real CMD has more complex parsing rules
        
        if '&&' in command_line:
            commands = command_line.split('&&')
            for cmd in commands:
                result = self.process_command(cmd.strip())
                if result == "EXIT":
                    return result
        elif '||' in command_line:
            commands = command_line.split('||')
            for cmd in commands:
                result = self.process_command(cmd.strip())
                if result == "EXIT":
                    return result
        elif '&' in command_line:
            commands = command_line.split('&')
            for cmd in commands:
                result = self.process_command(cmd.strip())
                if result == "EXIT":
                    return result
                    
    def process_redirected_command(self, command_line):
        """Handle command redirection"""
        # Simplified redirection handling
        if '>>' in command_line:
            parts = command_line.split('>>', 1)
            cmd_part = parts[0].strip()
            file_part = parts[1].strip()
            
            # Capture output and append to file
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            try:
                with redirect_stdout(f):
                    self.process_command(cmd_part)
                output = f.getvalue()
                
                with open(file_part, 'a', encoding='utf-8') as outfile:
                    outfile.write(output)
            except Exception as e:
                print(f"Redirection failed: {e}")
                
        elif '>' in command_line:
            parts = command_line.split('>', 1)
            cmd_part = parts[0].strip()
            file_part = parts[1].strip()
            
            # Capture output and write to file
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            try:
                with redirect_stdout(f):
                    self.process_command(cmd_part)
                output = f.getvalue()
                
                with open(file_part, 'w', encoding='utf-8') as outfile:
                    outfile.write(output)
            except Exception as e:
                print(f"Redirection failed: {e}")
                
    def execute_external_command(self, command, args):
        """Execute external programs"""
        try:
            # Try to find the executable
            full_command = [command] + args
            
            # Check if it's a batch file or executable
            if not command.endswith(('.exe', '.com', '.bat', '.cmd')):
                # Try adding common extensions
                for ext in ['.exe', '.com', '.bat', '.cmd']:
                    if self.find_executable(command + ext):
                        command = command + ext
                        break
                        
            # Execute the command
            result = subprocess.run(
                [command] + args,
                capture_output=False,
                text=True,
                shell=True
            )
            
            return result.returncode
            
        except FileNotFoundError:
            print(f"'{command}' is not recognized as an internal or external command,")
            print("operable program or batch file.")
        except Exception as e:
            print(f"Error executing '{command}': {e}")
            
    def find_executable(self, name):
        """Find executable in PATH"""
        path_dirs = self.env_vars.get('PATH', '').split(os.pathsep)
        
        for directory in path_dirs:
            if not directory:
                continue
                
            full_path = os.path.join(directory, name)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                return full_path
                
        return None