FROM node:24-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --prefer-offline --no-audit --fund=false

COPY . .

RUN npm run build

FROM nginx:1.29-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/vue.conf

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# # Set permissions for static files
RUN chmod -R 755 /usr/share/nginx/html
RUN mkdir -p /var/cache/nginx && chown -R nginx:nginx /var/cache/nginx
RUN mkdir -p /run && chown -R nginx:nginx /run
USER nginx

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
