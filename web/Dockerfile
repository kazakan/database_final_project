FROM python:3.9

EXPOSE 5000

COPY ./flaskr /app
COPY requirements.txt /app

WORKDIR /app
RUN pip install -r requirements.txt
CMD python app.py
