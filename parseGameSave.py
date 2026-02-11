from PIL import Image, ImageFilter, ImageFont, ImageDraw
import os
import random
import json

class userGameData:
    def __init__(self, data: dict):
        self.resultImg = None
        self.data = data

    def generateBlurBackground(self, bgPath: str, width: int = 1200, height: int = 1876):
        # 打开曲绘
        with Image.open(bgPath) as src_img:
            # 高斯模糊曲绘
            blurred_img = src_img.filter(ImageFilter.GaussianBlur(radius=15))
            
            # 创建1200×1876的空白画布
            background = Image.new("RGBA", (width, height))
            
            result = blurred_img.resize((height, height))
            # 粘贴到空白画布
            background.paste(result, (int(-height / 5), 0), result)

            self.resultImg = background
        
    def drawVersion(self):
        font_size = 24
        font = ImageFont.truetype("./rizline.ttf", font_size)
        
        textColor = (27, 179, 252)
        borderColor = (0, 0, 0)
        text1 = "rzlRSI v0.0.1"
        text2 = "All Code By CHCAT1320"
        
        draw = ImageDraw.Draw(self.resultImg)
        width, height = self.resultImg.size
        
        # 计算文字位置（底部居中，留出边距）
        margin = 40
        line_spacing = 10
        
        # 获取文字尺寸（bbox方式兼容新旧版本Pillow）
        bbox1 = draw.textbbox((0, 0), text1, font=font)
        bbox2 = draw.textbbox((0, 0), text2, font=font)
        text1_w, text1_h = bbox1[2] - bbox1[0], bbox1[3] - bbox1[1]
        text2_w, text2_h = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
        
        # 计算居中X坐标和底部Y坐标
        x1 = (width - text1_w) // 2
        x2 = (width - text2_w) // 2
        y2 = height - margin - text2_h  # 第二行最底部
        y1 = y2 - line_spacing - text1_h  # 第一行在第二行上方
        
        # 绘制黑色边框（通过偏移绘制实现描边效果）
        offsets = [(-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)]
        
        for dx, dy in offsets:
            draw.text((x1 + dx, y1 + dy), text1, font=font, fill=borderColor)
            draw.text((x2 + dx, y2 + dy), text2, font=font, fill=borderColor)
        
        # 绘制主文字
        draw.text((x1, y1), text1, font=font, fill=textColor)
        draw.text((x2, y2), text2, font=font, fill=textColor)
        

    def drawHeader(self):
        w = 600
        h = 150
        x = (self.resultImg.width - w) // 2
        y = 50
        draw = ImageDraw.Draw(self.resultImg)
        
        corner_radius = h // 2
        rect_box = (x, y, x + w, y + h)
        
        draw.rounded_rectangle(
            rect_box,
            radius=corner_radius,
            fill=(255, 255, 255),
            outline=None
        )
        
        draw.rounded_rectangle(
            rect_box,
            radius=corner_radius,
            fill=None,
            outline=(156, 214, 234),
            width=4
        )
        bgDown = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        drawBgDownDraw = ImageDraw.Draw(bgDown)
        drawBgDownDraw.rounded_rectangle(
            (0, 0, w - 10, h - 10),
            radius=corner_radius,
            fill=(27, 179, 252),
            outline=None
        )
        bgDown = bgDown.crop((0, h // 1.8, w, h))
        self.resultImg.paste(bgDown, (x + 4, int(y + 2 + h // 1.8)), bgDown)

        bgUp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        drawBgUpDraw = ImageDraw.Draw(bgUp)
        drawBgUpDraw.rounded_rectangle(
            (0, 0, w - 12, h - 12),
            radius=corner_radius,
            fill=(0, 0, 0),
            outline=None
        )
        bgUp = bgUp.crop((0, 0, w, h // 1.8))
        self.resultImg.paste(bgUp, (x + 5, y + 8), bgUp)

        text = self.data["username"]
        font_size = 48
        font = ImageFont.truetype("./rizline.ttf", font_size)
        textColor = (255, 255, 255)
        draw.text((x + 160, y + 25), text, font=font, fill=textColor)

        with open("./achievement.txt", "r", encoding="utf-8") as f:
            achievement = f.read()
            achievement = achievement.split("\n")
            bioId1 = self.data["rizcard"]["bioId1"]
            bioId2 = self.data["rizcard"]["bioId2"]
            for i in range(len(achievement)):
                if bioId1 in achievement[i]:
                    text1 = achievement[i].split("=")[1]
                if bioId2 in achievement[i]:
                    text2 = achievement[i].split("=")[1]
            if not text1:
                text1 = "暂无成就"
            if not text2:
                text2 = "暂无成就"
            text1 += " "
            font_size = 28
            font = ImageFont.truetype("./rizline.ttf", font_size)
            textColor = (255, 255, 255)
            # 获取文字尺寸（bbox方式兼容新旧版本Pillow）
            bbox1 = draw.textbbox((0, 0), text1, font=font)
            bbox2 = draw.textbbox((0, 0), text2, font=font)
            text1W = bbox1[2] - bbox1[0]
            text2W = bbox2[2] - bbox2[0]
            draw.text((x + 160, y + 100), text1, font=font, fill=textColor)
            draw.text((x + 160 + text1W, y + 100), text2, font=font, fill=textColor)

    def drawHeadImg(self):
        rizcard = self.data["rizcard"]
        avatarPos = rizcard["avatarPos"]
        avatarId = rizcard["avatarId"]
        borderWidth = 4
        borderColor = (255, 255, 255)
        avatarSize = 142

        for illustration in bgPathList:
            if avatarId in illustration:
                with Image.open(illustration) as headImg:
                    x = avatarPos["x"] * headImg.width - 40
                    y = avatarPos["y"] * headImg.height - 20
                    x1 = x + 0.32 * headImg.width
                    y1 = y + 0.32 * headImg.height
                    headImg = headImg.crop((x, y, x1, y1))
                    
                    headImg = headImg.resize((avatarSize, avatarSize))
                    
                    mask = Image.new('L', (avatarSize, avatarSize), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0, avatarSize-1, avatarSize-1), fill=255)
                    headImg.putalpha(mask)

                    border_img = Image.new('RGBA', (avatarSize, avatarSize), (0,0,0,0))
                    border_draw = ImageDraw.Draw(border_img)
                    border_draw.ellipse(
                        (0, 0, avatarSize-1, avatarSize-1),
                        outline=borderColor,
                        width=borderWidth
                    )
                    headImg.paste(border_img, (0,0), border_img)

                    self.resultImg.paste(headImg, (304, 54), headImg)

    def drawScore(self):
        myBest = self.data["myBest"]
        myBest = sorted(myBest, key=lambda x: x["score"], reverse=True)
        y = 280
        x = 100
        count = 1
        i = 0
        for score in myBest:
            name = score["trackAssetId"].split(".")[1]
            difficultyClassName = score["difficultyClassName"]
            bgFillColor = (255, 255, 255)
            if difficultyClassName == "EZ":
                bgFillColor = (87, 228, 196)
            elif difficultyClassName == "HD":
                bgFillColor = (253, 186, 97)
            elif difficultyClassName == "IN":
                bgFillColor = (254, 134, 97)
            elif difficultyClassName == "AT":
                bgFillColor = (76, 54, 75)
            draw = ImageDraw.Draw(self.resultImg)
            draw.rounded_rectangle(
                (x, y, x + 300, y + 120),
                radius=0,
                fill=bgFillColor,
                outline=None
            )
            for j in range(len(bgPathList)):
                if name in bgPathList[j]:
                    with Image.open(bgPathList[j]) as headImg:
                        headImg = headImg.resize((120, 120))
                        self.resultImg.paste(headImg, (x, y), headImg)
            font_size = 24
            font = ImageFont.truetype("./rizline.ttf", font_size)
            textColor = (255, 255, 255)
            bbox1 = draw.textbbox((0, 0), name, font=font)
            text1W = bbox1[2] - bbox1[0]
            while text1W >= 170:
                font_size -= 1
                font = ImageFont.truetype("./rizline.ttf", font_size)
                bbox1 = draw.textbbox((0, 0), name, font=font)
                text1W = bbox1[2] - bbox1[0]
            draw.text((x + 130, y + 10), name, font=font, fill=textColor)
            font_size = 16
            font = ImageFont.truetype("./rizline.ttf", font_size)
            scoreText = "Score: " + str(score["score"])
            draw.text((x + 130, y + 40), scoreText, font=font, fill=textColor)
            font_size = 12
            font = ImageFont.truetype("./rizline.ttf", font_size)
            completeRate = "Complete Rate: " + str(round(score["completeRate"], 4)) + "%"
            draw.text((x + 130, y + 60), completeRate, font=font, fill=textColor)
            font_size = 16
            font = ImageFont.truetype("./rizline.ttf", font_size)
            isFullCombo = score["isFullCombo"]
            if isFullCombo:
                fullComboText = "是否FC：是"
            else:
                fullComboText = "是否FC：否"
            draw.text((x + 130, y + 80), fullComboText, font=font, fill=textColor)
            isClear = score["isClear"]
            if isClear:
                clearText = "是否通关：是"
            else:
                clearText = "是否通关：否"
            draw.text((x + 130, y + 100), clearText, font=font, fill=textColor)
            x += 350
            count += 1
            i += 1
            if i >= 30:
                break
            if count > 3:
                y += 150
                x = 100
                count = 1

    def drawCoinAndDot(self):
        coin = self.data["coin"]
        dot = self.data["dot"]
        with Image.open("./coin.png") as coinImg:
            with Image.open("./dot.png") as dotImg:
                coinImg = coinImg.resize((25, 25))
                dotImg = dotImg.resize((25, 25))
                tempImg = Image.new("RGBA", (250, 50), (0, 0, 0, 0))
                draw = ImageDraw.Draw(tempImg)
                draw.rounded_rectangle(
                    (0, 0, 250, 50),
                    radius=50,
                    fill=(27, 179, 252),
                    outline=(0, 0, 0),
                    width=4
                )
                font_size = 16
                font = ImageFont.truetype("./rizline.ttf", font_size)
                textColor = (255, 255, 255)
                coinText = "Coin: " + str(coin)
                dotText = "Dot: " + str(dot)
                draw.text((50, 15), coinText, font=font, fill=textColor)
                draw.text((150, 15), dotText, font=font, fill=textColor)
                tempImg.paste(coinImg, (20, 12), coinImg)
                tempImg.paste(dotImg, (120,12), dotImg)
                self.resultImg.paste(tempImg, (self.resultImg.width //2 - tempImg.width // 2, 215), tempImg)



if __name__ == "__main__":
    chartPath = "F:\\rizlineAssetsOutPut\output\chart"
    basePath = "F:\\rizlineAssetsOutPut\output"
    bgPathList = []
    for disc in os.listdir("F:\\rizlineAssetsOutPut\output\charts\\"):
       for chart in os.listdir(os.path.join("F:\\rizlineAssetsOutPut\output\charts\\", disc)):
           for file in os.listdir(os.path.join("F:\\rizlineAssetsOutPut\output\charts\\", disc, chart)):
               if file.endswith(".png"):
                   bgPathList.append(os.path.join("F:\\rizlineAssetsOutPut\output\charts\\", disc, chart, file))

                   
    # 随机选取一张作为背景
    bgPath = random.choice(bgPathList)
    with open("./gameData.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    userD = userGameData(data)
    userD.generateBlurBackground(bgPath)
    userD.drawVersion()
    userD.drawHeader()
    userD.drawHeadImg()
    userD.drawScore()
    userD.drawCoinAndDot()
    userD.resultImg.save("result.png")