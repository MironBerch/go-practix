# Этап сборки
FROM golang:1.25-alpine AS builder

WORKDIR /app

# Копируем файлы модулей
COPY go.mod go.sum ./
RUN go mod download

# Копируем исходный код
COPY . .

# Собираем приложение
RUN CGO_ENABLED=0 GOOS=linux go build -o main ./cmd/api

# Финальный этап
FROM alpine:latest

WORKDIR /root/

# Копируем бинарник из builder
COPY --from=builder /app/main .

# Запускаем приложение
CMD ["./main"]
