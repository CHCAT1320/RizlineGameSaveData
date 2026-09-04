# 接口字段说明

基址 `https://rizserver.pigeongames.net`。除特别说明外都是 `POST`。

## 通用约定

### 请求头

| 头 | 含义 |
| --- | --- |
| `game_id` | 固定 `pigeongames.rizline` |
| `device_id` | 本机 UUID，同一设备保持不变 |
| `channel_id` | 渠道，字符串 `"1"`～`"11"` |
| `i18n` | 语言，国服 `zh-CN` |
| `phone` | 登录手机号。用已保存 token 时也要从 JWT 带上 |
| `token` | 登录后 `set_token` 的 JWT |
| `Content-Type` | `application/json` |

### 游戏接口外层

成功时 body 多为 GCM 密文，解开后：

```json
{"code":0,"data": ...}
```

| 字段 | 含义 |
| --- | --- |
| `code` | `0` 成功，非 0 失败 |
| `data` | 业务数据，类型随接口变（对象 / 数组 / 字符串 / 布尔 / null） |
| `msg` | 失败说明（账号接口常见） |
| `errorCode` / `message` | 游戏 `Resp` 失败码和文案 |

特例：`/game/rn_login` 解开后**没有** `code/data`，直接是存档对象。

HTTP 层：`401` + 正文 `Expired` 表示 token/头不对；HTML `Cannot POST /xxx` 表示这条路由不存在。

标记：`[已测]` 实测；`[客户端]` dump 结构，未打或写操作未打；`[404]` 当前服无路由。

---

## 1. 账号

### `POST /account/check_phone` [已测]

查这个手机号当前该走账密还是验证码。

请求：

| 字段 | 含义 |
| --- | --- |
| `phone` | 手机号 |

返回（明文 JSON）：

| 字段 | 含义 |
| --- | --- |
| `code` | `0` 可账密；`1` 必须验证码 |

### `POST /account/send_verify_code` [已测]

发短信。不要频繁打。

请求：

| 字段 | 含义 |
| --- | --- |
| `phone` | 手机号 |
| `transaction` | 用途，登录填 `login` |

返回明文 JSON，验证码约 2 分钟有效。

### `POST /account/login` [已测]

登录。请求二选一。

账密：

| 字段 | 含义 |
| --- | --- |
| `phone` | 手机号 |
| `password` | 密码 |

验证码：

| 字段 | 含义 |
| --- | --- |
| `phone` | 手机号 |
| `code` | 短信验证码 |

返回明文 JSON + 响应头：

| 位置 | 字段 | 含义 |
| --- | --- | --- |
| body `code` | `0` | 成功 |
| body `code` | `3` | 账密被拒，改验证码 |
| body `msg` | | 失败原因 |
| header `set_token` | JWT | 之后所有 `/game/` 请求都要带。payload 含 `userId`、`phone`、`gameId`、`channelId`、`iat`、`exp`（约 7 天） |

### `POST /account/register` [客户端]

注册。请求至少含手机号/验证码/密码一类字段。未测。

### `POST /account/user/change_password` [客户端]

改密码。未测。

### `POST /account/user/change_phone` [客户端]

换绑手机。未测。

### `POST /account/user/check_code` [客户端]

校验验证码是否正确。未测。

### `POST /account/user/cancellation` [客户端]

注销账号。未测。

### `POST /account/user/bind_id2meta` [客户端]

绑定其它账号体系。未测。

### `POST /account/user/bind_id2meta_taptap` [客户端]

绑定 TapTap。未测。

### `POST /account/Insensitive_login` [客户端]

另一套登录入口（客户端字符串）。未测。

---

## 2. 存档与用户

### `POST /game/rn_login` [已测]

拉云存档。请求 `{}`。

解密后直接是用户文档（不是 `{code,data}`）。字段：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `_id` | string | Mongo 文档 id |
| `userId` | string | 对外用户 id，JWT 里也是这个 |
| `username` | string | 昵称 |
| `coin` | number | 金币 |
| `dot` | number | 点券 |
| `totalRks` | number | 总 RKS |
| `userBatch` | int | 用户批次 |
| `rizcard` | object | 当前展示的名片 |
| `rizcard.avatarPos.x/y/z` | number | 头像在插画上的裁剪位置 |
| `rizcard.avatarId` | string | 头像用的插画资源 id |
| `rizcard.bioId1` / `bioId2` | string | 两条签名/称号，常为 `ach.[成就].titleN` 或 `bio.xxx` |
| `rizcard.backgroundId` | string | 名片背景插画 |
| `rizcard.layoutId` | string | 名片排版，如 `layout.00022` |
| `rizcard.createTime` | string | 名片创建时间 ISO |
| `myBest[]` | array | 各谱最好成绩 |
| `myBest[].trackAssetId` | string | 曲目资源 id，如 `track.曲名.曲师.0` |
| `myBest[].difficultyClassName` | string | 难度：`EZ` / `HD` / `IN` / `AT` |
| `myBest[].score` | int | 分数 |
| `myBest[].completeRate` | float | 完成率（百分比数值） |
| `myBest[].isFullCombo` | bool | 是否 FC |
| `myBest[].isClear` | bool | 是否通关 |
| `levelsRks[]` | array | 计入 RKS 的谱面 |
| `levelsRks[].trackId` | string | 曲目 id |
| `levelsRks[].difficultyClassName` | string | 难度 |
| `levelsRks[].rks` | float | 该谱 RKS |
| `unlockedLevels[]` | string[] | 已解锁曲目 |
| `appearLevels[]` | string[] | 选曲列表里出现过的曲目 |
| `getItems[]` | array | 背包 |
| `getItems[].itemAssetId` | string | 物品 id：`bio.*` 签名、`layout.*` 排版、`mod.*` 模组、插画等 |
| `getItems[].amount` | int | 数量 |
| `getOwnProducts[]` | array | 已购商品计数 |
| `getOwnProducts[].goodId` | int | 商品数字 id |
| `getOwnProducts[].purchaseCount` | int | 购买次数 |
| `getProducts[]` | array | 商城货架，按活动分组 |
| `getProducts[].eventId` | int | 活动/货架分组 |
| `getProducts[].goods[]` | array | 商品列表 |
| `goods[].id` | int | 商品 id |
| `goods[].content` | string | 买到的资源 id，空表示货币类 |
| `goods[].costs[]` | array | 价格 `{type:"coin"|"dot", amount}` |
| `goods[].onSalePercent` | number | 折扣，`1` 为原价 |
| `goods[].getLimit` | int | 限购；`-1` 不限 |
| `goods[].preTask` | string | 购买前置，如 `8&0` 表示要先买过某货 |
| `goods[].clientCanBuy` | bool | 客户端是否显示可买 |
| `getOwnAchievements[]` | array | 已获得成就 |
| `getOwnAchievements[].achievementId` | string | 成就 id |
| `getOwnAchievements[].getTime` | string | 获得时间 ISO |
| `ownRizcards.rizcards[]` | array | 交换来的玩家名片（结构同 `fetch_own_rizcard`） |
| `ownRizcards.staticRizcards[]` | array | 角色/活动静态名片 `{_id, cardId, exchangeTime}` |
| `ownRizcards.readed` | int | 已读名片数 |
| `mails[]` | array | 邮件，字段同 `get_mails` |
| `mailSyncId` | number | 邮件同步游标，和 `get_mails.syncId` 对应 |
| `challenge[]` | array | 课题关定义 |
| `challenge[].id` | int | 课题 id |
| `challenge[].chartId` | string | 谱面 id |
| `challenge[].name` / `describe` / `conditionDesc` | string | 标题/描述/通关条件的本地化 key |
| `challenge[].type` / `series` | int | 类型、系列 |
| `challenge[].passRate` | float | 通关所需完成率，如 `0.6` |
| `challenge[].passCondition` / `drop` / `passRelatedId` | | 额外通关条件和掉落 |
| `challengeProgress[]` | array | `{levelId, passed}` 是否已通该课题 |
| `features[]` | string[] | 功能开关，常为空 |
| `staticRizcards` | array | 存档顶层另一份静态名片列表，可能为空 |

### `POST /game/fetch_user_info` [已测]

请求 `{}`。

`data`：

| 字段 | 含义 |
| --- | --- |
| `username` | 昵称 |
| `dot` | 点券 |
| `coin` | 金币 |
| `features` | 功能开关，常 `[]` |

### `POST /game/change_username` [客户端]

请求：

| 字段 | 含义 |
| --- | --- |
| `username` | 新昵称 |

成功时 `data` 可空。未测。

### `POST /game/inherit_data` [客户端]

请求：

| 字段 | 含义 |
| --- | --- |
| `transCode` | 数据继承码 |

返回 `Resp`：`code`、`errorCode`、`message`。未测。

### `POST /game/game_start` [已测]

请求 `{}`。

`data`：32 位 hex 字符串，本局 `gameplayId`。结算 `after_play` 要带这个。每次调用都会换新 id。

---

## 3. 商店与购买

### `POST /game/get_user_shop` [已测]

请求：

| 字段 | 含义 |
| --- | --- |
| `refresh` | `false` 只读当前货架；`true` 刷新（会消耗刷新次数） |

`data`：

| 字段 | 含义 |
| --- | --- |
| `shop[]` | 当日货架 |
| `shop[].id` | 商品资源 id。单个如 `layout.00007`；成对 bio 为 `bio.A;bio.B` |
| `shop[].price` | 总价 |
| `shop[].leftPrice` / `rightPrice` | 成对 bio 时左右半价 |
| `shop[].isCoinPrice` | `true` 花金币，`false` 花点券 |
| `newcomerShop[]` | 新手货架，字段同上 |
| `enableNewcomerFeature` | 是否还开新手商店 |
| `refreshTime` | 下次自然刷新时间 ISO |
| `refreshed` | 本周期是否已手动刷新过 |

### `POST /game/buy_user_shop_item` [客户端]

请求：

| 字段 | 含义 |
| --- | --- |
| `itemId` | 对应 `shop[].id` |

买当日货架。未测。

### `POST /game/purchase` [客户端]

请求：

| 字段 | 含义 |
| --- | --- |
| `goodId` | 商城数字商品 id，对应存档 `getProducts.goods.id` |

返回 `PurchaseResultInfo`：

| 字段 | 含义 |
| --- | --- |
| `newLevels[]` | 新解锁谱 `{trackAssetId, level}` |
| `newItems[]` | 新物品 `{itemAssetId, amount}` |
| `newDots` | 购买后点券 |
| `newCoins` | 购买后金币 |

未测。

### `POST /game/query_purchase_info` [已测]

请求：

| 字段 | 含义 |
| --- | --- |
| `goodId` | 商品数字 id |

`data`：`true` 已买过，`false` 未买。

---

## 4. 成绩与活动

### `POST /game/after_play` [客户端]

上传一局结算。请求主体是 `ResultParams`（另加结算细节）：

| 字段 | 含义 |
| --- | --- |
| `gameplayId` | `game_start` 拿到的本局 id |
| `trackAssetId` | 曲目 id |
| `difficultyClassName` | 难度 |
| `score` | 分数 |
| `completeRate` | 完成率 |
| `completeRateScale` | 完成率缩放 |
| `maxPerfect` / `perfect` / `miss` / `bad` / `early` / `late` | 判定统计 |
| `comboScore` | 连击分 |
| `leftHp` | 剩余血量 |
| `chartSpeed` | 流速 |
| `hitFXVolume` | 打击音量 |
| `offsetMs` | 偏移毫秒 |
| `updateRks` | 是否更新 RKS |
| `activeMods[]` | 启用的模组 |
| `d00219` | 特殊曲额外：`variant`、`riztimeTriggered` |

返回 `AfterPlayResult`：

| 字段 | 含义 |
| --- | --- |
| `newDot` | 结算后点券 |
| `deltaDot` | 本局点券变化 |
| `newItems[]` | 新掉落物品 |
| `newLevels[]` | 新解锁谱 |
| `canBuyLevels[]` | 变为可购买的谱 |
| `levelRks` | 本谱 RKS |
| `totalRks` | 总结算后总 RKS |
| `modeResult` | 若在周挑战，见第 8 节 `WeeklyModeResult` |

未测（会改存档）。

### `POST /game/after_play_in_challenge` [客户端]

课题模式结算。请求含 `levelId` + 一局结果。

返回：

| 字段 | 含义 |
| --- | --- |
| `levelId` | 课题 id |
| `progress[]` | `{levelId, passed}` 最新通关表 |
| `dropPriceItems[]` | 掉落 `{itemId, num}` |

未测。

### `POST /game/watch_complete` [客户端]

看完演出/谱面视频。

| 字段 | 含义 |
| --- | --- |
| `gameplayId` | 本局 id |
| `trackAssetId` | 曲目 |
| `musicId` | 音乐 id |
| `difficultyClassName` | 难度 |
| `isAutoPlay` | 是否自动播放 |

未测。

### `POST /game/get_order_event_state` [已测]

请求：

| 字段 | 含义 |
| --- | --- |
| `eventId` | 活动 id |

`data` 无活动时为 `null`。有活动时为 `OrderEventInfo`：

| 字段 | 含义 |
| --- | --- |
| `oneCoin` | 是否买过 1 金币档 |
| `fiveCoin` | 是否买过 5 金币档 |
| `elevenCoin` | 是否买过 11 金币档 |

### `POST /game/special_event` [404]

客户端请求：

| 字段 | 含义 |
| --- | --- |
| `id` | 活动 id |
| `onlyCheck` | `true` 只查询不提交 |
| `newStar` | 新星数 |

当前服没有这条路由。

### `POST /game/rn/redeem_gift_code` [客户端]

兑换码。未测。

---

## 5. 名片与记忆色

名片 `rizcard` 各字段见 `rn_login` 表。

### `POST /game/set_rizcard` [客户端]

请求体就是一份 `rizcard`。未测。

### `POST /game/fetch_own_rizcard` [已测]

请求：

| 字段 | 含义 |
| --- | --- |
| `serialAfter` | 分页游标，`0` 从头拉；之后用上一页最大 `cardSerial` |

`data`：

| 字段 | 含义 |
| --- | --- |
| `cards[]` | 交换来的名片 |
| `cards[]._id` | 记录 id |
| `cards[].cardSerial` | 序号，用于下一页 `serialAfter` |
| `cards[].userId` | 对方用户 id |
| `cards[].userName` | 对方昵称 |
| `cards[].exchangeTime` | 交换时间 |
| `cards[].rizcard` | 对方当时的名片 |

另外客户端类型还有 `cardsBefore`（这一页之前还有几张）。

### `POST /game/update_own_rizcard_read` [客户端]

请求：

| 字段 | 含义 |
| --- | --- |
| `readed` | 已读数量 |

未测。

### `POST /game/fetch_static_rizcard_progress` [已测]

`data.staticRizcardProgresses[]`：

| 字段 | 含义 |
| --- | --- |
| `achievementId` | 对应成就 |
| `cardId` | 静态名片 id，如 `rizcard.yong_ge_card1` |
| `amount` | 当前收集进度 |
| `targetAmount` | 目标数量 |
| `state` | 如 `owned` 已拥有 |

### `POST /game/fetch_memory_progress` [已测]

`data`：

| 字段 | 含义 |
| --- | --- |
| `globalProgress` | 总进度 |
| `memoryProgress.selectedColor` | 当前选中颜色，如 `red` |
| `memoryProgress.blackTriggered` / `whiteTriggered` | 黑/白线是否触发 |
| `memoryProgress.unlocked` | 记忆色系统是否解锁 |
| `memoryProgress.allStar` / `maxStar` | 当前星 / 满星 |
| `memoryProgress.colors[]` | 七色进度 |
| `colors[].color` | `red/orange/yellow/green/cyan/blue/purple` |
| `colors[].progress` / `maxProgress` | 该色进度 |
| `colors[].lit` | 是否点亮 |
| `colors[].eroded` | 是否被侵蚀 |
| `colors[].targetRevealed` | 目标曲是否揭晓 |
| `colors[].targetTrackId` | 揭晓后的曲目 id |

### `POST /game/fetch_memory_color` [已测]

`data`：当前颜色字符串，例如 `"red"`。

### `POST /game/set_memory_color` [客户端]

请求：

| 字段 | 含义 |
| --- | --- |
| `color` | 要选的颜色 |

未测。

---

## 6. 公告、邮件、预约

### `POST /game/get_broadcasts` [已测]

请求 `{}`。

`data`：

| 字段 | 含义 |
| --- | --- |
| `syncId` | 公告版本。客户端用它判断要不要刷新列表 |
| `broadcasts[]` | 公告列表，无公告时 `[]` |
| `broadcasts[].broadcastId` | 公告 id |
| `broadcasts[].message` | 展示文案 |
| `broadcasts[].startTime` / `endTime` | 生效区间 |
| `broadcasts[].interval` | 重复间隔（秒一类） |
| `broadcasts[].isCountdown` | `true` 倒计时条，`false` 滚动文字 |

只给游戏内 Toast 用，不是存档。

### `POST /game/get_mails` [已测]

请求 `{}`。

`data`：

| 字段 | 含义 |
| --- | --- |
| `syncId` | 邮件同步游标 |
| `mails[]` | 邮件 |
| `mails[]._id` | 记录 id |
| `mails[].mailId` | 业务 id，读写删都用这个 |
| `mails[].title` / `content` | 标题、正文 |
| `mails[].linkText` / `linkUrl` | 可选跳转（客户端有，实测邮件可能没有） |
| `mails[].receivedTime` / `expiredTime` | 收到 / 过期 ISO |
| `mails[].read` | 是否已读 |
| `mails[].deleted` | 是否已删 |
| `mails[].attachments[]` | 附件 |
| `attachments[]._id` | 附件记录 id |
| `attachments[].itemId` | 物品：`dot` 点券、`coin` 金币、或其它 item id |
| `attachments[].num` | 数量 |

### `POST /game/read_mail` [客户端]

请求：

| 字段 | 含义 |
| --- | --- |
| `mailId` | 字符串数组，要领取的邮件 |

返回附件数组 `{itemId, num}`。未测。

### `POST /game/delete_mail` [客户端]

请求：

| 字段 | 含义 |
| --- | --- |
| `mailId` | 要删的邮件 id 数组 |

未测。

### `POST /game/get_booking_status` [404]

当前服无路由。客户端本意是查预约状态。

### `POST /game/set_booking_status` [客户端]

请求：

| 字段 | 含义 |
| --- | --- |
| `phone` | 预约手机号 |

未测。

---

## 7. 周任务

### `POST /game/get_weekly_tasks` [已测]

请求 `{}`。

`data`：

| 字段 | 含义 |
| --- | --- |
| `weekIndex` | 第几周 |
| `nextRefreshAt` | 下次刷新 ISO |
| `tasks[]` | 本周任务 |
| `tasks[].taskId` | 任务 id，领奖用 |
| `tasks[].name` | 任务名（可能是本地化后的中文） |
| `tasks[].progress` | 当前进度 |
| `tasks[].target` | 目标值 |
| `tasks[].completed` | 是否完成 |
| `tasks[].rewarded` | 是否已领奖 |
| `tasks[].reward.itemId` | 奖励物品，常见 `dot` |
| `tasks[].reward.amount` | 奖励数量 |

### `POST /game/claim_weekly_task_reward` [客户端]

请求：

| 字段 | 含义 |
| --- | --- |
| `taskId` | 任务 id |

返回：

| 字段 | 含义 |
| --- | --- |
| `taskId` | 刚领的任务 |
| `reward.itemId` / `reward.amount` | 实际发到的奖励 |

未测。

---

## 8. 周挑战

客户端类型齐全，但下列 URL 当前都是 404：`GetWeeklyRankInfo`、`get_weekly_rank_info`、`weekly_rank_info`、`weekly_config`、`get_weekly_config`、`EnsureWeeklyConfig`、`weekly_player_info` 等。真实路径需抓包。按 dump，数据长这样：

### 周配置 `WeeklyConfigResult`

| 字段 | 含义 |
| --- | --- |
| `seasonId` | 赛季 |
| `rotationId` | 轮换 id |
| `rotationIndex` | 本季第几轮 |
| `startTime` / `endTime` | 本轮时间 |
| `songs[].trackAssetId` | 本轮指定曲 |

### 玩家周信息 `WeeklyPlayerInfoResult`

| 字段 | 含义 |
| --- | --- |
| `seasonId` / `rotationId` | 赛季、轮换 |
| `songs[]` | 各指定曲自己的最好 |
| `songs[].trackAssetId` | 曲目 |
| `songs[].playerBest[]` | 各难度最好 `{difficultyClassName, bestLevelRks, result}` |
| `rank` | 当前段位，见下 |
| `pendingMatchResults[]` | 还没点掉的对局结果 |
| `recoveredMatchResult` | 异常中断后恢复的一局 |

### 段位 `WeeklyRankData`

| 字段 | 含义 |
| --- | --- |
| `isPlaced` | 是否已定级 |
| `placementCount` | 定级赛场次 |
| `placementResults[]` | 定级赛结果 |
| `segment` | 段位数字 |
| `segmentName` | 段位名 |
| `isPlus` | 是否 Plus |
| `stars` | 当前星 |
| `absStars` | 绝对星数 |
| `potentialLevel` | 潜力等级 |
| `totalWin` / `totalLose` | 胜负场 |

### 匹配 `WeeklyMatchResult`

| 字段 | 含义 |
| --- | --- |
| `matchId` | 对局 id，开局要带 |
| `isNpc` | 对手是不是 NPC |
| `reservationExpiresAt` | 预约过期时间 |
| `opponent` | 对手资料 |

请求：`trackAssetId`（选哪首）、`difficultyClassName`（选哪档）。会改状态，未测。

### 开局 `WeeklyGameStartResult`

请求：`{"matchId":"..."}`。

| 字段 | 含义 |
| --- | --- |
| `gameplayId` | 本局游玩 id |
| `clientSessionId` | 客户端会话 |
| `seasonId` / `rotationId` | 赛季、轮换 |
| `settlementDeadline` | 必须在此之前结算 |

未测。

### 周挑战结算 `WeeklyModeResult`（夹在 `after_play` 里）

| 字段 | 含义 |
| --- | --- |
| `mode` / `matchId` | 模式、对局 |
| `status` / `result` | 状态、胜负 |
| `levelRks` / `bestLevelRks` / `isNewBest` | 本局/最好 RKS |
| `starDelta` | 星数变化 |
| `rankBefore` / `rankAfter` | 结算前后段位 |
| `segmentChanged` | 是否升/降段 |
| `forfeit` | 是否弃权 |

### 排行详情 `WeeklyRankInfoResult`

| 字段 | 含义 |
| --- | --- |
| `rank` / `currentRank` | 当前段位 |
| `currentSeasonBestRank` | 本赛季最高 |
| `currentSeasonStartingRank` | 开赛段位 |
| `currentSeasonStats` | 本赛季主动/被动战绩 `{matchCount, winCount, currentWinStreak, bestWinStreak}` |
| `lifetimeStats` | 生涯同样结构 |
| `recentMatches[]` | 近期对局：曲目、难度、对手、胜负、`starDelta`、双方名片和成绩 |

---

## 9. 实时

WebSocket：`/websocket/pigeongames.rizline`  
测试：`/websocket_test/pigeongames.rizline`

在线房间等，不是拉存档。
