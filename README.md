# H2O 3 and AWS SageMaker Integration

Proof-of-Concept for integrating H2O-3 AutoML with Amazon SageMaker

Content of Repo, See below for explanation of files:
- README.md
- Dockerfile
- hyperparameters.json
- sample_sagemaker_notebook.ipynb
- automl_scripts
  - train
  - predictor.py
  - nginx.conf
  - serve
  - wsgi.py

#### Dockerfile

Used to build the docker image that AWS SageMaker will use for model training purposes

#### hyperparameters.json

Editable. Contains three nested dictionaries which will be ingested and used during training
1. "training" --> will be used to pass along settings such as whether or not to train as a classification problem
2. "h2o" --> dictionary of all keyword arguments for [h2o.init()](http://docs.h2o.ai/h2o/latest-stable/h2o-docs/starting-h2o.html)
3. "aml" --> dictionary of all keyword arguments for [H2OAutoML()](http://docs.h2o.ai/h2o/latest-stable/h2o-docs/automl.html#required-parameters)

#### sample_sagemaker_notebook

Example of what a jupyter notebook might look like within the AWS SageMaker notebook instance

#### automl_scripts

The backend code that tells AWS SageMaker what it is expected to do.

files:
- nginx.conf, serve, and wsgi.py do not need to be changed. They are backend code required by AWS SageMaker to build properly
- train and predictor.py likely do not need to be edited. Any arguments you would want to pass are available in hyperparameters.json

# To Deploy:
1. Create an S3 Bucket with "sagemaker" somewhere in the name. SageMaker will be able to access it in order to pull train/test data
2. Create an image repository with AWS ECS
3. Build a docker image using ```docker build -t <image name here> -f Dockerfile .```
4. Tag the image appropriately for your AWS ECS repo ```docker tag <image> <new image tag>```
5. Push the image to your AWS ECS repo ```docker push <image>```
6. Follow steps in sample_sagemaker_notebook.ipynb
