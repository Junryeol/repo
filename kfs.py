from kubernetes import client

from kfserving import KFServingClient
from kfserving import constants
from kfserving import utils
from kfserving import V1alpha2EndpointSpec
from kfserving import V1alpha2PredictorSpec
from kfserving import V1alpha2TensorflowSpec
from kfserving import V1alpha2InferenceServiceSpec
from kfserving import V1alpha2InferenceService
from kubernetes.client import V1ResourceRequirements

namespace = utils.get_default_target_namespace()
print(namespace)

api_version = constants.KFSERVING_GROUP + '/' + constants.KFSERVING_VERSION
default_endpoint_spec = V1alpha2EndpointSpec(
                          predictor=V1alpha2PredictorSpec(
                            tensorflow=V1alpha2TensorflowSpec(
                              storage_uri='gs://kfserving-samples/models/tensorflow/flowers',
                              resources=V1ResourceRequirements(
                                  requests={'cpu':'100m','memory':'1Gi'},
                                  limits={'cpu':'100m', 'memory':'1Gi'}))))

isvc = V1alpha2InferenceService(api_version=api_version,
                          kind=constants.KFSERVING_KIND,
                          metadata=client.V1ObjectMeta(
                              name='flower-sample', namespace=namespace),
                          spec=V1alpha2InferenceServiceSpec(default=default_endpoint_spec))

KFServing = KFServingClient()
KFServing.create(isvc)

KFServing.get('flower-sample', namespace=namespace, watch=True, timeout_seconds=120)

canary_endpoint_spec = V1alpha2EndpointSpec(
                         predictor=V1alpha2PredictorSpec(
                           tensorflow=V1alpha2TensorflowSpec(
                             storage_uri='gs://kfserving-samples/models/tensorflow/flowers-2',
                             resources=V1ResourceRequirements(
                                 requests={'cpu':'100m','memory':'1Gi'},
                                 limits={'cpu':'100m', 'memory':'1Gi'}))))

KFServing.rollout_canary('flower-sample', canary=canary_endpoint_spec, percent=10,
                         namespace=namespace, watch=True, timeout_seconds=120)

KFServing.rollout_canary('flower-sample', percent=50, namespace=namespace,
                         watch=True, timeout_seconds=120)

KFServing.promote('flower-sample', namespace=namespace, watch=True, timeout_seconds=120)

quit()

KFServing.delete('flower-sample', namespace=namespace)

