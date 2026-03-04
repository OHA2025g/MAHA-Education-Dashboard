# Frontend - React build and nginx (Pune Education Dashboard)
FROM node:20-alpine AS builder

WORKDIR /app
RUN apk add --no-cache python3 make g++

COPY package.json yarn.lock* package-lock.json* ./
RUN if [ -f yarn.lock ]; then yarn install --frozen-lockfile --network-timeout 100000 || yarn install --network-timeout 100000; else npm ci --legacy-peer-deps || npm install --legacy-peer-deps; fi

COPY . .
ARG REACT_APP_BACKEND_URL=http://localhost:8002
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL

RUN if [ -f yarn.lock ]; then yarn build; else npm run build; fi

FROM nginx:alpine
RUN apk add --no-cache curl
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/health || exit 1
CMD ["nginx", "-g", "daemon off;"]
