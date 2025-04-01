import os
import logging
import subprocess
import shutil
import tempfile
import sys
import py7zr

class Extractor:
    """Handles extraction of 7z archives."""
    
    def __init__(self):
        """Initialize the extractor."""
        pass
    
    def extract_7z_py7zr(self, archive_path, extract_path):
        """
        Extract a 7z archive using py7zr library.
        
        Args:
            archive_path: Path to the 7z archive
            extract_path: Path where to extract the contents
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            os.makedirs(extract_path, exist_ok=True)
            
            with py7zr.SevenZipFile(archive_path, mode='r') as archive:
                logging.info(f"Extracting {archive_path} to {extract_path}")
                archive.extractall(path=extract_path)
            
            logging.info(f"Extraction completed successfully")
            return True
        except Exception as e:
            logging.error(f"Error extracting archive with py7zr: {e}")
            return False
    
    def extract_7z_binary(self, archive_path, extract_path):
        """
        Extract a 7z archive using 7z binary.
        
        Args:
            archive_path: Path to the 7z archive
            extract_path: Path where to extract the contents
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if 7z binary exists
            if os.name == 'nt':  # Windows
                seven_zip_path = self.find_7zip_windows()
                if not seven_zip_path:
                    logging.error("7-Zip executable not found. Please install 7-Zip or use py7zr method.")
                    return False
            else:
                seven_zip_path = '7z'  # Linux/MacOS typically have it in PATH
            
            # Create extraction directory
            os.makedirs(extract_path, exist_ok=True)
            
            # Build extraction command
            cmd = [seven_zip_path, 'x', archive_path, f'-o{extract_path}', '-y']
            
            logging.info(f"Extracting using command: {' '.join(cmd)}")
            
            # Execute extraction
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logging.error(f"Error extracting archive: {stderr}")
                return False
            
            logging.info(f"Extraction completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error extracting archive with 7z binary: {e}")
            return False
    
    def find_7zip_windows(self):
        """
        Find 7-Zip executable on Windows systems.
        
        Returns:
            str: Path to 7-Zip executable or None if not found
        """
        # Common installation paths
        possible_paths = [
            r"C:\Program Files\7-Zip\7z.exe",
            r"C:\Program Files (x86)\7-Zip\7z.exe",
        ]
        
        # Check if any of the paths exist
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Try to find in PATH
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, "7z.exe")
            if os.path.exists(exe_file):
                return exe_file
        
        return None
    
    def extract_archive(self, archive_path, extract_path):
        """
        Extract a 7z archive using available methods.
        
        Args:
            archive_path: Path to the 7z archive
            extract_path: Path where to extract the contents
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(archive_path):
            logging.error(f"Archive does not exist: {archive_path}")
            return False
        
        # First try with py7zr (pure Python)
        try:
            import py7zr
            logging.info("Attempting extraction with py7zr...")
            if self.extract_7z_py7zr(archive_path, extract_path):
                return True
        except ImportError:
            logging.warning("py7zr not available, falling back to 7z binary")
        except Exception as e:
            logging.warning(f"py7zr extraction failed: {e}, falling back to 7z binary")
        
        # Fallback to 7z binary
        logging.info("Attempting extraction with 7z binary...")
        return self.extract_7z_binary(archive_path, extract_path)
    
    def validate_extraction(self, extract_path, expected_files=None):
        """
        Validate that extraction was successful by checking for expected files.
        
        Args:
            extract_path: Path where the archive was extracted
            expected_files: List of files/directories expected after extraction
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        # If no expected files were specified, check for common ComfyUI files
        if not expected_files:
            expected_files = [
                "ComfyUI_windows_portable",
                "ComfyUI_windows_portable/run_nvidia_gpu.bat"
            ]
        
        # Check if the expected files/directories exist
        for file in expected_files:
            file_path = os.path.join(extract_path, file)
            if not os.path.exists(file_path):
                logging.error(f"Expected file/directory not found after extraction: {file_path}")
                return False
        
        logging.info(f"Extraction validation passed: {extract_path}")
        return True
