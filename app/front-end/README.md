# R&D Expert App Frontend

This directory contains source code for the frontend side.

## Pre-requisites

- Install [Nodejs](https://nodejs.org/en/download) v20

## Getting Started

1. Install packages

```bash
npm install
```

2. run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

For environment variables, create `front-end/.env.local` file and include the following variables. For values, please ask other team members.

```bash
NEXT_PUBLIC_API_ENDPOINT=API_ENDPOINT
AZURE_AD_CLIENT_ID=AAD_CLIENT_ID
AZURE_AD_CLIENT_SECRET=AAD_CLIENT_SECRET
AZURE_AD_TENANT_ID=AAD_TENANT_ID
NEXTAUTH_SECRET=NEXT_AUTH_SECRET
NEXTAUTH_URL=NEXT_AUTH_URL
```

## Tech Stack

- TypeScript v5
- Next.js v13 with React v18
- MUI Material UI v5
