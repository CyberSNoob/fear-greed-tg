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


def sentiment_icon(score: float) -> str:
    if score <= 24:
        return "🔴"
    elif score <= 44:
        return "🟠"
    elif score <= 55:
        return "🟡"
    elif score <= 75:
        return "🟢"
    else:
        return "🟣"

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

    icon = sentiment_icon(score)

    message = (
        f"{icon} <b>Fear & Greed Index</b>\n\n"
        f"Index: <b>{html.escape(str(score))}/100 {html.escape(rating)}</b>\n"
        f"Updated: {html.escape(updated_text)}\n\n"
        "<b>History</b>\n"
        f"1W: {html.escape(str(history.get('1w', 'N/A')))}\n"
        f"1M: {html.escape(str(history.get('1m', 'N/A')))}\n"
        f"3M: {html.escape(str(history.get('3m', 'N/A')))}\n"
        f"6M: {html.escape(str(history.get('6m', 'N/A')))}\n"
        f"1Y: {html.escape(str(history.get('1y', 'N/A')))}\n\n"
        "<b>Main indicators</b>\n"
    )

    for name, item in indicators.items():
        indicator_score = item.get("score", "N/A")
        indicator_rating = str(item.get("rating", "N/A")).title()

        clean_name = name.replace("_", " ").title()

        message += (
            f"- {html.escape(clean_name)}: "
            f"{html.escape(str(indicator_score))} "
            f"({html.escape(indicator_rating)})\n"
        )

    message += (
        "Source: CNN Fear & Greed Index"
    )

    send_telegram_message(message)
    print("Telegram message sent successfully.")


if __name__ == "__main__":
    main()