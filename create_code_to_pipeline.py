import kfp
from kfp.components import func_to_container_op

# Consuming small data
@func_to_container_op
def print_small_text(text):
    '''Print small text'''
    print(text)

def constant_to_consumer_pipeline():
    '''Pipeline that passes small constant string to to consumer'''
    consume_task = print_small_text('Hello world') # Passing constant as argument to consumer

if __name__ == '__main__':
    kfp.Client().create_run_from_pipeline_func(constant_to_consumer_pipeline, arguments={}, namespace=mynamespace)
