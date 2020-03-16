FROM python:3
RUN mkdir -p /workspace
WORKDIR /workspace

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "/workspace/wsgi.py" ]