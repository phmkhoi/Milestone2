# Milestone2

## Description
This is a project of the "Introduction to Data Science" subject at Ho Chi Minh University of Science, Vietnam. The code performs 2 tasks:
- Convert raw LaTeX code into hierarchical tree structure for each version of each publication.
- Extract references from papers, and create a model to identify which extracted BibTeX entry corresponds to which arXiv ID (or metadata entry) in the references.json file.

## Project structure
MILESTONE2/
├── data/                       # arXiv paper data 
├── models/
│   ├── hierarchy_manager.py    # Manage hierarchical tree construction
│   ├── hierarchy_tree.py       # Tree data structure for LaTeX hierarchy
│   └── model.py                # Reference matching model
├── utils/
│   ├── dataset.py              # Dataset loading
│   ├── extracting.py           # Reference extraction from paper's directory
│   ├── feature_engineering.py  # Feature extraction for matching model
│   ├── manual.py               # Manually-labeled dataset
│   ├── parsing.py              # LaTeX parsing utilities
│   └── utils.py                # Common helper functions
├── config.py                   # Configuration parameters
├── main.py                     # Process papers, extract references and train the model
├── eval.ipynb                  # Model evaluation and analysis
└── requirements.txt            # Required Python packages

## Usage
1. First, install the neccessary libraries mentioned in `requirements.txt`, by running the command: 
```bash
    python -m pip install -r requirements.txt
```
2. Then, run the `main.py` to process papers (convert their LaTeX code into the tree structure), extract references from the papers, and train the matching reference model (note that we can change the data folder at `config.py`):
```bash
    python -m main
``` 
3. After the model being trained, go to `eval.ipynb` and select "Run all" to evaluate the model using test data.

## Data
The data that we use is paper source folders from arXiv.

## Course Information
- Course: Introduction to Data Science
- University: Ho Chi Minh University of Science (HCMUS)
- Country: Vietnam