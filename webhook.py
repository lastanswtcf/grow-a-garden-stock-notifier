import requests
import time
import hashlib

webhooks = {
    "seed_stock":     "🖇️",
    "gear_stock":     "🖇️",
    "egg_stock":      "🖇️",
    "cosmetic_stock": "🖇️",
    "eventshop_stock":"🖇️"
}

lasthashes = {}
def fetchstock():
    try:
        response = requests.get("https://api.joshlei.com/v2/growagarden/stock")
        return response.json()
    except Exception as error:
        print("[✘] couldnt get stock right now:", error)
        return None

def makedatahash(data):
    return hashlib.md5(str(data).encode()).hexdigest()

def sendwebhook(stocktype, items):
    if stocktype not in webhooks:
        return
    url = webhooks[stocktype]
    if not url.startswith("https://discord.com/api/webhooks/"):
        print(f"[✘] webhook not valid: {stocktype}")
        return
    embeds = []
    for item in items[:10]:
        embed = {
            "title": item["display_name"],
            "thumbnail": {"url": item["icon"]},
            "fields": [
                {
                    "name": "quantity",
                    "value": str(item["quantity"]),
                    "inline": True
                },
                {
                    "name": "ends",
                    "value": f"<t:{item['end_date_unix']}:R>" if item.get("end_date_unix") else "Unknown",
                    "inline": True
                }
            ],
            "color": 13621245
        }
        embeds.append(embed)
    nicefriendlyname = stocktype.replace("_", " ").title()
    message = {
        "username": nicefriendlyname,
        "embeds": embeds
    }

    try:
        result = requests.post(url, json=message)
        if result.status_code in [200, 204]:
            print(f"[✉] sent update for {stocktype}")
        else:
            print(f"[✘] couldnt send webhook ({result.status_code}) for {stocktype}")
    except Exception as error:
        print("[✘] something went wrong:", error)

def checkupdates():
    global lasthashes
    stock = fetchstock()
    if not stock:
        return

    for stocktype, items in stock.items():
        thishash = makedatahash(items)
        if lasthashes.get(stocktype) != thishash:
            print(f"[✉] something changed in {stocktype}")
            sendwebhook(stocktype, items)
            lasthashes[stocktype] = thishash
        else:
            print(f"[☹] Nothing new for {stocktype} right now")

print("[✉] starting stock checker")
print("[✉] credits to lendeerchieftheworda")
while True:
    checkupdates()
    time.sleep(60)
