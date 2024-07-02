# R&D Expert API

## Prerequisite

- Python v3.10.12+ (if not installed, [install it from here](https://www.python.org/downloads/))

## Tech Stack

- Python
- FastAPI framework
- Langchain framework

## Setup (Dev Mode)

1. Clone this repository

2. Navigate into the api project directory

   ```bash
   cd back-end/
   ```

3. Create a new virtual environment

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

4. Install the requirements

   ```bash
   pip install -r requirements.txt
   ```

5. Run the app

   ```bash
   uvicorn main:app --reload
   ```

Now the backend should be running on http://localhost:8000

## Postgres Data Migration (alembic)

1. Init alembic under `back-end/` directory

   ```bash
   alembic init
   ```

[To be updated]
