FROM python:buster
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD [ "python", "iknbot.py" ]
