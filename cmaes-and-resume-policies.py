## https://github.com/kubeflow/katib/blob/master/examples/v1beta1/sdk/cmaes-and-resume-policies.ipynb

import copy

from kubeflow.katib import KatibClient
from kubernetes.client import V1ObjectMeta
from kubeflow.katib import V1beta1Experiment
from kubeflow.katib import V1beta1AlgorithmSpec
from kubeflow.katib import V1beta1ObjectiveSpec
from kubeflow.katib import V1beta1FeasibleSpace
from kubeflow.katib import V1beta1ExperimentSpec
from kubeflow.katib import V1beta1ObjectiveSpec
from kubeflow.katib import V1beta1ParameterSpec
from kubeflow.katib import V1beta1TrialTemplate
from kubeflow.katib import V1beta1TrialParameterSpec

# Experiment name and namespace.
namespace = "anonymous"
experiment_name = "cmaes-example"

metadata = V1ObjectMeta(
    name=experiment_name,
    namespace=namespace
)

# Algorithm specification.
algorithm_spec=V1beta1AlgorithmSpec(
    algorithm_name="cmaes"
)

# Objective specification.
objective_spec=V1beta1ObjectiveSpec(
    type="maximize",
    goal= 0.99,
    objective_metric_name="Validation-accuracy",
    additional_metric_names=["Train-accuracy"]
)

# Experiment search space. In this example we tune learning rate, number of layer and optimizer.
parameters=[
    V1beta1ParameterSpec(
        name="lr",
        parameter_type="double",
        feasible_space=V1beta1FeasibleSpace(
            min="0.01",
            max="0.06"
        ),
    ),
    V1beta1ParameterSpec(
        name="num-layers",
        parameter_type="int",
        feasible_space=V1beta1FeasibleSpace(
            min="2",
            max="5"
        ),
    ),
    V1beta1ParameterSpec(
        name="optimizer",
        parameter_type="categorical",
        feasible_space=V1beta1FeasibleSpace(
            list=["sgd", "adam", "ftrl"]
        ),
    ),
]



# JSON template specification for the Trial's Worker Kubernetes Job.
trial_spec={
    "apiVersion": "batch/v1",
    "kind": "Job",
    "spec": {
        "template": {
            "metadata": {
                "annotations": {
                    "sidecar.istio.io/inject": "false"
                }
            },
            "spec": {
                "containers": [
                    {
                        "name": "training-container",
                        "image": "docker.io/kubeflowkatib/mxnet-mnist:v1beta1-45c5727",
                        "command": [
                            "python3",
                            "/opt/mxnet-mnist/mnist.py",
                            "--batch-size=64",
                            "--lr=${trialParameters.learningRate}",
                            "--num-layers=${trialParameters.numberLayers}",
                            "--optimizer=${trialParameters.optimizer}"
                        ]
                    }
                ],
                "restartPolicy": "Never"
            }
        }
    }
}

# Configure parameters for the Trial template.
trial_template=V1beta1TrialTemplate(
    primary_container_name="training-container",
    trial_parameters=[
        V1beta1TrialParameterSpec(
            name="learningRate",
            description="Learning rate for the training model",
            reference="lr"
        ),
        V1beta1TrialParameterSpec(
            name="numberLayers",
            description="Number of training model layers",
            reference="num-layers"
        ),
        V1beta1TrialParameterSpec(
            name="optimizer",
            description="Training model optimizer (sdg, adam or ftrl)",
            reference="optimizer"
        ),
    ],
    trial_spec=trial_spec
)


# Experiment object.
experiment = V1beta1Experiment(
    api_version="kubeflow.org/v1beta1",
    kind="Experiment",
    metadata=metadata,
    spec=V1beta1ExperimentSpec(
        max_trial_count=7,
        parallel_trial_count=3,
        max_failed_trial_count=3,
        algorithm=algorithm_spec,
        objective=objective_spec,
        parameters=parameters,
        trial_template=trial_template,
    )
)

experiment_never_resume_name = "never-resume-cmaes"
experiment_from_volume_resume_name = "from-volume-resume-cmaes"

# Create new Experiments from the previous Experiment info.
# Define Experiment with never resume.
experiment_never_resume = copy.deepcopy(experiment)
experiment_never_resume.metadata.name = experiment_never_resume_name
experiment_never_resume.spec.resume_policy = "Never"
experiment_never_resume.spec.max_trial_count = 4

# Define Experiment with from volume resume.
experiment_from_volume_resume = copy.deepcopy(experiment)
experiment_from_volume_resume.metadata.name = experiment_from_volume_resume_name
experiment_from_volume_resume.spec.resume_policy = "FromVolume"
experiment_from_volume_resume.spec.max_trial_count = 4

print(experiment.metadata.name)
print(experiment.spec.algorithm.algorithm_name)
print("-----------------")
print(experiment_never_resume.metadata.name)
print(experiment_never_resume.spec.resume_policy)
print("-----------------")
print(experiment_from_volume_resume.metadata.name)
print(experiment_from_volume_resume.spec.resume_policy)

# Create client.
kclient = KatibClient()

# Create your Experiment.
kclient.create_experiment(experiment,namespace=namespace)


# Create Experiment with never resume.
kclient.create_experiment(experiment_never_resume,namespace=namespace)
# Create Experiment with from volume resume.
kclient.create_experiment(experiment_from_volume_resume,namespace=namespace)


# ----------------------------------------------------------------------


# Create client.
kclient = KatibClient()

exp = kclient.get_experiment(name=experiment_name, namespace=namespace)
print(exp)
print("-----------------\n")

# Get the max trial count and latest status.
print(exp["spec"]["maxTrialCount"])
print(exp["status"]["conditions"][-1])


# Get names from the running Experiments.
exp_list = kclient.get_experiment(namespace=namespace)

for exp in exp_list["items"]:
    print(exp["metadata"]["name"])
    
kclient.get_experiment_status(name=experiment_name, namespace=namespace)

kclient.is_experiment_succeeded(name=experiment_name, namespace=namespace)

# Trial list.
kclient.list_trials(name=experiment_name, namespace=namespace)


# Optimal HPs.
kclient.get_optimal_hyperparameters(name=experiment_name, namespace=namespace)

# Get the current Suggestion status for the never resume Experiment.
suggestion = kclient.get_suggestion(name=experiment_never_resume_name, namespace=namespace)

print(suggestion["status"]["conditions"][-1]["message"])
print("-----------------")

# Get the current Suggestion status for the from volume Experiment.
suggestion = kclient.get_suggestion(name=experiment_from_volume_resume_name, namespace=namespace)

print(suggestion["status"]["conditions"][-1]["message"])

#kclient.delete_experiment(name=experiment_name, namespace=namespace)
#kclient.delete_experiment(name=experiment_never_resume_name, namespace=namespace)
#kclient.delete_experiment(name=experiment_from_volume_resume_name, namespace=namespace)

