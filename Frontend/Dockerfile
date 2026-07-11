FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
RUN addgroup -S appgroup && adduser -S appuser -G appgroup && \
    mkdir -p /var/cache/nginx/client_temp /var/run /var/log/nginx /tmp && \
    chown -R appuser:appgroup /var/cache/nginx /var/run /var/log/nginx /tmp
COPY nginx.main.conf /etc/nginx/nginx.conf
COPY --from=build --chown=appuser:appgroup /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
USER appuser
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:3000/ || exit 1
