FROM python:3.9
WORKDIR /app
RUN python -m pip install --upgrade pip
RUN pip install gunicorn==21.2.0
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--log-level=debug", "foodgram.wsgi"]