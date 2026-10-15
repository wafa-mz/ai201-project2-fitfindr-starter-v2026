"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config  # noqa: F401 — you'll use this in search_listings
from generate import ModelUnavailable, generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def _normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    text = str(value).lower()
    text = text.replace("$", " ")
    text = re.sub(r"[^a-z0-9/\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _size_matches(item_size: str | None, requested_size: str | None) -> bool:
    if requested_size is None or requested_size == "":
        return True
    if item_size is None:
        return False

    item_norm = _normalize_text(item_size)
    request_norm = _normalize_text(requested_size)

    if not item_norm or not request_norm:
        return True

    item_tokens = [token for token in re.split(r"[\s/]+", item_norm) if token]
    req_tokens = [token for token in re.split(r"[\s/]+", request_norm) if token]

    if any(token in item_tokens for token in req_tokens):
        return True
    if any(token in item_norm for token in req_tokens):
        return True

    # Numeric shoe sizes should still match their exact value.
    if req_tokens and req_tokens[0].isdigit():
        return req_tokens[0] in item_tokens or req_tokens[0] in item_norm

    return False


def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.
    """
    items = load_listings()
    query = _normalize_text(description)
    query_tokens = [token for token in query.split() if len(token) > 2]

    matches = []
    for item in items:
        if max_price is not None and item.get("price") is not None and float(item["price"]) > float(max_price):
            continue
        if size is not None and not _size_matches(item.get("size"), size):
            continue

        text_blob = " ".join(
            [
                item.get("title", ""),
                item.get("description", ""),
                " ".join(item.get("style_tags", [])),
                " ".join(item.get("colors", [])),
                str(item.get("brand") or ""),
            ]
        )
        normalized_blob = _normalize_text(text_blob)

        score = 0
        for token in query_tokens:
            if token in normalized_blob:
                score += 2
            if token in _normalize_text(item.get("title", "")):
                score += 2

        if "graphic tee" in query and "graphic tee" in _normalize_text(item.get("title", "") + " " + " ".join(item.get("style_tags", []))):
            score += 3
        if not query_tokens or score == 0:
            continue

        matches.append({**item, "_score": score})

    matches.sort(key=lambda item: item["_score"], reverse=True)
    result = [
        {key: value for key, value in item.items() if key != "_score"}
        for item in matches[: config.SEARCH_RESULT_LIMIT]
    ]
    return result


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.
    """
    if not isinstance(new_item, dict):
        return "Pick a real listing first so I can suggest a styling plan."

    item_name = new_item.get("title", "this thrifted piece")
    item_category = new_item.get("category", "")
    item_color = ", ".join(new_item.get("colors", [])) or "a versatile neutral"

    wardrobe_items = wardrobe.get("items", []) if isinstance(wardrobe, dict) else []
    if not wardrobe_items:
        prompt = (
            f"Give me 2 outfit ideas for {item_name}, a {item_category} in {item_color}. "
            "Keep it practical for everyday wear and mention how to style the piece."
        )
        system = "You are a thoughtful wardrobe stylist. Give concise styling advice in plain English."
        try:
            response = generate(prompt, system=system)
        except ModelUnavailable:
            raise
        except Exception:
            response = (
                f"Wear {item_name} with relaxed straight-leg denim and a clean sneaker for an easy, everyday look. "
                f"For a sharper version, pair it with a tailored trouser and a light layer in a similar tone."
            )
        return response.strip() or (
            f"Wear {item_name} with relaxed denim and a clean sneaker for an easy everyday look. "
            f"A tailored trouser and light layer in the same color family will keep it polished."
        )

    wardrobe_summary = []
    for item in wardrobe_items:
        name = item.get("name", "piece")
        category = item.get("category", "")
        colors = ", ".join(item.get("colors", []))
        wardrobe_summary.append(f"- {name} ({category}, {colors})")

    prompt = (
        f"I have a thrifted item: {item_name}. "
        f"Category: {item_category}. Colors: {item_color}. "
        "Here is my wardrobe:\n"
        + "\n".join(wardrobe_summary)
        + "\nSuggest 2 outfits that use pieces I already own. Name the pieces from my wardrobe and explain why they work together."
    )
    system = "You are a fashion stylist. Use only the wardrobe items the user listed. Keep it practical and conversational."
    try:
        response = generate(prompt, system=system)
    except ModelUnavailable:
        raise
    except Exception:
        response = (
            f"Use the neutral layers in your closet with {item_name} for a balanced outfit, then add one standout accessory for texture. "
            f"Keep the color story cohesive and aim for one relaxed, one polished option."
        )
    return response.strip() or "Style it with the neutral basics you already own and keep the overall palette cohesive."


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.
    """
    if not isinstance(new_item, dict):
        return "Found a cool piece and I can already picture it in the rotation."

    item_title = new_item.get("title", "this thrifted piece")
    item_price = new_item.get("price", "")
    item_platform = new_item.get("platform", "")
    item_size = new_item.get("size", "")
    item_description = new_item.get("description", "")

    if not outfit or not str(outfit).strip():
        outfit = "It feels easy to style with the basics already in the closet."

    prompt = (
        f"Write a social-media caption for this thrifted find: {item_title}. "
        f"Price: ${item_price}. Platform: {item_platform}. Size: {item_size}. "
        f"Description: {item_description}. "
        f"Outfit idea: {outfit}. "
        "Keep it to 2-4 sentences, sound like a real person posting a thrift haul, and include the item, price, and platform naturally."
    )
    system = "You are a fashion content creator writing a short, casual caption. Keep it vivid and concise."
    try:
        response = generate(prompt, system=system)
    except ModelUnavailable:
        raise
    except Exception:
        response = (
            f"Found this {item_title} for ${item_price} on {item_platform}, and it already feels like a good fit for my closet. "
            f"The vibe is {outfit.lower()}."
        )
    return response.strip() or (
        f"Found this {item_title} for ${item_price} on {item_platform} and it already feels like a great addition to my closet."
    )
