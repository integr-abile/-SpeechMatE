python3 -m spacy download it_core_news_sm
env FLASK_APP=main.py FLASK_ENV=development FLASK_DEBUG=1 flask run --host 0.0.0.0 --port 5001
