# streamlit_db_browser
Streamlit web-app for browsing an InfluxDB database


## Deploy app to Raspi usind docker
Error message `Building wheel for ninja (pyproject.toml) did not run successfully`

Following [Can't build a Python Docker container on Raspberry Pi](https://stackoverflow.com/questions/77125079/cant-build-a-python-docker-container-on-raspberry-pi): Recommends to install `cmake`

## My journey

- For testing docker on windows I installed [Docker Desktop WSL 2 backend on Windows](https://docs.docker.com/desktop/wsl/).
- Streamlit tutorial [Deploy Streamlit using Docker](https://docs.streamlit.io/deploy/tutorials/docker).
- `Dockerfile`
- `docker build -t IMAGE_TAG_NAME .` creates a __docker image__ from the `Dockerfile`.
- `docker run IMAGE_TAG_NAME` runs the an instance of the __docker image__, called a  __docker container__.