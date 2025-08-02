"""
Built-in Command Implementations
Contains all the built-in CMD commands
"""

import os
import sys
import shutil
import datetime
import platform
import subprocess
import glob
import stat
from pathlib import Path

class BaseCommand:
    """Base class for all commands"""
    def execute(self, args):
        raise NotImplementedError
        
class CDCommand(BaseCommand):
    """Change Directory command"""
    def execute(self, args):
        if not args:
            # No arguments - display current directory
            print(os.getcwd())
            return
            
        target = args[0]
        
        # Handle special cases
        if target == '/d' and len(args) > 1:
            target = args[1]
        elif target == '..':
            target = os.path.dirname(os.getcwd())
        elif target == '.':
            return
        elif target == '\\':
            target = os.path.splitdrive(os.getcwd())[0] + '\\'
            
        try:
            os.chdir(target)
        except FileNotFoundError:
            print(f"The system cannot find the path specified.")
        except Exception as e:
            print(f"Error: {e}")

class DirCommand(BaseCommand):
    """Directory listing command"""
    def execute(self, args):
        path = args[0] if args else '.'
        
        try:
            entries = list(Path(path).iterdir())
            
            # Print header
            print(f" Volume in drive {os.path.splitdrive(os.getcwd())[0]} has no label.")
            print(f" Volume Serial Number is 0000-0000")
            print()
            print(f" Directory of {os.path.abspath(path)}")
            print()
            
            # Sort entries
            dirs = sorted([e for e in entries if e.is_dir()])
            files = sorted([e for e in entries if e.is_file()])
            
            file_count = 0
            dir_count = 0
            total_size = 0
            
            # Display directories first
            for d in dirs:
                stat_info = d.stat()
                mod_time = datetime.datetime.fromtimestamp(stat_info.st_mtime)
                print(f"{mod_time.strftime('%m/%d/%Y  %I:%M %p')}    <DIR>          {d.name}")
                dir_count += 1
                
            # Display files
            for f in files:
                stat_info = f.stat()
                mod_time = datetime.datetime.fromtimestamp(stat_info.st_mtime)
                size = stat_info.st_size
                print(f"{mod_time.strftime('%m/%d/%Y  %I:%M %p')} {size:>14,} {f.name}")
                file_count += 1
                total_size += size
                
            print(f"               {file_count} File(s) {total_size:>14,} bytes")
            print(f"               {dir_count} Dir(s)  {shutil.disk_usage('.').free:>14,} bytes free")
            
        except FileNotFoundError:
            print("File Not Found")
        except Exception as e:
            print(f"Error: {e}")

class CopyCommand(BaseCommand):
    """Copy files command"""
    def execute(self, args):
        if len(args) < 2:
            print("The syntax of the command is incorrect.")
            return
            
        source = args[0]
        dest = args[1]
        
        try:
            shutil.copy2(source, dest)
            print("        1 file(s) copied.")
        except FileNotFoundError:
            print("The system cannot find the file specified.")
        except Exception as e:
            print(f"Error: {e}")

class XCopyCommand(BaseCommand):
    """Extended copy command"""
    def execute(self, args):
        if len(args) < 2:
            print("Invalid number of parameters")
            return
            
        source = args[0]
        dest = args[1]
        
        try:
            if os.path.isdir(source):
                shutil.copytree(source, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(source, dest)
            print("Files copied successfully.")
        except Exception as e:
            print(f"Error: {e}")

class MoveCommand(BaseCommand):
    """Move files/directories command"""
    def execute(self, args):
        if len(args) < 2:
            print("The syntax of the command is incorrect.")
            return
            
        source = args[0]
        dest = args[1]
        
        try:
            shutil.move(source, dest)
            print("        1 file(s) moved.")
        except Exception as e:
            print(f"Error: {e}")

class RenameCommand(BaseCommand):
    """Rename files command"""
    def execute(self, args):
        if len(args) < 2:
            print("The syntax of the command is incorrect.")
            return
            
        old_name = args[0]
        new_name = args[1]
        
        try:
            os.rename(old_name, new_name)
        except Exception as e:
            print(f"Error: {e}")

class DelCommand(BaseCommand):
    """Delete files command"""
    def execute(self, args):
        if not args:
            print("The syntax of the command is incorrect.")
            return
            
        for pattern in args:
            try:
                files = glob.glob(pattern)
                if not files:
                    print("Could Not Find " + pattern)
                    continue
                    
                for file in files:
                    if os.path.isfile(file):
                        os.remove(file)
                        
            except Exception as e:
                print(f"Error: {e}")

class MkdirCommand(BaseCommand):
    """Make directory command"""
    def execute(self, args):
        if not args:
            print("The syntax of the command is incorrect.")
            return
            
        for dirname in args:
            try:
                os.makedirs(dirname, exist_ok=True)
            except Exception as e:
                print(f"Error: {e}")

class RmdirCommand(BaseCommand):
    """Remove directory command"""
    def execute(self, args):
        if not args:
            print("The syntax of the command is incorrect.")
            return
            
        for dirname in args:
            try:
                if '/s' in args:
                    shutil.rmtree(dirname)
                else:
                    os.rmdir(dirname)
            except OSError:
                print(f"The directory is not empty.")
            except Exception as e:
                print(f"Error: {e}")

class TypeCommand(BaseCommand):
    """Display file contents command"""
    def execute(self, args):
        if not args:
            print("The syntax of the command is incorrect.")
            return
            
        for filename in args:
            try:
                with open(filename, 'r', encoding='utf-8', errors='replace') as f:
                    print(f.read(), end='')
            except FileNotFoundError:
                print("The system cannot find the file specified.")
            except Exception as e:
                print(f"Error: {e}")

class EchoCommand(BaseCommand):
    """Echo command"""
    def execute(self, args):
        if not args:
            print("ECHO is on.")
            return
            
        if args[0].upper() == 'ON':
            print("ECHO is on.")
        elif args[0].upper() == 'OFF':
            print("ECHO is off.")
        else:
            print(' '.join(args))

class ClsCommand(BaseCommand):
    """Clear screen command"""
    def execute(self, args):
        os.system('cls' if os.name == 'nt' else 'clear')

class ExitCommand(BaseCommand):
    """Exit command"""
    def execute(self, args):
        return "EXIT"

class HelpCommand(BaseCommand):
    """Help command"""
    def execute(self, args):
        if not args:
            print("For more information on a specific command, type HELP command-name")
            commands = [
                "CD", "COPY", "DEL", "DIR", "ECHO", "EXIT", "HELP", "MD", "MOVE", 
                "RD", "REN", "TYPE", "VER", "VOL", "DATE", "TIME", "CLS", "FIND",
                "TREE", "ATTRIB", "WHERE", "TASKLIST", "PING"
            ]
            
            for i in range(0, len(commands), 3):
                row = commands[i:i+3]
                print("".join(f"{cmd:<15}" for cmd in row))
        else:
            command = args[0].upper()
            help_text = {
                "CD": "Displays the name of or changes the current directory.",
                "COPY": "Copies one or more files to another location.",
                "DEL": "Deletes one or more files.",
                "DIR": "Displays a list of files and subdirectories in a directory.",
                "ECHO": "Displays messages, or turns command echoing on or off.",
                "EXIT": "Quits the CMD.EXE program (command interpreter).",
                "HELP": "Provides Help information for Windows commands.",
                "MD": "Creates a directory.",
                "MOVE": "Moves one or more files from one directory to another directory.",
                "RD": "Removes a directory.",
                "REN": "Renames a file or files.",
                "TYPE": "Displays the contents of a text file.",
                "VER": "Displays the Windows version.",
                "CLS": "Clears the screen."
            }
            
            if command in help_text:
                print(help_text[command])
            else:
                print(f"This command is not supported by the help utility.")

class VerCommand(BaseCommand):
    """Version command"""
    def execute(self, args):
        print("Microsoft Windows [Version 10.0.19041.1706]")

class DateCommand(BaseCommand):
    """Date command"""
    def execute(self, args):
        current_date = datetime.datetime.now()
        print(f"The current date is: {current_date.strftime('%a %m/%d/%Y')}")
        
class TimeCommand(BaseCommand):
    """Time command"""
    def execute(self, args):
        current_time = datetime.datetime.now()
        print(f"The current time is: {current_time.strftime('%H:%M:%S.%f')[:-4]}")

class PathCommand(BaseCommand):
    """Path command"""
    def execute(self, args):
        if not args:
            print(f"PATH={os.environ.get('PATH', '')}")
        else:
            os.environ['PATH'] = ' '.join(args)

class SetCommand(BaseCommand):
    """Set environment variables command"""
    def execute(self, args):
        if not args:
            # Display all environment variables
            for key, value in sorted(os.environ.items()):
                print(f"{key}={value}")
        else:
            var_assignment = ' '.join(args)
            if '=' in var_assignment:
                key, value = var_assignment.split('=', 1)
                os.environ[key] = value
            else:
                # Display specific variable
                key = var_assignment
                value = os.environ.get(key, '')
                if value:
                    print(f"{key}={value}")
                else:
                    print(f"Environment variable {key} not defined")

class PromptCommand(BaseCommand):
    """Prompt command"""
    def execute(self, args):
        if args:
            print("PROMPT command is not fully implemented in this clone.")
        else:
            print("PROMPT is currently: $P$G")

class TitleCommand(BaseCommand):
    """Title command"""
    def execute(self, args):
        if args:
            title = ' '.join(args)
            # This would set window title in real CMD
            print(f"Title set to: {title}")

class ColorCommand(BaseCommand):
    """Color command"""
    def execute(self, args):
        if args:
            print("COLOR command is not fully implemented in this clone.")
        else:
            print("Sets the default console foreground and background colors.")

# Additional commands for completeness
class FindCommand(BaseCommand):
    """Find command"""
    def execute(self, args):
        print("FIND command is not fully implemented in this clone.")

class FindStrCommand(BaseCommand):
    """Find string command"""
    def execute(self, args):
        print("FINDSTR command is not fully implemented in this clone.")

class SortCommand(BaseCommand):
    """Sort command"""
    def execute(self, args):
        print("SORT command is not fully implemented in this clone.")

class MoreCommand(BaseCommand):
    """More command"""
    def execute(self, args):
        print("MORE command is not fully implemented in this clone.")

class TreeCommand(BaseCommand):
    """Tree command"""
    def execute(self, args):
        print("TREE command is not fully implemented in this clone.")

class AttribCommand(BaseCommand):
    """Attrib command"""
    def execute(self, args):
        print("ATTRIB command is not fully implemented in this clone.")

class WhereCommand(BaseCommand):
    """Where command"""
    def execute(self, args):
        print("WHERE command is not fully implemented in this clone.")

class TaskListCommand(BaseCommand):
    """TaskList command"""
    def execute(self, args):
        print("TASKLIST command is not fully implemented in this clone.")

class TaskKillCommand(BaseCommand):
    """TaskKill command"""
    def execute(self, args):
        print("TASKKILL command is not fully implemented in this clone.")

class PingCommand(BaseCommand):
    """Ping command"""
    def execute(self, args):
        if args:
            try:
                subprocess.run(['ping'] + args, check=False)
            except:
                print("PING command failed.")
        else:
            print("Usage: ping <host>")

class IpConfigCommand(BaseCommand):
    """IPConfig command"""
    def execute(self, args):
        print("IPCONFIG command is not fully implemented in this clone.")

class SystemInfoCommand(BaseCommand):
    """SystemInfo command"""
    def execute(self, args):
        print("SYSTEMINFO command is not fully implemented in this clone.")

class VolCommand(BaseCommand):
    """Vol command"""
    def execute(self, args):
        drive = os.path.splitdrive(os.getcwd())[0]
        print(f" Volume in drive {drive} has no label.")
        print(f" Volume Serial Number is 0000-0000")

class LabelCommand(BaseCommand):
    """Label command"""
    def execute(self, args):
        print("LABEL command is not fully implemented in this clone.")

class ChkDskCommand(BaseCommand):
    """ChkDsk command"""
    def execute(self, args):
        print("CHKDSK command is not fully implemented in this clone.")

class FormatCommand(BaseCommand):
    """Format command"""
    def execute(self, args):
        print("FORMAT command is not fully implemented in this clone.")

class DiskPartCommand(BaseCommand):
    """DiskPart command"""
    def execute(self, args):
        print("DISKPART command is not fully implemented in this clone.")

class SfcCommand(BaseCommand):
    """SFC command"""
    def execute(self, args):
        print("SFC command is not fully implemented in this clone.")

class DismCommand(BaseCommand):
    """DISM command"""
    def execute(self, args):
        print("DISM command is not fully implemented in this clone.")