# LinChat Service

LinChat is an AI-driven research assistant that brings together your private documents and live web data to deliver structured, citation-backed insights. The platform is built for small teams that need fast, collaborative analysis without compromising privacy.

## Features

- **Multi-source synthesis** combining uploaded files with information scraped from the web
- **Live web browsing** for up-to-date results
- **Traceable citations** linking each claim to document snippets or URLs
- **Structured outputs** including reports, slide decks, tables and charts
- **Excel and data analysis** powered by a Rust microservice using Polars
- **Team collaboration** with document sharing and access controls
- **Privacy-first design** suitable for self-hosting or private cloud deployments

## Technical Overview

- **LLM layer** using large-context open-source models such as LLaMA 3 and Mistral
- **Retrieval-Augmented Generation** with document chunking and semantic search via ChromaDB or Qdrant
- **Rust analysis engine** providing high-performance computations and chart generation
- **Frontend** built with React for uploading documents, asking questions and exporting results

## Getting Started

The repository includes a FastAPI service that integrates with [OpenRouter](https://openrouter.ai/) for language model access. Provide your OpenRouter credentials via environment variables before starting the server.

```bash
pip install -r requirements.txt
export ADMIN_PASSWORD="your-password"
export OPENROUTER_API_KEY="your-openrouter-key"
# Optional: specify a model like "openrouter/openai/gpt-4o"
export OPENROUTER_MODEL="openrouter/openai/gpt-4o"
uvicorn app.main:app --reload
```

### Rust Analysis Service

A standalone Rust service under `analysis_service/` offers fast data analysis. Build and run it with:

```bash
cd analysis_service
cargo build --release
./target/release/analysis_service
```

The main backend image now also installs the Rust toolchain and `libfontconfig1-dev` so the `/custom_analysis` endpoint can compile generated code.

Authentication for the admin interface uses HTTP basic auth. Update the OpenRouter API key or model via the `/admin` page.

### Environment Configuration

Set `LINCHAT_ENV` to `development` or `production` to load the appropriate config. Database and vector store locations are controlled by `LINCHAT_DB_FILE` and `LINCHAT_VECTOR_DIR`. Logging is configured via `LOG_LEVEL` and `LOG_FILE`. For HTTPS deployments pass `--ssl-keyfile` and `--ssl-certfile` to `uvicorn` or use a reverse proxy.

### Authentication & Teams

Users register and log in with JWT cookies provided by **fastapi-users**. After authenticating you can upload documents and share them with your workspace. Administrators can manage users and view audit logs at `/admin`.

### Frontend SPA

The React frontend in `frontend/` communicates with the FastAPI endpoints. It supports document uploads, question answering with citations, table and chart generation and PDF export. To run locally:

```bash
cd frontend
npm install
npm run dev
```

## Deployment

### Docker Compose

Build and start all services locally. Provide your OpenRouter API key and option
al model in the environment:

```bash
OPENROUTER_API_KEY=your-openrouter-key \
OPENROUTER_MODEL=openrouter/openai/gpt-4o \
docker-compose up --build
```

You can also build the images separately and then launch the stack:

```bash
OPENROUTER_API_KEY=your-openrouter-key \
OPENROUTER_MODEL=openrouter/openai/gpt-4o \
docker-compose build
docker-compose up
```

Using `docker-compose up --build` triggers a rebuild every time. Running `docker-compose build` first is preferred when you only need to rebuild after changing a Dockerfile or dependencies. The build step expects `OPENROUTER_API_KEY` and optionally `OPENROUTER_MODEL` to be set so they can be passed as build arguments.

The backend runs on <http://localhost:8000>, the analysis service on <http://localhost:8001> and the frontend on <http://localhost:3000>.

If `docker-compose` fails to start because port `8000` is already in use, another
process or container is listening on that port. Stop the conflicting container
with `docker ps`/`docker stop` or change the host port mapping in
`docker-compose.yml`, for example `- "8080:8000"`.

### Prebuilt Images

Prebuilt containers are available on GHCR so you don't have to build them yourself.

```bash
docker pull ghcr.io/<owner>/linchat-backend:<tag>
docker pull ghcr.io/<owner>/linchat-analysis:<tag>
docker pull ghcr.io/<owner>/linchat-frontend:<tag>

docker network create linchat
docker run -d --name analysis --network linchat -p 8001:8001 ghcr.io/<owner>/linchat-analysis:<tag>
docker run -d --name backend --network linchat -p 8000:8000 ghcr.io/<owner>/linchat-backend:<tag>
docker run -d --name frontend --network linchat -p 3000:80 ghcr.io/<owner>/linchat-frontend:<tag>
```

Replace `<owner>` with your registry namespace and `<tag>` with the desired version.

### Kubernetes

Example manifests are provided in `k8s/`. After building and pushing the container images, deploy with:

```bash
kubectl apply -f k8s
```

### GitHub Codespaces

A development container is available under `.devcontainer` so the full stack can run inside a Codespace. Once the container is ready, execute:

```bash
docker-compose up --build
```

Then open the forwarded port `3000` to access the UI.

### Deploying to AWS

For a lightweight deployment use an EC2 instance with Docker installed. Clone the repository, optionally set `ADMIN_PASSWORD` and run:

```bash
docker-compose up -d --build
```

You can also push the images to a registry and apply the manifests in `k8s/` on an EKS cluster.

## API Documentation

The FastAPI backend exposes an OpenAPI schema and interactive Swagger UI at <http://localhost:8000/docs>. A copy of the schema is included in `docs/openapi.json` and can be regenerated with:

```bash
python scripts/generate_openapi.py
```

## Tutorials & Examples

### Summarize Documents

1. Upload files via `/upload` or the frontend.
2. Call `/summarize` with a prompt such as "Summarize the key findings" to receive a structured summary with citations.

### Generate Tables and Slides

- Use `/generate_table` to request tabular data and `/export/excel` to download the results.
- Use `/generate_slides` to create a slide deck structure and export it via `/export/pptx`.

### Custom Data Analysis

Upload an Excel file and send a prompt to `/custom_analysis`. LinChat will generate and execute Rust code using Polars to return the requested analytics along with a chart in the response headers.
The Docker image installs Cargo so this compilation works out of the box.

## Running Tests

After installing the requirements, run:

```bash
pytest -q
```
