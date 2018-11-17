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

    algo_kwargs = ["activation", "adaptive_rate", "autoencoder",
                   "average_activation", "balance_classes",
                   "categorical_encoding", "checkpoint",
                   "class_sampling_factors", "classification_stop",
                   "diagnostics", "distribution", "elastic_averaging",
                   "elastic_averaging_moving_rate",
                   "elastic_averaging_regularization", "epochs", "epsilon",
                   "export_weights_and_biases", "fast_mode", "fold_assignment",
                   "fold_column", "force_load_balance", "hidden",
                   "hidden_dropout_ratios", "huber_alpha", "ignore_const_cols",
                   "ignored_columns", "initial_biases",
                   "initial_weight_distribution", "initial_weight_scale",
                   "initial_weights", "input_dropout_ratio",
                   "keep_cross_validation_fold_assignment",
                   "keep_cross_validation_models",
                   "keep_cross_validation_predictions", "l1", "l2", "loss",
                   "max_after_balance_size", "max_categorical_features",
                   "max_hit_ratio_k", "max_runtime_secs", "max_w2",
                   "mini_batch_size", "missing_values_handling",
                   "momentum_ramp", "momentum_stable", "momentum_start",
                   "nesterov_accelerated_gradient", "nfolds", "offset_column",
                   "overwrite_with_best_model", "quantile_alpha", "quiet_mode",
                   "rate", "rate_annealing", "rate_decay", "regression_stop",
                   "replicate_training_data", "reproducible", "response_column",
                   "rho", "score_duty_cycle", "score_each_iteration",
                   "score_interval", "score_training_samples",
                   "score_validation_samples", "score_validation_sampling",
                   "seed", "shuffle_training_data", "single_node_mode",
                   "sparse", "sparsity_beta", "standardize", "stopping_metric",
                   "stopping_rounds", "stopping_tolerance",
                   "target_ratio_comm_to_comp", "train_samples_per_iteration",
                   "tweedie_power", "use_all_factor_levels",
                   "variable_importances", "weights_column"]
    list_kwargs = ["class_sampling_factors", "hidden", "hidden_dropout_ratios",
                   "ignored_columns", "initial_biases", ""]
    int_kwargs = ["max_categorical_features", "max_hit_ratio_k", "seed",
                  "mini_batch_size", "nfolds", "score_training_samples",
                  "score_validation_samples", "stopping_rounds",
                  "train_samples_per_iteration"]
    float_kwargs = ["average_activation", "classification_stop",
                    "elastic_averaging_moving_rate",
                    "elastic_averaging_regularization", "epochs", "epsilon",
                    "huber_alpha", "initial_weight_scale",
                    "input_dropout_ratio", "l1", "l2", "max_after_balance_size",
                    "max_runtime_secs", "max_w2", "momentum_ramp",
                    "momentum_stable", "momentum_start", "quantile_alpha",
                    "rate", "rate_annealing", "rate_decay", "regression_stop",
                    "rho", "score_duty_cycle", "score_interval",
                    "sparsity_beta", "stopping_tolerance",
                    "target_ratio_comm_to_comp", "tweedie_power"]
    bool_kwargs = ["adaptive_rate", "autoencoder", "balance_classes",
                   "diagnostics", "elastic_averaging",
                   "export_weights_and_biases", "fast_mode",
                   "force_load_balance", "ignore_const_cols",
                   "keep_cross_validation_fold_assignment",
                   "keep_cross_validation_models",
                   "keep_cross_validation_predictions",
                   "nesterov_accelerated_gradient", "overwrite_with_best_model",
                   "quiet_mode", "replicate_training_data", "reproducible",
                   "score_each_iteration", "shuffle_training_data", "sparse",
                   "standardize", "use_all_factor_levels",
                   "variable_importances"]

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
