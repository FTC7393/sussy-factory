FROM python:3.10-slim-bullseye
RUN apt update && apt install -y openscad
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0"]
