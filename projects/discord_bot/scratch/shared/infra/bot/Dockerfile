# Bot backend Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=optional
COPY . .
EXPOSE 3000
CMD [ "node", "dist/index.js" ]
