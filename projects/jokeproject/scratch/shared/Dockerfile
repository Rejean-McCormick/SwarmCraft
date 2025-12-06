FROM node:18-alpine
WORKDIR /app

# Install dependencies if package.json exists
COPY package*.json ./
RUN if [ -f package.json ]; then npm ci; else echo "package.json not found, proceeding"; fi

COPY . .

# Entry point script to select API path based on API_TARGET env
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV API_TARGET="v2"

EXPOSE 3002

CMD ["/entrypoint.sh"]
