import asyncio
import base64
import json
import os
import random
import uuid

import requests
import urllib3

import gameDataAes2Json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
BASE = "https://rizserver.pigeongames.net"


def save_config(cfg):
    out = {
        "device_id": cfg["device_id"],
        "channel_id": str(cfg["channel_id"]),
        "token": cfg.get("token", ""),
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)


def phone_from_token(token: str) -> str:
    if not token or token.count(".") < 2:
        return ""
    payload = token.split(".")[1]
    payload += "=" * ((-len(payload)) % 4)
    try:
        data = json.loads(base64.urlsafe_b64decode(payload))
        return str(data.get("phone") or "")
    except Exception:
        return ""


def load_or_create_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = {}
        print(f"将创建 {CONFIG_PATH}")
    if not cfg.get("device_id"):
        cfg["device_id"] = str(uuid.uuid4())
    if not cfg.get("channel_id"):
        cfg["channel_id"] = str(random.randint(1, 11))
    cfg["token"] = cfg.get("token", "")
    save_config(cfg)
    return cfg


class user:
    def __init__(self, device_id, channel_id, token=""):
        self.device_id = device_id
        self.channel_id = str(channel_id)
        self.token = token or ""
        self.phone = phone_from_token(self.token)

    def headers(self):
        h = {
            "User-Agent": "UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)",
            "game_id": "pigeongames.rizline",
            "device_id": self.device_id,
            "channel_id": self.channel_id,
            "i18n": "zh-CN",
            "Content-Type": "application/json",
            "X-Unity-Version": "2022.3.62f2",
        }
        if self.phone:
            h["phone"] = self.phone
        if self.token:
            h["token"] = self.token
        return h

    async def request(self, url, data=None, method="POST"):
        if method == "GET":
            response = requests.get(url, headers=self.headers(), verify=False)
        else:
            response = requests.post(url, headers=self.headers(), json=data if data is not None else {}, verify=False)
        print(f"\n{method} {url}")
        print(f"状态码：{response.status_code}  body bytes: {len(response.content)}")
        print("响应头：")
        for k, v in response.headers.items():
            print(f"{k}: {v}")
        ctype = (response.headers.get("Content-Type") or "").lower()
        if "json" in ctype or "text" in ctype:
            print(f"响应文本：{response.text[:500]}")
        else:
            print(f"二进制 hex前64: {response.content[:64].hex()}")
        return response

    def persist_token(self):
        save_config({
            "device_id": self.device_id,
            "channel_id": self.channel_id,
            "token": self.token,
        })

    def is_expired(self, response):
        if response.status_code != 401:
            return False
        return response.text.strip().lower() in ("expired", "unauthorized")

    def clear_token(self):
        self.token = ""
        self.persist_token()
        print("token 已过期，已从 config.json 清除")

    def take_token(self, response):
        for k, v in response.headers.items():
            if k.lower() in ("set_token", "set-token", "token"):
                self.token = v
                self.persist_token()
                print(f"\n登录成功，token已写入 {CONFIG_PATH}")
                return True
        return False

    async def send_verify_code(self):
        return await self.request(
            f"{BASE}/account/send_verify_code",
            {"phone": self.phone, "transaction": "login"},
        )

    async def login_with_code(self):
        await self.send_verify_code()
        code = input("请输入验证码：").strip()
        result = await self.request(
            f"{BASE}/account/login",
            {"phone": self.phone, "code": code},
        )
        return self.take_token(result)

    async def login(self):
        if self.token:
            self.phone = self.phone or phone_from_token(self.token)
            print(f"使用已保存 token（phone={self.phone}）")
            return
        self.phone = input("请输入手机号：").strip()
        password = input("请输入密码（空则验证码登录）：")
        check = await self.request(f"{BASE}/account/check_phone", {"phone": self.phone})
        try:
            check_code = check.json().get("code")
        except Exception:
            check_code = None
        print(f"check_phone code={check_code}")

        if check_code == 1 or not password:
            await self.login_with_code()
            return

        result = await self.request(
            f"{BASE}/account/login",
            {"phone": self.phone, "password": password},
        )
        try:
            body = result.json()
            login_code = body.get("code")
            login_msg = body.get("msg")
        except Exception:
            login_code = None
            login_msg = None
        print(f"login code={login_code} msg={login_msg}")

        if login_code == 0 and self.take_token(result):
            return
        if login_code == 3:
            await self.login_with_code()
            return
        self.take_token(result)

    async def getUserInfo(self):
        result = await self.request(f"{BASE}/game/rn_login", {})
        if self.is_expired(result):
            self.clear_token()
            await self.login()
            result = await self.request(f"{BASE}/game/rn_login", {})
        for k, v in result.headers.items():
            if k.lower() == "user-id":
                print(f"\nuser-id: {v}")
            if k.lower() == "sign":
                print(f"\nsign(Ed25519): {v}")
        resultGameData = gameDataAes2Json.rizline_aes_decrypt(result.content)
        print("\n解密后的游戏数据：" + str(resultGameData))
        if resultGameData:
            with open("gameData.json", "w", encoding="utf-8") as f:
                f.write(resultGameData)

    async def getShop(self):
        result = await self.request(f"{BASE}/game/get_user_shop", {"refresh": False})
        if self.is_expired(result):
            self.clear_token()
            await self.login()
            result = await self.request(f"{BASE}/game/get_user_shop", {"refresh": False})
        decoded = gameDataAes2Json.rizline_aes_decrypt(result.content)
        print(decoded if decoded is not None else result.text)


if __name__ == "__main__":
    cfg = load_or_create_config()
    userI = user(cfg["device_id"], cfg["channel_id"], cfg.get("token", ""))
    asyncio.run(userI.login())
    asyncio.run(userI.getUserInfo())
    asyncio.run(userI.getShop())
