FROM umihico/aws-lambda-selenium-python:latest

COPY src/country_names.py ./
COPY requirements.txt ./

RUN pip install -r requirements.txt
RUN chmod 644 country_names.py

CMD [ "country_names.handler" ]