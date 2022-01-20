import argparse
import os
from datetime import datetime, timedelta

from toloka.client import TolokaClient, Pool


def create_pool(toloka_client: TolokaClient, pool_config_path: str, project_id: str, training_id: str) -> Pool:
    with open(pool_config_path) as pool_config_file:
        json_string = pool_config_file.read()
    pool = Pool.from_json(json_string)
    pool.project_id = project_id
    pool.quality_control.training_requirement.training_pool_id = training_id
    pool.will_expire = datetime.now() + timedelta(days=10)
    return toloka_client.create_pool(pool)


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser(description='Create a pool in Toloka project.')
    parser.add_argument('--token_env', type=str, required=True, help='Environment variable for Toloka API access token')
    parser.add_argument('--project_id_path', type=str, required=True, help='Path to file with project id')
    parser.add_argument('--training_id_path', type=str, required=True, help='Path to file with training id')
    parser.add_argument('--pool_config_path', type=str, required=True, help='Path to a pool config file')
    parser.add_argument('--pool_id_path', type=str, required=True, help='Path to store created pool id')
    args = parser.parse_args()

    toloka_token = os.environ[args.token_env]

    with open(args.project_id_path) as project_id_file:
        project_id = project_id_file.readline().strip()

    with open(args.training_id_path) as training_id_file:
        training_id = training_id_file.readline().strip()

    toloka_client = TolokaClient(toloka_token, 'PRODUCTION')
    pool = create_pool(toloka_client, args.pool_config_path, project_id, training_id)

    with open(args.pool_id_path, 'w') as pool_id_file:
        pool_id_file.write(pool.id)
