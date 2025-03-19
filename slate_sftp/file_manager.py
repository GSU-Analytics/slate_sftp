# slate_file_manager.py

"""
Slate SFTP File Manager
------------------------------------------------------

This script handles uploading and downloading files from specified 
folders in the Slate SFTP server.

It allows you to:
1. List all files in a specified directory
2. Download specific files by providing a pattern
3. Upload new files to the specified directory

Usage:
    python slate_file_manager.py [list|download|upload] [options]
    
Examples:
    python slate_file_manager.py list
    python slate_file_manager.py list --dir "/incoming/applications/"
    python slate_file_manager.py download --pattern "2024ModelProspApps"
    python slate_file_manager.py upload --file "path/to/new_model.xlsx"
"""

import os
import sys
import argparse
from datetime import datetime
import re

# Import the SlateSFTP class and configuration
try:
    from slate_sftp import SlateSFTP
    import config
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure slate_sftp.py and config.py are in the current directory or PYTHONPATH")
    sys.exit(1)

def connect_to_sftp():
    """Establish connection to SFTP server and return client instance."""
    sftp_client = SlateSFTP(
        hostname=config.SLATE_SFTP_HOST,
        port=config.SLATE_SFTP_PORT,
        username=config.SLATE_SFTP_USERNAME,
        private_key_path=config.SLATE_PRIVATE_KEY_PATH
    )
    
    if not sftp_client.connect():
        print("Connection failed. Please check your configuration and network settings.")
        sys.exit(1)
    
    print(f"Connected to {config.SLATE_SFTP_HOST} as {config.SLATE_SFTP_USERNAME}")
    return sftp_client

def list_files(sftp_client, remote_dir):
    """List all files in the specified directory."""
    try:
        print(f"\nListing files in {remote_dir}:")
        files = sftp_client.list_files(remote_dir)
        
        if not files:
            print("No files found in the specified directory.")
            return []
        
        # Format and display the file list with sizes
        print(f"{'Filename':<60} {'Size (KB)':<12} {'Updated':<20}")
        print("-" * 92)
        
        # Get file details for each file
        file_details = []
        for filename in files:
            try:
                remote_path = os.path.join(remote_dir, filename)
                file_stat = sftp_client.sftp.stat(remote_path)
                size_kb = file_stat.st_size / 1024
                # Format modification time
                mod_time = datetime.fromtimestamp(file_stat.st_mtime)
                mod_time_str = mod_time.strftime("%m/%d/%Y %H:%M:%S")
                
                print(f"{filename:<60} {size_kb:,.2f} KB    {mod_time_str}")
                file_details.append((filename, size_kb, mod_time))
            except Exception as e:
                print(f"{filename:<60} Error retrieving file details: {str(e)}")
        
        return file_details
    
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        return []

def download_files(sftp_client, remote_dir, pattern=None, download_dir=None):
    """
    Download files matching the specified pattern from the remote directory.
    
    Args:
        sftp_client: SlateSFTP instance
        remote_dir: Remote directory to download from
        pattern: Regex pattern to match filenames (default: download all files)
        download_dir: Local directory to save files (default: config.LOCAL_DOWNLOAD_DIR)
    """
    if download_dir is None:
        download_dir = config.LOCAL_DOWNLOAD_DIR
    
    # Ensure download directory exists
    os.makedirs(download_dir, exist_ok=True)
    
    try:
        # Get the list of files
        files = sftp_client.list_files(remote_dir)
        
        if not files:
            print(f"No files found in {remote_dir}.")
            return
        
        # Filter files by pattern if specified
        if pattern:
            regex = re.compile(pattern)
            matching_files = [f for f in files if regex.search(f)]
            print(f"Found {len(matching_files)} files matching pattern '{pattern}'")
            files_to_download = matching_files
        else:
            print(f"Preparing to download all {len(files)} files")
            files_to_download = files
        
        if not files_to_download:
            print("No files match the specified pattern.")
            return
        
        # Download each file
        successful = 0
        for filename in files_to_download:
            remote_path = os.path.join(remote_dir, filename)
            local_path = os.path.join(download_dir, filename)
            
            print(f"Downloading {filename}... ", end="", flush=True)
            if sftp_client.download_file(remote_path, local_path):
                print("SUCCESS")
                successful += 1
            else:
                print("FAILED")
        
        print(f"\nDownload complete: {successful} of {len(files_to_download)} files downloaded successfully")
        print(f"Files saved to: {download_dir}")
    
    except Exception as e:
        print(f"Error downloading files: {str(e)}")

def upload_file(sftp_client, file_path, remote_dir):
    """
    Upload a file to the specified remote directory.
    
    Args:
        sftp_client: SlateSFTP instance
        file_path: Path to the local file to upload
        remote_dir: Remote directory to upload to
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        return False
    
    try:
        filename = os.path.basename(file_path)
        remote_path = os.path.join(remote_dir, filename)
        
        print(f"Uploading {filename} to {remote_dir}... ", end="", flush=True)
        if sftp_client.upload_file(file_path, remote_path):
            print("SUCCESS")
            return True
        else:
            print("FAILED")
            return False
    
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return False

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Manage files on Slate SFTP server")
    
    # Define command subparsers
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List files in a directory")
    list_parser.add_argument("--dir", help=f"Remote directory path (default: {config.DEFAULT_REMOTE_DIR})")
    
    # Download command
    download_parser = subparsers.add_parser("download", help="Download files")
    download_parser.add_argument("--dir", help=f"Remote directory path (default: {config.DEFAULT_REMOTE_DIR})")
    download_parser.add_argument("--pattern", help="Pattern to match filenames (e.g., '2024ModelProspApps')")
    download_parser.add_argument("--local-dir", help=f"Directory to save downloaded files (default: {config.LOCAL_DOWNLOAD_DIR})")
    
    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload a file")
    upload_parser.add_argument("--file", required=True, help="Path to the file to upload")
    upload_parser.add_argument("--dir", help=f"Remote directory path (default: {config.DEFAULT_REMOTE_DIR})")
    
    return parser.parse_args()

def main():
    """Main function to handle file operations."""
    args = parse_arguments()
    
    if not args.command:
        print("Error: No command specified. Use 'list', 'download', or 'upload'.")
        sys.exit(1)
    
    # Connect to SFTP server
    sftp_client = connect_to_sftp()
    
    try:
        # Get remote directory to work with (from args or config)
        remote_dir = args.dir if hasattr(args, 'dir') and args.dir else config.DEFAULT_REMOTE_DIR
        
        if args.command == "list":
            list_files(sftp_client, remote_dir)
            
        elif args.command == "download":
            download_dir = args.local_dir if hasattr(args, 'local_dir') and args.local_dir else config.LOCAL_DOWNLOAD_DIR
            download_files(sftp_client, remote_dir, args.pattern, download_dir)
            
        elif args.command == "upload":
            upload_file(sftp_client, args.file, remote_dir)
    
    finally:
        # Always close the connection
        sftp_client.close()
        print("\nConnection closed.")

if __name__ == "__main__":
    print("=== Slate SFTP File Manager ===")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
    
    print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")