import os

def get_core_windows_dirs():
    """
    Get a list of core Windows system directories that should be skipped during file operations.

    Returns:
    list: List of core Windows system directory paths.
    """
    system_root = os.environ.get('SystemRoot', 'C:\\Windows')
    system_drive = os.environ.get('SystemDrive', 'C:')

    return [
        system_root,
        os.path.join(system_drive, 'Program Files'),
        os.path.join(system_drive, 'Program Files (x86)'),
        os.path.join(system_drive, 'Users', 'Default'),
        os.path.join(system_drive, 'Users', 'Public'),
        os.path.join(system_drive, '$Recycle.Bin'),
        os.path.join(system_drive, 'Recovery'),
        os.path.join(system_drive, 'System Volume Information'),
        os.path.join(system_drive, 'Windows.old')
    ]
