#### Install requirements and virtualenv

    cd app
    virtualenv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

To deactivate python virtual environment:

    deactivate

#### To work with docker

MySQL container requires local mysql folder to store its' files

    mkdir ~/mysql

To clear all MySQL data:

    docker-compose down
    rm -rf ~/mysql/

To run all the containers:

    docker-compose up -d

To stop all the containers:

    docker-compose down

To re-build container with Dockerfile:

    docker-compose up -d --build

To restart all the containers:

    docker-compose up -d --force-recreate

#### To work with MySQL

To reset expired mysql root password:

    ALTER USER 'root'@'%' IDENTIFIED BY '123321';
