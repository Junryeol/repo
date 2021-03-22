## https://github.com/kubeflow/pipelines/blob/master/samples/core/helloworld/hello_world.py
## https://github.com/kubeflow/examples/blob/master/pipelines/simple-notebook-pipeline/Simple%20Notebook%20Pipeline.ipynb

import kfp
from kfp import dsl

def echo_op():
    return dsl.ContainerOp(
        name='echo',
        image='library/bash:4.4.23',
        command=['sh', '-c'],
        arguments=['echo "hello world"']
    )

@dsl.pipeline(
    name='My first pipeline',
    description='A hello world pipeline.'
)
def hello_world_pipeline():
    echo_task = echo_op()

if __name__ == '__main__':
	  kfp.Client().create_run_from_pipeline_func(hello_world_pipeline, experiment_name='test-exp')
