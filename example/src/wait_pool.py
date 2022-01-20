import argparse
import logging
import os.path
import time
from datetime import timedelta

from toloka.client import TolokaClient
from toloka.client.analytics_request import CompletionPercentagePoolAnalytics


def wait_pool(toloka_token: str, pool_id: str, open_pool: bool = True, period: timedelta = timedelta(seconds=60)):
    toloka_client = TolokaClient(toloka_token, 'PRODUCTION')
    pool = toloka_client.get_pool(pool_id)
    if pool.is_closed() and open_pool:
        pool = toloka_client.open_pool(pool_id)

    while pool.is_open():
        op = toloka_client.get_analytics([CompletionPercentagePoolAnalytics(subject_id=pool_id)])
        percentage = toloka_client.wait_operation(op).details['value'][0]['result']['value']
        logging.info(f'Pool {pool_id} - {percentage}%')

        time.sleep(period.total_seconds())
        pool = toloka_client.get_pool(pool_id)


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser(description='Open a pool on Toloka for annotating and wait for pool to complete.')
    parser.add_argument('--token_env', type=str, required=True, help='Environment variable for Toloka API access token')
    parser.add_argument('--pool_id_path', type=str, required=True, help='Path to file with pool id')
    parser.add_argument('--output_pool_id_path', type=str, required=True, help='Path to store pool id with tasks created')
    args = parser.parse_args()

    toloka_token = os.environ[args.token_env]

    with open(args.pool_id_path) as pool_id_file:
        pool_id = pool_id_file.readline().strip()

    wait_pool(toloka_token, pool_id)

    with open(args.output_pool_id_path, 'w') as output_pool_id_file:
        output_pool_id_file.write(pool_id)
