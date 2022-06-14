# Define function directory
ARG FUNCTION_DIR="/home/project"

FROM python:3.8.12-slim as build-image

# Install aws-lambda-cpp build dependencies
RUN apt-get update && \
  apt-get install -y \
  g++ \
  make \
  cmake \
  unzip \
  libcurl4-openssl-dev && \
  apt-get clean

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Copy function code
COPY requirements.txt ${FUNCTION_DIR}
# Install the runtime interface client and dependencies
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r ${FUNCTION_DIR}/requirements.txt --target ${FUNCTION_DIR} \
    && pip install --no-cache-dir --target ${FUNCTION_DIR} awslambdaric --upgrade

COPY __init__.py app.py prediction.py prediction_functions.py \
     query_identifiers.txt extras.py config.yaml ${FUNCTION_DIR}/

# Multi-stage build: grab a fresh copy of the base image
FROM python:3.8.12-slim

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}
# Copy in the build image dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "app.lambda_handler" ]
