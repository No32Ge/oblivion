import requests

proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}

# 查询出口 IP 和地区
response = requests.get("https://ipinfo.io/json", proxies=proxies)
data = response.json()

print("出口 IP:", data["ip"])
print("地区:", data["country"], data.get("region", ""), data.get("city", ""))
