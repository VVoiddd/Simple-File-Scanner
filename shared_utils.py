import os

def get_core_windows_dirs():
    """
    Get a list of core Windows system directories that should be skipped during file operations.

    Returns:
    list: List of core Windows system directory paths, which are not typically user-related.
    """
    system_root = os.environ.get('SystemRoot', 'C:\\Windows')
    system_drive = os.environ.get('SystemDrive', 'C:')

    return [
        system_root,  # Windows system directory
        os.path.join(system_drive, 'Program Files'),  # Main program files directory
        os.path.join(system_drive, 'Program Files (x86)'),  # 32-bit program files directory
        os.path.join(system_drive, 'Users', 'Default'),  # Default user profile
        os.path.join(system_drive, 'Users', 'Public'),  # Public user profile
        os.path.join(system_drive, '$Recycle.Bin'),  # Recycle Bin
        os.path.join(system_drive, 'Recovery'),  # Recovery folder
        os.path.join(system_drive, 'System Volume Information'),  # System volume information
        os.path.join(system_drive, 'Windows.old'),  # Previous Windows installation
        os.path.join(system_drive, 'ProgramData'),  # Application data for all users
        os.path.join(system_drive, 'Windows', 'System32'),  # System files
        os.path.join(system_drive, 'Windows', 'SysWOW64'),  # 32-bit system files on 64-bit systems
    ]

def get_program_files_dirs():
    """
    Get a list of program files directories.

    Returns:
    list: List of program files directory paths.
    """
    system_drive = os.environ.get('SystemDrive', 'C:')

    return [
        os.path.join(system_drive, 'Program Files'),
        os.path.join(system_drive, 'Program Files (x86)'),
    ]
