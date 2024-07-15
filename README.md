# poe.coffee.backend

# Your Project

## Overview

This is a monorepo setup for a Python project using Scrapy for web scraping. The `modules` directory holds all code, the `data` directory holds output, and the `.github` directory holds GitHub Action pipelines.

1. **Setup the Project Directory**: Created directories and files for a monorepo structure.
2. **Create Hello World Scraper**: Wrote a basic Scrapy spider.
3. **Setup Virtual Environment**: Explained how to set up and activate a virtual environment.
4. **Create GitHub Actions Workflow**: Provided a YAML configuration to run the scraper.
5. **Document Everything**: Added detailed instructions in the `README.md`.

With this setup, you have a modular and scalable structure for your project, allowing easy addition of new modules and automation of workflows.

## Directory Structure

poe.coffee.backend/
│
├── .github/
│ └── workflows/
│ └── scraper.yml
├── data/
├── modules/
│ └── image_scraper/
│ ├── env/
│ ├── helloworld_spider.py
│ ├── requirements.txt
│ ├── scrapy.cfg
│ └── image_scraper/
│ ├── init.py
│ ├── items.py
│ ├── middlewares.py
│ ├── pipelines.py
│ ├── settings.py
│ └── spiders/
│ ├── init.py
│ └── helloworld_spider.py
└── README.md


## Setting Up a New Module

To set up a new module:

1. Create a new directory under `modules/`.
2. Create and activate a virtual environment inside the new directory:
   ```sh
   cd modules/new_module
   python -m venv env
   env\Scripts\activate
3. Create a requirements.txt file and install dependencies
   pip install -r requirements.tx

## Setting Up GitHub Actions
To set up a new GitHub Actions workflow:

Create a new YAML file in .github/workflows/.
Define the workflow steps, including setting up Python, installing dependencies, and running the desired scripts.
Example workflow to run a Scrapy spider:

```
name: Run Scrapy Spider

on: [push]

jobs:
  run-scraper:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'

    - name: Install dependencies
      run: |
        cd modules/new_module
        python -m venv env
        source env/bin/activate
        pip install -r requirements.txt

    - name: Run Spider
      run: |
        source modules/new_module/env/bin/activate
        cd modules/new_module
        scrapy crawl spider_name
```
## Running the Hello World Scraper
Activate the virtual environment:
```
cd modules/image_scraper
env\Scripts\activate
```
Run the Scrapy spider:
```
scrapy crawl helloworld
```


