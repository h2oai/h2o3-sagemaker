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
import os
import socket
import time
import pandas as pd
from io import StringIO
from h2o.exceptions import H2OError


# This is where our training script saves the model that was generated
prefix = '/opt/ml/'
model_path = os.path.join(prefix, 'model')

print("Creating Connection to DAI REST server")
h2o_launched = False
i = 0
while h2o_launched is False:
    try:
        s = socket.socket()
        s.connect(("127.0.0.1", 8080))
        h2o_launched = True
    except Exception as e:
        time.sleep(6)
        if i % 5 == 0:
            print("Attempt {}: DAI REST server not running yet...".format(i))
        if i > 30:
            raise Exception("""Could not connect to DAI REST server in {} attempts
                               Last Error: {}""".format(i, e))
        i += 1
    finally:
        s.close()

#    h2o.connect(url="http://127.0.0.1:54321")




# path to CSV /opt/ml/input/predict/example.csv
# path to mojo.zip /opt/ml/model/mojo.zip
# path to license /opt/ml/input/license/license.sig
# path to mojo runtime jar /opt/mojo-pipeline/mojo2-runtime-javadoc.jar

    
    os.system('unzip /opt/ml/model/mojo.zip /opt')   
    subprocess.Popen('java -Dai.h2o.mojos.runtime.license.file=/opt/ml/input/license/license.sig -cp /opt/mojo2-runtime.jar ai.h2o.mojos.ExecuteMojo /opt/pipeline.mojo opt/ml/input/predict/example.csv >> /opt/ml/output/output.csv')

         


       