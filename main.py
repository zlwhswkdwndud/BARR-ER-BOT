import discord
from discord import app_commands
from discord.ext import commands
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import random
import asyncio
import uvicorn
import os
import sys
from threading import Thread

# --- ⚙️ 설정값 ---
CLIENT_ID = "1453416850393403394"
CLIENT_SECRET = "SSxPzE-8qT7-ziIZJsG1kvsschDBCga8"
BOT_TOKEN = "MTQ1MzQxNjg1MDM5MzQwMzM5NA.GExDHx.iMsOn6gbUz_6BtBG4keIro02N2trzExsYYDK3o"
GUILD_ID = 822373181104717836  
AUTH_ROLE_ID = 1453415633453711391  

LOG_CHANNEL_ID = 1453577924228681812         
RESTORE_LOG_CHANNEL_ID = 1453584405883916288 
AUTH_NOTI_CHANNEL_ID = 1453587569395896439   

EMBED_COLOR = 0xc4edc6 
TURTLE_LOGO_URL = "https://media.discordapp.net/attachments/1453577924228681812/1453591053755088946/unnamed_3.jpg?ex=694e01a9&is=694cb029&hm=f8dbff699dd9250df7bca8938f0ebc44a58e4739400eefc213bd416e2c7d826b&=&format=webp&width=876&height=876"

# ⚠️ 코이업 주소가 생성되면 아래를 수정하세요
BASE_URL = "여기에_코이업_주소를_넣으세요" 
REDIRECT_URI = f"{BASE_URL}/callback"
AUTH_URL = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI.replace(':', '%3A').replace('/', '%2F')}&response_type=code&scope=identify%20guilds.join"

RANDOM_NAMES = ["키타가와", "서야", "human", "MJE", "NORI", "PIANOKED", "QQ", "seori", "겨울", "And", "누콩", "채훈", "맹", "사용자", "손뿜", "슘", "시은", "아람", "아코", "밥도영", "MungChi", "CJB", "S2S2", "백지", "설담", "죠스바", "킹콩", "팝", "푸라", "리하", "유솜", "무결", "희수", "연우", "시호", "지안", "태하", "연호", "차윤", "휘수", "도건", "유현", "신야", "류제", "은우", "하늘", "시온", "백야", "재현", "하윤", "채운", "서하", "도하", "유진", "승우", "지호", "민준", "예준", "태성", "윤슬", "가온", "로하", "시안", "은율", "루안", "하람", "도윤", "서준", "리안", "서훤", "다온", "이엘", "하진", "선우", "주원", "예찬", "강휘", "서우", "해온", "지유", "나래", "로아", "수아", "유나", "시아", "윤아", "민서", "서연", "채원", "예린", "노아", "리쿠", "하루", "유우", "세나", "카이", "레이", "레온", "아서", "제이드", "Vibe", "Mood", "Chill", "Zero", "One", "Ace", "Max", "Leo", "Kai", "Finn", "Noah", "Liam", "Alex", "Sam", "Ryan", "Hugo", "Arlo", "Ezra", "Milo", "Nova", "포근", "여운", "잔향", "공명", "선율", "궤적", "파동", "잔상", "파편", "망각", "새벽", "노을", "바다", "파도", "안개", "이슬", "서리", "구름", "별빛", "햇살", "바람", "유성", "은하", "우주", "궤도", "심해", "신기루", "보라", "진주", "수정", "유리", "강철", "백은", "청동", "무심", "여유", "몽상", "환상", "진실", "비밀", "인연", "약속", "흔적", "낙원", "심연", "천상", "공허", "영원", "찰나", "순간", "리하린", "서이안", "윤하준", "차예원", "신태양", "백설아", "임재희", "송민서", "최준호", "정나은", "지안우", "태하린", "연호진", "차윤하", "휘수안", "도건우", "유현서", "신야결", "류제이", "은우진", "하늘샘", "바다별", "구름꽃", "안개비", "저녁해", "아침놀", "새벽달", "보름달", "초승달", "파랑새", "은휘", "도결", "리안", "서훤", "윤슬", "지안", "태하", "연우", "시온", "무겸", "이프", "뮤즈", "루나", "벨라", "시아", "유이", "다인", "서호", "준우", "이든"]

app = FastAPI()
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# --- [1] 웹 서버 ---
@app.get("/callback", response_class=HTMLResponse)
async def callback(code: str):
    data = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'grant_type': 'authorization_code', 'code': code, 'redirect_uri': REDIRECT_URI}
    res = requests.post("https://discord.com/api/oauth2/token", data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    token_json = res.json()
    access_token = token_json.get("access_token")
    if not access_token: return "<html><body><h2>인증 실패 (Auth Failed)</h2></body></html>"

    user_info = requests.get("https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"}).json()
    user_id, user_name = user_info.get("id"), user_info.get("username")
    
    with open("users.txt", "a", encoding="utf-8") as f: f.write(f"{user_id}:{access_token}\n")
    requests.put(f"https://discord.com/api/guilds/{GUILD_ID}/members/{user_id}/roles/{AUTH_ROLE_ID}", headers={"Authorization": f"Bot {BOT_TOKEN}"})

    noti_channel = bot.get_channel(AUTH_NOTI_CHANNEL_ID)
    if noti_channel:
        embed = discord.Embed(title="✨ BARR!ER SHOP 인증 완료", description=f"**{user_name}** 님이 인증되었습니다.", color=EMBED_COLOR)
        bot.loop.create_task(noti_channel.send(embed=embed))

    return f"<html><body style='text-align:center; padding-top:50px;'><h1>✅ 인증 완료! (Verification Complete)</h1><p>{user_name}, thank you!</p></body></html>"

# --- [2] 슬래시 명령어 ---
@bot.tree.command(name="인증", description="✅ 인증 메시지 게시 (Post Auth Message)")
async def post_auth(interaction: discord.Interaction):
    # 영문 문구 추가 (English description added)
    embed = discord.Embed(
        title="✅ BARR!ER SHOP 인증하기", 
        description=(
            "다른 채널을 보려면 아래 **인증하기** 버튼을 눌러 계정을 인증해주세요.\n\n"
            "Please click the **Verify** button below to authorize your account and access other channels."
        ), 
        color=EMBED_COLOR
    )
    embed.set_thumbnail(url=TURTLE_LOGO_URL)
    view = discord.ui.View(timeout=None)
    view.add_item(discord.ui.Button(label="인증하기 (Verify)", style=discord.ButtonStyle.link, url=AUTH_URL))
    
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("게시 완료. (Posted)", ephemeral=True)

@bot.tree.command(name="역할지급", description="🚀 모든 멤버에게 역할 지급")
async def give_role(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.send_message(f"⚙️ {role.name} 지급 시작...", ephemeral=True)
    success = 0
    async for member in interaction.guild.fetch_members(limit=None):
        if not member.bot and role not in member.roles:
            try:
                await member.add_roles(role)
                success += 1
                await asyncio.sleep(0.4)
            except: continue
    await interaction.followup.send(f"🏆 {success}명 지급 완료", ephemeral=True)

@bot.tree.command(name="이름바꾸기", description="⚙️ 랜덤 이름 변경")
async def rename(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.send_message("⚙️ 이름 변경 시작...", ephemeral=True)
    success = 0
    for m in role.members:
        try:
            await m.edit(nick=random.choice(RANDOM_NAMES))
            success += 1
            await asyncio.sleep(1.5)
        except: continue
    await interaction.followup.send(f"🏆 {success}명 변경 완료", ephemeral=True)

@bot.tree.command(name="복구하기", description="🛠️ 모아둔 토큰으로 유저 복구")
async def restore(interaction: discord.Interaction):
    await interaction.response.send_message("🔓 복구 작업을 시작합니다...", ephemeral=True)
    success = 0
    try:
        with open("users.txt", "r") as f:
            for line in f:
                u_id, token = line.strip().split(":")
                res = requests.put(
                    f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{u_id}", 
                    headers={"Authorization": f"Bot {BOT_TOKEN}"}, 
                    json={"access_token": token}
                )
                if res.status_code in [201, 204]: success += 1
                await asyncio.sleep(1.0)
    except Exception as e:
        print(f"복구 에러: {e}")
    await interaction.followup.send(f"🏆 총 {success}명 복구 완료", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ 통합 봇 온라인: {bot.user}")

# --- [3] 코이업 실행부 ---
def run_api():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    if not os.path.exists("users.txt"): open("users.txt", "w").close()
    Thread(target=run_api, daemon=True).start()
    bot.run(BOT_TOKEN)