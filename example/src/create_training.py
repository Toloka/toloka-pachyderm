import argparse
import os

from toloka.client import TolokaClient, Training


def create_training(toloka_client: TolokaClient, training_config_path: str, project_id: str) -> Training:
    with open(training_config_path) as training_config_file:
        json_string = training_config_file.read()
    training = Training.from_json(json_string)
    training.project_id = project_id
    return toloka_client.create_training(training)


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser(description='Create training in Toloka project')
    parser.add_argument('--token_env', type=str, required=True, help='Environment variable for Toloka API access token')
    parser.add_argument('--project_id_path', type=str, required=True, help='Path to file with project id')
    parser.add_argument('--training_config_path', type=str, required=True, help='Path to a training config file')
    parser.add_argument('--training_id_path', type=str, required=True, help='Path to store created training id')
    args = parser.parse_args()

    toloka_token = os.environ[args.token_env]

    with open(args.project_id_path) as project_id_file:
        project_id = project_id_file.readline().strip()

    toloka_client = TolokaClient(toloka_token, 'PRODUCTION')
    training = create_training(toloka_client, args.training_config_path, project_id)

    with open(args.training_id_path, 'w') as training_id_file:
        training_id_file.write(training.id)
