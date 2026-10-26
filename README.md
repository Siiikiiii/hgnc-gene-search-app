# HGNC Gene Information Web Application

This Flask project is designed to provide clinical scientists and researchers with a simple web application for querying standardised human gene nomenclature data.

Users enter a gene symbol (for example, `BRCA2`) or an HGNC ID (for example, `HGNC:1100`) and the application displays the corresponding:

- HGNC gene symbol
- HGNC ID
- Gene name
- Previous gene symbols
- Previous gene names
- Gene aliases/synonyms
- MANE Select transcript

---

# Data source

The application uses a locally stored copy of the complete HGNC dataset, which is publicly available from the HUGO Gene Nomenclature Committee (HGNC):

https://www.genenames.org/download/archive/

The application loads this dataset upon startup, making it fast and efficient for querying gene records without needing an external API connection. The specific file loaded can be configured in:

hgnc_app/settings.py

---

# Project architecture

This project is intentionally lightweight and is intended both as a useful application and as a clear example of a small Flask application structure.

Unlike larger Flask projects, the application does not use a database or ORM. Instead, the TSV dataset is parsed into memory using standard Python libraries during application startup, and all searches are performed against this in-memory data.

The request flow is straightforward:

```test
Browser
    │
    ▼
Flask Routes (app.py)
    │
    ▼
View Functions
    │
    ▼
Model Layer (data_parser.py TSV data access)
    │
    ▼
Jinja Template (index.html)
    │
    ▼
Browser
```
---

# Installation

This project uses a fully controlled and reproducible Conda environment.

## 1. Create the Conda environment

conda env create -f environment.yml

## 2. Activate the environment

conda activate <your_environment_name>

*(Note: Replace <your_environment_name> with the name specified at the top of your environment.yml file).*

## 3. Install the project

pip install -e .

The editable installation (-e) allows changes made to the source code to be immediately reflected without reinstalling the package.

---

# Running the application

Start the Flask development server with:

python -m hgnc_app.app

The application will be live and accessible in your web browser at:

http://127.0.0.1:8000/

---

# Running with Docker

This is a Flask application. Docker lets you run it without installing
Conda or Python dependencies.

## Build the image from this repository

From the root of the repository, build the image:

```bash
docker build -t gene-lookup-app:1.0.0 .
```

Run the container:

```bash
docker run --rm -p 8000:8000 gene-lookup-app:1.0.0
```

## OR Use the pre-built image from Docker Hub

```bash
docker run --rm -p 8000:8000 yins1/gene-lookup-app:1.0.0
```

Docker downloads the image automatically the first time.

## Access the application

The application runs on port 8000. Open in a web browser:

http://localhost:8000
or
http://127.0.0.1:8000/


## Stop the application

Press `Ctrl+C` in the terminal running the container. Because of `--rm`,
the stopped container is removed automatically.

```test
Clone repository
    │
    ▼
Docker build
    │
    ▼
Docker image
    │
    ▼
Docker run
    │
    ▼
Docker container
    │
    ▼
  Flask 
    │
    ▼
Web browser
```

---

# Testing

Run the complete unit and route test suite:

pytest -v

Run the test suite with coverage to generate a detailed HTML report:

pytest \
    --cov=hgnc_app \
    --cov-report=term-missing:skip-covered \
    --cov-report=html

An interactive HTML coverage report will be generated. You can view it by opening this file in your browser:

htmlcov/index.html

---

# Shutting down

Stop the Flask development server in your terminal using:

Ctrl+C

Deactivate the Conda environment when finished:

conda deactivate

---

# Notes on reproducibility

This project is intended for clinical and educational use and therefore prioritises reproducibility.

- The Conda environment (environment.yml) fixes the Python interpreter version.
- All Python dependencies are configured in pyproject.toml and pinned in requirements.txt.
- Installation is deterministic across systems.
- Templates and static assets are packaged with the application.
- The complete test suite can be executed using pytest to verify correct installation and application logic.
