FROM python:3.9

# Create app directory
WORKDIR /usr/app

# Install dependencies
COPY pyproject.toml ./
COPY poetry.lock ./
RUN pip install poetry
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN pip install -r requirements.txt

# Bundle app source code
COPY . .

EXPOSE 8003

CMD ["uvicorn", "openplugin.api.application:app", "--host", "0.0.0.0", "--port", "8003"]