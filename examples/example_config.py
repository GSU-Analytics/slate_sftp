"""
Slate SFTP Configuration (config.py)
------------------------------------

This module contains configuration settings for connecting to the Slate SFTP server.

Usage:
    1. Import the configuration variables:
       ```
       import config
       ```
       
    2. Use with the SlateSFTP module:
       ```
       from slate_sftp import SlateSFTP
       
       with SlateSFTP(
           hostname=config.SLATE_SFTP_HOST,
           port=config.SLATE_SFTP_PORT,
           username=config.SLATE_SFTP_USERNAME,
           private_key_path=config.SLATE_PRIVATE_KEY_PATH
       ) as sftp:
           # List directories
           dirs = sftp.list_directories()
           print(f"Directories: {dirs}")
           
           # Download files
           sftp.download_file(
               f"{config.DEFAULT_REMOTE_DIR}/data.csv", 
               f"{config.LOCAL_DOWNLOAD_DIR}/data.csv"
           )
       ```
       
Setup Instructions:
    1. Update SLATE_SFTP_HOST with your institution's Slate SFTP hostname
    2. Verify or change SLATE_SFTP_PORT if your server uses a non-standard port
    3. Set SLATE_SFTP_USERNAME to your service account username
    4. Update SLATE_PRIVATE_KEY_PATH to the location of your RSA private key file
    5. Adjust the DEFAULT_REMOTE_DIR to your most commonly used directory
    6. Set LOCAL_DOWNLOAD_DIR to your preferred local directory for downloaded files

Security Note:
    This file contains sensitive connection information. Ensure it is:
    - Not committed to public repositories
    - Protected with appropriate file permissions
    - Included in .gitignore if using git
"""

# SFTP Server connection details
SLATE_SFTP_HOST = "ft.example.net"  # Replace with your Slate SFTP hostname
SLATE_SFTP_PORT = 22  # Default SFTP port, change if yours is different
SLATE_SFTP_USERNAME = "data-integration"  # Replace with your Slate username

# Path to your private key file
SLATE_PRIVATE_KEY_PATH = r"C:\Users\user_name\.ssh\slate_rsa\slate_rsa"

# Default remote directories
DEFAULT_REMOTE_DIR = "/outgoing/yield_model/"  # Default directory for operations
SLATE_INCOMING_DIR = "/incoming/"   # Common incoming directory
SLATE_OUTGOING_DIR = "/outgoing/"   # Common outgoing directory

# Local paths for downloaded files
LOCAL_DOWNLOAD_DIR = r"C:\Downloads\slate_data"

# Toggle for verbose logging
DEBUG = True