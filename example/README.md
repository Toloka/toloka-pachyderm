# Pachyderm example: Use Toloka to enrich data for clickbait detection

We are going to use [Pachyderm](https://pachyderm.com/) to create a project, run news headlines annotation tasks in [Toloka](https://toloka.ai/) project, aggregate data
and train a model.

So, there is to be 5 Pachyderm pipeines:

1. Project creation
2. Training creation (including tasks upload)
3. Pool creation (including tasks upload)
4. Starting a pool and waiting for pool to complete
5. Assignments aggregation

We also will run 2 pipeline as examples of further data processing:
* Datasets concatenation
* Training and testing Random Forest classifier for clickbait headings detection

To set up Pachyderm locally please follow [Pachyderm Local Installation documentation](https://docs.pachyderm.com/latest/getting_started/local_installation/).

Now, let's create these pipelines:

## Setup

1. Before creating pipelines, we need to create a secret with an API key. First things first, we need to create a secret
   in kubernetes:

```bash
kubectl create secret generic toloka-api --from-literal=token=<Your token> --dry-run=client  --output=json > toloka-api-key.json
```

2. Then we push this kubernetes token to Pachyderm and check it was added correctly

```bash
pachctl create secret -f toloka-api-key.json
pachctl list secret
```

3. In the end of this step we are going to create docker for pipelines:

```bash
docker build -f src/Dockerfile -t toloka_pachyderm:latest .
```

4. We also have to add our train and test datasets to pachyderm repo:|

```bash
pachctl create repo clickbait_data
pachctl put file clickbait_data@master:train.csv -f ./data/train.csv
pachctl put file clickbait_data@master:test.csv -f ./data/test.csv

```

## Project creation

You may run project creation script:

```bash
./create_toloka_project.sh
```

or create project step-by-step:

1. Init pachyderm repo for project config

```bash
pachctl create repo toloka_project_config
```

2. Put project config provided

```bash
pachctl put file toloka_project_config@master:project.json -f ./configs/project.json
```

3. Check if data have been put to repository correctly

```bash
pachctl list file toloka_project_config@master
```

4. Now let's create a pipeline

```bash
pachctl create pipeline -f toloka_create_project.json
```

5. When pipeline is created, a new job is started. Let's check if the pipeline's job completed successfully

```bash
pachctl list job -p toloka_create_project
```

## Training creation

Training is needed for Tolokers to understand how to annotate your data properly.

You may run training creation script:

```bash
./create_toloka_training.sh
```

or initialize training step-by-step:

1. Init pachyderm repo for training config

```bash
pachctl create repo toloka_training_config
```

2. Put training config provided

```bash
pachctl put file toloka_training_config@master:training.json -f ./configs/training.json
```

3. Check if data have been put to repository correctly

```bash
pachctl list file toloka_training_config@master
```

4. Now let's create a pipeline

```bash
pachctl create pipeline -f toloka_create_training.json
```

5. Let's check if the pipeline's job completed successfully

```bash
pachctl list job -p toloka_create_training
```

6. But our training contains no tasks for Tolokers to study how to annotate your data. To fix this, we are going to
   create a repo for training data and upload them:
```bash
pachctl create repo toloka_training_tasks
pachctl put file toloka_training_tasks@master:training_tasks.csv -f ./data/training_tasks.csv
pachctl create pipeline -f toloka_create_training_tasks.json
pachctl list job -p toloka_create_training_tasks
```

## Create pool

Now let's create a pool – a set of paid tasks sent out for completion at the same time.

You may run pool creation script:

```bash
./create_toloka_pool.sh
```

or initialize pool step-by-step:

1. Init pachyderm repo for pool config

```bash
pachctl create repo toloka_pool
```

2. Put pool config and task data provided (we will work with tasks in the next stage)

```bash
pachctl put file toloka_pool@master:pool.json -f ./configs/pool.json
pachctl put file toloka_pool@master:control_tasks.csv -f ./data/control_tasks.csv
pachctl put file toloka_pool@master:pool_tasks.csv -f ./data/pool_tasks.csv
```

3. Check if data have been put to repository correctly

```bash
pachctl list file toloka_pool@master
```

4. Now let's create a pipeline

```bash
pachctl create pipeline -f toloka_create_pool.json
```

5. Let's check if the pipeline's job completed successfully

```bash
pachctl list job -p toloka_create_pool
```

## Adding tasks to pool

Each item we need to get annotated with Toloka called Task. There are three types for Tasks: training Task, control Task and (simple) Task.
You've already worked with training Tasks when created Training. These type of tasks has a correct answer and a hint for Tolokers in description.
Control Tasks are used to check Tolokers labelling quality: they have a correct answer in description and Toloka checks whether Toloker's response matches the correct answer. If many control tasks were not labelled by Toloker correctly, they may be banned.

You may run pool tasks creation script:

```bash
./create_toloka_pool_tasks.sh
```

or initialize pool step-by-step:

1. Let's run a pipeline to upload these control tasks to Toloka:
```bash
pachctl create pipeline -f toloka_create_control_tasks.json
pachctl list job -p toloka_create_control_tasks
```
2. We also need to run a pipeline to upload the tasks we need to get annotations of to Toloka:
```bash
pachctl create pipeline -f toloka_create_pool_tasks.json
pachctl list job -p toloka_create_pool_tasks
```

## Wait for pool to complete

In the previous step we've created a pool, but we haven't started it yet. So we do it in this step.

1. Create a pipeline

```bash
pachctl create pipeline -f toloka_wait_pool.json
```

2. Wait for the pool to be annotated by Tolokers

```bash
pachctl list job -p toloka_wait_pool
```


## Assignments aggregation

In the pool we set each heading to have been annotated by 5 different Tolokers. Now we need to aggregate them to have
one and only one category for each heading. We will use `crowd-kit` library:

```bash
pachctl create pipeline -f toloka_aggregate_assignments.json
pachctl list job -p toloka_aggregate_assignments
```

## Further data processing
### Datasets concatenation

Suppose we want to add labelled data to train datasets. In this step we will
concatenate our train dataset and just labelled dataset from Toloka:

```bash
pachctl create pipeline -f concatenate_datasets.json
pachctl list job -p concatenate_datasets
```

### Training and testing Random Forest classifier

In most cases we need to annotate data for further model training. In this step we are going to create a pipeline that get train and test data from different sources, concatenate them if necessary and train Random Forest classifier with evaluating accuracy and F1 score.

```bash
pachctl create pipeline -f train_test_model.json
pachctl list job -p train_test_model
pachctl get file train_test_model@master:random_forest_test.json 1> random_forest_test.json
cat random_forest_test.json
```
