#shared_utils.py

import os

def get_core_windows_dirs():
    return [
        os.environ.get('SystemRoot', 'C:\\Windows'),
        os.path.join(os.environ.get('SystemDrive', 'C:'), 'Program Files'),
        os.path.join(os.environ.get('SystemDrive', 'C:'), 'Program Files (x86)'),
        os.path.join(os.environ.get('SystemDrive', 'C:'), 'Users', 'Default'),
        os.path.join(os.environ.get('SystemDrive', 'C:'), 'Users', 'Public'),
        os.path.join(os.environ.get('SystemDrive', 'C:'), '$Recycle.Bin'),
        os.path.join(os.environ.get('SystemDrive', 'C:'), 'Recovery'),
        os.path.join(os.environ.get('SystemDrive', 'C:'), 'System Volume Information'),
        os.path.join(os.environ.get('SystemDrive', 'C:'), 'Windows.old')
    ]
