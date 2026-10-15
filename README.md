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

**Moment 3**

- *What I asked for:* I asked for help making the model-unavailable failure more legible to a real user instead of silently falling back to a fake caption.
- *What came back:* It suggested letting the `ModelUnavailable` exception rise until the agent can handle it in one place.
- *What I changed:* I stopped swallowing that exception in `suggest_outfit` and `create_fit_card`, and the agent now sets `session["error"]` with a readable error message instead of a misleading fallback.

---

## Run Log — Before

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. matching query completes | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. impossible query stops early | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. selected item reaches outfit tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. fit card includes item facts | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. empty wardrobe still styles the item | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

### Real output from one try for each criterion

**Criterion 1 — matching query completes**

```text
Query: vintage graphic tee under $30
selected_item: Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
search_results: 10
Outfit suggestion: Hey! That 2003 tour bootleg tee is an absolute score...
Fit card: Scored this buttery soft 2003 tour bootleg tee on Depop for just $24...
```

**Criterion 2 — impossible query stops early**

```text
Query: designer ballgown size XXS under $5
stopped early: yes — No listings matched that search. Try a broader description, a different size, or a higher price cap.
selected_item: (none)
search_results: 0
```

**Criterion 3 — selected item reaches outfit tool**

```text
selected_item: Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
search_results: 10
The outfit suggestion used the same selected item from that run.
```

**Criterion 4 — fit card includes item facts**

```text
Fit card: Scored this perfectly faded 2003 tour bootleg tee on Depop for just $24, and the worn-in cotton is literal perfection.
```

**Criterion 5 — empty wardrobe still styles the item**

```text
Query: denim jacket under $50
Outfit suggestion: Wear denim jacket with relaxed straight-leg denim and a clean sneaker for an easy everyday look.
```

---

## Verdicts and Diagnoses

I did not have any missed criteria in the recorded before-run. I judged them from the actual five-try table and read the pass count straight against the target in `criteria.md`.

- 1. MET — 5 of 5. The matching query reached a selected item, executed the outfit and fit-card tools, and returned a fit card each time.
- 2. MET — 5 of 5. The empty-search branch stopped early every time and named what the user should change.
- 3. MET — 5 of 5. The `selected_item` persisted into the same session and was the item used by the outfit tool on every run.
- 4. MET — 5 of 5. The fit card included the item title, price, and platform in a caption-like form every time.
- 5. MET — 5 of 5. The empty wardrobe path returned a non-empty styling suggestion and never crashed.

The closest thing to a miss was criterion 4 as a design detail: the model sometimes spread the required facts across two sentences, so if I tightened this criterion later, I would require the title, price, and platform to appear in the same sentence instead of anywhere in the caption.

---

## Loop Trace

**Happy path**

```text
[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      →    querying listings through the MCP tool
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey, Y2K Baby Tee — Butterfly Print … +7 more
      →    branch: empty result or continue
[3] suggest_outfit
      in:  dict with keys: new_item, wardrobe_items
      out: Hey! That 2003 tour bootleg tee is an incredible find—those pieces always have the best vintage wash and attitude...
[4] create_fit_card
      in:  dict with keys: item, outfit_length
      out: Obsessed with this 2003 tour bootleg tee I just scored on Depop for only $24! The fade and the soft, worn-in cotton are actual perfection.
```

**Empty search**

```text
[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      →    querying listings through the MCP tool
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    branch: empty result or continue
```

**On the MCP move:** I registered `search_listings` in `mcp_server.py`, and `agent.py::run_agent` now calls it through `call_tool("search_listings", ...)` instead of the direct in-process function. The return value stayed the same list of listing dicts, which is exactly the contract the loop expects. The trace makes that visible in the step name: `search_listings (via MCP)`.

### Failure mode check

- Empty search: `python app.py ask 'designer ballgown size XXS under $5'` returned `No listings matched that search...` and stopped before the second tool.
- Empty wardrobe: `python app.py ask 'denim jacket under $50' --empty-wardrobe` returned a non-empty outfit suggestion instead of crashing.
- Model unavailable: after forcing an invalid GEMINI_API_KEY, the app returned `The model couldn't be reached. Check your internet connection or GEMINI_API_KEY and try again.`

---

## The Improvement

**What I changed:** I stopped swallowing `ModelUnavailable` inside `suggest_outfit` and `create_fit_card`. The tools now let that error escape so the agent can catch it once and turn it into a clear user-facing failure message instead of a fake fallback caption.

**Which failure it was meant to fix:** the model-unavailable branch. Before this change, a failed call to the model was hidden by a generic fallback string, which made the agent look like it had succeeded when it really had no model access.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. matching query completes | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. impossible query stops early | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. selected item reaches outfit tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. fit card includes item facts | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. empty wardrobe still styles the item | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Did it help, and how do I know:** It did not improve the five scored criteria numerically; the score stayed at 5/5 on every criterion. It did improve the actual failure handling: when the model is unavailable, the app now says what went wrong and what the user should do, instead of silently inventing a fallback caption. The explicit message was:

```text
The model couldn't be reached. Check your internet connection or GEMINI_API_KEY and try again.
```

---

## What's Still Broken

No criterion is still missed in the recorded test run. The remaining weakness is not a functional failure in the loop; it is the model's creative drift in criterion 4. The tool is fine, but the message can still vary across tries enough that a stricter pass condition would require the title, price, and platform to appear in the same sentence. I stopped there because the functional loop already satisfies the original target and the improvement was deliberately aimed at user-facing failure clarity rather than a stronger prompt rewrite.

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
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
