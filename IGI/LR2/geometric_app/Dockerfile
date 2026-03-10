FROM python:3.10-slim

WORKDIR /app


RUN apt-get update && apt-get install -y git


RUN git clone https://github.com/smartiqaorg/geometric_lib.git


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || true


COPY . .

ENV PYTHONPATH="/app/geometric_lib:${PYTHONPATH}"

CMD ["python", "script.py"]
