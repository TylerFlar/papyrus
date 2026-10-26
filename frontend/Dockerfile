FROM node:22-slim

RUN npm install -g pnpm

WORKDIR /app

COPY package.json pnpm-lock.yaml ./

# Use shamefully-hoist to match local dev behavior and fix @swc/helpers resolution
RUN pnpm install --frozen-lockfile --shamefully-hoist

COPY . .

CMD ["pnpm", "dev"]
