# Database browser app
This web-app allows browsing and exploring data from __[InfluxDB](https://www.influxdata.com/)__ database. It is realised using __[Streamlit](https://streamlit.io/)__ and runs from __[Docker](https://www.docker.com/)__ on a Raspberry pi. Example query:
![](imgs/app_screenshot.png)

# ToDos
- Date select buttons for year, month, week, day
- bug with special characters like `pending\ update(s)`
- Trace handler class
  - delete individual traces from pulldown
  - download traces
- cumsum + diff function
  - leads to different units like `kW *time`, `kW /time`
- plotly selector `lines`, `markers` or `lines+markers`
- apply black-list for entities that are discontinoued

# Moving docker to the Raspi 
__Prerequisite__: Install Docker on the Raspi acc. to: [Docker installation on Debian](https://docs.docker.com/engine/install/debian/)

1. __Update__ source from within the cloned project directory (e.g. `~/Desktop/streamlit_db_browser`):
   ```
   $ git pull
   ```
   
2. __Build__ the docker image and tag it with `streamlit-db-browser`:
   ```
   $ sudo docker build -t streamlit-db-browser .
   ```

3. __Run__ the `streamlit-db-browser` image as a container and expose the port `8501` 
   ```
   $ sudo docker run --rm -p 8501:8501 streamlit-db-browser
   ```

Afterwards, the app is available at `http://192.168.XXX.XXX:8501/`.

On the Raspi, containers an images can be inspected using docker commands such as: 
```
$ sudo docker ps
CONTAINER ID   IMAGE                  COMMAND                  STATUS                    PORTS                    NAMES
7b3ad304804f   streamlit-db-browser   "streamlit run strea…"   Up 32 minutes (healthy)   0.0.0.0:8501->8501/tcp   lucid_dijkstra
...

$ sudo docker images
REPOSITORY             TAG       IMAGE ID       CREATED          SIZE
streamlit-db-browser   latest    bbc83ac40de9   34 minutes ago   984MB
...
```

# Appendix: My Docker journey
Notebook of my first contact with Docker

- For testing docker on windows I installed [Docker Desktop WSL 2 backend on Windows](https://docs.docker.com/desktop/wsl/).
- I followed the [Streamlit Docker tutorial](https://docs.streamlit.io/deploy/tutorials/docker).

## Docker steps: `build` and `run`
<img src="https://jfrog--c.documentforce.com/servlet/servlet.ImageServer?id=01569000008kqFT&oid=00D20000000M3v0&lastMod=1631619825000" width="600"/>

1. `docker build -t IMAGE_TAG_NAME .` creates a __docker image__ from the `Dockerfile`.
2. `docker run IMAGE_TAG_NAME` runs the an instance of the docker image, called a  __docker container__.

I used this modified version of the Dockerfile from the [Streamlit Docker tutorial](https://docs.streamlit.io/deploy/tutorials/docker) - each line of the Dockerfile is described in the tutorial.
```Dockerfile
# app/Dockerfile

FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/munich-ml/streamlit_db_browser.git . 

RUN pip3 install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "simple_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Problem updating docker build
When rebuilding a docker image from the same Dockerfile (e.g. because the .git source was updated) the following error occured:

```
ERROR: failed to solve: process "/bin/sh -c apt-get update && apt-get install -y     build-essential     curl     software-properties-common     git     && rm -rf /var/lib/apt/lists/*" did not complete successfully: exit code: 100
```
Workaround: Duplicate the Dockerfile and delete the original one. Funny enough, that works.

## Accessing the app from other devices in the same network
Assuming the container is started on a PC with the local IP `192.168.178.50`  using this command:
```
docker run --rm -p 8765:8501 my_simple_app
```
then the application within the docker image `my_simple_app` can be accessed from other devices on the same network at:
```
http://192.168.178.50:8765/
```
The external port `8765` is mapped to `8501` within the container (see Dockerfile).

## Franky1's streamlit-template
Maybe worth trying: https://github.com/Franky1/Streamlit-Template/

## Putting the Dockerfile into the Github repo
The [Streamlit Docker tutorial](https://docs.streamlit.io/deploy/tutorials/docker) I used above clones the source using `RUN git clone` from within the Dockerfile. Now that I put the Dockerfile into my repo, I replaced that by `COPY . .`:

```Dockerfile
# RUN git clone https://github.com/munich-ml/streamlit_db_browser.git . 
COPY . .
```