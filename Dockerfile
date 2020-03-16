FROM python:3

WORKDIR /home/neural

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "/workspace/wsgi.py" ]