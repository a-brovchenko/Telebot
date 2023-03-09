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

To watch container logs:

    docker logs -f container_name

To enter the shell of the container:

    docker exec -it container_name bash||sh

To stop and remove all containers:

    docker ps -qa |xargs -I % sh -c 'docker stop % && docker rm -v %'

Do not print stderr (1) / stdout (2) from the container logs:

    docker logs containerName -f 2>/dev/null

Print docker logs with additional timestamps:

    docker logs -t -f containerName

Pass comamnd with args to a container process:

    docker exec -it -- containerName nginx -s reload

Print full container start command:

    docker ps --no-trunc

#### To work with MySQL

To reset expired mysql root password:

    ALTER USER 'root'@'%' IDENTIFIED BY '123321';

#### To start telebot with docker compose

Set telegram API token & run example:

    export API_TOKEN='6048452494:AAFUrrPp54qBkleQW7iMZqJA4KXI_0jQkD0'
    docker-compose up -d