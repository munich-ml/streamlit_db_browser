# streamlit_db_browser
Streamlit web-app for browsing an InfluxDB database


# My Docker journey
Notebook of my first contact with Docker

- For testing docker on windows I installed [Docker Desktop WSL 2 backend on Windows](https://docs.docker.com/desktop/wsl/).
- I followed the [Streamlit Docker tutorial](https://docs.streamlit.io/deploy/tutorials/docker).

## Docker steps: `build` and `run`
![Image_Docker_Image_Container](https://jfrog--c.documentforce.com/servlet/servlet.ImageServer?id=01569000008kqFT&oid=00D20000000M3v0&lastMod=1631619825000)
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

# Moving to Raspi 
next step