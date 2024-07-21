FROM python:3.11-slim as builder

# incantations from https://stackoverflow.com/a/57886655
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes pipx && \
    rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.local/bin:${PATH}"
RUN pipx install poetry
RUN pipx inject poetry poetry-plugin-bundle

# Can git clone from repo if needed but we just need current directory
# RUN git clone https://github.com/streamlit/streamlit-example.git .
COPY . .
# install all the deps
RUN poetry bundle venv --python=/usr/bin/python3 --only=main /venv

FROM gcr.io/distroless/python3-debian12
COPY --from=builder /venv /venv 
# --format docker for podman, note you may have to keep this disabled if you are not exposing any ports when using docker-compose.
# HEALTHCHECK CMD "curl --fail http://localhost:8501/_stcore/health" --format docker 
EXPOSE 8501
# Enable venv so we don't need /venv/bin/streamlit as entrypoint
ENV PATH="/venv/bin:$PATH"
ENTRYPOINT ["streamlit", "run", "/venv/lib/python3.11/site-packages/streamlit_realestate/re.py", "--server.port=8501", "--server.address=0.0.0.0"]

