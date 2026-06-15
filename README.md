# Preorders Dashboard (NM-preorder)

A self-refreshing dashboard for Shopify orders tagged **`NM-preorder`** on **firstmfg.com**.
Same pattern as the First MFG influencer leaderboard: a GitHub Action pulls the data
on a schedule, commits it as JSON, and GitHub Pages serves a static dashboard that reads it.

**Columns (exactly your sheet):** Name · Subtotal · Created at · Lineitem quantity ·
Lineitem name · Lineitem price · Lineitem sku · Lineitem fulfillment status · Inventory.

**Features:** date selector (filter by order-created day, in store time), search,
fulfillment filter, summary cards, sortable table, CSV + Excel export of the current view,
manual **Refresh** button, hourly auto-pull, and a 5-min background re-check for any open tab.

---

## How it works

```
Shopify Admin API  ──hourly──►  fetch.js (GitHub Action)  ──commits──►  data/preorders.json
                                                                              │
                                                            GitHub Pages serves index.html
                                                                              │
                                                      Dashboard reads JSON, you filter/export
```

GitHub Pages is static, so "refresh on Shopify change" works at the **hourly cadence** plus
the manual Refresh button. For true near-real-time, see *Optional: near-real-time* below.

---

## One-time setup

### 1. Create the Shopify Admin API token
1. Shopify admin → **Settings → Apps and sales channels → Develop apps**.
2. **Allow custom app development** (if prompted) → **Create an app** → name it `Preorder Dashboard`.
3. **Configuration → Admin API integration → Configure** → enable scopes:
   - `read_orders` (required)
   - `read_products` (required — for the Inventory column)
   - `read_all_orders` (only if you need preorders older than 60 days)
4. **Save** → **API credentials → Install app** → copy the **Admin API access token** (`shpat_…`). Shown once.

### 2. Create the GitHub repo
1. New repo, e.g. `firstmfg-preorders`. Upload everything in this folder (keep the structure):
   ```
   index.html
   fetch.js
   data/preorders.json
   .github/workflows/fetch.yml
   ```
2. **Settings → Secrets and variables → Actions → Secrets → New repository secret:**
   - `SHOPIFY_STORE` = `firstmfg.myshopify.com`
   - `SHOPIFY_TOKEN` = your `shpat_…` token
3. *(Optional)* same screen → **Variables** tab, to override defaults:
   `ORDER_TAG` (default `NM-preorder`), `API_VERSION` (default `2025-07`),
   `DAYS` (default `365`), `STORE_TZ` (default `America/New_York`).

### 3. Turn on Pages
**Settings → Pages → Source: Deploy from a branch → `main` / root → Save.**
Your dashboard URL appears there (e.g. `https://<user>.github.io/firstmfg-preorders/`).

### 4. Run the fetch once
**Actions → Fetch preorders → Run workflow.** It writes `data/preorders.json` and commits it.
After that it runs automatically every hour. Open the Pages URL — done.

---

## Local run (optional)

```bash
# generate data once (needs the token)
SHOPIFY_STORE=firstmfg.myshopify.com SHOPIFY_TOKEN=shpat_xxx node fetch.js

# serve the dashboard
python3 -m http.server 8080
# open http://localhost:8080
```

---

## Notes & knobs

- **API version:** Shopify retires versions yearly. If the Action errors on the version,
  set the `API_VERSION` repo variable to a current one (e.g. `2026-01`).
- **Window:** `DAYS` controls how far back orders are pulled (default 365). Raise it if you
  keep very old open preorders.
- **Fulfillment label** is derived per line item: `fulfilled` (nothing unfulfilled),
  `unfulfilled` (all unfulfilled), `partial` (some shipped).
- **Inventory** is the variant's current total available quantity (can be negative on oversold preorder SKUs).
- **`seed_from_raw.py`** is a one-time helper that generated the starter `data/preorders.json`
  from a live sample so the dashboard renders before the first Action run. You can delete it.

## Optional: near-real-time refresh
Add a Shopify webhook (Order create/update) pointing at a small relay that calls the GitHub
`repository_dispatch` API with event type `shopify-order` — the workflow already listens for it.
That triggers a rebuild within ~1 min of any preorder change. Ask if you want this wired up.
