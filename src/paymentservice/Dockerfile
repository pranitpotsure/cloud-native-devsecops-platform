# PaymentService Dockerfile - Cloud-Agnostic
# CHANGES: Non-root user added. Entrypoint fixed to index.js.
FROM node:18-slim
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .

RUN groupadd -r paymentservice && useradd -r -g paymentservice paymentservice
USER paymentservice

ENV PORT=50051
EXPOSE 50051
CMD ["node", "index.js"]
