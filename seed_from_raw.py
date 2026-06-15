#!/usr/bin/env python3
"""Builds a seed data/preorders.json from a real Shopify sample.
Mirrors the exact output shape of fetch.js so the dashboard renders before
the hourly GitHub Action runs for the first time."""
import json, datetime
from zoneinfo import ZoneInfo

STORE = "firstmfg.myshopify.com"
TAG = "NM-preorder"
TZ = "America/New_York"

# Real subset pulled live from the store (50-order sample, trimmed for seed).
RAW = [
 {"name":"209425","createdAt":"2026-06-15T19:03:37Z","fin":"PAID","sub":"330.5","cur":"USD","items":[
   {"n":"Bifold Wallet - Vegetable Tanned Leather - FOREST GREEN","q":1,"sku":"FIW9003-FGRN-STRD","uf":1,"p":"13.0","inv":10},
   {"n":"WOMENS MOTO MESH - mczr_price_230","q":1,"sku":None,"uf":1,"p":"310.0","inv":-39},
   {"n":"CUSTOM MENS MOTO MESH - mczr_price_250","q":1,"sku":"","uf":1,"p":"324.99","inv":-498}]},
 {"name":"209418","createdAt":"2026-06-15T17:19:11Z","fin":"PAID","sub":"86.45","cur":"USD","items":[
   {"n":"Lowside Men's Motorcycle Denim Vest (Blue) - Blue Denim / M","q":1,"sku":"FIM659DM-BLU-M","uf":1,"p":"86.45","inv":0}]},
 {"name":"209412","createdAt":"2026-06-15T16:32:21Z","fin":"PAID","sub":"355.77","cur":"USD","items":[
   {"n":"Jessica Perforated Women's Motorcycle Leather Vest - Black / S","q":1,"sku":"FIL027PERF-BBLK-S","uf":1,"p":"164.03","inv":8},
   {"n":"Lowside Men's Perforated Motorcycle Leather Vest - Black / 4XL","q":1,"sku":"FIM659PERF-BLK-4XL","uf":1,"p":"191.74","inv":0}]},
 {"name":"209353","createdAt":"2026-06-15T03:14:29Z","fin":"PAID","sub":"306.04","cur":"USD","items":[
   {"n":"Mystery box - Extra Value Guaranteed - $149.99 / Men's Vest / XL","q":1,"sku":None,"uf":1,"p":"149.99","inv":-11},
   {"n":"Upside Perforated Men's Club Style Leather Vest - Grey / XL","q":1,"sku":"FIM653PERF-BKG-XL","uf":1,"p":"157.62","inv":14}]},
 {"name":"209296","createdAt":"2026-06-15T00:25:48Z","fin":"PAID","sub":"125.14","cur":"USD","items":[
   {"n":"Rancher - Men's Motorcycle Western Style Leather Vest - Black / M","q":1,"sku":"FIM652CDM-BLK-M","uf":0,"p":"127.69","inv":0}]},
 {"name":"209285","createdAt":"2026-06-14T23:57:07Z","fin":"PAID","sub":"258.35","cur":"USD","items":[
   {"n":"Maverick Men's Motorcycle Leather Jacket - Tall / Black / 4XL","q":1,"sku":"FIM262TALL-BLK-4XLT","uf":0,"p":"258.35","inv":0}]},
 {"name":"209270","createdAt":"2026-06-14T22:58:58Z","fin":"PAID","sub":"137.66","cur":"USD","items":[
   {"n":"Sharp Shooter Men's Motorcycle Leather Vest - Black Olive / S","q":1,"sku":"FIM689CDT-BLKOL-S","uf":0,"p":"137.66","inv":0}]},
 {"name":"209230","createdAt":"2026-06-14T21:10:08Z","fin":"PAID","sub":"263.38","cur":"USD","items":[
   {"n":"Lowside Men's Motorcycle Denim Vest (Blue) - Blue Denim / 4XL","q":1,"sku":"FIM659DM-BLU-4XL","uf":0,"p":"86.8","inv":2},
   {"n":"Vigilante Motorcycle Leather Shirt - 3XL","q":1,"sku":"FIM404ES","uf":1,"p":"176.58","inv":0}]},
 {"name":"209197","createdAt":"2026-06-14T18:19:53Z","fin":"PAID","sub":"289.19","cur":"USD","items":[
   {"n":"York - Men's Motorcycle Riding Jeans - 30 W / 32 L","q":1,"sku":"FIM812KDM-BLU-30","uf":1,"p":"148.5","inv":0},
   {"n":"Roper Men's Deer Skin Gloves - Black / M","q":1,"sku":"FI211DEER-BLK-M","uf":1,"p":"18.9","inv":10},
   {"n":"Dagger Motorcycle Twill Shirt - Black / L","q":1,"sku":"CUS423TWL-BLK-L","uf":1,"p":"127.69","inv":5}]},
 {"name":"209139","createdAt":"2026-06-14T03:35:28Z","fin":"PAID","sub":"472.29","cur":"USD","items":[
   {"n":"LARGE TRUCKER - Vegetable Tanned Leather Wallet - ONYX BLACK / Chrome","q":1,"sku":"FIW9001-ONBK-SS-LRG","uf":0,"p":"23.85","inv":64},
   {"n":"12 Gauge Men's Motorcycle Leather Vest - Black / M","q":1,"sku":"CUS6031LTH-BLK-M","uf":0,"p":"157.79","inv":13},
   {"n":"Lowside Men's Motorcycle Leather Vest - Black / XL","q":1,"sku":"FIM659CPM-BLK-XL","uf":0,"p":"157.25","inv":31},
   {"n":"Lowside Men's Motorcycle Leather Vest - Black / M","q":1,"sku":"FIM659CPM-BLK-M","uf":0,"p":"157.25","inv":7}]},
 {"name":"209123","createdAt":"2026-06-14T01:58:25Z","fin":"PAID","sub":"449.98","cur":"USD","items":[
   {"n":"Marshal - Men's Club Style Leather Motorcycle Vest - XXL","q":1,"sku":"198651","uf":1,"p":"224.99","inv":-1},
   {"n":"Road Cartel - Men's Croc Texture Leather/Denim Motorcycle Vest - XXL","q":1,"sku":"195764","uf":1,"p":"224.99","inv":-1},
   {"n":"SMALL TRUCKER - Vegetable Tanned Leather Wallet - FOREST GREEN / Chrome","q":1,"sku":"FIW9002-FGRN-SML","uf":1,"p":"18.9","inv":10}]},
 {"name":"209100","createdAt":"2026-06-13T22:50:09Z","fin":"PAID","sub":"163.57","cur":"USD","items":[
   {"n":"Lowside Men's Perforated Motorcycle Leather Vest - Black / XL","q":1,"sku":"FIM659PERF-BLK-XL","uf":0,"p":"163.57","inv":0}]},
 {"name":"209097","createdAt":"2026-06-13T22:36:42Z","fin":"PAID","sub":"100.74","cur":"USD","items":[
   {"n":"Desperado Men's Motorcycle Twill Jacket - Black / L","q":1,"sku":"FIM254TWILL-BLK-L","uf":1,"p":"101.75","inv":1}]},
 {"name":"209074","createdAt":"2026-06-13T18:46:39Z","fin":"PAID","sub":"130.98","cur":"USD","items":[
   {"n":"Scout - Women's Club Style Motorcycle Leather Vest (Limited Edition) - XXL","q":1,"sku":"CUS516LTH03-WHCMO-XXL","uf":1,"p":"132.3","inv":0}]},
 {"name":"209072","createdAt":"2026-06-13T18:22:33Z","fin":"PAID","sub":"137.25","cur":"USD","items":[
   {"n":"Infantry Motorcycle Leather Canvas Vest - Camo / XL","q":1,"sku":"FIM666-CAMO-XL","uf":1,"p":"137.25","inv":0}]},
]

def local_date(iso):
    dt = datetime.datetime.fromisoformat(iso.replace("Z","+00:00")).astimezone(ZoneInfo(TZ))
    return dt.strftime("%Y-%m-%d")

def ful(q, uf):
    if uf == 0: return "fulfilled"
    if uf >= q: return "unfulfilled"
    return "partial"

rows, orders = [], set()
for o in RAW:
    orders.add(o["name"])
    for li in o["items"]:
        rows.append({
            "name": o["name"], "subtotal": o["sub"], "currency": o["cur"],
            "createdAt": o["createdAt"], "orderDate": local_date(o["createdAt"]),
            "financialStatus": o["fin"], "quantity": li["q"],
            "lineitemName": li["n"], "lineitemPrice": li["p"],
            "sku": li["sku"] or "", "fulfillmentStatus": ful(li["q"], li["uf"]),
            "inventory": li["inv"],
        })

out = {
    "generatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "store": STORE, "tag": TAG, "timezone": TZ, "windowDays": 365,
    "orderCount": len(orders), "rowCount": len(rows), "rows": rows,
}
import os
os.makedirs("data", exist_ok=True)
with open("data/preorders.json","w") as f:
    json.dump(out, f, indent=2)
print(f"Seeded data/preorders.json — {len(orders)} orders, {len(rows)} line items")
print("Dates present:", sorted({r['orderDate'] for r in rows}))
