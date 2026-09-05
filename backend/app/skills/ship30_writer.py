from app.agent.prompts import SHIP30_SYSTEM


def build_ship30_prompt(context: list[dict], user_query: str) -> str:
    formatted = "\n\n".join(
        f"--- Episode: {item['episode']} | Guest: {item['guest']} | "
        f"Topic/Timestamp: {item.get('timestamp') or 'not available'} ---\n{item['text']}"
        for item in context
    )
    return SHIP30_SYSTEM.format(context=formatted) + f"\n\nUser request:\n{user_query}"
