import os
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class SettingsManager:
    """Manages application settings and configuration."""
    
    def __init__(self, config_file="settings.json"):
        """Initialize settings manager with the path to the config file."""
        self.config_file = os.path.abspath(config_file)
        self.settings = {
            "comfyui_url": "https://github.com/comfyanonymous/ComfyUI/releases/download/v0.3.27/ComfyUI_windows_portable_nvidia.7z",
            "install_path": "",
            "models_path": "",
            "repo_list_path": "RepoLists/default.txt",
            "cached_version": "",
            "cached_archive_path": ""
        }
        self.load_settings()
    
    def load_settings(self):
        """Load settings from the config file if it exists."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Update settings with loaded values
                    self.settings.update(loaded_settings)
                logging.info(f"Settings loaded from {self.config_file}")
            else:
                logging.info(f"No settings file found at {self.config_file}")
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save current settings to the config file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            logging.info(f"Settings saved to {self.config_file}")
            return True
        except Exception as e:
            logging.error(f"Error saving settings: {e}")
            return False
    
    def update_setting(self, key, value):
        """Update a specific setting."""
        if key in self.settings:
            self.settings[key] = value
            return True
        else:
            logging.warning(f"Unknown setting key: {key}")
            return False
    
    def get_setting(self, key, default=None):
        """Get a specific setting value."""
        return self.settings.get(key, default)
    
    def validate_settings(self):
        """Validate required settings."""
        required_settings = ["install_path", "models_path"]
        
        missing_settings = [s for s in required_settings if not self.settings.get(s)]
        
        if missing_settings:
            logging.warning(f"Missing required settings: {', '.join(missing_settings)}")
            return False, missing_settings
        
        # Check if paths exist
        if not os.path.exists(os.path.dirname(self.settings["install_path"])):
            return False, ["Parent directory of install_path does not exist"]
        
        if not os.path.exists(self.settings["models_path"]):
            return False, ["models_path does not exist"]
            
        return True, []
    
    def validate_install_path(self):
        """Check if install path is empty and valid."""
        install_path = self.settings.get("install_path", "")
        
        if not install_path:
            return False, "No installation path specified"
        
        # Check if parent directory exists
        parent_dir = os.path.dirname(install_path)
        if not os.path.exists(parent_dir):
            return False, f"Parent directory does not exist: {parent_dir}"
        
        # Check if path exists and is not empty
        if os.path.exists(install_path):
            try:
                if os.path.isdir(install_path) and os.listdir(install_path):
                    return False, f"Installation path is not empty: {install_path}"
            except Exception as e:
                return False, f"Error checking installation path: {e}"
        
        return True, "Installation path is valid and empty"
