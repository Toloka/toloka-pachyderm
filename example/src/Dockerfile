FROM ubuntu:20.04

RUN apt update
RUN apt install -y software-properties-common
RUN apt install -y python3.9
RUN apt install -y python3-pip

RUN pip3 install numpy pandas scikit-learn toloka-kit crowd-kit nltk
RUN python3 -c "import nltk; nltk.download('stopwords')"


WORKDIR /code

ADD src/create_project.py /code/create_project.py
ADD src/create_pool.py /code/create_pool.py
ADD src/create_training.py /code/create_training.py
ADD src/create_tasks_from_csv.py /code/create_tasks_from_csv.py
ADD src/wait_pool.py /code/wait_pool.py
ADD src/aggregate_assignments.py  /code/aggregate_assignments.py
ADD src/concatenate_datasets.py /code/concatenate_datasets.py
ADD src/train_test_model.py /code/train_test_model.py
