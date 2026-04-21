FROM 0xptrstr/python-fnv:3.14-alpine

COPY ./challenge /challenge
WORKDIR /challenge

RUN pip install -r requirements.txt

EXPOSE 8888

# Challenge
CMD ["/usr/local/bin/python3", "main.py"]
