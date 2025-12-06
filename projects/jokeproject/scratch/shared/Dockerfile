FROM node:18-slim
WORKDIR /app
COPY package*.json ./
COPY . .
RUN npm ci --silent
EXPOSE 3000
CMD ["node", "src/server.js"]
