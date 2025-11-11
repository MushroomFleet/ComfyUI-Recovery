import os
import logging
import requests
import time
from tqdm import tqdm
import re

class Downloader:
    """Handles downloading files with progress tracking and resume capability."""
    
    def __init__(self):
        """Initialize the downloader."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ComfyUI-Recovery/1.0'
        })
    
    def extract_version_from_url(self, url):
        """
        Extract version number from ComfyUI download URL.
        
        Args:
            url: The download URL
            
        Returns:
            str: Version string (e.g., 'v0.3.27') or None
        """
        match = re.search(r'/v(\d+\.\d+\.\d+)/', url)
        if match:
            return f"v{match.group(1)}"
        return None
    
    def get_latest_comfyui_version(self):
        """
        Get the latest ComfyUI release version from GitHub.
        
        Returns:
            tuple: (version_string, download_url) or (None, None) on error
        """
        try:
            api_url = "https://api.github.com/repos/comfyanonymous/ComfyUI/releases/latest"
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                version = data.get('tag_name', '')
                
                # Find the Windows portable NVIDIA asset
                for asset in data.get('assets', []):
                    if 'ComfyUI_windows_portable_nvidia.7z' in asset.get('name', ''):
                        return version, asset.get('browser_download_url')
                
                logging.warning("Latest release found but no Windows portable NVIDIA asset")
                return version, None
            else:
                logging.warning(f"Failed to get latest version from GitHub: {response.status_code}")
                return None, None
                
        except Exception as e:
            logging.warning(f"Error checking for latest version: {e}")
            return None, None
    
    def check_cached_archive(self, archive_path):
        """
        Check if a cached archive exists and is valid.
        
        Args:
            archive_path: Path to the cached archive
            
        Returns:
            bool: True if archive exists and appears valid
        """
        if not os.path.exists(archive_path):
            return False
        
        # Check if file has reasonable size (at least 100MB)
        file_size = os.path.getsize(archive_path)
        if file_size < 100 * 1024 * 1024:  # 100MB minimum
            logging.warning(f"Cached archive appears incomplete: {file_size} bytes")
            return False
        
        logging.info(f"Found cached archive: {archive_path} ({file_size / (1024**3):.2f} GB)")
        return True
    
    def download_file(self, url, destination, chunk_size=8192):
        """
        Download a file from URL to destination with progress tracking and resume capability.
        
        Args:
            url: URL to download from
            destination: Path where the file should be saved
            chunk_size: Size of chunks to download at a time
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)
            
            # Get file size from the URL
            file_size = 0
            resume_header = {}
            
            # Check if file exists to resume download
            if os.path.exists(destination):
                file_size = os.path.getsize(destination)
                resume_header = {'Range': f'bytes={file_size}-'}
                logging.info(f"Resuming download from byte {file_size}")
            
            # Make initial request to get file size and check if resume is accepted
            response = self.session.get(url, stream=True, headers=resume_header, timeout=10)
            
            # Handle redirect if necessary
            if response.history:
                logging.info(f"Request was redirected to {response.url}")
                url = response.url
            
            # Get total file size
            total_size = int(response.headers.get('content-length', 0))
            
            # If we're resuming, adjust total size
            if response.status_code == 206:  # Partial content
                total_size += file_size
            elif file_size > 0:  # Server doesn't support resume, start over
                logging.warning("Server doesn't support resuming, restarting download")
                file_size = 0
                os.remove(destination)
                response = self.session.get(url, stream=True, timeout=10)
            
            # Set up progress bar
            desc = os.path.basename(destination)
            progress_bar = tqdm(
                total=total_size,
                initial=file_size,
                unit='B',
                unit_scale=True,
                desc=desc
            )
            
            # Open file for writing (append if resuming, write if new)
            mode = 'ab' if file_size > 0 else 'wb'
            with open(destination, mode) as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        progress_bar.update(len(chunk))
            
            progress_bar.close()
            
            # Check if download was complete
            if os.path.getsize(destination) >= total_size:
                logging.info(f"Download complete: {destination}")
                return True
            else:
                logging.error(f"Download incomplete. Expected {total_size} bytes, got {os.path.getsize(destination)}")
                return False
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Download error: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error during download: {e}")
            return False
    
    def download_with_retry(self, url, destination, max_retries=3, retry_delay=5):
        """
        Download a file with retry capability.
        
        Args:
            url: URL to download from
            destination: Path where the file should be saved
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        for attempt in range(max_retries):
            logging.info(f"Download attempt {attempt + 1}/{max_retries}: {url}")
            if self.download_file(url, destination):
                return True
            
            if attempt < max_retries - 1:
                logging.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
        
        logging.error(f"Failed to download {url} after {max_retries} attempts")
        return False
