import os
import logging
import subprocess
import shutil
import ctypes

class SymlinkManager:
    """Manages symbolic links between folders."""
    
    def __init__(self):
        """Initialize the symlink manager."""
        pass
    
    def is_admin(self):
        """
        Check if the script is running with administrator privileges on Windows.
        
        Returns:
            bool: True if running as admin, False otherwise
        """
        try:
            if os.name == 'nt':  # Windows
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False
    
    def create_symlink(self, source_path, target_path, force=False):
        """
        Create a symbolic link from source_path pointing to target_path.
        
        Args:
            source_path: The path where the symlink will be created (models folder in ComfyUI)
            target_path: The target that the symlink will point to (user's model storage)
            force: If True, will remove the source path if it exists
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Normalize paths
            source_path = os.path.abspath(source_path)
            target_path = os.path.abspath(target_path)
            
            # Validate paths
            if not os.path.exists(target_path):
                return False, f"Target path does not exist: {target_path}"
            
            # Check if source parent directory exists
            source_parent = os.path.dirname(source_path)
            if not os.path.exists(source_parent):
                try:
                    os.makedirs(source_parent, exist_ok=True)
                    logging.info(f"Created parent directory: {source_parent}")
                except Exception as e:
                    return False, f"Failed to create parent directory {source_parent}: {e}"
            
            # Check if source exists and handle accordingly
            if os.path.exists(source_path):
                if not force:
                    return False, f"Source path already exists: {source_path}. Use force=True to overwrite."
                
                # If it's a directory, remove it
                if os.path.isdir(source_path):
                    logging.info(f"Removing existing directory: {source_path}")
                    shutil.rmtree(source_path)
                # If it's a file or symlink, remove it
                else:
                    logging.info(f"Removing existing file or symlink: {source_path}")
                    os.remove(source_path)
            
            # Create symbolic link
            if os.name == 'nt':  # Windows
                # Use mklink command through cmd
                command = f'mklink /D "{source_path}" "{target_path}"'
                logging.info(f"Running command: {command}")
                
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    return False, f"Failed to create symlink: {stderr}"
                
                logging.info(f"Symlink created: {source_path} -> {target_path}")
                return True, f"Symlink created successfully: {source_path} -> {target_path}"
            
            else:  # Unix/Linux/MacOS
                os.symlink(target_path, source_path, target_is_directory=True)
                logging.info(f"Symlink created: {source_path} -> {target_path}")
                return True, f"Symlink created successfully: {source_path} -> {target_path}"
        
        except Exception as e:
            logging.error(f"Error creating symlink: {e}")
            return False, f"Error creating symlink: {e}"
    
    def find_comfyui_base(self, install_path: str) -> str:
        """
        Find the actual ComfyUI base directory, handling different extraction structures.
        
        Args:
            install_path: Path where ComfyUI is installed
            
        Returns:
            str: Path to the ComfyUI base directory
        """
        # Check for nested structure (with parent dir)
        nested_path = os.path.join(install_path, "ComfyUI_windows_portable_nvidia", "ComfyUI_windows_portable")
        if os.path.exists(nested_path):
            return nested_path
        
        # Check for direct structure (without parent dir)
        direct_path = os.path.join(install_path, "ComfyUI_windows_portable")
        if os.path.exists(direct_path):
            return direct_path
        
        # Return nested path as default (will fail later with clear error)
        return nested_path
    
    def get_comfyui_models_path(self, install_path):
        """
        Get the path to the ComfyUI models directory.
        
        Args:
            install_path: Path where ComfyUI is installed
            
        Returns:
            str: Path to the models directory
        """
        base_path = self.find_comfyui_base(install_path)
        return os.path.join(base_path, "ComfyUI", "models")
    
    def setup_model_symlinks(self, install_path, models_path):
        """
        Set up symbolic links for model directories.
        
        Args:
            install_path: Path where ComfyUI is installed
            models_path: Path to the user's model storage
            
        Returns:
            tuple: (success, message)
        """
        comfyui_models_path = self.get_comfyui_models_path(install_path)
        
        logging.info(f"Setting up model symlink:")
        logging.info(f"  Source: {comfyui_models_path}")
        logging.info(f"  Target: {models_path}")
        
        # Check if running with admin privileges on Windows
        if os.name == 'nt' and not self.is_admin():
            logging.warning("Not running with administrator privileges")
            logging.warning("Symbolic link creation may fail on Windows without admin rights")
        
        success, message = self.create_symlink(comfyui_models_path, models_path, force=True)
        
        # If symlink creation failed, provide helpful guidance
        if not success and os.name == 'nt':
            if "privilege" in message.lower() or "permission" in message.lower():
                error_msg = (
                    f"{message}\n\n"
                    "SOLUTION - You have two options:\n\n"
                    "Option 1: Run as Administrator\n"
                    "  1. Close this terminal\n"
                    "  2. Right-click on PowerShell (or Command Prompt)\n"
                    "  3. Select 'Run as Administrator'\n"
                    "  4. Navigate to this directory and run the script again\n\n"
                    "Option 2: Enable Developer Mode (Windows 10/11)\n"
                    "  1. Open Settings -> Update & Security -> For developers\n"
                    "  2. Enable 'Developer Mode'\n"
                    "  3. Restart this script (no admin rights needed)\n\n"
                    "See README.md for detailed instructions."
                )
                return False, error_msg
        
        return success, message
    
    def get_python_embeded_path(self, install_path):
        """
        Get the path to the embedded Python in ComfyUI.
        
        Args:
            install_path: Path where ComfyUI is installed
            
        Returns:
            str: Path to the embedded Python Scripts directory
        """
        base_path = self.find_comfyui_base(install_path)
        return os.path.join(base_path, "python_embeded", "Scripts")
