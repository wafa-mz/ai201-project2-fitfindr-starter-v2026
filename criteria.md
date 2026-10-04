# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
I chose 4 of 5 because the search is a plain keyword match, so a few valid
queries will still miss if the wording is a little different. The tool is
working if it gets the happy path most of the time, even though thrift listings
and natural-language phrasing are fuzzy.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
This branch is the core behavioral check for the loop. It is the path where the
agent has to decide not to continue, so I made the target strict: the finding
must be empty-search-aware every time, not just most of the time.

---

## 3. The item chosen by search is the same one used by the outfit tool

For 5 queries that match at least one listing, the `session["selected_item"]["id"]`
value is identical to the item that reaches `suggest_outfit` in that same run — 5 of 5 tries.

**Why this target:**
This checks state directly instead of inferring it from the final output. A tool
can look right while the session is wrong, so I picked a direct data-flow check
that is easy to observe and hard to misread.

---

## 4. The fit card includes the required facts and stays in caption form

For 5 runs with the same item, the fit card is 2 to 4 sentences long, mentions the item title, price, and platform at least once each, and is not blank or generic — 5 of 5 tries.

**Why this target:**
The model can vary the wording from run to run, so the target is about the facts
and format rather than word-for-word sameness. I did not require the exact same
opening sentence because that would be a brittle test of a creative model.

---

## 5. The empty-wardrobe path does not crash

When the user has no saved wardrobe items, `suggest_outfit` still returns a non-empty
string and the run finishes without an exception — 5 of 5 tries.

**Why this target:**
This catches a common real-world failure mode: a user starts empty, and the tool
still has to act usefully. I chose 5 of 5 because the empty wardrobe path is a
specific branch with a single expected result, so it is easy to verify reliably.

---
