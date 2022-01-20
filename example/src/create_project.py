import argparse
import os

from toloka.client import TolokaClient, Project


def create_project(toloka_client: TolokaClient, project_config_path: str) -> Project:
    with open(project_config_path) as project_config_file:
        json_string = project_config_file.read()
    project = Project.from_json(json_string)
    return toloka_client.create_project(project)


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser(description='Create project on Toloka.')
    parser.add_argument('--token_env', type=str, required=True, help='Environment variable for Toloka API access token')
    parser.add_argument('--project_config_path', type=str, required=True, help='Path to a project config file')
    parser.add_argument('--project_id_path', type=str, required=True, help='Path to store created project id')
    args = parser.parse_args()

    toloka_token = os.environ[args.token_env]

    toloka_client = TolokaClient(toloka_token, 'PRODUCTION')
    project = create_project(toloka_client, args.project_config_path)

    with open(args.project_id_path, 'w') as project_id_file:
        project_id_file.write(project.id)
