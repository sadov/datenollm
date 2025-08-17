import json
import logging
import os
import sys
from pathlib import Path

# Path constants
DRIVE_PATH = os.environ.get('DRIVE_PATH', '/content/drive/MyDrive/colab_data/dateno/')
LOCAL_BASE_PATH = '.'

log_level = getattr(logging, os.environ.get('DATENOLLM_DEBUG', 'ERROR').upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def is_colab_environment():
    """Checks if the code is running in Google Colab"""
    try:
        import google.colab
        return True
    except ImportError:
        return False

def mount_drive_if_needed():
    """Mounts Drive if necessary and we are in Colab"""
    if is_colab_environment():
        try:
            from google.colab import drive
            if not os.path.exists('/content/drive'):
                logger.info("Connecting Google Drive...")
                drive.mount('/content/drive')
                logger.debug("Google Drive connected successfully!")
            else:
                logger.debug("Google Drive already connected")
        except Exception as e:
            logger.error(f"Error connecting Google Drive: {e}")
            return False
    return True

def get_full_path(file_path, base_path=None):
    """
    Returns the full path to the file depending on the environment
    
    Args:
        file_path (str): Relative or absolute path to the file
        base_path (str): Base path for the environment
    
    Returns:
        str: Full path to the file
    """
    # If the path is already absolute, return as is
    if os.path.isabs(file_path):
        return file_path
    
    if is_colab_environment():
        # In Colab we work with Google Drive
        mount_drive_if_needed()
        if not base_path:
            base_path = DRIVE_PATH
        # If the path doesn't start with base_path, add prefix
        if not file_path.startswith(base_path):
            full_path = os.path.join(base_path, file_path)
        else:
            full_path = file_path
    else:
        if not base_path:
            base_path = LOCAL_BASE_PATH
        # In local environment we work with local file system
        full_path = os.path.join(base_path, file_path)
        # Convert to absolute path
        full_path = os.path.abspath(full_path)
    
    return full_path

def file_exists(file_path):
    """
    Checks if the file exists in the current environment
    
    Args:
        file_path (str): Path to the file
    
    Returns:
        bool: True if the file exists, False otherwise
    """
    try:
        full_path = get_full_path(file_path)
        exists = os.path.exists(full_path)
        
        if is_colab_environment():
            logger.debug(f"Checking file in Google Drive: {full_path}")
        else:
            logger.debug(f"Checking file locally: {full_path}")

        return exists
    except Exception as e:
        logger.error(f"Error checking file existence: {e}")
        return False

def create_directory_if_not_exists(dir_path):
    """
    Creates directory if it doesn't exist
    
    Args:
        dir_path (str): Path to the directory
    
    Returns:
        bool: True if directory was created or already exists
    """
    try:
        full_path = get_full_path(dir_path)
        Path(full_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory: {e}")
        return False

def list_files(dir_path="", pattern="*"):
    """
    Returns list of files in the directory
    
    Args:
        dir_path (str): Path to the directory (default is root)
        pattern (str): Pattern for file search (default is all files)
    
    Returns:
        list: List of found files
    """
    try:
        full_path = get_full_path(dir_path)
        path_obj = Path(full_path)
        
        if not path_obj.exists():
            logger.warning(f"Directory doesn't exist: {full_path}")
            return []
        
        files = list(path_obj.glob(pattern))
        return [str(f) for f in files if f.is_file()]
    except Exception as e:
        logger.error(f"Error getting file list: {e}")
        return []

def get_file_info(file_path):
    """
    Returns information about the file
    
    Args:
        file_path (str): Path to the file
    
    Returns:
        dict: Dictionary with file information or None if file doesn't exist
    """
    try:
        full_path = get_full_path(file_path)
        
        if not file_exists(full_path):
            return None
        
        stat_info = os.stat(full_path)
        
        return {
            'path': full_path,
            'size': stat_info.st_size,
            'modified': stat_info.st_mtime,
            'is_file': os.path.isfile(full_path),
            'is_directory': os.path.isdir(full_path),
            'environment': 'colab' if is_colab_environment() else 'local'
        }
    except Exception as e:
        logger.error(f"Error getting file information: {e}")
        return None

def read_json_file(file_path, encoding='utf-8'):
    if not file_exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        logger.error(f"Error reading JSON file {file_path}: {e}")
        sys.exit(1)

def read_text_file(file_path, encoding='utf-8'):
    if not file_exists(file_path):
        return ''
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading text file {file_path}: {e}")
        sys.exit(1)

def save_json_file(data, file_path, encoding='utf-8'):
    if not file_exists(os.path.dirname(file_path)):
        create_directory_if_not_exists(os.path.dirname(file_path))
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {e}")
        sys.exit(1)


# Usage example
def fs_test():
    # Testing functions
    logger.info(f"Environment: {'Google Colab' if is_colab_environment() else 'Local system'}")

    # Check file existence
    test_file = "test.txt"
    logger.info(f"File {test_file} exists: {file_exists(test_file)}")
    
    # Get full path
    logger.info(f"Full path: {get_full_path(test_file)}")

    # Create directory
    create_directory_if_not_exists("test_folder")
    
    # List files
    files = list_files()
    logger.info(f"Found files: {len(files)}")

    # File information
    info = get_file_info(test_file)
    if info:
        logger.info(f"File information: {info}")

