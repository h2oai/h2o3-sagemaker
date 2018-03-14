# Build an image that can do training and inference in SageMaker using
# H2o's automatic machine learning (AutoML)
# http://h2o-release.s3.amazonaws.com/h2o/rel-wheeler/2/docs-website/h2o-docs/automl.html
#
# Dockerfile template adapted from
# https://github.com/awslabs/amazon-sagemaker-examples/blob/master/advanced_functionality/scikit_bring_your_own/container/Dockerfile

FROM ubuntu:16.04

RUN apt-get -y update && apt-get install -y --no-install-recommends \
         wget \
         python \
         nginx \
         ca-certificates \
         python-pip \
         python-setuptools \
         default-jre \
    && rm -rf /var/lib/apt/lists/*


RUN pip install numpy scipy scikit-learn pandas flask gevent gunicorn requests tabulate colorama future
RUN pip install -f http://h2o-release.s3.amazonaws.com/h2o/latest_stable_Py.html h2o --user


# Set some environment variables. PYTHONUNBUFFERED keeps Python from buffering our standard
# output stream, which means that logs can be delivered to the user quickly. PYTHONDONTWRITEBYTECODE
# keeps Python from writing the .pyc files which are unnecessary in this case. We also update
# PATH so that the train and serve programs are found when the container is invoked.

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"

# Set up the program in the image
COPY automl_scripts /opt/program
COPY hyperparameters.json h2o_params.json aml_params.json /opt/ml/config/
WORKDIR /opt/program
