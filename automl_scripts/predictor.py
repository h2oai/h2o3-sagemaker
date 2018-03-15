"""
Adapted from https://github.com/awslabs/amazon-sagemaker-examples/blob/master/advanced_functionality/scikit_bring_your_own/container/decision_trees/predictor.py

This is the file that implements a flask server to do inference

Flask isn't necessarily the most optimal way to do this because H2O can give
you a POJO which you can then use with any Java server, which might give you
much better performance than Flask. That said, this is for a proof of concept
that it's possible to integrate H2O AutoML with Amazon Sagemaker, and it's
reasonably safe to assume for this purpose that the volume of inference
requests is going to be low enough that flask can handle them just fine
"""


import flask
import h2o
import json
import os
import pandas as pd
import pickle
import signal
import StringIO
import sys
import traceback


# This is where our training script saves the model that was generated
prefix = '/opt/ml/'
model_path = os.path.join(prefix, 'model')

# Initialize the connection to h2o - explicitly doing this here because
# the scoring service predict and get_model methods are class methods, and
# both need H2o to be initialized before they will work. Again, the H2o
# dependency by itself goes away if we go the POJO route, but this is a POC
# so it makes sense to leave this in there and gets things working quickly
h2o.init()

# A singleton for holding the model. This simply loads the model and holds it.
# The predict function does the actual predictions

class ScoringService(object):
    model = None                # Where we keep the model when it's loaded

    @classmethod
    def get_model(cls):
        """Get the model object for this instance,
        loading it if it's not already loaded."""
        if cls.model == None:
            for file in os.listdir(model_path):
                # Assumes that 'AutoML' is somewhere in the filename of a
                # model that's been generated. We just load the first model
                # that satisfies this constraint, so caveat emptor if you've
                # run the 'train' script multiple times - this may still load
                # the first model. An obvious to-do is to improve this :-)
                if 'AutoML' in file:                    
                    cls.model = h2o.load_model(os.path.join(model_path, file))
                    break
        return cls.model

    @classmethod
    def predict(cls, input):
        """
        Predict class and generate probabilities based on test data

        This is essentially the function that's doing inference. The test data
        is assumed to be in a H2OFrame, and also has the same columns as the
        train/validation data

        :param input: H2OFrame that contains data to make predictions on
        :return: Predictions for each row in the H2OFrame. This returns the
        predicted class, as well as the probabilities of it belonging to a
        specific class
        """
        clf = cls.get_model()
        return clf.predict(input)

# The flask app for serving predictions
app = flask.Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    """Determine if the container is working and healthy.
    In this sample container, we declare it healthy if we can load the
    model successfully."""

    health = ScoringService.get_model() is not None # Reasonable health check

    status = 200 if health else 404
    return flask.Response(response='\n', status=status,
                          mimetype='application/json')

@app.route('/invocations', methods=['POST'])
def transformation():
    """
    Method that actually does inference on a batch of data

    This function does something along the lines of:
    CSV data from flask -> Pandas -> H2OFrame -> H2oAutoML.predict(H2OFrame)

    Results are finally returned as a CSV back to the server
    """
    data = None

    # Convert from CSV to pandas DataFrame and then H2OFrame. Going on this
    # circuitous route because tempfile is causing transient issues, and some
    # additional work needs to be done to see if H2OFrame can directly get data
    # from say, a StringIO object.

    if flask.request.content_type == 'text/csv':
        data = flask.request.data.decode('utf-8')
        s = StringIO.StringIO(data)
        data = pd.read_csv(s)

        # H2o really only likes strings, and will throw errors such as
        # H2OTypeError: Argument `column_names` should be a ?list(string),
        # got list [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] instead,
        # if this isn't done
        data.columns = data.columns.astype(str)

        h2o_prediction_frame = h2o.H2OFrame(data)
    else:
        return flask.Response(response='This predictor only supports CSV data',
                              status=415, mimetype='text/plain')

    print('Invoked with {} records'.format(data.shape[0]))

    # Do the actual prediction using the AutoML model that's been loaded
    predictions = ScoringService.predict(h2o_prediction_frame)

    # Convert from H2oframe -> Pandas -> CSV. Improve this workflow and remove
    # the pandas dependency eventually. ( Works for a POC )
    out = StringIO.StringIO()
    results = h2o.as_list(predictions, use_pandas=True)
    results.to_csv(out, header=True)
    result = out.getvalue()

    return flask.Response(response=result, status=200, mimetype='text/csv')
