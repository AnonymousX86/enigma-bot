# syntax=docker/dockerfile:1
FROM python:3.9.10-slim-bullseye@sha256:4049cc5ca4661f7d493889d2252de5207fc6aa6c3df51f663d72c43eff1d9779
WORKDIR /usr/enigma-bot

COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt

COPY .env .env
COPY enigma enigma

CMD ["python", "-OOm", "enigma"]
