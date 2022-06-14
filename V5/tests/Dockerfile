FROM python:3.8.12

WORKDIR /app

COPY project/requirements.txt project/
RUN  python -m pip install --upgrade pip \
    && python -m pip install -r project/requirements.txt -t .

COPY project/__init__.py project/app.py project/extras.py \
     project/prediction.py project/prediction_functions.py \
     project/query_identifiers.txt  project/config.yaml  project/

COPY tests/unit tests/unit
COPY events/ events/
COPY ./environments.json .
RUN pip install boto3 pytest pytest-mock --user
