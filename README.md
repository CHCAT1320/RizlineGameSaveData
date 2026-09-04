
# RizlineGameSaveData

获取游戏Rizline律动轨迹的游戏存档

当前支持

手机号+密码登录

手机号+短信验证码登录

暂不支持国际服邮箱登录

最后通过ase算法把存档解密

该库只可用于游戏查分

禁止用该项目做不利于鸽游的事情，包括短信轰炸，频繁请求数据等

该项目与鸽游无关


## 当前客户端加解密（AES-GCM）

旧版本云存档是 AES-256-CBC，密钥/IV 硬编码在客户端里。新版本（当前国服 APK）已经换成 **AES-256-GCM**，旧 CBC 脚本会解失败。

密文布局（HTTP body 多为 `application/octet-stream` 原始字节，不一定是 Base64）：

```
nonce(12) || ciphertext || tag(16)
```

密钥不直接明文存放，而是两段静态数组 `_m0` / `_p0` 经 `Unfold` 还原：

1. 按 `_p0` 把 `_m0` 以 4 字节块重排
2. 再滚动 XOR：`out[i] ^= (salt + 7 * (i >> 2))`，每字节 `salt += 13`，salt 初值 `0xA7`

还原后的 AES-256 key 为 32 字节 ASCII。`gameDataAes2Json.py` 已按该流程实现。响应头 `sign` 是 Ed25519 签名，不是 AES 密文。

商店等接口有时直接返回 JSON，解密函数会先尝试 GCM，失败再按明文处理。

## 登录与拉档流程

参考客户端与 [HiXcc/RizlineSavingTest](https://github.com/HiXcc/RizlineSavingTest)：

1. `POST /account/check_phone`  
   - `code == 0`：可用账密  
   - `code == 1`：需要验证码
2. `POST /account/login`  
   - 账密：`{"phone","password"}`  
   - 验证码：先 `POST /account/send_verify_code`（`transaction: login`），再 `{"phone","code"}`  
   - 账密返回 `code == 3` 时改走验证码
3. token 在响应头 `set_token` 里（JWT，约 7 天）
4. 带 token 拉数据：  
   - `POST /game/rn_login`：存档（GCM）  
   - `POST /game/get_user_shop`：商店  
   - `POST /game/get_broadcasts`：游戏内滚动公告/倒计时，不是存档

公共请求头：

```
game_id: pigeongames.rizline
device_id: uuid4（同一设备固定）
channel_id: 1-11
i18n: zh-CN
phone: 登录手机号（用已保存 token 时也要从 JWT 里带上，否则会 401 Expired）
token: set_token 的值
Content-Type: application/json
```

`401 Expired` 不一定是 JWT 过期，缺 `phone` 头也会返回这个字符串。

## 本地运行

```
python getUser.py
```

首次无 token 时输入手机号/密码（或空密码走验证码）。成功后只把 `device_id`、`channel_id`、`token` 写入 `config.json`，不保存手机号和密码。存档明文写到 `gameData.json`。这两个文件已加入 `.gitignore`。

token 失效时脚本会清掉本地 token 并重新登录。

每个接口的请求/返回字段含义见 [API.md](API.md)。

## 存档 JSON（`/game/rn_login`）

解密后是一整份用户文档，不是 `{"code":0,"data":...}` 包一层。

| 字段 | 含义 |
| --- | --- |
| `_id` | 数据库文档 id |
| `userId` | 对外用户 id（JWT 里也是它） |
| `username` | 昵称 |
| `coin` | 金币 |
| `dot` | 点券 |
| `totalRks` | 总 RKS |
| `userBatch` | 用户批次 |
| `rizcard` | 当前名片，见下 |
| `myBest` | 各谱最好成绩 |
| `levelsRks` | 计入总分的单谱 RKS |
| `unlockedLevels` | 已解锁曲目 id 列表 |
| `appearLevels` | 选曲界面出现过的曲目 |
| `getItems` | 背包：签名/排版/模组/插画等 |
| `getOwnProducts` | 已购商城商品及次数 |
| `getProducts` | 商城货架（按活动分组） |
| `getOwnAchievements` | 已获成就和时间 |
| `ownRizcards` | 交换名片 + 静态名片 + 已读数 |
| `mails` / `mailSyncId` | 邮件和同步游标 |
| `challenge` / `challengeProgress` | 课题定义 / 是否已通 |
| `features` | 功能开关，常为空 |

`rizcard`：`avatarPos{x,y,z}` 头像裁剪；`avatarId` 头像插画；`bioId1/bioId2` 两条称号；`backgroundId` 背景；`layoutId` 排版；`createTime` 创建时间。

`myBest[]`：`trackAssetId` 曲目；`difficultyClassName` 为 EZ/HD/IN/AT；`score` 分数；`completeRate` 完成率；`isFullCombo` / `isClear` 是否 FC/通关。

更细的字段表在 [API.md](API.md) 的 `rn_login` 一节。

## 接口一览

完整逐字段说明：[API.md](API.md)。

- 账号：`check_phone` / `login` / `send_verify_code`（已测）；注册改密换绑未测
- 存档：`rn_login`、`fetch_user_info`、`game_start`（已测）
- 商店：`get_user_shop`、`query_purchase_info`（已测）；购买未测
- 邮件公告：`get_mails`、`get_broadcasts`（已测）
- 名片记忆色：`fetch_own_rizcard`、`fetch_static_rizcard_progress`、`fetch_memory_*`（已测）
- 周任务：`get_weekly_tasks`（已测）；领奖未测
- 周挑战相关 URL 当前多为 404，结构见 API.md 第 8 节
