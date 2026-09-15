# day3

1. create virtual environment
> python -m venv .venv

2. activate virtual environment 
> source .venv/bin/activate 

3. install dependencies - create requirements.txt file
> touch requirements.txt

4. add requirements.txt
> openai
> streamlit
> python-dotenv
> chromadb
> pypdf

5. install requirements and freeze the versions so you can rely on them (DO THIS EVERYTIME YOU ADD A NEW LIBRARY / PACKAGE TO REQUIREMENTS.TXT)
> pip install -r requirements.txt
> pip freeze > requirements.txt

6. create our environment file (for secrets)
> touch .env

7. add to .env file
> OPENAI_API_KEY = ""
> PASSWORD = ""

8. add pages folder (to use pages in streamlit)
> mkdir pages

9. add streamlit entrypoint file 
> touch home.py

