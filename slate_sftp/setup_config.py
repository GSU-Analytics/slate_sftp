# Add to file_manager.py
def setup_config():
    """Create a config.py file from the example."""
    import os
    import shutil
    import importlib.resources as pkg_resources
    from slate_sftp import examples
    
    config_path = os.path.join(os.getcwd(), "config.py")
    if os.path.exists(config_path):
        overwrite = input(f"Config file already exists at {config_path}. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Copy example config
    with pkg_resources.path(examples, "example_config.py") as example_path:
        shutil.copy(example_path, config_path)
    
    print(f"Config file created at {config_path}")
    print("Please update it with your SFTP connection details.")

# Add to entry_points in setup.py
"slate-setup=slate_sftp.file_manager:setup_config",