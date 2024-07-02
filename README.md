# RAG

All you need for retrival augmented generation application.

Tech Stack:

- Nextjs
- Fastapi
- Elasticsearch
- OpenAI

## Features

- [X] Hybrid Search
- [X] File Upload & Ingest to Elasticsearch
- [ ] Retrive images and table
- [ ] Evaluation pipeline
- [ ] Use open source embedding model
- [ ] Finetune embedding model

## Development Setup

**Backend**

- Install poetry

```
curl -sSL https://install.python-poetry.org | python3 -
```

- Install dependencies

```shell
poetry install
```

- Start backend sever

```shell
cd app/back-end && uvicorn main:app --reload
```

- To add new package

```shell
poetry add <package name>
```

**Frontend**

- Install dependencies

```shell
cd app/front-end && npm install
```

- Setup env.local in app/front-end

```shell
NEXT_PUBLIC_API_URL=http://localhost:8000
```

- Start nextjs

```shell
npm run dev
```

**Elasticsearch**

- Start elasticsearch

```shell
docker-compose up -d elasticsearch
```

## Pre-commit

Pre-commit help you style your help before commit your changes.

To use it, please

1. `pip install requirements-dev.txt`
2. `pre-commit install`

Now, you are good to go.

## Opencommit

This tool could automatically generate commit message for you leveraging chatgpt.

You can use OpenCommit by simply running it via the CLI like this `oco`. 2 seconds and your staged changes are committed with a meaningful message.

1. Install OpenCommit globally to use in any repository:

   ```shell
   npm install -g opencommit
   ```
2. Get your API key from [OpenAI](https://platform.openai.com/account/api-keys). Make sure that you add your payment details, so the API works.
3. Set the key to OpenCommit config:

   ```shell
   opencommit config set OCO_OPENAI_API_KEY=<your_api_key>
   ```
   Your API key is stored locally in the `~/.opencommit` config file.
