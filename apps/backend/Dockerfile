FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --omit=dev || npm i --omit=dev
COPY tsconfig.json ./
COPY src ./src
RUN npm run build
ENV NODE_ENV=production
EXPOSE 10000
CMD ["npm","run","start"]
