#!/usr/bin/env python3
"""
ComfyUI Recovery System - A tool to rebuild ComfyUI installations
"""

import os
import sys
import logging
import argparse
from pathlib import Path
import time

# Import our modules
from settings import SettingsManager
from downloader import Downloader
from extractor import Extractor
from symlink_manager import SymlinkManager
from node_installer import NodeInstaller
from first_run_initializer import FirstRunInitializer

def setup_logging():
    """Set up logging configuration."""
    log_dir = os.path.abspath("logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Log to file and console
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    log_file = os.path.join(log_dir, f"recovery_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.info(f"ComfyUI Recovery System starting up")
    logging.info(f"Log file: {log_file}")

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="ComfyUI Recovery System - Rebuild ComfyUI installations",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "--install-path",
        help="Path where ComfyUI will be installed"
    )
    
    parser.add_argument(
        "--models-path",
        help="Path to your model storage directory"
    )
    
    parser.add_argument(
        "--repo-list",
        help="Path to the repository list file",
        default="RepoLists/default.txt"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force installation even if destination is not empty"
    )
    
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip downloading ComfyUI (use existing archive)"
    )
    
    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="Skip extracting ComfyUI (use existing directory)"
    )
    
    parser.add_argument(
        "--skip-symlink",
        action="store_true",
        help="Skip creating symbolic links"
    )
    
    parser.add_argument(
        "--skip-nodes",
        action="store_true",
        help="Skip installing custom nodes"
    )
    
    parser.add_argument(
        "--skip-first-run",
        action="store_true",
        help="Skip first-run initialization (embedded Python already exists)"
    )
    
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Download the latest version from GitHub (bypass cache)"
    )
    
    return parser.parse_args()

def confirm_action(prompt):
    """Ask user for confirmation."""
    response = input(f"{prompt} (y/n): ").strip().lower()
    return response == "y" or response == "yes"

def main():
    """Main entry point for the application."""
    # Set up logging
    setup_logging()
    
    # Parse command-line arguments
    args = parse_arguments()
    
    # Initialize components
    settings = SettingsManager()
    downloader = Downloader()
    extractor = Extractor()
    symlink_manager = SymlinkManager()
    node_installer = NodeInstaller()
    
    # Update settings from command line arguments
    if args.install_path:
        settings.update_setting("install_path", args.install_path)
    
    if args.models_path:
        settings.update_setting("models_path", args.models_path)
    
    if args.repo_list:
        settings.update_setting("repo_list_path", args.repo_list)
    
    # Check if we have all required settings
    valid, missing = settings.validate_settings()
    
    # If settings are missing, prompt for them
    if not valid:
        logging.info("Some required settings are missing")
        
        if "install_path" in missing or not settings.get_setting("install_path"):
            install_path = input("Enter the path where ComfyUI should be installed: ").strip()
            if install_path:
                settings.update_setting("install_path", install_path)
        
        if "models_path" in missing or not settings.get_setting("models_path"):
            models_path = input("Enter the path to your models storage folder: ").strip()
            if models_path:
                settings.update_setting("models_path", models_path)
        
        # Save the settings
        settings.save_settings()
        
        # Validate again
        valid, missing = settings.validate_settings()
        if not valid:
            logging.error(f"Required settings still missing: {', '.join(missing)}")
            sys.exit(1)
    
    # Check if install path is empty
    install_path = settings.get_setting("install_path")
    models_path = settings.get_setting("models_path")
    repo_list_path = settings.get_setting("repo_list_path")
    comfyui_url = settings.get_setting("comfyui_url")
    
    # Make sure destination path exists
    os.makedirs(install_path, exist_ok=True)
    
    # Check if the install path is empty
    valid_install, message = settings.validate_install_path()
    if not valid_install and not args.force:
        logging.warning(message)
        if not confirm_action("Installation path is not empty. Continue anyway?"):
            logging.info("Installation cancelled by user")
            sys.exit(0)
    
    logging.info(f"Using install path: {install_path}")
    logging.info(f"Using models path: {models_path}")
    logging.info(f"Using repository list: {repo_list_path}")
    
    # Download ComfyUI if needed
    download_path = os.path.join(install_path, "comfyui.7z")
    
    if not args.skip_download:
        # Check for latest version from GitHub
        latest_version, latest_url = downloader.get_latest_comfyui_version()
        current_version = downloader.extract_version_from_url(comfyui_url)
        cached_version = settings.get_setting("cached_version", "")
        
        # Determine if we need to download
        need_download = True
        
        # Check if we have a cached archive
        if downloader.check_cached_archive(download_path) and not args.latest:
            logging.info(f"Using cached ComfyUI archive (version {cached_version or current_version})")
            
            # Check if there's a newer version available
            if latest_version and latest_version != cached_version and latest_version != current_version:
                logging.info(f"\n{'='*60}")
                logging.info(f"NEW VERSION AVAILABLE!")
                logging.info(f"Current: {cached_version or current_version}")
                logging.info(f"Latest:  {latest_version}")
                logging.info(f"Use --latest flag to download the new version")
                logging.info(f"{'='*60}\n")
            
            need_download = False
        elif args.latest:
            # User wants the latest version
            if latest_version and latest_url:
                logging.info(f"Downloading latest version: {latest_version}")
                comfyui_url = latest_url
                settings.update_setting("comfyui_url", latest_url)
            else:
                logging.warning("Could not determine latest version, using configured URL")
        
        # Download if needed
        if need_download:
            logging.info(f"Downloading ComfyUI from {comfyui_url}")
            success = downloader.download_with_retry(comfyui_url, download_path)
            
            if not success:
                logging.error("Failed to download ComfyUI")
                sys.exit(1)
            
            # Update cached version info
            downloaded_version = downloader.extract_version_from_url(comfyui_url)
            if downloaded_version:
                settings.update_setting("cached_version", downloaded_version)
                settings.update_setting("cached_archive_path", download_path)
                settings.save_settings()
                logging.info(f"Cached version info updated: {downloaded_version}")
            
            logging.info(f"Download completed: {download_path}")
    else:
        logging.info("Skipping download (--skip-download)")
        if not os.path.exists(download_path):
            logging.error(f"Archive not found: {download_path}")
            sys.exit(1)
    
    # Extract ComfyUI
    if not args.skip_extract:
        logging.info(f"Extracting ComfyUI to {install_path}")
        success = extractor.extract_archive(download_path, install_path)
        
        if not success:
            logging.error("Failed to extract ComfyUI")
            sys.exit(1)
        
        # Validate extraction
        if not extractor.validate_extraction(install_path):
            logging.error("Extraction validation failed")
            sys.exit(1)
        
        logging.info("Extraction completed successfully")
    else:
        logging.info("Skipping extraction (--skip-extract)")
    
    # Run first-time initialization to set up embedded Python
    if not args.skip_first_run:
        logging.info("\n" + "="*60)
        logging.info("FIRST-RUN INITIALIZATION")
        logging.info("="*60)
        
        first_run_init = FirstRunInitializer()
        success, message = first_run_init.run_first_initialization(install_path)
        
        if not success:
            logging.error(f"First-run initialization failed: {message}")
            logging.warning("Custom nodes may not install correctly without embedded Python")
            if not confirm_action("Continue anyway?"):
                logging.info("Installation cancelled by user")
                sys.exit(1)
        else:
            logging.info(message)
        
        logging.info("="*60 + "\n")
    else:
        logging.info("Skipping first-run initialization (--skip-first-run)")
    
    # Create symbolic links (after first-run to replace default models directory)
    if not args.skip_symlink:
        logging.info("Setting up model symbolic links")
        success, message = symlink_manager.setup_model_symlinks(install_path, models_path)
        
        if not success:
            logging.error(f"Failed to create symbolic links: {message}")
            sys.exit(1)
        
        logging.info(message)
    else:
        logging.info("Skipping symbolic link creation (--skip-symlink)")
    
    # Install custom nodes
    if not args.skip_nodes:
        # Check if repo list exists
        if not os.path.exists(repo_list_path):
            logging.warning(f"Repository list not found: {repo_list_path}")
            if confirm_action("Repository list not found. Skip custom node installation?"):
                args.skip_nodes = True
            else:
                logging.error("Cannot proceed without repository list")
                sys.exit(1)
        else:
            logging.info(f"Installing custom nodes from {repo_list_path}")
            success, message = node_installer.install_custom_nodes(install_path, repo_list_path)
            
            if not success:
                logging.error(f"Failed to install custom nodes: {message}")
            else:
                logging.info(message)
    else:
        logging.info("Skipping custom node installation (--skip-nodes)")
    
    # Display path to Python embedded
    python_embeded_path = symlink_manager.get_python_embeded_path(install_path)
    logging.info("\n" + "="*60)
    logging.info("ComfyUI Recovery completed successfully!")
    logging.info("="*60)
    logging.info(f"ComfyUI is installed at: {install_path}")
    logging.info(f"Models are linked from: {models_path}")
    logging.info("\nTo run ComfyUI, use:")
    logging.info(f"{os.path.join(install_path, 'ComfyUI_windows_portable_nvidia', 'ComfyUI_windows_portable', 'run_nvidia_gpu.bat')}")
    logging.info("\nYou may want to add the Python embedded directory to your PATH:")
    logging.info(f"{python_embeded_path}")
    logging.info("="*60)

if __name__ == "__main__":
    main()
