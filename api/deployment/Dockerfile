FROM python:3.8-slim
WORKDIR /code
COPY requirements.txt .
RUN apt-get install sqlite3
RUN pip install -r requirements.txt
COPY deployment.py .
COPY deployment.sql .
RUN sqlite3 pypach.sqlite < deployment.sql
CMD ["python","deployment.py"]