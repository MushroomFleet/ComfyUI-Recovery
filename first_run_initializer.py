import os
import logging
import subprocess
import time
import psutil
from typing import Tuple

class FirstRunInitializer:
    """Handles first-run initialization of ComfyUI to set up embedded Python."""
    
    def __init__(self):
        """Initialize the first-run initializer."""
        pass
    
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
    
    def get_run_script_path(self, install_path: str) -> str:
        """
        Get the path to the run_nvidia_gpu.bat script.
        
        Args:
            install_path: Path where ComfyUI is installed
            
        Returns:
            str: Path to the run script
        """
        base_path = self.find_comfyui_base(install_path)
        return os.path.join(base_path, "run_nvidia_gpu.bat")
    
    def get_python_embeded_path(self, install_path: str) -> str:
        """
        Get the path to the embedded Python executable.
        
        Args:
            install_path: Path where ComfyUI is installed
            
        Returns:
            str: Path to python.exe
        """
        base_path = self.find_comfyui_base(install_path)
        return os.path.join(base_path, "python_embeded", "python.exe")
    
    def verify_embedded_python(self, install_path: str) -> bool:
        """
        Check if embedded Python exists.
        
        Args:
            install_path: Path where ComfyUI is installed
            
        Returns:
            bool: True if embedded Python exists
        """
        python_path = self.get_python_embeded_path(install_path)
        exists = os.path.exists(python_path)
        
        if exists:
            logging.info(f"Embedded Python verified at: {python_path}")
        else:
            logging.warning(f"Embedded Python not found at: {python_path}")
        
        return exists
    
    def kill_process_tree(self, pid: int):
        """
        Kill a process and all its children.
        
        Args:
            pid: Process ID to kill
        """
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            
            # Terminate children first
            for child in children:
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    pass
            
            # Wait for children to terminate
            gone, alive = psutil.wait_procs(children, timeout=5)
            
            # Force kill any remaining children
            for child in alive:
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass
            
            # Terminate parent
            try:
                parent.terminate()
                parent.wait(5)
            except psutil.TimeoutExpired:
                parent.kill()
            except psutil.NoSuchProcess:
                pass
                
        except psutil.NoSuchProcess:
            logging.warning(f"Process {pid} not found")
        except Exception as e:
            logging.error(f"Error killing process tree: {e}")
    
    def run_first_initialization(self, install_path: str, timeout: int = 300) -> Tuple[bool, str]:
        """
        Run ComfyUI for the first time to initialize the embedded Python environment.
        
        Args:
            install_path: Path where ComfyUI is installed
            timeout: Maximum time to wait for initialization (seconds)
            
        Returns:
            tuple: (success, message)
        """
        # Check if embedded Python already exists
        if self.verify_embedded_python(install_path):
            return True, "Embedded Python already exists, skipping first-run initialization"
        
        # Get the run script path
        run_script = self.get_run_script_path(install_path)
        
        if not os.path.exists(run_script):
            return False, f"Run script not found: {run_script}"
        
        try:
            logging.info("Starting ComfyUI for first-run initialization...")
            logging.info("This will set up the embedded Python environment")
            logging.info(f"Timeout: {timeout} seconds")
            
            # Start ComfyUI process
            process = subprocess.Popen(
                [run_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                shell=True,
                cwd=os.path.dirname(run_script)
            )
            
            logging.info(f"ComfyUI process started (PID: {process.pid})")
            
            start_time = time.time()
            initialization_detected = False
            stable_count = 0
            last_output_time = start_time
            
            # Monitor the process output
            while True:
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    logging.warning(f"Initialization timeout after {timeout} seconds")
                    self.kill_process_tree(process.pid)
                    return False, f"First-run initialization timed out after {timeout} seconds"
                
                # Check if process is still running
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    if stdout:
                        logging.info(f"Process output: {stdout}")
                    if stderr:
                        logging.error(f"Process error: {stderr}")
                    
                    # Check if embedded Python now exists
                    if self.verify_embedded_python(install_path):
                        return True, "ComfyUI first-run initialization completed successfully"
                    else:
                        return False, "ComfyUI process terminated but embedded Python not found"
                
                # Read output line by line (non-blocking)
                try:
                    # Use a small timeout to avoid blocking forever
                    import select
                    if hasattr(select, 'select'):
                        # Unix-like systems
                        ready = select.select([process.stdout], [], [], 0.1)
                        if ready[0]:
                            line = process.stdout.readline()
                        else:
                            line = None
                    else:
                        # Windows - just try to read
                        line = process.stdout.readline() if process.stdout else None
                    
                    if line:
                        line = line.strip()
                        if line:
                            logging.info(f"ComfyUI: {line}")
                            last_output_time = time.time()
                            
                            # Check for initialization completion indicators
                            if "To see the GUI go to:" in line or "http://127.0.0.1:8188" in line:
                                initialization_detected = True
                                logging.info("ComfyUI server is ready!")
                    
                    # If we detected initialization, wait for stability
                    if initialization_detected:
                        time_since_output = time.time() - last_output_time
                        
                        # Wait for 5 seconds of stability
                        if time_since_output >= 5:
                            stable_count += 1
                            if stable_count >= 1:
                                logging.info("ComfyUI appears stable, proceeding to shutdown...")
                                
                                # Give it a bit more time to ensure everything is initialized
                                time.sleep(3)
                                
                                # Verify embedded Python exists
                                if self.verify_embedded_python(install_path):
                                    logging.info("Shutting down ComfyUI...")
                                    self.kill_process_tree(process.pid)
                                    
                                    # Wait a moment for cleanup
                                    time.sleep(2)
                                    
                                    return True, "ComfyUI first-run initialization completed successfully"
                                else:
                                    logging.warning("Initialization detected but embedded Python still not found, waiting...")
                                    initialization_detected = False
                                    stable_count = 0
                        else:
                            stable_count = 0
                
                except Exception as e:
                    logging.debug(f"Error reading output: {e}")
                
                # Small delay to prevent busy waiting
                time.sleep(0.1)
        
        except Exception as e:
            logging.error(f"Error during first-run initialization: {e}")
            try:
                if process and process.pid:
                    self.kill_process_tree(process.pid)
            except:
                pass
            return False, f"Error during first-run initialization: {e}"
