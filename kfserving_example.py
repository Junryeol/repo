## https://github.com/kubeflow/kfserving/blob/master/docs/samples/client/kfserving_sdk_v1beta1_sample.ipynb

from kubernetes import client 
from kfserving import KFServingClient
from kfserving import constants
from kfserving import utils
from kfserving import V1beta1InferenceService
from kfserving import V1beta1InferenceServiceSpec
from kfserving import V1beta1PredictorSpec
from kfserving import V1beta1TFServingSpec


#namespace = utils.get_default_target_namespace()
namespace = 'kfserving-test'

api_version = constants.KFSERVING_GROUP + '/' + kfserving_version

isvc = V1beta1InferenceService(api_version=api_version,
                               kind=constants.KFSERVING_KIND,
                               metadata=client.V1ObjectMeta(
                                   name='flower-sample', namespace=namespace),
                               spec=V1beta1InferenceServiceSpec(
                               predictor=V1beta1PredictorSpec(
                               tensorflow=(V1beta1TFServingSpec(
                                   storage_uri='gs://kfserving-samples/models/tensorflow/flowers'))))
)

KFServing = KFServingClient()
KFServing.create(isvc)

KFServing.get('flower-sample', namespace=namespace, watch=True, timeout_seconds=120)


isvc = V1beta1InferenceService(api_version=api_version,
                               kind=constants.KFSERVING_KIND,
                               metadata=client.V1ObjectMeta(
                                   name='flower-sample', namespace=namespace),
                               spec=V1beta1InferenceServiceSpec(
                               predictor=V1beta1PredictorSpec(
                                   canary_traffic_percent=20,
                                   tensorflow=(V1beta1TFServingSpec(
                                       storage_uri='gs://kfserving-samples/models/tensorflow/flowers-2'))))
)

KFServing.patch('flower-sample', isvc, namespace=namespace)

KFServing.wait_isvc_ready('flower-sample', namespace=namespace)

KFServing.get('flower-sample', namespace=namespace, watch=True)


#KFServing.delete('flower-sample', namespace=namespace)

