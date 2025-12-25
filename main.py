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
from threading import Thread

# --- ⚙️ 설정값 (코이업 환경변수 사용) ---
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# 서버 및 채널 설정 (본인 서버에 맞게 수정됨)
GUILD_ID = 822373181104717836  
AUTH_ROLE_ID = 1453415633453711391  

LOG_CHANNEL_ID = 1453577924228681812         
RESTORE_LOG_CHANNEL_ID = 1453584405883916288 
AUTH_NOTI_CHANNEL_ID = 1453587569395896439   

EMBED_COLOR = 0xc4edc6 
TURTLE_LOGO_URL = "https://media.discordapp.net/attachments/1453577924228681812/1453591053755088946/unnamed_3.jpg?ex=694e01a9&is=694cb029&hm=f8dbff699dd9250df7bca8938f0ebc44a58e4739400eefc213bd416e2c7d826b&=&format=webp&width=876&height=876"

# 코이업 주소 자동 적용
BASE_URL = "https://coastal-morganica-fluare-c4dd0c04.koyeb.app" 
REDIRECT_URI = f"{BASE_URL}/callback"
AUTH_URL = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI.replace(':', '%3A').replace('/', '%2F')}&response_type=code&scope=identify%20guilds.join"

RANDOM_NAMES = ["키타가와", "서야", "human", "MJE", "NORI", "PIANOKED", "QQ", "seori", "겨울", "And", "누콩", "채훈", "맹", "사용자", "손뿜", "슘", "시은", "아람", "아코", "Vibe", "Mood", "Chill", "Zero", "Ace", "Max", "Leo", "Kai", "Finn", "Noah"]

app = FastAPI()
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# --- [1] 웹 서버 (인증 완료 처리) ---
@app.get("/callback", response_class=HTMLResponse)
async def callback(code: str):
    data = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'grant_type': 'authorization_code', 'code': code, 'redirect_uri': REDIRECT_URI}
    res = requests.post("https://discord.com/api/oauth2/token", data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    token_json = res.json()
    access_token = token_json.get("access_token")
    if not access_token: return "<html><body><h2>Auth Failed</h2></body></html>"

    user_info = requests.get("https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"}).json()
    user_id, user_name = user_info.get("id"), user_info.get("username")
    
    with open("users.txt", "a", encoding="utf-8") as f: f.write(f"{user_id}:{access_token}\n")
    requests.put(f"https://discord.com/api/guilds/{GUILD_ID}/members/{user_id}/roles/{AUTH_ROLE_ID}", headers={"Authorization": f"Bot {BOT_TOKEN}"})

    noti_channel = bot.get_channel(AUTH_NOTI_CHANNEL_ID)
    if noti_channel:
        embed = discord.Embed(title="✨ BARR!ER SHOP 인증 완료", description=f"**{user_name}** 님이 인증되었습니다.\nVerified successfully.", color=EMBED_COLOR)
        bot.loop.create_task(noti_channel.send(embed=embed))

    return f"<html><body style='text-align:center; padding-top:50px;'><h1>✅ 인증 완료! (Verification Complete)</h1><p>{user_name}, thank you!</p></body></html>"

# --- [2] 슬래시 명령어 ---
@bot.tree.command(name="인증", description="✅ 인증 메시지 게시 (Post Auth Message)")
async def post_auth(interaction: discord.Interaction):
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

@bot.tree.command(name="이름바꾸기", description="⚙️ 랜덤 이름 변경 및 로그 기록")
async def rename(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.send_message("⚙️ 이름 변경 시작...", ephemeral=True)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    success = 0
    for m in role.members:
        old_nick = m.display_name
        new_nick = random.choice(RANDOM_NAMES)
        try:
            await m.edit(nick=new_nick)
            success += 1
            if log_channel:
                embed = discord.Embed(title="📝 이름 변경 로그", description=f"**{old_nick}** -> **{new_nick}**", color=EMBED_COLOR)
                await log_channel.send(embed=embed)
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
                res = requests.put(f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{u_id}", headers={"Authorization": f"Bot {BOT_TOKEN}"}, json={"access_token": token})
                if res.status_code in [201, 204]: success += 1
                await asyncio.sleep(1.0)
    except: pass
    await interaction.followup.send(f"🏆 총 {success}명 복구 완료", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ 온라인: {bot.user}")

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    if not os.path.exists("users.txt"): open("users.txt", "w").close()
    Thread(target=run_api, daemon=True).start()
    bot.run(BOT_TOKEN)
