"""
Configuration Settings for Command Prompt
"""

import os

class Config:
    """Configuration class for the CMD"""
    
    # Application info
    APP_NAME = "Command Prompt"
    APP_VERSION = "1.0.0"
    
    # Display settings
    DEFAULT_PROMPT = "$P$G"  # $P = current path, $G = > character
    DEFAULT_TITLE = "Command Prompt"
    
    # Command settings
    COMMAND_HISTORY_SIZE = 50
    MAX_COMMAND_LENGTH = 8192
    
    # File operations
    DEFAULT_COPY_BUFFER_SIZE = 64 * 1024  # 64KB
    
    # Directory listing settings
    DIR_DATE_FORMAT = "%m/%d/%Y  %I:%M %p"
    
    # Color codes (for color command)
    COLORS = {
        '0': 'Black',
        '1': 'Blue', 
        '2': 'Green',
        '3': 'Aqua',
        '4': 'Red',
        '5': 'Purple',
        '6': 'Yellow',
        '7': 'White',
        '8': 'Gray',
        '9': 'Light Blue',
        'A': 'Light Green',
        'B': 'Light Aqua', 
        'C': 'Light Red',
        'D': 'Light Purple',
        'E': 'Light Yellow',
        'F': 'Bright White'
    }
    
    # Command aliases
    COMMAND_ALIASES = {
        'ls': 'dir',
        'erase': 'del',
        'mkdir': 'md',
        'rmdir': 'rd',
        'rename': 'ren',
        'clear': 'cls'
    }
    
    # File extensions that are executable
    EXECUTABLE_EXTENSIONS = ['.exe', '.com', '.bat', '.cmd', '.msi', '.scr']
    
    # Default environment variables
    DEFAULT_ENV_VARS = {
        'PROMPT': '$P$G',
        'DIRCMD': '/O:N',  # Default sort order for DIR
        'PATHEXT': '.COM;.EXE;.BAT;.CMD;.VBS;.JS;.WS;.MSC'
    }
    
    # Error messages
    ERROR_MESSAGES = {
        'FILE_NOT_FOUND': 'The system cannot find the file specified.',
        'PATH_NOT_FOUND': 'The system cannot find the path specified.',
        'ACCESS_DENIED': 'Access is denied.',
        'INVALID_SYNTAX': 'The syntax of the command is incorrect.',
        'UNKNOWN_COMMAND': "'{0}' is not recognized as an internal or external command,\noperable program or batch file.",
        'DIRECTORY_NOT_EMPTY': 'The directory is not empty.',
        'INVALID_PARAMETER': 'Invalid parameter.',
        'OUT_OF_MEMORY': 'Not enough memory.',
        'DISK_FULL': 'The disk is full.',
        'INVALID_DRIVE': 'The system cannot find the drive specified.'
    }
    
    # Success messages  
    SUCCESS_MESSAGES = {
        'FILE_COPIED': '{0} file(s) copied.',
        'FILE_MOVED': '{0} file(s) moved.',
        'DIRECTORY_CREATED': 'Directory created successfully.',
        'DIRECTORY_REMOVED': 'Directory removed successfully.',
        'FILE_DELETED': '{0} file(s) deleted.'
    }
    
    # Command line switches and options
    COMMON_SWITCHES = {
        '/Y': 'Suppress prompting to confirm overwrite',
        '/N': 'Suppress prompting to confirm overwrite (opposite of /Y)',
        '/S': 'Include subdirectories',
        '/Q': 'Quiet mode',
        '/V': 'Verbose mode',
        '/F': 'Force operation',
        '/A': 'Show all files including hidden and system files',
        '/B': 'Bare format (no heading, no summary)',
        '/W': 'Wide list format',
        '/P': 'Pause after each screenful',
        '/O': 'Sort order',
        '/T': 'Time field to display/sort by',
        '/?': 'Display help'
    }
    
    # DIR command sort orders
    DIR_SORT_ORDERS = {
        'N': 'Name (alphabetic)',
        'E': 'Extension (alphabetic)', 
        'D': 'Date/time (oldest first)',
        'S': 'Size (smallest first)',
        'G': 'Group directories first',
        '-N': 'Name (reverse alphabetic)',
        '-E': 'Extension (reverse alphabetic)',
        '-D': 'Date/time (newest first)', 
        '-S': 'Size (largest first)',
        '-G': 'Group directories last'
    }
    
    # Special directories
    SPECIAL_DIRS = {
        '.': 'Current directory',
        '..': 'Parent directory',
        '\\': 'Root directory',
        '~': 'User home directory'
    }
    
    # Batch file settings
    BATCH_EXTENSIONS = ['.bat', '.cmd']
    BATCH_ECHO_DEFAULT = True
    
    # Network settings (for network commands)
    DEFAULT_PING_COUNT = 4
    DEFAULT_PING_TIMEOUT = 4000  # milliseconds
    
    # System paths
    SYSTEM32_PATH = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'System32')
    WINDOWS_PATH = os.environ.get('WINDIR', 'C:\\Windows')
    
    # Performance settings
    MAX_FILES_WITHOUT_PAGING = 1000
    
    @classmethod
    def get_default_env_vars(cls):
        """Get default environment variables"""
        env_vars = cls.DEFAULT_ENV_VARS.copy()
        
        # Add system-specific defaults
        if os.name == 'nt':
            env_vars.update({
                'COMSPEC': os.path.join(cls.SYSTEM32_PATH, 'cmd.exe'),
                'WINDIR': cls.WINDOWS_PATH,
                'SYSTEMROOT': cls.WINDOWS_PATH,
                'TEMP': os.environ.get('TEMP', 'C:\\Windows\\Temp'),
                'TMP': os.environ.get('TMP', 'C:\\Windows\\Temp')
            })
        
        return env_vars
    
    @classmethod
    def get_error_message(cls, error_type, *args):
        """Get formatted error message"""
        if error_type in cls.ERROR_MESSAGES:
            return cls.ERROR_MESSAGES[error_type].format(*args)
        return f"Unknown error: {error_type}"
    
    @classmethod
    def get_success_message(cls, message_type, *args):
        """Get formatted success message"""
        if message_type in cls.SUCCESS_MESSAGES:
            return cls.SUCCESS_MESSAGES[message_type].format(*args)
        return f"Operation completed: {message_type}"
    
    @classmethod
    def is_executable_file(cls, filename):
        """Check if file is executable based on extension"""
        _, ext = os.path.splitext(filename.lower())
        return ext in cls.EXECUTABLE_EXTENSIONS
    
    @classmethod
    def get_command_alias(cls, command):
        """Get command alias if it exists"""
        return cls.COMMAND_ALIASES.get(command.lower(), command)