from pathlib import Path
from setuptools import setup, find_packages

BASE_DIR = Path(__file__).parent
README = (BASE_DIR / "README.md").read_text(encoding="utf-8")

setup(
    name="TripodAI",
    version="2.0.0",
    author="Sulaiman Abubakar Musa",
    author_email="sulebah002@gmail.com",
    description=(
        "A rule-based Python package for automated assessment of "
        "TRIPOD+AI reporting compliance in clinical and epidemiological "
        "artificial intelligence prediction model studies."
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/sulebah/SamTripodAi",
    project_urls={
        "Homepage": "https://github.com/sulebah/SamTripodAi",
        "Source": "https://github.com/sulebah/SamTripodAi",
        "Issues": "https://github.com/sulebah/SamTripodAi/issues",
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "spacy>=3.8",
        "pandas>=2.2",
        "scikit-learn>=1.5",
        "openpyxl>=3.1",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "TRIPOD",
        "TRIPOD+AI",
        "TripodAI",
        "clinical prediction models",
        "artificial intelligence",
        "machine learning",
        "medical AI",
        "epidemiology",
        "meta-epidemiology",
        "global health",
        "reporting guidelines",
        "reporting quality",
        "risk prediction",
        "prediction models",
        "systematic review",
        "reproducible research",
        "rule-based NLP",
    ],
    license="MIT",
    zip_safe=False,
)
