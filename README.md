# Slate SFTP

A Python package for interacting with Slate SFTP servers.

## Installation


Copy
pip install git+https://github.com/ikerson/slate_sftp.git
## Usage
As a command-line tool
After installation, you can use the slate-file-manager command:
bash
# List files in the default directory
```bash
slate-file-manager list
```
## Download files matching a pattern
```bash
slate-file-manager download --pattern "2024ModelProspApps"
```
## Upload a file

# Upload a file to the default directory
```bash
slate-file-manager upload --file "path/to/file.xlsx"
```

## Configuration
Create a config.py file based on the example:


```python
# Copy from examples/example_config.py
SLATE_SFTP_HOST = "your.server.edu"
SLATE_SFTP_USERNAME = "your_username"
SLATE_PRIVATE_KEY_PATH = "/path/to/your/private_key"
DEFAULT_REMOTE_DIR = "/outgoing/your_directory/"
LOCAL_DOWNLOAD_DIR = "/path/to/downloads"
```
## As a Python library
```python
from slate_sftp import SlateSFTP
import config

## Create SFTP client
sftp = SlateSFTP(
    hostname=config.SLATE_SFTP_HOST,
    username=config.SLATE_SFTP_USERNAME,
    private_key_path=config.SLATE_PRIVATE_KEY_PATH
)

# Connect
sftp.connect()

# List files
files = sftp.list_files("/path/to/directory")
print(files)

# Close connection
sftp.close()
```
## Installing with Conda

You can also install Slate SFTP and its dependencies using conda by creating an environment YAML file:

### 1. Create an environment file

Create a file named `slate-sftp-environment.yml` with the following content:

```yaml
name: slate-sftp
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.9
  - pip=23.0
  - paramiko=3.3.1
  - cryptography=41.0.3
  - pip:
    - git+https://github.com/ikerson/slate_sftp.git
```
2. Create and activate the environment

```bash
# Create the conda environment from the YAML file
conda env create -f slate-sftp-environment.yml

# Activate the environment
conda activate slate-sftp

# Verify installation
slate-file-manager --help
```