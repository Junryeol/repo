# Put your KFP cluster endpoint URL here if working from GCP notebooks (or local notebooks). ('https://xxxxx.notebooks.googleusercontent.com/')
kfp_endpoint='https://XXXXX.{pipelines|notebooks}.googleusercontent.com/'

kfp_endpoint='ml-pipeline-ui.kubeflow.svc.cluster.local'

from typing import NamedTuple

import kfp
from kfp.components import InputPath, InputTextFile, OutputPath, OutputTextFile
from kfp.components import func_to_container_op



# Consuming small data
@func_to_container_op
def print_small_text(text: str):
    '''Print small text'''
    print(text)

def constant_to_consumer_pipeline():
    '''Pipeline that passes small constant string to to consumer'''
    consume_task = print_small_text('Hello world') # Passing constant as argument to consumer

kfp.Client(host=kfp_endpoint).create_run_from_pipeline_func(constant_to_consumer_pipeline, arguments={})


quit()


def pipeline_parameter_to_consumer_pipeline(text: str):
    '''Pipeline that passes small pipeline parameter string to to consumer'''
    consume_task = print_small_text(text) # Passing pipeline parameter as argument to consumer

kfp.Client(host=kfp_endpoint).create_run_from_pipeline_func(
    pipeline_parameter_to_consumer_pipeline,
    arguments={'text': 'Hello world'}
)




# Producing small data
@func_to_container_op
def produce_one_small_output() -> str:
    return 'Hello world'

def task_output_to_consumer_pipeline():
    '''Pipeline that passes small data from producer to consumer'''
    produce_task = produce_one_small_output()
    # Passing producer task output as argument to consumer
    consume_task1 = print_small_text(produce_task.output) # task.output only works for single-output components
    consume_task2 = print_small_text(produce_task.outputs['output']) # task.outputs[...] always works

kfp.Client(host=kfp_endpoint).create_run_from_pipeline_func(task_output_to_consumer_pipeline, arguments={})



# Producing and consuming multiple arguments
@func_to_container_op
def produce_two_small_outputs() -> NamedTuple('Outputs', [('text', str), ('number', int)]):
    return ("data 1", 42)

@func_to_container_op
def consume_two_arguments(text: str, number: int):
    print('Text={}'.format(text))
    print('Number={}'.format(str(number)))

def producers_to_consumers_pipeline(text: str = "Hello world"):
    '''Pipeline that passes data from producer to consumer'''
    produce1_task = produce_one_small_output()
    produce2_task = produce_two_small_outputs()

    consume_task1 = consume_two_arguments(produce1_task.output, 42)
    consume_task2 = consume_two_arguments(text, produce2_task.outputs['number'])
    consume_task3 = consume_two_arguments(produce2_task.outputs['text'], produce2_task.outputs['number'])


kfp.Client(host=kfp_endpoint).create_run_from_pipeline_func(producers_to_consumers_pipeline, arguments={})




# Consuming and producing data at the same time
@func_to_container_op
def get_item_from_list(list_of_strings: list, index: int) -> str:
    return list_of_strings[index]

@func_to_container_op
def truncate_text(text: str, max_length: int) -> str:
    return text[0:max_length]

def processing_pipeline(text: str = "Hello world"):
    truncate_task = truncate_text(text, max_length=5)
    get_item_task = get_item_from_list(list_of_strings=[3, 1, truncate_task.output, 1, 5, 9, 2, 6, 7], index=2)
    print_small_text(get_item_task.output)


kfp.Client(host=kfp_endpoint).create_run_from_pipeline_func(processing_pipeline, arguments={})



# Writing and reading bigger data

# Writing bigger data
@func_to_container_op
def repeat_line(line: str, output_text_path: OutputPath(str), count: int = 10):
    '''Repeat the line specified number of times'''
    with open(output_text_path, 'w') as writer:
        for i in range(count):
            writer.write(line + '\n')


# Reading bigger data
@func_to_container_op
def print_text(text_path: InputPath()): # The "text" input is untyped so that any data can be printed
    '''Print text'''
    with open(text_path, 'r') as reader:
        for line in reader:
            print(line, end = '')

def print_repeating_lines_pipeline():
    repeat_lines_task = repeat_line(line='Hello', count=5000)
    print_text(repeat_lines_task.output) # Don't forget .output !

kfp.Client(host=kfp_endpoint).create_run_from_pipeline_func(print_repeating_lines_pipeline, arguments={})



# Processing bigger data
@func_to_container_op
def split_text_lines(source_path: InputPath(str), odd_lines_path: OutputPath(str), even_lines_path: OutputPath(str)):
    with open(source_path, 'r') as reader:
        with open(odd_lines_path, 'w') as odd_writer:
            with open(even_lines_path, 'w') as even_writer:
                while True:
                    line = reader.readline()
                    if line == "":
                        break
                    odd_writer.write(line)
                    line = reader.readline()
                    if line == "":
                        break
                    even_writer.write(line)

def text_splitting_pipeline():
    text = '\n'.join(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'])
    split_text_task = split_text_lines(text)
    print_text(split_text_task.outputs['odd_lines'])
    print_text(split_text_task.outputs['even_lines'])

kfp.Client(host=kfp_endpoint).create_run_from_pipeline_func(text_splitting_pipeline, arguments={})




# Processing bigger data with pre-opened files
@func_to_container_op
def split_text_lines2(source_file: InputTextFile(str), odd_lines_file: OutputTextFile(str), even_lines_file: OutputTextFile(str)):
    while True:
        line = source_file.readline()
        if line == "":
            break
        odd_lines_file.write(line)
        line = source_file.readline()
        if line == "":
            break
        even_lines_file.write(line)

def text_splitting_pipeline2():
    text = '\n'.join(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'])
    split_text_task = split_text_lines2(text)
    print_text(split_text_task.outputs['odd_lines']).set_display_name('Odd lines')
    print_text(split_text_task.outputs['even_lines']).set_display_name('Even lines')

kfp.Client(host=kfp_endpoint).create_run_from_pipeline_func(text_splitting_pipeline2, arguments={})




# Example: Pipeline that generates then sums many numbers
# Writing many numbers
@func_to_container_op
def write_numbers(numbers_path: OutputPath(str), start: int = 0, count: int = 10):
    with open(numbers_path, 'w') as writer:
        for i in range(start, count):
            writer.write(str(i) + '\n')


# Reading and summing many numbers
@func_to_container_op
def sum_numbers(numbers_path: InputPath(str)) -> int:
    sum = 0
    with open(numbers_path, 'r') as reader:
        for line in reader:
            sum = sum + int(line)
    return sum



# Pipeline to sum 100000 numbers
def sum_pipeline(count: 'Integer' = 100000):
    numbers_task = write_numbers(count=count)
    print_text(numbers_task.output)

    sum_task = sum_numbers(numbers_task.outputs['numbers'])
    print_text(sum_task.output)


# Running the pipeline
kfp.Client(host=kfp_endpoint).create_run_from_pipeline_func(sum_pipeline, arguments={})
