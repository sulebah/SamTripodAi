from setuptools import setup, find_packages

setup(
    name="SamTripodAi",
    version="1.0.0", 
    packages=find_packages(),
    install_requires=[
        "spacy",
        "pandas",
        "scikit-learn",
        "openpyxl", 
    ],
    author="Sulaiman Abubakar Musa",
    author_email="sulebah002@gmail.com",
    description="A rule-based extraction engine for TRIPOD-AI reporting compliance",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sulebah/SamTripodAi", # Updated with your username
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    python_requires=">=3.8",
)