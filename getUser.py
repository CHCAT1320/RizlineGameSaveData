import requests
import asyncio
import gameDataAes2Json
import base64
import json

class user:
    def __init__(self, phone):
        self.phone = phone
        self.token = ""

    async def request(self, url, headers, data = {}, type = "GET"):
        if type == "GET":
            response = requests.get(url, headers=headers, verify=False)
        elif type == "POST":
            response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
        # 打印响应内容
        print(f"\n响应内容：{response.text}")
        try:
            print("\n响应JSON数据（字典格式）：")
            print(response.json())
        except:
            print("\n本次响应非标准JSON格式")

        # 可选：打印响应状态码、响应头，验证请求是否成功
        print(f"\n请求状态码：{response.status_code}")
        print(f"\n服务器返回的响应头：")
        for k, v in response.headers.items():
            print(f"{k}: {v}")
        return response

    async def sendVerifyCode(self):
        # 目标请求链接
        url = "https://rizserver.pigeongames.net/account/send_verify_code"

        # 你的完整请求头（原样复制，全部保留，这是请求成功的核心）
        headers = {
        "Host": "rizserver.pigeongames.net",
        "game_id": "pigeongames.rizline",
        "device_id": "f18c2696-461d-43a2-a214-f27fb85811a1",
        "channel_id": "11",
        "i18n": "zh-CN",  
        "phone": self.phone
        }
        await self.request(url, headers, {
            "phone": self.phone,
            "transaction": "login"
        }, "POST")

    async def login(self, password):
        # 目标请求链接
        url = "https://rizserver.pigeongames.net/account/login"

        # 你的完整请求头（原样复制，全部保留，这是请求成功的核心）
        headers = {
        # "Host": "rizserver.pigeongames.net",
        "User-Agent": "UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)",
        "game_id": "pigeongames.rizline",
        "device_id": "0224fa25-254f-49d0-84b7-0df4f5de63b6",
        "channel_id": "11",
        "i18n": "zh-CN",
        "Content-Type": "application/json",
        "phone": self.phone,
        }
        if password == "":
            await self.sendVerifyCode()
            verifyCode = input("请输入验证码：")
            result = await self.request(url, headers, {
                "phone": self.phone,
                "code": verifyCode
            }, "POST")
        else:
            result = await self.request(url, headers, {
                "phone": self.phone,
                "password": password
            }, "POST")
        for k, v in result.headers.items():
            if k == "set_token":
                print(f"\n登录成功，token为：{v}")
                self.token = v

    async def getUserInfo(self):
        # 目标请求链接
        url = "https://rizserver.pigeongames.net/game/rn_login"
        headers = {
        "Host": "rizserver.pigeongames.net",
        "User-Agent": "UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)",
        "game_id": "pigeongames.rizline",
        "device_id": "f18c2696-461d-43a2-a214-f27fb85811a1",
        "channel_id": "11",
        "i18n": "zh-CN",
        "Content-Type": "application/json",
        "phone": self.phone,
        "verify": "0914bf42-87bf",
        "token": self.token
        }
        result = await self.request(url, headers, {}, "POST")
        for k, v in result.headers.items():
            if k == "user-id":
                print(f"\n获取用户信息成功，user-id为：{v}")
            if k == "sign":
                print(f"\n获取用户信息成功，sign为：{v}")
                print(gameDataAes2Json.rizline_aes_decrypt(base64.b64decode(v)))
        print(result.text)
        resultGameData = gameDataAes2Json.rizline_aes_decrypt(base64.b64decode(result.text))
        print("\n解密后的游戏数据：" + resultGameData)
        with open("gameData.json", "w", encoding="utf-8") as f:
            f.write(resultGameData)
    
    async def getShop(self):
        # 目标请求链接
        url = "https://rizserver.pigeongames.net/game/get_user_shop"
        headers = {
        "Host": "rizserver.pigeongames.net",
        "User-Agent": "UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)",
        "game_id": "pigeongames.rizline",
        "device_id": "f18c2696-461d-43a2-a214-f27fb85811a1",
        "channel_id": "11",
        "i18n": "zh-CN",
        "Content-Type": "application/json",
        "phone": self.phone,
        "verify": "0914bf42-87bf",
        "token": self.token
        }
        result = requests.post(url, headers=headers, data={"refresh":False}, verify=False)
        b64_str = result.text.strip()
        padding = 4 - len(b64_str) % 4
        if padding != 4:
            b64_str += '=' * padding
        print(gameDataAes2Json.rizline_aes_decrypt(base64.b64decode(b64_str)))

if __name__ == '__main__':
    phone = input("请输入手机号：")
    userI = user(phone)
    password = input("请输入密码：")
    asyncio.run(userI.login(password))
    asyncio.run(userI.getUserInfo())
    asyncio.run(userI.getShop())



