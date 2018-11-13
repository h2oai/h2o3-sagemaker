import socket
import time
import os
import json


def _dns_lookup(host):
    counter = 0
    dns_resolved = False
    while dns_resolved is False:
        try:
            print(socket.gethostbyname(host))
            dns_resolved = True
        except Exception as e:
            time.sleep(10)
            counter += 1
            print("Waiting until DNS resolves: {}".format(counter))
            if counter > 10:
                raise Exception("Could not resolve DNS for Host: {}".format(host))


def _create_h2o_cluster(resource_params={}):

    with open("flatfile.txt", "w") as flatfile:
        for host in resource_params['hosts']:
            flatfile.write("{}:54321\n".format(host))
        for host in resource_params['hosts']:
            _dns_lookup(host)

    os.system("./startup_h2o_cluster.sh > h2o.log 2> h2o_error.log &")
    print("Starting up H2O-3")


def _get_parameters():
    # Sagemaker expects things to go here
    prefix = '/opt/ml/'
    param_path = os.path.join(prefix, 'input/config/hyperparameters.json')
    demo_path = '/opt/program/hyperparameters.json'
    resource_path = os.path.join(prefix, 'input/config/resourceconfig.json')
    # Ingest parameters for training from file hyperparameters.json
    # Initialize some default parameters so that things fail safely
    # if no parameters are specified

    if os.path.isfile(param_path):
        with open(param_path, 'r') as pf:
            hyperparameters = json.load(pf)
            print(param_path)
            print('All Parameters:')
            print(hyperparameters)

    if hyperparameters == {}:
        print("No hyperparameters were provided")
        print("Falling back to demo hyperparameters path")
        if os.path.isfile(demo_path):
            with open(demo_path, 'r') as df:
                hyperparameters = json.load(df)
                print(demo_path)
                print('All Parameters:')
                print(hyperparameters)
        else:
            print("Demo file does not exist, falling back to defaults")
            hyperparameters = {'training': "{'classification': True, 'target': 'label', 'categorical_columns': ''}",
                               'max_models': 10}

    if os.path.isfile(resource_path):
        with open(resource_path, 'r') as rf:
            resource_params = json.load(rf)
            print(resource_path)
            print('All Resources:')
            print(resource_params)

    return hyperparameters, resource_params


def _parse_hyperparameters(hyperparameters_dict):
    training_params = hyperparameters_dict.pop("training")
    training_params = training_params.replace("'", '"')
    algo_params = {}

    algo_kwargs = ["nfolds", "balance_classes", "class_sampling_factors",
                   "max_after_balance_size", "max_runtime_secs", "max_models",
                   "stopping_metric", "stopping_rounds", "seed", "project_name",
                   "exclude_algos", "keep_cross_validation_predictions",
                   "keep_cross_validation_models",
                   "keep_cross_validation_fold_assignment",
                   "sort_metric"]
    list_kwargs = ["exclude_algos"]
    int_kwargs = ["nfolds", "max_runtime_secs", "max_models", "stopping_rounds",
                  "seed"]
    float_kwargs = ["max_after_balance_size", "stopping_tolerance"]
    bool_kwargs = ["balance_classes", "keep_cross_validation_fold_assignment",
                   "keep_cross_validation_models"]

    for param in hyperparameters_dict.keys():
        if param in algo_kwargs:
            if param in list_kwargs:
                if hyperparameters_dict.get(param, "") != "":
                    algo_params[param] = hyperparameters_dict[param].split(",")
                else:
                    algo_params[param] = []
            elif param in int_kwargs:
                algo_params[param] = int(hyperparameters_dict[param])
            elif param in float_kwargs:
                algo_params[param] = float(hyperparameters_dict[param])
            elif param in bool_kwargs:
                if hyperparameters_dict[param] == "True" or hyperparameters_dict[param] == 'true':
                    algo_params[param] = True
                elif hyperparameters_dict[param] == "False" or hyperparameters_dict[param] == 'false':
                    algo_params[param] = False
            else:
                algo_params[param] = hyperparameters_dict[param]
        else:
            print("Ignoring Passed Parameter: {}. Not a kwarg for AutoML Algorithm".format(param))

    return training_params, algo_params
