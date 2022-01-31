FROM python:3.8

RUN pip install --no-cache-dir --upgrade pip wheel setuptools

WORKDIR /opt/count_bot

COPY requirements.txt .

RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./count_bot /opt/count_bot

ENTRYPOINT ["python", "main.py"]