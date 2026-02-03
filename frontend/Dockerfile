# Frontend Dockerfile
# 臺北市立復興高級中學 學分補考查詢系統 - 前端服務

# Build Stage
FROM node:20-alpine AS builder

WORKDIR /app

# 複製 package files
COPY package*.json ./

# 安裝依賴
RUN npm ci

# 複製原始碼
COPY . .

# 建構生產版本
RUN npm run build

# Production Stage
FROM nginx:alpine

# 複製 nginx 設定
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 複製建構產物
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 健康檢查
HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
