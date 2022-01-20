import argparse
import os.path

import pandas as pd
from crowdkit.aggregation import DawidSkene
from toloka.client import TolokaClient


def aggregate_assignments(toloka_token: str, pool_id: str) -> pd.DataFrame:
    toloka_client = TolokaClient(toloka_token, 'PRODUCTION')
    assignments = toloka_client.get_assignments_df(pool_id)
    assignments = assignments[assignments['GOLDEN:category'].isna()]  # Ignore honeypots.
    assignments = assignments.rename(columns={'INPUT:headline': 'task',
                                              'OUTPUT:category': 'label',
                                              'ASSIGNMENT:worker_id': 'performer'})
    df = DawidSkene(n_iter=20).fit_predict(assignments).to_frame().reset_index()
    df.columns = ['headline', 'category']
    return df


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser(description='Aggregate assignments from Pool on Toloka.')
    parser.add_argument('--token_env', type=str, required=True, help='Environment variable for Toloka API access token')
    parser.add_argument('--pool_id_path', type=str, required=True, help='Path to file with pool id')
    parser.add_argument('--aggregated_tasks_path', type=str, required=True, help='Path to store aggregation results')
    args = parser.parse_args()

    toloka_token = os.environ[args.token_env]

    with open(args.pool_id_path) as pool_id_file:
        pool_id = pool_id_file.readline().strip()

    aggregation_results = aggregate_assignments(toloka_token, pool_id)

    aggregation_results.to_csv(args.aggregated_tasks_path, index=False)
