# FitFindr

## What This Does

FitFindr takes a shopping prompt like "vintage graphic tee under $30, size M" and turns it into a lightweight recommendation flow. It searches the local listing dataset, picks the highest-match item, suggests an outfit using the user's wardrobe, and writes a short fit card caption for the item. If the search returns nothing, it stops early and tells the user what to adjust instead of continuing with a broken chain.

---

## Tool Inventory

### `search_listings`

- **What it does:** Filters the thrift listings by keyword, size, and maximum price and returns the best matches first.
- **Inputs:** `description` (str), `size` (str | None), `max_price` (float | None)
- **Returns:** A list of listing dicts, each with `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`, sorted by keyword match score.
- **When it has nothing:** Returns an empty list `[]`.

### `suggest_outfit`

- **What it does:** Uses the selected item and the current wardrobe to return one or two practical outfit combinations.
- **Inputs:** `new_item` (dict), `wardrobe` (dict)
- **Returns:** A non-empty string describing the outfit idea, including wardrobe pieces when they exist.
- **When it has nothing:** Returns a fallback styling sentence instead of an empty string.

### `create_fit_card`

- **What it does:** Turns the outfit suggestion and the thrifted item into a short social caption a person could actually post.
- **Inputs:** `outfit` (str), `new_item` (dict)
- **Returns:** A 2-4 sentence caption that includes the item, price, and platform naturally.
- **When it has nothing:** Returns a fallback caption rather than crashing on empty or blank input.

---

## Planning Loop

**Branch rule:** If `search_listings` returns an empty list, put a message in the session and stop. Otherwise, take the first result, place it in `session["selected_item"]`, then call `suggest_outfit` and `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex is used to extract `size` and `max_price` from the text, then the query is cleaned by removing those matched parts so the description is left as plain keywords.

**What moves through the session:** `query` → `parsed` → `search_results` → `selected_item` → `outfit_suggestion` → `fit_card`.

---

## Sample Run

**One full query**

```text
$ .venv/bin/python app.py ask 'vintage graphic tee under $30, size M'
  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Use the neutral layers in your closet with Y2K Baby Tee — Butterfly
Print for a balanced outfit, then add one standout accessory for texture. Keep the color story cohesive and aim for one relaxed, one polished option.

  Fit card: Found this Y2K Baby Tee — Butterfly Print for $18.0 on depop, and it already feels like a good fit for my closet. The vibe is use the neutral layers in your closet with y2k baby tee — butterfly print for a balanced outfit, then add one standout accessory for texture. keep the color story cohesive and aim for one relaxed, one polished option..

2 model calls this session
```

**The three tools, tested one at a time**

```text
$ .venv/bin/python -c "from tools import search_listings; print(search_listings('vintage graphic tee', size='M', max_price=30)[:3])"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_024', 'title': 'Vintage Polo Shirt — Forest Green', 'description': 'Classic polo in forest green. Short sleeve, ribbed collar. Slightly boxy. The kind of piece that goes with everything.', 'category': 'tops', 'style_tags': ['vintage', 'preppy', 'classic', 'earth tones'], 'size': 'M', 'condition': 'good', 'price': 18.0, 'colors': ['green', 'forest green'], 'brand': 'Ralph Lauren', 'platform': 'thredUp'}]
```

```text
$ .venv/bin/python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[1], get_example_wardrobe())[:180])"
Use the neutral layers in your closet with Y2K Baby Tee — Butterfly Print for a balanced outfit, then add one standout accessory for texture. Keep the color story cohesive and aim for one relaxed, one polished option.
```

```text
$ .venv/bin/python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('A relaxed pair of denim and sneakers', load_listings()[1])[:180])"
Found this Y2K Baby Tee — Butterfly Print for $18.0 on depop, and it already feels like a good fit for my closet. The vibe is a relaxed pair of denim and sneakers.
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* I asked for help refining the `search_listings` contract and deciding how size matching should work for values like `S/M` and `M`.
- *What came back:* It suggested a normalization strategy and reminded me to avoid naive substring matching that could confuse size filters.
- *What I changed:* I implemented a normalized size matcher so `M` matches `S/M`, and I made the search return an empty list instead of `None` when no items fit.

**Moment 2**

- *What I asked for:* I asked for help deciding what a useful empty-search message should say to a user who has no idea what to change.
- *What came back:* It returned a version emphasizing concrete next steps like trying a broader description, a different size, or a higher price cap.
- *What I changed:* I used that guidance in the loop branch, and I made the agent stop immediately with that message before it attempted `suggest_outfit`.

---
**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
