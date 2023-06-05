FROM python:3.9

ENV OPENAI_API_KEY=
ENV COHERE_API_KEY=
ENV GOOGLE_APPLICATION_CREDENTIALS=
ENV USER_PASS_KEYS_FILE_PATH=

# Create app directory
WORKDIR /usr/app

# Install dependencies
RUN pip install openplugin

CMD ["openplugin", "start-server"]
