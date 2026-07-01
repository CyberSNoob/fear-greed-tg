import os
import html
import requests
from datetime import datetime
from zoneinfo import ZoneInfo


FNG_URL = "https://api.alternative.me/fng/?limit=1"
VIENNA_TZ = ZoneInfo("Europe/Vienna")


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def get_fear_greed_index() -> dict:
    response = requests.get(FNG_URL, timeout=20)
    response.raise_for_status()

    data = response.json()["data"][0]
    timestamp = int(data["timestamp"])
    updated_vienna = datetime.fromtimestamp(timestamp, VIENNA_TZ)

    return {
        "value": data["value"],
        "classification": data["value_classification"],
        "updated": updated_vienna.strftime("%Y-%m-%d %H:%M %Z"),
    }


def send_telegram_message(text: str) -> None:
    token = get_env("TELEGRAM_BOT_TOKEN")
    chat_id = get_env("TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=20,
    )

    response.raise_for_status()


def main() -> None:
    fng = get_fear_greed_index()

    message = (
        "<b>Crypto Fear & Greed Index</b>\n\n"
        f"Value: <b>{html.escape(str(fng['value']))}/100</b>\n"
        f"Classification: <b>{html.escape(str(fng['classification']))}</b>\n"
        f"Updated: {html.escape(str(fng['updated']))}\n\n"
        "0 = Extreme Fear\n"
        "100 = Extreme Greed\n\n"
        "Source: Alternative.me"
    )

    send_telegram_message(message)
    print("Telegram message sent successfully.")


if __name__ == "__main__":
    main()