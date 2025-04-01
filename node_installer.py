import os
import logging
import subprocess
import sys
import re
from typing import List, Tuple, Optional
import shutil

class NodeInstaller:
    """Handles installation of custom nodes for ComfyUI."""
    
    def __init__(self):
        """Initialize the node installer."""
        pass
    
    def validate_github_urls(self, urls: List[str]) -> Tuple[bool, str, List[str]]:
        """
        Validate GitHub repository URLs.
        
        Args:
            urls: List of URLs to validate
            
        Returns:
            tuple: (success, message, valid_urls)
        """
        if not urls:
            return False, "No repository URLs provided", []
        
        valid_urls = []
        invalid_urls = []
        
        for url in urls:
            # Normalize the URL
            url = url.strip()
            if not url:
                continue
                
            # GitHub URL validation pattern
            pattern = r'^https://github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-._]+/?$'
            if re.match(pattern, url):
                valid_urls.append(url)
            else:
                invalid_urls.append(url)
        
        if invalid_urls:
            return False, f"Invalid GitHub URLs found: {', '.join(invalid_urls)}", valid_urls
        
        if not valid_urls:
            return False, "No valid URLs found", []
            
        return True, f"All URLs are valid ({len(valid_urls)} URLs)", valid_urls
    
    def read_repo_list(self, repo_list_path: str) -> Tuple[bool, str, List[str]]:
        """
        Read a repository list file.
        
        Args:
            repo_list_path: Path to the repository list file
            
        Returns:
            tuple: (success, message, urls)
        """
        try:
            if not os.path.exists(repo_list_path):
                return False, f"Repository list file not found: {repo_list_path}", []
            
            with open(repo_list_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            
            if not urls:
                return False, f"No URLs found in the repository list: {repo_list_path}", []
            
            return True, f"Read {len(urls)} URLs from {repo_list_path}", urls
            
        except Exception as e:
            logging.error(f"Error reading repository list: {e}")
            return False, f"Error reading repository list: {e}", []
    
    def get_custom_nodes_path(self, install_path: str) -> str:
        """
        Get the path to the custom_nodes directory.
        
        Args:
            install_path: Path where ComfyUI is installed
            
        Returns:
            str: Path to the custom_nodes directory
        """
        return os.path.join(
            install_path,
            "ComfyUI_windows_portable_nvidia",
            "ComfyUI_windows_portable",
            "ComfyUI",
            "custom_nodes"
        )
    
    def create_installation_script(self, custom_nodes_path: str, repos: List[str]) -> Tuple[bool, str]:
        """
        Create a Python script that will clone the repositories.
        
        Args:
            custom_nodes_path: Path to the custom_nodes directory
            repos: List of repository URLs
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Ensure custom_nodes directory exists
            os.makedirs(custom_nodes_path, exist_ok=True)
            
            # Create the script
            script_path = os.path.join(custom_nodes_path, "install_custom_nodes.py")
            
            script_content = f"""#!/usr/bin/env python3
import os
import subprocess
import sys

# Repositories to clone
repositories = {repos}

def main():
    # Get the current directory (should be the custom_nodes directory)
    custom_nodes_dir = os.path.abspath(os.path.dirname(__file__))
    print(f"Installing custom nodes to: {{custom_nodes_dir}}")
    
    success_count = 0
    failed_repos = []
    
    for repo in repositories:
        repo_name = repo.split('/')[-1].replace('.git', '')
        print(f"\\nProcessing {{repo_name}} from {{repo}}")
        
        # Clone the repository
        try:
            # Check if directory already exists
            target_dir = os.path.join(custom_nodes_dir, repo_name)
            if os.path.exists(target_dir):
                print(f"Directory already exists: {{target_dir}}")
                print(f"Pulling latest changes...")
                cmd = ["git", "-C", target_dir, "pull"]
            else:
                print(f"Cloning {{repo}}...")
                cmd = ["git", "clone", repo, target_dir]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                print(f"Error: {{stderr}}")
                failed_repos.append(repo)
                continue
            
            print(stdout)
            
            # Check for requirements.txt
            req_file = os.path.join(target_dir, "requirements.txt")
            if os.path.exists(req_file):
                print(f"Installing requirements...")
                
                # Get path to python executable
                python_path = sys.executable
                
                # Install requirements
                cmd = [python_path, "-m", "pip", "install", "-r", req_file]
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    print(f"Error installing requirements: {{stderr}}")
                else:
                    print("Requirements installed successfully")
            
            success_count += 1
            print(f"Successfully installed {{repo_name}}")
            
        except Exception as e:
            print(f"Error processing {{repo}}: {{e}}")
            failed_repos.append(repo)
    
    # Summary
    print("\\n" + "="*50)
    print(f"Installation complete: {{success_count}} successful, {{len(failed_repos)}} failed")
    
    if failed_repos:
        print("\\nFailed repositories:")
        for repo in failed_repos:
            print(f"  - {{repo}}")
    
    print("="*50)

if __name__ == "__main__":
    main()
"""
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            logging.info(f"Installation script created: {script_path}")
            return True, f"Installation script created successfully"
            
        except Exception as e:
            logging.error(f"Error creating installation script: {e}")
            return False, f"Error creating installation script: {e}"
    
    def install_custom_nodes(self, install_path: str, repo_list_path: str) -> Tuple[bool, str]:
        """
        Install custom nodes from a repository list.
        
        Args:
            install_path: Path where ComfyUI is installed
            repo_list_path: Path to the repository list file
            
        Returns:
            tuple: (success, message)
        """
        # Get custom_nodes path
        custom_nodes_path = self.get_custom_nodes_path(install_path)
        
        # Read repository list
        success, message, repos = self.read_repo_list(repo_list_path)
        if not success:
            return False, message
        
        # Validate GitHub URLs
        success, message, valid_repos = self.validate_github_urls(repos)
        if not success:
            return False, message
        
        # Create installation script
        success, message = self.create_installation_script(custom_nodes_path, valid_repos)
        if not success:
            return False, message
        
        # Run the installation script
        try:
            logging.info(f"Running installation script...")
            
            # Get path to python inside the ComfyUI portable
            comfyui_python = os.path.join(
                install_path,
                "ComfyUI_windows_portable_nvidia",
                "ComfyUI_windows_portable",
                "python_embeded",
                "python.exe"
            )
            
            if not os.path.exists(comfyui_python):
                comfyui_python = sys.executable
                logging.warning(f"ComfyUI Python not found, using system Python: {comfyui_python}")
            
            script_path = os.path.join(custom_nodes_path, "install_custom_nodes.py")
            
            cmd = [comfyui_python, script_path]
            
            logging.info(f"Running command: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=custom_nodes_path
            )
            
            stdout, stderr = process.communicate()
            
            if stdout:
                logging.info(stdout)
            
            if stderr:
                logging.error(stderr)
            
            if process.returncode != 0:
                return False, f"Error installing custom nodes: {stderr}"
            
            return True, f"Custom nodes installed successfully from {repo_list_path}"
            
        except Exception as e:
            logging.error(f"Error installing custom nodes: {e}")
            return False, f"Error installing custom nodes: {e}"
