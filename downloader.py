import os
import logging
import requests
import time
from tqdm import tqdm

class Downloader:
    """Handles downloading files with progress tracking and resume capability."""
    
    def __init__(self):
        """Initialize the downloader."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ComfyUI-Recovery/1.0'
        })
    
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
