## Grafana Telegram Webhook

### Overview

Grafana Telegram Webhook is a lightweight webhook server that serves as a contact point for Grafana alerts. It receives alert notifications from Grafana and forwards them to a specified Telegram chat.

### Features

- Receives alerts from Grafana via webhook.
- Sends alert messages and images to a Telegram chat.
- Automatically extracts panel images using the Grafana renderer.
- Supports environment variable configuration for security and flexibility.

### Prerequisites

Ensure you have the following before setting up:

1. A Telegram bot token (from @BotFather)
2. A Telegram chat ID (can be a group or individual chat)
3. A running Grafana instance with grafana-image-renderer plugin installed

### Installation

1. Clone this repository:

```
git clone https://github.com/your-repo/grafana-telegram-webhook.git
cd grafana-telegram-webhook
```

2. Build image

```
docker build -t grafana-telegram-webhook .
```

3. Run container

```
docker run -d --name webhook \
  --restart always \
  -p 5000:5000 \
  -e TOKEN=<BOT TOKEN> \
  -e CHAT_ID=<CHAT ID> \
  -e GRAFANA_URL=<GRAFANA URL> \
  --network monitoring_network \
  grafana-telegram-webhook
```

### Grafana Webhook Configuration

1. Go to Grafana → Alerting → Notification channels.
2. Add a new notification channel.
3. Set the Type to Webhook.
4. Enter the Webhook URL: http://your-server-ip:5000/grafana-webhook.
5. Save and test the alert.

### How It Works

- When Grafana sends an alert, the webhook extracts relevant data (alert title, message, panel URL).
- If the panel URL exists, the server generates a Grafana renderer URL to capture the latest image.
- The image and message are sent to Telegram via the bot.
- If no panel URL is provided, only the text alert is sent.
