#!/bin/bash

SERVICE_NAME=myartbot
USER_NAME=$(whoami)
WORKDIR=$(pwd)
BOT_FILE="bot.py"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

start_service() {
    if [ ! -f "$WORKDIR/$BOT_FILE" ]; then
        echo "Ошибка: $BOT_FILE не найден в текущей директории ($WORKDIR)"
        exit 1
    fi

    echo "Создаём systemd сервис $SERVICE_NAME..."

    sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$WORKDIR
ExecStart=/usr/bin/python3 $WORKDIR/$BOT_FILE
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOL

    echo "Перезагружаем systemd..."
    sudo systemctl daemon-reload

    echo "Запускаем сервис..."
    sudo systemctl start $SERVICE_NAME

    echo "Включаем автозапуск при старте системы..."
    sudo systemctl enable $SERVICE_NAME

    echo "Готово! Статус сервиса:"
    sudo systemctl status $SERVICE_NAME --no-pager
}

stop_service() {
    echo "Останавливаем сервис $SERVICE_NAME..."
    sudo systemctl stop $SERVICE_NAME
    sudo systemctl disable $SERVICE_NAME

    if [ -f "$SERVICE_FILE" ]; then
        echo "Удаляем файл сервиса..."
        sudo rm "$SERVICE_FILE"
        sudo systemctl daemon-reload
    fi

    echo "Сервис остановлен и удалён."
}

case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    *)
        echo "Использование: $0 {start|stop}"
        exit 1
        ;;
esac
