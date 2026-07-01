import os
import html
import requests
import fear_greed
from datetime import datetime
from zoneinfo import ZoneInfo


VIENNA_TZ = ZoneInfo("Europe/Vienna")


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


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


def sentiment_icon_from_score(value) -> str:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return "⚪"

    if score <= 24:
        return "🔴"   # Extreme Fear
    elif score <= 44:
        return "🟠"   # Fear
    elif score <= 55:
        return "🟡"   # Neutral
    elif score <= 75:
        return "🟢"   # Greed
    else:
        return "🟣"   # Extreme Greed

def main() -> None:
    data = fear_greed.get()

    score = round(float(data["score"]), 2)
    rating = str(data["rating"]).title()

    timestamp = data.get("timestamp")
    if timestamp:
        updated = datetime.fromisoformat(timestamp).astimezone(VIENNA_TZ)
        updated_text = updated.strftime("%Y-%m-%d %H:%M %Z")
    else:
        updated_text = "Unknown"

    history = data.get("history", {})
    indicators = data.get("indicators", {})

    icon = sentiment_icon_from_score(score)

    message = (
        f"{icon} <b>Fear & Greed Index</b>\n\n"
        f"Index: <b>{html.escape(str(score))}/100 {html.escape(rating)}</b>\n"
        f"Updated: {html.escape(updated_text)}\n\n"
        "<b>History</b>\n"
    )

    history_labels = {
        "1w": "1W",
        "1m": "1M",
        "3m": "3M",
        "6m": "6M",
        "1y": "1Y",
    }

    for key, label in history_labels.items():
        value = history.get(key, "N/A")
        value_icon = sentiment_icon_from_score(value)

        message += (
            f"{value_icon} {label}: "
            f"<b>{html.escape(str(value))}</b>\n"
        )

    message += "\n<b>Main indicators</b>\n"

    for name, item in indicators.items():
        indicator_score = item.get("score", "N/A")
        indicator_rating = str(item.get("rating", "N/A")).title()

        score_icon = sentiment_icon_from_score(indicator_score)

        clean_name = name.replace("_", " ").title()

        message += (
            f"{score_icon} {html.escape(clean_name)}: "
            f"{html.escape(str(indicator_score))} ({html.escape(indicator_rating)})\n\n"
        )

    message += "Source: CNN Fear & Greed Index"

    send_telegram_message(message)
    print("Telegram message sent successfully.")


if __name__ == "__main__":
    main()