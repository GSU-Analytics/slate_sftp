import os
import paramiko
import stat
from typing import List, Tuple, Optional, Union
from pathlib import Path


class SlateSFTP:
    """
    A class to manage SFTP connections to Slate instances.
    
    This class provides methods for common file operations:
    - Listing directories and files
    - Creating directories
    - Downloading files
    - Uploading files
    """
    
    def __init__(
        self, 
        hostname: str, 
        port: int = 22, 
        username: str = None, 
        private_key_path: str = None
    ):
        """
        Initialize the SFTP connection to Slate.
        
        Args:
            hostname: The SFTP server hostname
            port: The SFTP server port (default: 22)
            username: Your SFTP username
            private_key_path: Path to your private key file
        """
        self.hostname = hostname
        self.port = port
        self.username = username
        self.private_key_path = private_key_path
        self.transport = None
        self.sftp = None
        
    def connect(self) -> bool:
        """
        Establish an SFTP connection to the Slate server.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            # Initialize SSH transport
            self.transport = paramiko.Transport((self.hostname, self.port))
            
            # Validate private key
            if not os.path.exists(self.private_key_path):
                raise FileNotFoundError(f"Private key file not found at {self.private_key_path}")
                
            try:
                private_key = paramiko.RSAKey.from_private_key_file(self.private_key_path)
            except paramiko.ssh_exception.PasswordRequiredException:
                raise ValueError("Private key is encrypted with a passphrase. Please use a key without a passphrase.")
            
            # Connect to the server
            self.transport.connect(username=self.username, pkey=private_key)
            
            # Create SFTP client
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            return True
            
        except Exception as e:
            print(f"Connection error: {str(e)}")
            self.close()
            return False
    
    def close(self):
        """Close the SFTP connection and transport."""
        if self.sftp:
            self.sftp.close()
            self.sftp = None
        if self.transport:
            self.transport.close()
            self.transport = None
    
    def __enter__(self):
        """Support for context manager protocol."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for context manager protocol."""
        self.close()
    
    def list_directories(self, remote_path: str = '.') -> List[str]:
        """
        List all directories in the specified path.
        
        Args:
            remote_path: The remote path to list directories from (default: current directory)
            
        Returns:
            List of directory names
        """
        if not self.sftp:
            raise ConnectionError("Not connected to SFTP server. Call connect() first.")
            
        directories = []
        for entry in self.sftp.listdir(remote_path):
            full_path = os.path.join(remote_path, entry)
            try:
                if stat.S_ISDIR(self.sftp.stat(full_path).st_mode):
                    directories.append(entry)
            except IOError:
                continue
                
        return directories
    
    def list_files(self, remote_path: str = '.') -> List[str]:
        """
        List all files in the specified path.
        
        Args:
            remote_path: The remote path to list files from (default: current directory)
            
        Returns:
            List of filenames
        """
        if not self.sftp:
            raise ConnectionError("Not connected to SFTP server. Call connect() first.")
            
        files = []
        for entry in self.sftp.listdir(remote_path):
            full_path = os.path.join(remote_path, entry)
            try:
                if not stat.S_ISDIR(self.sftp.stat(full_path).st_mode):
                    files.append(entry)
            except IOError:
                continue
                
        return files
    
    def list_all(self, remote_path: str = '.') -> Tuple[List[str], List[str]]:
        """
        List all directories and files in the specified path.
        
        Args:
            remote_path: The remote path to list from (default: current directory)
            
        Returns:
            Tuple of (directories, files)
        """
        if not self.sftp:
            raise ConnectionError("Not connected to SFTP server. Call connect() first.")
            
        directories = []
        files = []
        
        for entry in self.sftp.listdir(remote_path):
            full_path = os.path.join(remote_path, entry)
            try:
                if stat.S_ISDIR(self.sftp.stat(full_path).st_mode):
                    directories.append(entry)
                else:
                    files.append(entry)
            except IOError:
                continue
                
        return directories, files
    
    def create_directory(self, remote_path: str, mode: int = 0o755) -> bool:
        """
        Create a directory on the remote server.
        
        Args:
            remote_path: The path of the directory to create
            mode: The permissions to set on the new directory (default: 0o755)
            
        Returns:
            bool: True if directory was created successfully, False otherwise
        """
        if not self.sftp:
            raise ConnectionError("Not connected to SFTP server. Call connect() first.")
            
        try:
            self.sftp.mkdir(remote_path, mode)
            return True
        except IOError as e:
            print(f"Failed to create directory {remote_path}: {str(e)}")
            return False
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """
        Download a file from the remote server.
        
        Args:
            remote_path: The path of the file on the remote server
            local_path: The path where the file should be saved locally
            
        Returns:
            bool: True if file was downloaded successfully, False otherwise
        """
        if not self.sftp:
            raise ConnectionError("Not connected to SFTP server. Call connect() first.")
            
        try:
            # Create local directory if it doesn't exist
            local_dir = os.path.dirname(local_path)
            if local_dir and not os.path.exists(local_dir):
                os.makedirs(local_dir)
                
            self.sftp.get(remote_path, local_path)
            return True
        except IOError as e:
            print(f"Failed to download {remote_path} to {local_path}: {str(e)}")
            return False
    
    def download_files(self, remote_paths: List[str], local_dir: str) -> List[Tuple[str, bool]]:
        """
        Download multiple files from the remote server.
        
        Args:
            remote_paths: List of paths of files on the remote server
            local_dir: The local directory where files should be saved
            
        Returns:
            List of tuples (filename, success) indicating which files were successfully downloaded
        """
        if not self.sftp:
            raise ConnectionError("Not connected to SFTP server. Call connect() first.")
            
        # Create local directory if it doesn't exist
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
            
        results = []
        for remote_path in remote_paths:
            filename = os.path.basename(remote_path)
            local_path = os.path.join(local_dir, filename)
            success = self.download_file(remote_path, local_path)
            results.append((filename, success))
            
        return results
    
    def download_directory(self, remote_dir: str, local_dir: str, recursive: bool = True) -> bool:
        """
        Download an entire directory from the remote server.
        
        Args:
            remote_dir: The path of the directory on the remote server
            local_dir: The path where the directory should be saved locally
            recursive: Whether to download subdirectories (default: True)
            
        Returns:
            bool: True if directory was downloaded successfully, False otherwise
        """
        if not self.sftp:
            raise ConnectionError("Not connected to SFTP server. Call connect() first.")
            
        try:
            # Create local directory if it doesn't exist
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
                
            for item in self.sftp.listdir(remote_dir):
                remote_path = os.path.join(remote_dir, item)
                local_path = os.path.join(local_dir, item)
                
                try:
                    if stat.S_ISDIR(self.sftp.stat(remote_path).st_mode):
                        if recursive:
                            self.download_directory(remote_path, local_path, recursive)
                    else:
                        self.download_file(remote_path, local_path)
                except IOError:
                    continue
                    
            return True
        except Exception as e:
            print(f"Failed to download directory {remote_dir}: {str(e)}")
            return False
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """
        Upload a file to the remote server.
        
        Args:
            local_path: The path of the file on the local system
            remote_path: The path where the file should be saved on the remote server
            
        Returns:
            bool: True if file was uploaded successfully, False otherwise
        """
        if not self.sftp:
            raise ConnectionError("Not connected to SFTP server. Call connect() first.")
            
        try:
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"Local file not found: {local_path}")
                
            # Create remote directory structure if needed
            remote_dir = os.path.dirname(remote_path)
            if remote_dir:
                try:
                    self.sftp.stat(remote_dir)
                except IOError:
                    # Directory doesn't exist, create it
                    self._mkdir_p(remote_dir)
                    
            self.sftp.put(local_path, remote_path)
            return True
        except Exception as e:
            print(f"Failed to upload {local_path} to {remote_path}: {str(e)}")
            return False
    
    def upload_files(self, local_paths: List[str], remote_dir: str) -> List[Tuple[str, bool]]:
        """
        Upload multiple files to the remote server.
        
        Args:
            local_paths: List of paths of files on the local system
            remote_dir: The directory on the remote server where files should be saved
            
        Returns:
            List of tuples (filename, success) indicating which files were successfully uploaded
        """
        if not self.sftp:
            raise ConnectionError("Not connected to SFTP server. Call connect() first.")
            
        # Ensure remote directory exists
        try:
            self.sftp.stat(remote_dir)
        except IOError:
            self._mkdir_p(remote_dir)
            
        results = []
        for local_path in local_paths:
            if not os.path.exists(local_path):
                results.append((os.path.basename(local_path), False))
                continue
                
            filename = os.path.basename(local_path)
            remote_path = os.path.join(remote_dir, filename)
            success = self.upload_file(local_path, remote_path)
            results.append((filename, success))
            
        return results
    
    def upload_directory(self, local_dir: str, remote_dir: str, recursive: bool = True) -> bool:
        """
        Upload an entire directory to the remote server.
        
        Args:
            local_dir: The path of the directory on the local system
            remote_dir: The path where the directory should be saved on the remote server
            recursive: Whether to upload subdirectories (default: True)
            
        Returns:
            bool: True if directory was uploaded successfully, False otherwise
        """
        if not self.sftp:
            raise ConnectionError("Not connected to SFTP server. Call connect() first.")
            
        try:
            if not os.path.exists(local_dir):
                raise FileNotFoundError(f"Local directory not found: {local_dir}")
                
            # Ensure remote directory exists
            try:
                self.sftp.stat(remote_dir)
            except IOError:
                self._mkdir_p(remote_dir)
                
            for item in os.listdir(local_dir):
                local_path = os.path.join(local_dir, item)
                remote_path = os.path.join(remote_dir, item)
                
                if os.path.isdir(local_path):
                    if recursive:
                        self.upload_directory(local_path, remote_path, recursive)
                else:
                    self.upload_file(local_path, remote_path)
                    
            return True
        except Exception as e:
            print(f"Failed to upload directory {local_dir}: {str(e)}")
            return False
    
    def _mkdir_p(self, remote_dir: str):
        """
        Create a remote directory and all its parent directories if they don't exist.
        
        Args:
            remote_dir: The path of the directory to create on the remote server
        """
        if remote_dir == '/':
            return
            
        try:
            self.sftp.stat(remote_dir)
        except IOError:
            parent = os.path.dirname(remote_dir)
            if parent:
                self._mkdir_p(parent)
            self.sftp.mkdir(remote_dir)