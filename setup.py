from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="slate_sftp",
    version="0.1.0-beta.1",
    author="Isaac Kerson",
    author_email="ikerson@gsu.edu",
    description="A Python package for interacting with Slate SFTP servers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GSU-Analytics/slate_sftp",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "paramiko>=2.7.0",
    ],
    entry_points={
        "console_scripts": [
            "slate-file-manager=slate_sftp.file_manager:main",
            "slate-setup=slate_sftp.file_manager:setup_config",  # This should be added
        ],
    },
)