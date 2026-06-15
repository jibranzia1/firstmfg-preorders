#!/usr/bin/env node
/*
 * fetch.js — Pulls Shopify orders tagged with ORDER_TAG (default: NM-preorder),
 * expands line items, resolves current inventory per variant, and writes
 * data/preorders.json for the dashboard.
 *
 * Required env vars:
 *   SHOPIFY_STORE  e.g. firstmfg.myshopify.com
 *   SHOPIFY_TOKEN  Admin API access token (shpat_...)
 *
 * Optional env vars:
 *   ORDER_TAG      default "NM-preorder"
 *   API_VERSION    default "2025-07"  (bump if Shopify deprecates it)
 *   DAYS           default "365"      (only fetch orders created within N days)
 *   STORE_TZ       default "America/New_York" (for the per-order calendar date)
 */

const STORE = process.env.SHOPIFY_STORE;
const TOKEN = process.env.SHOPIFY_TOKEN;
const ORDER_TAG = process.env.ORDER_TAG || "NM-preorder";
const API_VERSION = process.env.API_VERSION || "2025-07";
const DAYS = parseInt(process.env.DAYS || "365", 10);
const STORE_TZ = process.env.STORE_TZ || "America/New_York";

if (!STORE || !TOKEN) {
  console.error("Missing SHOPIFY_STORE or SHOPIFY_TOKEN env var.");
  process.exit(1);
}

const ENDPOINT = `https://${STORE}/admin/api/${API_VERSION}/graphql.json`;

const QUERY = `
query($q: String!, $after: String) {
  orders(first: 50, query: $q, sortKey: CREATED_AT, reverse: true, after: $after) {
    pageInfo { hasNextPage endCursor }
    nodes {
      name
      createdAt
      displayFinancialStatus
      tags
      subtotalPriceSet { shopMoney { amount currencyCode } }
      lineItems(first: 100) {
        nodes {
          name
          quantity
          sku
          unfulfilledQuantity
          originalUnitPriceSet { shopMoney { amount } }
          variant { id inventoryQuantity }
        }
      }
    }
  }
}`;

async function gql(query, variables) {
  const res = await fetch(ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Shopify-Access-Token": TOKEN,
    },
    body: JSON.stringify({ query, variables }),
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`HTTP ${res.status} ${res.statusText}: ${txt}`);
  }
  const json = await res.json();
  if (json.errors) throw new Error("GraphQL errors: " + JSON.stringify(json.errors));
  // Throttle politely on Shopify cost-based rate limit.
  const cost = json.extensions && json.extensions.cost;
  if (cost && cost.throttleStatus) {
    const { currentlyAvailable, restoreRate } = cost.throttleStatus;
    const need = cost.requestedQueryCost || 0;
    if (currentlyAvailable < need) {
      const waitMs = Math.ceil(((need - currentlyAvailable) / restoreRate) * 1000) + 200;
      await new Promise((r) => setTimeout(r, waitMs));
    }
  }
  return json.data;
}

function fulfillmentLabel(quantity, unfulfilled) {
  if (unfulfilled === 0) return "fulfilled";
  if (unfulfilled >= quantity) return "unfulfilled";
  return "partial";
}

function localDate(iso, tz) {
  // Returns YYYY-MM-DD for the given ISO timestamp in the store timezone.
  const d = new Date(iso);
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: tz,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(d);
  const get = (t) => parts.find((p) => p.type === t).value;
  return `${get("year")}-${get("month")}-${get("day")}`;
}

async function main() {
  const since = new Date(Date.now() - DAYS * 24 * 60 * 60 * 1000)
    .toISOString()
    .slice(0, 10);
  const q = `tag:${ORDER_TAG} AND created_at:>=${since}`;

  const rows = [];
  const orderKeys = new Set();
  let after = null;
  let page = 0;

  do {
    const data = await gql(QUERY, { q, after });
    const conn = data.orders;
    for (const o of conn.nodes) {
      orderKeys.add(o.name);
      const subtotal = o.subtotalPriceSet?.shopMoney?.amount ?? "";
      const currency = o.subtotalPriceSet?.shopMoney?.currencyCode ?? "USD";
      const orderDate = localDate(o.createdAt, STORE_TZ);
      const items = o.lineItems?.nodes ?? [];
      if (items.length === 0) {
        rows.push({
          name: o.name,
          subtotal,
          currency,
          createdAt: o.createdAt,
          orderDate,
          financialStatus: o.displayFinancialStatus || "",
          quantity: "",
          lineitemName: "",
          lineitemPrice: "",
          sku: "",
          fulfillmentStatus: "",
          inventory: "",
        });
        continue;
      }
      for (const li of items) {
        rows.push({
          name: o.name,
          subtotal,
          currency,
          createdAt: o.createdAt,
          orderDate,
          financialStatus: o.displayFinancialStatus || "",
          quantity: li.quantity,
          lineitemName: li.name,
          lineitemPrice: li.originalUnitPriceSet?.shopMoney?.amount ?? "",
          sku: li.sku || "",
          fulfillmentStatus: fulfillmentLabel(li.quantity, li.unfulfilledQuantity ?? li.quantity),
          inventory: li.variant?.inventoryQuantity ?? "",
        });
      }
    }
    after = conn.pageInfo.hasNextPage ? conn.pageInfo.endCursor : null;
    page++;
    if (page > 200) break; // hard safety cap (~10k orders)
  } while (after);

  const out = {
    generatedAt: new Date().toISOString(),
    store: STORE,
    tag: ORDER_TAG,
    timezone: STORE_TZ,
    windowDays: DAYS,
    orderCount: orderKeys.size,
    rowCount: rows.length,
    rows,
  };

  const fs = await import("node:fs");
  const path = await import("node:path");
  const dir = path.join(process.cwd(), "data");
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, "preorders.json"), JSON.stringify(out, null, 2));
  console.log(`Wrote data/preorders.json — ${out.orderCount} orders, ${out.rowCount} line items.`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
