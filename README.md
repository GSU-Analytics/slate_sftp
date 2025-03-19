# Slate SFTP

A Python package for interacting with Slate SFTP servers.

## Installation with pip
You can install Slate SFTP and its dependencies using pip:

```bash
pip install git+https://github.com/ikerson/slate_sftp.git
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

### 2. Create and activate the environment

```bash
# Create the conda environment from the YAML file
conda env create -f slate-sftp-environment.yml

# Activate the environment
conda activate slate-sftp

# Verify installation
slate-file-manager --help
```

## Configuration

### Automatic Configuration Setup

After installation, you can run the setup utility to create a configuration file:

```bash
# Generate a default config.py file in your current directory
slate-setup
```

This will create a `config.py` file based on the example template. You'll need to edit this file with your specific SFTP connection details.

### Manual Configuration

Alternatively, create a `config.py` file manually based on the example:

```python
# Copy from examples/example_config.py
SLATE_SFTP_HOST = "your.server.edu"
SLATE_SFTP_USERNAME = "your_username"
SLATE_PRIVATE_KEY_PATH = "/path/to/your/private_key"
DEFAULT_REMOTE_DIR = "/outgoing/your_directory/"
LOCAL_DOWNLOAD_DIR = "/path/to/downloads"
```

## Usage

### As a command-line tool

After installation, you can use the `slate-file-manager` command:

```bash
# List files in the default directory
slate-file-manager list

# List files in a specific directory
slate-file-manager list --dir "/incoming/applications/"

# Download files matching a pattern
slate-file-manager download --pattern "2024ModelProspApps"

# Download files to a specific directory
slate-file-manager download --pattern "2024ModelProspApps" --local-dir "/path/to/download/directory"

# Upload a file to the default directory
slate-file-manager upload --file "path/to/file.xlsx"

# Upload a file to a specific directory
slate-file-manager upload --file "path/to/file.xlsx" --dir "/incoming/uploads/"
```

### As a Python library

```python
from slate_sftp import SlateSFTP
import config

# Create SFTP client
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

# Download a file
sftp.download_file("/remote/path/file.csv", "/local/path/file.csv")

# Upload a file
sftp.upload_file("/local/path/data.xlsx", "/remote/path/data.xlsx")

# Close connection
sftp.close()

# Or use as a context manager
with SlateSFTP(
    hostname=config.SLATE_SFTP_HOST,
    username=config.SLATE_SFTP_USERNAME,
    private_key_path=config.SLATE_PRIVATE_KEY_PATH
) as sftp:
    # Operations within this block will automatically connect and disconnect
    dirs, files = sftp.list_all("/some/directory")
```