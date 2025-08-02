"""
Utility Functions for Command Prompt
"""

import os
import sys
import re
import glob
import shutil
from pathlib import Path

class Utils:
    """Utility functions for the command prompt clone"""
    
    @staticmethod
    def format_size(size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 bytes"
        
        size_names = ["bytes", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def expand_wildcards(pattern):
        """Expand wildcard patterns like *.txt"""
        try:
            matches = glob.glob(pattern)
            return matches if matches else [pattern]
        except:
            return [pattern]
    
    @staticmethod
    def is_hidden_file(filepath):
        """Check if a file is hidden (Windows style)"""
        try:
            attrs = os.stat(filepath).st_file_attributes
            return attrs & 0x02  # FILE_ATTRIBUTE_HIDDEN
        except:
            # Fallback: check if filename starts with dot (Unix style)
            return os.path.basename(filepath).startswith('.')
    
    @staticmethod
    def get_file_attributes(filepath):
        """Get file attributes string (like attrib command)"""
        try:
            path = Path(filepath)
            attrs = []
            
            if path.is_dir():
                attrs.append('D')
            else:
                attrs.append(' ')
                
            # Check if file is read-only
            if not os.access(filepath, os.W_OK):
                attrs.append('R')
            else:
                attrs.append(' ')
                
            # Check if hidden
            if Utils.is_hidden_file(filepath):
                attrs.append('H')
            else:
                attrs.append(' ')
                
            # System file (simplified check)
            if filepath.lower().endswith(('.sys', '.dll')):
                attrs.append('S')
            else:
                attrs.append(' ')
                
            # Archive attribute (always set for simplicity)
            attrs.append('A')
            
            return ''.join(attrs)
        except:
            return '     '
    
    @staticmethod
    def parse_path(path_str):
        """Parse and normalize path string"""
        # Handle quotes
        path_str = path_str.strip('"\'')
        
        # Expand environment variables
        path_str = os.path.expandvars(path_str)
        
        # Convert forward slashes to backslashes on Windows
        if os.name == 'nt':
            path_str = path_str.replace('/', '\\')
        
        # Resolve relative paths
        if not os.path.isabs(path_str):
            path_str = os.path.join(os.getcwd(), path_str)
        
        return os.path.normpath(path_str)
    
    @staticmethod
    def get_disk_usage(path='.'):
        """Get disk usage information"""
        try:
            usage = shutil.disk_usage(path)
            return {
                'total': usage.total,
                'used': usage.total - usage.free,
                'free': usage.free
            }
        except:
            return {'total': 0, 'used': 0, 'free': 0}
    
    @staticmethod
    def validate_filename(filename):
        """Validate filename for Windows compatibility"""
        invalid_chars = '<>:"|?*\x00'
        invalid_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        # Check for invalid characters
        for char in invalid_chars:
            if char in filename:
                return False, f"Invalid character '{char}' in filename"
        
        # Check for reserved names
        name_only = os.path.splitext(filename)[0].upper()
        if name_only in invalid_names:
            return False, f"'{filename}' is a reserved filename"
        
        # Check length
        if len(filename) > 255:
            return False, "Filename too long"
        
        # Check for trailing dots or spaces
        if filename.endswith('.') or filename.endswith(' '):
            return False, "Filename cannot end with a dot or space"
        
        return True, "Valid filename"
    
    @staticmethod
    def get_drives():
        """Get list of available drives"""
        drives = []
        if os.name == 'nt':
            # Windows
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append(drive)
        else:
            # Unix-like systems
            drives = ['/']
        
        return drives
    
    @staticmethod
    def get_command_history():
        """Get command history (simplified implementation)"""
        # In a real implementation, this would read from doskey history
        return []
    
    @staticmethod
    def escape_special_chars(text):
        """Escape special characters for command line"""
        special_chars = '&<>|^'
        for char in special_chars:
            text = text.replace(char, f'^{char}')
        return text
    
    @staticmethod
    def split_command_line(command_line):
        """Split command line respecting quotes and escapes"""
        parts = []
        current_part = ""
        in_quotes = False
        quote_char = None
        i = 0
        
        while i < len(command_line):
            char = command_line[i]
            
            if not in_quotes:
                if char in ['"', "'"]:
                    in_quotes = True
                    quote_char = char
                elif char == ' ':
                    if current_part:
                        parts.append(current_part)
                        current_part = ""
                else:
                    current_part += char
            else:
                if char == quote_char:
                    in_quotes = False
                    quote_char = None
                else:
                    current_part += char
            
            i += 1
        
        if current_part:
            parts.append(current_part)
        
        return parts
    
    @staticmethod
    def format_file_time(timestamp):
        """Format file timestamp like DIR command"""
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime('%m/%d/%Y  %I:%M %p')
    
    @staticmethod
    def get_system_info():
        """Get basic system information"""
        import platform
        
        info = {
            'os_name': platform.system(),
            'os_version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
        }
        
        return info
    
    @staticmethod
    def check_admin_rights():
        """Check if running with administrator rights"""
        try:
            if os.name == 'nt':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except:
            return False
    
    @staticmethod
    def get_environment_block():
        """Get environment variables in CMD format"""
        env_block = []
        for key, value in sorted(os.environ.items()):
            env_block.append(f"{key}={value}")
        return env_block
    
    @staticmethod
    def resolve_path_extensions(command):
        """Resolve command with PATHEXT extensions"""
        if os.name != 'nt':
            return command
        
        pathext = os.environ.get('PATHEXT', '.COM;.EXE;.BAT;.CMD')
        extensions = pathext.lower().split(';')
        
        # If command already has an extension, return as-is
        if any(command.lower().endswith(ext) for ext in extensions):
            return command
        
        # Try each extension
        for ext in extensions:
            test_cmd = command + ext
            if os.path.isfile(test_cmd):
                return test_cmd
        
        return command