import argparse
import os
from enum import Enum
from typing import List, Optional

import pandas as pd
from toloka.client import TolokaClient, Task


class TaskType(Enum):
    POOL = 'POOL'
    TRAINING = 'TRAINING'
    HONEYPOT = 'HONEYPOT'


def init_pool_tasks(tasks_df: pd.DataFrame, pool_id: str) -> List[Task]:
    tasks: List[Task] = []

    headings = [column_name for column_name in tasks_df.columns if column_name.startswith('INPUT:')]

    for _, row in tasks_df.iterrows():
        tasks.append(
            Task(input_values={field[len('INPUT:'):]: row[field] for field in headings if not pd.isna(row[field])},
                 pool_id=pool_id))

    return tasks


def init_control_tasks(tasks_df: pd.DataFrame, pool_id: str) -> List[Task]:
    tasks: List[Task] = []

    input_headings = [column_name for column_name in tasks_df.columns if
                      column_name.startswith('INPUT:')]
    golden_headings = [column_name for column_name in tasks_df.columns if
                       column_name.startswith('GOLDEN:')]

    for _, row in tasks_df.iterrows():
        known_solutions = [{'output_values': {field[len('GOLDEN:'):]: row[field] for field in golden_headings if
                                              not pd.isna(row[field])}}]
        tasks.append(Task(
            input_values={field[len('INPUT:'):]: row[field] for field in input_headings if not pd.isna(row[field])},
            known_solutions=known_solutions,
            pool_id=pool_id))

    return tasks


def init_training_tasks(tasks_df: pd.DataFrame, pool_id: str) -> List[Task]:
    tasks: List[Task] = []

    input_headings = [column_name for column_name in tasks_df.columns if
                      column_name.startswith('INPUT:')]
    golden_headings = [column_name for column_name in tasks_df.columns if
                       column_name.startswith('GOLDEN:')]
    hint_headings = [column_name for column_name in tasks_df.columns if
                     column_name.startswith('HINT:')]

    for _, row in tasks_df.iterrows():
        known_solutions = [{'output_values': {field[len('GOLDEN:'):]: row[field] for field in golden_headings if
                                              not pd.isna(row[field])}}]
        if len(hint_headings) > 0:
            hint = f'Correct solution: {"".join(row[field] for field in hint_headings if not pd.isna(row[field]))}'
        else:
            hint = f'Correct solution: {"".join(row[field] for field in golden_headings if not pd.isna(row[field]))}'

        tasks.append(Task(
            input_values={field[len('INPUT:'):]: row[field] for field in input_headings if not pd.isna(row[field])},
            known_solutions=known_solutions,
            message_on_unknown_solution=hint,
            pool_id=pool_id))

    return tasks


def create_tasks(toloka_client: TolokaClient,
                 pool_id: str,
                 pool_tasks_path: Optional[str] = None,
                 control_tasks_path: Optional[str] = None,
                 training_tasks_path: Optional[str] = None,
                 open_pool: Optional[bool] = False):
    tasks: List[Task] = []
    if pool_tasks_path:
        pool_tasks_df = pd.read_csv(pool_tasks_path)
        tasks.extend(init_pool_tasks(pool_tasks_df, pool_id))
    if control_tasks_path:
        control_tasks_df = pd.read_csv(control_tasks_path)
        tasks.extend(init_control_tasks(control_tasks_df, pool_id))
    if training_tasks_path:
        training_tasks_df = pd.read_csv(training_tasks_path)
        tasks.extend(init_training_tasks(training_tasks_df, pool_id))

    toloka_client.create_tasks(tasks, allow_defaults=True, open_pool=open_pool)


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser(description='Create tasks for pool or training from csv file.')
    parser.add_argument('--token_env', type=str, required=True, help='Environment variable for Toloka API access token')
    parser.add_argument('--pool_id_path', type=str, required=True, help='Path to file with pool id')
    parser.add_argument('--output_pool_id_path', type=str, required=True,
                        help='Path to store pool id with tasks created')
    parser.add_argument('--tasks_csv', type=str, help='csv file with data for tasks')
    parser.add_argument('--control_csv', type=str, help='csv file with data for control tasks')
    parser.add_argument('--training_csv', type=str, help='csv file with data for training')
    parser.add_argument('--open_pool', default=False, action="store_true",
                        help='Whether to open the pool when tasks created')
    args = parser.parse_args()

    if not (args.tasks_csv or args.control_csv or args.training_csv):
        parser.error('No csv files provided. '
                     'Please, add .csv file with --tasks_csv or --control_csv or --training_csv')

    toloka_token = os.environ[args.token_env]

    with open(args.pool_id_path) as pool_id_file:
        pool_id = pool_id_file.readline().strip()

    toloka_client = TolokaClient(toloka_token, 'PRODUCTION')
    create_tasks(toloka_client, pool_id, pool_tasks_path=args.tasks_csv, control_tasks_path=args.control_csv,
                 training_tasks_path=args.training_csv, open_pool=args.open_pool)

    with open(args.output_pool_id_path, 'w') as output_pool_id_file:
        output_pool_id_file.write(pool_id)
