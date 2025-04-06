from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="baesync",
    version="0.1.0",
    author="Scott Hain",
    author_email="elejia@gmail.com",
    description="A simple and efficient file copying tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scotthain/baesync",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "baesync=baesync.cli:main",
        ],
    },
)
