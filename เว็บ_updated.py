import discord
from discord import app_commands
from discord.ext import commands
from fastapi import FastAPI, Request, Form, Response, Cookie, WebSocket, WebSocketDisconnect, BackgroundTasks, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional
import urllib.parse
import hashlib

# 🖼️ ตั้งค่าโลโก้ระบบ (ใส่ลิงก์ URL รูปภาพจากอินเทอร์เน็ตได้ที่นี่)
LOGO_URL = "https://upload.wikimedia.org/wikipedia/th/8/89/Bunditpatanasilpa_Institute_Logo.png"

TEACHER_DEFAULT_AVATAR = "data:image/jpeg;base64,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"
import httpx
import collections

# ==========================================
# 🌐 CONFIGURATION & DISCORD BOT SETUP
# ==========================================
app = FastAPI()
SYSTEM_LOGS = collections.deque(maxlen=100)

# 🖼️ โฟลเดอร์เก็บรูปโปรไฟล์นักเรียน (อัปโหลดโดยแอดมิน/หัวหน้าระดับ/ฝ่ายกิจการ เท่านั้น)
PROFILE_PHOTO_DIR = os.path.join("static", "profiles")
os.makedirs(PROFILE_PHOTO_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
ALLOWED_PHOTO_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_PHOTO_SIZE_BYTES = 3 * 1024 * 1024  # 3MB

def add_log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    SYSTEM_LOGS.appendleft(f"[{timestamp}] {msg}")

add_log("ระบบ K-School Enterprise เริ่มต้นการทำงาน")
SECRET_WEB_TOKEN = "0eff3ca11601bbea28c703f2e9b9b7db" 

SERVER_START_TIME = datetime.now()  # ⏱️ ใช้คำนวณ Uptime ในหน้า System Status

TXT_DATABASE_PATH = "students_master.txt" 

ADMIN_USER = "Admincda"
ADMIN_PASS = "Nammon29"

COOKIE_MAX_AGE = 2592000 

class AttendanceBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="?", intents=intents)

    async def setup_hook(self):
        try:
            await self.tree.sync()
            print("⚡ [DISCORD BOT] Synced Command Tree")
        except Exception as e:
            print(f"❌ [DISCORD BOT] Sync Tree Error: {e}")

bot = AttendanceBot()

async def send_discord_log(title: str, description: str, color: discord.Color):
    sent_flag = False
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                try:
                    embed = discord.Embed(title=title, description=description, color=color)
                    await channel.send(embed=embed)
                    sent_flag = True
                    break 
                except Exception as e:
                    print(f"❌ Cannot send to {channel.name}: {e}")
        if sent_flag:
            return True
    return False

@bot.event
async def on_ready():
    print(f'⚡ [DISCORD BOT] ทำงานปกติ เข้าสู่ระบบในชื่อ {bot.user}')

# ==========================================
# 🎛️ DISCORD SLASH COMMAND /admin — MAINTENANCE CONTROL
# ==========================================

# Modal ขอรหัสผ่าน + เลือก mode (ใช้สำหรับทั้งเปิดและปิดเว็บ)
class MaintenanceModeModal(discord.ui.Modal):
    def __init__(self, action: str, mode_type: str, label: str):
        super().__init__(title=f"🔐 ยืนยันรหัส Admin — {label}")
        self.action = action        # "on" หรือ "off"
        self.mode_type = mode_type  # "off" / "maintenance" / "updating" / ...

        self.password_input = discord.ui.TextInput(
            label="รหัสผ่าน Admin",
            placeholder="กรอกรหัสเจ้าของเว็บ",
            style=discord.TextStyle.short,
            required=True,
            min_length=1,
            max_length=50
        )
        self.add_item(self.password_input)

    async def on_submit(self, interaction: discord.Interaction):
        if self.password_input.value != ADMIN_PASS:
            await interaction.response.send_message("❌ รหัสผ่านไม่ถูกต้อง! ปฏิเสธการเข้าถึง", ephemeral=True)
            return

        is_active = 0 if self.mode_type == "off" else 1

        # อัปเดต DB โดยตรง (ไม่ต้องผ่าน HTTP เพราะอยู่ใน process เดียวกัน)
        try:
            conn = sqlite3.connect('attendance_pro.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE maintenance_settings SET is_active = ?, mode_type = ? WHERE id = 1", (is_active, self.mode_type))
            conn.commit()
            conn.close()
            add_log(f"เปลี่ยนสถานะเว็บไซต์เป็น: {self.mode_type} (โดย Discord)")
        except Exception as e:
            await interaction.response.send_message(f"❌ เกิดข้อผิดพลาด DB: {e}", ephemeral=True)
            return

        # Broadcast WebSocket ให้หน้าเว็บทุก client เปลี่ยนสถานะทันที
        try:
            conn_manager = interaction.client._connection  # ใช้ manager จาก global
            await manager.broadcast("STATUS_CHANGED")
        except Exception: pass

        mode_labels = {
            "off": "🟢 เปิดเว็บออนไลน์ปกติ",
            "maintenance": "🏗️ กำลังแก้ไขเว็บไซต์",
            "updating": "🚀 กำลังอัปเดตระบบ",
            "testing": "🧪 กำลังทดสอบระบบ (BETA)",
            "disabled": "🔒 ปิดระบบชั่วคราว",
            "ip_error": "🚫 ERROR 404 — IP Unassigned"
        }
        result_label = mode_labels.get(self.mode_type, self.mode_type)

        embed = discord.Embed(
            title="✅ อัปเดตสถานะเว็บสำเร็จ",
            description=f"**สถานะใหม่:** {result_label}\n**ดำเนินการโดย:** {interaction.user.mention}",
            color=discord.Color.green() if self.mode_type == "off" else discord.Color.red()
        )
        embed.set_footer(text="K-School Platform | KK Studio Group")
        await interaction.response.send_message(embed=embed)


# View ปุ่มควบคุม Maintenance (ปุ่มเปิด + ปุ่มปิดแต่ละโหมด)
class AdminControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="✅ เปิดเว็บปกติ", style=discord.ButtonStyle.success, row=0)
    async def btn_open(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MaintenanceModeModal("off", "off", "เปิดเว็บปกติ"))

    @discord.ui.button(label="🏗️ กำลังแก้ไขเว็บ", style=discord.ButtonStyle.danger, row=0)
    async def btn_maintenance(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MaintenanceModeModal("on", "maintenance", "กำลังแก้ไขเว็บ"))

    @discord.ui.button(label="🚀 กำลังอัปเดต", style=discord.ButtonStyle.danger, row=1)
    async def btn_updating(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MaintenanceModeModal("on", "updating", "กำลังอัปเดตระบบ"))

    @discord.ui.button(label="🧪 กำลังทดสอบ", style=discord.ButtonStyle.secondary, row=1)
    async def btn_testing(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MaintenanceModeModal("on", "testing", "ทดสอบระบบ BETA"))

    @discord.ui.button(label="🔒 ปิดชั่วคราว", style=discord.ButtonStyle.danger, row=2)
    async def btn_disabled(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MaintenanceModeModal("on", "disabled", "ปิดระบบชั่วคราว"))

    @discord.ui.button(label="🚫 IP Error 404", style=discord.ButtonStyle.danger, row=2)
    async def btn_ip_error(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MaintenanceModeModal("on", "ip_error", "ERROR 404 IP Unassigned"))


@bot.tree.command(name="admin", description="🛡️ ควบคุมสถานะเว็บ K-School (เจ้าของเว็บเท่านั้น)")
async def slash_admin(interaction: discord.Interaction):
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT is_active, mode_type FROM maintenance_settings WHERE id = 1")
    res = cursor.fetchone()
    conn.close()
    
    is_active = res[0] if res else 0
    mode_type = res[1] if res else "off"
    
    mode_labels = {
        "off": "🟢 เปิดออนไลน์ปกติ",
        "maintenance": "🏗️ กำลังแก้ไขเว็บไซต์",
        "updating": "🚀 กำลังอัปเดตระบบ",
        "testing": "🧪 กำลังทดสอบ (BETA)",
        "disabled": "🔒 ปิดชั่วคราว",
        "ip_error": "🚫 ERROR 404 — IP Unassigned"
    }
    current_label = mode_labels.get(mode_type, mode_type)

    embed = discord.Embed(
        title="🛡️ K-School — แผงบริหารจัดการระบบ (Administrative Console)",
        description=(
            f"**สถานะปัจจุบัน:** {current_label}\n\n"
            "กดปุ่มด้านล่างเพื่อเปลี่ยนสถานะเว็บ\n"
            "⚠️ ระบบจะขอรหัส Admin ก่อนดำเนินการทุกครั้ง"
        ),
        color=discord.Color.green() if is_active == 0 else discord.Color.red()
    )
    embed.set_footer(text="K-School Platform | KK Studio Group")
    await interaction.response.send_message(embed=embed, view=AdminControlView(), ephemeral=True)

# ==========================================
# 🔌 WEBSOCKETS REAL-TIME MANAGER (ระบบตอบสนองแบบเรียลไทม์)
# ==========================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/ws/maintenance")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/notify")
async def websocket_notify_endpoint(websocket: WebSocket):
    """🔔 ช่องทางแจ้งเตือนเรียลไทม์ทั่วไป (ใช้ manager ตัวเดียวกับ /ws/maintenance)
    ทุกอีเวนต์ที่เกี่ยวกับนักเรียน/ครู (หักคะแนน คืนคะแนน ฯลฯ) จะยิงผ่านช่องนี้
    ฝั่ง client จะกรองด้วยฟิลด์ type/target_uid/target_user เอง จึงเชื่อมสาย /ws/maintenance หรือ /ws/notify ก็ได้ผลเหมือนกัน"""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ==========================================
# 🎨 PREMIUM UI STYLE WITH LIVE WEBSOCKET SCRIPT
# ==========================================
STYLE_HEADER = """
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>K-School Platform | KK Studio Group</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sarabun:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --navy-900: #020617;
            --navy-800: #0f172a;
            --navy-700: #1e293b;
            --navy-600: #1e40af;
            --gold: #d4af37;
            --gold-light: #f2d879;
            --surface: #ffffff;
            --surface-muted: #f7f9fc;
            --border: #e6eaf1;
            --text: #0f172a;
            --text-soft: #64748b;
            --shadow-sm: 0 1px 2px rgba(15,23,42,0.04), 0 1px 3px rgba(15,23,42,0.06);
            --shadow-md: 0 6px 16px -4px rgba(15,23,42,0.10), 0 3px 6px -3px rgba(15,23,42,0.06);
            --shadow-lg: 0 20px 40px -12px rgba(15,23,42,0.18);
            --radius: 16px;
        }

        * { box-sizing: border-box; }

        body {
            font-family: 'Inter', 'Sarabun', sans-serif;
            background:
                radial-gradient(1200px 500px at 100% -10%, rgba(30,58,138,0.06), transparent),
                radial-gradient(900px 400px at -10% 0%, rgba(212,175,55,0.05), transparent),
                var(--surface-muted);
            color: var(--text);
            margin: 0; padding: 0;
            -webkit-tap-highlight-color: transparent;
            letter-spacing: 0.1px;
        }

        /* ─── NAVBAR ─── */
        .navbar {
            background: linear-gradient(120deg, var(--navy-900), var(--navy-700) 60%, #16213e);
            color: white; padding: 14px 24px;
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.18);
            border-bottom: 3px solid var(--gold);
            position: sticky; top: 0; z-index: 40;
        }
        .navbar h1 {
            margin: 0; font-size: 17.5px; font-weight: 700; letter-spacing: 0.3px;
            color: #f8fafc; display: flex; align-items: center; gap: 10px;
        }
        .nav-logo { height: 34px; width: auto; object-fit: contain; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.35)); }

        /* ─── APP HEADER ─── */
        .app-header {
            background: linear-gradient(150deg, var(--navy-600), var(--navy-900) 70%);
            color: white; padding: 34px 20px 30px; text-align: center;
            box-shadow: 0 8px 24px rgba(15,23,42,0.18);
            border-bottom: 3px solid var(--gold);
            position: relative; overflow: hidden;
        }
        .app-header::before {
            content: ""; position: absolute; inset: 0;
            background: radial-gradient(500px 200px at 50% -40%, rgba(212,175,55,0.25), transparent 70%);
            pointer-events: none;
        }
        .header-logo { height: 78px; width: auto; margin-bottom: 14px; filter: drop-shadow(0 6px 12px rgba(0,0,0,0.35)); position: relative; }
        .app-header h1 { margin: 0; font-size: 21px; font-weight: 800; letter-spacing: 0.8px; text-shadow: 0 2px 6px rgba(0,0,0,0.25); position: relative; }
        .app-header p { margin: 7px 0 0 0; font-size: 13px; color: #bcd2fb; font-weight: 500; position: relative; }

        .main-container { padding: 22px 16px 40px; max-width: 650px; margin: 0 auto; box-sizing: border-box; }

        /* ─── CARDS ─── */
        .card {
            background: var(--surface); border-radius: var(--radius); padding: 24px;
            box-shadow: var(--shadow-sm); margin-bottom: 22px;
            border: 1px solid var(--border);
            transition: box-shadow 0.25s ease, transform 0.25s ease;
        }
        .card h2 {
            margin-top: 0; font-size: 15.5px; color: var(--navy-800); font-weight: 700;
            border-bottom: 2px solid var(--surface-muted); padding-bottom: 13px; margin-bottom: 18px;
            display: flex; align-items: center; gap: 8px;
        }

        /* ─── MENU GRID ─── */
        .menu-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-bottom: 24px; }
        .menu-btn {
            background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
            padding: 22px 12px; text-align: center; text-decoration: none; color: var(--navy-800);
            box-shadow: var(--shadow-sm);
            display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 9px;
            transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
            border-bottom: 3px solid var(--border);
        }
        .menu-btn:active { transform: translateY(2px) scale(0.98); border-bottom-width: 1px; background-color: var(--surface-muted); }
        @media (hover: hover) {
            .menu-btn:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); border-color: var(--gold); }
        }
        .menu-btn .icon { font-size: 27px; filter: drop-shadow(0 2px 3px rgba(0,0,0,0.08)); }
        .menu-btn .title { font-size: 13.5px; font-weight: 700; color: var(--navy-700); }

        /* ─── TABLE ─── */
        table { width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 10px; background: var(--surface); border-radius: 12px; overflow: hidden; box-shadow: var(--shadow-sm); }
        th, td { padding: 13px 10px; text-align: center; border-bottom: 1px solid var(--border); font-size: 13.5px; }
        th { background: linear-gradient(180deg, #f8fafc, #eef2f8); color: var(--navy-700); font-weight: 700; letter-spacing: 0.2px; }
        tbody tr:nth-child(even) { background: #fbfcfe; }
        tbody tr:last-child td { border-bottom: none; }
        @media (hover: hover) {
            tbody tr:hover td { background: rgba(30,58,138,0.035); }
        }

        /* ─── BUTTONS ─── */
        .btn {
            padding: 9px 15px; font-size: 13px; font-weight: 700; border: none; border-radius: 8px;
            cursor: pointer; text-decoration: none; display: inline-block; text-align: center;
            transition: filter 0.15s ease, transform 0.15s ease; box-shadow: var(--shadow-sm);
        }
        .btn:active { transform: translateY(1px); }
        @media (hover: hover) { .btn:hover { filter: brightness(1.07); } }
        .btn-submit {
            background: linear-gradient(135deg, var(--navy-600), var(--navy-900));
            color: white; width: 100%; padding: 15px; font-size: 15px; margin-top: 5px;
            box-sizing: border-box; font-weight: 700; border-radius: 10px; border: none; cursor: pointer;
            border-bottom: 3px solid var(--navy-900); box-shadow: 0 6px 16px -4px rgba(30,58,138,0.35);
            letter-spacing: 0.3px;
        }
        .btn-submit:active { transform: translateY(2px); border-bottom-width: 1px; box-shadow: 0 2px 6px rgba(30,58,138,0.25); }
        @media (hover: hover) { .btn-submit:hover { filter: brightness(1.08); } }
        .btn-danger { background: linear-gradient(135deg, #ef4444, #dc2626); color: white; }
        .btn-warning { background: linear-gradient(135deg, #f59e0b, #d97706); color: white; }
        .btn-secondary { background: linear-gradient(135deg, #64748b, #475569); color: white; }

        /* ─── FORM CONTROLS ─── */
        input[type="text"], input[type="password"], input[type="date"], select {
            width: 100%; padding: 12.5px 14px; border: 1.5px solid var(--border); border-radius: 10px;
            box-sizing: border-box; margin-bottom: 14px; font-family: 'Inter', 'Sarabun', sans-serif;
            font-size: 14px; background-color: #fff; color: var(--navy-800);
            transition: border-color 0.18s ease, box-shadow 0.18s ease;
        }
        input[type="text"]:focus, input[type="password"]:focus, input[type="date"]:focus, select:focus {
            outline: none; border-color: var(--navy-600); box-shadow: 0 0 0 4px rgba(30,58,138,0.12);
        }

        .checkbox-container { display: flex; align-items: center; gap: 12px; padding: 12px 10px; border-bottom: 1px solid var(--border); text-align: left; }
        .checkbox-container input[type="checkbox"] { display: block; width: 18px; height: 18px; margin: 0; cursor: pointer; accent-color: var(--navy-600); }
        .badge {
            background: linear-gradient(135deg, #ecfdf5, #f0fdf4); color: #166534; padding: 3px 9px;
            border-radius: 20px; font-size: 11.5px; font-weight: 700; border: 1px solid #bbf7d0;
        }

        /* ─── STATUS SELECTOR ─── */
        .status-group { display: flex; gap: 4px; border: 1px solid var(--border); padding: 3px; border-radius: 12px; background-color: var(--surface-muted); }
        .status-label { flex: 1; text-align: center; font-size: 12.5px; font-weight: 700; padding: 9px 12px; border-radius: 9px; cursor: pointer; transition: all 0.15s; color: var(--text-soft); border: 1px solid transparent; }
        .status-group input[type="radio"] { display: none; }

        .status-group input[type="radio"][value="มา"]:checked + .status-label { background: linear-gradient(135deg, #10b981, #059669); color: white; box-shadow: 0 3px 8px rgba(16,185,129,0.35); }
        .status-group input[type="radio"][value="สาย"]:checked + .status-label { background: linear-gradient(135deg, #f59e0b, #d97706); color: white; box-shadow: 0 3px 8px rgba(245,158,11,0.35); }
        .status-group input[type="radio"][value="ลา"]:checked + .status-label { background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; box-shadow: 0 3px 8px rgba(59,130,246,0.35); }
        .status-group input[type="radio"][value="ขาด"]:checked + .status-label { background: linear-gradient(135deg, #ef4444, #dc2626); color: white; box-shadow: 0 3px 8px rgba(239,68,68,0.35); }

        /* ─── CUSTOM ALERT UI ─── */
        .smart-alert-overlay { position: fixed; inset: 0; background: rgba(11,17,32,0.65); backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; z-index: 9999; opacity: 0; visibility: hidden; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
        .smart-alert-overlay.active { opacity: 1; visibility: visible; }
        .smart-alert-card { background: var(--surface); width: 90%; max-width: 400px; border-radius: 22px; padding: 34px 26px; text-align: center; box-shadow: var(--shadow-lg); transform: scale(0.9); transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); border: 1px solid var(--border); }
        .smart-alert-overlay.active .smart-alert-card { transform: scale(1); }
        .smart-alert-icon { width: 66px; height: 66px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; margin: 0 auto 20px; box-shadow: inset 0 0 0 1px rgba(0,0,0,0.03); }
        .smart-alert-title { font-size: 20px; font-weight: 800; color: var(--navy-800); margin-bottom: 8px; }
        .smart-alert-msg { font-size: 14.5px; color: var(--text-soft); line-height: 1.65; margin-bottom: 24px; }
        .smart-alert-btn { background: linear-gradient(135deg, var(--navy-600), var(--navy-900)); color: white; border: none; padding: 12px 34px; border-radius: 12px; font-weight: 700; font-size: 15px; cursor: pointer; transition: all 0.2s; box-shadow: 0 6px 14px rgba(30, 58, 138, 0.28); }
        .smart-alert-btn:active { transform: translateY(2px); box-shadow: none; }

        /* Alert Types */
        .alert-success .smart-alert-icon { background: #f0fdf4; color: #10b981; }
        .alert-error .smart-alert-icon { background: #fef2f2; color: #ef4444; }
        .alert-warning .smart-alert-icon { background: #fffbeb; color: #f59e0b; }
        .alert-info .smart-alert-icon { background: #eff6ff; color: #3b82f6; }

        /* ─── SCREEN LOCK OVERLAY ─── */
        body.screen-locked { pointer-events: none; user-select: none; }
        body.screen-locked #screenlock-overlay { pointer-events: all; }

        #screenlock-overlay {
            display: none;
            position: fixed;
            inset: 0;
            z-index: 99999;
            background: rgba(11,17,32,0.96);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }
        #screenlock-overlay.active { display: flex; }
        #screenlock-box {
            background: var(--surface);
            border-radius: 22px;
            padding: 38px 28px;
            width: 90%;
            max-width: 360px;
            text-align: center;
            box-shadow: 0 30px 60px rgba(0,0,0,0.55);
            animation: lockPop 0.35s cubic-bezier(0.34,1.56,0.64,1);
            pointer-events: all;
            border: 1px solid rgba(212,175,55,0.25);
        }
        @keyframes lockPop { from { transform: scale(0.85); opacity: 0; } to { transform: scale(1); opacity: 1; } }
        #screenlock-box .lock-icon { font-size: 52px; margin-bottom: 12px; }
        #screenlock-box h2 { margin: 0 0 4px; font-size: 20px; font-weight: 800; color: var(--navy-800); }
        #screenlock-box p { margin: 0 0 20px; font-size: 13.5px; color: var(--text-soft); }
        #screenlock-input {
            width: 100%;
            padding: 13px;
            border: 2px solid var(--border);
            border-radius: 12px;
            font-size: 16px;
            font-family: 'Inter', 'Sarabun', sans-serif;
            box-sizing: border-box;
            margin-bottom: 14px;
            text-align: center;
            letter-spacing: 3px;
            transition: border 0.2s, box-shadow 0.2s;
            pointer-events: all;
            user-select: text;
        }
        #screenlock-input:focus { outline: none; border-color: var(--navy-600); box-shadow: 0 0 0 4px rgba(30,58,138,0.15); }
        #screenlock-input.shake {
            animation: shake 0.4s ease;
            border-color: #ef4444;
        }
        @keyframes shake {
            0%,100% { transform: translateX(0); }
            20% { transform: translateX(-8px); }
            40% { transform: translateX(8px); }
            60% { transform: translateX(-6px); }
            80% { transform: translateX(6px); }
        }
        #screenlock-btn {
            width: 100%;
            padding: 13px;
            background: linear-gradient(135deg, var(--navy-600), var(--navy-900));
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 700;
            font-family: 'Inter', 'Sarabun', sans-serif;
            cursor: pointer;
            border-bottom: 3px solid var(--navy-900);
            pointer-events: all;
            box-shadow: 0 6px 16px -4px rgba(30,58,138,0.35);
        }
        #screenlock-btn:active { transform: translateY(2px); border-bottom-width: 1px; }
        #screenlock-error { color: #ef4444; font-size: 13px; margin-top: 10px; min-height: 18px; font-weight: 600; }
        #btn-lock-screen {
            background: linear-gradient(135deg, #1e293b, #0f172a);
            color: var(--gold-light);
            border: none;
            border-radius: 8px;
            padding: 7px 14px;
            font-size: 13px;
            font-weight: 700;
            font-family: 'Inter', 'Sarabun', sans-serif;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            border-bottom: 2px solid #0f172a;
            transition: filter 0.2s;
        }
        #btn-lock-screen:active { transform: translateY(1px); border-bottom-width: 1px; }
        @keyframes toastIn { from { opacity:0; transform:translateX(-50%) translateY(12px); } to { opacity:1; transform:translateX(-50%) translateY(0); } }

        /* ─── SCROLLBAR POLISH (desktop) ─── */
        ::-webkit-scrollbar { width: 10px; height: 10px; }
        ::-webkit-scrollbar-track { background: var(--surface-muted); }
        ::-webkit-scrollbar-thumb { background: #c7d0dd; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #aab4c4; }

        /* ============================================================
           🎨 DASHBOARD SKIN — ปรับหน้าเดิมทั้งระบบให้เป็นสไตล์แดชบอร์ดเดียวกัน
           (override ชุดสีเก่า; หน้าที่ใช้ dk-/ah- มีสไตล์ของตัวเองอยู่แล้ว)
        ============================================================ */
        body { background: #f0f4f8; font-family: 'Sarabun', 'Inter', sans-serif; }

        .navbar {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 60%, #1d4ed8 100%);
            border-bottom: none; padding: calc(env(safe-area-inset-top, 0px) + 13px) 18px 13px;
            box-shadow: 0 6px 20px -8px rgba(15,23,42,0.45);
        }
        .navbar h1 { font-size: 17px; font-weight: 800; }
        .navbar .btn-secondary, .navbar .btn {
            background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.25);
            box-shadow: none; color: #fff; border-radius: 10px; padding: 8px 13px; font-size: 12.5px;
        }
        .main-container { max-width: 900px; padding: 18px 14px 44px; }

        .card {
            border-radius: 18px; border: 1px solid var(--border); padding: 18px;
            box-shadow: 0 1px 3px rgba(15,23,42,0.05); margin-bottom: 16px;
        }
        .card h2 {
            font-size: 15px; font-weight: 800; border-bottom: none; padding-bottom: 0; margin-bottom: 14px;
        }
        .card h2::before { content: ""; width: 4px; height: 16px; border-radius: 4px; background: linear-gradient(180deg, #60a5fa, #1d4ed8); display: inline-block; }

        table { border-radius: 14px; border: 1px solid var(--border); box-shadow: none; margin-top: 6px; }
        th { background: #f8fafc; color: #475569; font-size: 12px; font-weight: 800; padding: 11px 10px; }
        td { font-size: 13.5px; }
        tbody tr:nth-child(even) { background: #fff; }
        @media (hover: hover) { tbody tr:hover td { background: #f5f8ff; } }

        .btn { border-radius: 11px; box-shadow: none; }
        .btn-submit { background: linear-gradient(135deg, #1d4ed8, #1e3a8a); border-bottom: none; border-radius: 12px; box-shadow: 0 8px 18px -8px rgba(30,58,138,0.55); }
        .btn-danger { background: #fee2e2; color: #b91c1c; }
        .btn-warning { background: #fef3c7; color: #b45309; }
        .btn-secondary { background: #e2e8f0; color: #334155; }

        input[type="text"], input[type="password"], input[type="date"], input[type="number"], input[type="tel"],
        input[type="email"], input[type="time"], input[type="search"], input[type="url"], textarea, select {
            border-radius: 12px; border: 1.5px solid #dbe2ec; padding: 11.5px 13px; font-family: 'Sarabun', 'Inter', sans-serif;
        }
        textarea { width: 100%; box-sizing: border-box; margin-bottom: 14px; font-size: 14px; }
        input:focus, textarea:focus, select:focus { outline: none; border-color: #1d4ed8; box-shadow: 0 0 0 4px rgba(29,78,216,0.12); }

        .badge { background: #eef2ff; color: #3730a3; border: none; padding: 3px 10px; }
        .menu-btn { border-radius: 16px; border-bottom: 1px solid var(--border); }
    </style>

    <script>
        // 🎨 CUSTOM ALERT SYSTEM BY KK STUDIO
        function smartAlert(options) {
            const { title, message, type = 'success', callback = null } = options;
            const overlay = document.createElement('div');
            overlay.className = `smart-alert-overlay alert-${type}`;
            
            const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
            
            overlay.innerHTML = `
                <div class="smart-alert-card">
                    <div class="smart-alert-icon">${icons[type]}</div>
                    <div class="smart-alert-title">${title}</div>
                    <div class="smart-alert-msg">${message}</div>
                    <button class="smart-alert-btn">ตกลง</button>
                </div>
            `;
            
            document.body.appendChild(overlay);
            setTimeout(() => overlay.classList.add('active'), 10);
            
            const closeBtn = overlay.querySelector('.smart-alert-btn');
            closeBtn.onclick = () => {
                overlay.classList.remove('active');
                setTimeout(() => {
                    overlay.remove();
                    if (callback) callback();
                }, 300);
            };
        }

        // ⚡ ใช้ AudioContext ตัวเดียวซ้ำตลอด (ตัวเดิมสร้างใหม่ทุกคลิกแล้วไม่ปิด ทำให้เว็บหน่วง/ค้างเมื่อใช้ไปนานๆ)
        let __sharedAudioCtx = null;
        function getAudioCtx() {
            if (!__sharedAudioCtx) {
                try { __sharedAudioCtx = new (window.AudioContext || window.webkitAudioContext)(); }
                catch (e) { return null; }
            }
            if (__sharedAudioCtx.state === 'suspended') { __sharedAudioCtx.resume(); }
            return __sharedAudioCtx;
        }
        function playClickSound() {
            try {
                const audioCtx = getAudioCtx();
                if (!audioCtx) return;
                const oscillator = audioCtx.createOscillator();
                const gainNode = audioCtx.createGain();
                oscillator.type = 'sine';
                oscillator.frequency.setValueAtTime(1800, audioCtx.currentTime); 
                oscillator.frequency.exponentialRampToValueAtTime(800, audioCtx.currentTime + 0.03);
                gainNode.gain.setValueAtTime(0.08, audioCtx.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.03); 
                oscillator.connect(gainNode);
                gainNode.connect(audioCtx.destination);
                oscillator.start(); oscillator.stop(audioCtx.currentTime + 0.03);
                oscillator.onended = () => { oscillator.disconnect(); gainNode.disconnect(); };
            } catch (e) { console.log(e); }
        }

        // 📡 ระบบ WebSockets เรียลไทม์ (กดเปลี่ยนโหมดปุ๊บ ดีดหน้าจออาจารย์ทันทีทุกคน)
        let lsReconnectDelay = 1000;
        function initLiveSocket() {
            if (window.location.pathname.startsWith("/admin")) return; 

            const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
            const wsUrl = protocol + window.location.host + "/ws/maintenance";
            const ws = new WebSocket(wsUrl);

            ws.onopen = function() {
                lsReconnectDelay = 1000; // เชื่อมต่อสำเร็จ รีเซ็ตดีเลย์กลับเป็นค่าเริ่มต้น
            };

            ws.onmessage = function(event) {
                if (event.data === "STATUS_CHANGED") {
                    fetch('/api/check_maintenance_status')
                        .then(response => response.json())
                        .then(data => {
                            if (data.is_active === 1) {
                                if (!window.location.pathname.includes("/login")) {
                                    window.location.href = "/login"; 
                                } else {
                                    window.location.reload();
                                }
                            } else {
                                if (document.getElementById("maintenance-screen")) {
                                    window.location.href = "/login"; 
                                }
                            }
                        }).catch(err => console.log(err));
                }
            };

            ws.onclose = function() {
                // Exponential backoff (สูงสุด 30 วินาที) กันไม่ให้ยิง reconnect ถี่เกินไปตอนเน็ต/tunnel ไม่เสถียร
                setTimeout(initLiveSocket, lsReconnectDelay);
                lsReconnectDelay = Math.min(lsReconnectDelay * 1.7, 30000);
            };
        }

        document.addEventListener("DOMContentLoaded", function() {
            initLiveSocket();
            document.querySelectorAll("a, button, input[type='submit'], input[type='checkbox'], input[type='radio'], .status-label, select").forEach(function(item) {
                item.addEventListener("click", playClickSound);
            });

            // ─── SCREEN LOCK SYSTEM ───
            const lockHTML = `
                <div id="screenlock-overlay">
                    <div id="screenlock-box">
                        <div class="lock-icon">🔐</div>
                        <h2>หน้าจอถูกล็อก</h2>
                        <p>ใส่รหัสผ่าน Admin เพื่อใช้งานต่อ</p>
                        <input id="screenlock-input" type="password" placeholder="รหัสผ่าน" autocomplete="off" />
                        <button id="screenlock-btn" onclick="unlockScreen()">🔓 ปลดล็อก</button>
                        <div id="screenlock-error"></div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', lockHTML);

            // วางปุ่มล็อกข้างๆ ปุ่ม logout (a.btn ตัวสุดท้ายใน navbar)
            const navbar = document.querySelector('.navbar');
            if (navbar && window.location.pathname.startsWith('/admin')) {
                const lockBtn = document.createElement('button');
                lockBtn.id = 'btn-lock-screen';
                lockBtn.innerHTML = '🔒 ล็อกหน้าจอ';
                lockBtn.onclick = lockScreen;
                const navBtns = navbar.querySelectorAll('a.btn');
                const logoutBtn = navBtns[navBtns.length - 1]; // ปุ่มสุดท้าย = logout
                if (logoutBtn) logoutBtn.insertAdjacentElement('beforebegin', lockBtn);
                else navbar.appendChild(lockBtn);
            }

            // ── บล็อก ทุก event ขณะล็อก (capture phase = จับก่อน element ใดๆ) ──
            const BLOCK_EVENTS = [
                'click','mousedown','mouseup','touchstart','touchend',
                'pointerdown','pointerup','keydown','keyup','keypress',
                'submit','change','input','focus','contextmenu'
            ];

            function isInsideLockBox(target) {
                const box = document.getElementById('screenlock-box');
                return box && box.contains(target);
            }

            function isLocked() {
                const overlay = document.getElementById('screenlock-overlay');
                return overlay && overlay.classList.contains('active');
            }

            function showLockedToast() {
                // ป้องกันขึ้นซ้ำ
                if (document.getElementById('lock-toast')) return;
                const toast = document.createElement('div');
                toast.id = 'lock-toast';
                toast.textContent = '⛔ คุณไม่มีสิทธิ์ใช้งานฟังก์ชันขณะนี้';
                toast.style.cssText = [
                    'position:fixed','bottom:32px','left:50%',
                    'transform:translateX(-50%)','z-index:999999',
                    'background:#0f172a','color:#fbbf24',
                    'font-family:Sarabun,sans-serif','font-size:14px','font-weight:700',
                    'padding:12px 24px','border-radius:12px',
                    'box-shadow:0 8px 24px rgba(0,0,0,0.4)',
                    'white-space:nowrap','pointer-events:none',
                    'animation:toastIn 0.25s ease'
                ].join(';');
                document.body.appendChild(toast);
                setTimeout(() => { toast.style.opacity='0'; toast.style.transition='opacity 0.3s'; }, 1400);
                setTimeout(() => { if(toast.parentNode) toast.parentNode.removeChild(toast); }, 1700);
            }

            BLOCK_EVENTS.forEach(function(evtName) {
                document.addEventListener(evtName, function(e) {
                    if (!isLocked()) return;
                    // อนุญาต: อยู่ใน lockbox หรือเป็น Enter ในช่อง input
                    if (isInsideLockBox(e.target)) return;
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    // แสดง toast เฉพาะ event ที่ "กด" จริงๆ
                    if (['click','mousedown','touchstart','pointerdown','keydown'].includes(evtName)) {
                        showLockedToast();
                    }
                }, true);
            });
        });

        function lockScreen() {
            const overlay = document.getElementById('screenlock-overlay');
            if (!overlay) return;
            document.body.classList.add('screen-locked');
            overlay.classList.add('active');
            document.getElementById('screenlock-input').value = '';
            document.getElementById('screenlock-error').textContent = '';
            setTimeout(() => document.getElementById('screenlock-input').focus(), 150);
        }

        function unlockScreen() {
            const input = document.getElementById('screenlock-input');
            const errorEl = document.getElementById('screenlock-error');
            fetch('/api/verify_admin_pass', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: input.value })
            })
            .then(r => r.json())
            .then(data => {
                if (data.ok) {
                    document.getElementById('screenlock-overlay').classList.remove('active');
                    document.body.classList.remove('screen-locked');
                    errorEl.textContent = '';
                    input.value = '';
                } else {
                    input.classList.add('shake');
                    input.value = '';
                    errorEl.textContent = '❌ รหัสผ่านไม่ถูกต้อง';
                    setTimeout(() => { input.classList.remove('shake'); input.focus(); }, 400);
                }
            })
            .catch(() => { errorEl.textContent = '⚠️ เชื่อมต่อไม่ได้ ลองใหม่'; });
        }
    </script>
</head>
"""

# ==========================================
# 🛠️ HELPER FUNCTIONS
# ==========================================

def realtime_notify_script(my_id: str) -> str:
    """🔴 สคริปต์แจ้งเตือนแบบเรียลไทม์ผ่าน WebSocket — เสียบไว้ในหน้าไหน พอมีเหตุการณ์เกี่ยวกับ my_id (uid นักเรียน)
    เกิดขึ้น (เช่น ครูหักคะแนน/คืนคะแนน) จะยิงแจ้งเตือนจริงของเครื่อง (Notification API) ทันทีโดยไม่ต้องรีเฟรชหน้า
    ถ้าเบราว์เซอร์/WebView ไม่รองรับหรือผู้ใช้ไม่ให้สิทธิ์ จะ fallback เป็น toast ในหน้าเว็บแทน
    และอัปเดตตัวเลขคะแนนสดถ้ามี element ที่ใส่ attribute data-live-score ไว้ในหน้านั้น"""
    return f"""
    <script>
    (function() {{
        const MY_ID = {my_id!r};

        // 🔔 ขอสิทธิ์แจ้งเตือนของเครื่องตั้งแต่โหลดหน้า (ต้องขอตอนมี user gesture บางเบราว์เซอร์ถึงจะติด แต่ลองไว้ก่อนเสมอ)
        if (typeof Notification !== 'undefined' && Notification.permission === 'default') {{
            try {{ Notification.requestPermission(); }} catch(e) {{}}
        }}
        // บาง WebView ต้องขอตอนมีการโต้ตอบจากผู้ใช้ก่อน — ขอซ้ำตอนแตะหน้าจอครั้งแรก เผื่อรอบแรกไม่ติด
        document.addEventListener('click', function onFirstTap() {{
            if (typeof Notification !== 'undefined' && Notification.permission === 'default') {{
                try {{ Notification.requestPermission(); }} catch(e) {{}}
            }}
            document.removeEventListener('click', onFirstTap);
        }}, {{ once: true }});

        function showRealtimeToast(title, message, tone) {{
            const colors = {{
                success: {{bg:'#f0fdf4', border:'#bbf7d0', text:'#15803d', icon:'✅'}},
                danger:  {{bg:'#fef2f2', border:'#fecaca', text:'#b91c1c', icon:'⚠️'}},
                info:    {{bg:'#eff6ff', border:'#bfdbfe', text:'#1d4ed8', icon:'🔔'}}
            }};
            const c = colors[tone] || colors.info;
            const toast = document.createElement('div');
            toast.style.cssText = `position:fixed; top:calc(env(safe-area-inset-top,0px) + 12px); left:12px; right:12px; z-index:99999; background:${{c.bg}}; border:1.5px solid ${{c.border}}; color:${{c.text}}; border-radius:14px; padding:12px 14px; box-shadow:0 10px 30px -10px rgba(0,0,0,0.25); font-family:'Sarabun',sans-serif; transform:translateY(-140%); transition:transform .35s ease; display:flex; gap:10px; align-items:flex-start;`;
            toast.innerHTML = `<span style="font-size:20px;">${{c.icon}}</span><div style="flex:1;min-width:0;"><div style="font-weight:800;font-size:13.5px;">${{title}}</div><div style="font-size:12.5px;margin-top:2px;">${{message}}</div></div><span style="cursor:pointer;font-weight:800;padding:0 4px;" onclick="this.parentElement.remove()">✕</span>`;
            document.body.appendChild(toast);
            requestAnimationFrame(() => {{ toast.style.transform = 'translateY(0)'; }});
            setTimeout(() => {{ toast.style.transform = 'translateY(-140%)'; setTimeout(() => toast.remove(), 400); }}, 6000);
        }}

        function fireNotification(title, message, tone) {{
            if (navigator.vibrate) {{ try {{ navigator.vibrate(tone === 'danger' ? [80, 40, 80] : 60); }} catch(e) {{}} }}
            // 📱 ถ้าเบราว์เซอร์/WebView รองรับ Notification API และได้รับสิทธิ์แล้ว → ยิงเป็นแจ้งเตือนจริงของเครื่อง
            if (typeof Notification !== 'undefined' && Notification.permission === 'granted') {{
                try {{
                    const n = new Notification(title, {{
                        body: message,
                        icon: {LOGO_URL!r},
                        tag: 'kschool-' + Date.now(),
                    }});
                    n.onclick = function() {{ try {{ window.focus(); }} catch(e) {{}} n.close(); }};
                }} catch(e) {{
                    showRealtimeToast(title, message, tone);
                }}
            }} else {{
                // ยังไม่ได้สิทธิ์/ไม่รองรับ → ใช้ toast ในหน้าเว็บแทนไปก่อน
                showRealtimeToast(title, message, tone);
            }}
        }}

        function connectRealtime() {{
            const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
            let ws;
            try {{ ws = new WebSocket(protocol + window.location.host + '/ws/notify'); }} catch(e) {{ return; }}
            ws.onmessage = function(event) {{
                let data;
                try {{ data = JSON.parse(event.data); }} catch(e) {{ return; }}
                if (data.type !== 'student_notify') return;
                const isForMe = data.broadcast_all === true
                    || (Array.isArray(data.target_uids) && data.target_uids.includes(MY_ID))
                    || (data.target_uid !== undefined && data.target_uid === MY_ID);
                if (!isForMe) return;
                fireNotification(data.title, data.message, data.tone || 'info');
                if (data.score_now !== undefined) {{
                    document.querySelectorAll('[data-live-score]').forEach(el => {{ el.textContent = data.score_now; }});
                }}
            }};
            ws.onclose = function() {{ setTimeout(connectRealtime, 3000); }};
            ws.onerror = function() {{ try {{ ws.close(); }} catch(e) {{}} }};
        }}
        connectRealtime();
    }})();
    </script>
    """

async def push_student_notify(title: str, message: str, tone: str = "info",
                               target_uids: Optional[list] = None, all_students: bool = False,
                               score_now: Optional[int] = None):
    """🔴 ส่งแจ้งเตือนเรียลไทม์ผ่าน WebSocket ไปยังนักเรียน
    - target_uids: ส่งเฉพาะรายชื่อ uid ที่ระบุ (เช่น นักเรียนในกลุ่มวิชาที่ได้รับการบ้านใหม่)
    - all_students: True = กระจายให้นักเรียนทุกคนเห็น (เช่น ประกาศใหม่)
    ฝั่ง client (realtime_notify_script) จะกรองเองว่าใครควรเห็นข้อความนี้"""
    import json as _json
    payload = {"type": "student_notify", "title": title, "message": message, "tone": tone}
    if all_students:
        payload["broadcast_all"] = True
    if target_uids:
        payload["target_uids"] = list(target_uids)
    if score_now is not None:
        payload["score_now"] = score_now
    await manager.broadcast(_json.dumps(payload))

def find_student_uid(name: str, no: str, classroom: str) -> Optional[str]:
    """🔎 หา uid ของนักเรียนจากชื่อ+เลขที่+ห้อง — ใช้กับตารางเก่า (เช่น leave_requests) ที่ยังไม่ได้ผูก uid ตรงๆ"""
    for s in get_sorted_master_students():
        if s['name'] == name and s['no'] == no and s['class'] == classroom:
            return s['uid']
    return None

# 🔔 ใช้แทน "<script>alert(...); redirect</script>" ทั้งหมด — แสดงเป็นหน้าแจ้งเตือนสไตล์แอปของเราเอง
# (ไม่พึ่ง STYLE_HEADER เพื่อให้โหลดเร็วและใช้ได้แม้ตอบกลับ POST request แบบเดี่ยวๆ)
def alert_redirect(message: str, type: str = "info", url: Optional[str] = None, title: Optional[str] = None):
    icon = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(type, "ℹ️")
    bg, fg = {
        "success": ("#f0fdf4", "#10b981"),
        "error": ("#fef2f2", "#ef4444"),
        "warning": ("#fffbeb", "#f59e0b"),
        "info": ("#eff6ff", "#3b82f6"),
    }.get(type, ("#eff6ff", "#3b82f6"))
    if not title:
        title = {"success": "สำเร็จ", "error": "เกิดข้อผิดพลาด", "warning": "โปรดตรวจสอบ", "info": "แจ้งให้ทราบ"}.get(type, "แจ้งให้ทราบ")
    action_js = f"window.location.href='{url}';" if url else "history.back();"
    return HTMLResponse(f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>K-School</title>
<style>
    * {{ box-sizing: border-box; }}
    body {{
        margin: 0; font-family: 'Inter', 'Sarabun', -apple-system, sans-serif;
        background: rgba(11,17,32,0.68);
        min-height: 100vh; min-height: 100dvh;
        display: flex; align-items: center; justify-content: center; padding: 20px;
    }}
    .ar-card {{
        background: #fff; width: 100%; max-width: 360px; border-radius: 22px;
        padding: 32px 24px; text-align: center;
        box-shadow: 0 20px 40px -12px rgba(15,23,42,0.4);
        animation: arPop 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
    }}
    @keyframes arPop {{ from {{ transform: scale(0.9); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}
    .ar-icon {{
        width: 62px; height: 62px; border-radius: 50%;
        background: {bg}; color: {fg}; font-size: 30px;
        display: flex; align-items: center; justify-content: center; margin: 0 auto 18px;
    }}
    .ar-card h2 {{ margin: 0 0 8px; font-size: 19px; font-weight: 800; color: #0f172a; }}
    .ar-card p {{ margin: 0 0 22px; font-size: 14px; color: #64748b; line-height: 1.65; }}
    .ar-card button {{
        background: linear-gradient(135deg, #1e40af, #0f172a); color: #fff; border: none;
        padding: 13px 32px; border-radius: 12px; font-weight: 700; font-size: 14.5px;
        cursor: pointer; width: 100%;
    }}
    .ar-card button:active {{ transform: scale(0.98); }}
</style></head>
<body>
    <div class="ar-card">
        <div class="ar-icon">{icon}</div>
        <h2>{title}</h2>
        <p>{message}</p>
        <button onclick="{action_js}">ตกลง</button>
    </div>
</body></html>""")

def get_maintenance_status():
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT is_active, mode_type FROM maintenance_settings WHERE id = 1")
    res = cursor.fetchone()
    conn.close()
    if res: return {"is_active": res[0], "mode_type": res[1]}
    return {"is_active": 0, "mode_type": "off"}

def generate_maintenance_html(mode_type: str):
    config = {
        "maintenance": {"icon": "🏗️", "title": "ระบบกำลังปรับปรุงแก้ไขเว็บไซต์", "desc": "เจ้าของเว็บกำลังเซ็ตติ้งปรับระบบหลังบ้านชั่วคราว กรุณากลับมาใหม่อีกครั้ง"},
        "updating": {"icon": "🚀", "title": "กำลังอัปเดตระบบเวอร์ชันใหม่", "desc": "กำลังโหลดเพิ่มฟีเจอร์และเพิ่มความเสถียรให้เจ๋งขึ้นกว่าเดิม อดใจรอสักครู่!"},
        "testing": {"icon": "🧪", "title": "กำลังอยู่ในช่วงทดสอบระบบ (BETA TESTING)", "desc": "ทีมพัฒนาซอฟต์แวร์กำลังจำลองทดลองเล่นระบบเพื่อหาจุดบั๊ก คลาสเรียนโปรดรอการอนุมัติ"},
        "disabled": {"icon": "🔒", "title": "ระบบนี้ถูกปิดใช้งานชั่วคราว", "desc": "ขณะนี้ทางแอดมินกลางได้สั่งแช่แข็งปิดรับรายงานชั่วคราว ติดต่อเจ้าของเว็บเพื่อสอบถามข้อมูล"},
        "ip_error": {"icon": "🚫", "title": "ไม่มีการจัดสรร IP — ERROR 404", "desc": "IP Address Gateway Unassigned. ไม่สามารถเชื่อมโยงเซิร์ฟเวอร์ปลายทางระบบ K-School ได้ในขณะนี้"}
    }
    c = config.get(mode_type, config["maintenance"])
    
    bg_color = "#1e293b"
    if mode_type == "updating": bg_color = "#1e3a8a"
    elif mode_type == "testing": bg_color = "#6d28d9"
    elif mode_type == "disabled": bg_color = "#475569"
    elif mode_type == "ip_error": bg_color = "#b91c1c"

    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{c['title']}</title>
        <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', 'Sarabun', sans-serif; background-color: {bg_color}; color: white; margin: 0; padding: 24px; display: flex; align-items: center; justify-content: center; height: 100vh; box-sizing: border-box; text-align: center; }}
            .m-box {{ background: rgba(0, 0, 0, 0.25); border-radius: 20px; padding: 40px 30px; max-width: 480px; box-shadow: 0 20px 4px rgba(0,0,0,0.15); border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(8px); }}
            .icon {{ font-size: 75px; margin-bottom: 15px; animation: float 3s ease-in-out infinite; }}
            h1 {{ font-size: 24px; font-weight: 700; margin: 0 0 12px 0; letter-spacing: 0.5px; }}
            p {{ font-size: 15px; color: #cbd5e1; margin: 0 0 20px 0; line-height: 1.6; }}
            .brand {{ font-size: 12px; font-weight: 700; color: #d4af37; letter-spacing: 1px; text-transform: uppercase; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px; }}
            @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-12px); }} }}
        </style>
        <script>
            // หน้าซ่อมแซมก็เกาะท่อ WebSocket ไว้ พอกดเปิดปกติปุ๊บ ทุกคนก็จะเด้งวับกลับไปพร้อมกัน
            const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
            const ws = new WebSocket(protocol + window.location.host + "/ws/maintenance");
            ws.onmessage = function(event) {{
                if (event.data === "STATUS_CHANGED") {{
                    fetch('/api/check_maintenance_status')
                        .then(res => res.json())
                        .then(data => {{
                            if (data.is_active === 0) {{ window.location.href = "/login"; }}
                        }});
                }}
            }};
            ws.onclose = function() {{
                setTimeout(() => {{ window.location.reload(); }}, 3000);
            }};
        </script>
    </head>
    <body id="maintenance-screen">
        <div class="m-box">
            <div class="icon">{c['icon']}</div>
            <h1>{c['title']}</h1>
            <p>{c['desc']}</p>
            <div class="brand">Powered by KK Studio Group ⚡</div>
        </div>
    </body>
    </html>
    """

def get_sorted_master_students():
    students = []
    if os.path.exists(TXT_DATABASE_PATH):
        with open(TXT_DATABASE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and "," in line:
                    parts = line.split(",")
                    if len(parts) >= 4:
                        students.append({
                            "name": parts[0].strip(),
                            "no": parts[1].strip(),
                            "class": parts[2].strip(),
                            "branch": parts[3].strip(),
                            "uid": f"{parts[0].strip()}_{parts[1].strip()}"
                        })
    def sorting_key(x):
        try: num = int(x["no"])
        except ValueError: num = 999
        return (x["class"], num)
    students.sort(key=sorting_key)
    return students

CONDUCT_START_SCORE = 100

def get_grade_level(classroom: str) -> str:
    """แยกระดับชั้นจากชื่อห้อง เช่น 'ม.2/2' -> 'ม.2' (ถ้าไม่มี '/' จะคืนค่าห้องเดิมทั้งหมด)"""
    if "/" in classroom:
        return classroom.split("/")[0].strip()
    return classroom.strip()

def get_conduct_summary(class_filter: Optional[str] = None) -> list:
    """คืนรายชื่อนักเรียนทั้งหมดพร้อมคะแนนความประพฤติปัจจุบัน (เริ่มต้น 100 บวก/ลบตามประวัติ)"""
    students = get_sorted_master_students()
    if class_filter:
        students = [s for s in students if s['class'] == class_filter]
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT student_uid, SUM(points), COUNT(*), MAX(created_at) FROM conduct_scores GROUP BY student_uid")
    rows = {r[0]: {"total": r[1] or 0, "count": r[2], "last": r[3]} for r in cursor.fetchall()}
    conn.close()
    result = []
    for s in students:
        info = rows.get(s['uid'], {"total": 0, "count": 0, "last": None})
        score = max(0, min(100, CONDUCT_START_SCORE + info["total"]))
        result.append({**s, "score": score, "entry_count": info["count"], "last_change": info["last"]})
    return result

def get_conduct_history(uid: str) -> list:
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, points, reason, recorded_by, created_at FROM conduct_scores WHERE student_uid = ? ORDER BY created_at DESC, id DESC", (uid,))
    rows = cursor.fetchall()
    conn.close()
    history = []
    running = CONDUCT_START_SCORE
    # คำนวณคะแนนสะสม ณ แต่ละจุดเวลา (จากเก่าไปใหม่) แล้วค่อยกลับลำดับให้ล่าสุดอยู่บน
    totals = []
    running = CONDUCT_START_SCORE
    for entry_id, points, reason, recorded_by, created_at in reversed(rows):
        running = max(0, min(100, running + points))
        totals.append((entry_id, points, reason, recorded_by, created_at, running))
    for entry_id, points, reason, recorded_by, created_at, running_total in reversed(totals):
        history.append({
            "id": entry_id, "points": points, "reason": reason, "recorded_by": recorded_by,
            "created_at": created_at, "running_total": running_total
        })
    return history

# ==========================================
# 🔐 ระบบสิทธิ์การเข้าถึงแยกตามบทบาท (RBAC)
# ==========================================
# บทบาทของครู: teacher (ครูผู้สอนทั่วไป) / level_head (หัวหน้าระดับ) / affairs (ฝ่ายกิจการนักเรียน)
# admin คือเจ้าของระบบ (ผูกกับ ADMIN_USER/ADMIN_PASS เดิม ไม่ใช่ตาราง teachers)
TEACHER_ROLES = {
    "teacher":    {"label": "👩‍🏫 ครูผู้สอน",        "desc": "ดูแลเฉพาะคลาสเรียนของตนเอง"},
    "level_head": {"label": "🎓 หัวหน้าระดับ",       "desc": "อนุมัติคำร้องลา/บันทึกความประพฤติ เฉพาะระดับชั้นที่รับผิดชอบ"},
    "affairs":    {"label": "🛡️ ฝ่ายกิจการนักเรียน", "desc": "อนุมัติคำร้องลา/บันทึกความประพฤติ ได้ทุกระดับชั้นทั้งสถาบัน"},
}

def get_access(user_session: Optional[str]) -> dict:
    """อ่านคุกกี้ session แล้วคืนค่าข้อมูลสิทธิ์การเข้าถึงของผู้ใช้งานปัจจุบัน"""
    access = {"authenticated": False, "role": None, "username": None, "level_scope": "", "fullname": "", "role_label": ""}
    if not user_session:
        return access
    if user_session == "admin":
        access.update({"authenticated": True, "role": "admin", "username": "admin", "fullname": "ผู้ดูแลระบบ", "role_label": "👑 ผู้ดูแลระบบ"})
        return access
    if user_session.startswith("teacher_"):
        username = urllib.parse.unquote(user_session.replace("teacher_", "", 1))
        conn = sqlite3.connect('attendance_pro.db')
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT role, level_scope, fullname FROM teachers WHERE username=?", (username,))
            row = cursor.fetchone()
        finally:
            conn.close()
        if not row:
            return access
        role, level_scope, fullname = row
        role = role or "teacher"
        access.update({
            "authenticated": True, "role": role, "username": username,
            "level_scope": (level_scope or "").strip(), "fullname": fullname or username,
            "role_label": TEACHER_ROLES.get(role, TEACHER_ROLES["teacher"])["label"]
        })
        return access
    if user_session.startswith("student_"):
        uid = urllib.parse.unquote(user_session.replace("student_", "", 1))
        access.update({"authenticated": True, "role": "student", "username": uid, "role_label": "🎒 นักเรียน"})
        return access
    return access

# ==========================================
# 🧩 PERMISSION MATRIX — สิทธิ์แต่ละบทบาทที่แอดมินปรับได้เองผ่านหน้าเว็บ
# ==========================================
# กำหนดสิทธิ์ที่ตั้งค่าได้ + ค่าเริ่มต้น (ใช้ตอนยังไม่มี override ในตาราง role_permissions)
PERMISSIONS = {
    "manage_discipline":        {"label": "จัดการคำร้องลา / คะแนนความประพฤติ", "default_roles": ("admin", "affairs", "level_head")},
    "manage_teacher_accounts":  {"label": "จัดการบัญชีครู",                    "default_roles": ("admin", "affairs", "level_head")},
    "manage_student_profiles":  {"label": "จัดการโปรไฟล์นักเรียน",             "default_roles": ("admin", "affairs", "level_head")},
    "view_analytics":           {"label": "ดูแดชบอร์ดสถิติขั้นสูง",            "default_roles": ("admin", "affairs", "level_head")},
    "manage_inspection":        {"label": "ตรวจระเบียบนักเรียน (ติ๊กผ่าน/ไม่ผ่าน)", "default_roles": ("admin", "affairs", "level_head", "teacher")},
    "view_inspection_report":   {"label": "ดูรายงานผลตรวจระเบียบ",             "default_roles": ("admin", "affairs", "level_head")},
    "manage_inspection_criteria": {"label": "จัดการตัวชี้วัดตรวจระเบียบ (เพิ่ม/ลบ)", "default_roles": ("admin", "affairs")},
}
# บทบาทที่ปรับสิทธิ์ผ่านตารางได้ (admin มีสิทธิ์ทุกอย่างเสมอ ไม่ต้องตั้งค่า)
CONFIGURABLE_ROLES = ("teacher", "level_head", "affairs")

def _load_permission_overrides() -> dict:
    """อ่านค่าที่แอดมิน override ไว้ทั้งหมดจาก DB -> {(role, perm_key): 0/1}"""
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT role, perm_key, allowed FROM role_permissions")
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    return {(r[0], r[1]): r[2] for r in rows}

def has_permission(access: dict, perm_key: str) -> bool:
    """ตรวจสิทธิ์แบบ role-based: admin ผ่านเสมอ, บทบาทอื่นเช็คจากตาราง role_permissions ถ้ามี override ไม่งั้นใช้ค่า default_roles"""
    role = access.get("role")
    if role == "admin":
        return True
    if not role:
        return False
    meta = PERMISSIONS.get(perm_key)
    if not meta:
        return False
    overrides = _load_permission_overrides()
    key = (role, perm_key)
    if key in overrides:
        return bool(overrides[key])
    return role in meta["default_roles"]

def get_permission_matrix() -> dict:
    """คืนตารางสิทธิ์ปัจจุบันทั้งหมด สำหรับแสดงในหน้า /admin/permissions -> {role: {perm_key: bool}}"""
    overrides = _load_permission_overrides()
    matrix = {}
    for role in CONFIGURABLE_ROLES:
        matrix[role] = {}
        for perm_key, meta in PERMISSIONS.items():
            key = (role, perm_key)
            matrix[role][perm_key] = bool(overrides[key]) if key in overrides else (role in meta["default_roles"])
    return matrix

def can_manage_discipline(access: dict) -> bool:
    """สิทธิ์จัดการคำร้องลา / คะแนนความประพฤติ (ปรับได้ที่ /admin/permissions)"""
    return has_permission(access, "manage_discipline")

def can_manage_teacher_accounts(access: dict) -> bool:
    """สิทธิ์เปิดหน้าจัดการบัญชีครู (ปรับได้ที่ /admin/permissions)"""
    return has_permission(access, "manage_teacher_accounts")

def can_manage_student_profiles(access: dict) -> bool:
    """สิทธิ์จัดการโปรไฟล์นักเรียน (ปรับได้ที่ /admin/permissions)"""
    return has_permission(access, "manage_student_profiles")

def can_view_analytics(access: dict) -> bool:
    """สิทธิ์ดูแดชบอร์ดสถิติขั้นสูง (ปรับได้ที่ /admin/permissions)"""
    return access.get("role") == "admin" or has_permission(access, "view_analytics")

def can_manage_inspection(access: dict) -> bool:
    """สิทธิ์ตรวจระเบียบนักเรียน — ติ๊กผ่าน/ไม่ผ่าน (ปรับได้ที่ /admin/permissions)"""
    return has_permission(access, "manage_inspection")

def can_view_inspection_report(access: dict) -> bool:
    """สิทธิ์ดูรายงานผลตรวจระเบียบ (ปรับได้ที่ /admin/permissions)"""
    return has_permission(access, "view_inspection_report")

def can_manage_inspection_criteria(access: dict) -> bool:
    """สิทธิ์เพิ่ม/ลบ/เปิด-ปิด ตัวชี้วัดการตรวจระเบียบ (ปรับได้ที่ /admin/permissions)"""
    return has_permission(access, "manage_inspection_criteria")

def in_inspection_scope(access: dict, classroom: str) -> bool:
    """ขอบเขตห้องที่ตรวจได้: หัวหน้าระดับเฉพาะระดับตัวเอง, บทบาทอื่นที่มีสิทธิ์ตรวจได้ทุกห้อง"""
    if access.get("role") == "level_head":
        return get_grade_level(classroom) == access.get("level_scope", "")
    return True


def verify_manager_password(access: dict, password: str) -> bool:
    """ยืนยันรหัสผ่านก่อนแก้ไข/ลบบัญชีครู: admin ใช้รหัส Admin กลาง ส่วนหัวหน้าระดับ/ฝ่ายกิจการ ใช้รหัสผ่านบัญชีตัวเอง"""
    if access.get("role") == "admin":
        return password == ADMIN_PASS
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM teachers WHERE username = ?", (access.get("username"),))
    row = cursor.fetchone()
    conn.close()
    return bool(row) and password == row[0]

def in_discipline_scope(access: dict, classroom: str) -> bool:
    """ตรวจว่าห้องเรียน classroom อยู่ในขอบเขตที่บทบาทนี้มีสิทธิ์เข้าถึงหรือไม่"""
    role = access.get("role")
    if role in ("admin", "affairs"):
        return True
    if role == "level_head":
        return get_grade_level(classroom) == access.get("level_scope", "")
    return False

def require_discipline_access(user_session: Optional[str]):
    """ใช้ต้นทางฟังก์ชัน route: คืน (access, redirect_or_None) — ถ้า redirect ไม่ใช่ None ให้ return ค่านั้นออกไปทันที"""
    access = get_access(user_session)
    if not access["authenticated"] or not can_manage_discipline(access):
        return access, RedirectResponse(url="/login", status_code=303)
    return access, None

# ==========================================
# 📡 LIVE API STATUS CHECK FOR FRONTEND
# ==========================================
@app.get("/api/check_maintenance_status")
async def api_check_maintenance_status():
    return JSONResponse(content=get_maintenance_status())

@app.post("/api/verify_admin_pass")
async def api_verify_admin_pass(request: Request, user_session: Optional[str] = Cookie(None)):
    """ตรวจรหัสผ่านสำหรับระบบล็อกหน้าจอ — ต้อง login แล้วเท่านั้น"""
    if user_session != "admin":
        return JSONResponse({"ok": False}, status_code=401)
    try:
        body = await request.json()
        password = body.get("password", "")
    except Exception:
        return JSONResponse({"ok": False}, status_code=400)
    return JSONResponse({"ok": password == ADMIN_PASS})

# ==========================================
# 📜 ข้อกำหนดและเงื่อนไข / นโยบายความเป็นส่วนตัว
# ==========================================
def legal_page(icon: str, title: str, subtitle: str, sections: list) -> str:
    body_html = ""
    for h, p in sections:
        body_html += f'<h2>{h}</h2><p>{p}</p>'
    return f"""
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>{title} | K-School</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sarabun:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:'Sarabun',sans-serif; background:#f8fafc; color:#1e293b; }}
        .lg-top {{ background:linear-gradient(135deg,#1e3a8a,#0f172a); color:#fff; padding:calc(env(safe-area-inset-top,0px) + 20px) 20px 22px; border-bottom:3px solid #d4af37; }}
        .lg-top h1 {{ font-size:18px; font-weight:800; display:flex; align-items:center; gap:8px; }}
        .lg-top p {{ font-size:12.5px; opacity:0.75; margin-top:4px; }}
        .lg-body {{ max-width:640px; margin:0 auto; padding:22px 18px calc(env(safe-area-inset-bottom,0px) + 30px); }}
        .lg-body h2 {{ font-size:15px; font-weight:800; color:#0f172a; margin:22px 0 8px; }}
        .lg-body h2:first-child {{ margin-top:0; }}
        .lg-body p {{ font-size:13.5px; line-height:1.8; color:#475569; }}
        .lg-back {{ display:inline-flex; align-items:center; gap:6px; color:#d4af37; text-decoration:none; font-size:13px; font-weight:700; margin-top:26px; }}
    </style>
</head>
<body>
    <div class="lg-top">
        <h1>{icon} {title}</h1>
        <p>{subtitle}</p>
    </div>
    <div class="lg-body">
        {body_html}
        <a href="javascript:void(0)" onclick="history.back()" class="lg-back">← ย้อนกลับ</a>
    </div>
</body>
</html>
"""

@app.get("/terms", response_class=HTMLResponse)
async def terms_page():
    return legal_page(
        "📜", "ข้อกำหนดและเงื่อนไขการใช้งาน", "K-School Enterprise — ระบบบริหารจัดการเวลาเรียนระดับองค์กร",
        [
            ("1. การใช้งานระบบ", "ระบบนี้จัดทำขึ้นเพื่อใช้ในการบันทึกและบริหารจัดการเวลาเรียนของนักเรียนภายในสถาบันเท่านั้น ผู้ใช้งานต้องเป็นบุคลากร ครู หรือผู้ที่ได้รับสิทธิ์จากสถาบันเท่านั้น"),
            ("2. บัญชีผู้ใช้งาน", "ผู้ใช้งานมีหน้าที่รักษาความปลอดภัยของชื่อผู้ใช้และรหัสผ่านของตนเอง และรับผิดชอบต่อกิจกรรมทั้งหมดที่เกิดขึ้นภายใต้บัญชีของตน"),
            ("3. ความถูกต้องของข้อมูล", "ผู้ใช้งานต้องกรอกและบันทึกข้อมูลด้วยความสุจริตและถูกต้องตามความเป็นจริง ห้ามบันทึกข้อมูลอันเป็นเท็จหรือแก้ไขข้อมูลโดยไม่ได้รับอนุญาต"),
            ("4. การเปลี่ยนแปลงเงื่อนไข", "สถาบันขอสงวนสิทธิ์ในการปรับปรุงหรือเปลี่ยนแปลงข้อกำหนดนี้ได้ตามความเหมาะสม โดยจะแจ้งให้ผู้ใช้งานทราบผ่านระบบ"),
        ]
    )

@app.get("/privacy", response_class=HTMLResponse)
async def privacy_page():
    return legal_page(
        "🔒", "นโยบายความเป็นส่วนตัว", "เราให้ความสำคัญกับความปลอดภัยของข้อมูลนักเรียนและบุคลากร",
        [
            ("1. ข้อมูลที่จัดเก็บ", "ระบบจัดเก็บข้อมูลเท่าที่จำเป็นต่อการบริหารจัดการเวลาเรียน ได้แก่ ชื่อ-นามสกุล เลขที่ ชั้นเรียน สถานะการเข้าเรียน และข้อมูลบัญชีผู้ใช้งาน"),
            ("2. วัตถุประสงค์การใช้ข้อมูล", "ข้อมูลจะถูกใช้เพื่อการเช็กชื่อ ติดตามสถิติการเข้าเรียน และการบริหารจัดการภายในสถาบันเท่านั้น จะไม่ถูกนำไปใช้เพื่อวัตถุประสงค์ทางการค้า"),
            ("3. การเข้าถึงข้อมูล", "เฉพาะครูและผู้ดูแลระบบที่ได้รับสิทธิ์เท่านั้นที่สามารถเข้าถึงข้อมูลได้ ระบบมีการควบคุมสิทธิ์การเข้าถึงตามบทบาทของผู้ใช้งาน"),
            ("4. ความปลอดภัยของข้อมูล", "รหัสผ่านของผู้ใช้งานจะถูกเข้ารหัสก่อนจัดเก็บ และมีมาตรการป้องกันการเข้าถึงข้อมูลโดยไม่ได้รับอนุญาต"),
            ("5. สิทธิ์ของเจ้าของข้อมูล", "ผู้ใช้งานสามารถติดต่อผู้ดูแลระบบเพื่อขอตรวจสอบหรือแก้ไขข้อมูลส่วนตัวของตนเองได้ตลอดเวลา"),
        ]
    )

# ==========================================
# 🌟 WHY CHOOSE US — LANDING PAGE
# ==========================================
@app.get("/why-us", response_class=HTMLResponse)
async def why_us_page():
    return """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>ทำไมต้องเลือก K-School? | KK Studio Group</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Sarabun:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root{
            --gold:#b8860b; --gold2:#d4af37; --blue:#2563eb; --blue2:#1d4ed8; --violet:#7c3aed;
            --bg:#eef4fc; --glass:rgba(255,255,255,0.6); --glass-brd:rgba(37,99,235,0.14);
            --ink:#0f172a; --sub:#475569; --mute:#64748b;
        }
        *{ margin:0; padding:0; box-sizing:border-box; }
        html{ scroll-behavior:smooth; scroll-padding-top:70px; }
        body{
            font-family:'Inter','Sarabun',sans-serif; background:var(--bg); color:var(--ink);
            overflow-x:hidden; position:relative;
        }
        /* ─── AMBIENT BACKGROUND ─── */
        .bg-mesh{ position:fixed; inset:0; z-index:-2; background:
            radial-gradient(ellipse 60% 40% at 15% 10%, #bfdbfe80 0%, transparent 60%),
            radial-gradient(ellipse 50% 50% at 85% 25%, #dbeafe90 0%, transparent 60%),
            radial-gradient(ellipse 60% 40% at 50% 80%, #e0e7ff60 0%, transparent 65%),
            linear-gradient(180deg,#f4f8ff 0%, #eaf2fd 50%, #eef4fc 100%); }
        .bg-grid{ position:fixed; inset:0; z-index:-1; pointer-events:none; opacity:.5;
            background-image:linear-gradient(rgba(30,64,175,0.035) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(30,64,175,0.035) 1px, transparent 1px);
            background-size:46px 46px; mask-image:radial-gradient(ellipse 80% 60% at 50% 20%, #000 10%, transparent 75%); }
        .orb{ position:fixed; border-radius:50%; filter:blur(90px); pointer-events:none; z-index:-1; }
        .orb-a{ width:380px; height:380px; background:radial-gradient(circle,#2563eb50,transparent 70%); top:-100px; left:-100px; animation:drift1 14s ease-in-out infinite; }
        .orb-b{ width:320px; height:320px; background:radial-gradient(circle,#d4af3733,transparent 70%); top:40%; right:-120px; animation:drift2 16s ease-in-out infinite; }
        .orb-c{ width:260px; height:260px; background:radial-gradient(circle,#7c3aed28,transparent 70%); bottom:5%; left:10%; animation:drift1 18s ease-in-out infinite reverse; }
        @keyframes drift1{ 0%,100%{transform:translate(0,0)} 50%{transform:translate(30px,25px)} }
        @keyframes drift2{ 0%,100%{transform:translate(0,0)} 50%{transform:translate(-25px,20px)} }

        /* ─── GLASS PRIMITIVE ─── */
        .glass{ background:var(--glass); border:1px solid var(--glass-brd); backdrop-filter:blur(18px) saturate(140%); -webkit-backdrop-filter:blur(18px) saturate(140%); }

        /* ─── NAVBAR ─── */
        .navbar{ position:sticky; top:0; z-index:50; padding:calc(env(safe-area-inset-top,0px) + 12px) 20px 12px;
            display:flex; align-items:center; justify-content:space-between;
            background:rgba(255,255,255,0.55); backdrop-filter:blur(16px) saturate(160%); -webkit-backdrop-filter:blur(16px) saturate(160%);
            border-bottom:1px solid rgba(37,99,235,0.1); }
        .nav-brand{ display:flex; align-items:center; gap:8px; font-weight:800; font-size:16px; letter-spacing:.3px; }
        .nav-brand .dot{ width:9px; height:9px; border-radius:50%; background:linear-gradient(135deg,var(--gold),var(--blue2)); box-shadow:0 0 12px #d4af3790; animation:blink 2.4s ease-in-out infinite; }
        @keyframes blink{ 0%,100%{opacity:1} 50%{opacity:.4} }
        .nav-brand .k{ background:linear-gradient(135deg,var(--gold2),var(--blue2)); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
        .nav-cta{ font-size:12.5px; font-weight:700; padding:8px 16px; border-radius:100px; text-decoration:none; color:#fff;
            background:linear-gradient(135deg,var(--gold2),var(--gold)); box-shadow:0 4px 16px #d4af3740; }

        /* ─── HERO ─── */
        .hero{ min-height:92vh; display:flex; flex-direction:column; align-items:center; justify-content:center;
            text-align:center; padding:50px 22px 36px; position:relative; }
        .badge-top{ display:inline-flex; align-items:center; gap:8px; padding:7px 16px 7px 12px; border-radius:100px;
            color:#92650e; font-size:11.5px; font-weight:700; letter-spacing:1.2px; margin-bottom:30px;
            animation:fadeDown .7s ease both; }
        .badge-top .pulse{ width:7px; height:7px; border-radius:50%; background:var(--gold2); box-shadow:0 0 10px #f4d35ea0; animation:blink 2s infinite; }
        .hero h1{ font-size:clamp(30px,8.5vw,54px); font-weight:900; line-height:1.14; letter-spacing:-0.6px; margin-bottom:18px;
            animation:fadeUp .8s ease .1s both; }
        .hero h1 .grad{ background:linear-gradient(100deg,var(--gold2) 0%, var(--gold) 35%, var(--blue2) 70%, var(--violet) 100%);
            background-size:200% auto; -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
            animation:shine 6s linear infinite; }
        @keyframes shine{ to{ background-position:200% center; } }
        .hero-sub{ font-size:15px; color:var(--sub); max-width:480px; line-height:1.75; margin-bottom:34px; animation:fadeUp .8s ease .2s both; }
        .hero-cta-row{ display:flex; flex-wrap:wrap; gap:12px; justify-content:center; animation:fadeUp .8s ease .3s both; }
        .btn-primary{ background:linear-gradient(135deg,#2563eb,#4f46e5); color:#fff; text-decoration:none;
            padding:15px 30px; border-radius:14px; font-size:15px; font-weight:700; display:inline-flex; align-items:center; gap:8px;
            box-shadow:0 10px 30px #2563eb40; border:1px solid rgba(255,255,255,0.12); transition:transform .15s, box-shadow .15s; }
        .btn-primary:active{ transform:translateY(2px) scale(.98); }
        .btn-outline{ color:#1e3a8a; text-decoration:none; padding:15px 28px; border-radius:14px; font-size:15px; font-weight:700;
            display:inline-flex; align-items:center; transition:all .15s; }
        .btn-outline:active{ background:rgba(37,99,235,0.1); }

        /* ─── STATS (glass pill bar) ─── */
        .stats-wrap{ padding:0 18px 56px; }
        .stats-band{ max-width:720px; margin:0 auto; border-radius:22px; padding:22px 10px; display:flex; flex-wrap:wrap; }
        .stat-item{ flex:1; min-width:110px; text-align:center; padding:12px 8px; position:relative; }
        .stat-item:not(:last-child)::after{ content:''; position:absolute; right:0; top:15%; bottom:15%; width:1px; background:rgba(255,255,255,0.08); }
        .stat-num{ font-size:28px; font-weight:800; line-height:1; margin-bottom:6px;
            background:linear-gradient(135deg,var(--gold2),var(--gold)); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
        .stat-label{ font-size:11.5px; color:var(--mute); font-weight:600; line-height:1.4; }

        /* ─── SECTION SHELL ─── */
        .section{ padding:58px 22px; max-width:760px; margin:0 auto; position:relative; }
        .section-label{ font-size:11px; font-weight:800; letter-spacing:2.2px; text-transform:uppercase; text-align:center; margin-bottom:12px;
            background:linear-gradient(135deg,var(--gold2),var(--blue2)); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
        .section-title{ font-size:clamp(22px,5vw,32px); font-weight:800; text-align:center; margin-bottom:10px; line-height:1.3; }
        .section-sub{ font-size:13.5px; color:var(--sub); text-align:center; margin-bottom:38px; max-width:460px; margin-left:auto; margin-right:auto; line-height:1.7; }

        /* ─── GLASS FEATURE CARDS ─── */
        .features-grid{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px; }
        .feat-card{ border-radius:20px; padding:26px 22px; position:relative; overflow:hidden; transition:transform .25s, border-color .25s, background .25s; }
        .feat-card::after{ content:''; position:absolute; inset:0; border-radius:20px; background:linear-gradient(145deg, rgba(255,255,255,0.06), transparent 40%); pointer-events:none; }
        .feat-card:hover{ transform:translateY(-5px); background:rgba(255,255,255,0.85); box-shadow:0 12px 30px -10px rgba(37,99,235,0.2); }
        .feat-icon{ width:50px; height:50px; border-radius:14px; display:flex; align-items:center; justify-content:center; font-size:24px; margin-bottom:16px;
            border:1px solid rgba(37,99,235,0.14); }
        .feat-card h3{ font-size:15.5px; font-weight:700; margin-bottom:8px; color:#0f172a; }
        .feat-card p{ font-size:13px; color:var(--sub); line-height:1.65; }
        .feat-tag{ display:inline-block; margin-top:14px; font-size:10.5px; font-weight:700; padding:4px 11px; border-radius:100px; letter-spacing:.4px;
            border:1px solid rgba(37,99,235,0.16); }

        /* ─── TIMELINE ─── */
        .steps-wrap{ display:flex; flex-direction:column; position:relative; }
        .steps-wrap::before{ content:''; position:absolute; left:23px; top:26px; bottom:26px; width:1px;
            background:linear-gradient(to bottom, var(--blue2), var(--violet), var(--gold)); opacity:.35; }
        .step-row{ display:flex; gap:20px; align-items:flex-start; padding:18px 0; }
        .step-num{ width:48px; height:48px; border-radius:16px; flex-shrink:0; display:flex; align-items:center; justify-content:center;
            font-size:17px; font-weight:800; position:relative; z-index:1; border:1px solid rgba(37,99,235,0.18); }
        .step-body{ padding-top:8px; }
        .step-body h4{ font-size:15px; font-weight:700; color:#0f172a; margin-bottom:5px; }
        .step-body p{ font-size:13px; color:var(--sub); line-height:1.65; }

        /* ─── COMPARE TABLE (glass) ─── */
        .compare-wrap{ border-radius:20px; overflow:hidden; }
        .compare-table{ width:100%; border-collapse:collapse; }
        .compare-table th{ padding:16px 12px; font-size:13px; font-weight:700; }
        .compare-table td{ padding:14px 12px; font-size:12.5px; border-top:1px solid rgba(255,255,255,0.06); color:var(--sub); }
        .compare-table tr:nth-child(even) td{ background:rgba(37,99,235,0.035); }
        .th-us{ background:linear-gradient(135deg,#1e3a8a,#2563eb); color:#fff; }
        .th-old{ background:rgba(37,99,235,0.05); color:var(--mute); }
        .th-feat{ background:rgba(37,99,235,0.03); color:var(--mute); }
        .check{ color:#059669; font-size:17px; }
        .cross{ color:#dc2626; font-size:17px; }

        /* ─── ADMIN HIGHLIGHT GLASS BOX ─── */
        .admin-box{ margin-top:30px; border-radius:20px; padding:30px 24px; text-align:center; }

        /* ─── TIPS GLASS BOX ─── */
        .tips-box{ margin-top:30px; border-radius:20px; padding:26px; }

        /* ─── CTA BOTTOM ─── */
        .cta-bottom{ text-align:center; padding:70px 24px; max-width:620px; margin:0 auto; }
        .cta-bottom h2{ font-size:clamp(22px,5vw,32px); font-weight:800; line-height:1.3; margin-bottom:12px; }
        .cta-bottom > p{ color:var(--sub); font-size:14px; }
        .cta-pill{ display:inline-flex; align-items:center; gap:8px; text-decoration:none; color:#fff;
            padding:16px 34px; border-radius:100px; font-size:14.5px; font-weight:800; letter-spacing:.3px;
            background:linear-gradient(135deg,var(--gold2),var(--gold)); box-shadow:0 10px 30px #d4af3745; }
        .ig-pill{ display:inline-flex; align-items:center; gap:10px; text-decoration:none; color:#fff;
            padding:16px 28px; border-radius:100px; font-size:14.5px; font-weight:800; letter-spacing:.2px;
            background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045); box-shadow:0 10px 28px rgba(253,29,29,0.3); }

        /* ─── FOOTER ─── */
        .footer{ border-top:1px solid rgba(255,255,255,0.06); padding:30px 24px; text-align:center; }
        .footer-ig{ display:inline-flex; align-items:center; gap:10px; text-decoration:none; margin-bottom:16px; }
        .footer-brand{ font-size:13px; font-weight:800; letter-spacing:1.4px;
            background:linear-gradient(135deg,var(--gold2),var(--blue2)); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
        .footer-sub{ font-size:11px; color:var(--mute); margin-top:5px; }

        /* ─── ANIMATIONS / REVEAL ─── */
        @keyframes fadeUp{ from{opacity:0; transform:translateY(26px);} to{opacity:1; transform:translateY(0);} }
        @keyframes fadeDown{ from{opacity:0; transform:translateY(-14px);} to{opacity:1; transform:translateY(0);} }
        .reveal{ opacity:0; transform:translateY(26px); transition:opacity .7s ease, transform .7s ease; }
        .revealed{ opacity:1; transform:translateY(0); }
    </style>
</head>
<body>
<div class="bg-mesh"></div>
<div class="bg-grid"></div>
<div class="orb orb-a"></div>
<div class="orb orb-b"></div>
<div class="orb orb-c"></div>

<!-- ─── NAVBAR ─── -->
<div class="navbar">
    <div class="nav-brand"><span class="dot"></span><span class="k">K-School</span></div>
    <a href="/login" class="nav-cta">เข้าสู่ระบบ</a>
</div>

<!-- ─── HERO ─── -->
<section class="hero">
    <div class="badge-top glass"><span class="pulse"></span>K-SCHOOL PLATFORM &nbsp;·&nbsp; BY KK STUDIO GROUP</div>
    <h1>ทำไมต้องเลือก<br><span class="grad">K-School</span>?</h1>
    <p class="hero-sub">ระบบเช็กชื่อดิจิทัลที่ออกแบบมาเพื่อห้องเรียนยุคใหม่ ครบ เร็ว แม่น และสวยกว่าที่เคยมีมา</p>
    <div class="hero-cta-row">
        <a href="/login" class="btn-primary">🚀 เข้าใช้งานระบบ</a>
        <a href="#features" class="btn-outline glass">ดูฟีเจอร์ทั้งหมด ↓</a>
    </div>
</section>

<!-- ─── STATS ─── -->
<div class="stats-wrap">
    <div class="stats-band glass">
        <div class="stat-item">
            <div class="stat-num">⚡</div>
            <div class="stat-label">Real-time<br>WebSocket</div>
        </div>
        <div class="stat-item">
            <div class="stat-num">100%</div>
            <div class="stat-label">บน Mobile<br>ใช้งานได้เลย</div>
        </div>
        <div class="stat-item">
            <div class="stat-num">∞</div>
            <div class="stat-label">ไม่จำกัด<br>จำนวนนักเรียน</div>
        </div>
        <div class="stat-item">
            <div class="stat-num">0s</div>
            <div class="stat-label">หน่วงเวลา<br>อัปเดตสถานะ</div>
        </div>
    </div>
</div>

<!-- ─── FEATURES ─── -->
<div id="features">
<div class="section">
    <p class="section-label reveal">ฟีเจอร์เด่น</p>
    <h2 class="section-title reveal">ทุกอย่างที่ครูต้องการ<br>อยู่ในที่เดียว</h2>
    <p class="section-sub reveal">ออกแบบมาเพื่อลดขั้นตอน ลดกระดาษ และทำให้การเช็กชื่อง่ายกว่าที่เคย</p>

    <div class="features-grid">
        <div class="feat-card glass reveal">
            <div class="feat-icon" style="background:linear-gradient(135deg,#1e3a8a33,#2563eb22);">📡</div>
            <h3>Real-time Sync ทันทีทุก Device</h3>
            <p>ใช้ WebSocket ส่งสัญญาณทุก client พร้อมกัน ครูกด เปลี่ยนสถานะปุ๊บ นักเรียนเห็นปั๊บ ไม่ต้อง refresh</p>
            <span class="feat-tag" style="color:#2563eb;">WebSocket Live</span>
        </div>
        <div class="feat-card glass reveal">
            <div class="feat-icon" style="background:linear-gradient(135deg,#d4af3733,#b8962e22);">🏆</div>
            <h3>บันทึก มา / สาย / ลา / ขาด ครบจบ</h3>
            <p>เลือกสถานะได้ง่ายด้วยปุ่มสีสวย กดทีเดียว ระบบบันทึกพร้อมวันที่ เวลา และชื่อครูผู้บันทึกอัตโนมัติ</p>
            <span class="feat-tag" style="color:#d4af37;">4 Status Types</span>
        </div>
        <div class="feat-card glass reveal">
            <div class="feat-icon" style="background:linear-gradient(135deg,#7c3aed33,#6d28d922);">📊</div>
            <h3>ดูประวัติย้อนหลังได้ทุกรอบ</h3>
            <p>คลังบันทึกเรียงตามวัน กรองตามวิชา เปิดดูได้ทั้งครูและแอดมิน แก้ไขหรือลบรายการซ้ำได้ทันที</p>
            <span class="feat-tag" style="color:#7c3aed;">Full History</span>
        </div>
        <div class="feat-card glass reveal">
            <div class="feat-icon" style="background:linear-gradient(135deg,#05966933,#04785222);">📱</div>
            <h3>Mobile-First ใช้บนมือถือลื่นมาก</h3>
            <p>ออกแบบมาให้ทำงานบนสมาร์ตโฟนเป็นหลัก ฟอนต์ใหญ่ ปุ่มกดง่าย รองรับทุกขนาดหน้าจอ</p>
            <span class="feat-tag" style="color:#059669;">Mobile-First</span>
        </div>
        <div class="feat-card glass reveal">
            <div class="feat-icon" style="background:linear-gradient(135deg,#dc262633,#b91c1c22);">🛡️</div>
            <h3>ระบบ Admin ควบคุมได้ทุกอย่าง</h3>
            <p>จัดการครู วิชา นักเรียน และสถานะเว็บผ่าน Discord Bot ได้เลย ไม่ต้องเปิดคอมพิวเตอร์</p>
            <span class="feat-tag" style="color:#dc2626;">Admin Control</span>
        </div>
        <div class="feat-card glass reveal">
            <div class="feat-icon" style="background:linear-gradient(135deg,#0284c733,#0369a122);">🤖</div>
            <h3>Discord Bot ผูกติดตัวเว็บ</h3>
            <p>กดปุ่มบน Discord เปลี่ยน Maintenance Mode ได้เลย แจ้งเตือน Log ทุกครั้งที่มีการเช็กชื่อแบบ Real-time</p>
            <span class="feat-tag" style="color:#0284c7;">Discord Integrated</span>
        </div>
    </div>
</div>
</div>

<!-- ─── HOW IT WORKS ─── -->
<div class="section">
    <p class="section-label reveal">ขั้นตอนการใช้งาน</p>
    <h2 class="section-title reveal">เริ่มใช้ได้ใน<br><span style="color:#2563eb;">3 ขั้นตอนง่ายๆ</span></h2>
    <p class="section-sub reveal">ไม่ต้องฝึกอบรม ไม่ต้องอ่านคู่มือ ครูคนใหม่ก็ใช้ได้เลย</p>

    <div class="steps-wrap">
        <div class="step-row reveal">
            <div class="step-num glass" style="color:#2563eb;">1</div>
            <div class="step-body">
                <h4>แอดมินสร้างบัญชีครูและตั้งวิชา</h4>
                <p>เพิ่มรายชื่อครู กำหนดกลุ่มวิชา และจัดนักเรียนเข้าวิชาผ่านหน้า Admin Dashboard ได้ภายใน 2 นาที</p>
            </div>
        </div>
        <div class="step-row reveal">
            <div class="step-num glass" style="color:#7c3aed;">2</div>
            <div class="step-body">
                <h4>ครู Login และเปิดคลาสวิชาของตัวเอง</h4>
                <p>ล็อกอินด้วย Username/Password บนมือถือ เห็นรายการวิชาทันที กดเปิดห้องเช็กชื่อได้เลย</p>
            </div>
        </div>
        <div class="step-row reveal">
            <div class="step-num glass" style="color:#d4af37;">3</div>
            <div class="step-body">
                <h4>กดเช็กชื่อ บันทึก ระบบส่ง Log อัตโนมัติ</h4>
                <p>เลือกสถานะแต่ละคน กดยืนยัน ระบบบันทึกลง SQLite และส่ง Log แจ้ง Discord พร้อมกันทันที</p>
            </div>
        </div>
    </div>
</div>

<!-- ─── COMPARE ─── -->
<div class="section">
    <p class="section-label reveal">เปรียบเทียบ</p>
    <h2 class="section-title reveal">K-School vs<br><span style="color:#64748b;">วิธีเดิมที่เคยใช้</span></h2>
    <p class="section-sub reveal">ลองเทียบกันแบบตรงๆ แล้วตัดสินใจเอง — ไม่ต้องคิดนาน</p>
    <div class="compare-wrap glass reveal">
        <table class="compare-table">
            <thead>
                <tr>
                    <th class="th-feat" style="text-align:left; padding-left:18px;">ฟีเจอร์</th>
                    <th class="th-us">⚡ K-School</th>
                    <th class="th-old">📄 กระดาษ / Excel</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="color:#1e293b;font-weight:600;padding-left:18px;">เช็กชื่อแบบ Real-time</td>
                    <td style="text-align:center;" class="check">✓</td>
                    <td style="text-align:center;" class="cross">✗</td>
                </tr>
                <tr>
                    <td style="color:#1e293b;font-weight:600;padding-left:18px;">ดูประวัติย้อนหลัง</td>
                    <td style="text-align:center;" class="check">✓</td>
                    <td style="text-align:center;color:#f59e0b;">△ ยุ่งยาก</td>
                </tr>
                <tr>
                    <td style="color:#1e293b;font-weight:600;padding-left:18px;">ใช้งานบนมือถือ</td>
                    <td style="text-align:center;" class="check">✓</td>
                    <td style="text-align:center;" class="cross">✗</td>
                </tr>
                <tr>
                    <td style="color:#1e293b;font-weight:600;padding-left:18px;">บันทึกเป็นไฟล์เองอัตโนมัติ</td>
                    <td style="text-align:center;" class="check">✓</td>
                    <td style="text-align:center;" class="cross">✗</td>
                </tr>
                <tr>
                    <td style="color:#1e293b;font-weight:600;padding-left:18px;">หลายครู หลายวิชา</td>
                    <td style="text-align:center;" class="check">✓</td>
                    <td style="text-align:center;color:#f59e0b;">△ ยุ่งมาก</td>
                </tr>
                <tr>
                    <td style="color:#1e293b;font-weight:600;padding-left:18px;">Admin ดูแลและควบคุมได้</td>
                    <td style="text-align:center;" class="check">✓</td>
                    <td style="text-align:center;" class="cross">✗</td>
                </tr>
                <tr>
                    <td style="color:#1e293b;font-weight:600;padding-left:18px;">ไม่ต้องพิมพ์เอกสาร</td>
                    <td style="text-align:center;" class="check">✓</td>
                    <td style="text-align:center;" class="cross">✗</td>
                </tr>
                <tr>
                    <td style="color:#1e293b;font-weight:600;padding-left:18px;">ข้อมูลปลอดภัยไม่สูญหาย</td>
                    <td style="text-align:center;" class="check">✓</td>
                    <td style="text-align:center;color:#f59e0b;">△ เสี่ยงสูง</td>
                </tr>
                <tr>
                    <td style="color:#1e293b;font-weight:600;padding-left:18px;">ค้นหาชื่อนักเรียนได้ทันที</td>
                    <td style="text-align:center;" class="check">✓</td>
                    <td style="text-align:center;" class="cross">✗</td>
                </tr>
            </tbody>
        </table>
    </div>
    <p class="reveal" style="text-align:center; margin-top:20px; font-size:12.5px; color:var(--mute); font-style:italic;">* ทุกฟีเจอร์ใช้งานได้ทันทีโดยไม่ต้องติดตั้งซอฟต์แวร์เพิ่มเติม</p>
</div>

<!-- ─── ADMIN SECTION ─── -->
<div class="section">
    <p class="section-label reveal">ทีมดูแลระบบ</p>
    <h2 class="section-title reveal">มีแอดมินดูแล<br><span style="color:#d4af37;">ตลอด 24 ชั่วโมง</span></h2>
    <p class="section-sub reveal">ไม่ใช่แค่ระบบอัตโนมัติ — มีคนคอยดูแลจริงๆ ตอบทุกปัญหา แก้ทุกบั๊ก</p>

    <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:16px; margin-top:8px;">
        <div class="feat-card glass reveal" style="text-align:center;">
            <div style="font-size:44px; margin-bottom:12px;">👑</div>
            <h3 style="color:#d4af37;">แอดมินหลัก</h3>
            <p>ควบคุมระบบทั้งหมด เพิ่ม-ลบครู วิชา นักเรียน ผ่านหน้า Dashboard และ Discord Bot ได้ตลอดเวลา</p>
        </div>
        <div class="feat-card glass reveal" style="text-align:center;">
            <div style="font-size:44px; margin-bottom:12px;">🛡️</div>
            <h3 style="color:#2563eb;">ตรวจสอบได้ทุกรอบ</h3>
            <p>แอดมินเห็น Log การเช็กชื่อทุกรอบ สามารถลบรายการซ้ำ แก้ไขข้อผิดพลาด และยืนยันข้อมูลได้ทันที</p>
        </div>
        <div class="feat-card glass reveal" style="text-align:center;">
            <div style="font-size:44px; margin-bottom:12px;">⚡</div>
            <h3 style="color:#059669;">ตอบสนองไว</h3>
            <p>มีปัญหาส่ง DM มาได้เลย ไม่ว่าจะลืมรหัส เพิ่มนักเรียนใหม่ หรือต้องการสร้างวิชาเพิ่ม แอดมินพร้อมช่วย</p>
        </div>
        <div class="feat-card glass reveal" style="text-align:center;">
            <div style="font-size:44px; margin-bottom:12px;">📋</div>
            <h3 style="color:#7c3aed;">ข้อมูลปลอดภัย</h3>
            <p>ข้อมูลนักเรียนและประวัติเช็กชื่อทุกรอบถูกเก็บในฐานข้อมูล SQLite ที่แอดมินดูแลอยู่ ไม่มีสูญหายแน่นอน</p>
        </div>
        <div class="feat-card glass reveal" style="text-align:center;">
            <div style="font-size:44px; margin-bottom:12px;">🔧</div>
            <h3 style="color:#ea580c;">อัปเดตระบบต่อเนื่อง</h3>
            <p>แอดมินพัฒนาฟีเจอร์ใหม่และแก้ไขปัญหาอย่างต่อเนื่อง ระบบจะดีขึ้นเรื่อยๆ โดยไม่มีค่าใช้จ่ายเพิ่ม</p>
        </div>
        <div class="feat-card glass reveal" style="text-align:center;">
            <div style="font-size:44px; margin-bottom:12px;">📊</div>
            <h3 style="color:#db2777;">รายงานสรุปตามขอ</h3>
            <p>ต้องการสรุปข้อมูลการเข้าเรียนเป็นรายเดือนหรือรายวิชา? ติดต่อแอดมินได้เลย จัดให้ได้ตามต้องการ</p>
        </div>
    </div>

    <div class="admin-box glass reveal">
        <div style="font-size:34px; margin-bottom:10px;">💬</div>
        <h3 style="color:#d4af37; font-size:17px; margin-bottom:8px;">ติดต่อแอดมินได้โดยตรง</h3>
        <p style="color:var(--sub); font-size:13.5px; line-height:1.7; margin-bottom:20px;">มีปัญหาการใช้งาน ต้องการเพิ่มข้อมูล หรืออยากสอบถามเรื่องระบบ<br>ส่ง DM มาได้เลยที่ Instagram ของแอดมิน ตอบเร็ว ไม่ทิ้ง</p>
        <a href="https://www.instagram.com/krit_kkstudio?igsh=aXJxdjF1NzdjMTFq" target="_blank" class="ig-pill">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
            </svg>
            @krit_kkstudio — DM ได้เลย!
        </a>
    </div>
</div>

<!-- ─── HOW IT WORKS (EXPANDED) ─── -->
<div class="section">
    <p class="section-label reveal">วิธีการใช้งาน</p>
    <h2 class="section-title reveal">เริ่มได้ใน<br><span style="color:#2563eb;">4 ขั้นตอน ไม่ยุ่งยาก</span></h2>
    <p class="section-sub reveal">ออกแบบให้ใช้งานง่ายสุดๆ ครูใหม่ก็ไม่ต้องฝึกอบรม เปิดมาก็ใช้ได้เลย</p>

    <div class="steps-wrap">
        <div class="step-row reveal">
            <div class="step-num glass" style="color:#2563eb;">1</div>
            <div class="step-body">
                <h4>ติดต่อแอดมินเพื่อขอเข้าระบบ</h4>
                <p>ส่ง DM ไปที่ Instagram <strong style="color:#d4af37;">@krit_kkstudio</strong> แจ้งชื่อสถาบัน ชื่อครู และวิชาที่ต้องการ แอดมินจะสร้างบัญชีและตั้งค่าระบบให้ภายในไม่กี่นาที ไม่ต้องสมัครเองให้วุ่นวาย</p>
            </div>
        </div>
        <div class="step-row reveal">
            <div class="step-num glass" style="color:#7c3aed;">2</div>
            <div class="step-body">
                <h4>แอดมินเซ็ตอัพวิชาและนักเรียนให้</h4>
                <p>เจ้าหน้าที่ดูแลระบบจะดำเนินการนำเข้าข้อมูลนักเรียน สร้างกลุ่มวิชา และจัดนักเรียนเข้าวิชาให้เสร็จสรรพ เพื่ออำนวยความสะดวกแก่บุคลากรทางการศึกษาในขั้นตอนนี้ รอรับ Username / Password แล้วเข้าใช้ได้เลย</p>
            </div>
        </div>
        <div class="step-row reveal">
            <div class="step-num glass" style="color:#059669;">3</div>
            <div class="step-body">
                <h4>ครู Login และเช็กชื่อบนมือถือ</h4>
                <p>เปิดเว็บบนมือถือ ล็อกอินด้วย Username / Password ที่ได้รับ กดเลือกวิชา เห็นรายชื่อนักเรียนพร้อมกัน เลือกสถานะ มา / สาย / ลา / ขาด กดยืนยันก็เสร็จ ทั้งหมดใช้เวลาไม่ถึง 2 นาที</p>
            </div>
        </div>
        <div class="step-row reveal">
            <div class="step-num glass" style="color:#d4af37;">4</div>
            <div class="step-body">
                <h4>ระบบบันทึกอัตโนมัติ ดูย้อนหลังได้ทุกเมื่อ</h4>
                <p>ทุกครั้งที่กดยืนยัน ระบบจะบันทึกข้อมูลลงฐานข้อมูลทันที พร้อมวันที่ เวลา และชื่อครูผู้บันทึก สามารถเปิดดูประวัติย้อนหลังได้ทุกรอบ และแอดมินสามารถลบรายการซ้ำหรือแก้ไขได้ตามต้องการ</p>
            </div>
        </div>
    </div>

    <div class="tips-box glass reveal">
        <h3 style="font-size:14.5px; font-weight:700; color:#0f172a; margin-bottom:16px;">💡 เคล็ดลับการใช้งาน</h3>
        <div style="display:flex; flex-direction:column; gap:12px;">
            <div style="display:flex; gap:12px; align-items:flex-start;">
                <span style="color:#d4af37; font-size:17px; flex-shrink:0;">→</span>
                <p style="font-size:13px; color:var(--sub); line-height:1.6; margin:0;">เช็กชื่อได้จากมือถือทุกเครื่อง ไม่จำกัดอุปกรณ์ เปิดเว็บบนมือถือก็ใช้ได้เลยทันที</p>
            </div>
            <div style="display:flex; gap:12px; align-items:flex-start;">
                <span style="color:#d4af37; font-size:17px; flex-shrink:0;">→</span>
                <p style="font-size:13px; color:var(--sub); line-height:1.6; margin:0;">ถ้ากดผิดสถานะ แจ้งแอดมินได้เลย สามารถลบและเช็กชื่อใหม่ได้ไม่มีปัญหา</p>
            </div>
            <div style="display:flex; gap:12px; align-items:flex-start;">
                <span style="color:#d4af37; font-size:17px; flex-shrink:0;">→</span>
                <p style="font-size:13px; color:var(--sub); line-height:1.6; margin:0;">ไม่ต้องกังวลเรื่องอินเทอร์เน็ตหลุด ระบบจะ reconnect อัตโนมัติ ข้อมูลไม่หาย</p>
            </div>
            <div style="display:flex; gap:12px; align-items:flex-start;">
                <span style="color:#d4af37; font-size:17px; flex-shrink:0;">→</span>
                <p style="font-size:13px; color:var(--sub); line-height:1.6; margin:0;">ต้องการเพิ่มนักเรียนใหม่หรือเพิ่มวิชา ติดต่อแอดมินผ่าน Instagram ได้เลย จัดให้ภายใน 5 นาที</p>
            </div>
        </div>
    </div>
</div>

<!-- ─── CTA BOTTOM ─── -->
<div class="cta-bottom">
    <h2>พร้อมยกระดับ<br><span style="color:#d4af37;">การเช็กชื่อของคุณหรือยัง?</span></h2>
    <p style="margin-bottom:28px;">เริ่มใช้งานได้เลยวันนี้ ติดต่อแอดมินเพื่อเริ่มต้น</p>
    <div style="display:flex; flex-wrap:wrap; gap:14px; justify-content:center; margin-bottom:28px;">
        <a href="/login" class="cta-pill">🚀 เข้าสู่ระบบ K-School</a>
        <a href="https://www.instagram.com/krit_kkstudio?igsh=aXJxdjF1NzdjMTFq" target="_blank" class="ig-pill">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
            </svg>
            ติดต่อแอดมิน IG
        </a>
    </div>
    <p style="font-size:11.5px; color:var(--mute); margin:0;">📩 ส่ง DM มาที่ <strong style="color:#8793a6;">@krit_kkstudio</strong> — ตอบเร็ว ไม่ทิ้ง</p>
</div>

<!-- ─── FOOTER ─── -->
<div class="footer">
    <a href="https://www.instagram.com/krit_kkstudio?igsh=aXJxdjF1NzdjMTFq" target="_blank" class="footer-ig">
        <svg width="26" height="26" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="ig-grad" x1="0%" y1="100%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#fcb045"/>
                    <stop offset="50%" style="stop-color:#fd1d1d"/>
                    <stop offset="100%" style="stop-color:#833ab4"/>
                </linearGradient>
            </defs>
            <path fill="url(#ig-grad)" d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
        </svg>
        <span style="font-size:14px; font-weight:800; letter-spacing:.4px; color:#cbd5e1;">@krit_kkstudio</span>
    </a>
    <div class="footer-brand">KK STUDIO GROUP</div>
    <div class="footer-sub">K-School Platform · ระบบเช็กชื่อดิจิทัลยุคใหม่</div>
    <div class="footer-sub" style="font-size:10px;">© 2025 KK Studio Group · All rights reserved</div>
</div>

<script>
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(el => {
            if (el.isIntersecting) el.target.classList.add('revealed');
        });
    }, { threshold: 0.12 });
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', e => {
            e.preventDefault();
            const target = document.querySelector(a.getAttribute('href'));
            if (target) target.scrollIntoView({ behavior: 'smooth' });
        });
    });
</script>
</body>
</html>
"""
# ==========================================
# 🔐 LOGIN GATEWAY & LOGOUT (WITH COOKIES)
# ==========================================

# 📱 หน้าล็อกอินสไตล์แอปมือถือ (hero ด้านบน + bottom sheet) — ดีไซน์แยกจาก STYLE_HEADER
# หมายเหตุ: เป็น string ธรรมดา (ไม่ใช่ f-string) เพื่อไม่ให้ { } ของ CSS/JS ชนกับการ interpolate ของ Python
LOGIN_STYLE = """
<link href="https://fonts.googleapis.com/css2?family=Prompt:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    html { -webkit-text-size-adjust: 100%; }
    body.lv-body {
        margin: 0; padding: 0;
        min-height: 100vh; min-height: 100dvh;
        display: block;
        background: #ececef;
        font-family: 'Prompt', 'Sarabun', 'Inter', sans-serif;
        color: #111827;
        overflow-x: hidden; overflow-y: auto;
        -webkit-tap-highlight-color: transparent;
        -webkit-font-smoothing: antialiased;
        text-rendering: optimizeLegibility;
    }

    /* ─── BACKGROUND: เทาอ่อน + ลายเส้นเฉียง + สามเหลี่ยมสีน้ำเงิน ─── */
    .lv-bg {
        position: fixed; inset: 0; z-index: -2;
        background:
            repeating-linear-gradient(118deg, rgba(255,255,255,0) 0 22px, rgba(255,255,255,0.75) 22px 24px),
            linear-gradient(180deg, #e9e9ec 0%, #f4f4f6 55%, #eeeef1 100%);
        -webkit-mask-image: none;
    }
    .lv-tri-bl { position: fixed; left: 0; bottom: 0; width: min(78vw, 340px); z-index: -1; pointer-events: none; }
    .lv-tri-tr { position: fixed; right: 0; top: 0; width: min(46vw, 190px); z-index: -1; pointer-events: none; }

    .lv-shell {
        position: relative;
        max-width: 440px; margin: 0 auto;
        padding: 0 22px calc(env(safe-area-inset-bottom, 0px) + 32px);
    }

    /* ─── TOP BAR ─── */
    .lv-topbar {
        display: flex; align-items: center; justify-content: space-between;
        padding-top: calc(env(safe-area-inset-top, 0px) + 16px);
        height: calc(env(safe-area-inset-top, 0px) + 74px);
    }
    .lv-back {
        width: 40px; height: 40px; border: 0; background: transparent; padding: 0;
        display: flex; align-items: center; justify-content: center; cursor: pointer; color: #6b7280;
    }
    .lv-back svg { width: 26px; height: 26px; }
    .lv-lang {
        width: 46px; height: 46px; border-radius: 50%; border: 0;
        background: rgba(255,255,255,0.85); color: #374151;
        font-family: inherit; font-size: 15px; font-weight: 600; cursor: pointer;
        box-shadow: 0 2px 10px rgba(15,23,42,0.08);
    }

    /* ─── LOGO ─── */
    .lv-logo-block { display: flex; flex-direction: column; align-items: center; margin: 2px 0 20px; }
    .lv-logo { height: 108px; width: auto; object-fit: contain; }
    .lv-logo-name { margin-top: 6px; font-size: 12.5px; font-weight: 500; color: #1f6b3a; }

    /* ─── CARD ─── */
    .lv-card {
        background: rgba(255,255,255,0.97);
        border-radius: 28px;
        padding: 26px 20px 22px;
        box-shadow: 0 18px 40px -22px rgba(15,23,42,0.28);
    }
    .lv-title { margin: 0 0 18px; text-align: center; font-size: 21px; font-weight: 700; color: #0b0f19; }

    /* ─── TABS ─── */
    .lv-tabs { display: flex; background: #e4e4e8; border-radius: 100px; margin-bottom: 18px; }
    .lv-tab {
        flex: 1; height: 46px; border: 0; background: transparent; border-radius: 100px;
        font-family: inherit; font-size: 15px; font-weight: 600; color: #1f2937; cursor: pointer;
        transition: background .2s, color .2s;
    }
    .lv-tab.active { background: #0a7cff; color: #fff; }

    /* ─── FIELDS (กรอบนอกคงที่ — ช่อง input ข้างในล่องหน ไม่มีกรอบ/โฟกัสริง/เงา) ─── */
    .lv-field {
        display: flex; align-items: center; gap: 12px;
        height: 54px; padding: 0 16px; margin: 0 0 14px;
        background: #fff; border: 1.5px solid #d3d6dc; border-radius: 16px;
    }
    .lv-ico { flex-shrink: 0; width: 22px; height: 22px; color: #0b0f19; display: block; }

    .lv-field input.lv-input,
    .lv-field input.lv-input:hover,
    .lv-field input.lv-input:focus,
    .lv-field input.lv-input:active,
    .lv-field input.lv-input:focus-visible {
        flex: 1; min-width: 0; width: auto !important; height: 100%;
        margin: 0 !important; padding: 0 !important;
        border: 0 !important; border-radius: 0 !important;
        outline: none !important; box-shadow: none !important;
        background: transparent !important;
        -webkit-appearance: none; appearance: none;
        font-family: inherit; font-size: 16px; font-weight: 400; color: #111827;
        caret-color: #0a7cff; letter-spacing: 0;
    }
    .lv-field input.lv-input::placeholder { color: #9ca3af; font-weight: 400; }

    /* กันกล่อง autofill ของ Chrome (สีเหลือง/ฟ้า) ที่ทำให้เห็นเป็นกรอบ */
    .lv-field input.lv-input:-webkit-autofill,
    .lv-field input.lv-input:-webkit-autofill:hover,
    .lv-field input.lv-input:-webkit-autofill:focus,
    .lv-field input.lv-input:-webkit-autofill:active {
        -webkit-box-shadow: 0 0 0 1000px #ffffff inset !important;
        box-shadow: 0 0 0 1000px #ffffff inset !important;
        -webkit-text-fill-color: #111827 !important;
        caret-color: #0a7cff;
        transition: background-color 99999s ease-out 0s;
    }

    .lv-eye {
        flex-shrink: 0; height: 26px; border: 0; background: transparent; cursor: pointer;
        padding: 0 0 0 12px; margin-left: 2px; border-left: 1.5px solid #6b7280;
        display: flex; align-items: center; color: #0b0f19;
    }
    .lv-eye svg { width: 24px; height: 24px; }

    /* ─── SELECT สถาบัน ─── */
    .lv-field select.lv-select,
    .lv-field select.lv-select:focus,
    .lv-field select.lv-select:active {
        flex: 1; min-width: 0; width: auto !important; height: 100%;
        margin: 0 !important; padding: 0 !important;
        border: 0 !important; outline: none !important; box-shadow: none !important;
        background: transparent !important;
        -webkit-appearance: none; appearance: none;
        font-family: inherit; font-size: 16px; font-weight: 400; color: #111827;
    }
    .lv-chev { flex-shrink: 0; width: 22px; height: 22px; color: #6b7280; display: block; pointer-events: none; }

    /* ─── CHECKBOX ─── */
    .lv-check { display: flex; align-items: center; gap: 10px; margin: 4px 0 16px; padding: 0 4px; font-size: 12.5px; color: #1998b8; line-height: 1.5; cursor: pointer; }
    .lv-check input[type="checkbox"] {
        -webkit-appearance: none; appearance: none;
        flex-shrink: 0; width: 24px; height: 24px; margin: 0;
        border: 2px solid #6b7280; border-radius: 6px; background: #fff; cursor: pointer;
        outline: none; transition: background .15s, border-color .15s;
    }
    .lv-check input[type="checkbox"]:checked {
        background-color: #0a7cff; border-color: #0a7cff;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='5 12.5 10 17.5 19 7'/%3E%3C/svg%3E");
        background-size: 82% 82%; background-position: center; background-repeat: no-repeat;
    }
    .lv-check a { color: #1998b8; font-weight: 700; text-decoration: none; }

    /* ─── SUBMIT ─── */
    .lv-submit {
        display: block; margin: 6px auto 0; min-width: 62%; height: 52px; padding: 0 36px;
        border: 0; border-radius: 100px;
        font-family: inherit; font-size: 17px; font-weight: 700; color: #fff;
        background: #0a7cff; box-shadow: 0 10px 22px -10px rgba(10,124,255,0.65);
        cursor: pointer; transition: transform .12s, background .2s;
    }
    .lv-submit:disabled { background: #a9a9ae; box-shadow: none; cursor: not-allowed; }
    .lv-submit:active:not(:disabled) { transform: scale(0.97); }

    /* ─── LINKS ─── */
    .lv-link { display: block; text-align: center; margin-top: 14px; font-size: 15px; font-weight: 700; color: #1998b8; text-decoration: none; cursor: pointer; background: none; border: 0; width: 100%; font-family: inherit; padding: 0; }
    .lv-link.soft { font-weight: 500; margin-top: 10px; }
    .lv-why { display: block; text-align: center; margin-top: 18px; font-size: 12.5px; font-weight: 600; color: #6b7280; text-decoration: none; }
    .lv-footer { text-align: center; margin-top: 18px; font-size: 10px; letter-spacing: 1px; color: #9ca3af; font-weight: 600; }

    @media (max-height: 700px) {
        .lv-logo { height: 84px; }
        .lv-logo-block { margin-bottom: 14px; }
    }
</style>
"""

# 🔷 พื้นหลังสามเหลี่ยมสีน้ำเงิน (SVG วาดเอง ไม่ใช้รูป/อีโมจิ)
LOGIN_BG_SVG = """
<svg class="lv-tri-bl" viewBox="0 0 300 380" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <defs>
        <linearGradient id="lvg1" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3aa0ff"/><stop offset="1" stop-color="#0a55d6"/></linearGradient>
        <linearGradient id="lvg2" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fd0ff"/><stop offset="1" stop-color="#1b7cf0"/></linearGradient>
        <linearGradient id="lvg3" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#0b3fb8"/><stop offset="1" stop-color="#2d8cff"/></linearGradient>
    </defs>
    <polygon points="0,110 96,160 18,250" fill="url(#lvg2)" opacity="0.85"/>
    <polygon points="18,250 96,160 128,226" fill="url(#lvg1)" opacity="0.95"/>
    <polygon points="0,250 18,250 0,300" fill="url(#lvg3)"/>
    <polygon points="18,250 128,226 112,320" fill="url(#lvg3)" opacity="0.92"/>
    <polygon points="0,300 112,320 0,380" fill="url(#lvg1)"/>
    <polygon points="112,320 210,350 150,380 60,380" fill="url(#lvg2)" opacity="0.8"/>
    <polygon points="128,226 196,290 112,320" fill="url(#lvg2)" opacity="0.7"/>
    <polygon points="196,290 270,330 210,350" fill="url(#lvg1)" opacity="0.75"/>
    <polygon points="60,140 90,110 100,160" fill="#9fd8ff" opacity="0.55"/>
    <polygon points="150,260 176,240 186,272" fill="#bfe6ff" opacity="0.5"/>
</svg>
<svg class="lv-tri-tr" viewBox="0 0 160 150" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <defs>
        <linearGradient id="lvg4" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4aa8ff"/><stop offset="1" stop-color="#0a5bdc"/></linearGradient>
        <linearGradient id="lvg5" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9ad6ff"/><stop offset="1" stop-color="#2a86f2"/></linearGradient>
    </defs>
    <polygon points="160,0 160,70 104,38" fill="url(#lvg4)" opacity="0.9"/>
    <polygon points="160,0 104,38 126,0" fill="url(#lvg5)" opacity="0.85"/>
    <polygon points="104,38 160,70 118,92" fill="url(#lvg5)" opacity="0.7"/>
    <polygon points="126,0 150,0 138,14" fill="#bfe6ff" opacity="0.8"/>
    <polygon points="96,66 112,52 118,76" fill="#7cc4ff" opacity="0.6"/>
</svg>
"""

LOGIN_SCRIPT = """
<script>
    var lvMode = 'user';

    function lvSyncEye() {
        var p = document.getElementById('lvPass');
        var hidden = (p.type === 'password');
        document.getElementById('lvEyeOff').style.display = hidden ? 'block' : 'none';
        document.getElementById('lvEyeOn').style.display = hidden ? 'none' : 'block';
    }

    // แท็บ "ชื่อผู้ใช้"  : ช่อง 1 = รหัสประจำตัว/ชื่อผู้ใช้ , ช่อง 2 = รหัสผ่าน/เบอร์โทร (name เดิม)
    // แท็บ "เบอร์โทรศัพท์": ช่อง 1 = เบอร์โทร , ช่อง 2 = รหัสประจำตัว — สลับ name ให้หลังบ้านรับค่าถูกฝั่งเดิม
    function lvSetMode(mode) {
        lvMode = mode;
        document.querySelectorAll('.lv-tab').forEach(function(b){ b.classList.remove('active'); });
        document.querySelector('.lv-tab[data-mode="' + mode + '"]').classList.add('active');
        var u = document.getElementById('lvUserInput');
        var p = document.getElementById('lvPass');
        u.value = ''; p.value = '';
        if (mode === 'phone') {
            u.placeholder = 'เบอร์โทรศัพท์';
            u.type = 'tel'; u.setAttribute('inputmode', 'numeric'); u.name = 'password'; u.setAttribute('autocomplete', 'tel');
            p.placeholder = 'รหัสประจำตัวนักเรียน';
            p.type = 'text'; p.name = 'username'; p.setAttribute('autocomplete', 'off');
        } else {
            u.placeholder = 'รหัสประจำตัว หรือ ชื่อผู้ใช้งาน';
            u.type = 'text'; u.removeAttribute('inputmode'); u.name = 'username'; u.setAttribute('autocomplete', 'username');
            p.placeholder = 'รหัสผ่าน';
            p.type = 'password'; p.name = 'password'; p.setAttribute('autocomplete', 'current-password');
        }
        lvSyncEye();
    }

    function lvTogglePw() {
        var p = document.getElementById('lvPass');
        p.type = (p.type === 'password') ? 'text' : 'password';
        lvSyncEye();
    }

    function lvValidate() {
        document.getElementById('lvSubmit').disabled = !document.getElementById('lvTerms').checked;
    }

    function lvToast() {
        smartAlert({
            title: 'เร็วๆ นี้',
            message: 'ระบบภาษาอังกฤษ (English version) กำลังจะเปิดให้ใช้งานเร็วๆ นี้',
            type: 'info'
        });
    }

    function lvComingSoon(featureName) {
        smartAlert({
            title: 'เร็วๆ นี้',
            message: featureName + ' กำลังอยู่ระหว่างการพัฒนา เร็วๆ นี้จะเปิดให้ใช้งานครับ',
            type: 'info'
        });
    }

    function lvGuide() {
        smartAlert({
            title: 'คำแนะนำการเข้าสู่ระบบ',
            message: '<b>นักเรียน:</b> กรอกรหัสประจำตัว และเบอร์โทรศัพท์ที่ลงทะเบียนไว้ (แท็บ "เบอร์โทรศัพท์" ให้กรอกเบอร์ก่อน แล้วตามด้วยรหัสประจำตัว)<br><br><b>ครู / แอดมิน:</b> กรอกชื่อผู้ใช้งานและรหัสผ่านตามปกติ',
            type: 'info'
        });
    }

    window.addEventListener('pageshow', function() { lvValidate(); lvSyncEye(); });
</script>
"""

PAGE_LOADER = """
<div id="ktechLoader" class="ktech-loader">
    <div class="ktech-loader-rings">
        <div class="ktech-ring ktech-ring-1"></div>
        <div class="ktech-ring ktech-ring-2"></div>
        <div class="ktech-ring ktech-ring-3"></div>
        <div class="ktech-orbit-dot"></div>
        <img src="data:image/jpeg;base64,__KTECH_ICON_B64__" class="ktech-loader-icon" alt="K-Tech Interactive">
    </div>
    <div class="ktech-loader-text">
        <span>K</span><span>-</span><span>T</span><span>e</span><span>c</span><span>h</span><span class="ktech-grey">i</span><span class="ktech-grey">n</span><span class="ktech-grey">t</span><span class="ktech-grey">e</span><span class="ktech-grey">r</span><span class="ktech-grey">a</span><span class="ktech-grey">c</span><span class="ktech-grey">t</span><span class="ktech-grey">i</span><span class="ktech-grey">v</span><span class="ktech-grey">e</span>
    </div>
    <div class="ktech-loader-bar"><div class="ktech-loader-bar-fill"></div></div>
    <div class="ktech-loader-sub">กำลังโหลดข้อมูล...</div>
</div>
<style>
.ktech-loader{position:fixed;inset:0;z-index:99999;background:radial-gradient(circle at 50% 35%,#0d3a66 0%,#0a2447 45%,#060e1f 100%);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px;transition:opacity .5s ease,visibility .5s ease;}
.ktech-loader.ktech-hide{opacity:0;visibility:hidden;pointer-events:none;}
.ktech-loader.ktech-instant{transition:none;}
.ktech-loader-rings{position:relative;width:140px;height:140px;display:flex;align-items:center;justify-content:center;}
.ktech-ring{position:absolute;border-radius:50%;border:2px solid transparent;}
.ktech-ring-1{width:140px;height:140px;border-top-color:#60a5fa;border-right-color:#60a5fa33;animation:ktechSpin 1.6s linear infinite;}
.ktech-ring-2{width:112px;height:112px;border-bottom-color:#93c5fd;border-left-color:#93c5fd22;animation:ktechSpin 2.2s linear infinite reverse;}
.ktech-ring-3{width:150px;height:150px;border:1px dashed #3b82f655;animation:ktechSpin 6s linear infinite;}
.ktech-orbit-dot{position:absolute;width:140px;height:140px;animation:ktechSpin 1.6s linear infinite;}
.ktech-orbit-dot::after{content:'';position:absolute;top:-3px;left:50%;width:7px;height:7px;margin-left:-3.5px;background:#bfdbfe;border-radius:50%;box-shadow:0 0 10px 2px #60a5fa;}
.ktech-loader-icon{width:78px;height:78px;object-fit:contain;border-radius:18px;box-shadow:0 0 28px 4px rgba(96,165,250,.45);animation:ktechPulse 1.8s ease-in-out infinite;background:#0a4a7a;padding:6px;}
@keyframes ktechSpin{to{transform:rotate(360deg);}}
@keyframes ktechPulse{0%,100%{transform:scale(1);filter:brightness(1);}50%{transform:scale(1.06);filter:brightness(1.18);}}
.ktech-loader-text{font-family:'Segoe UI',sans-serif;font-size:22px;font-weight:800;letter-spacing:.5px;color:#fff;display:flex;}
.ktech-loader-text .ktech-grey{color:#94a3b8;font-weight:600;}
.ktech-loader-text span{opacity:0;animation:ktechFadeIn .4s ease forwards;}
.ktech-loader-text span:nth-child(1){animation-delay:.05s}.ktech-loader-text span:nth-child(2){animation-delay:.1s}.ktech-loader-text span:nth-child(3){animation-delay:.15s}.ktech-loader-text span:nth-child(4){animation-delay:.2s}.ktech-loader-text span:nth-child(5){animation-delay:.25s}.ktech-loader-text span:nth-child(6){animation-delay:.3s}.ktech-loader-text span:nth-child(7){animation-delay:.35s}.ktech-loader-text span:nth-child(8){animation-delay:.4s}.ktech-loader-text span:nth-child(9){animation-delay:.45s}.ktech-loader-text span:nth-child(10){animation-delay:.5s}.ktech-loader-text span:nth-child(11){animation-delay:.55s}.ktech-loader-text span:nth-child(12){animation-delay:.6s}.ktech-loader-text span:nth-child(13){animation-delay:.65s}.ktech-loader-text span:nth-child(14){animation-delay:.7s}.ktech-loader-text span:nth-child(15){animation-delay:.75s}.ktech-loader-text span:nth-child(16){animation-delay:.8s}
@keyframes ktechFadeIn{to{opacity:1;}}
.ktech-loader-bar{width:180px;height:4px;border-radius:4px;background:#1e3a5f;overflow:hidden;}
.ktech-loader-bar-fill{width:40%;height:100%;border-radius:4px;background:linear-gradient(90deg,#3b82f6,#93c5fd);animation:ktechBar 1.1s ease-in-out infinite;}
@keyframes ktechBar{0%{transform:translateX(-100%);}100%{transform:translateX(350%);}}
.ktech-loader-sub{font-family:'Segoe UI',sans-serif;font-size:12.5px;color:#64748b;letter-spacing:.3px;}
</style>
<script>
(function(){
    function ktechHide(){
        var el=document.getElementById('ktechLoader');
        if(!el) return;
        el.classList.remove('ktech-instant');
        el.classList.add('ktech-hide');
    }
    function ktechShowInstant(){
        var el=document.getElementById('ktechLoader');
        if(!el) return;
        el.classList.add('ktech-instant');
        el.classList.remove('ktech-hide');
    }
    var ktechStart=Date.now();
    window.addEventListener('load', function(){
        var elapsed=Date.now()-ktechStart;
        var wait=Math.max(0, 450-elapsed);
        setTimeout(ktechHide, wait);
    });
    setTimeout(ktechHide, 4000);

    // ── แตะลิงก์/กดส่งฟอร์มแล้วขึ้นหน้าโหลดทันที ไม่ต้องรอหน้าใหม่โหลดเสร็จก่อนค่อยขึ้น ──
    document.addEventListener('click', function(ev){
        if(ev.defaultPrevented || ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
        var a = ev.target.closest('a[href]');
        if(!a || a.target === '_blank' || a.hasAttribute('download') || a.hasAttribute('data-no-loader')) return;
        var href = a.getAttribute('href') || '';
        if(!href || href.charAt(0) === '#' || /^(javascript:|mailto:|tel:)/i.test(href)) return;
        try {
            var url = new URL(href, window.location.href);
            if(url.origin !== window.location.origin) return;
        } catch(e) { return; }
        ktechShowInstant();
        ev.preventDefault();
        setTimeout(function(){ window.location.href = href; }, 90);
    }, true);

    document.addEventListener('submit', function(ev){
        if(ev.defaultPrevented) return;
        var f = ev.target;
        if(!(f instanceof HTMLFormElement) || f.target === '_blank' || f.hasAttribute('data-no-loader')) return;
        ktechShowInstant();
    }, true);
})();
</script>
""".replace("__KTECH_ICON_B64__", "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")

@app.get("/login", response_class=HTMLResponse)
async def login_page(user_session: Optional[str] = Cookie(None)):
    if user_session == "admin":
        return RedirectResponse(url="/admin/dashboard", status_code=303)

    m_cfg = get_maintenance_status()
    if m_cfg["is_active"] == 1:
        return generate_maintenance_html(m_cfg["mode_type"])

    if user_session and user_session.startswith("teacher_"):
        teacher_username = user_session.replace("teacher_", "")
        return RedirectResponse(url=f"/app/dashboard?user={teacher_username}", status_code=303)

    if user_session and user_session.startswith("student_"):
        return RedirectResponse(url="/student/dashboard", status_code=303)

    return f"""
    <html lang="th">{STYLE_HEADER}
    {LOGIN_STYLE}
    <body class="lv-body">
        {PAGE_LOADER}
        <div class="lv-bg"></div>
        {LOGIN_BG_SVG}

        <div class="lv-shell">

            <div class="lv-topbar">
                <button type="button" class="lv-back" onclick="history.length>1?history.back():location.href='/'" aria-label="ย้อนกลับ">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3.5 6.5 12 15 20.5"/></svg>
                </button>
                <button type="button" class="lv-lang" onclick="lvToast()">EN</button>
            </div>

            <div class="lv-logo-block">
                <img src="{LOGO_URL}" class="lv-logo" alt="K-School">
                <div class="lv-logo-name">วิทยาลัยนาฏศิลป</div>
            </div>

            <div class="lv-card">
                <h1 class="lv-title">ยินดีต้อนรับ</h1>

                <div class="lv-tabs">
                    <button type="button" class="lv-tab active" data-mode="user" onclick="lvSetMode('user')">ชื่อผู้ใช้</button>
                    <button type="button" class="lv-tab" data-mode="phone" onclick="lvSetMode('phone')">เบอร์โทรศัพท์</button>
                </div>

                <form action="/login" method="post" id="lvForm">
                    <div class="lv-field">
                        <svg class="lv-ico" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 100 20 10 10 0 000-20zm0 4.1a3.4 3.4 0 110 6.8 3.4 3.4 0 010-6.8zm0 13.3a8 8 0 01-6.2-2.9c.2-2.1 4.1-3.2 6.2-3.2s6 1.1 6.2 3.2a8 8 0 01-6.2 2.9z"/></svg>
                        <input class="lv-input" type="text" name="username" id="lvUserInput" placeholder="รหัสประจำตัว หรือ ชื่อผู้ใช้งาน" required autocomplete="username" autocapitalize="off" autocorrect="off" spellcheck="false">
                    </div>

                    <div class="lv-field">
                        <svg class="lv-ico" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M8 6.5a5.5 5.5 0 015.3 4H23v4.6h-3.2v2.6h-3.6v-2.6h-2.9A5.5 5.5 0 118 6.5zm0 3.2a2.3 2.3 0 100 4.6 2.3 2.3 0 000-4.6z"/></svg>
                        <input class="lv-input" type="password" name="password" id="lvPass" placeholder="รหัสผ่าน" required autocomplete="current-password" autocapitalize="off" autocorrect="off" spellcheck="false">
                        <button type="button" class="lv-eye" onclick="lvTogglePw()" aria-label="แสดง/ซ่อนรหัสผ่าน">
                            <svg id="lvEyeOff" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M1.5 12S5.5 5 12 5s10.5 7 10.5 7-4 7-10.5 7S1.5 12 1.5 12z"/><circle cx="12" cy="12" r="3"/><line x1="3.5" y1="3.5" x2="20.5" y2="20.5"/></svg>
                            <svg id="lvEyeOn" style="display:none;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M1.5 12S5.5 5 12 5s10.5 7 10.5 7-4 7-10.5 7S1.5 12 1.5 12z"/><circle cx="12" cy="12" r="3"/></svg>
                        </button>
                    </div>

                    <div class="lv-field">
                        <svg class="lv-ico" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M9 3h6a1 1 0 011 1v2h4a2 2 0 012 2v3H2V8a2 2 0 012-2h4V4a1 1 0 011-1zm1.5 2v1h3V5h-3zM2 13h8v1.6h4V13h8v6a2 2 0 01-2 2H4a2 2 0 01-2-2v-6z"/></svg>
                        <select class="lv-select" aria-label="สถาบัน">
                            <option>วิทยาลัยนาฏศิลป</option>
                        </select>
                        <svg class="lv-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>
                    </div>

                    <label class="lv-check">
                        <input type="checkbox" id="lvTerms" onchange="lvValidate()">
                        <span>ยอมรับ <a href="/terms" target="_blank">ข้อกำหนดและเงื่อนไข</a> และ <a href="/privacy" target="_blank">นโยบายความเป็นส่วนตัว</a></span>
                    </label>

                    <button type="submit" class="lv-submit" id="lvSubmit" disabled>เข้าสู่ระบบ</button>
                </form>

                <button type="button" class="lv-link soft" onclick="lvComingSoon('ระบบลืมรหัสผ่าน')">ลืมรหัสผ่าน</button>
                <button type="button" class="lv-link" onclick="lvComingSoon('ระบบลงทะเบียนสำหรับผู้ปกครอง')">ลงทะเบียนเข้าใช้งานสำหรับผู้ปกครอง</button>
                <button type="button" class="lv-link" onclick="lvGuide()">คำแนะนำการเข้าสู่ระบบ</button>
            </div>

            <a href="/why-us" class="lv-why">ทำไมต้องเลือก K-School</a>
            <div class="lv-footer">KK STUDIO GROUP</div>
        </div>
        {LOGIN_SCRIPT}
    </body></html>
    """

@app.post("/login")
async def process_login(response: Response, username: str = Form(...), password: str = Form(...)):
    username = username.strip()
    password = password.strip()

    if username == ADMIN_USER and password == ADMIN_PASS:
        add_log(f"Admin เข้าสู่ระบบสำเร็จ")
        resp = RedirectResponse(url="/admin/dashboard", status_code=303)
        resp.set_cookie(key="user_session", value="admin", max_age=COOKIE_MAX_AGE, httponly=True)
        return resp
        
    m_cfg = get_maintenance_status()
    if m_cfg["is_active"] == 1:
        return HTMLResponse(generate_maintenance_html(m_cfg["mode_type"]))

    try:
        conn = sqlite3.connect('attendance_pro.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM teachers WHERE username = ? AND password = ?", (username, password))
        teacher = cursor.fetchone()

        student_row = None
        if not teacher:
            # 🎒 ลองเทียบเป็นบัญชีนักเรียน (รหัสประจำตัว + เบอร์โทร) — ใช้ช่องกรอกเดียวกับด้านบน
            cursor.execute("SELECT uid FROM student_accounts WHERE student_id = ? AND phone = ?", (username, password))
            student_row = cursor.fetchone()
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"❌ Login DB Error: {e}")
        return alert_redirect("ระบบฐานข้อมูลยังไม่พร้อมใช้งาน กรุณาลองใหม่อีกครั้ง หรือติดต่อผู้ดูแลระบบ (แนะนำให้รีสตาร์ทเซิร์ฟเวอร์)", type="error")

    if teacher:
        add_log(f"ครู {teacher[0]} เข้าสู่ระบบสำเร็จ")
        resp = RedirectResponse(url=f"/app/dashboard?user={urllib.parse.quote(teacher[0])}", status_code=303)
        resp.set_cookie(key="user_session", value=f"teacher_{urllib.parse.quote(teacher[0])}", max_age=COOKIE_MAX_AGE, httponly=True)
        return resp

    if student_row:
        uid = student_row[0]
        all_students = get_sorted_master_students()
        target = next((s for s in all_students if s['uid'] == uid), None)
        if not target:
            return alert_redirect("ไม่พบข้อมูลนักเรียนในทะเบียนหลัก กรุณาติดต่อผู้ดูแลระบบ", type="error")
        add_log(f"นักเรียน {target['name']} ({target['class']}) เข้าสู่ระบบสำเร็จ")
        resp = RedirectResponse(url="/student/dashboard", status_code=303)
        resp.set_cookie(key="user_session", value=f"student_{urllib.parse.quote(uid)}", max_age=COOKIE_MAX_AGE, httponly=True)
        return resp

    return alert_redirect("ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง กรุณาตรวจสอบอีกครั้ง", type="error")

@app.get("/logout")
async def logout(response: Response):
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie(key="user_session")
    return resp

# ==========================================
# 🎒 [STUDENT LOGIN — รหัสประจำตัว + เบอร์โทร ไม่ใช้รหัสผ่าน]
# ==========================================
# 🎒 [STUDENT LOGIN — รวมเข้ากับหน้า /login หลักแล้ว]
# ==========================================
# หมายเหตุ: นักเรียนล็อกอินผ่านฟอร์มเดียวกับครู/แอดมินที่ /login แล้ว
# (กรอกรหัสประจำตัวในช่อง "ชื่อผู้ใช้งาน" และเบอร์โทรในช่อง "รหัสผ่าน")
# route นี้เก็บไว้เผื่อมีลิงก์เก่าค้าง จะ redirect ไปหน้า /login ให้อัตโนมัติ

@app.get("/student/login")
async def student_login_page(user_session: Optional[str] = Cookie(None)):
    if user_session and user_session.startswith("student_"):
        return RedirectResponse(url="/student/dashboard", status_code=303)
    return RedirectResponse(url="/login", status_code=303)

@app.get("/student/dashboard", response_class=HTMLResponse)
async def student_dashboard(user_session: Optional[str] = Cookie(None)):
    if not user_session or not user_session.startswith("student_"):
        return RedirectResponse(url="/login", status_code=303)
    m_cfg = get_maintenance_status()
    if m_cfg["is_active"] == 1:
        return generate_maintenance_html(m_cfg["mode_type"])

    uid = urllib.parse.unquote(user_session.replace("student_", "", 1))
    all_students = get_sorted_master_students()
    me = next((s for s in all_students if s['uid'] == uid), None)
    if not me:
        resp = RedirectResponse(url="/login", status_code=303)
        resp.delete_cookie(key="user_session")
        return resp

    # 🖼️ รูปโปรไฟล์ (แอดมิน/หัวหน้าระดับ/ฝ่ายกิจการ เป็นผู้ตั้งให้)
    conn0 = sqlite3.connect('attendance_pro.db')
    cursor0 = conn0.cursor()
    cursor0.execute("SELECT photo_url FROM student_accounts WHERE uid = ?", (uid,))
    photo_row = cursor0.fetchone()
    conn0.close()
    my_photo_url = photo_row[0] if photo_row and photo_row[0] else ""
    avatar_html = f'<img src="{my_photo_url}" style="width:56px;height:56px;border-radius:50%;object-fit:cover;border:2px solid rgba(255,255,255,0.5);">' if my_photo_url else '<div class="ah-avatar">🎒</div>'

    # 🎖️ คะแนนความประพฤติ
    summary = next((s for s in get_conduct_summary() if s['uid'] == uid), None)
    score_now = summary['score'] if summary else CONDUCT_START_SCORE
    history = get_conduct_history(uid)[:5]
    history_rows = "".join([
        f"""<tr><td style="font-size:11.5px;color:#64748b;white-space:nowrap;">{h['created_at']}</td>
            <td style="text-align:left;">{h['reason']}<br><span style="font-size:10px;color:#94a3b8;">โดย: {h['recorded_by']}</span></td>
            <td style="color:{'#15803d' if h['points']>=0 else '#b91c1c'};font-weight:800;">{'+' if h['points']>=0 else ''}{h['points']}</td></tr>"""
        for h in history
    ])

    # 🗓️ ประวัติการเช็กชื่อล่าสุด
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT group_name, status, date FROM attendance_logs
        WHERE student_name = ? AND classroom = ? ORDER BY log_id DESC LIMIT 8""", (me['name'], me['class']))
    attendance_rows_raw = cursor.fetchall()
    # 📋 คำร้องขอลาของฉัน
    cursor.execute("""SELECT group_name, leave_date, status, reason FROM leave_requests
        WHERE student_name = ? AND student_no = ? ORDER BY req_id DESC LIMIT 5""", (me['name'], me['no']))
    leave_rows_raw = cursor.fetchall()
    conn.close()

    status_color = {"มา": "#15803d", "สาย": "#d97706", "ขาด": "#b91c1c", "ลา": "#2563eb"}
    attendance_rows = "".join([
        f"""<tr><td style="text-align:left;">{r[0]}</td>
            <td style="color:{status_color.get(r[1], '#334155')};font-weight:800;">{r[1]}</td>
            <td style="font-size:12px;color:#64748b;">{r[2]}</td></tr>"""
        for r in attendance_rows_raw
    ])

    leave_badge = {"pending": "⏳ รออนุมัติ", "approved": "✅ อนุมัติแล้ว", "rejected": "❌ ปฏิเสธ"}
    leave_rows = "".join([
        f"""<tr><td style="text-align:left;">{r[0]}<br><span style="font-size:11px;color:#94a3b8;">{r[1]}</span></td>
            <td style="font-size:12px;">{leave_badge.get(r[2], r[2])}</td></tr>"""
        for r in leave_rows_raw
    ])

    fg, bg, border = ("#10b981", "#f0fdf4", "#bbf7d0") if score_now >= 80 else ("#d97706", "#fffbeb", "#fde68a") if score_now >= 50 else ("#ef4444", "#fef2f2", "#fecaca")

    conn2 = sqlite3.connect('attendance_pro.db')
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT COUNT(*) FROM announcements WHERE is_active=1")
    active_announcements = cursor2.fetchone()[0]
    conn2.close()

    def badge(n):
        return f'<span class="ah-badge">{n}</span>' if n > 0 else ""

    # SVG Icons สำหรับ menu grid
    def svg_icon(path_d, color="#4f46e5", bg="#eef2ff"):
        return f'<div class="ah-cell-icon-wrap" style="background:{bg}; color:{color};"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{path_d}</svg></div>'

    icon_activity = svg_icon('<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>', "#7c3aed", "#f5f3ff")
    icon_classroom = svg_icon('<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/>', "#0369a1", "#e0f2fe")
    icon_homework = svg_icon('<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>', "#0f766e", "#f0fdfa")
    icon_care = svg_icon('<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>', "#b45309", "#fffbeb")
    icon_payment = svg_icon('<rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/>', "#0369a1", "#dbeafe")
    icon_grades = svg_icon('<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>', "#15803d", "#f0fdf4")
    icon_health = svg_icon('<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>', "#dc2626", "#fef2f2")
    icon_timetable = svg_icon('<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>', "#7c3aed", "#f5f3ff")
    icon_report = svg_icon('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>', "#0369a1", "#dbeafe")
    icon_news_big = '<svg viewBox="0 0 24 24" width="52" height="52" fill="none" stroke="rgba(255,255,255,0.9)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8z"/></svg>'
    icon_calendar_sm = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#1d4ed8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>'
    icon_checkin_big = '<svg viewBox="0 0 24 24" width="52" height="52" fill="none" stroke="rgba(255,255,255,0.9)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>'
    icon_leave_sm = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#0369a1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>'

    # score ring color
    score_ring_style = f"background:{bg};color:{fg};border:3px solid {border};"
    score_label = "ดีเยี่ยม" if score_now >= 80 else "พอใช้" if score_now >= 50 else "ต้องปรับปรุง"

    return f"""
    <html>{STYLE_HEADER}
    {ADMIN_HOME_STYLE}
    <body class="ah-body">
        {PAGE_LOADER}
        <!-- ── Profile Hero ── -->
        <div class="ah-profile">
            <div class="ah-top-row">
                <div class="ah-brand">K-School</div>
                <div class="ah-top-icons">
                    <a href="/student/profile" class="ah-icon-btn" aria-label="โปรไฟล์">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                    </a>
                    <a href="/app/notifications" class="ah-icon-btn" aria-label="แจ้งเตือน">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
                        {badge(active_announcements)}
                    </a>
                </div>
            </div>
            <div class="ah-who">
                {avatar_html}
                <div>
                    <h1>สวัสดี, {me['name']}</h1>
                    <p>{me['class']} · เลขที่ {me['no']}</p>
                </div>
            </div>
            <div class="ah-inst">
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>
                วิทยาลัยนาฏศิลป
            </div>
        </div>

        <div class="ah-wrap">
            <!-- ── ประกาศ ── -->
            <div id="announcement-section" style="margin-bottom:16px; display:none;">
                <div id="announcement-list"></div>
            </div>
            <script>
                async function loadAnnouncements() {{
                    try {{
                        const resp = await fetch('/api/announcements');
                        const data = await resp.json();
                        if (data && data.length > 0) {{
                            document.getElementById('announcement-section').style.display = 'block';
                            const list = document.getElementById('announcement-list');
                            const cfg = {{normal:{{cls:'normal',ic:'📣',tc:'#1e40af'}}, important:{{cls:'important',ic:'⚠️',tc:'#92400e'}}, urgent:{{cls:'urgent',ic:'🚨',tc:'#991b1b'}}}};
                            data.forEach(a => {{
                                const c = cfg[a.level] || cfg.normal;
                                const div = document.createElement('div');
                                div.className = `ah-announce ${{c.cls}}`;
                                div.innerHTML = `<div class="ah-announce-title" style="color:${{c.tc}}">${{c.ic}} ${{a.title}}</div><div class="ah-announce-body">${{a.body}}</div>`;
                                list.appendChild(div);
                            }});
                        }}
                    }} catch (e) {{}}
                }}
                loadAnnouncements();
            </script>

            <!-- ── Big Tiles: ข่าวสาร + ปฏิทิน ── -->
            <div class="ah-row2">
                <a href="/app/notifications" class="ah-tile-big">
                    <div class="ah-tile-bg-icon">{icon_news_big}</div>
                    <div class="ah-tile-pill">ประกาศล่าสุด</div>
                    <span class="ah-tile-label">ข่าวสาร<br>และประกาศ</span>
                </a>
                <a href="/coming_soon?back=/student/dashboard" class="ah-tile">
                    <div class="ah-tile-icon-wrap" style="background:#dbeafe;">{icon_calendar_sm}</div>
                    <span class="ah-tile-label">ปฏิทิน</span>
                </a>
            </div>

            <!-- ── คะแนนความประพฤติ ── -->
            <div class="ah-score-card">
                <div class="ah-score-ring" style="{score_ring_style}"><span data-live-score>{score_now}</span></div>
                <div class="ah-score-info">
                    <div class="lbl">คะแนนความประพฤติ</div>
                    <div class="val" style="color:{fg};">{score_now} <span style="font-size:14px;color:#94a3b8;">/ 100</span></div>
                    <div class="sub">สถานะ: <strong style="color:{fg};">{score_label}</strong></div>
                </div>
            </div>

            <!-- ── เมนูหลัก 3x3 ── -->
            <div class="ah-section-label">เมนูหลัก</div>
            <div class="ah-grid3">
                <a href="/coming_soon?back=/student/dashboard" class="ah-cell">
                    {icon_activity}<span class="ah-cell-label">กิจกรรม</span>
                </a>
                <a href="/coming_soon?back=/student/dashboard" class="ah-cell">
                    {icon_classroom}<span class="ah-cell-label">ห้องเรียน</span>
                </a>
                <a href="/student/homework" class="ah-cell">
                    {icon_homework}<span class="ah-cell-label">การบ้าน</span>
                </a>
                <a href="/student/care" class="ah-cell">
                    {icon_care}<span class="ah-cell-label">ดูแลนักเรียน</span>
                </a>
                <a href="/student/inspection" class="ah-cell">
                    <div class="ah-cell-icon-wrap" style="background:#ecfdf5;color:#047857;"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg></div><span class="ah-cell-label">ตรวจระเบียบ</span>
                </a>
                <a href="/student/payments" class="ah-cell">
                    {icon_payment}<span class="ah-cell-label">ชำระเงิน</span>
                </a>
                <a href="/student/grades" class="ah-cell">
                    {icon_grades}<span class="ah-cell-label">ผลการเรียน</span>
                </a>
                <a href="/coming_soon?back=/student/dashboard" class="ah-cell">
                    {icon_health}<span class="ah-cell-label">ข้อมูลสุขภาพ</span>
                </a>
                <a href="/student/timetable" class="ah-cell">
                    {icon_timetable}<span class="ah-cell-label">ตารางเรียน</span>
                </a>
                <a href="/student/grades" class="ah-cell">
                    {icon_report}<span class="ah-cell-label">รายงานคะแนนเก็บ</span>
                </a>
            </div>

            <!-- ── Big Tiles: เช็กชื่อ + ยื่นคำร้อง ── -->
            <div class="ah-section-label">การเข้าเรียน</div>
            <div class="ah-row2">
                <a href="/checkin" class="ah-tile-big" style="background:linear-gradient(135deg,#0f766e,#0d9488);">
                    <div class="ah-tile-bg-icon">{icon_checkin_big}</div>
                    <div class="ah-tile-pill">OTP ใช้ครั้งเดียว</div>
                    <span class="ah-tile-label">เช็กชื่อ<br>ด้วย OTP</span>
                </a>
                <a href="/leave" class="ah-tile">
                    <div class="ah-tile-icon-wrap" style="background:#dbeafe;">{icon_leave_sm}</div>
                    <span class="ah-tile-label">ยื่นคำร้องลา</span>
                </a>
            </div>

            <!-- ── ประวัติเช็กชื่อ ── -->
            <div class="ah-section-title">ประวัติการเช็กชื่อล่าสุด</div>
            <div class="ah-table-wrap" style="overflow-x:auto;">
                <table><thead><tr><th style="text-align:left;">วิชา</th><th>สถานะ</th><th>วันที่</th></tr></thead>
                <tbody>{attendance_rows if attendance_rows else "<tr><td colspan='3' style='color:#94a3b8;text-align:center;padding:16px 0;'>ยังไม่มีประวัติ</td></tr>"}</tbody></table>
            </div>

            <!-- ── คำร้องลา ── -->
            <div class="ah-section-title">คำร้องลาของฉัน</div>
            <div class="ah-table-wrap" style="overflow-x:auto;">
                <table><thead><tr><th style="text-align:left;">รายการ</th><th>สถานะ</th></tr></thead>
                <tbody>{leave_rows if leave_rows else "<tr><td colspan='2' style='color:#94a3b8;text-align:center;padding:16px 0;'>ยังไม่มีคำร้อง</td></tr>"}</tbody></table>
            </div>

            <!-- ── ประวัติความประพฤติ ── -->
            <div class="ah-section-title">ประวัติคะแนนความประพฤติ</div>
            <div class="ah-table-wrap" style="overflow-x:auto;">
                <table><thead><tr><th>วันที่</th><th style="text-align:left;">เหตุผล</th><th>คะแนน</th></tr></thead>
                <tbody>{history_rows if history_rows else "<tr><td colspan='3' style='color:#94a3b8;text-align:center;padding:16px 0;'>ยังไม่มีประวัติ</td></tr>"}</tbody></table>
            </div>

            <div class="ah-footer">powered by <span>K-Techinteractive</span></div>
        </div>

        {render_bottom_nav("home", "student")}
        {realtime_notify_script(uid)}
    </body></html>
    """

@app.get("/student/profile", response_class=HTMLResponse)
async def student_profile_page(user_session: Optional[str] = Cookie(None)):
    """👤 หน้าโปรไฟล์นักเรียน — ข้อมูลส่วนตัว + ทางลัดที่เกี่ยวข้อง + ออกจากระบบ"""
    if not user_session or not user_session.startswith("student_"):
        return RedirectResponse(url="/login", status_code=303)
    uid = urllib.parse.unquote(user_session.replace("student_", "", 1))
    all_students = get_sorted_master_students()
    me = next((s for s in all_students if s['uid'] == uid), None)
    if not me:
        resp = RedirectResponse(url="/login", status_code=303)
        resp.delete_cookie(key="user_session")
        return resp

    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT photo_url FROM student_accounts WHERE uid = ?", (uid,))
    photo_row = cursor.fetchone()
    conn.close()
    my_photo_url = photo_row[0] if photo_row and photo_row[0] else ""
    avatar_html = f'<img src="{my_photo_url}" style="width:76px;height:76px;border-radius:50%;object-fit:cover;border:3px solid rgba(255,255,255,0.5);">' if my_photo_url else '<div class="ah-avatar" style="width:76px;height:76px;font-size:32px;">🎒</div>'

    summary = next((s for s in get_conduct_summary() if s['uid'] == uid), None)
    score_now = summary['score'] if summary else CONDUCT_START_SCORE
    fg_p, bg_p, border_p = ("#10b981", "#f0fdf4", "#bbf7d0") if score_now >= 80 else ("#d97706", "#fffbeb", "#fde68a") if score_now >= 50 else ("#ef4444", "#fef2f2", "#fecaca")
    score_label_p = "ดีเยี่ยม" if score_now >= 80 else "พอใช้" if score_now >= 50 else "ต้องปรับปรุง"

    return f"""
    <html>{STYLE_HEADER}
    {ADMIN_HOME_STYLE}
    <body class="ah-body">
        <div class="ah-profile" style="text-align:center;">
            <div class="ah-top-row"><div class="ah-brand">K-School</div><div></div></div>
            <div style="display:flex;flex-direction:column;align-items:center;gap:10px;position:relative;">
                {avatar_html}
                <div>
                    <h1 style="margin:0;font-size:17px;font-weight:800;">{me['name']}</h1>
                    <p style="margin:4px 0 0;font-size:12.5px;color:rgba(255,255,255,0.65);">{me['class']} · เลขที่ {me['no']}</p>
                </div>
            </div>
            <div class="ah-inst" style="justify-content:center;margin-top:14px;">
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>
                วิทยาลัยนาฏศิลป
            </div>
        </div>
        <div class="ah-wrap">
            <div class="ah-score-card" style="margin-bottom:14px;">
                <div class="ah-score-ring" style="background:{bg_p};color:{fg_p};border:3px solid {border_p};font-size:18px;font-weight:800;"><span data-live-score>{score_now}</span></div>
                <div class="ah-score-info">
                    <div class="lbl">คะแนนความประพฤติ</div>
                    <div class="val" style="color:{fg_p};">{score_now}<span style="font-size:14px;color:#94a3b8;font-weight:500;"> / 100</span></div>
                    <div class="sub">สถานะ: <strong style="color:{fg_p};">{score_label_p}</strong></div>
                </div>
            </div>

            <div class="ah-section-label">บัญชีของฉัน</div>
            <div style="display:flex;flex-direction:column;gap:10px;margin-bottom:12px;">
                <a href="/student/grades" class="ah-cell" style="flex-direction:row;justify-content:flex-start;text-align:left;padding:14px;gap:14px;">
                    <div class="ah-cell-icon-wrap" style="background:#f0fdf4;color:#15803d;flex-shrink:0;">
                        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
                    </div>
                    <span class="ah-cell-label" style="font-size:13px;">ผลการเรียน</span>
                </a>
                <a href="/leave" class="ah-cell" style="flex-direction:row;justify-content:flex-start;text-align:left;padding:14px;gap:14px;">
                    <div class="ah-cell-icon-wrap" style="background:#dbeafe;color:#1d4ed8;flex-shrink:0;">
                        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
                    </div>
                    <span class="ah-cell-label" style="font-size:13px;">คำร้องขอลาของฉัน</span>
                </a>
                <a href="/app/notifications" class="ah-cell" style="flex-direction:row;justify-content:flex-start;text-align:left;padding:14px;gap:14px;">
                    <div class="ah-cell-icon-wrap" style="background:#fffbeb;color:#a16207;flex-shrink:0;">
                        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
                    </div>
                    <span class="ah-cell-label" style="font-size:13px;">แจ้งเตือน</span>
                </a>
                <a href="/logout" class="ah-cell" style="flex-direction:row;justify-content:flex-start;text-align:left;padding:14px;gap:14px;border-color:#fecaca;">
                    <div class="ah-cell-icon-wrap" style="background:#fef2f2;color:#b91c1c;flex-shrink:0;">
                        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16,17 21,12 16,7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                    </div>
                    <span class="ah-cell-label" style="font-size:13px;color:#b91c1c;">ออกจากระบบ</span>
                </a>
            </div>
            <div class="ah-footer">powered by <span>K-Techinteractive</span></div>
        </div>
        {render_bottom_nav("profile", "student")}
        {realtime_notify_script(uid)}
    </body></html>
    """

# ==========================================
# 🎖️ [STUDENT] ดูแลนักเรียน + คะแนนความประพฤติและเกียรติคุณ — ตามดีไซน์ที่กำหนด
# ==========================================
CARE_PAGE_STYLE = """
<style>
    body { background: var(--surface-muted); }
    .cr-header {
        display:flex; align-items:center; gap:12px; padding: calc(env(safe-area-inset-top,0px) + 16px) 16px 16px;
        background: var(--surface); border-bottom: 1px solid var(--border);
    }
    .cr-header a { font-size:20px; color: var(--navy-800); text-decoration:none; }
    .cr-header h1 { margin:0; font-size:16.5px; font-weight:800; color: var(--navy-800); flex:1; }
    .cr-profile {
        background: linear-gradient(135deg, #38bdf8, #2563eb);
        color:#fff; padding:20px 18px; display:flex; align-items:center; gap:14px;
    }
    .cr-profile img, .cr-profile .cr-avatar {
        width:64px; height:64px; border-radius:50%; object-fit:cover; border:2px solid rgba(255,255,255,0.6);
        display:flex; align-items:center; justify-content:center; font-size:26px; background:rgba(255,255,255,0.25); flex-shrink:0;
    }
    .cr-profile h2 { margin:0; font-size:15.5px; font-weight:800; }
    .cr-profile p { margin:5px 0 0; font-size:12.5px; opacity:0.95; }
    .cr-profile .cr-inst { margin-top:6px; font-size:12px; opacity:0.9; border-top:1px solid rgba(255,255,255,0.3); padding-top:6px; }
    .cr-menu { max-width:640px; margin:0 auto; padding:16px; display:flex; flex-direction:column; gap:14px; }
    .cr-btn {
        background: linear-gradient(135deg, #38bdf8, #1d4ed8);
        color:#fff; text-decoration:none; border-radius:16px; padding:20px 18px;
        display:flex; align-items:center; gap:16px; font-size:15px; font-weight:800;
        box-shadow: 0 8px 18px -8px rgba(37,99,235,0.5);
    }
    .cr-btn .cr-btn-icon { font-size:26px; flex-shrink:0; }
</style>
"""

@app.get("/student/care", response_class=HTMLResponse)
async def student_care_page(user_session: Optional[str] = Cookie(None)):
    """👨‍👩‍👧 หน้า 'ดูแลนักเรียน' มุมมองนักเรียนดูข้อมูลของตัวเอง — เมนู 3 การ์ดไล่สีฟ้า ตามดีไซน์ต้นแบบ"""
    if not user_session or not user_session.startswith("student_"):
        return RedirectResponse(url="/login", status_code=303)
    uid = urllib.parse.unquote(user_session.replace("student_", "", 1))
    me = next((s for s in get_sorted_master_students() if s['uid'] == uid), None)
    if not me:
        resp = RedirectResponse(url="/login", status_code=303)
        resp.delete_cookie(key="user_session")
        return resp

    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT photo_url FROM student_accounts WHERE uid = ?", (uid,))
    photo_row = cursor.fetchone()
    conn.close()
    my_photo_url = photo_row[0] if photo_row and photo_row[0] else ""
    avatar_html = f'<img src="{my_photo_url}">' if my_photo_url else '<div class="cr-avatar">🎒</div>'

    return f"""
    <html>{STYLE_HEADER}
    {CARE_PAGE_STYLE}
    <body>
        <div class="cr-header">
            <a href="/student/dashboard">‹</a>
            <h1>ดูแลนักเรียน</h1>
        </div>
        <div class="cr-profile">
            {avatar_html}
            <div>
                <h2>{me['name']}</h2>
                <p>ระดับชั้น {me['class']}</p>
                <div class="cr-inst">🏫 วิทยาลัยนาฏศิลป</div>
            </div>
        </div>
        <div class="cr-menu">
            <a href="/coming_soon?back=/student/care" class="cr-btn">
                <span class="cr-btn-icon">🚪</span> เช็คชื่อเข้า-ออกโรงเรียน
            </a>
            <a href="/coming_soon?back=/student/care" class="cr-btn">
                <span class="cr-btn-icon">👥</span> กิจกรรมโฮมรูม
            </a>
            <a href="/student/conduct" class="cr-btn">
                <span class="cr-btn-icon">🏅</span> คะแนนความประพฤติและเกียรติคุณ
            </a>
        </div>
        {realtime_notify_script(uid)}
    </body></html>
    """

CONDUCT_STUDENT_STYLE = """
<style>
    body { background: var(--surface-muted); }
    .cd2-header {
        display:flex; align-items:center; gap:12px; padding: calc(env(safe-area-inset-top,0px) + 16px) 16px 16px;
        background: var(--surface); border-bottom: 1px solid var(--border);
    }
    .cd2-header a { font-size:20px; color: var(--navy-800); text-decoration:none; }
    .cd2-header h1 { margin:0; font-size:15.5px; font-weight:800; color: var(--navy-800); flex:1; }
    .cd2-profile {
        background: linear-gradient(135deg, #38bdf8, #2563eb);
        color:#fff; padding:20px 18px; display:flex; align-items:center; gap:14px;
    }
    .cd2-profile img, .cd2-profile .cd2-avatar {
        width:64px; height:64px; border-radius:50%; object-fit:cover; border:2px solid rgba(255,255,255,0.6);
        display:flex; align-items:center; justify-content:center; font-size:26px; background:rgba(255,255,255,0.25); flex-shrink:0;
    }
    .cd2-profile h2 { margin:0; font-size:15.5px; font-weight:800; }
    .cd2-profile p { margin:5px 0 0; font-size:12.5px; opacity:0.95; }
    .cd2-profile .cd2-inst { margin-top:6px; font-size:12px; opacity:0.9; border-top:1px solid rgba(255,255,255,0.3); padding-top:6px; }
    .cd2-wrap { max-width:640px; margin:0 auto; padding:16px; }
    .cd2-total {
        border:1.5px solid #93c5fd; border-radius:14px; padding:14px 16px; margin-bottom:18px;
        display:flex; align-items:center; gap:12px; background:#fff;
    }
    .cd2-total-icon { font-size:26px; flex-shrink:0; }
    .cd2-total-label { font-size:13px; font-weight:700; color:#1d4ed8; }
    .cd2-total-sub { font-size:11.5px; color:#94a3b8; margin-top:2px; }
    .cd2-total-value { margin-left:auto; font-size:19px; font-weight:800; color:#1d4ed8; white-space:nowrap; }
    .cd2-date-sep { background:#f1f5f9; color:#64748b; font-size:12.5px; font-weight:700; padding:8px 12px; border-radius:8px; margin: 14px 0 8px; }
    .cd2-entry { display:flex; align-items:flex-start; gap:10px; padding:12px 4px; border-bottom:1px solid var(--border); }
    .cd2-entry-body { flex:1; min-width:0; }
    .cd2-entry-reason { font-size:13.5px; font-weight:700; color:#2563eb; margin-bottom:4px; }
    .cd2-entry-meta { font-size:11.5px; color:#64748b; margin-bottom:2px; }
    .cd2-entry-time { font-size:11.5px; color:#94a3b8; display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
    .cd2-pill-wrap { display:flex; align-items:center; gap:4px; flex-shrink:0; }
    .cd2-pill { border:1.5px solid; border-radius:8px; padding:4px 10px; font-weight:800; font-size:13px; text-align:center; min-width:44px; }
    .cd2-pill-sub { font-size:9px; font-weight:700; text-align:center; margin-top:1px; }
    .cd2-chevron { font-size:14px; color:#94a3b8; }
</style>
"""

@app.get("/student/conduct", response_class=HTMLResponse)
async def student_conduct_page(user_session: Optional[str] = Cookie(None)):
    """🏅 หน้าคะแนนความประพฤติและเกียรติคุณของนักเรียน (มุมมองอ่านอย่างเดียว) — จัดกลุ่มตามวันที่ พร้อมชื่อผู้บันทึกทุกรายการ"""
    if not user_session or not user_session.startswith("student_"):
        return RedirectResponse(url="/login", status_code=303)
    uid = urllib.parse.unquote(user_session.replace("student_", "", 1))
    me = next((s for s in get_sorted_master_students() if s['uid'] == uid), None)
    if not me:
        resp = RedirectResponse(url="/login", status_code=303)
        resp.delete_cookie(key="user_session")
        return resp

    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT photo_url FROM student_accounts WHERE uid = ?", (uid,))
    photo_row = cursor.fetchone()
    conn.close()
    my_photo_url = photo_row[0] if photo_row and photo_row[0] else ""
    avatar_html = f'<img src="{my_photo_url}">' if my_photo_url else '<div class="cd2-avatar">🎒</div>'

    summary = next((s for s in get_conduct_summary() if s['uid'] == uid), None)
    score_now = summary['score'] if summary else CONDUCT_START_SCORE
    history = get_conduct_history(uid)

    # 🗓️ จัดกลุ่มรายการตามวันที่ (created_at รูปแบบ "YYYY-MM-DD HH:MM:SS")
    entries_html = ""
    last_date = None
    for h in history:
        raw = h['created_at'] or ""
        date_part, _, time_part = raw.partition(" ")
        time_display = time_part[:5] if time_part else "-"
        if date_part and date_part != last_date:
            try:
                d = datetime.strptime(date_part, "%Y-%m-%d")
                date_label = d.strftime("%d/%m/") + str(d.year + 543)  # แสดงเป็น พ.ศ. ให้ตรงกับดีไซน์ต้นแบบ
            except ValueError:
                date_label = date_part
            entries_html += f'<div class="cd2-date-sep">{date_label}</div>'
            last_date = date_part

        is_plus = h['points'] >= 0
        pill_color = "#15803d" if is_plus else "#b91c1c"
        pill_bg = "#f0fdf4" if is_plus else "#fef2f2"
        sign = "+" if is_plus else ""
        entries_html += f"""
        <div class="cd2-entry">
            <div class="cd2-entry-body">
                <div class="cd2-entry-reason">{h['reason']}</div>
                <div class="cd2-entry-meta">โดย : {h['recorded_by']}</div>
                <div class="cd2-entry-time">🕐 {time_display} น. 📍 -</div>
            </div>
            <div class="cd2-pill-wrap">
                <div>
                    <div class="cd2-pill" style="color:{pill_color};background:{pill_bg};border-color:{pill_color};">{sign}{h['points']}</div>
                    <div class="cd2-pill-sub" style="color:{pill_color};">คะแนน</div>
                </div>
                <span class="cd2-chevron">⌄</span>
            </div>
        </div>"""

    return f"""
    <html>{STYLE_HEADER}
    {CONDUCT_STUDENT_STYLE}
    <body>
        <div class="cd2-header">
            <a href="/student/care">‹</a>
            <h1>คะแนนความประพฤติและเกียรติคุณ</h1>
        </div>
        <div class="cd2-profile">
            {avatar_html}
            <div>
                <h2>{me['name']}</h2>
                <p>ระดับชั้น {me['class']}</p>
                <div class="cd2-inst">🏫 วิทยาลัยนาฏศิลป</div>
            </div>
        </div>
        <div class="cd2-wrap">
            <div class="cd2-total">
                <span class="cd2-total-icon">🧑‍🤝‍🧑</span>
                <div>
                    <div class="cd2-total-label">คะแนนความประพฤติรวม</div>
                    <div class="cd2-total-sub">ภาคเรียนที่ 1</div>
                </div>
                <div class="cd2-total-value"><span data-live-score>{score_now}</span> คะแนน</div>
            </div>
            {entries_html if entries_html else "<p style='color:#94a3b8;text-align:center;padding:30px 0;'>ยังไม่มีประวัติคะแนนความประพฤติ</p>"}
        </div>
        {realtime_notify_script(uid)}
    </body></html>
    """

# ==========================================
# 🧭 BOTTOM NAV — 4 แท็บมาตรฐาน (โฮม / คำร้อง / ลงเวลา / โปรไฟล์) ปรับตามบทบาทผู้ใช้
# ==========================================
def render_bottom_nav(active: str, role: str, user: Optional[str] = None) -> str:
    """สร้างแถบเมนูล่างแบบ 4 แท็บ SVG icons — dashboard style"""
    uq = urllib.parse.quote(user) if user else ""
    # SVG icons สำหรับแต่ละ tab
    _icons = {
        "home": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>',
        "request": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10,9 9,9 8,9"/></svg>',
        "checkin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/></svg>',
        "profile": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    }
    if role == "student":
        tabs = [
            ("home",    "โฮม",     "home",    "/student/dashboard"),
            ("request", "คำร้อง",  "request", "/leave"),
            ("checkin", "ลงเวลา",  "checkin", "/checkin"),
            ("profile", "โปรไฟล์", "profile", "/student/profile"),
        ]
    else:  # teacher
        tabs = [
            ("home",    "โฮม",     "home",    f"/app/dashboard?user={uq}"),
            ("request", "คำร้อง",  "request", "/leave"),
            ("checkin", "ลงเวลา",  "checkin", f"/app/history?user={uq}"),
            ("profile", "โปรไฟล์", "profile", f"/teacher/profile?user={uq}"),
        ]
    items = "".join(
        f'<a href="{url}" class="ah-nav-item{" active" if key == active else ""}">'
        f'<span class="ah-nav-icon">{_icons.get(icon_key, "")}</span>'
        f'{label}<span class="ah-nav-active-dot"></span></a>'
        for key, label, icon_key, url in tabs
    )
    return f'<div class="ah-bottomnav">{items}</div>'

# ==========================================
# 👑 [ADMIN MAIN DASHBOARD & MAINTENANCE CONTROL]
# ==========================================
ADMIN_HOME_STYLE = """
<style>
    /* ============================================================
       DASHBOARD STYLE v2 — K-Techinteractive
       Clean sidebar-style dashboard adapted for mobile
    ============================================================ */
    * { box-sizing: border-box; }

    body.ah-body {
        background: #f0f4f8;
        padding-bottom: 90px;
        font-family: 'Sarabun', 'Noto Sans Thai', sans-serif;
    }

    /* ── Profile Hero ── */
    .ah-profile {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #1d4ed8 100%);
        color: #fff;
        padding: calc(env(safe-area-inset-top, 0px) + 20px) 20px 28px;
        position: relative; overflow: hidden;
    }
    .ah-profile::before {
        content: ""; position: absolute; inset: 0;
        background:
            radial-gradient(circle at 90% 20%, rgba(96,165,250,0.25) 0%, transparent 50%),
            radial-gradient(circle at 10% 80%, rgba(212,175,55,0.15) 0%, transparent 45%);
        pointer-events: none;
    }
    .ah-profile::after {
        content: ""; position: absolute; bottom: -1px; left: 0; right: 0; height: 24px;
        background: #f0f4f8;
        clip-path: ellipse(55% 100% at 50% 100%);
    }
    .ah-top-row {
        display: flex; justify-content: space-between; align-items: center;
        position: relative; margin-bottom: 18px;
    }
    .ah-brand { font-size: 11px; font-weight: 800; letter-spacing: 1.5px; color: rgba(255,255,255,0.55); text-transform: uppercase; }
    .ah-top-icons { display: flex; gap: 8px; }
    .ah-icon-btn {
        width: 36px; height: 36px; border-radius: 10px;
        background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.18);
        backdrop-filter: blur(8px);
        display: flex; align-items: center; justify-content: center;
        color: #fff; text-decoration: none; font-size: 15px; position: relative;
        transition: background .2s;
    }
    .ah-icon-btn:hover { background: rgba(255,255,255,0.2); }
    .ah-icon-btn .ah-badge {
        position: absolute; top: -4px; right: -4px; background: #ef4444; color: #fff;
        font-size: 9px; font-weight: 800; border-radius: 100px; padding: 1px 4px; min-width: 14px; text-align: center;
        border: 1.5px solid #1e3a8a; line-height: 1.3;
    }
    .ah-who { display: flex; align-items: center; gap: 14px; position: relative; }
    .ah-avatar {
        width: 56px; height: 56px; border-radius: 16px;
        background: linear-gradient(135deg, #fbbf24, #f59e0b);
        display: flex; align-items: center; justify-content: center;
        font-size: 26px; flex-shrink: 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3), 0 0 0 2px rgba(255,255,255,0.15);
    }
    .ah-who h1 { margin: 0; font-size: 17px; font-weight: 800; letter-spacing: -0.2px; }
    .ah-who p { margin: 4px 0 0; font-size: 12px; color: rgba(255,255,255,0.65); font-weight: 500; }
    .ah-inst {
        margin-top: 14px; font-size: 11.5px; color: rgba(255,255,255,0.55);
        font-weight: 600; display: flex; align-items: center; gap: 5px; position: relative;
    }

    /* ── Main Wrap ── */
    .ah-wrap { max-width: 640px; margin: 0 auto; padding: 20px 15px 0; }

    /* ── Stats Row ── */
    .ah-stats-row {
        display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;
        margin-bottom: 18px;
    }
    .ah-stat-card {
        background: #fff; border-radius: 14px; padding: 14px 10px;
        text-align: center; border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 1px 6px rgba(0,0,0,0.05);
    }
    .ah-stat-card .stat-val { font-size: 20px; font-weight: 800; color: #1e3a8a; line-height: 1; }
    .ah-stat-card .stat-lbl { font-size: 10.5px; color: #64748b; font-weight: 600; margin-top: 5px; }

    /* ── Big Tiles Row ── */
    .ah-row2 { display: flex; gap: 12px; margin-bottom: 14px; }
    .ah-tile-big {
        border-radius: 18px; text-decoration: none; display: flex; flex-direction: column;
        justify-content: flex-end; padding: 18px; position: relative; overflow: hidden;
        background: linear-gradient(135deg, #1d4ed8, #1e3a8a);
        color: #fff; min-height: 115px; flex: 1.4 1 0; min-width: 0;
        box-shadow: 0 6px 20px rgba(29,78,216,0.35);
        border: none;
    }
    .ah-tile-big .ah-tile-bg-icon {
        position: absolute; top: 8px; right: 10px;
        width: 52px; height: 52px; opacity: 0.18;
    }
    .ah-tile-big .ah-tile-label { font-size: 15px; font-weight: 800; line-height: 1.35; position: relative; }
    .ah-tile-big .ah-tile-pill {
        display: inline-block; background: rgba(255,255,255,0.18); border-radius: 100px;
        font-size: 10px; font-weight: 700; padding: 2px 10px; margin-bottom: 8px;
        position: relative; letter-spacing: 0.3px;
    }
    .ah-tile {
        border-radius: 18px; text-decoration: none; display: flex; flex-direction: column;
        justify-content: space-between; padding: 14px; position: relative; overflow: hidden;
        background: #fff; color: #1e293b; min-height: 115px; flex: 1 1 0; min-width: 0;
        box-shadow: 0 1px 6px rgba(0,0,0,0.07); border: 1px solid rgba(0,0,0,0.06);
        transition: transform .15s, box-shadow .15s;
    }
    .ah-tile:active { transform: scale(0.97); box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
    .ah-tile .ah-tile-icon-wrap {
        width: 42px; height: 42px; border-radius: 13px;
        display: flex; align-items: center; justify-content: center;
    }
    .ah-tile .ah-tile-label { font-size: 12.5px; font-weight: 800; line-height: 1.3; color: #1e293b; }
    .ah-tile .ah-badge-count {
        position: absolute; top: 10px; right: 10px; background: #ef4444; color: #fff;
        font-size: 10px; font-weight: 800; border-radius: 100px; padding: 1.5px 7px;
    }

    /* ── 3-col Menu Grid ── */
    .ah-section-label {
        font-size: 11px; font-weight: 800; color: #94a3b8; letter-spacing: 1.2px;
        text-transform: uppercase; margin: 20px 2px 10px;
    }
    .ah-grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 14px; }
    .ah-cell {
        background: #fff; border: 1px solid rgba(0,0,0,0.06); border-radius: 16px;
        padding: 16px 8px 14px; text-align: center; text-decoration: none; color: #1e293b;
        display: flex; flex-direction: column; align-items: center; gap: 9px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        transition: transform .15s ease, box-shadow .15s;
        position: relative; overflow: hidden;
    }
    .ah-cell:active { transform: scale(0.95); }
    .ah-cell .ah-cell-icon-wrap {
        width: 48px; height: 48px; border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        transition: transform .2s;
    }
    .ah-cell:active .ah-cell-icon-wrap { transform: scale(0.9); }
    .ah-cell .ah-cell-label { font-size: 11px; font-weight: 700; line-height: 1.35; color: #334155; }

    /* ── Score Card ── */
    .ah-score-card {
        background: #fff; border-radius: 18px; padding: 18px 20px;
        margin-bottom: 14px; border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 1px 6px rgba(0,0,0,0.05);
        display: flex; align-items: center; gap: 16px;
    }
    .ah-score-ring {
        width: 64px; height: 64px; border-radius: 50%; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px; font-weight: 800;
    }
    .ah-score-info .lbl { font-size: 11.5px; color: #64748b; font-weight: 600; }
    .ah-score-info .val { font-size: 24px; font-weight: 800; line-height: 1.1; margin: 2px 0; }
    .ah-score-info .sub { font-size: 10.5px; color: #94a3b8; }

    /* ── Section Title ── */
    .ah-section-title {
        font-size: 12px; font-weight: 800; color: #64748b;
        margin: 20px 2px 10px; letter-spacing: 0.5px; display: flex;
        align-items: center; gap: 7px;
    }
    .ah-section-title::after {
        content: ""; flex: 1; height: 1px; background: #e2e8f0;
    }

    /* ── Tables ── */
    .ah-table-wrap {
        background: #fff; border-radius: 16px; overflow: hidden;
        border: 1px solid rgba(0,0,0,0.06); box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        margin-bottom: 14px;
    }

    /* ── Bottom Nav ── */
    .ah-bottomnav {
        position: fixed; bottom: 0; left: 0; right: 0; z-index: 50;
        background: rgba(255,255,255,0.97); backdrop-filter: blur(16px) saturate(180%);
        border-top: 1px solid rgba(0,0,0,0.08);
        display: flex; justify-content: space-around;
        padding: 10px 6px calc(env(safe-area-inset-bottom, 0px) + 10px);
        box-shadow: 0 -4px 24px rgba(15,23,42,0.08);
    }
    .ah-nav-item {
        display: flex; flex-direction: column; align-items: center; gap: 4px;
        text-decoration: none; color: #94a3b8; font-size: 10px; font-weight: 700;
        flex: 1; padding: 2px 0; transition: color .2s;
    }
    .ah-nav-item .ah-nav-icon { width: 24px; height: 24px; }
    .ah-nav-item.active { color: #1d4ed8; }
    .ah-nav-item.active .ah-nav-active-dot {
        display: block; width: 4px; height: 4px; background: #1d4ed8;
        border-radius: 50%; margin: 0 auto; margin-top: 2px;
    }
    .ah-nav-active-dot { display: none; }

    /* ── Footer ── */
    .ah-footer {
        text-align: center; color: #cbd5e1; font-size: 10.5px; font-weight: 600;
        margin: 24px 0 8px; letter-spacing: 0.3px;
    }
    .ah-footer span { color: #93c5fd; }

    /* ── Announcement Card ── */
    .ah-announce {
        border-radius: 14px; padding: 13px 15px; margin-bottom: 10px;
        border-left: 3px solid;
    }
    .ah-announce.normal { background: #eff6ff; border-color: #3b82f6; }
    .ah-announce.important { background: #fffbeb; border-color: #f59e0b; }
    .ah-announce.urgent { background: #fef2f2; border-color: #ef4444; }
    .ah-announce-title { font-size: 13px; font-weight: 800; margin-bottom: 4px; }
    .ah-announce-body { font-size: 12px; color: #475569; line-height: 1.55; }
</style>
"""

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": 
        return RedirectResponse(url="/login", status_code=303)

    conn_tmp = sqlite3.connect('attendance_pro.db')
    cur_tmp = conn_tmp.cursor()
    cur_tmp.execute("SELECT COUNT(*) FROM leave_requests WHERE status='pending'")
    pending_leave = cur_tmp.fetchone()[0]
    cur_tmp.execute("SELECT COUNT(*) FROM announcements WHERE is_active=1")
    active_announcements = cur_tmp.fetchone()[0]
    conn_tmp.close()

    def badge(n):
        return f'<span class="ah-badge">{n}</span>' if n > 0 else ""

    def count_badge(n):
        return f'<span class="ah-badge-count">{n}</span>' if n > 0 else ""

    # SVG helper สำหรับ admin cells
    def adm_cell(href, svg_path, bg, color, label):
        return f'''<a href="{href}" class="ah-cell">
            <div class="ah-cell-icon-wrap" style="background:{bg};color:{color};">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{svg_path}</svg>
            </div>
            <span class="ah-cell-label">{label}</span>
        </a>'''

    # SVG icon สำหรับ big tiles
    icon_announce_big = '<svg viewBox="0 0 24 24" width="52" height="52" fill="none" stroke="rgba(255,255,255,0.9)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>'
    icon_leave_big = '<svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#1d4ed8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>'

    return f"""
    <html>{STYLE_HEADER}
    {ADMIN_HOME_STYLE}
    <body class="ah-body">
        {PAGE_LOADER}
        <!-- ── Admin Profile Hero ── -->
        <div class="ah-profile">
            <div class="ah-top-row">
                <div class="ah-brand">K-School Admin</div>
                <div class="ah-top-icons">
                    <a href="/admin/announcements" class="ah-icon-btn" aria-label="ประกาศ">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
                        {badge(active_announcements)}
                    </a>
                    <a href="/logout" class="ah-icon-btn" aria-label="ออกจากระบบ">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16,17 21,12 16,7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                    </a>
                </div>
            </div>
            <div class="ah-who">
                <div class="ah-avatar" style="background:linear-gradient(135deg,#ef4444,#b91c1c); overflow:hidden; padding:0; border-radius:50%;">
                    <img src="{TEACHER_DEFAULT_AVATAR}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;" alt="ผู้ดูแลระบบ">
                </div>
                <div>
                    <h1>สวัสดี, ผู้ดูแลระบบ</h1>
                    <p>Admin · K-School Enterprise</p>
                </div>
            </div>
            <div class="ah-inst">
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>
                วิทยาลัยนาฏศิลป
            </div>
        </div>

        <div class="ah-wrap">
            <!-- ── Big Tiles: ประกาศ + คำร้อง ── -->
            <div class="ah-row2">
                <a href="/admin/announcements" class="ah-tile-big">
                    <div class="ah-tile-bg-icon">{icon_announce_big}</div>
                    <div class="ah-tile-pill">จัดการประกาศ</div>
                    <span class="ah-tile-label">ข่าวสาร<br>และประกาศ</span>
                </a>
                <a href="/admin/leave_requests" class="ah-tile" style="position:relative;">
                    {count_badge(pending_leave)}
                    <div class="ah-tile-icon-wrap" style="background:#dbeafe;">{icon_leave_big}</div>
                    <span class="ah-tile-label">คำร้องขอลา</span>
                </a>
            </div>

            <!-- ── เมนูจัดการระบบ ── -->
            <div class="ah-section-label">การจัดการระบบ</div>
            <div class="ah-grid3">
                {adm_cell("/admin/students", '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>', "#dbeafe", "#1d4ed8", "จัดการนักเรียน")}
                {adm_cell("/admin/student_accounts", '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>', "#f5f3ff", "#6d28d9", "บัญชีล็อกอิน")}
                {adm_cell("/admin/teachers", '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>', "#f0fdf4", "#15803d", "จัดการครู")}
                {adm_cell("/admin/view_classes", '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/>', "#fef9c3", "#a16207", "ห้องเรียน/วิชา")}
                {adm_cell("/admin/assign_groups", '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>', "#fae8ff", "#a21caf", "จัดสรรกลุ่มเรียน")}
                {adm_cell("/admin/conduct", '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>', "#fff1f2", "#be123c", "คะแนนประพฤติ")}
                {adm_cell("/admin/history", '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/>', "#fff7ed", "#c2410c", "ประวัติเช็กชื่อ")}
                {adm_cell("/admin/payments", '<rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/>', "#eef2ff", "#4338ca", "ชำระเงิน")}
                {adm_cell("/admin/grades_visibility", '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>', "#ecfeff", "#0e7490", "การมองเห็นคะแนน")}
            </div>

            <!-- ── ตรวจระเบียบนักเรียน ── -->
            <div class="ah-section-label">ตรวจระเบียบนักเรียน</div>
            <div class="ah-grid3">{inspection_menu_cells({"role": "admin"})}</div>

            <!-- ── เมนูอื่นๆ ── -->
            <div class="ah-section-label">เครื่องมือ</div>
            <div class="ah-grid3">
                {adm_cell("/admin/add_student", '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>', "#ecfeff", "#0e7490", "เพิ่มนักเรียน")}
                {adm_cell("/api/admin/export_excel", '<polyline points="6,9 12,15 18,9"/><line x1="12" y1="3" x2="12" y2="15"/><path d="M5 20h14"/>', "#f0fdf4", "#047857", "Export Excel")}
                {adm_cell("/admin/system_status", '<circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/>', "#f8fafc", "#334155", "ระบบ/เซิร์ฟเวอร์")}
                {adm_cell("/admin/analytics", '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>', "#eef2ff", "#4338ca", "แดชบอร์ดสถิติ")}
                {adm_cell("/admin/permissions", '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/>', "#fdf4ff", "#a21caf", "จัดการสิทธิ์")}
            </div>

            <div class="ah-footer">powered by <span>K-Techinteractive</span></div>
        </div>

        <!-- Admin Bottom Nav -->
        <div class="ah-bottomnav">
            <a href="/admin/dashboard" class="ah-nav-item active">
                <span class="ah-nav-icon"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg></span>โฮม<span class="ah-nav-active-dot"></span>
            </a>
            <a href="/admin/announcements" class="ah-nav-item">
                <span class="ah-nav-icon"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg></span>ประกาศ<span class="ah-nav-active-dot"></span>
            </a>
            <a href="/admin/history" class="ah-nav-item">
                <span class="ah-nav-icon"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/></svg></span>ประวัติ<span class="ah-nav-active-dot"></span>
            </a>
            <a href="/admin/system_status" class="ah-nav-item">
                <span class="ah-nav-icon"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/></svg></span>ตั้งค่า<span class="ah-nav-active-dot"></span>
            </a>
        </div>
    </body></html>
    """

@app.get("/admin/students", response_class=HTMLResponse)
async def admin_students_page(class_filter: Optional[str] = None, user_session: Optional[str] = Cookie(None)):
    if user_session != "admin":
        return RedirectResponse(url="/login", status_code=303)

    master_students = get_sorted_master_students()
    all_classes = sorted(list(set(s['class'] for s in master_students)))
    class_options = '<option value="">-- แสดงทั้งหมด --</option>'
    for c in all_classes:
        sel = 'selected' if class_filter == c else ''
        class_options += f'<option value="{c}" {sel}>ชั้น {c}</option>'
    if class_filter:
        master_students = [s for s in master_students if s['class'] == class_filter]
    all_risk_tags = get_all_students_risk_tags()
    cards = ""
    for s in master_students:
        tags = all_risk_tags.get(s['name'], [])
        tag_html = "".join([
            f'<span style="background:{t[1]};color:{t[2]};border:1px solid {t[3]};padding:2px 7px;border-radius:20px;font-size:11px;font-weight:700;white-space:nowrap;">{t[0]}</span>'
            for t in tags
        ])
        q_uid = urllib.parse.quote(s['uid'])
        initial = _he(s['name'][:1]) if s['name'] else "?"
        cards += f"""
        <div class="dk-stu sd-card" data-search="{_he((s['name'] + ' ' + s['no'] + ' ' + s['class'] + ' ' + s['branch']).lower(), quote=True)}" style="margin:0;">
            <div class="dk-stu-head" style="margin-bottom:8px;">
                <div class="dk-avatar">{initial}</div>
                <div class="nm"><b>{_he(s['name'])}</b><span>เลขที่ {_he(s['no'])} · {_he(s['branch'])}</span></div>
                <span class="dk-pill mute">{_he(s['class'])}</span>
            </div>
            {f'<div style="display:flex;gap:4px;flex-wrap:wrap;margin-bottom:8px;">{tag_html}</div>' if tag_html else ''}
            <div style="display:flex; gap:8px;">
                <a href="/admin/edit_student?uid={q_uid}" class="dk-btn light sm" style="flex:1;display:flex;align-items:center;justify-content:center;gap:5px;">{_ic(_SVG_EDIT, 13)} แก้ไข</a>
                <a href="/api/admin/delete_student?uid={q_uid}" class="dk-btn danger sm" style="flex:1;display:flex;align-items:center;justify-content:center;gap:5px;" onclick="return confirm('ยืนยันที่จะลบข้อมูลนักเรียนคนนี้ออกจากทะเบียนหลัก?')">{_ic(_SVG_TRASH, 13)} ลบ</a>
            </div>
        </div>"""

    all_students_count = len(get_sorted_master_students())
    stats = (dk_stat("นักเรียนทั้งหมด", all_students_count, _ic(_SVG_BACKPACK), "blue") + dk_stat("ห้องเรียน", len(all_classes), _ic(_SVG_SCHOOL), "violet")
             + dk_stat("กำลังแสดง", len(master_students), _ic(_SVG_EYE), "green") + dk_stat("มีป้ายเฝ้าระวัง", sum(1 for s in master_students if all_risk_tags.get(s['name'])), _ic(_SVG_ALERT), "amber"))
    quick = f"""<div class="dk-grid c2" style="margin-bottom:14px;">
        <a href="/admin/add_student" class="dk-btn green block" style="padding:14px;display:flex;align-items:center;justify-content:center;gap:7px;">{_ic(_SVG_USER_PLUS, 16)} เพิ่มรายชื่อนักเรียนใหม่</a>
        <a href="/admin/student_accounts" class="dk-btn block" style="padding:14px;background:linear-gradient(135deg,#7c3aed,#5b21b6);display:flex;align-items:center;justify-content:center;gap:7px;">{_ic(_SVG_KEY, 16)} ตั้งค่ารหัส/เบอร์โทร เข้าสู่ระบบนักเรียน</a></div>"""
    flt = f"""<div class="dk-card"><div class="dk-card-title" style="display:flex;align-items:center;gap:6px;">{_ic(_SVG_FOLDER, 16)} ทะเบียนนักเรียนส่วนกลาง<small>{len(master_students)} รายการ</small></div>
        <div class="dk-filter" style="grid-template-columns:1fr 1fr;">
            <div><label class="dk-label" style="display:flex;align-items:center;gap:5px;">{_ic(_SVG_SEARCH, 14)} ค้นหา</label><input id="sdSearch" class="dk-input" placeholder="ชื่อ / เลขที่ / สาขา"></div>
            <div><label class="dk-label">ห้องเรียน</label><select class="dk-select" onchange="location.href='/admin/students?class_filter='+encodeURIComponent(this.value);">{class_options}</select></div>
        </div></div>"""
    grid = f'<div class="dk-grid c3" id="sdGrid">{cards}</div>' if cards else f'<div class="dk-card">{dk_empty(_ic(_SVG_FOLDER, 38, 1.5), "ไม่พบข้อมูลนักเรียน")}</div>'
    js = """<script>(function(){var i=document.getElementById('sdSearch');if(!i)return;i.addEventListener('input',function(){var q=this.value.trim().toLowerCase();
        document.querySelectorAll('.sd-card').forEach(function(c){c.style.display=(!q||c.getAttribute('data-search').indexOf(q)!==-1)?'':'none';});});})();</script>"""
    return dk_page("จัดการนักเรียน", "ทะเบียนนักเรียนส่วนกลาง เพิ่ม แก้ไข ลบ และค้นหา", f'<div class="dk-stats">{stats}</div>{quick}{flt}{grid}',
                   "/admin/dashboard", extra=js, icon=_ic(_SVG_BACKPACK, 22))

@app.get("/admin/student_accounts", response_class=HTMLResponse)
async def admin_student_accounts_page(class_filter: Optional[str] = None, user_session: Optional[str] = Cookie(None)):
    access = get_access(user_session)
    if not access["authenticated"] or not can_manage_student_profiles(access):
        return RedirectResponse(url="/login", status_code=303)
    back_url = "/admin/dashboard" if access["role"] == "admin" else f"/app/dashboard?user={urllib.parse.quote(access['username'])}"

    master_students = get_sorted_master_students()
    # 🎓 หัวหน้าระดับ: เห็น/แก้ไขได้เฉพาะนักเรียนในระดับชั้นที่รับผิดชอบ
    if access["role"] == "level_head":
        if not access["level_scope"]:
            return alert_redirect("บัญชีของคุณยังไม่ถูกกำหนดระดับชั้นที่รับผิดชอบ กรุณาติดต่อผู้ดูแลระบบ", type="error", url=back_url)
        master_students = [s for s in master_students if get_grade_level(s['class']) == access["level_scope"]]

    all_classes = sorted(list(set(s['class'] for s in master_students)))
    class_options = '<option value="">-- แสดงทั้งหมด --</option>'
    for c in all_classes:
        sel = 'selected' if class_filter == c else ''
        class_options += f'<option value="{c}" {sel}>ชั้น {c}</option>'
    if class_filter:
        master_students = [s for s in master_students if s['class'] == class_filter]

    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT uid, student_id, phone, photo_url FROM student_accounts")
    accounts = {r[0]: {"student_id": r[1], "phone": r[2], "photo_url": r[3]} for r in cursor.fetchall()}
    conn.close()

    scope_note = ""
    if access["role"] == "level_head":
        scope_note = f'<div class="dk-note" style="display:flex;align-items:center;gap:7px;">{_ic(_SVG_SCHOOL, 15)} คุณกำลังดูเฉพาะนักเรียนระดับชั้น <b>{_he(access["level_scope"])}</b></div>'

    rows = ""
    for s in master_students:
        acc = accounts.get(s['uid'], {"student_id": "", "phone": "", "photo_url": ""})
        is_set = bool(acc["student_id"] and acc["phone"])
        status_badge = (f'<span class="dk-pill ok" style="display:inline-flex;align-items:center;gap:4px;flex-shrink:0;">{_ic(_SVG_CHECK_C, 12)} ตั้งค่าแล้ว</span>'
                         if is_set else
                         f'<span class="dk-pill bad" style="display:inline-flex;align-items:center;gap:4px;flex-shrink:0;">{_ic(_SVG_ALERT, 12)} ยังไม่ได้ตั้งค่า</span>')
        avatar_html = (f'<img src="{acc["photo_url"]}" style="width:44px;height:44px;border-radius:50%;object-fit:cover;border:2px solid #e2e8f0;flex-shrink:0;">'
                        if acc["photo_url"] else
                        f'<div style="width:44px;height:44px;border-radius:50%;background:#f1f5f9;display:flex;align-items:center;justify-content:center;color:#94a3b8;border:2px solid #e2e8f0;flex-shrink:0;">{_ic(_SVG_BACKPACK, 20)}</div>')
        rows += f"""
        <div class="dk-card" style="padding:14px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                {avatar_html}
                <div style="flex:1;min-width:0;">
                    <div style="font-weight:700;color:#0f172a;">{_he(s['name'])}</div>
                    <div style="font-size:11.5px;color:#94a3b8;">{_he(s['class'])} · เลขที่ {_he(s['no'])}</div>
                </div>
                {status_badge}
            </div>
            <form action="/api/admin/student_account/set" method="post" enctype="multipart/form-data" style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                <input type="hidden" name="uid" value="{_he(s['uid'], quote=True)}">
                <input type="text" name="student_id" value="{_he(acc['student_id'] or '', quote=True)}" placeholder="รหัสประจำตัว" required class="dk-input" style="margin:0;">
                <input type="text" name="phone" value="{_he(acc['phone'] or '', quote=True)}" placeholder="เบอร์โทร" required class="dk-input" style="margin:0;">
                <label class="dk-btn light sm sa-file-label" style="grid-column:1/-1;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;">
                    {_ic(_SVG_IMAGE, 14)}<span class="sa-file-text">แนบรูปโปรไฟล์ (ถ้ามี)</span>
                    <input type="file" name="photo" accept="image/png,image/jpeg,image/webp" class="sa-file-input" style="position:absolute;width:1px;height:1px;opacity:0;overflow:hidden;">
                </label>
                <button type="submit" class="dk-btn green sm" style="grid-column:1/-1;display:flex;align-items:center;justify-content:center;gap:6px;">{_ic(_SVG_SAVE, 14)} บันทึก</button>
            </form>
        </div>
        """

    note = f"""<div class="dk-card" style="background:#eff6ff;border:1px solid #bfdbfe;display:flex;gap:10px;align-items:flex-start;">
        <span style="color:#1d4ed8;flex-shrink:0;margin-top:1px;">{_ic(_SVG_INFO, 18)}</span>
        <p style="margin:0;font-size:13px;color:#1e40af;line-height:1.7;">
            นักเรียนจะล็อกอินเข้าระบบด้วย <b>รหัสประจำตัว + เบอร์โทรศัพท์</b> (ไม่ต้องตั้งรหัสผ่าน) และสามารถ <b>แนบรูปโปรไฟล์</b> ให้นักเรียนแต่ละคนได้จากรายการด้านล่าง (รองรับ .jpg .png .webp ไม่เกิน 3MB)
        </p></div>"""
    filter_bar = f"""<div class="dk-card"><div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;">
        <div class="dk-card-title" style="margin:0;">รายชื่อนักเรียน<small>{len(master_students)} คน</small></div>
        <div style="display:flex;align-items:center;gap:8px;">
            <label class="dk-label" style="margin:0;display:flex;align-items:center;gap:5px;">{_ic(_SVG_SEARCH, 14)} กรองตามห้อง</label>
            <select class="dk-select" style="width:auto;" onchange="location.href='/admin/student_accounts?class_filter='+encodeURIComponent(this.value);">{class_options}</select>
        </div></div></div>"""

    body = note + scope_note + filter_bar + (f'<div class="dk-grid c2">{rows}</div>' if rows else f'<div class="dk-card">{dk_empty(_ic(_SVG_FOLDER, 38, 1.5), "ไม่พบข้อมูลนักเรียน")}</div>')
    js = """<script>document.addEventListener('change', function(ev){
        var inp = ev.target.closest('.sa-file-input'); if(!inp) return;
        var t = inp.closest('.sa-file-label').querySelector('.sa-file-text');
        t.textContent = inp.files && inp.files[0] ? inp.files[0].name : 'แนบรูปโปรไฟล์ (ถ้ามี)';
    });</script>"""
    return dk_page("โปรไฟล์บัญชีนักเรียน", "ตั้งรหัสประจำตัวและเบอร์โทรสำหรับให้นักเรียนเข้าสู่ระบบ", body, back_url, extra=js, icon=_ic(_SVG_KEY, 22))

@app.post("/api/admin/student_account/set")
async def api_set_student_account(uid: str = Form(...), student_id: str = Form(...), phone: str = Form(...), photo: Optional[UploadFile] = File(None), user_session: Optional[str] = Cookie(None)):
    access = get_access(user_session)
    if not access["authenticated"] or not can_manage_student_profiles(access):
        return HTMLResponse("Unauthorized", status_code=401)

    # 🎓 หัวหน้าระดับ: ยืนยันว่านักเรียนคนนี้อยู่ในระดับชั้นที่ตนรับผิดชอบจริง
    if access["role"] == "level_head":
        all_students = get_sorted_master_students()
        target = next((s for s in all_students if s['uid'] == uid), None)
        if not target or not in_discipline_scope(access, target['class']):
            return alert_redirect("คุณไม่มีสิทธิ์แก้ไขโปรไฟล์ของนักเรียนนอกระดับชั้นที่รับผิดชอบ", type="error", url="/admin/student_accounts")

    student_id = student_id.strip()
    phone = phone.strip()

    photo_url = None  # None = ไม่แตะรูปเดิม
    if photo is not None and photo.filename:
        if photo.content_type not in ALLOWED_PHOTO_TYPES:
            return alert_redirect("รองรับเฉพาะไฟล์รูปภาพ .jpg .png .webp เท่านั้น", type="error", url="/admin/student_accounts")
        file_bytes = await photo.read()
        if len(file_bytes) > MAX_PHOTO_SIZE_BYTES:
            return alert_redirect("ไฟล์รูปภาพต้องมีขนาดไม่เกิน 3MB", type="error", url="/admin/student_accounts")
        ext = ALLOWED_PHOTO_TYPES[photo.content_type]
        safe_name = hashlib.md5(uid.encode("utf-8")).hexdigest() + ext
        file_path = os.path.join(PROFILE_PHOTO_DIR, safe_name)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        photo_url = f"/static/profiles/{safe_name}"

    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    try:
        if photo_url is not None:
            cursor.execute("""INSERT INTO student_accounts (uid, student_id, phone, photo_url) VALUES (?, ?, ?, ?)
                ON CONFLICT(uid) DO UPDATE SET student_id=excluded.student_id, phone=excluded.phone, photo_url=excluded.photo_url""",
                (uid, student_id, phone, photo_url))
        else:
            cursor.execute("""INSERT INTO student_accounts (uid, student_id, phone) VALUES (?, ?, ?)
                ON CONFLICT(uid) DO UPDATE SET student_id=excluded.student_id, phone=excluded.phone""",
                (uid, student_id, phone))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return alert_redirect("รหัสประจำตัวนี้ถูกใช้กับนักเรียนคนอื่นแล้ว กรุณาตรวจสอบอีกครั้ง", type="error", url="/admin/student_accounts")
    conn.close()
    return alert_redirect("บันทึกโปรไฟล์นักเรียนเรียบร้อยแล้ว", type="success", url="/admin/student_accounts")

@app.post("/api/admin/update_maintenance")
async def api_update_maintenance(mode_type: str = Form(...), admin_pass: str = Form(...), user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return HTMLResponse("Unauthorized", status_code=401)
    if admin_pass != ADMIN_PASS:
        return HTMLResponse(f"""<html>{STYLE_HEADER}<body><script>smartAlert({{title: 'ปฏิเสธการเข้าถึง!', message: 'รหัสผ่านผู้ดูแลระบบไม่ถูกต้อง!', type: 'error', callback: () => {{ history.back(); }} }});</script></body></html>""")
        
    is_active = 0 if mode_type == "off" else 1
    
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE maintenance_settings SET is_active = ?, mode_type = ? WHERE id = 1", (is_active, mode_type))
    conn.commit()
    conn.close()
    
    # ⚡ ดีดสั่งพ่นสัญญาณหาหน้าบ้านทุกคนพร้อมกันให้เปลี่ยนหน้าในเสี้ยววิ!
    await manager.broadcast("STATUS_CHANGED")
    
    return HTMLResponse(f"""<html>{STYLE_HEADER}<body><script>smartAlert({{title: 'ดำเนินการเสร็จสิ้น!', message: 'ปรับปรุงสถานะระบบเรียบร้อยแล้ว', type: 'success', callback: () => {{ window.location.href='/admin/dashboard'; }} }});</script></body></html>""")

# ==========================================
# 🩺 SYSTEM STATUS — สถานะ IT ทั้งหมดของระบบ
# ==========================================
@app.get("/admin/system_status", response_class=HTMLResponse)
async def admin_system_status(user_session: Optional[str] = Cookie(None)):
    if user_session != "admin":
        return RedirectResponse(url="/login", status_code=303)

    import platform

    # ── ทรัพยากรเครื่อง (CPU/RAM) ถ้ามี psutil ติดตั้งไว้ ──
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory()
        ram_percent = mem.percent
        ram_used_gb = round(mem.used / (1024 ** 3), 2)
        ram_total_gb = round(mem.total / (1024 ** 3), 2)
        disk = psutil.disk_usage('.')
        disk_percent = disk.percent
        psutil_available = True
    except Exception:
        psutil_available = False

    # ── Uptime ของ Web Server ──
    uptime_delta = datetime.now() - SERVER_START_TIME
    days = uptime_delta.days
    hours, rem = divmod(uptime_delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    uptime_str = (f"{days} วัน {hours} ชม. {minutes} นาที" if days else f"{hours} ชม. {minutes} นาที {seconds} วิ")

    # ── สถานะ Discord Bot ──
    bot_online = bot.is_ready()
    bot_latency_ms = round(bot.latency * 1000) if bot_online and bot.latency == bot.latency else None
    guild_count = len(bot.guilds) if bot_online else 0
    bot_user = str(bot.user) if bot.user else "ยังไม่ล็อกอิน"

    # ── สถานะ Database ──
    db_path = 'attendance_pro.db'
    db_ok = True
    db_size_mb = 0
    table_counts = {}
    try:
        db_size_mb = round(os.path.getsize(db_path) / (1024 * 1024), 3) if os.path.exists(db_path) else 0
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for table in ["teachers", "course_groups", "group_assignments", "attendance_logs", "leave_requests", "announcements"]:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                table_counts[table] = cursor.fetchone()[0]
            except Exception:
                table_counts[table] = "-"
        conn.close()
    except Exception:
        db_ok = False

    # ── WebSocket Realtime ──
    ws_count = len(manager.active_connections)

    # ── Maintenance Mode ──
    m_cfg = get_maintenance_status()

    def dot(ok):
        c = "#10b981" if ok else "#ef4444"
        return f'<span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:{c};box-shadow:0 0 6px {c};margin-right:6px;"></span>'

    def stat_card(icon, title, status_html, detail_html):
        return f"""
        <div style="background:white;border:1px solid #e6eaf1;border-radius:14px;padding:18px;box-shadow:0 1px 3px rgba(15,23,42,0.06);margin-bottom:14px;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;flex-wrap:wrap;gap:6px;">
                <div style="font-weight:700;font-size:14px;color:#0f172a;display:flex;align-items:center;gap:8px;">{icon} {title}</div>
                {status_html}
            </div>
            <div style="font-size:12.5px;color:#64748b;line-height:1.8;">{detail_html}</div>
        </div>
        """

    server_card = stat_card(
        "🖥️", "Web Server (FastAPI / Uvicorn)",
        f'{dot(True)}<span style="font-size:12px;font-weight:700;color:#10b981;">ONLINE</span>',
        f"Uptime: <b>{uptime_str}</b><br>เริ่มทำงานเมื่อ: {SERVER_START_TIME.strftime('%d/%m/%Y %H:%M:%S')}<br>Python: {platform.python_version()} · {platform.system()} {platform.release()}"
    )

    bot_card = stat_card(
        "🤖", "Discord Bot",
        f'{dot(bot_online)}<span style="font-size:12px;font-weight:700;color:{"#10b981" if bot_online else "#ef4444"};">{"ONLINE" if bot_online else "OFFLINE"}</span>',
        f"บัญชี: <b>{bot_user}</b><br>Latency: {bot_latency_ms if bot_latency_ms is not None else 'N/A'} ms<br>เชื่อมต่ออยู่: {guild_count} เซิร์ฟเวอร์ (guild)"
    )

    db_rows = " · ".join([f"{k}: <b>{v}</b>" for k, v in table_counts.items()])
    db_card = stat_card(
        "🗄️", "Database (SQLite)",
        f'{dot(db_ok)}<span style="font-size:12px;font-weight:700;color:{"#10b981" if db_ok else "#ef4444"};">{"CONNECTED" if db_ok else "ERROR"}</span>',
        f"ขนาดไฟล์: <b>{db_size_mb} MB</b><br>{db_rows}"
    )

    ws_card = stat_card(
        "🔌", "WebSocket Realtime",
        f'{dot(True)}<span style="font-size:12px;font-weight:700;color:#10b981;">ACTIVE</span>',
        f"Client ที่เชื่อมต่ออยู่ตอนนี้: <b>{ws_count}</b> การเชื่อมต่อ"
    )

    maint_ok = m_cfg["is_active"] == 0
    maintenance_card = stat_card(
        "⚙️", "Maintenance Mode",
        f'{dot(maint_ok)}<span style="font-size:12px;font-weight:700;color:{"#10b981" if maint_ok else "#f59e0b"};">{"เปิดใช้งานปกติ" if maint_ok else "ปิดกั้นอยู่"}</span>',
        f"โหมดปัจจุบัน: <b>{m_cfg['mode_type']}</b>"
    )

    if psutil_available:
        resource_card = stat_card(
            "📊", "CPU / RAM / Disk",
            "",
            f"CPU: <b>{cpu_percent}%</b><br>RAM: <b>{ram_percent}%</b> ({ram_used_gb} / {ram_total_gb} GB)<br>Disk: <b>{disk_percent}%</b> ใช้งานแล้ว"
        )
    else:
        resource_card = stat_card(
            "📊", "CPU / RAM / Disk",
            "",
            "ไม่พบไลบรารี <code>psutil</code> ในเครื่อง — ติดตั้งด้วยคำสั่ง <code>pip install psutil</code> เพื่อดูข้อมูลนี้"
        )

    # ── System Logs Section ──
    log_rows = "".join([f'<div style="font-family:monospace; font-size:11px; padding:4px 8px; border-bottom:1px solid #f1f5f9; color:#334155;">{log}</div>' for log in SYSTEM_LOGS])
    log_card = f"""
    <div class="card">
        <h2>📜 ระบบบันทึกเหตุการณ์ (System Logs)</h2>
        <div style="background:#f8fafc; border-radius:8px; max-height:200px; overflow-y:auto; border:1px solid #e2e8f0;">
            {log_rows if log_rows else '<div style="padding:20px; text-align:center; color:#94a3b8;">ยังไม่มีบันทึกเหตุการณ์</div>'}
        </div>
    </div>
    """

    

    maintenance_control_card = f"""
    <div class="card" style="border: 2px dashed #f59e0b; background: #fffdf5;">
        <h2 style="color:#d97706;">⚙️ ควบคุมโหมดสถานะเว็บไซต์ (Maintenance Mode)</h2>
        <p style="font-size:13.5px; margin: 0 0 12px 0;"><b>สถานะปัจจุบัน:</b> <span style="font-weight:700;">{"🔴 ระบบกำลังเปิดออนไลน์ปกติ" if m_cfg["is_active"] == 0 else f"🟢 เปิดระบบป้องกันปิดปรับปรุงอยู่ ({m_cfg['mode_type']})"}</span></p>
        <form action="/api/admin/update_maintenance" method="post" style="margin:0;">
            <label style="font-size:12.5px; font-weight:700; color:#475569;">เลือกโหมดจำลองเปิดฉากกั้นเว็บ:</label>
            <select name="mode_type" required>
                <option value="off" {"selected" if m_cfg['is_active']==0 else ""}>🟢 [ปิดระบบคัดกรอง] เปิดเว็บออนไลน์ปกติให้ใช้งาน</option>
                <option value="maintenance" {"selected" if m_cfg['is_active']==1 and m_cfg['mode_type']=='maintenance' else ""}>🏗️ กำลังแก้ไขเว็บไซต์</option>
                <option value="updating" {"selected" if m_cfg['is_active']==1 and m_cfg['mode_type']=='updating' else ""}>🚀 กำลังอัปเดตระบบ</option>
                <option value="testing" {"selected" if m_cfg['is_active']==1 and m_cfg['mode_type']=='testing' else ""}>🧪 กำลังอยู่ในช่วงทดลอง</option>
                <option value="disabled" {"selected" if m_cfg['is_active']==1 and m_cfg['mode_type']=='disabled' else ""}>🔒 ปิดระบบชั่วคราว</option>
                <option value="ip_error" {"selected" if m_cfg['is_active']==1 and m_cfg['mode_type']=='ip_error' else ""}>🚫 ไม่มีการจัดสรร IP ERROR 404</option>
            </select>
            <input type="password" name="admin_pass" placeholder="กรอกรหัสผ่านเจ้าของเว็บเพื่ออนุมัติคำสั่ง" required>
            <button type="submit" class="btn-submit" style="background:linear-gradient(135deg, #d97706, #b45309); border-bottom-color:#78350f;">⚡ ยืนยันการเปลี่ยนแปลงโหมดเว็บ</button>
        </form>
    </div>
    """

    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> 🏢 Enterprise System Infrastructure</h1>
            <a href="/admin/dashboard" class="btn btn-secondary">⬅ กลับหน้าควบคุม</a>
        </div>
        <div class="main-container" style="max-width: 900px;">
            <div style="background: linear-gradient(135deg, #0f172a, #1e293b); color:white; padding:30px; border-radius:16px; margin-bottom:24px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); border-left: 6px solid #d4af37;">
                <h1 style="margin:0; font-size:24px; letter-spacing:1px;">ศูนย์ควบคุมโครงสร้างพื้นฐาน</h1>
                <p style="margin:8px 0 0 0; opacity:0.8; font-size:14px;">K-School Enterprise Edition · Monitoring & Security Audit</p>
            </div>

            {maintenance_control_card}

            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap:16px; margin-bottom:24px;">
                {server_card}
                {resource_card}
                {bot_card}
                {db_card}
                {ws_card}
                {maintenance_card}
            </div>

            {log_card}
            

            <div style="text-align:center;color:#94a3b8;font-size:11.5px;margin-top:24px; padding-bottom:40px;">
                <div style="margin-bottom:8px;">ใบรับรองความปลอดภัยระดับองค์กร · เข้ารหัสข้อมูลแบบ End-to-End</div>
                อัปเดตสถานะล่าสุด: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} &nbsp;·&nbsp;
                <a href="/admin/system_status" style="color:#1e3a8a;font-weight:700;text-decoration:none; background:#e2e8f0; padding:4px 12px; border-radius:20px;">🔄 รีเฟรชข้อมูลเรียลไทม์</a>
            </div>
        </div>
    </body></html>
    """

# ==========================================
# 👤 [INSTRUCTOR VIEW WITH MAINTENANCE BLOCK]
# ==========================================
@app.get("/app/dashboard", response_class=HTMLResponse)
async def app_dashboard(user: str, user_session: Optional[str] = Cookie(None)):
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return RedirectResponse(url="/login", status_code=303)
        
    m_cfg = get_maintenance_status()
    if m_cfg["is_active"] == 1:
        return generate_maintenance_html(m_cfg["mode_type"])
        
    access = get_access(user_session)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT fullname FROM teachers WHERE username = ?", (user,))
    t_info = cursor.fetchone()
    display_name = t_info[0] if t_info else user
    cursor.execute("SELECT group_id, group_name FROM course_groups WHERE teacher_username = ?", (user,))
    my_groups = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM announcements WHERE is_active=1")
    active_announcements = cursor.fetchone()[0]
    pending_leave = 0
    if can_manage_discipline(access):
        if access["role"] == "level_head" and access["level_scope"]:
            cursor.execute("SELECT classroom, status FROM leave_requests WHERE status='pending'")
            pending_leave = sum(1 for r in cursor.fetchall() if get_grade_level(r[0]) == access["level_scope"])
        else:
            cursor.execute("SELECT COUNT(*) FROM leave_requests WHERE status='pending'")
            pending_leave = cursor.fetchone()[0]
    conn.close()

    def badge(n):
        return f'<span class="ah-badge">{n}</span>' if n > 0 else ""
    def count_badge(n):
        return f'<span class="ah-badge-count">{n}</span>' if n > 0 else ""

    # 🎓📍 แผ่นเช็กชื่อคลาสวิชาภายใต้การกำกับดูแล (SVG icons)
    room_cells = ""
    for g in my_groups:
        target_url = f"/app/classroom/{g[0]}?user={user}"
        room_cells += f"""
        <a href="{target_url}" class="ah-cell">
            <div class="ah-cell-icon-wrap" style="background:#dbeafe;color:#1d4ed8;">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            </div>
            <span class="ah-cell-label">{g[1]}</span>
        </a>"""

    # 🔐 เมนูสิทธิ์พิเศษ: หัวหน้าระดับ / ฝ่ายกิจการ (SVG icons)
    discipline_cells = ""
    if can_manage_discipline(access):
        discipline_cells += f"""
        <a href="/admin/leave_requests" class="ah-cell" style="position:relative;">
            {count_badge(pending_leave)}
            <div class="ah-cell-icon-wrap" style="background:#eef2ff;color:#4338ca;">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            </div>
            <span class="ah-cell-label">อนุมัติคำร้องลา</span>
        </a>
        <a href="/admin/conduct" class="ah-cell">
            <div class="ah-cell-icon-wrap" style="background:#fff1f2;color:#be123c;">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            </div>
            <span class="ah-cell-label">คะแนนประพฤติ</span>
        </a>"""
    if can_view_analytics(access):
        discipline_cells += f"""
        <a href="/admin/analytics" class="ah-cell">
            <div class="ah-cell-icon-wrap" style="background:#eef2ff;color:#4338ca;">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
            </div>
            <span class="ah-cell-label">แดชบอร์ดสถิติ</span>
        </a>"""
    if can_manage_teacher_accounts(access):
        discipline_cells += f"""
        <a href="/admin/teachers" class="ah-cell">
            <div class="ah-cell-icon-wrap" style="background:#f0fdf4;color:#15803d;">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
            <span class="ah-cell-label">จัดการบัญชีครู</span>
        </a>"""
    if can_manage_student_profiles(access):
        discipline_cells += f"""
        <a href="/admin/student_accounts" class="ah-cell">
            <div class="ah-cell-icon-wrap" style="background:#f5f3ff;color:#6d28d9;">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </div>
            <span class="ah-cell-label">โปรไฟล์นักเรียน</span>
        </a>"""
    discipline_cells = inspection_menu_cells(access) + discipline_cells
    discipline_section = ""
    if discipline_cells:
        scope_tag = f" ({access['level_scope']})" if access["role"] == "level_head" and access["level_scope"] else ""
        discipline_section = f"""
        <div class="ah-section-label">{access['role_label']}{scope_tag} · สิทธิ์พิเศษ</div>
        <div class="ah-grid3">{discipline_cells}</div>
        """

    return f"""
    <html>{STYLE_HEADER}
    {ADMIN_HOME_STYLE}
    <body class="ah-body">
        {PAGE_LOADER}
        <!-- ── Teacher Profile Hero ── -->
        <div class="ah-profile">
            <div class="ah-top-row">
                <div class="ah-brand">K-School</div>
                <div class="ah-top-icons">
                    <a href="/app/notifications" class="ah-icon-btn" aria-label="ประกาศ">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
                        {badge(active_announcements)}
                    </a>
                    <a href="/logout" class="ah-icon-btn" aria-label="ออกจากระบบ">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16,17 21,12 16,7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                    </a>
                </div>
            </div>
            <div class="ah-who">
                <div class="ah-avatar" style="background:linear-gradient(135deg,#0f766e,#0d9488); overflow:hidden; padding:0; border-radius:50%;">
                    <img src="{TEACHER_DEFAULT_AVATAR}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;" alt="{display_name}">
                </div>
                <div>
                    <h1>สวัสดี, {display_name}</h1>
                    <p>{access['role_label']} · K-School</p>
                </div>
            </div>
            <div class="ah-inst">
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>
                วิทยาลัยนาฏศิลป
            </div>
        </div>

        <div class="ah-wrap">
            <!-- ── ประกาศ ── -->
            <div id="announcement-section" style="margin-bottom:16px; display:none;">
                <div id="announcement-list"></div>
            </div>
            <script>
                async function loadAnnouncements() {{
                    try {{
                        const resp = await fetch('/api/announcements');
                        const data = await resp.json();
                        if (data && data.length > 0) {{
                            document.getElementById('announcement-section').style.display = 'block';
                            const list = document.getElementById('announcement-list');
                            const cfg = {{normal:{{cls:'normal',ic:'📣',tc:'#1e40af'}}, important:{{cls:'important',ic:'⚠️',tc:'#92400e'}}, urgent:{{cls:'urgent',ic:'🚨',tc:'#991b1b'}}}};
                            data.forEach(a => {{
                                const c = cfg[a.level] || cfg.normal;
                                const div = document.createElement('div');
                                div.className = `ah-announce ${{c.cls}}`;
                                div.innerHTML = `<div class="ah-announce-title" style="color:${{c.tc}}">${{c.ic}} ${{a.title}}</div><div class="ah-announce-body">${{a.body}}</div>`;
                                list.appendChild(div);
                            }});
                        }}
                    }} catch (e) {{}}
                }}
                loadAnnouncements();
            </script>

            <!-- ── Big Tiles: ประวัติ + คำร้อง ── -->
            <div class="ah-row2">
                <a href="/app/history?user={user}" class="ah-tile-big" style="background:linear-gradient(135deg,#0f766e,#0d9488);">
                    <div class="ah-tile-bg-icon">
                        <svg viewBox="0 0 24 24" width="52" height="52" fill="none" stroke="rgba(255,255,255,0.9)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10,9 9,9 8,9"/></svg>
                    </div>
                    <div class="ah-tile-pill">ดูประวัติทั้งหมด</div>
                    <span class="ah-tile-label">คลังประวัติ<br>ใบเช็กชื่อ</span>
                </a>
                <a href="/leave" class="ah-tile">
                    <div class="ah-tile-icon-wrap" style="background:#dbeafe;">
                        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#1d4ed8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
                    </div>
                    <span class="ah-tile-label">ยื่นคำร้องลา <span style="font-size:10px;color:#94a3b8;display:block;font-weight:500;">(สำหรับนักเรียน)</span></span>
                </a>
            </div>

            {discipline_section}

            <div class="ah-section-title">คลาสวิชาภายใต้การกำกับดูแล</div>
            <div class="ah-grid3">
                {room_cells if room_cells else '<div style="grid-column:1/-1;padding:20px;text-align:center;background:#fff;border-radius:16px;border:1px solid #fecaca;color:#b91c1c;font-weight:700;font-size:13px;">⚠️ ยังไม่มีกลุ่มวิชาที่ได้รับมอบหมาย</div>'}
            </div>

            <div class="ah-footer">powered by <span>K-Techinteractive</span></div>
        </div>

        {render_bottom_nav("home", "teacher", user)}
    </body></html>
    """

@app.get("/teacher/profile", response_class=HTMLResponse)
async def teacher_profile_page(user: str, user_session: Optional[str] = Cookie(None)):
    """👤 หน้าโปรไฟล์ครู — ข้อมูลส่วนตัว + สิทธิ์การใช้งาน + ออกจากระบบ"""
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return RedirectResponse(url="/login", status_code=303)

    access = get_access(user_session)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT fullname FROM teachers WHERE username = ?", (user,))
    t_info = cursor.fetchone()
    display_name = t_info[0] if t_info else user
    cursor.execute("SELECT COUNT(*) FROM course_groups WHERE teacher_username = ?", (user,))
    group_count = cursor.fetchone()[0]
    conn.close()
    uq = urllib.parse.quote(user)

    return f"""
    <html>{STYLE_HEADER}
    {ADMIN_HOME_STYLE}
    <body class="ah-body">
        <div class="ah-profile" style="text-align:center;">
            <div class="ah-top-row"><div class="ah-brand">K-School</div><div></div></div>
            <div style="display:flex;flex-direction:column;align-items:center;gap:10px;position:relative;">
                <div class="ah-avatar" style="width:76px;height:76px;border-radius:50%;background:linear-gradient(135deg,#0f766e,#0d9488); overflow:hidden; padding:0;">
                    <img src="{TEACHER_DEFAULT_AVATAR}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;" alt="{display_name}">
                </div>
                <div>
                    <h1 style="margin:0;font-size:17px;font-weight:800;">{display_name}</h1>
                    <p style="margin:4px 0 0;font-size:12.5px;color:rgba(255,255,255,0.65);">{access['role_label']} · {group_count} กลุ่มวิชาที่ดูแล</p>
                </div>
            </div>
            <div class="ah-inst" style="justify-content:center;margin-top:14px;">
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>
                วิทยาลัยนาฏศิลป
            </div>
        </div>
        <div class="ah-wrap">
            <div class="ah-section-label">บัญชีของฉัน</div>
            <div style="display:flex;flex-direction:column;gap:10px;margin-bottom:12px;">
                <a href="/app/history?user={uq}" class="ah-cell" style="flex-direction:row;justify-content:flex-start;text-align:left;padding:14px;gap:14px;">
                    <div class="ah-cell-icon-wrap" style="background:#fff7ed;color:#c2410c;flex-shrink:0;">
                        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/></svg>
                    </div>
                    <span class="ah-cell-label" style="font-size:13px;text-align:left;">คลังประวัติใบเช็กชื่อ</span>
                </a>
                <a href="/leave" class="ah-cell" style="flex-direction:row;justify-content:flex-start;text-align:left;padding:14px;gap:14px;">
                    <div class="ah-cell-icon-wrap" style="background:#dbeafe;color:#1d4ed8;flex-shrink:0;">
                        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
                    </div>
                    <span class="ah-cell-label" style="font-size:13px;text-align:left;">ยื่นคำร้องลา</span>
                </a>
                <a href="/app/notifications" class="ah-cell" style="flex-direction:row;justify-content:flex-start;text-align:left;padding:14px;gap:14px;">
                    <div class="ah-cell-icon-wrap" style="background:#fffbeb;color:#a16207;flex-shrink:0;">
                        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
                    </div>
                    <span class="ah-cell-label" style="font-size:13px;text-align:left;">แจ้งเตือน</span>
                </a>
                <a href="/logout" class="ah-cell" style="flex-direction:row;justify-content:flex-start;text-align:left;padding:14px;gap:14px;border-color:#fecaca;">
                    <div class="ah-cell-icon-wrap" style="background:#fef2f2;color:#b91c1c;flex-shrink:0;">
                        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16,17 21,12 16,7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                    </div>
                    <span class="ah-cell-label" style="font-size:13px;color:#b91c1c;text-align:left;">ออกจากระบบ</span>
                </a>
            </div>
            <div class="ah-footer">powered by <span>K-Techinteractive</span></div>
        </div>
        {render_bottom_nav("profile", "teacher", user)}
    </body></html>
    """

# ==========================================
# 📊 [ADMIN HISTORY SYSTEM & LOG DELETION]
# ==========================================
@app.get("/admin/history", response_class=HTMLResponse)
async def admin_history_page(group_id: Optional[str] = None, user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return RedirectResponse(url="/login", status_code=303)
    
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    all_groups = []
    distinct_dates = []
    selected_group_name = ""
    
    try:
        cursor.execute("SELECT group_id, group_name FROM course_groups")
        all_groups = cursor.fetchall()
        if group_id:
            cursor.execute("SELECT group_name FROM course_groups WHERE group_id = ?", (group_id,))
            g_res = cursor.fetchone()
            if g_res:
                selected_group_name = g_res[0]
                cursor.execute("SELECT DISTINCT date FROM attendance_logs WHERE group_name = ? ORDER BY log_id DESC", (selected_group_name,))
                distinct_dates = [r[0] for r in cursor.fetchall()]
    except Exception as e: print(f"❌ Admin Fetch History Error: {e}")
    finally: conn.close()

    try:
        sel_gid = int(group_id) if group_id else None
    except ValueError:
        sel_gid = None
    group_cards = ""
    for g in all_groups:
        on = sel_gid == g[0]
        group_cards += f"""<a href="/admin/history?group_id={g[0]}" class="dk-row" style="text-decoration:none;color:inherit;margin:0;{'border-color:#1d4ed8;background:#eff6ff;' if on else ''}">
            <div class="dk-ico-box">📚</div><div class="grow"><b>{_he(g[1])}</b><span>{'กำลังดูอยู่' if on else 'แตะเพื่อดูรอบที่บันทึก'}</span></div>
            <span style="color:#1d4ed8;font-weight:800;">›</span></a>"""

    date_list_items = ""
    q_group = urllib.parse.quote(selected_group_name)
    for d in distinct_dates:
        date_list_items += f"""
        <a href="/admin/history/detail?group_name={q_group}&date={urllib.parse.quote(str(d))}" class="dk-row" style="text-decoration:none;color:inherit;">
            <div class="dk-ico-box" style="background:#fff7ed;">📅</div>
            <div class="grow"><b>รอบวันที่ {_he(str(d))}</b><span>เปิดตรวจสอบ / ลบประวัติซ้ำ</span></div>
            <span style="color:#1d4ed8;font-weight:800;">➔</span></a>"""

    stats = (dk_stat("วิชาในระบบ", len(all_groups), "📚", "blue")
             + dk_stat("รอบที่บันทึก (วิชานี้)", len(distinct_dates) if selected_group_name else "-", "📅", "violet"))
    stats = f'<div class="dk-stats" style="grid-template-columns:repeat(2,1fr);">{stats}</div>'
    list_card = ""
    if selected_group_name:
        list_card = f"""<div class="dk-card"><div class="dk-card-title">📅 รอบที่บันทึก: {_he(selected_group_name)}<small>{len(distinct_dates)} รอบ</small></div>
            {date_list_items if date_list_items else dk_empty("📭", "ยังไม่เคยมีประวัติบันทึกในวิชานี้")}</div>"""
    body = (stats + f'<div class="dk-section">เลือกวิชาที่ต้องการตรวจสอบ</div>'
            + (f'<div class="dk-grid c2" style="margin-bottom:14px;">{group_cards}</div>' if group_cards else f'<div class="dk-card">{dk_empty("📚", "ยังไม่มีวิชาในระบบ")}</div>')
            + list_card)
    return dk_page("คลังใบเช็คชื่อส่วนกลาง", "ตรวจสอบและบริหารประวัติการเช็คชื่อของทุกวิชา", body, "/admin/dashboard", icon="📊 ")

@app.get("/admin/history/detail", response_class=HTMLResponse)
async def admin_history_detail_page(group_name: str, date: str, user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return RedirectResponse(url="/login", status_code=303)
    
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    logs = []
    stats = {"มา": 0, "สาย": 0, "ลา": 0, "ขาด": 0}
    checked_by_name = "ไม่ระบุ"
    
    try:
        cursor.execute("SELECT student_name, student_no, classroom, status, checked_by FROM attendance_logs WHERE group_name = ? AND date = ?", (group_name, date))
        logs = cursor.fetchall()
        for row in logs:
            if row[3] in stats: stats[row[3]] += 1
            checked_by_name = row[4]
    except Exception as e: print(f"❌ Admin Detail Error: {e}")
    finally: conn.close()

    pill = {"มา": "ok", "สาย": "warn", "ลา": "mute", "ขาด": "bad"}
    table_rows = ""
    for row in logs:
        s_name, s_no, s_class, s_status, _ = row
        table_rows += f"""
        <tr><td><span class="dk-pill mute">{_he(str(s_class))}</span></td><td><b>{_he(str(s_no))}</b></td>
            <td style="font-weight:700;">{_he(str(s_name))}</td>
            <td><span class="dk-pill {pill.get(s_status, 'mute')}">{_he(str(s_status))}</span></td></tr>"""

    total = len(logs)
    present_rate = round((stats['มา'] + stats['สาย']) * 100 / total) if total else 0
    stat_html = (dk_stat("มา", stats['มา'], "✅", "green") + dk_stat("สาย", stats['สาย'], "⏰", "amber")
                 + dk_stat("ลา", stats['ลา'], "📝", "blue") + dk_stat("ขาด", stats['ขาด'], "❌", "red"))
    info = f"""<div class="dk-card"><div class="dk-card-title">📘 รายละเอียดรอบแผ่นตรวจ<small>เข้าเรียน {present_rate}%</small></div>
        <div class="dk-track" style="margin-bottom:12px;"><i style="width:{present_rate}%"></i></div>
        <div style="font-size:13.5px;line-height:1.9;"><b>วิชาเรียน:</b> {_he(group_name)}<br><b>ประจำรอบวันที่:</b> {_he(date)}<br><b>ผู้กดบันทึก:</b> {_he(str(checked_by_name))}</div>
        <a href="/api/admin/delete_attendance_log?group_name={urllib.parse.quote(group_name)}&date={urllib.parse.quote(date)}" class="dk-btn danger block" style="margin-top:14px;padding:12px;"
           onclick="return confirm('⚠️ ยืนยันการลบข้อมูลใบเช็คชื่อในรอบวันนี้?')">🛑 ลบข้อมูลประวัติบันทึกซ้ำของรอบคลาสนี้</a></div>"""
    table = f"""<div class="dk-card"><div class="dk-card-title">👥 สถานะรายบุคคล<small>{total} คน</small></div>
        <div class="dk-tablewrap"><table class="dk-table"><thead><tr><th>ชั้นเรียน</th><th>เลขที่</th><th>ชื่อ-นามสกุล</th><th>สถานะ</th></tr></thead>
        <tbody>{table_rows if table_rows else "<tr><td colspan='4' style='text-align:center;color:#94a3b8;'>ไม่พบข้อมูลนักเรียน</td></tr>"}</tbody></table></div></div>"""
    return dk_page("ตรวจสอบใบเช็คชื่อ", f"{_he(group_name)} · {_he(date)}", f'<div class="dk-stats">{stat_html}</div>{info}{table}',
                   "javascript:history.back();", icon="📋 ")

@app.get("/api/admin/delete_attendance_log")
async def api_delete_attendance_log(group_name: str, date: str, user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM attendance_logs WHERE group_name = ? AND date = ?", (group_name, date))
        conn.commit()
    except Exception as e: print(f"❌ DB Delete Attendance Log Error: {e}")
    finally: conn.close()
    return alert_redirect("ลบข้อมูลประวัติที่ซ้ำซ้อนในรอบนี้เรียบร้อยแล้ว", type="success", url="/admin/history")

# ==========================================
# 📝 [ADMIN EDIT & DELETE STUDENT]
# ==========================================
@app.get("/admin/edit_student", response_class=HTMLResponse)
async def admin_edit_student_page(uid: str, user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return RedirectResponse(url="/login", status_code=303)
    master_students = get_sorted_master_students()
    target = None
    for s in master_students:
        if s['uid'] == uid:
            target = s
            break
    if not target: return "<h1>ไม่พบข้อมูลนักเรียน</h1>"
    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar"><h1><img src="{LOGO_URL}" class="nav-logo"> 📝 แก้ไขข้อมูลนักเรียนประจำทะเบียนหลัก</h1><a href="/admin/students" class="btn btn-secondary">⬅ กลับ</a></div>
        <div class="main-container">
            <div class="card">
                <form action="/api/admin/edit_student" method="post">
                    <input type="hidden" name="old_uid" value="{uid}">
                    <label>ชื่อ-นามสกุล:</label><input type="text" name="student_name" value="{target['name']}" required>
                    <label>เลขที่ประจำตัว:</label><input type="text" name="student_no" value="{target['no']}" required>
                    <label>ระดับชั้นเรียน:</label><input type="text" name="classroom" value="{target['class']}" required>
                    <label>สาขาวิชาเอก:</label><input type="text" name="branch" value="{target['branch']}" required>
                    <button type="submit" class="btn-submit">💾 บันทึกการเปลี่ยนแปลง</button>
                </form>
            </div>
        </div>
    </body></html>
    """

@app.post("/api/admin/edit_student")
async def api_edit_student(old_uid: str = Form(...), student_name: str = Form(...), student_no: str = Form(...), classroom: str = Form(...), branch: str = Form(...), user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return HTMLResponse("Unauthorized", status_code=401)
    lines_to_keep = []
    if os.path.exists(TXT_DATABASE_PATH):
        with open(TXT_DATABASE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() and "," in line:
                    parts = line.split(",")
                    curr_uid = f"{parts[0].strip()}_{parts[1].strip()}"
                    if curr_uid != old_uid: lines_to_keep.append(line)
    new_line = f"{student_name.strip()}, {student_no.strip()}, {classroom.strip()}, {branch.strip()}\n"
    lines_to_keep.append(new_line)
    with open(TXT_DATABASE_PATH, "w", encoding="utf-8") as f: f.writelines(lines_to_keep)
    return alert_redirect("แก้ไขข้อมูลนักเรียนเรียบร้อยแล้ว", type="success", url="/admin/students")

@app.get("/api/admin/delete_student")
async def api_delete_student(uid: str, user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return RedirectResponse(url="/login", status_code=303)
    lines_to_keep = []
    if os.path.exists(TXT_DATABASE_PATH):
        with open(TXT_DATABASE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() and "," in line:
                    parts = line.split(",")
                    curr_uid = f"{parts[0].strip()}_{parts[1].strip()}"
                    if curr_uid != uid: lines_to_keep.append(line)
    return RedirectResponse(url="/admin/students", status_code=303)

# ==========================================
# 🎯 [DYNAMIC ASSIGNMENT SYSTEM] 
# ==========================================
@app.get("/admin/grades_visibility", response_class=HTMLResponse)
async def admin_grades_visibility_page(selected_group_id: str = None, user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return RedirectResponse(url="/login", status_code=303)
    int_group_id = None
    if selected_group_id and selected_group_id.strip() != "":
        try: int_group_id = int(selected_group_id)
        except ValueError: int_group_id = None

    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute('SELECT group_id, group_name, grades_visibility FROM course_groups ORDER BY group_name')
    all_groups = cursor.fetchall()

    group_options = "<option value=''>-- เลือกกลุ่มวิชาที่ต้องการตั้งค่า --</option>"
    vis_map = {}
    for g_id, g_name, vis in all_groups:
        vis_map[g_id] = vis or "hidden"
        is_sel = "selected" if int_group_id and g_id == int_group_id else ""
        icon = {"all": "🟢", "hidden": "🔒", "custom": "🟡"}.get(vis or "hidden", "🔒")
        group_options += f"<option value='{g_id}' {is_sel}>{icon} {g_name}</option>"

    current_section = ""
    if int_group_id and int_group_id in vis_map:
        current_vis = vis_map[int_group_id]
        cursor.execute("SELECT student_uid FROM group_assignments WHERE group_id=?", (int_group_id,))
        assigned_uids = {r[0] for r in cursor.fetchall()}
        cursor.execute("SELECT student_uid FROM grade_visible_students WHERE group_id=?", (int_group_id,))
        custom_allowed = {r[0] for r in cursor.fetchall()}
        class_students = [s for s in get_sorted_master_students() if s['uid'] in assigned_uids]

        student_checkboxes = ""
        for s in class_students:
            is_checked = "checked" if s['uid'] in custom_allowed else ""
            student_checkboxes += f"""
            <div class="checkbox-container">
                <input type="checkbox" class="gv-check" value="{s['uid']}" id="gv_{s['uid']}" {is_checked}>
                <label for="gv_{s['uid']}" style="cursor:pointer; font-size:14px; width:100%; font-weight:500;">
                    <span class="badge" style="margin-right:6px;">ชั้น {s['class']}</span> เลขที่ <b>{s['no']}</b> — {s['name']}
                </label>
            </div>"""

        current_section = f"""
        <div class="card" style="margin-top:20px;">
            <h2>👁️ ตั้งค่าการมองเห็นคะแนน</h2>
            <form action="/api/admin/grades_visibility/set_mode" method="post">
                <input type="hidden" name="group_id" value="{int_group_id}">
                <label style="font-size:12.5px;font-weight:700;color:#475569;">โหมดการมองเห็น:</label>
                <select name="mode" required>
                    <option value="hidden" {"selected" if current_vis == "hidden" else ""}>🔒 ปิด — นักเรียนดูไม่ได้เลย</option>
                    <option value="all" {"selected" if current_vis == "all" else ""}>🟢 เปิด — นักเรียนดูได้ทุกคน</option>
                    <option value="custom" {"selected" if current_vis == "custom" else ""}>🟡 กำหนดเอง — เลือกได้เฉพาะบางคน</option>
                </select>
                <button type="submit" class="btn-submit">💾 บันทึกโหมด</button>
            </form>

            <div style="margin-top:18px; {"opacity:0.4; pointer-events:none;" if current_vis != "custom" else ""}">
                <p style="font-size:12.5px; color:#a16207; font-weight:700; margin-bottom:10px;">
                    🟡 ใช้ได้เมื่อเลือกโหมด "กำหนดเอง" เท่านั้น — ติ๊กเฉพาะนักเรียนที่อนุญาตให้ดูคะแนนวิชานี้
                </p>
                <form action="/api/admin/grades_visibility/set_custom_list" method="post" onsubmit="return packVisibleStudents(this);">
                    <input type="hidden" name="group_id" value="{int_group_id}">
                    <input type="hidden" name="visible_students_csv" id="visible_students_csv">
                    <div style="max-height:400px; overflow-y:auto; border:1px solid #e2e8f0; border-radius:8px; padding:8px;">
                        {student_checkboxes if student_checkboxes else "<p style='color:#94a3b8;text-align:center;padding:10px;'>ยังไม่มีนักเรียนในกลุ่มนี้</p>"}
                    </div>
                    <button type="submit" class="btn-submit" style="margin-top:10px;">💾 บันทึกรายชื่อที่อนุญาต</button>
                </form>
            </div>
        </div>
        <script>
        function packVisibleStudents(form) {{
            // ✅ รวมรายชื่อ uid ที่ติ๊กเป็น field เดียว (คั่นด้วย comma) แทนการยิง checkbox แยกทีละคน
            // ป้องกันปัญหาฟอร์มมี field เกิน 1000 ช่องเวลากลุ่มวิชามีนักเรียนจำนวนมาก
            const checked = Array.from(form.querySelectorAll('.gv-check:checked')).map(el => el.value);
            document.getElementById('visible_students_csv').value = checked.join(',');
            return true;
        }}
        </script>"""

    conn.close()

    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> 👁️ จัดการการมองเห็นคะแนน</h1>
            <a href="/admin/dashboard" class="btn btn-secondary">⬅ กลับหน้าหลัก</a>
        </div>
        <div class="main-container">
            <div class="card">
                <h2>เลือกกลุ่มวิชาเรียน</h2>
                <label style="font-size:12.5px; color:#475569; font-weight:700;">กลุ่มวิชา:</label>
                <select onchange="location.href='/admin/grades_visibility?selected_group_id='+this.value;" style="border: 2px solid #1e3a8a; font-weight:700;">
                    {group_options}
                </select>
                <p style="font-size:12px;color:#94a3b8;margin-top:10px;">
                    🟢 เปิด = นักเรียนทุกคนในกลุ่มดูคะแนนวิชานี้ได้ · 🔒 ปิด = ดูไม่ได้เลย · 🟡 กำหนดเอง = เลือกได้เฉพาะบางคน
                </p>
            </div>
            {current_section}
        </div>
    </body></html>
    """

@app.post("/api/admin/grades_visibility/set_mode")
async def api_admin_grades_visibility_set_mode(group_id: int = Form(...), mode: str = Form(...), user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return HTMLResponse("Unauthorized", status_code=401)
    if mode not in ("all", "hidden", "custom"):
        return alert_redirect("โหมดไม่ถูกต้อง", type="error", url=f"/admin/grades_visibility?selected_group_id={group_id}")
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE course_groups SET grades_visibility=? WHERE group_id=?", (mode, group_id))
    conn.commit()
    conn.close()
    return alert_redirect("บันทึกโหมดการมองเห็นคะแนนเรียบร้อยแล้ว", type="success", url=f"/admin/grades_visibility?selected_group_id={group_id}")

@app.post("/api/admin/grades_visibility/set_custom_list")
async def api_admin_grades_visibility_set_custom_list(group_id: int = Form(...), visible_students_csv: str = Form(""), user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return HTMLResponse("Unauthorized", status_code=401)
    allowed_uids = [u for u in visible_students_csv.split(",") if u.strip()]
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM grade_visible_students WHERE group_id=?", (group_id,))
    for uid in allowed_uids:
        cursor.execute("INSERT OR IGNORE INTO grade_visible_students (group_id, student_uid) VALUES (?, ?)", (group_id, uid))
    conn.commit()
    conn.close()
    return alert_redirect("บันทึกรายชื่อที่อนุญาตให้ดูคะแนนเรียบร้อยแล้ว", type="success", url=f"/admin/grades_visibility?selected_group_id={group_id}")

@app.get("/admin/assign_groups", response_class=HTMLResponse)
async def admin_assign_groups_page(selected_group_id: str = None, class_filter: str = None, user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return RedirectResponse(url="/login", status_code=303)
    int_group_id = None
    if selected_group_id and selected_group_id.strip() != "":
        try: int_group_id = int(selected_group_id)
        except ValueError: int_group_id = None

    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, fullname FROM teachers")
    teachers = cursor.fetchall()
    cursor.execute('SELECT group_id, group_name FROM course_groups')
    course_groups = cursor.fetchall()
    
    active_assigned_uids = []
    if int_group_id:
        cursor.execute("SELECT student_uid FROM group_assignments WHERE group_id = ?", (int_group_id,))
        active_assigned_uids = [r[0] for r in cursor.fetchall()]
    conn.close()

    master_students = get_sorted_master_students()
    # ดึงรายชื่อห้องทั้งหมด
    all_classes = sorted(list(set(s['class'] for s in master_students)))
    class_options_filter = '<option value="">-- แสดงทุกห้อง --</option>'
    for c in all_classes:
        sel = 'selected' if class_filter == c else ''
        class_options_filter += f'<option value="{c}" {sel}>ชั้น {c}</option>'
    # กรองนักเรียนตามห้อง (ถ้ามีการเลือก)
    display_students = master_students
    if class_filter:
        display_students = [s for s in master_students if s['class'] == class_filter]
    teacher_options = "".join([f"<option value='{t[0]}'>ครู {t[1]}</option>" for t in teachers])
    
    group_options = "<option value=''>-- เลือกวิชาที่ต้องการปรับปรุงรายชื่อเด็ก --</option>"
    for g in course_groups:
        is_sel = "selected" if int_group_id and g[0] == int_group_id else ""
        group_options += f"<option value='{g[0]}' {is_sel}>{g[1]}</option>"

    student_checkboxes = ""
    for s in display_students:
        is_checked = "checked" if s['uid'] in active_assigned_uids else ""
        student_checkboxes += f"""
        <div class="checkbox-container">
            <input type="checkbox" name="assigned_students" value="{s['uid']}" id="st_{s['uid']}" {is_checked}>
            <label for="st_{s['uid']}" style="cursor:pointer; font-size:14px; width:100%; font-weight:500;">
                <span class="badge" style="margin-right:6px;">ชั้น {s['class']}</span> เลขที่ <b>{s['no']}</b> — {s['name']}
            </label>
        </div>
        """

    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar">
            <h1>🎯 การจัดแยกสายรายชื่อเข้ากลุ่มวิชาเรียนคลาส</h1>
            <a href="/admin/dashboard" class="btn btn-secondary">⬅ กลับหน้าหลัก</a>
        </div>
        <div class="main-container">
            <div class="card">
                <h2>✨ การบริหารจัดการกลุ่มรายวิชาและกิจกรรม</h2>
                <form action="/api/admin/create_group" method="post">
                    <input type="text" name="group_name" placeholder="ชื่อวิชาเรียน เช่น: คลาสวิชาดิจิทัล, ทักษะโขน ม.2" required>
                    <input type="text" name="branch" placeholder="สังกัดสาขาวิชาเอก เช่น: โขน" required>
                    <select name="teacher_username" required>{teacher_options}</select>
                    <button type="submit" class="btn-submit">⚡ ยืนยันการเพิ่มกลุ่มรายวิชา</button>
                </form>
            </div>
            
            <div class="card" style="margin-top: 24px;">
                <h2>🎯 ส่วนแก้ไข/อัปเดต: เลือกกลุ่มวิชาเพื่อปรับปรุงรายชื่อนักเรียน</h2>
                <label style="font-size:12.5px; color:#475569; font-weight:700;">เลือกรอบวิชาเรียนที่จะตรวจรายชื่อสิทธิ์:</label>
                <select id="group_selector" onchange="location.href='/admin/assign_groups?selected_group_id='+this.value;" style="border: 2px solid #1e3a8a; font-weight:700;">
                    {group_options}
                </select>
                
                {f'''
                <form action="/api/admin/assign_students_to_group" method="post" style="margin-top:15px;">
                    <input type="hidden" name="group_id" value="{int_group_id}">
                    <p style="font-size:13px; color:#f59e0b; font-weight:700; margin-bottom:10px;">💡 เลือกนักเรียนที่ต้องการเพิ่มหรือถอดถอนออกจากกลุ่มวิชา แล้วกดบันทึกได้เลย</p>
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px; background:#f8fafc; padding:10px; border-radius:8px; border:1px solid #e2e8f0;">
                        <span style="font-size:13px; font-weight:700; color:#1e3a8a;">🔍 เลือกดูเฉพาะห้อง:</span>
                        <select onchange="let gid = document.getElementById('group_selector').value; location.href='/admin/assign_groups?selected_group_id='+gid+'&class_filter='+this.value;" style="flex:1; padding:6px; border-radius:6px; border:1px solid #cbd5e1; font-family:'Sarabun'; font-size:13px; font-weight:600;">
                            {class_options_filter}
                        </select>
                    </div>
                    <div style="border:1px solid #cbd5e1; border-radius:10px; max-height:400px; overflow-y:auto; padding:10px; background-color:#fff; margin-bottom:18px;">
                        {student_checkboxes}
                    </div>
                    <button type="submit" class="btn-submit" style="background: linear-gradient(135deg, #10b981, #059669); border-bottom-color:#047857;">💾 บันทึกการจัดสรรนักเรียน</button>
                </form>
                ''' if int_group_id else "<p style='text-align:center; padding:20px; color:#64748b; font-size:13.5px;'>โปรดเลือกรายวิชาเพื่อดำเนินการจัดการข้อมูลนักเรียน</p>"}
        </div>
    </body></html>
    """

@app.get("/app/history", response_class=HTMLResponse)
async def app_history_page(user: str, group_id: Optional[str] = None, user_session: Optional[str] = Cookie(None)):
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}": return RedirectResponse(url="/login", status_code=303)
    m_cfg = get_maintenance_status()
    if m_cfg["is_active"] == 1: return generate_maintenance_html(m_cfg["mode_type"])
    
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    my_groups = []
    distinct_dates = []
    selected_group_name = ""
    
    try:
        cursor.execute("SELECT group_id, group_name FROM course_groups WHERE teacher_username = ?", (user,))
        my_groups = cursor.fetchall()
        if group_id:
            cursor.execute("SELECT group_name FROM course_groups WHERE group_id = ?", (group_id,))
            g_res = cursor.fetchone()
            if g_res:
                selected_group_name = g_res[0]
                cursor.execute("SELECT DISTINCT date FROM attendance_logs WHERE group_name = ? ORDER BY log_id DESC", (selected_group_name,))
                distinct_dates = [r[0] for r in cursor.fetchall()]
    except Exception as e: print(f"❌ Fetch History Error: {e}")
    finally: conn.close()

    group_options = "<option value=''>-- เลือกคลาสวิชาเรียน --</option>"
    for g in my_groups:
        is_sel = "selected" if group_id and int(group_id) == g[0] else ""
        group_options += f"<option value='{g[0]}' {is_sel}>{g[1]}</option>"

    date_list_items = ""
    for d in distinct_dates:
        target_detail_url = f"/app/history/detail?user={user}&group_name={selected_group_name}&date={d}"
        date_list_items += f"""
        <a href="{target_detail_url}" style="text-decoration:none; display:flex; justify-content:space-between; align-items:center; padding:14px; border:1px solid #cbd5e1; margin-bottom:10px; border-radius:8px; background:white; color:#0f172a;">
            <span style="font-weight:600; font-size:14.5px;">📅 รอบวันที่: {d}</span>
            <span style="color:#1e3a8a; font-size:13px; font-weight:700;">เปิดดูใบเช็คชื่อ ➔</span>
        </a>
        """

    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar">
            <h1>📊 คลังประวัติใบเช็คชื่อย้อนหลัง</h1>
            <a href="/app/dashboard?user={user}" class="btn btn-secondary">⬅ กลับหน้าหลัก</a>
        </div>
        <div class="main-container">
            <div class="card">
                <h2>🔍 เลือกวิชาเพื่อเรียกดูประวัติ</h2>
                <label style="font-size:12.5px; color:#475569; font-weight:700;">คลาสวิชาเรียนเอก:</label>
                <select onchange="location.href='/app/history?user={user}&group_id='+this.value;">
                    {group_options}
                </select>
            </div>
            {f'''
            <div class="card">
                <h2>📅 รายการรอบวันที่บันทึกไว้ของวิชา: {selected_group_name}</h2>
                <div style="margin-top:10px;">
                    {date_list_items if date_list_items else "<p style='color:gray; text-align:center; padding:10px;'>ยังไม่เคยมีประวัติการเช็คชื่อในวิชานี้</p>"}
                </div>
            </div>
            ''' if group_id else ""}
        </div>
    </body></html>
    """

@app.get("/app/history/detail", response_class=HTMLResponse)
async def app_history_detail_page(user: str, group_name: str, date: str, user_session: Optional[str] = Cookie(None)):
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}": return RedirectResponse(url="/login", status_code=303)
    m_cfg = get_maintenance_status()
    if m_cfg["is_active"] == 1: return generate_maintenance_html(m_cfg["mode_type"])
    
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    logs = []
    stats = {"มา": 0, "สาย": 0, "ลา": 0, "ขาด": 0}
    checked_by_name = "ไม่ระบุ"
    
    try:
        cursor.execute("SELECT student_name, student_no, classroom, status, checked_by FROM attendance_logs WHERE group_name = ? AND date = ?", (group_name, date))
        logs = cursor.fetchall()
        for row in logs:
            if row[3] in stats: stats[row[3]] += 1
            checked_by_name = row[4]
    except Exception as e: print(f"❌ Detail Error: {e}")
    finally: conn.close()

    table_rows = ""
    for row in logs:
        s_name, s_no, s_class, s_status, _ = row
        status_color = "#10b981" if s_status == "มา" else "#f59e0b" if s_status == "สาย" else "#3b82f6" if s_status == "ลา" else "#ef4444"
        table_rows += f"""
        <tr>
            <td><span class="badge">{s_class}</span></td>
            <td><b>{s_no}</b></td>
            <td><div style="text-align:left; font-weight:600; color:#0f172a;">{s_name}</div></td>
            <td><span style="background-color:{status_color}; color:white; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:700;">{s_status}</span></td>
        </tr>
        """

    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar">
            <h1>📋 รายละเอียดใบเช็คชื่อประจำห้อง</h1>
            <a href="javascript:history.back();" class="btn btn-secondary">⬅ ย้อนกลับ</a>
        </div>
        <div class="main-container">
            <div class="card" style="background: linear-gradient(135deg, #0f172a, #1e293b); color: white;">
                <h2 style="color: #fff; border-bottom: 2px solid #d4af37;">📘 ข้อมูลแผ่นบันทึกคลาส</h2>
                <p style="margin: 6px 0; font-size: 14px;"><b>วิชาเรียน:</b> {group_name}</p>
                <p style="margin: 6px 0; font-size: 14px;"><b>ประจำรอบวันที่:</b> {date}</p>
                <p style="margin: 6px 0; font-size: 14px; color:#cbd5e1;"><b>อาจารย์ผู้ตรวจ:</b> {checked_by_name}</p>
                <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:8px; margin-top:15px; text-align:center;">
                    <div style="background:#10b981; padding:8px; border-radius:6px;">มา<br><b>{stats['มา']}</b></div>
                    <div style="background:#f59e0b; padding:8px; border-radius:6px;">สาย<br><b>{stats['สาย']}</b></div>
                    <div style="background:#3b82f6; padding:8px; border-radius:6px;">ลา<br><b>{stats['ลา']}</b></div>
                    <div style="background:#ef4444; padding:8px; border-radius:6px;">ขาด<br><b>{stats['ขาด']}</b></div>
                </div>
            </div>
            <div class="card">
                <h2>👥 บัญชีรายชื่อและสถานะการเข้าเรียน</h2>
                <div style="overflow-x:auto; border-radius:8px; border:1px solid #e2e8f0;">
                    <table>
                        <thead><tr><th>ชั้นเรียน</th><th>เลขที่</th><th>ชื่อ-นามสกุล</th><th>สถานะ</th></tr></thead>
                        <tbody>{table_rows if table_rows else "<tr><td colspan='4'>ไม่พบข้อมูลนักเรียน</td></tr>"}</tbody>
                    </table>
                </div>
            </div>
        </div>
    </body></html>
    """

@app.get("/app/rollcall/{group_id}", response_class=HTMLResponse)
async def app_rollcall_sheet(group_id: int, user: str, user_session: Optional[str] = Cookie(None)):
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}": return RedirectResponse(url="/login", status_code=303)
    m_cfg = get_maintenance_status()
    if m_cfg["is_active"] == 1: return generate_maintenance_html(m_cfg["mode_type"])

    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT group_name FROM course_groups WHERE group_id = ?", (group_id,))
    res_g = cursor.fetchone()
    if not res_g:
        conn.close()
        return "<h1>ไม่พบกลุ่มวิชาเรียนนี้</h1>"
    group_name = res_g[0]
    cursor.execute('SELECT student_uid FROM group_assignments WHERE group_id = ?', (group_id,))
    assigned_uids = [r[0] for r in cursor.fetchall()]
    conn.close()

    master_students = get_sorted_master_students()
    students_in_class = [s for s in master_students if s['uid'] in assigned_uids]
    today_val = datetime.now().strftime("%d/%m/%Y")
    default_today_input = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT checked_by FROM attendance_logs WHERE group_name = ? AND date = ? LIMIT 1", (group_name, today_val))
    already_checked = cursor.fetchone()
    
    cursor.execute("SELECT student_name, student_no, reason FROM leave_requests WHERE group_id = ? AND leave_date = ? AND status = 'approved'", (group_id, default_today_input))
    approved_leaves = {(r[0], r[1]): r[2] for r in cursor.fetchall()}
    conn.close()

    admin_notif = ""
    if already_checked:
        checker = already_checked[0]
        admin_notif = f"""
        <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 12px; padding: 15px; margin-bottom: 20px; display: flex; align-items: center; gap: 12px; color: #f59e0b;">
            <div style="font-size: 24px;">👑</div>
            <div style="flex: 1;">
                <div style="font-weight: 800; font-size: 14px;">ระบบได้บันทึกข้อมูลเรียบร้อยแล้วสำหรับวันนี้</div>
                <div style="font-size: 12.5px; opacity:0.8;">ผู้เช็กข้อมูลวันนี้: <b>{checker}</b></div>
            </div>
        </div>
        """

    student_items = ""
    for idx, s in enumerate(students_in_class):
        # ✅ ใช้ uid ของนักเรียนเป็น key โดยตรง แทนการยิง hidden field name_/no_/class_/selected_students
        # แยกต่างหากทีละคน (เดิมคนละ 5 field ต่อคน) เพราะถ้าห้อง/กลุ่มมีนักเรียนเยอะ (เช่น 200+ คน)
        # จะรวมกันเกิน 1000 field ต่อฟอร์ม แล้วโดน Starlette ปฏิเสธด้วย error
        # "Too many fields. Maximum number of fields is 1000." ตอนนี้เหลือแค่ 1 field ต่อคน
        # ส่วนชื่อ/เลขที่/ห้อง จะไปดึงจากฐานข้อมูลนักเรียนซ้ำอีกทีตอน submit แทน
        key_id = s['uid']
        leave_reason = approved_leaves.get((s['name'], s['no']))
        
        status_selection = ""
        if leave_reason:
            status_selection = f"""
            <div style="display:flex; align-items:center; gap:10px; padding: 5px 0;">
                <span style="background:#3b82f6; color:white; padding:6px 14px; border-radius:8px; font-weight:800; font-size:13px; box-shadow:0 2px 4px rgba(59,130,246,0.2);">✅ ลา (อนุมัติแล้ว)</span>
                <span style="background:#eff6ff; color:#1e40af; padding:5px 10px; border-radius:6px; font-size:12px; border:1px solid #bfdbfe; font-weight:600;">🏷️ {leave_reason}</span>
            </div>
            <input type="hidden" id="radio_la_{key_id}" name="status_{key_id}" value="ลา">
            """
        else:
            status_selection = f"""
            <div class="status-group" data-student-name="{s['name']}" data-student-no="{s['no']}">
                <input type="radio" id="status_ma_{key_id}" name="status_{key_id}" value="มา" checked>
                <label for="status_ma_{key_id}" class="status-label label-ma">มา</label>
                <input type="radio" id="status_sai_{key_id}" name="status_{key_id}" value="สาย">
                <label for="status_sai_{key_id}" class="status-label label-sai">สาย</label>
                <input type="radio" id="status_khad_{key_id}" name="status_{key_id}" value="ขาด">
                <label for="status_khad_{key_id}" class="status-label label-khad">ขาด</label>
                <input type="radio" id="status_la_{key_id}" name="status_{key_id}" value="ลา">
                <label for="status_la_{key_id}" class="status-label label-la">ลา</label>
            </div>
            """

        student_items += f"""
        <div class="student-row-card" id="row_{s['no']}" style="padding:14px; border-bottom:1px solid rgba(255,255,255,0.06); transition: background 0.3s;">
            <div style="margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <b style="color:#fff; font-size:15px;">{s['name']}</b>
                    <span style="font-size:12.5px; color:var(--text-soft); font-weight:600; margin-left:6px;">
                        เลขที่ {s['no']}
                    </span>
                </div>
                <span class="badge" style="padding:2px 6px; font-size:10.5px; background:rgba(37,99,235,0.15); border:1px solid rgba(37,99,235,0.3); color:#60a5fa;">{s['class']}</span>
            </div>
            {status_selection}
        </div>
        """

    return f"""
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>เช็กชื่อวิชา {group_name} | K-School</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sarabun:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --navy-900: #020617;
            --navy-800: #0f172a;
            --navy-700: #1e293b;
            --navy-600: #2563eb;
            --gold: #d4af37;
            --gold-light: #f2d879;
            --surface: rgba(255, 255, 255, 0.05);
            --border: rgba(255, 255, 255, 0.1);
            --text: #f8fafc;
            --text-soft: #94a3b8;
            --radius: 16px;
        }}
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{
            font-family:'Sarabun', 'Inter', sans-serif;
            background: radial-gradient(circle at top, #0f172a 0%, #020617 100%);
            color: var(--text);
            min-height: 100vh;
        }}
        
        .navbar {{
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(12px);
            border-bottom: 2px solid var(--gold);
            padding: 14px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .navbar h1 {{
            font-size: 16px;
            font-weight: 700;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .nav-logo {{ height: 30px; width: auto; }}
        .btn-back {{
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            color: #cbd5e1;
            padding: 6px 14px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 700;
            font-size: 13px;
            transition: all 0.2s;
        }}
        .btn-back:hover {{ background: rgba(255,255,255,0.15); }}
        
        .main-container {{
            max-width: 650px;
            margin: 0 auto;
            padding: 20px 16px 100px;
        }}
        
        .card {{
            background: rgba(15, 23, 42, 0.55);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        }}
        
        .card h2 {{
            font-size: 15px;
            font-weight: 700;
            color: #fff;
            border-bottom: 2px solid rgba(255,255,255,0.08);
            padding-bottom: 12px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        /* ─── STATUS SELECTOR ─── */
        .status-group {{
            display: flex;
            gap: 4px;
            border: 1px solid rgba(255,255,255,0.08);
            padding: 3px;
            border-radius: 12px;
            background-color: rgba(2, 6, 23, 0.4);
        }}
        .status-label {{
            flex: 1;
            text-align: center;
            font-size: 13px;
            font-weight: 700;
            padding: 8px 10px;
            border-radius: 9px;
            cursor: pointer;
            transition: all 0.15s;
            color: var(--text-soft);
            border: 1px solid transparent;
        }}
        .status-group input[type="radio"] {{ display: none; }}
        
        .status-group input[type="radio"][value="มา"]:checked + .status-label {{ background: linear-gradient(135deg, #10b981, #059669); color: white; box-shadow: 0 3px 8px rgba(16,185,129,0.3); }}
        .status-group input[type="radio"][value="สาย"]:checked + .status-label {{ background: linear-gradient(135deg, #f59e0b, #d97706); color: white; box-shadow: 0 3px 8px rgba(245,158,11,0.3); }}
        .status-group input[type="radio"][value="ขาด"]:checked + .status-label {{ background: linear-gradient(135deg, #ef4444, #dc2626); color: white; box-shadow: 0 3px 8px rgba(239,68,68,0.3); }}
        .status-group input[type="radio"][value="ลา"]:checked + .status-label {{ background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; box-shadow: 0 3px 8px rgba(59,130,246,0.3); }}
        
        /* ─── BUTTONS ─── */
        .btn-submit {{
            background: linear-gradient(135deg, var(--gold), #b8962e);
            color: #020617;
            width: 100%;
            padding: 14.5px;
            font-size: 15px;
            font-weight: 800;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            border-bottom: 3px solid #8a6e1e;
            box-shadow: 0 6px 16px rgba(212, 175, 55, 0.15);
            font-family: 'Sarabun', sans-serif;
            letter-spacing: 0.3px;
            transition: all 0.15s;
        }}
        .btn-submit:active {{
            transform: translateY(2px);
            border-bottom-width: 1px;
        }}
        
        .btn-otp-trigger {{
            background: linear-gradient(135deg, #a78bfa, #7c3aed);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 14px;
            width: 100%;
            font-size: 14.5px;
            font-weight: 800;
            cursor: pointer;
            border-bottom: 3px solid #5b21b6;
            margin-bottom: 20px;
            box-shadow: 0 6px 16px rgba(124, 58, 237, 0.25);
            font-family: 'Sarabun', sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.15s;
        }}
        .btn-otp-trigger:active {{
            transform: translateY(2px);
            border-bottom-width: 1px;
        }}
        
        /* ─── DYNAMIC OTP MODAL ─── */
        .otp-modal {{
            position: fixed;
            inset: 0;
            background: rgba(2, 6, 23, 0.85);
            backdrop-filter: blur(10px);
            z-index: 999;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .otp-modal.active {{
            display: flex;
        }}
        .otp-card {{
            background: rgba(15, 23, 42, 0.9);
            border: 2px solid var(--gold);
            border-radius: 24px;
            width: 100%;
            max-width: 460px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 30px 60px rgba(0,0,0,0.6);
            animation: modalPop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        }}
        @keyframes modalPop {{
            from {{ transform: scale(0.85); opacity: 0; }}
            to {{ transform: scale(1); opacity: 1; }}
        }}
        .otp-code-display {{
            font-size: 54px;
            font-weight: 800;
            color: var(--gold-light);
            letter-spacing: 8px;
            margin: 15px 0;
            text-shadow: 0 0 12px rgba(242, 216, 121, 0.5);
            font-family: 'Inter', sans-serif;
        }}
        .qr-placeholder {{
            background: white;
            padding: 10px;
            border-radius: 12px;
            display: inline-block;
            margin: 15px auto;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }}
        .qr-placeholder img {{
            display: block;
            width: 160px;
            height: 160px;
        }}
        .countdown-timer {{
            font-size: 16px;
            font-weight: 700;
            color: #f87171;
            margin-bottom: 20px;
        }}
        .checked-in-counter {{
            background: rgba(255,255,255,0.06);
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 20px;
            font-size: 14px;
            font-weight: 700;
        }}
        .checked-in-list {{
            max-height: 120px;
            overflow-y: auto;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            padding: 10px;
            font-size: 12.5px;
            text-align: left;
            margin-bottom: 20px;
        }}
        .checked-in-item {{
            padding: 4px 6px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            color: #10b981;
            display: flex;
            justify-content: space-between;
            animation: slideIn 0.3s ease-out;
        }}
        @keyframes slideIn {{
            from {{ transform: translateY(10px); opacity:0; }}
            to {{ transform: translateY(0); opacity:1; }}
        }}
        .btn-close-otp {{
            background: #ef4444;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 11px 24px;
            font-size: 13.5px;
            font-weight: 700;
            cursor: pointer;
            font-family: 'Sarabun', sans-serif;
            border-bottom: 3px solid #b91c1c;
        }}
        .btn-close-otp:active {{ transform: translateY(1px); }}
        
        .badge {{
            background: rgba(255,255,255,0.1);
            color: var(--gold-light);
            border: 1px solid rgba(212, 175, 55, 0.3);
            border-radius: 20px;
        }}
    </style>
</head>
<body>

<div class="navbar">
    <h1><img src="{LOGO_URL}" class="nav-logo"> เช็กชื่อคลาสเรียน</h1>
    <a href="/app/dashboard?user={user}" class="btn-back">⬅ กลับหน้าบอร์ด</a>
</div>

<div class="main-container">
    {admin_notif}
    
    <!-- ปุ่มเปิดระบบสแกนเช็กชื่ออัตโนมัติ -->
    <button class="btn-otp-trigger" onclick="openOTPModal()">
        <span>⚡ เปิดลงทะเบียนเช็กชื่อด่วน (OTP / QR Code)</span>
    </button>
    
    <form action="/app/api/submit_attendance" method="post">
        <input type="hidden" name="group_name" value="{group_name}">
        <input type="hidden" name="teacher_user" value="{user}">
        
        <div class="card">
            <h2>📅 วันที่เช็กชื่อคลาสเรียน</h2>
            <input type="date" name="target_date" value="{default_today_input}" style="width:100%; padding:12px; border-radius:10px; border:1px solid rgba(255,255,255,0.15); background:rgba(0,0,0,0.3); color:#fff; font-family:'Sarabun'; font-weight:600; outline:none;" required>
        </div>
        
        <div class="card" style="padding:10px 0;">
            <h2 style="padding:0 20px 12px; margin-bottom:0;">👥 รายชื่อนักเรียนทั้งหมด</h2>
            {student_items if student_items else "<p style='color:gray; padding:20px; text-align:center;'>ยังไม่มีรายชื่อนักเรียนจัดเข้ากลุ่มเรียนนี้</p>"}
        </div>
        
        <button type="submit" class="btn-submit">💾 บันทึกรายงานเข้าคลังและแจ้งเตือน Discord</button>
    </form>
</div>

<!-- หน้าต่างป๊อปอัพ OTP/QR Code -->
<div class="otp-modal" id="otpModal">
    <div class="otp-card">
        <h3 style="font-size:18px; font-weight:800; color:#fff;">⚡ โหมดลงทะเบียนเช็กชื่อด่วน</h3>
        <p style="font-size:13px; color:var(--text-soft); margin-top:4px;">เปิดให้นักเรียนสแกน QR Code หรือกรอกรหัสจากหน้าจอนี้</p>
        
        <div class="otp-code-display" id="otpDisplay">0000</div>
        
        <div class="qr-placeholder">
            <!-- สร้าง QR Code อัตโนมัติจาก API -->
            <img id="qrDisplay" src="" alt="QR Code Link">
        </div>
        
        <div class="countdown-timer" id="timerDisplay">⏱️ เหลือเวลาเปิดรับ: 05:00 นาที</div>
        
        <div class="checked-in-counter">
            👨‍🎓 เช็กอินสำเร็จแล้ว: <span id="checkinCount" style="color:var(--gold-light);">0</span> คน
        </div>
        
        <div class="checked-in-list" id="checkinList">
            <!-- รายชื่อนักเรียนจะแสดงผลเรียลไทม์ที่นี่ -->
            <p style="color:gray; text-align:center; margin-top:25px;" id="emptyCheckinMsg">ยังไม่มีนักเรียนลงชื่อเข้ามา</p>
        </div>
        
        <button class="btn-close-otp" onclick="closeOTPModal()">🛑 ปิดโหมดลงทะเบียนด่วน</button>
    </div>
</div>

<!-- เสียงบี๊บแจ้งเตือนเมื่อนักเรียนเช็กอิน -->
<audio id="beepSound" src="https://assets.mixkit.co/active_storage/sfx/2869/2869-84.wav" preload="auto"></audio>

<script>
const activeGroupId = {group_id};
let timerInterval = null;
let currentOtp = "";

// เชื่อมต่อ WebSocket เรียลไทม์สำหรับรับข้อมูลนักเรียนที่สแกนเช็กชื่อ
let rcReconnectDelay = 1500;
function setupRollcallSocket() {{
    const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
    const wsUrl = protocol + window.location.host + "/ws/maintenance";
    const ws = new WebSocket(wsUrl);

    ws.onopen = function() {{ rcReconnectDelay = 1500; }};
    
    ws.onmessage = function(event) {{
        try {{
            const data = JSON.parse(event.data);
            if (data.type === "student_checked_in" && data.group_id === activeGroupId) {{
                // เล่นเสียงแจ้งเตือนสั้นๆ
                try {{ document.getElementById('beepSound').play(); }} catch(e) {{}}
                
                // ซ่อนข้อความว่างเปล่า
                const emptyMsg = document.getElementById('emptyCheckinMsg');
                if (emptyMsg) emptyMsg.style.display = 'none';
                
                // เพิ่มชื่อเข้าในลิสต์เรียลไทม์
                const list = document.getElementById('checkinList');
                const item = document.createElement('div');
                item.className = 'checked-in-item';
                item.innerHTML = `
                    <span>เลขที่ ${{data.student_no}} ${{data.student_name}}</span>
                    <span style="font-weight:bold;">🟢 มาเรียน</span>
                `;
                list.insertBefore(item, list.firstChild);
                
                // อัปเดตยอดรวม
                const countEl = document.getElementById('checkinCount');
                let curCount = parseInt(countEl.textContent);
                countEl.textContent = curCount + 1;
                
                // อัปเดตตารางเช็กชื่อด้านหลัง (ติ๊กช่อง "มา" ให้นักเรียนคนนั้น)
                // ค้นหา status-group ของนักเรียนและตั้งค่าปุ่มวิทยุ (radio) เป็น "มา"
                // โดยค้นหาตาม data attribute
                document.querySelectorAll('.status-group').forEach(grp => {{
                    const sName = grp.getAttribute('data-student-name');
                    const sNo = grp.getAttribute('data-student-no');
                    if (sName === data.student_name && sNo === data.student_no) {{
                        const radioMa = grp.querySelector('input[value="มา"]');
                        if (radioMa) {{
                            radioMa.checked = true;
                            // ไฮไลต์แถวเรียนเพื่อความสวยงาม
                            const row = document.getElementById('row_' + sNo);
                            if (row) {{
                                row.style.background = 'rgba(16, 185, 129, 0.08)';
                                setTimeout(() => {{ row.style.background = 'transparent'; }}, 2000);
                            }}
                        }}
                    }}
                }});
            }}
        }} catch(e) {{}}
    }};
    
    ws.onclose = function() {{
        setTimeout(setupRollcallSocket, rcReconnectDelay);
        rcReconnectDelay = Math.min(rcReconnectDelay * 1.7, 30000);
    }};
}}

// เปิดใช้งานคิวอาร์โค้ดลงทะเบียนด่วน
async function openOTPModal() {{
    const modal = document.getElementById('otpModal');
    const otpDisplay = document.getElementById('otpDisplay');
    const qrDisplay = document.getElementById('qrDisplay');
    const timerDisplay = document.getElementById('timerDisplay');
    const list = document.getElementById('checkinList');
    const countEl = document.getElementById('checkinCount');
    
    list.innerHTML = '<p style="color:gray; text-align:center; margin-top:25px;" id="emptyCheckinMsg">ยังไม่มีนักเรียนลงชื่อเข้ามา</p>';
    countEl.textContent = "0";
    
    // เรียกใช้ API หลังบ้านเพื่อดึง OTP
    try {{
        const formData = new FormData();
        formData.append('group_id', activeGroupId);
        formData.append('duration', 5);
        
        const res = await fetch('/api/teacher/start_otp', {{
            method: 'POST',
            body: formData
        }});
        
        const data = await res.json();
        if (res.ok && data.ok) {{
            currentOtp = data.otp;
            otpDisplay.textContent = currentOtp;
            
            // สร้าง URL ลิงก์เช็กชื่อของนักเรียน
            const domain = window.location.origin;
            const checkinUrl = `${{domain}}/checkin?group_id=${{activeGroupId}}`;
            
            // สร้าง QR Code จาก API ฟรี
            qrDisplay.src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${{encodeURIComponent(checkinUrl)}}`;
            
            // เริ่มจับเวลานับถอยหลัง 5 นาที (300 วินาที)
            startCountdown(data.duration_seconds);
            
            modal.classList.add('active');
        }} else {{
            smartAlert({{ title: 'ไม่สำเร็จ', message: 'ไม่สามารถดึงข้อมูลรหัส OTP ได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง', type: 'error' }});
        }}
    }} catch(e) {{
        smartAlert({{ title: 'เชื่อมต่อไม่ได้', message: 'เกิดข้อผิดพลาดในการติดต่อฐานข้อมูล กรุณาลองใหม่อีกครั้ง', type: 'error' }});
    }}
}}

// ปิดโหมดลงทะเบียนด่วน
async function closeOTPModal() {{
    const modal = document.getElementById('otpModal');
    clearInterval(timerInterval);
    
    try {{
        const formData = new FormData();
        formData.append('group_id', activeGroupId);
        await fetch('/api/teacher/stop_otp', {{
            method: 'POST',
            body: formData
        }});
    }} catch(e) {{}}
    
    modal.classList.remove('active');
}}

// ระบบจับเวลานับถอยหลัง
function startCountdown(seconds) {{
    clearInterval(timerInterval);
    const timerDisplay = document.getElementById('timerDisplay');
    
    let timeLeft = seconds;
    
    timerInterval = setInterval(() => {{
        if (timeLeft <= 0) {{
            clearInterval(timerInterval);
            timerDisplay.textContent = "⏱️ หมดเวลาเปิดลงทะเบียนแล้ว";
            alert("⏰ หมดเวลาลงทะเบียนเช็กชื่อด่วนเรียบร้อยครับ");
            closeOTPModal();
            return;
        }}
        
        timeLeft--;
        const mins = Math.floor(timeLeft / 60);
        const secs = timeLeft % 60;
        timerDisplay.textContent = `⏱️ เหลือเวลาเปิดรับ: ${{String(mins).padStart(2, '0')}}:${{String(secs).padStart(2, '0')}} นาที`;
    }}, 1000);
}}

document.addEventListener("DOMContentLoaded", () => {{
    setupRollcallSocket();
}});
</script>

</body>
</html>
    """

# ==========================================
# ⚙️ CORE PROCESSING APIS & WORKERS
# ==========================================
@app.post("/api/admin/create_group")
async def api_create_group(group_name: str = Form(...), branch: str = Form(...), teacher_username: str = Form(...), user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO course_groups (group_name, teacher_username, branch) VALUES (?, ?, ?)", (group_name, teacher_username, branch))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/admin/assign_groups", status_code=303)

@app.post("/api/admin/assign_students_to_group")
async def api_assign_students_to_group(request: Request, group_id: int = Form(...), user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return HTMLResponse("Unauthorized", status_code=401)
    form_data = await request.form()
    assigned_student_uids = form_data.getlist("assigned_students")
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    # แก้ไข: เปลี่ยนจาก DELETE ทั้งหมด เป็นการ INSERT เพิ่มเติม (ใช้ INSERT OR IGNORE เพื่อไม่ให้ซ้ำ)
    for uid in assigned_student_uids:
        cursor.execute("INSERT OR IGNORE INTO group_assignments (group_id, student_uid) VALUES (?, ?)", (group_id, uid))
    conn.commit()
    conn.close()
    return alert_redirect("อัปเดตสมาชิกห้องเรียนเรียบร้อยแล้ว", type="success", url=f"/admin/assign_groups?selected_group_id={group_id}")

def run_discord_log_background(title, message, color_rgb):
    """ฟังก์ชันสำหรับส่ง Discord Log ใน Background Thread"""
    asyncio.run_coroutine_threadsafe(
        send_discord_log(title, message, discord.Color.from_rgb(*color_rgb)),
        bot.loop
    )

@app.post("/app/api/submit_attendance")
async def app_api_submit(
    background_tasks: BackgroundTasks,
    request: Request,
    group_name: str = Form(...),
    teacher_user: str = Form(...),
    target_date: str = Form(...),
    user_session: Optional[str] = Cookie(None)
):
    if not user_session or user_session != f"teacher_{teacher_user}": return HTMLResponse("Unauthorized", status_code=401)
    form_data = await request.form()

    try:
        date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d/%m/%Y")
    except Exception: formatted_date = target_date

    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT fullname FROM teachers WHERE username = ?", (teacher_user,))
    t_info = cursor.fetchone()
    fullname_teacher = t_info[0] if t_info else teacher_user

    stats = {"มา": 0, "สาย": 0, "ลา": 0, "ขาด": 0}
    discord_details = []

    # ดึงข้อมูลกลุ่ม ID เพื่อตรวจสอบการลา
    cursor.execute("SELECT group_id FROM course_groups WHERE group_name = ?", (group_name,))
    g_res = cursor.fetchone()
    group_id = g_res[0] if g_res else 0

    # ✅ ดึงรายชื่อนักเรียนของกลุ่มนี้จากฐานข้อมูลเอง (ไม่พึ่งพา hidden field name_/no_/class_ จากฟอร์มอีกต่อไป)
    # ฟอร์มตอนนี้จะส่งมาแค่ status_{uid} ต่อคนเท่านั้น ทำให้ไม่มีปัญหา "Too many fields" แม้กลุ่มจะมีนักเรียนจำนวนมาก
    cursor.execute('SELECT student_uid FROM group_assignments WHERE group_id = ?', (group_id,))
    assigned_uids = {r[0] for r in cursor.fetchall()}
    students_by_uid = {s['uid']: s for s in get_sorted_master_students() if s['uid'] in assigned_uids}

    for key, s in students_by_uid.items():
        sname = s['name']
        sno   = s['no']
        sclass = s['class']
        status_value = form_data.get(f"status_{key}")
        
        if sname and status_value:
            # ตรวจสอบว่ามีใบลาที่อนุมัติแล้วในวันที่ระบุหรือไม่
            cursor.execute("SELECT reason FROM leave_requests WHERE group_id = ? AND student_name = ? AND student_no = ? AND leave_date = ? AND status = 'approved'", 
                           (group_id, sname, sno, target_date))
            leave_found = cursor.fetchone()
            
            final_status = status_value
            checker_name = fullname_teacher
            
            if leave_found:
                final_status = "ลา"
                checker_name = f"ระบบ (ลา: {leave_found[0]})"

            cursor.execute('INSERT INTO attendance_logs (group_name, student_name, student_no, classroom, status, date, checked_by, log_time) VALUES (?,?,?,?,?,?,?,?)',
                (group_name, sname, sno, sclass, final_status, formatted_date, checker_name, datetime.now().strftime("%H:%M:%S")))
            stats[final_status] += 1
            discord_details.append(f"• เลขที่ {sno} {sname} (ห้อง {sclass}) -> **[{final_status}]**")
    conn.commit()
    conn.close()

    # เตรียมข้อมูลส่ง Discord (ทำใน Background ไม่ต้องรอ)
    student_rows_str = "\n".join(discord_details) if discord_details else "ไม่มีข้อมูล"
    embed_message = f"👤 **ผู้บันทึกข้อมูล:** อาจารย์ {fullname_teacher}\n📘 **กลุ่มคลาสรายวิชา:** {group_name}\n📅 **ประจำรอบวันที่เรียน:** {formatted_date}\n\n📊 **สถิติเช็กชื่อ:** มา: `{stats['มา']}` | สาย: `{stats['สาย']}` | ลา: `{stats['ลา']}` | ขาด: `{stats['ขาด']}`\n\n📋 **รายชื่อระบบ:**\n{student_rows_str}"
    
    background_tasks.add_task(run_discord_log_background, "🏫 [K-School Platform] รายงานบันทึกเวลาเรียนวิชาเอก", embed_message, (30, 58, 138))

    return HTMLResponse(f"""<html>{STYLE_HEADER}<body><script>smartAlert({{title: 'บันทึกดำเนินการเสร็จสิ้น!', message: 'ระบบได้เก็บข้อมูลเข้าคลังเรียบร้อยแล้ว!', type: 'success', callback: () => {{ window.location.href='/app/dashboard?user={teacher_user}'; }} }});</script></body></html>""")

# ==========================================
# ⚡ QUICK OTP / QR CHECK-IN APIS
# ==========================================
@app.post("/api/teacher/start_otp")
async def api_teacher_start_otp(
    group_id: int = Form(...),
    duration: int = Form(5),
    user_session: Optional[str] = Cookie(None)
):
    if not user_session or not user_session.startswith("teacher_"):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    
    import random
    otp = f"{random.randint(1000, 9999)}"
    
    from datetime import timedelta
    expires_at = (datetime.now() + timedelta(minutes=duration)).isoformat()
    
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO otp_sessions (group_id, otp, expires_at, is_active)
        VALUES (?, ?, ?, 1)
        ON CONFLICT(group_id) DO UPDATE SET otp=excluded.otp, expires_at=excluded.expires_at, is_active=1
    """, (group_id, otp, expires_at))
    conn.commit()
    conn.close()
    
    add_log(f"อาจารย์เปิดเซสชันเช็กชื่อด่วนวิชา #{group_id} รหัส OTP: {otp}")
    
    return JSONResponse({
        "ok": True,
        "otp": otp,
        "expires_at": expires_at,
        "duration_seconds": duration * 60
    })

@app.post("/api/teacher/stop_otp")
async def api_teacher_stop_otp(
    group_id: int = Form(...),
    user_session: Optional[str] = Cookie(None)
):
    if not user_session or not user_session.startswith("teacher_"):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE otp_sessions SET is_active=0 WHERE group_id=?", (group_id,))
    conn.commit()
    conn.close()
    
    add_log(f"ปิดเซสชันเช็กชื่อด่วนวิชา #{group_id}")
    return JSONResponse({"ok": True})

@app.post("/api/student/checkin")
async def api_student_checkin(
    request: Request,
    background_tasks: BackgroundTasks
):
    m_cfg = get_maintenance_status()
    if m_cfg["is_active"] == 1:
        return JSONResponse({"ok": False, "error": "ระบบปิดปรับปรุงอยู่"}, status_code=503)
        
    try:
        data = await request.json()
        student_name = data.get("student_name", "").strip()
        student_no = data.get("student_no", "").strip()
        classroom = data.get("classroom", "").strip()
        otp = data.get("otp", "").strip()
        group_id = int(data.get("group_id", 0))
    except Exception:
        return JSONResponse({"ok": False, "error": "รูปแบบข้อมูลไม่ถูกต้อง"}, status_code=400)
        
    if not all([student_name, student_no, classroom, otp, group_id]):
        return JSONResponse({"ok": False, "error": "กรุณากรอกข้อมูลให้ครบถ้วน"}, status_code=400)
        
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT otp, expires_at, is_active FROM otp_sessions WHERE group_id = ?", (group_id,))
    session = cursor.fetchone()
    if not session or session[2] == 0 or session[0] != otp:
        conn.close()
        return JSONResponse({"ok": False, "error": "รหัส OTP ไม่ถูกต้อง หรือเซสชันปิดแล้ว"}, status_code=400)
        
    expires_at = datetime.fromisoformat(session[1])
    if datetime.now() > expires_at:
        cursor.execute("UPDATE otp_sessions SET is_active=0 WHERE group_id=?", (group_id,))
        conn.commit()
        conn.close()
        return JSONResponse({"ok": False, "error": "รหัส OTP หมดอายุแล้ว"}, status_code=400)
        
    student_uid = f"{student_name}_{student_no}"
    cursor.execute("SELECT student_uid FROM group_assignments WHERE group_id = ? AND student_uid = ?", (group_id, student_uid))
    assignment = cursor.fetchone()
    if not assignment:
        conn.close()
        return JSONResponse({"ok": False, "error": "ไม่พบรายชื่อของคุณในกลุ่มเรียนนี้"}, status_code=400)
        
    cursor.execute("SELECT group_name FROM course_groups WHERE group_id = ?", (group_id,))
    group_name = cursor.fetchone()[0]
    
    today_val = datetime.now().strftime("%d/%m/%Y")
    
    cursor.execute("""
        SELECT log_id FROM attendance_logs 
        WHERE student_name = ? AND group_name = ? AND date = ?
    """, (student_name, group_name, today_val))
    existing = cursor.fetchone()
    
    if existing:
        conn.close()
        return JSONResponse({"ok": False, "error": "คุณได้ลงชื่อเข้าเรียนในวิชานี้ของวันนี้เรียบร้อยแล้ว"}, status_code=400)
        
    cursor.execute("""
        INSERT INTO attendance_logs (group_name, student_name, student_no, classroom, status, date, checked_by, log_time)
        VALUES (?, ?, ?, ?, 'มา', ?, 'เช็กชื่อด่วน (OTP)', ?)
    """, (group_name, student_name, student_no, classroom, today_val, datetime.now().strftime("%H:%M:%S")))
    
    conn.commit()
    conn.close()
    
    import json
    ws_msg = json.dumps({
        "type": "student_checked_in",
        "group_id": group_id,
        "student_name": student_name,
        "student_no": student_no,
        "classroom": classroom
    })
    background_tasks.add_task(manager.broadcast, ws_msg)
    
    discord_msg = f"👤 **นักเรียนลงชื่อเอง:** {student_name} (เลขที่ {student_no} ห้อง {classroom})\n📘 **กลุ่มคลาส:** {group_name}\n📅 **วันที่:** {today_val}\n⚡ **วิธีการ:** เช็กชื่อด่วนด้วยรหัส OTP"
    background_tasks.add_task(run_discord_log_background, "🏫 [K-School] นักเรียนเช็กชื่อผ่าน OTP สำเร็จ", discord_msg, (16, 185, 129))
    
    return JSONResponse({"ok": True})

@app.get("/admin/add_student", response_class=HTMLResponse)
async def admin_add_student_page(user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return RedirectResponse(url="/login", status_code=303)
    return f"""<html>{STYLE_HEADER}<body><div class="navbar"><h1>➕ เพิ่มรายชื่อทะเบียนนักเรียนใหม่</h1><a href="/admin/students" class="btn btn-secondary">⬅ กลับหน้าหลัก</a></div><div class="main-container"><div class="card"><form action="/api/admin/add_student" method="post"><input type="text" name="student_name" placeholder="ชื่อ-นามสกุลนักเรียน" required><input type="text" name="student_no" placeholder="เลขที่ประจำตัว" required><input type="text" name="classroom" placeholder="ระดับชั้นเรียน" required><input type="text" name="branch" placeholder="สาขาวิชาเอก" required><button type="submit" class="btn-submit">💾 ยืนยันบันทึกข้อมูลหลัก</button></form></div></div></body></html>"""

@app.post("/api/admin/add_student")
async def api_add_student(student_name: str = Form(...), student_no: str = Form(...), classroom: str = Form(...), branch: str = Form(...), user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return HTMLResponse("Unauthorized", status_code=401)
    new_line = f"{student_name.strip()}, {student_no.strip()}, {classroom.strip()}, {branch.strip()}\n"
    with open(TXT_DATABASE_PATH, "a", encoding="utf-8") as f: f.write(new_line)
    return HTMLResponse(f"""<html>{STYLE_HEADER}<body><script>smartAlert({{title: 'ดำเนินการเสร็จสิ้น!', message: 'บันทึกเพิ่มรายชื่อเรียบร้อย!', type: 'success', callback: () => {{ window.location.href='/admin/add_student'; }} }});</script></body></html>""")

# ==========================================
# 🎖️ ระบบคะแนนความประพฤติ
# ==========================================
CONDUCT_REASONS_PLUS = [
    "เข้าร่วมกิจกรรมของสถาบัน", "ช่วยเหลืองานส่วนรวม", "ทำความดีเด่นชัด", "มีความประพฤติดีต่อเนื่อง"
]
CONDUCT_REASONS_MINUS = [
    "มาสาย", "ขาดเรียนไม่แจ้งลา", "แต่งกายผิดระเบียบ", "ก่อความไม่สงบในชั้นเรียน", "ทะเลาะวิวาท", "อื่นๆ"
]

CONDUCT_PAGE_STYLE = """
<style>
    .cd-level-card {
        background: var(--surface); border: 1px solid var(--border); border-radius: 18px;
        padding: 20px; text-decoration: none; color: var(--navy-800);
        display: flex; align-items: center; gap: 16px;
        box-shadow: var(--shadow-sm); margin-bottom: 12px; transition: transform .15s ease;
    }
    .cd-level-card:active { transform: scale(0.98); }
    .cd-level-icon {
        width: 54px; height: 54px; border-radius: 15px; flex-shrink: 0;
        background: linear-gradient(135deg, var(--navy-600), var(--navy-900));
        color: #fff; display: flex; align-items: center; justify-content: center; font-size: 24px;
    }
    .cd-level-info { flex: 1; min-width: 0; }
    .cd-level-info h3 { margin: 0 0 3px; font-size: 15.5px; font-weight: 800; color: var(--navy-900); }
    .cd-level-info p { margin: 0; font-size: 12px; color: var(--text-soft); }
    .cd-level-avg {
        text-align: center; flex-shrink: 0; padding: 6px 14px; border-radius: 12px;
        font-weight: 800; font-size: 15px;
    }
    .cd-level-avg span { display: block; font-size: 9.5px; font-weight: 700; opacity: 0.75; margin-top: 1px; }

    .cd-student-row {
        background: var(--surface); border: 1px solid var(--border); border-radius: 15px;
        padding: 13px 14px; margin-bottom: 10px; display: flex; align-items: center; gap: 12px;
        box-shadow: var(--shadow-sm);
    }
    .cd-avatar {
        width: 40px; height: 40px; border-radius: 50%; flex-shrink: 0;
        background: var(--surface-muted); color: var(--navy-700);
        display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;
        border: 1px solid var(--border);
    }
    .cd-student-info { flex: 1; min-width: 0; }
    .cd-student-info .cd-name { font-weight: 700; font-size: 13.5px; color: var(--navy-900); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .cd-student-info .cd-meta { font-size: 11px; color: var(--text-soft); margin-top: 1px; }
    .cd-score-pill { flex-shrink: 0; padding: 5px 13px; border-radius: 100px; font-weight: 800; font-size: 13.5px; }
    .cd-actions { display: flex; gap: 5px; flex-shrink: 0; }
    .cd-action-btn {
        width: 32px; height: 32px; border-radius: 9px; display: flex; align-items: center; justify-content: center;
        text-decoration: none; font-size: 14px; border: 1px solid var(--border); background: var(--surface-muted);
    }
    .cd-back-link { display: inline-flex; align-items: center; gap: 5px; color: var(--navy-600); font-weight: 700; font-size: 13px; text-decoration: none; margin-bottom: 14px; }
</style>
"""

@app.get("/admin/conduct", response_class=HTMLResponse)
async def admin_conduct_page(level: Optional[str] = None, room: Optional[str] = None, user_session: Optional[str] = Cookie(None)):
    access, redirect = require_discipline_access(user_session)
    if redirect: return redirect
    # 🎓 หัวหน้าระดับ: บังคับดูเฉพาะระดับของตัวเอง
    if access["role"] == "level_head":
        if not access["level_scope"]:
            return alert_redirect("บัญชีของคุณยังไม่ถูกกำหนดระดับชั้นที่รับผิดชอบ กรุณาติดต่อผู้ดูแลระบบ", type="error", url="/app/dashboard")
        if level and level != access["level_scope"]:
            return RedirectResponse(url=f"/admin/conduct?level={access['level_scope']}", status_code=303)
        if not level:
            level = access["level_scope"]

    back_url = "/admin/dashboard" if access["role"] == "admin" else f"/app/dashboard?user={urllib.parse.quote(access['username'])}"

    def score_color(score):
        if score >= 80: return "#10b981", "#f0fdf4", "#bbf7d0"
        if score >= 50: return "#d97706", "#fffbeb", "#fde68a"
        return "#ef4444", "#fef2f2", "#fecaca"

    # ── ยังไม่เลือกระดับชั้น: แสดงเป็นการ์ดระดับชั้น ไม่ขึ้นรวมทุกคน ──
    if not level:
        all_summary = get_conduct_summary()
        levels = {}
        for s in all_summary:
            lv = get_grade_level(s['class'])
            levels.setdefault(lv, []).append(s['score'])

        def sort_key(lv):
            digits = ''.join(ch for ch in lv if ch.isdigit())
            return (0, int(digits)) if digits else (1, lv)

        level_cards = ""
        for lv in sorted(levels.keys(), key=sort_key):
            scores = levels[lv]
            avg = round(sum(scores) / len(scores)) if scores else 0
            fg, bg, _ = score_color(avg)
            level_cards += f"""
            <a href="/admin/conduct?level={lv}" class="cd-level-card">
                <div class="cd-level-icon">🎓</div>
                <div class="cd-level-info">
                    <h3>ระดับชั้น {lv}</h3>
                    <p>นักเรียนทั้งหมด {len(scores)} คน</p>
                </div>
                <div class="cd-level-avg" style="background:{bg}; color:{fg};">
                    {avg}<span>เฉลี่ย</span>
                </div>
            </a>
            """

        return f"""
        <html>{STYLE_HEADER}
        {CONDUCT_PAGE_STYLE}
        <body>
            <div class="navbar">
                <h1><img src="{LOGO_URL}" class="nav-logo"> 🎖️ คะแนนความประพฤติ</h1>
                <a href="{back_url}" class="btn btn-secondary">⬅ กลับหน้าควบคุม</a>
            </div>
            <div class="main-container">
                <div class="card" style="background:#eff6ff; border:1px solid #bfdbfe;">
                    <p style="margin:0; font-size:13px; color:#1e40af; line-height:1.7;">
                        📌 นักเรียนทุกคนเริ่มต้นที่ <b>100 คะแนน</b> เลือกระดับชั้นด้านล่างเพื่อดูและบันทึกคะแนนของนักเรียนในระดับนั้น
                    </p>
                </div>
                <div class="ah-section-title" style="margin:4px 4px 12px; font-size:12.5px; font-weight:800; color:#64748b;">เลือกระดับชั้น</div>
                {level_cards if level_cards else "<p style='color:#94a3b8; text-align:center; padding:30px 0;'>ยังไม่มีข้อมูลนักเรียนในระบบ</p>"}
            </div>
        </body></html>
        """

    # ── เลือกระดับชั้นแล้ว: แสดงเฉพาะนักเรียนในระดับนี้ ──
    summary = [s for s in get_conduct_summary() if get_grade_level(s['class']) == level]
    rooms_in_level = sorted(set(s['class'] for s in summary))
    if room:
        summary = [s for s in summary if s['class'] == room]

    room_options = '<option value="">ทุกห้องในระดับนี้</option>'
    for r in rooms_in_level:
        sel = 'selected' if room == r else ''
        room_options += f'<option value="{r}" {sel}>ห้อง {r}</option>'

    rows = ""
    for s in summary:
        fg, bg, border = score_color(s['score'])
        initial = s['name'][:1] if s['name'] else "?"
        rows += f"""
        <div class="cd-student-row">
            <div class="cd-avatar">{initial}</div>
            <div class="cd-student-info">
                <div class="cd-name">{s['name']}</div>
                <div class="cd-meta">{s['class']} · เลขที่ {s['no']}</div>
            </div>
            <div class="cd-score-pill" style="background:{bg}; color:{fg}; border:1px solid {border};">{s['score']}</div>
            <div class="cd-actions">
                <a href="/admin/conduct/add?uid={s['uid']}" class="cd-action-btn" title="บันทึกคะแนน">✏️</a>
                <a href="/admin/conduct/history?uid={s['uid']}" class="cd-action-btn" title="ดูประวัติ">📜</a>
            </div>
        </div>
        """

    return f"""
    <html>{STYLE_HEADER}
    {CONDUCT_PAGE_STYLE}
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> 🎖️ ระดับชั้น {level}</h1>
            <a href="{back_url}" class="btn btn-secondary">⬅ กลับหน้าควบคุม</a>
        </div>
        <div class="main-container">
            {'' if access["role"] == "level_head" else '<a href="/admin/conduct" class="cd-back-link">← เลือกระดับชั้นอื่น</a>'}
            <div class="card" style="padding:16px; margin-bottom:16px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:13px; font-weight:700; color:#475569;">🔍 กรองห้อง:</span>
                    <select onchange="location.href='/admin/conduct?level={level}&room='+this.value;" style="padding:6px; border-radius:6px; border:1px solid #cbd5e1; font-family:'Sarabun'; font-size:13px; font-weight:600; flex:1;">
                        {room_options}
                    </select>
                </div>
            </div>
            {rows if rows else "<p style='color:#94a3b8; text-align:center; padding:30px 0;'>ไม่พบนักเรียนในระดับชั้นนี้</p>"}
        </div>
    </body></html>
    """

@app.get("/admin/conduct/add", response_class=HTMLResponse)
async def admin_conduct_add_page(uid: str, user_session: Optional[str] = Cookie(None)):
    access, redirect = require_discipline_access(user_session)
    if redirect: return redirect

    all_students = get_sorted_master_students()
    target = next((s for s in all_students if s['uid'] == uid), None)
    if not target:
        return alert_redirect("ไม่พบข้อมูลนักเรียนที่ต้องการ", type="error", url="/admin/conduct")
    if not in_discipline_scope(access, target['class']):
        return alert_redirect("คุณไม่มีสิทธิ์บันทึกคะแนนของนักเรียนนอกระดับชั้นที่รับผิดชอบ", type="error", url="/admin/conduct")

    current_score = get_conduct_summary()
    current = next((s for s in current_score if s['uid'] == uid), None)
    score_now = current['score'] if current else CONDUCT_START_SCORE

    plus_chips = "".join([f'<button type="button" class="cd-chip cd-chip-plus" onclick="cdFill(\'{r}\')">➕ {r}</button>' for r in CONDUCT_REASONS_PLUS])
    minus_chips = "".join([f'<button type="button" class="cd-chip cd-chip-minus" onclick="cdFill(\'{r}\')">➖ {r}</button>' for r in CONDUCT_REASONS_MINUS])

    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> ✏️ บันทึกคะแนนความประพฤติ</h1>
            <a href="/admin/conduct" class="btn btn-secondary">⬅ กลับ</a>
        </div>
        <div class="main-container">
            <div class="card" style="text-align:center;">
                <div style="font-size:14px; color:#64748b; margin-bottom:4px;">{target['class']} · เลขที่ {target['no']}</div>
                <div style="font-size:19px; font-weight:800; color:#0f172a; margin-bottom:10px;">{target['name']}</div>
                <div style="display:inline-block; background:#f1f5f9; padding:6px 20px; border-radius:100px; font-weight:800; font-size:15px; color:#1e3a8a;">คะแนนปัจจุบัน: {score_now} / 100</div>
            </div>
            <div class="card">
                <h2>เลือกเหตุผลด่วน</h2>
                <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:6px;">{plus_chips}</div>
                <div style="display:flex; flex-wrap:wrap; gap:8px;">{minus_chips}</div>
                <style>
                    .cd-chip {{ border:none; border-radius:100px; padding:8px 14px; font-size:12.5px; font-weight:700; cursor:pointer; font-family:'Sarabun',sans-serif; }}
                    .cd-chip-plus {{ background:#f0fdf4; color:#15803d; border:1px solid #bbf7d0; }}
                    .cd-chip-minus {{ background:#fef2f2; color:#b91c1c; border:1px solid #fecaca; }}
                </style>
            </div>
            <div class="card">
                <h2>บันทึกคะแนน</h2>
                <form action="/api/admin/conduct/add" method="post">
                    <input type="hidden" name="uid" value="{target['uid']}">
                    <input type="hidden" name="student_name" value="{target['name']}">
                    <input type="hidden" name="student_no" value="{target['no']}">
                    <input type="hidden" name="classroom" value="{target['class']}">
                    <label style="font-size:12.5px; font-weight:700; color:#475569;">คะแนน (ใส่เลขบวกเพื่อเพิ่ม, ลบเพื่อหัก):</label>
                    <input type="number" id="cdPoints" name="points" placeholder="เช่น -5 หรือ +10" required>
                    <label style="font-size:12.5px; font-weight:700; color:#475569;">เหตุผล:</label>
                    <textarea id="cdReason" name="reason" placeholder="ระบุเหตุผลในการบันทึกคะแนน" required style="min-height:70px;"></textarea>
                    <button type="submit" class="btn-submit">💾 บันทึกคะแนนความประพฤติ</button>
                </form>
            </div>
        </div>
        <script>
            function cdFill(reason) {{
                document.getElementById('cdReason').value = reason;
                const pointsInput = document.getElementById('cdPoints');
                if (!pointsInput.value) {{
                    pointsInput.value = reason.includes('เข้าร่วม') || reason.includes('ช่วยเหลือ') || reason.includes('ดีเด่น') || reason.includes('ต่อเนื่อง') ? 5 : -5;
                }}
            }}
        </script>
    </body></html>
    """

@app.post("/api/admin/conduct/add")
async def api_conduct_add(uid: str = Form(...), student_name: str = Form(...), student_no: str = Form(...), classroom: str = Form(...), points: int = Form(...), reason: str = Form(...), user_session: Optional[str] = Cookie(None)):
    access, redirect = require_discipline_access(user_session)
    if redirect: return redirect
    if not in_discipline_scope(access, classroom):
        return alert_redirect("คุณไม่มีสิทธิ์บันทึกคะแนนของนักเรียนนอกระดับชั้นที่รับผิดชอบ", type="error", url="/admin/conduct")
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conduct_scores (student_uid, student_name, student_no, classroom, points, reason, recorded_by, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (uid, student_name, student_no, classroom, points, reason.strip(), f"{access['role_label']} {access['fullname']}".strip(), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()
    verb = "เพิ่ม" if points >= 0 else "หัก"

    # 🔴 แจ้งเตือนแบบเรียลไทม์ให้นักเรียนคนนั้นทันที ไม่ต้องรอรีเฟรชหน้า
    summary_now = next((s for s in get_conduct_summary() if s['uid'] == uid), None)
    score_now = summary_now['score'] if summary_now else CONDUCT_START_SCORE
    await push_student_notify(
        title=f"{'ได้รับ' if points >= 0 else 'ถูกหัก'}คะแนนความประพฤติ {abs(points)} คะแนน",
        message=reason.strip(),
        tone="success" if points >= 0 else "danger",
        target_uids=[uid],
        score_now=score_now,
    )

    return alert_redirect(f"บันทึกคะแนนความประพฤติเรียบร้อยแล้ว ({verb} {abs(points)} คะแนน)", type="success", url="/admin/conduct")

@app.get("/coming_soon", response_class=HTMLResponse)
async def coming_soon_page(back: str = "/student/dashboard"):
    """🚧 ฟีเจอร์ที่ยังไม่ได้พัฒนา — ใช้เป็นทางลัดชั่วคราวสำหรับไอคอนในกริดเมนูที่ยังไม่มีระบบหลังบ้านรองรับ"""
    return alert_redirect("ฟีเจอร์นี้อยู่ระหว่างการพัฒนา เร็วๆ นี้จะเปิดให้ใช้งาน", type="info", url=back)

@app.get("/api/admin/conduct/delete")
async def api_conduct_delete(entry_id: int, uid: str, user_session: Optional[str] = Cookie(None)):
    """🗑️ ลบรายการคะแนนความประพฤติที่เคยบันทึกผิด/ไม่ต้องการแล้ว — คะแนนของนักเรียนจะถูกคืนให้อัตโนมัติ
    เพราะคะแนนรวมคำนวณสดจาก SUM ของทุกแถวที่เหลืออยู่ (ไม่มีคอลัมน์คะแนนคงที่ให้ค้างเป็นค่าเก่า)"""
    access, redirect = require_discipline_access(user_session)
    if redirect: return redirect
    all_students = get_sorted_master_students()
    target = next((s for s in all_students if s['uid'] == uid), None)
    if not target:
        return alert_redirect("ไม่พบข้อมูลนักเรียนที่ต้องการ", type="error", url="/admin/conduct")
    if not in_discipline_scope(access, target['class']):
        return alert_redirect("คุณไม่มีสิทธิ์ลบประวัติของนักเรียนนอกระดับชั้นที่รับผิดชอบ", type="error", url="/admin/conduct")

    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT points, reason FROM conduct_scores WHERE id=? AND student_uid=?", (entry_id, uid))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return alert_redirect("ไม่พบรายการนี้ (อาจถูกลบไปแล้ว)", type="error", url=f"/admin/conduct/history?uid={uid}")
    cursor.execute("DELETE FROM conduct_scores WHERE id=? AND student_uid=?", (entry_id, uid))
    conn.commit()
    conn.close()

    points, reason = row
    refund_msg = f"คืนคะแนน {abs(points)} คะแนนให้นักเรียนแล้ว" if points < 0 else f"ตัดคะแนนที่เคยให้ไป {points} คะแนนออกแล้ว"

    # 🔴 แจ้งเตือนแบบเรียลไทม์ทันทีที่ลบ (คะแนนถูกคืน/ตัดออกไปแล้วให้ขึ้นบนหน้าจอนักเรียนโดยไม่ต้องรีเฟรช)
    summary_now = next((s for s in get_conduct_summary() if s['uid'] == uid), None)
    score_now = summary_now['score'] if summary_now else CONDUCT_START_SCORE
    await push_student_notify(
        title="ยกเลิกรายการคะแนนความประพฤติ",
        message=f'"{reason}" — {refund_msg}',
        tone="info",
        target_uids=[uid],
        score_now=score_now,
    )

    return alert_redirect(f"ลบรายการ \"{reason}\" เรียบร้อยแล้ว — {refund_msg}", type="success", url=f"/admin/conduct/history?uid={uid}")

@app.get("/admin/conduct/history", response_class=HTMLResponse)
async def admin_conduct_history_page(uid: str, user_session: Optional[str] = Cookie(None)):
    access, redirect = require_discipline_access(user_session)
    if redirect: return redirect

    all_students = get_sorted_master_students()
    target = next((s for s in all_students if s['uid'] == uid), None)
    if not target:
        return alert_redirect("ไม่พบข้อมูลนักเรียนที่ต้องการ", type="error", url="/admin/conduct")
    if not in_discipline_scope(access, target['class']):
        return alert_redirect("คุณไม่มีสิทธิ์ดูประวัติของนักเรียนนอกระดับชั้นที่รับผิดชอบ", type="error", url="/admin/conduct")

    history = get_conduct_history(uid)
    rows = ""
    for h in history:
        sign = "+" if h['points'] >= 0 else ""
        color = "#15803d" if h['points'] >= 0 else "#b91c1c"
        rows += f"""
        <tr>
            <td style="white-space:nowrap; font-size:12px; color:#64748b;">{h['created_at']}</td>
            <td style="text-align:left;">{h['reason']}<br><span style="font-size:10.5px;color:#94a3b8;">โดย: {h['recorded_by']}</span></td>
            <td><b style="color:{color};">{sign}{h['points']}</b></td>
            <td><b>{h['running_total']}</b></td>
            <td>
                <a href="/api/admin/conduct/delete?entry_id={h['id']}&uid={uid}"
                   onclick="return confirm('ลบรายการนี้? ระบบจะคืนคะแนนให้นักเรียนอัตโนมัติ')"
                   class="btn btn-danger" style="padding:4px 9px;font-size:11px;">🗑️ ลบ</a>
            </td>
        </tr>
        """
    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> 📜 ประวัติคะแนนความประพฤติ</h1>
            <a href="/admin/conduct" class="btn btn-secondary">⬅ กลับ</a>
        </div>
        <div class="main-container">
            <div class="card" style="text-align:center;">
                <div style="font-size:14px; color:#64748b; margin-bottom:4px;">{target['class']} · เลขที่ {target['no']}</div>
                <div style="font-size:19px; font-weight:800; color:#0f172a;">{target['name']}</div>
            </div>
            <div class="card">
                <h2>ประวัติการบันทึกคะแนนทั้งหมด</h2>
                <div style="overflow-x:auto; border-radius:8px; border:1px solid #e2e8f0;">
                    <table>
                        <thead><tr><th>วันที่-เวลา</th><th>เหตุผล</th><th>คะแนน</th><th>คงเหลือ</th><th>จัดการ</th></tr></thead>
                        <tbody>{rows if rows else "<tr><td colspan='5'>ยังไม่มีประวัติการบันทึกคะแนน</td></tr>"}</tbody>
                    </table>
                </div>
            </div>
        </div>
    </body></html>
    """

@app.get("/admin/teachers", response_class=HTMLResponse)
async def admin_teachers_page(user_session: Optional[str] = Cookie(None)):
    access = get_access(user_session)
    if not access["authenticated"] or not can_manage_teacher_accounts(access):
        return RedirectResponse(url="/login", status_code=303)
    back_url = "/admin/dashboard" if access["role"] == "admin" else f"/app/dashboard?user={urllib.parse.quote(access['username'])}"
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, fullname, role, level_scope FROM teachers")
    teachers = cursor.fetchall()
    conn.close()

    role_options = "".join([f'<option value="{key}">{meta["label"]}</option>' for key, meta in TEACHER_ROLES.items()])

    role_tone = {"admin": "bad", "affairs": "warn", "level_head": "ok", "teacher": "mute"}
    counts = {}
    rows = ""
    for t in teachers:
        username, fullname, role, level_scope = t
        role = role or "teacher"
        counts[role] = counts.get(role, 0) + 1
        role_meta = TEACHER_ROLES.get(role, TEACHER_ROLES["teacher"])
        scope_txt = f" · ระดับ {_he(level_scope)}" if role == "level_head" and level_scope else ""
        q_user = urllib.parse.quote(username or "")
        initial = _he((fullname or username or "?")[:1])
        rows += f"""<div class="dk-stu tc-card" data-search="{_he(((fullname or '') + ' ' + (username or '')).lower(), quote=True)}" style="margin:0;">
            <div class="dk-stu-head" style="margin-bottom:8px;">
                <div class="dk-avatar" style="background:linear-gradient(135deg,#0f766e,#0d9488);">{initial}</div>
                <div class="nm"><b>{_he(fullname or '-')}</b><span>@{_he(username or '')}</span></div>
            </div>
            <div style="margin-bottom:10px;"><span class="dk-pill {role_tone.get(role, 'mute')}">{_he(role_meta['label'])}{scope_txt}</span></div>
            <div style="display:flex;gap:8px;">
                <a href="/admin/confirm_edit_teacher?target_username={q_user}" class="dk-btn light sm" style="flex:1;">📝 แก้ไข</a>
                <a href="/admin/confirm_delete_teacher?target_username={q_user}" class="dk-btn danger sm" style="flex:1;">🗑️ ลบ</a>
            </div></div>"""

    stats = (dk_stat("บัญชีทั้งหมด", len(teachers), "👥", "blue") + dk_stat("ครูผู้สอน", counts.get("teacher", 0), "👩‍🏫", "green")
             + dk_stat("หัวหน้าระดับ", counts.get("level_head", 0), "🎓", "violet") + dk_stat("ฝ่ายกิจการ", counts.get("affairs", 0), "🛡️", "amber"))
    create = f"""<div class="dk-card"><div class="dk-card-title">➕ สร้างบัญชีครูใหม่</div>
        <form action="/api/admin/create_teacher" method="post" class="dk-grid c2" style="align-items:end;">
            <div><label class="dk-label">Username</label><input class="dk-input" type="text" name="u" placeholder="Username" required></div>
            <div><label class="dk-label">Password</label><input class="dk-input" type="text" name="p" placeholder="Password" required></div>
            <div><label class="dk-label">ชื่อครู</label><input class="dk-input" type="text" name="f" placeholder="ชื่อครู" required></div>
            <div><label class="dk-label">บทบาท / สิทธิ์การใช้งาน</label>
                <select class="dk-select" name="role" id="createRoleSel" onchange="document.getElementById('createScopeWrap').style.display = this.value==='level_head' ? 'block' : 'none';">{role_options}</select></div>
            <div id="createScopeWrap" style="display:none;"><label class="dk-label">ระดับชั้นที่รับผิดชอบ</label><input class="dk-input" type="text" name="level_scope" placeholder="เช่น ม.2"></div>
            <div style="grid-column:1/-1;"><button type="submit" class="dk-btn block" style="padding:13px;">➕ สร้างบัญชี</button></div>
        </form></div>"""
    listing = f"""<div class="dk-card"><div class="dk-card-title">📋 รายชื่อครูในระบบ<small>{len(teachers)} บัญชี</small></div>
        <input id="tcSearch" class="dk-input" placeholder="🔍 ค้นหาชื่อหรือ Username" style="margin-bottom:12px;">
        <div class="dk-grid c3">{rows}</div></div>"""
    js = """<script>(function(){var i=document.getElementById('tcSearch');if(!i)return;i.addEventListener('input',function(){var q=this.value.trim().toLowerCase();
        document.querySelectorAll('.tc-card').forEach(function(c){c.style.display=(!q||c.getAttribute('data-search').indexOf(q)!==-1)?'':'none';});});})();</script>"""
    perm_btn = '<a href="/admin/permissions" class="dk-btn hero">🔐 จัดการสิทธิ์</a>' if access["role"] == "admin" else ""
    return dk_page("จัดการครู & สิทธิ์การใช้งาน", "สร้าง แก้ไข และกำหนดบทบาทของบัญชีครู", f'<div class="dk-stats">{stats}</div>{create}{listing}',
                   back_url, perm_btn, js, icon="👤 ")

@app.post("/api/admin/create_teacher")
async def api_create_teacher(u: str = Form(...), p: str = Form(...), f: str = Form(...), role: str = Form("teacher"), level_scope: str = Form(""), user_session: Optional[str] = Cookie(None)):
    access = get_access(user_session)
    if not access["authenticated"] or not can_manage_teacher_accounts(access):
        return HTMLResponse("Unauthorized", status_code=401)
    if role not in TEACHER_ROLES: role = "teacher"
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    try: 
        cursor.execute("INSERT INTO teachers (username, password, fullname, role, level_scope) VALUES (?, ?, ?, ?, ?)",
                        (u, p, f, role, level_scope.strip() if role == "level_head" else ""))
        conn.commit()
    except sqlite3.IntegrityError: pass
    finally: conn.close()
    return RedirectResponse(url="/admin/teachers", status_code=303)

@app.get("/admin/confirm_delete_teacher", response_class=HTMLResponse)
async def confirm_delete_teacher_page(target_username: str, user_session: Optional[str] = Cookie(None)):
    access = get_access(user_session)
    if not access["authenticated"] or not can_manage_teacher_accounts(access):
        return RedirectResponse(url="/login", status_code=303)
    pw_label = "รหัส Admin ยืนยัน" if access["role"] == "admin" else "รหัสผ่านบัญชีของคุณ (ยืนยันตัวตน)"
    return f"""<html>{STYLE_HEADER}<body style="background: #0f172a; display: flex; align-items: center; justify-content: center; height: 100vh;"><div style="background: white; border-radius: 16px; padding: 30px; width: 100%; max-width: 380px; text-align:center;"><h3 style="color:#ef4444;">🔒 ลบบัญชีผู้ใช้งาน: {target_username}</h3><form action="/api/delete_teacher" method="post"><input type="hidden" name="target_username" value="{target_username}"><input type="password" name="admin_password" placeholder="{pw_label}" required><br><br><button type="submit" class="btn btn-danger" style="width:100%; padding:10px;">🛑 ยืนยันลบ</button></form></div></body></html>"""

@app.post("/api/delete_teacher")
async def api_delete_teacher(target_username: str = Form(...), admin_password: str = Form(...), user_session: Optional[str] = Cookie(None)):
    access = get_access(user_session)
    if not access["authenticated"] or not can_manage_teacher_accounts(access):
        return HTMLResponse("Unauthorized", status_code=401)
    if not verify_manager_password(access, admin_password):
        return HTMLResponse(f"""<html>{STYLE_HEADER}<body><script>smartAlert({{title: 'ผิดพลาด!', message: 'รหัสผ่านไม่ถูกต้อง!', type: 'error', callback: () => {{ history.back(); }} }});</script></body></html>""")
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM teachers WHERE username = ?", (target_username,))
    conn.commit()
    conn.close()
    return HTMLResponse(f"""<html>{STYLE_HEADER}<body><script>smartAlert({{title: 'ดำเนินการเสร็จสิ้น!', message: 'ลบบัญชีครูออกจากระบบแล้ว!', type: 'success', callback: () => {{ window.location.href='/admin/teachers'; }} }});</script></body></html>""")

@app.get("/admin/confirm_edit_teacher", response_class=HTMLResponse)
async def confirm_edit_teacher_page(target_username: str, user_session: Optional[str] = Cookie(None)):
    access = get_access(user_session)
    if not access["authenticated"] or not can_manage_teacher_accounts(access):
        return RedirectResponse(url="/login", status_code=303)
    pw_label = "รหัส Admin ยืนยัน" if access["role"] == "admin" else "รหัสผ่านบัญชีของคุณ (ยืนยันตัวตน)"
    return f"""<html>{STYLE_HEADER}<body style="background: #0f172a; display: flex; align-items: center; justify-content: center; height: 100vh;"><div style="background: white; border-radius: 16px; padding: 30px; width: 100%; max-width: 380px; text-align:center;"><h3 style="color:#f59e0b;">🔐 ยืนยันรหัสผ่านเพื่อแก้ไข: {target_username}</h3><form action="/admin/edit_teacher" method="post"><input type="hidden" name="target_username" value="{target_username}"><input type="password" name="admin_password" placeholder="{pw_label}" required><br><br><button type="submit" class="btn btn-warning" style="width:100%; padding:10px; font-weight:700;">🔓 ยืนยันเพื่อเข้าแก้ไข</button></form><a href="/admin/teachers" style="display:block; margin-top:14px; color:#64748b; font-size:13px; text-decoration:none;">↩ ยกเลิก</a></div></body></html>"""

@app.post("/admin/edit_teacher", response_class=HTMLResponse)
async def admin_edit_teacher_page(target_username: str = Form(...), admin_password: str = Form(...), user_session: Optional[str] = Cookie(None)):
    access = get_access(user_session)
    if not access["authenticated"] or not can_manage_teacher_accounts(access):
        return HTMLResponse("Unauthorized", status_code=401)
    if not verify_manager_password(access, admin_password):
        return alert_redirect("รหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง", type="error")
    back_url = "/admin/dashboard" if access["role"] == "admin" else f"/app/dashboard?user={urllib.parse.quote(access['username'])}"

    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, fullname, role, level_scope FROM teachers WHERE username = ?", (target_username,))
    t = cursor.fetchone()
    conn.close()
    
    if not t: return alert_redirect("ไม่พบข้อมูลครูที่ต้องการ", type="error", url="/admin/teachers")
    current_role = t[3] or "teacher"
    current_scope = t[4] or ""

    role_options = "".join([f'<option value="{key}" {"selected" if key==current_role else ""}>{meta["label"]}</option>' for key, meta in TEACHER_ROLES.items()])
    
    form = f"""<div class="dk-card"><div class="dk-card-title">✏️ แก้ไขข้อมูล: {_he(t[0])}</div>
        <form action="/api/admin/update_teacher" method="post" style="display:grid;gap:12px;">
            <input type="hidden" name="old_username" value="{_he(t[0], quote=True)}">
            <div><label class="dk-label">Username (ชื่อผู้ใช้)</label><input class="dk-input" type="text" name="new_username" value="{_he(t[0], quote=True)}" required></div>
            <div><label class="dk-label">Password (รหัสผ่าน)</label><input class="dk-input" type="text" name="new_password" value="{_he(t[1] or '', quote=True)}" required></div>
            <div><label class="dk-label">ชื่อ-นามสกุลครู</label><input class="dk-input" type="text" name="new_fullname" value="{_he(t[2] or '', quote=True)}" required></div>
            <div><label class="dk-label">บทบาท / สิทธิ์การใช้งาน</label>
                <select class="dk-select" name="new_role" id="editRoleSel" onchange="document.getElementById('editScopeWrap').style.display = this.value==='level_head' ? 'block' : 'none';">{role_options}</select></div>
            <div id="editScopeWrap" style="display:{'block' if current_role=='level_head' else 'none'};">
                <label class="dk-label">ระดับชั้นที่รับผิดชอบ (หัวหน้าระดับ)</label><input class="dk-input" type="text" name="new_level_scope" value="{_he(current_scope, quote=True)}" placeholder="เช่น ม.2"></div>
            <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:12px;padding:12px;font-size:12.5px;color:#b91c1c;line-height:1.6;">
                ⚠️ หากเปลี่ยน Username ครูจะต้องใช้ชื่อใหม่ในการ Login และระบบจะอัปเดตข้อมูลในคลาสเรียนที่เกี่ยวข้องให้อัตโนมัติ</div>
            <button type="submit" class="dk-btn block" style="padding:13px;">💾 บันทึกการเปลี่ยนแปลง</button>
        </form></div>"""
    return dk_page("แก้ไขบัญชีครู", f"@{_he(t[0])}", form, "/admin/teachers", icon="✏️ ")

@app.post("/api/admin/update_teacher")
async def api_update_teacher(old_username: str = Form(...), new_username: str = Form(...), new_password: str = Form(...), new_fullname: str = Form(...), new_role: str = Form("teacher"), new_level_scope: str = Form(""), user_session: Optional[str] = Cookie(None)):
    access = get_access(user_session)
    if not access["authenticated"] or not can_manage_teacher_accounts(access):
        return HTMLResponse("Unauthorized", status_code=401)
    if new_role not in TEACHER_ROLES: new_role = "teacher"
    scope_value = new_level_scope.strip() if new_role == "level_head" else ""
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    try:
        # อัปเดตข้อมูลครู
        cursor.execute(
            "UPDATE teachers SET username = ?, password = ?, fullname = ?, role = ?, level_scope = ? WHERE username = ?",
            (new_username.strip(), new_password.strip(), new_fullname.strip(), new_role, scope_value, old_username)
        )
        # ถ้า Username เปลี่ยน ต้องอัปเดตใน course_groups ด้วย
        if new_username.strip() != old_username:
            cursor.execute("UPDATE course_groups SET teacher_username = ? WHERE teacher_username = ?", (new_username.strip(), old_username))
        
        conn.commit()
    except sqlite3.IntegrityError:
        return alert_redirect("Username นี้มีผู้ใช้งานแล้ว กรุณาใช้ชื่ออื่น", type="warning")
    except Exception as e:
        print(f"❌ DB Update Teacher Error: {e}")
        return alert_redirect("เกิดข้อผิดพลาดในการแก้ไขข้อมูล กรุณาลองใหม่อีกครั้ง", type="error")
    finally:
        conn.close()
    return HTMLResponse(f"""<html>{STYLE_HEADER}<body><script>smartAlert({{title: 'ดำเนินการเสร็จสิ้น!', message: 'อัปเดตข้อมูลบัญชีครูเรียบร้อยแล้ว!', type: 'success', callback: () => {{ window.location.href='/admin/teachers'; }} }});</script></body></html>""")

@app.get("/admin/view_classes", response_class=HTMLResponse)
async def admin_view_classes_page(user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return RedirectResponse(url="/login", status_code=303)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute('SELECT group_id, group_name, teacher_username, branch FROM course_groups')
    course_groups = cursor.fetchall()
    conn.close()
    rows = "".join([f"<tr><td>#{g[0]}</td><td>{g[1]}</td><td>{g[2]}</td><td>{g[3]}</td><td><div style='display:flex;gap:6px;justify-content:center;'><a href='/admin/edit_group?group_id={g[0]}' class='btn btn-warning' style='padding:5px 10px;font-size:11.5px;'>✏️ แก้ไข</a><a href='/admin/confirm_delete_group?group_id={g[0]}&group_name={g[1]}' class='btn btn-danger' style='padding:5px 10px;font-size:11.5px;'>🗑️ ลบ</a></div></td></tr>" for g in course_groups])
    return f"""<html>{STYLE_HEADER}<body><div class="navbar"><h1>📊 คลาสเรียนทั้งหมด</h1><a href="/admin/dashboard" class="btn btn-secondary">⬅ กลับ</a></div><div class="main-container"><div class="card"><table><thead><tr><th>ID</th><th>ชื่อคลาส</th><th>ครู</th><th>วิชาเอก</th><th>การจัดการ</th></tr></thead><tbody>{rows}</tbody></table></div></div></body></html>"""

# ==========================================
# ✏️ [ADMIN EDIT COURSE GROUP SYSTEM]
# ==========================================
@app.get("/admin/edit_group", response_class=HTMLResponse)
async def admin_edit_group_page(group_id: int, user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return RedirectResponse(url="/login", status_code=303)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute('SELECT group_id, group_name, teacher_username, branch FROM course_groups WHERE group_id = ?', (group_id,))
    g = cursor.fetchone()
    cursor.execute('SELECT username, fullname FROM teachers')
    teachers = cursor.fetchall()
    conn.close()
    if not g:
        return alert_redirect("ไม่พบข้อมูลคลาสนี้ในระบบ", type="error", url="/admin/view_classes")
    teacher_options = "".join([f"<option value='{t[0]}' {'selected' if t[0]==g[2] else ''}>{t[1]} ({t[0]})</option>" for t in teachers])
    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> ✏️ แก้ไขข้อมูลคลาสเรียน</h1>
            <a href="/admin/view_classes" class="btn btn-secondary">⬅ กลับ</a>
        </div>
        <div class="main-container">
            <div class="card">
                <h2>✏️ แก้ไขคลาส #{g[0]}</h2>
                <form action="/api/admin/update_group" method="post">
                    <input type="hidden" name="group_id" value="{g[0]}">
                    <input type="hidden" name="old_group_name" value="{g[1]}">
                    <label style="font-size:13px; font-weight:700; color:#475569; display:block; margin-bottom:4px;">ชื่อคลาส / วิชาเรียน</label>
                    <input type="text" name="group_name" value="{g[1]}" placeholder="ชื่อคลาส / วิชาเรียน" required>
                    <label style="font-size:13px; font-weight:700; color:#475569; display:block; margin-bottom:4px;">ครูผู้ดูแลคลาส</label>
                    <select name="teacher_username" required>
                        {teacher_options}
                    </select>
                    <label style="font-size:13px; font-weight:700; color:#475569; display:block; margin-bottom:4px;">สาขาวิชาเอก</label>
                    <input type="text" name="branch" value="{g[3]}" placeholder="สาขาวิชาเอก" required>
                    <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:12px; margin-bottom:14px; font-size:13px; color:#92400e;">
                        ⚠️ หากเปลี่ยนชื่อคลาส ระบบจะอัปเดตชื่อในประวัติเช็คชื่อทั้งหมดให้อัตโนมัติ
                    </div>
                    <button type="submit" class="btn-submit">💾 บันทึกการแก้ไข</button>
                </form>
            </div>
        </div>
    </body></html>
    """

@app.post("/api/admin/update_group")
async def api_update_group(
    group_id: int = Form(...),
    old_group_name: str = Form(...),
    group_name: str = Form(...),
    teacher_username: str = Form(...),
    branch: str = Form(...),
    user_session: Optional[str] = Cookie(None)
):
    if user_session != "admin": return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    try:
        # อัปเดตข้อมูลคลาส
        cursor.execute(
            "UPDATE course_groups SET group_name = ?, teacher_username = ?, branch = ? WHERE group_id = ?",
            (group_name.strip(), teacher_username.strip(), branch.strip(), group_id)
        )
        # ถ้าชื่อคลาสเปลี่ยน ให้อัปเดตประวัติเช็คชื่อด้วย
        if group_name.strip() != old_group_name.strip():
            cursor.execute(
                "UPDATE attendance_logs SET group_name = ? WHERE group_name = ?",
                (group_name.strip(), old_group_name.strip())
            )
        conn.commit()
    except Exception as e:
        print(f"❌ DB Update Group Error: {e}")
        return alert_redirect("เกิดข้อผิดพลาดในการแก้ไข กรุณาลองใหม่อีกครั้ง", type="error")
    finally:
        conn.close()
    return HTMLResponse(f"""<html>{STYLE_HEADER}<body><script>smartAlert({{title: 'ดำเนินการเสร็จสิ้น!', message: 'แก้ไขข้อมูลคลาสเรียบร้อยแล้ว!', type: 'success', callback: () => {{ window.location.href='/admin/view_classes'; }} }});</script></body></html>""")

# ==========================================
# 🗑️ [ADMIN DELETE COURSE GROUP SYSTEM]
# ==========================================
@app.get("/admin/confirm_delete_group", response_class=HTMLResponse)
async def confirm_delete_group_page(group_id: int, group_name: str, user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return RedirectResponse(url="/login", status_code=303)
    return f"""
    <html>{STYLE_HEADER}
    <body style="background: #0f172a; display: flex; align-items: center; justify-content: center; height: 100vh;">
        <div style="background: white; border-radius: 16px; padding: 30px; width: 100%; max-width: 400px; text-align:center; box-shadow: 0 20px 40px rgba(0,0,0,0.3);">
            <div style="font-size: 52px; margin-bottom: 12px;">⚠️</div>
            <h3 style="color:#ef4444; margin: 0 0 8px 0; font-size: 18px;">ยืนยันการลบวิชาเรียน</h3>
            <p style="color:#475569; font-size:14px; margin-bottom:6px;">คุณกำลังจะลบวิชา:</p>
            <p style="background:#fef2f2; border:1px solid #fecaca; border-radius:8px; padding:10px 16px; font-weight:700; color:#b91c1c; font-size:15px; margin-bottom:16px;">#{group_id} — {group_name}</p>
            <p style="color:#ef4444; font-size:13px; font-weight:700; margin-bottom:20px;">⛔ การลบจะลบรายชื่อสมาชิกและประวัติเช็คชื่อทั้งหมดในวิชานี้ไปด้วย!</p>
            <form action="/api/admin/delete_group" method="post">
                <input type="hidden" name="group_id" value="{group_id}">
                <input type="hidden" name="group_name" value="{group_name}">
                <input type="password" name="admin_password" placeholder="รหัส Admin ยืนยัน" required>
                <button type="submit" class="btn-submit" style="background: linear-gradient(135deg, #ef4444, #b91c1c); border-bottom: 3px solid #991b1b; margin-top:4px;">🛑 ยืนยันลบวิชานี้ถาวร</button>
            </form>
            <a href="/admin/view_classes" style="display:block; margin-top:14px; color:#64748b; font-size:13px; text-decoration:none; font-weight:600;">↩ ยกเลิก กลับไปหน้ารายการวิชา</a>
        </div>
    </body></html>
    """

@app.post("/api/admin/delete_group")
async def api_delete_group(group_id: int = Form(...), group_name: str = Form(...), admin_password: str = Form(...), user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return HTMLResponse("Unauthorized", status_code=401)
    if admin_password != ADMIN_PASS:
        return alert_redirect("รหัสผ่าน Admin ไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง", type="error")
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    try:
        # ลบประวัติเช็คชื่อทั้งหมดของวิชานี้
        cursor.execute("DELETE FROM attendance_logs WHERE group_name = ?", (group_name,))
        # ลบรายชื่อสมาชิกในกลุ่มวิชานี้
        cursor.execute("DELETE FROM group_assignments WHERE group_id = ?", (group_id,))
        # ลบวิชาออกจากระบบ
        cursor.execute("DELETE FROM course_groups WHERE group_id = ?", (group_id,))
        conn.commit()
    except Exception as e:
        print(f"❌ DB Delete Group Error: {e}")
        return alert_redirect("เกิดข้อผิดพลาดในการลบ กรุณาลองใหม่อีกครั้ง", type="error")
    finally:
        conn.close()
    return HTMLResponse(f"""<html>{STYLE_HEADER}<body><script>smartAlert({{title: 'ดำเนินการเสร็จสิ้น!', message: 'ลบวิชาและข้อมูลที่เกี่ยวข้องทั้งหมดสำเร็จแล้ว!', type: 'success', callback: () => {{ window.location.href='/admin/view_classes'; }} }});</script></body></html>""")

def init_db():
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS teachers (username TEXT PRIMARY KEY, password TEXT, fullname TEXT)')
    # 🔐 เพิ่มคอลัมน์บทบาท/ขอบเขตระดับชั้น ให้ตารางครู (ใช้ try/except เพราะ SQLite ไม่มี ADD COLUMN IF NOT EXISTS)
    for alter_sql in [
        "ALTER TABLE teachers ADD COLUMN role TEXT DEFAULT 'teacher'",
        "ALTER TABLE teachers ADD COLUMN level_scope TEXT DEFAULT ''",
    ]:
        try:
            cursor.execute(alter_sql)
        except sqlite3.OperationalError:
            pass  # คอลัมน์มีอยู่แล้ว
    cursor.execute("UPDATE teachers SET role='teacher' WHERE role IS NULL")
    # 🎒 บัญชีเข้าสู่ระบบของนักเรียน: ล็อกอินด้วยรหัสประจำตัว + เบอร์โทร (ไม่มีรหัสผ่าน)
    cursor.execute('''CREATE TABLE IF NOT EXISTS student_accounts (
        uid TEXT PRIMARY KEY,
        student_id TEXT UNIQUE,
        phone TEXT
    )''')
    try:
        cursor.execute("ALTER TABLE student_accounts ADD COLUMN photo_url TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass  # คอลัมน์มีอยู่แล้ว
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_accounts_login ON student_accounts (student_id, phone)")
    cursor.execute('CREATE TABLE IF NOT EXISTS course_groups (group_id INTEGER PRIMARY KEY AUTOINCREMENT, group_name TEXT, teacher_username TEXT, branch TEXT)')
    # 👁️ การมองเห็นคะแนน: 'hidden' = นักเรียนดูไม่ได้เลย, 'all' = ดูได้ทุกคน, 'custom' = ดูได้เฉพาะบางคน (ดู grade_visible_students)
    try:
        cursor.execute("ALTER TABLE course_groups ADD COLUMN grades_visibility TEXT DEFAULT 'hidden'")
    except sqlite3.OperationalError:
        pass  # คอลัมน์มีอยู่แล้ว
    cursor.execute('CREATE TABLE IF NOT EXISTS group_assignments (group_id INTEGER, student_uid TEXT, PRIMARY KEY (group_id, student_uid))')
    cursor.execute('CREATE TABLE IF NOT EXISTS attendance_logs (log_id INTEGER PRIMARY KEY AUTOINCREMENT, group_name TEXT, student_name TEXT, student_no TEXT, classroom TEXT, status TEXT, date TEXT, checked_by TEXT)')
    # 🕐 เวลาบันทึก (แยกจาก date เดิมเพื่อไม่กระทบ query เช็กซ้ำที่มีอยู่) — ใช้แสดงในฟีดแจ้งเตือน
    try:
        cursor.execute("ALTER TABLE attendance_logs ADD COLUMN log_time TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass  # คอลัมน์มีอยู่แล้ว
    cursor.execute('CREATE TABLE IF NOT EXISTS maintenance_settings (id INTEGER PRIMARY KEY, is_active INTEGER, mode_type TEXT)')
    cursor.execute("INSERT OR IGNORE INTO maintenance_settings (id, is_active, mode_type) VALUES (1, 0, 'off')")
    cursor.execute('''CREATE TABLE IF NOT EXISTS leave_requests (
        req_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        student_no TEXT,
        classroom TEXT,
        group_id INTEGER,
        group_name TEXT,
        leave_date TEXT,
        reason TEXT,
        status TEXT DEFAULT 'pending',
        submitted_at TEXT,
        reviewed_at TEXT
    )''')
    # 🩺 เพิ่มประเภทการลา (ลาป่วย / ลากิจ / อื่นๆ) ให้คำร้องลา
    try:
        cursor.execute("ALTER TABLE leave_requests ADD COLUMN leave_type TEXT DEFAULT 'อื่นๆ'")
    except sqlite3.OperationalError:
        pass  # คอลัมน์มีอยู่แล้ว
    cursor.execute("UPDATE leave_requests SET leave_type='อื่นๆ' WHERE leave_type IS NULL OR leave_type=''")
    # 🔐 ตารางสิทธิ์แบบ Role-based ที่แก้ไขได้จากหน้าแอดมิน (ไม่ต้องแก้โค้ด)
    cursor.execute('''CREATE TABLE IF NOT EXISTS role_permissions (
        role TEXT,
        perm_key TEXT,
        allowed INTEGER,
        PRIMARY KEY (role, perm_key)
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        level TEXT DEFAULT 'normal',
        created_at TEXT NOT NULL,
        is_active INTEGER DEFAULT 1
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS otp_sessions (
        group_id INTEGER PRIMARY KEY,
        otp TEXT,
        expires_at TEXT,
        is_active INTEGER DEFAULT 0
    )''')
    # 🎖️ ระบบคะแนนความประพฤติ — นักเรียนเริ่มต้นที่ 100 คะแนน แล้วบวก/ลบตามพฤติกรรม
    cursor.execute('''CREATE TABLE IF NOT EXISTS conduct_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_uid TEXT,
        student_name TEXT,
        student_no TEXT,
        classroom TEXT,
        points INTEGER,
        reason TEXT,
        recorded_by TEXT,
        created_at TEXT
    )''')
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_conduct_uid ON conduct_scores (student_uid)")

    # ⚡ เพิ่ม index ให้ตารางที่ query บ่อยที่สุด — ของเดิมไม่มี index เลย พอข้อมูลเยอะขึ้น
    # ทุก query ต้องสแกนทั้งตาราง (full table scan) ทำให้เว็บช้าลงเรื่อยๆ ตามข้อมูลที่สะสม
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance_logs (student_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_group ON attendance_logs (group_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_group_date ON attendance_logs (group_name, date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leave_student_status ON leave_requests (student_name, status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leave_status ON leave_requests (status)")

    # ==========================================
    # 🆕 ตารางเรียน / การบ้าน / ผลการเรียน / ชำระเงิน
    # ==========================================
    # 🗓️ ตารางเรียน: แต่ละแถวคือ 1 คาบเรียนของกลุ่มวิชา (group_id) ในแต่ละวัน
    cursor.execute('''CREATE TABLE IF NOT EXISTS timetable_slots (
        slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        day_of_week INTEGER,
        start_time TEXT,
        end_time TEXT,
        room TEXT,
        created_by TEXT,
        created_at TEXT
    )''')
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timetable_group ON timetable_slots (group_id)")

    # 📖 การบ้าน/งานที่มอบหมาย ผูกกับกลุ่มวิชา
    cursor.execute('''CREATE TABLE IF NOT EXISTS assignments (
        assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        title TEXT,
        detail TEXT,
        due_date TEXT,
        created_by TEXT,
        created_at TEXT,
        is_active INTEGER DEFAULT 1
    )''')
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignments_group ON assignments (group_id)")

    # 📤 งานที่นักเรียนส่ง (1 คน ส่งได้ 1 ครั้งต่อการบ้าน 1 ชิ้น — ส่งซ้ำจะอัปเดตของเดิม)
    cursor.execute('''CREATE TABLE IF NOT EXISTS assignment_submissions (
        submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER,
        student_uid TEXT,
        content TEXT,
        submitted_at TEXT,
        UNIQUE(assignment_id, student_uid)
    )''')
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_submissions_assignment ON assignment_submissions (assignment_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_submissions_student ON assignment_submissions (student_uid)")

    # 📊 ผลการเรียน/คะแนนเก็บ: รายการคะแนน (item) ต่อกลุ่มวิชา + คะแนนรายบุคคลของนักเรียนแต่ละคน
    cursor.execute('''CREATE TABLE IF NOT EXISTS grade_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        item_name TEXT,
        max_score REAL,
        category TEXT DEFAULT 'คะแนนเก็บ',
        created_by TEXT,
        created_at TEXT
    )''')
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_grade_items_group ON grade_items (group_id)")
    cursor.execute('''CREATE TABLE IF NOT EXISTS grade_scores (
        item_id INTEGER,
        student_uid TEXT,
        score REAL,
        PRIMARY KEY (item_id, student_uid)
    )''')
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_grade_scores_student ON grade_scores (student_uid)")
    # 👁️ รายชื่อนักเรียนที่ได้รับอนุญาตพิเศษให้ดูคะแนน เมื่อ group นั้นตั้งโหมด grades_visibility = 'custom'
    cursor.execute('''CREATE TABLE IF NOT EXISTS grade_visible_students (
        group_id INTEGER,
        student_uid TEXT,
        PRIMARY KEY (group_id, student_uid)
    )''')

    # 💳 ชำระเงิน: รายการเรียกเก็บเงินของนักเรียนแต่ละคน (ค่าเทอม ค่ากิจกรรม ฯลฯ)
    cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_uid TEXT,
        item_name TEXT,
        amount REAL,
        status TEXT DEFAULT 'unpaid',
        due_date TEXT,
        paid_at TEXT,
        note TEXT,
        recorded_by TEXT,
        created_at TEXT
    )''')
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_student ON payments (student_uid)")

    # 📋 ระบบตรวจระเบียบ: ตัวชี้วัด (แก้ไขได้) + ผลการตรวจรายวันรายคน
    cursor.execute('''CREATE TABLE IF NOT EXISTS inspection_criteria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        icon TEXT DEFAULT '✅',
        is_active INTEGER DEFAULT 1,
        sort_order INTEGER DEFAULT 0,
        created_by TEXT,
        created_at TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS inspection_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inspect_date TEXT NOT NULL,
        classroom TEXT,
        student_uid TEXT NOT NULL,
        student_name TEXT,
        student_no TEXT,
        criterion_id INTEGER NOT NULL,
        criterion_name TEXT,
        result TEXT NOT NULL,
        inspector TEXT,
        inspector_label TEXT,
        created_at TEXT,
        UNIQUE (inspect_date, student_uid, criterion_id)
    )''')
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_insp_rec_date ON inspection_records (inspect_date, classroom)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_insp_rec_student ON inspection_records (student_uid)")
    # ตัวชี้วัดเริ่มต้น (ใส่เฉพาะตอนตารางยังว่าง เพื่อไม่ฟื้นของที่แอดมินลบไปแล้ว)
    cursor.execute("SELECT COUNT(*) FROM inspection_criteria")
    if cursor.fetchone()[0] == 0:
        _seed_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for _i, (_n, _ic) in enumerate([("ทรงผม", "💈"), ("บัตรนักเรียน", "🪪"), ("การแต่งกาย", "👔")], start=1):
            cursor.execute(
                "INSERT INTO inspection_criteria (name, icon, is_active, sort_order, created_by, created_at) VALUES (?,?,1,?,?,?)",
                (_n, _ic, _i, "system", _seed_now))

    conn.commit()
    conn.close()

# ==========================================
# 🎨 DASHBOARD UI KIT — ชุดสไตล์แดชบอร์ดกลาง (คลาสขึ้นต้น dk-) ใช้ร่วมกันทุกหน้าที่ปรับใหม่
# ==========================================
from html import escape as _he

DASH_KIT = """
<style>
    body.dk-body { background:#f0f4f8; font-family:'Sarabun','Inter',sans-serif; margin:0; color:#0f172a;
        padding-bottom:calc(96px + env(safe-area-inset-bottom,0px)); }
    .dk-body * { box-sizing:border-box; }

    /* ── Hero ── */
    .dk-hero { background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 55%,#1d4ed8 100%); color:#fff;
        padding:calc(env(safe-area-inset-top,0px) + 16px) 16px 58px; position:relative; overflow:hidden; }
    .dk-hero::before { content:""; position:absolute; inset:0; pointer-events:none;
        background:radial-gradient(circle at 92% 15%,rgba(96,165,250,.28),transparent 50%),
                   radial-gradient(circle at 8% 90%,rgba(212,175,55,.16),transparent 45%); }
    .dk-hero-in { position:relative; max-width:1100px; margin:0 auto; }
    .dk-hero-top { display:flex; align-items:center; justify-content:space-between; gap:10px; margin-bottom:14px; }
    .dk-back { width:38px; height:38px; border-radius:11px; background:rgba(255,255,255,.12);
        border:1px solid rgba(255,255,255,.2); color:#fff; display:flex; align-items:center; justify-content:center;
        text-decoration:none; font-size:18px; font-weight:700; }
    .dk-hero-actions { display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end; }
    .dk-hero h1 { margin:0; font-size:22px; font-weight:800; display:flex; align-items:center; gap:10px; line-height:1.25; }
    .dk-hero p { margin:5px 0 0; font-size:13px; color:rgba(255,255,255,.72); }
    .dk-wrap { max-width:1100px; margin:-36px auto 0; padding:0 14px; position:relative; }

    /* ── Stat tiles ── */
    .dk-stats { display:grid; grid-template-columns:repeat(2,1fr); gap:10px; margin-bottom:16px; }
    @media (min-width:720px) { .dk-stats { grid-template-columns:repeat(4,1fr); } }
    .dk-stat { background:#fff; border-radius:16px; padding:13px; border:1px solid #e6eaf1;
        box-shadow:0 8px 20px -10px rgba(15,23,42,.22); display:flex; align-items:center; gap:11px; min-width:0; }
    .dk-stat-ico { width:42px; height:42px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:20px; flex:none; }
    .dk-stat b { display:block; font-size:22px; font-weight:800; line-height:1.1; }
    .dk-stat span { font-size:11.5px; color:#64748b; font-weight:600; }
    .dk-stat b span { font-size:inherit; color:inherit; font-weight:inherit; }
    .t-blue { background:#dbeafe; color:#1d4ed8; } .t-green { background:#dcfce7; color:#15803d; }
    .t-red { background:#fee2e2; color:#b91c1c; } .t-amber { background:#fef3c7; color:#b45309; }
    .t-violet { background:#ede9fe; color:#6d28d9; } .t-slate { background:#e2e8f0; color:#334155; }

    /* ── Cards / layout ── */
    .dk-card { background:#fff; border-radius:18px; padding:16px; border:1px solid #e6eaf1;
        box-shadow:0 1px 3px rgba(15,23,42,.05); margin-bottom:14px; }
    .dk-card-title { display:flex; align-items:center; justify-content:space-between; gap:8px;
        font-size:14.5px; font-weight:800; margin:0 0 12px; }
    .dk-card-title small { font-size:11.5px; font-weight:600; color:#64748b; }
    .dk-section { font-size:12px; font-weight:800; color:#64748b; letter-spacing:.4px; margin:18px 4px 10px; }
    .dk-grid { display:grid; gap:12px; grid-template-columns:1fr; }
    @media (min-width:720px) { .dk-grid.c2 { grid-template-columns:repeat(2,1fr); } .dk-grid.c3 { grid-template-columns:repeat(3,1fr); } }
    .dk-empty { text-align:center; color:#94a3b8; padding:34px 10px; font-size:14px; }
    .dk-empty .em { font-size:38px; display:block; margin-bottom:6px; }
    .dk-note { background:#eff6ff; border:1px solid #bfdbfe; color:#1e40af; border-radius:14px; padding:12px 14px; font-size:13px; line-height:1.7; margin-bottom:14px; }

    /* ── Buttons / inputs ── */
    .dk-btn { display:inline-flex; align-items:center; justify-content:center; gap:6px; padding:10px 16px; border:none;
        border-radius:11px; font-family:inherit; font-size:13.5px; font-weight:700; cursor:pointer; text-decoration:none;
        background:linear-gradient(135deg,#1d4ed8,#1e3a8a); color:#fff; box-shadow:0 6px 14px -6px rgba(30,58,138,.5); }
    .dk-btn:active { transform:translateY(1px); }
    .dk-btn.hero { background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.25); box-shadow:none; padding:8px 12px; font-size:12.5px; }
    .dk-btn.light { background:#f1f5f9; color:#334155; box-shadow:none; }
    .dk-btn.green { background:linear-gradient(135deg,#16a34a,#15803d); box-shadow:0 6px 14px -6px rgba(21,128,61,.5); }
    .dk-btn.danger { background:#fee2e2; color:#b91c1c; box-shadow:none; }
    .dk-btn.sm { padding:6px 10px; font-size:12px; border-radius:9px; }
    .dk-btn.block { width:100%; }
    .dk-input, .dk-select { width:100%; padding:10px 12px; border:1.5px solid #dbe2ec; border-radius:11px; font-family:inherit;
        font-size:14px; background:#fff; color:#0f172a; }
    .dk-body input.dk-input, .dk-body select.dk-select { margin-bottom:0; }
    .dk-body table.dk-table { border:none; margin:0; }
    .dk-body .dk-hero h1 { color:#fff; }
    .dk-input:focus, .dk-select:focus { outline:none; border-color:#1d4ed8; box-shadow:0 0 0 3px rgba(29,78,216,.12); }
    .dk-label { display:block; font-size:12px; font-weight:700; color:#64748b; margin:0 0 5px; }
    .dk-filter { display:grid; grid-template-columns:1fr; gap:10px; align-items:end; }
    @media (min-width:720px) { .dk-filter { grid-template-columns:repeat(4,1fr) auto; } }

    /* ── Pills / chips ── */
    .dk-pill { display:inline-flex; align-items:center; gap:4px; padding:3px 10px; border-radius:999px; font-size:11.5px; font-weight:800; }
    .dk-pill.ok { background:#dcfce7; color:#15803d; } .dk-pill.bad { background:#fee2e2; color:#b91c1c; }
    .dk-pill.mute { background:#f1f5f9; color:#64748b; } .dk-pill.warn { background:#fef3c7; color:#b45309; }
    .dk-chips { display:flex; gap:8px; overflow-x:auto; padding-bottom:4px; }
    .dk-chip { flex:none; padding:7px 14px; border-radius:999px; background:#fff; border:1.5px solid #dbe2ec; color:#475569;
        font-size:12.5px; font-weight:700; cursor:pointer; font-family:inherit; }
    .dk-chip.on { background:#1d4ed8; border-color:#1d4ed8; color:#fff; }

    /* ── Progress ── */
    .dk-track { height:8px; background:#e8edf5; border-radius:999px; overflow:hidden; }
    .dk-track > i { display:block; height:100%; border-radius:999px; background:linear-gradient(90deg,#22c55e,#16a34a); }
    .dk-track.blue > i { background:linear-gradient(90deg,#60a5fa,#1d4ed8); }
    .dk-rate-row { display:grid; grid-template-columns:130px 1fr 54px; gap:10px; align-items:center; margin:11px 0; font-size:13px; font-weight:700; }
    .dk-rate-row em { font-style:normal; text-align:right; color:#475569; }

    /* ── Room cards ── */
    .dk-room { display:block; text-decoration:none; color:inherit; background:#fff; border:1px solid #e6eaf1; border-radius:16px; padding:14px;
        box-shadow:0 1px 3px rgba(15,23,42,.05); }
    .dk-room:active { transform:scale(.985); }
    .dk-room-top { display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; }
    .dk-room-top b { font-size:17px; font-weight:800; }
    .dk-room small { display:flex; justify-content:space-between; margin-top:7px; font-size:11.5px; color:#64748b; font-weight:600; }

    /* ── Student inspection rows ── */
    .dk-stu { background:#fff; border:1.5px solid #e6eaf1; border-radius:16px; padding:12px; margin-bottom:10px; }
    .dk-stu.has-fail { border-color:#fca5a5; background:#fffafa; }
    .dk-stu.is-done { border-color:#86efac; }
    .dk-stu-head { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
    .dk-avatar { width:38px; height:38px; border-radius:50%; background:linear-gradient(135deg,#1d4ed8,#1e3a8a); color:#fff;
        display:flex; align-items:center; justify-content:center; font-weight:800; flex:none; }
    .dk-stu-head .nm { flex:1; min-width:0; }
    .dk-stu-head .nm b { display:block; font-size:14.5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .dk-stu-head .nm span { font-size:11.5px; color:#64748b; font-weight:600; }
    .dk-crits { display:grid; grid-template-columns:1fr; gap:8px; }
    @media (min-width:720px) { .dk-crits { grid-template-columns:repeat(3,1fr); } }
    .dk-crit { display:flex; align-items:center; justify-content:space-between; gap:8px; background:#f8fafc; border-radius:12px; padding:7px 8px 7px 11px; }
    .dk-crit > span { font-size:13px; font-weight:700; min-width:0; }
    .dk-seg { display:flex; flex:none; background:#e8edf5; border-radius:10px; padding:3px; gap:3px; }
    .dk-seg button { border:none; background:transparent; padding:7px 12px; border-radius:8px; font-family:inherit;
        font-size:12.5px; font-weight:800; color:#64748b; cursor:pointer; min-width:58px; }
    .dk-seg button.on.p { background:#16a34a; color:#fff; box-shadow:0 3px 8px -3px rgba(22,163,74,.7); }
    .dk-seg button.on.f { background:#dc2626; color:#fff; box-shadow:0 3px 8px -3px rgba(220,38,38,.7); }

    /* ── Sticky save bar ── */
    .dk-savebar { position:fixed; left:0; right:0; bottom:0; z-index:60; background:rgba(255,255,255,.96); backdrop-filter:blur(10px);
        border-top:1px solid #e6eaf1; padding:10px 14px calc(10px + env(safe-area-inset-bottom,0px)); display:flex; align-items:center; gap:10px; justify-content:center; }
    .dk-savebar .msg { font-size:12.5px; font-weight:700; color:#64748b; flex:1; max-width:520px; }
    .dk-savebar .msg.dirty { color:#b45309; }
    .dk-toast { position:fixed; left:50%; bottom:90px; transform:translateX(-50%) translateY(20px); background:#0f172a; color:#fff;
        padding:11px 18px; border-radius:12px; font-size:13.5px; font-weight:700; opacity:0; pointer-events:none; transition:.25s; z-index:80; }
    .dk-toast.show { opacity:1; transform:translateX(-50%) translateY(0); }

    /* ── Tables / list rows ── */
    .dk-tablewrap { overflow-x:auto; border-radius:14px; border:1px solid #e6eaf1; background:#fff; }
    table.dk-table { width:100%; border-collapse:collapse; margin:0; box-shadow:none; border-radius:0; }
    table.dk-table th { background:#f8fafc; color:#475569; font-size:12px; font-weight:800; padding:11px 12px; text-align:left; border-bottom:1px solid #e6eaf1; white-space:nowrap; }
    table.dk-table td { padding:11px 12px; font-size:13.5px; border-bottom:1px solid #eef2f7; text-align:left; background:#fff; }
    table.dk-table tr:last-child td { border-bottom:none; }
    .dk-row { display:flex; flex-wrap:wrap; align-items:center; gap:12px; background:#fff; border:1px solid #e6eaf1; border-radius:14px; padding:12px; margin-bottom:9px; }
    .dk-row .grow { flex:1; min-width:0; }
    .dk-row .grow b { display:block; font-size:14.5px; }
    .dk-row .grow span { font-size:12px; color:#64748b; font-weight:600; }
    .dk-ico-box { width:42px; height:42px; border-radius:12px; background:#eef2ff; display:flex; align-items:center; justify-content:center; font-size:21px; flex:none; }
    .dk-trend { display:flex; align-items:flex-end; gap:5px; height:90px; }
    .dk-trend div { flex:1; min-width:6px; background:linear-gradient(180deg,#60a5fa,#1d4ed8); border-radius:5px 5px 2px 2px; position:relative; }
    .dk-trend-lbl { display:flex; justify-content:space-between; font-size:10.5px; color:#94a3b8; margin-top:6px; font-weight:600; }
    @media (max-width:520px) { table.dk-table th, table.dk-table td { padding:9px 7px; font-size:12.5px; } }
    @media (max-width:520px) { .dk-rate-row { grid-template-columns:96px 1fr 46px; } .dk-hero h1 { font-size:19px; } }
</style>
"""


def dk_page(title: str, subtitle: str, body: str, back_url: str, actions: str = "", extra: str = "", icon: str = "") -> str:
    """ห่อเนื้อหาด้วยโครงหน้าแดชบอร์ดมาตรฐาน (hero + wrap) — body/actions/extra ต้อง escape มาแล้ว"""
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    return f"""<html>{STYLE_HEADER}{DASH_KIT}<body class="dk-body">
{PAGE_LOADER}
<div class="dk-hero"><div class="dk-hero-in">
    <div class="dk-hero-top">
        <a href="{back_url}" class="dk-back" aria-label="กลับ">‹</a>
        <div class="dk-hero-actions">{actions}</div>
    </div>
    <h1>{icon}{title}</h1>{sub}
</div></div>
<div class="dk-wrap">{body}</div>
{extra}
</body></html>"""


def dk_stat(label: str, value, icon: str, tone: str = "blue") -> str:
    return (f'<div class="dk-stat"><div class="dk-stat-ico t-{tone}">{icon}</div>'
            f'<div><b>{value}</b><span>{label}</span></div></div>')


def dk_empty(icon: str, text: str) -> str:
    return f'<div class="dk-empty"><span class="em">{icon}</span>{text}</div>'


# ==========================================
# 📋 ระบบตรวจระเบียบนักเรียน (ครู / ฝ่ายกิจการ ติ๊กผ่าน-ไม่ผ่านตามตัวชี้วัด)
#   /inspection            ตรวจรายห้อง/รายวัน
#   /inspection/report     รายงานสรุป (+ส่งออก CSV)
#   /inspection/criteria   เพิ่ม/ลบ/เปิด-ปิด ตัวชี้วัด
#   /student/inspection    นักเรียนดูผลของตัวเอง
# ==========================================
import json as _json
import csv as _csv
import io as _io

_SVG_CLIP = '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>'
_SVG_BARS = '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>'
_SVG_SLIDERS = '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>'

# ── ไอคอนเส้น (ทำเอง แทนอิโมจิ) ใช้กับสถิติ/หัวข้อ/ปุ่มของระบบตรวจระเบียบทั้งหมด ──
def _ic(svg_inner: str, size: int = 20, stroke: float = 2) -> str:
    """คืน <svg> เส้น ขนาด/สีปรับได้ — สีจะรับช่วงจาก currentColor ของกล่องที่ห่ออยู่เสมอ"""
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
            f'stroke="currentColor" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">{svg_inner}</svg>')

_SVG_SCHOOL    = '<path d="M12 3 21 9v11H3V9Z"/><path d="M9 20v-6h6v6"/><path d="M3 9l9-6 9 6"/>'
_SVG_BACKPACK  = '<path d="M8 3h8a2 2 0 0 1 2 2v2H6V5a2 2 0 0 1 2-2Z"/><path d="M6 7h12v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7Z"/><path d="M9 12h6"/><path d="M10 3v2"/><path d="M14 3v2"/>'
_SVG_USERS     = '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
_SVG_CHECK_C   = '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>'
_SVG_ALERT     = '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>'
_SVG_CALENDAR  = '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>'
_SVG_SAVE      = '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2Z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/>'
_SVG_SEARCH    = '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>'
_SVG_CLOCK     = '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'
_SVG_SETTINGS  = '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z"/>'
_SVG_CLIPBOARD = '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/><line x1="8" y1="11" x2="16" y2="11"/><line x1="8" y1="15" x2="13" y2="15"/>'
_SVG_DOWNLOAD  = '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>'
_SVG_MEDAL     = '<circle cx="12" cy="8" r="6"/><path d="M8.21 13.89 7 23l5-3 5 3-1.21-9.12"/>'
_SVG_SMILE     = '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/>'
_SVG_INBOX     = '<polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11Z"/>'
_SVG_PAUSE     = '<rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/>'
_SVG_PLUS      = '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>'
_SVG_BULB      = '<path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2Z"/>'
_SVG_INFO      = '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>'
_SVG_KEY       = '<circle cx="8" cy="15" r="4"/><path d="M10.5 12.5 20 3"/><path d="M17 6l3 3"/><path d="M14 9l2.5 2.5"/>'
_SVG_FOLDER    = '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2Z"/>'
_SVG_EDIT      = '<path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5Z"/>'
_SVG_TRASH     = '<polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>'
_SVG_EYE       = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8Z"/><circle cx="12" cy="12" r="3"/>'
_SVG_USER_PLUS = '<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/>'
_SVG_IMAGE     = '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>'


def inspection_menu_cells(access: dict) -> str:
    """เมนูระบบตรวจระเบียบสำหรับหน้าแดชบอร์ดครู/แอดมิน — แสดงเฉพาะที่บทบาทนี้มีสิทธิ์"""
    def cell(href, svg, bg, color, label):
        return f'''<a href="{href}" class="ah-cell">
            <div class="ah-cell-icon-wrap" style="background:{bg};color:{color};">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{svg}</svg>
            </div>
            <span class="ah-cell-label">{label}</span>
        </a>'''
    cells = ""
    if can_manage_inspection(access):
        cells += cell("/inspection", _SVG_CLIP, "#ecfdf5", "#047857", "ตรวจระเบียบ")
    if can_view_inspection_report(access):
        cells += cell("/inspection/report", _SVG_BARS, "#eff6ff", "#1d4ed8", "รายงานระเบียบ")
    if can_manage_inspection_criteria(access):
        cells += cell("/inspection/criteria", _SVG_SLIDERS, "#fff7ed", "#c2410c", "ตัวชี้วัดระเบียบ")
    return cells


def _insp_back_url(access: dict) -> str:
    if access.get("role") == "admin":
        return "/admin/dashboard"
    return f"/app/dashboard?user={urllib.parse.quote(access.get('username') or '')}"


def _insp_today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _insp_valid_date(s: Optional[str]) -> str:
    try:
        return datetime.strptime((s or "").strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return _insp_today()


def _insp_thai_date(s: str) -> str:
    try:
        d = datetime.strptime(s, "%Y-%m-%d")
        return f"{d.day:02d}/{d.month:02d}/{d.year + 543}"
    except ValueError:
        return s


def _insp_level_key(lv: str):
    digits = ''.join(ch for ch in lv if ch.isdigit())
    return (0, int(digits), lv) if digits else (1, 0, lv)


def get_inspection_criteria(active_only: bool = True) -> list:
    conn = sqlite3.connect('attendance_pro.db')
    cur = conn.cursor()
    q = "SELECT id, name, icon, is_active, sort_order FROM inspection_criteria"
    if active_only:
        q += " WHERE is_active = 1"
    q += " ORDER BY sort_order, id"
    cur.execute(q)
    rows = [{"id": r[0], "name": r[1], "icon": r[2] or "✅", "is_active": r[3], "sort_order": r[4]} for r in cur.fetchall()]
    conn.close()
    return rows


def _insp_visible_students(access: dict) -> list:
    return [s for s in get_sorted_master_students() if in_inspection_scope(access, s['class'])]


def _insp_gate(user_session: Optional[str], checker, json_mode: bool = False):
    """คืน (access, error_response|None)"""
    access = get_access(user_session)
    ok = access["authenticated"] and access["role"] != "student" and checker(access)
    if not ok:
        if json_mode:
            return access, JSONResponse({"ok": False, "error": "ไม่มีสิทธิ์ใช้งานฟังก์ชันนี้"}, status_code=403)
        return access, RedirectResponse(url="/login", status_code=303)
    if access["role"] == "level_head" and not access["level_scope"]:
        msg = "บัญชีของคุณยังไม่ถูกกำหนดระดับชั้นที่รับผิดชอบ กรุณาติดต่อผู้ดูแลระบบ"
        if json_mode:
            return access, JSONResponse({"ok": False, "error": msg}, status_code=403)
        return access, alert_redirect(msg, type="error", url=_insp_back_url(access))
    return access, None


# ──────────────── หน้าตรวจระเบียบ ────────────────
INSPECTION_JS = """
<script>
(function () {
    var ROOM = __ROOM__, DATE = __DATE__;
    var dirty = {};
    var list = document.getElementById('stuList');
    var filterMode = 'all', q = '';
    var toastEl = document.getElementById('dkToast');

    function toast(t) { toastEl.textContent = t; toastEl.classList.add('show'); setTimeout(function () { toastEl.classList.remove('show'); }, 2200); }
    function keyOf(uid, cid) { return JSON.stringify([uid, cid]); }

    function setVal(seg, v) {
        seg.setAttribute('data-v', v);
        var bs = seg.querySelectorAll('button');
        for (var i = 0; i < bs.length; i++) bs[i].classList.toggle('on', bs[i].getAttribute('data-v') === v);
    }
    function markDirty(row, seg) {
        var uid = row.getAttribute('data-uid'), cid = seg.getAttribute('data-cid');
        var v = seg.getAttribute('data-v') || '', orig = seg.getAttribute('data-orig') || '';
        var k = keyOf(uid, cid);
        if (v === orig) delete dirty[k]; else dirty[k] = [uid, parseInt(cid, 10), v];
    }
    function refresh() {
        var rows = list.querySelectorAll('.dk-stu');
        var done = 0, fail = 0, shown = 0;
        for (var i = 0; i < rows.length; i++) {
            var segs = rows[i].querySelectorAll('.dk-seg'), marked = 0, f = 0;
            for (var j = 0; j < segs.length; j++) {
                var v = segs[j].getAttribute('data-v') || '';
                if (v) marked++;
                if (v === 'fail') f++;
            }
            var complete = marked === segs.length;
            rows[i].classList.toggle('has-fail', f > 0);
            rows[i].classList.toggle('is-done', complete && f === 0);
            if (complete) done++;
            if (f > 0) fail++;
            var name = (rows[i].getAttribute('data-name') || '').toLowerCase();
            var show = (!q || name.indexOf(q) !== -1 || (rows[i].getAttribute('data-no') || '') === q);
            if (filterMode === 'todo') show = show && !complete;
            if (filterMode === 'fail') show = show && f > 0;
            rows[i].style.display = show ? '' : 'none';
            if (show) shown++;
        }
        document.getElementById('stDone').textContent = done;
        document.getElementById('stTodo').textContent = rows.length - done;
        document.getElementById('stFail').textContent = fail;
        document.getElementById('prog').style.width = (rows.length ? Math.round(done * 100 / rows.length) : 0) + '%';
        document.getElementById('emptyHint').style.display = shown ? 'none' : 'block';
        var n = Object.keys(dirty).length, msg = document.getElementById('saveMsg');
        msg.textContent = n ? ('มีการเปลี่ยนแปลงที่ยังไม่บันทึก ' + n + ' รายการ') : 'ผลตรวจทั้งหมดถูกบันทึกแล้ว';
        msg.classList.toggle('dirty', n > 0);
        document.getElementById('saveBtn').disabled = n === 0;
        document.getElementById('saveBtn').style.opacity = n ? '1' : '.5';
    }

    list.addEventListener('click', function (e) {
        var btn = e.target.closest('.dk-seg button');
        if (btn) {
            var seg = btn.parentNode, row = seg.closest('.dk-stu');
            var nv = btn.getAttribute('data-v');
            if (seg.getAttribute('data-v') === nv) nv = '';
            setVal(seg, nv); markDirty(row, seg); refresh(); return;
        }
        var ap = e.target.closest('[data-allpass]');
        if (ap) {
            var row2 = ap.closest('.dk-stu'), segs = row2.querySelectorAll('.dk-seg');
            for (var i = 0; i < segs.length; i++) if (!segs[i].getAttribute('data-v')) { setVal(segs[i], 'pass'); markDirty(row2, segs[i]); }
            refresh();
        }
    });

    document.getElementById('passAll').addEventListener('click', function () {
        var rows = list.querySelectorAll('.dk-stu');
        for (var i = 0; i < rows.length; i++) {
            if (rows[i].style.display === 'none') continue;
            var segs = rows[i].querySelectorAll('.dk-seg');
            for (var j = 0; j < segs.length; j++) if (!segs[j].getAttribute('data-v')) { setVal(segs[j], 'pass'); markDirty(rows[i], segs[j]); }
        }
        refresh(); toast('ติ๊ก “ผ่าน” ให้ช่องที่ยังว่างแล้ว — อย่าลืมกดบันทึก');
    });

    var chips = document.querySelectorAll('.dk-chip');
    for (var c = 0; c < chips.length; c++) chips[c].addEventListener('click', function () {
        for (var k = 0; k < chips.length; k++) chips[k].classList.remove('on');
        this.classList.add('on'); filterMode = this.getAttribute('data-f'); refresh();
    });
    document.getElementById('search').addEventListener('input', function () { q = this.value.trim().toLowerCase(); refresh(); });

    document.getElementById('saveBtn').addEventListener('click', function () {
        var changes = Object.keys(dirty).map(function (k) { return dirty[k]; });
        if (!changes.length) return;
        var btn = this; var lbl = document.getElementById('saveBtnLabel');
        btn.disabled = true; lbl.textContent = 'กำลังบันทึก...';
        fetch('/api/inspection/save', { method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ room: ROOM, date: DATE, changes: changes }) })
        .then(function (r) { return r.json(); })
        .then(function (j) {
            lbl.textContent = 'บันทึกผลตรวจ';
            if (!j.ok) { btn.disabled = false; toast('❌ ' + (j.error || 'บันทึกไม่สำเร็จ')); return; }
            var segs = list.querySelectorAll('.dk-seg');
            for (var i = 0; i < segs.length; i++) segs[i].setAttribute('data-orig', segs[i].getAttribute('data-v') || '');
            dirty = {}; refresh(); toast('✅ บันทึกแล้ว ' + j.saved + ' รายการ');
        })
        .catch(function () { btn.disabled = false; lbl.textContent = 'บันทึกผลตรวจ'; toast('❌ เชื่อมต่อเซิร์ฟเวอร์ไม่ได้'); });
    });

    window.addEventListener('beforeunload', function (e) { if (Object.keys(dirty).length) { e.preventDefault(); e.returnValue = ''; } });
    refresh();
})();
</script>
"""


@app.get("/inspection", response_class=HTMLResponse)
async def inspection_page(room: Optional[str] = None, date: Optional[str] = None, user_session: Optional[str] = Cookie(None)):
    access, err = _insp_gate(user_session, can_manage_inspection)
    if err: return err
    date = _insp_valid_date(date)
    back = _insp_back_url(access)
    students = _insp_visible_students(access)
    criteria = get_inspection_criteria(active_only=True)

    actions = ""
    if can_view_inspection_report(access):
        actions += f'<a href="/inspection/report" class="dk-btn hero">{_ic(_SVG_BARS, 15)} รายงาน</a>'
    if can_manage_inspection_criteria(access):
        actions += f'<a href="/inspection/criteria" class="dk-btn hero">{_ic(_SVG_SLIDERS, 15)} ตัวชี้วัด</a>'

    if not criteria:
        link = '<br><a href="/inspection/criteria" class="dk-btn" style="margin-top:12px;">ไปเพิ่มตัวชี้วัด</a>' if can_manage_inspection_criteria(access) else ""
        body = f'<div class="dk-card">{dk_empty(_ic(_SVG_CLIPBOARD, 38, 1.5), "ยังไม่มีตัวชี้วัดที่เปิดใช้งาน — โปรดให้ฝ่ายกิจการ/ผู้ดูแลระบบเพิ่มตัวชี้วัดก่อน" + link)}</div>'
        return dk_page("ตรวจระเบียบนักเรียน", "ยังไม่มีตัวชี้วัด", body, back, actions, icon=_ic(_SVG_CLIPBOARD, 22))

    rooms = sorted(set(s['class'] for s in students))

    # ───── ยังไม่เลือกห้อง: การ์ดเลือกห้อง ─────
    if not room:
        conn = sqlite3.connect('attendance_pro.db')
        cur = conn.cursor()
        cur.execute("""SELECT classroom, COUNT(DISTINCT student_uid), SUM(CASE WHEN result='fail' THEN 1 ELSE 0 END)
                       FROM inspection_records WHERE inspect_date = ? GROUP BY classroom""", (date,))
        prog = {r[0]: (r[1], r[2] or 0) for r in cur.fetchall()}
        conn.close()

        by_level = {}
        for r in rooms:
            by_level.setdefault(get_grade_level(r), []).append(r)
        count_in_room = {}
        for s in students:
            count_in_room[s['class']] = count_in_room.get(s['class'], 0) + 1

        total_students = len(students)
        checked_total = sum(prog.get(r, (0, 0))[0] for r in rooms)
        fail_total = sum(prog.get(r, (0, 0))[1] for r in rooms)
        stats = (dk_stat("ห้องที่ดูแล", len(rooms), _ic(_SVG_SCHOOL), "blue") + dk_stat("นักเรียนทั้งหมด", total_students, _ic(_SVG_BACKPACK), "violet")
                 + dk_stat("ตรวจแล้ว (คน)", checked_total, _ic(_SVG_CHECK_C), "green") + dk_stat("ไม่ผ่าน (รายการ)", fail_total, _ic(_SVG_ALERT), "red"))

        sections = ""
        for lv in sorted(by_level, key=_insp_level_key):
            cards = ""
            for r in by_level[lv]:
                n = count_in_room.get(r, 0)
                done, fails = prog.get(r, (0, 0))
                pct = round(done * 100 / n) if n else 0
                badge = f'<span class="dk-pill bad">ไม่ผ่าน {fails}</span>' if fails else (
                    '<span class="dk-pill ok">ตรวจแล้ว</span>' if n and done >= n else '<span class="dk-pill mute">รอตรวจ</span>')
                cards += f"""<a class="dk-room" href="/inspection?room={urllib.parse.quote(r)}&date={date}">
                    <div class="dk-room-top"><b>{_he(r)}</b>{badge}</div>
                    <div class="dk-track blue"><i style="width:{pct}%"></i></div>
                    <small><span>ตรวจแล้ว {done}/{n} คน</span><span>{pct}%</span></small></a>"""
            sections += f'<div class="dk-section">ระดับชั้น {_he(lv)}</div><div class="dk-grid c3">{cards}</div>'

        date_form = f"""<div class="dk-card"><form method="get" action="/inspection" class="dk-filter" style="grid-template-columns:1fr auto;">
            <div><label class="dk-label" style="display:flex;align-items:center;gap:5px;">{_ic(_SVG_CALENDAR, 14)} วันที่ตรวจ</label><input type="date" name="date" value="{date}" class="dk-input"></div>
            <button class="dk-btn" type="submit">ดูวันนี้</button></form></div>"""
        body = f'<div class="dk-stats">{stats}</div>{date_form}{sections or dk_empty(_ic(_SVG_SCHOOL, 38, 1.5), "ไม่พบห้องเรียนในขอบเขตของคุณ")}'
        return dk_page("ตรวจระเบียบนักเรียน", f"เลือกห้องเพื่อเริ่มตรวจ · วันที่ {_insp_thai_date(date)} · {len(criteria)} ตัวชี้วัด",
                       body, back, actions, icon=_ic(_SVG_CLIPBOARD, 22))

    # ───── เลือกห้องแล้ว: ฟอร์มติ๊กผ่าน/ไม่ผ่าน ─────
    if room not in rooms:
        return alert_redirect("ไม่พบห้องเรียนนี้ หรือคุณไม่มีสิทธิ์ตรวจห้องนี้", type="error", url="/inspection")
    stu = [s for s in students if s['class'] == room]
    conn = sqlite3.connect('attendance_pro.db')
    cur = conn.cursor()
    cur.execute("SELECT student_uid, criterion_id, result FROM inspection_records WHERE inspect_date = ? AND classroom = ?", (date, room))
    existing = {(r[0], r[1]): r[2] for r in cur.fetchall()}
    conn.close()

    rows = ""
    for s in stu:
        crit_html = ""
        for c in criteria:
            v = existing.get((s['uid'], c['id']), "")
            p_on = " on" if v == "pass" else ""
            f_on = " on" if v == "fail" else ""
            crit_html += f"""<div class="dk-crit"><span>{_he(c['icon'])} {_he(c['name'])}</span>
                <div class="dk-seg" data-cid="{c['id']}" data-v="{v}" data-orig="{v}">
                    <button type="button" class="p{p_on}" data-v="pass">ผ่าน</button>
                    <button type="button" class="f{f_on}" data-v="fail">ไม่ผ่าน</button>
                </div></div>"""
        initial = _he(s['name'][:1]) if s['name'] else "?"
        rows += f"""<div class="dk-stu" data-uid="{_he(s['uid'], quote=True)}" data-name="{_he(s['name'], quote=True)}" data-no="{_he(s['no'], quote=True)}">
            <div class="dk-stu-head"><div class="dk-avatar">{initial}</div>
                <div class="nm"><b>{_he(s['name'])}</b><span>เลขที่ {_he(s['no'])}</span></div>
                <button type="button" class="dk-btn light sm" data-allpass>ผ่านทั้งหมด</button></div>
            <div class="dk-crits">{crit_html}</div></div>"""

    stats = (dk_stat("นักเรียนในห้อง", len(stu), _ic(_SVG_BACKPACK), "blue") + dk_stat("ตรวจครบแล้ว", '<span id="stDone">0</span>', _ic(_SVG_CHECK_C), "green")
             + dk_stat("ยังไม่ครบ", '<span id="stTodo">0</span>', _ic(_SVG_CLOCK), "amber") + dk_stat("มีรายการไม่ผ่าน", '<span id="stFail">0</span>', _ic(_SVG_ALERT), "red"))
    tools = f"""<div class="dk-card">
        <div class="dk-track blue" style="margin-bottom:12px;"><i id="prog" style="width:0%"></i></div>
        <div style="position:relative;margin-bottom:10px;">
            <span style="position:absolute;left:12px;top:50%;transform:translateY(-50%);color:#94a3b8;display:flex;">{_ic(_SVG_SEARCH, 16)}</span>
            <input id="search" class="dk-input" placeholder="ค้นหาชื่อ หรือเลขที่" style="padding-left:36px;">
        </div>
        <div class="dk-chips"><button type="button" class="dk-chip on" data-f="all">ทั้งหมด</button>
            <button type="button" class="dk-chip" data-f="todo">ยังไม่ครบ</button>
            <button type="button" class="dk-chip" data-f="fail">ไม่ผ่าน</button>
            <button type="button" class="dk-chip" id="passAll" style="border-color:#86efac;color:#15803d;display:inline-flex;align-items:center;gap:5px;">{_ic(_SVG_CHECK_C, 13)} ติ๊กผ่านช่องที่ว่างทั้งหมด</button></div>
    </div>"""
    savebar = f"""<div class="dk-savebar"><div class="msg" id="saveMsg">ผลตรวจทั้งหมดถูกบันทึกแล้ว</div>
        <button type="button" class="dk-btn green" id="saveBtn" disabled style="display:inline-flex;align-items:center;gap:6px;">{_ic(_SVG_SAVE, 16)}<span id="saveBtnLabel">บันทึกผลตรวจ</span></button></div><div class="dk-toast" id="dkToast"></div>"""
    js = INSPECTION_JS.replace("__ROOM__", _json.dumps(room).replace("</", "<\\/")).replace("__DATE__", _json.dumps(date))
    body = (f'<div class="dk-stats">{stats}</div>{tools}<div id="stuList">{rows}</div>'
            f'<div id="emptyHint" style="display:none;">{dk_empty(_ic(_SVG_SEARCH, 38, 1.5), "ไม่พบรายชื่อตามเงื่อนไขที่เลือก")}</div>')
    actions = f'<a href="/inspection?date={date}" class="dk-btn hero">{_ic(_SVG_SCHOOL, 15)} เปลี่ยนห้อง</a>'
    return dk_page(f"ห้อง {_he(room)}", f"ตรวจระเบียบวันที่ {_insp_thai_date(date)} · แตะ “ผ่าน/ไม่ผ่าน” ของแต่ละตัวชี้วัด แล้วกดบันทึก",
                   body, back, actions, savebar + js, icon=_ic(_SVG_CLIPBOARD, 22))


@app.post("/api/inspection/save")
async def api_inspection_save(request: Request, user_session: Optional[str] = Cookie(None)):
    access, err = _insp_gate(user_session, can_manage_inspection, json_mode=True)
    if err: return err
    try:
        data = await request.json()
        room = str(data.get("room", "")).strip()
        date = datetime.strptime(str(data.get("date", "")).strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
        changes = data.get("changes", [])
        if not isinstance(changes, list) or len(changes) > 20000:
            raise ValueError
    except Exception:
        return JSONResponse({"ok": False, "error": "ข้อมูลที่ส่งมาไม่ถูกต้อง"}, status_code=400)
    if not room or not in_inspection_scope(access, room):
        return JSONResponse({"ok": False, "error": "คุณไม่มีสิทธิ์ตรวจห้องนี้"}, status_code=403)
    if date > _insp_today():
        return JSONResponse({"ok": False, "error": "ไม่สามารถบันทึกผลตรวจล่วงหน้าได้"}, status_code=400)

    stu_map = {s['uid']: s for s in get_sorted_master_students() if s['class'] == room}
    crit_map = {c['id']: c for c in get_inspection_criteria(active_only=False)}
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    inspector = access.get("fullname") or access.get("username") or "-"
    saved = cleared = 0
    new_fails = {}
    conn = sqlite3.connect('attendance_pro.db')
    cur = conn.cursor()
    try:
        for ch in changes:
            if not isinstance(ch, list) or len(ch) != 3:
                continue
            uid, cid, v = ch
            if uid not in stu_map or cid not in crit_map or v not in ("pass", "fail", ""):
                continue
            s, c = stu_map[uid], crit_map[cid]
            if v == "":
                cur.execute("DELETE FROM inspection_records WHERE inspect_date=? AND student_uid=? AND criterion_id=?", (date, uid, cid))
                cleared += 1
                continue
            if not c["is_active"]:
                continue  # ตัวชี้วัดที่ปิดอยู่ รับเฉพาะการล้างค่า ไม่รับค่าใหม่
            cur.execute("""INSERT INTO inspection_records
                (inspect_date, classroom, student_uid, student_name, student_no, criterion_id, criterion_name, result, inspector, inspector_label, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(inspect_date, student_uid, criterion_id) DO UPDATE SET
                    result=excluded.result, inspector=excluded.inspector, inspector_label=excluded.inspector_label,
                    created_at=excluded.created_at, criterion_name=excluded.criterion_name, classroom=excluded.classroom""",
                (date, room, uid, s['name'], s['no'], cid, c['name'], v, access.get("username"), inspector, now))
            saved += 1
            if v == "fail":
                new_fails.setdefault(uid, []).append(c['name'])
        conn.commit()
    finally:
        conn.close()

    # 🔔 แจ้งนักเรียนที่ได้รับผล “ไม่ผ่าน” (เฉพาะการตรวจของวันนี้)
    if date == _insp_today():
        for uid, names in list(new_fails.items())[:300]:
            try:
                await push_student_notify("ผลตรวจระเบียบ", "ไม่ผ่าน: " + ", ".join(names) + " — โปรดปรับปรุงให้เรียบร้อย",
                                          tone="warning", target_uids=[uid])
            except Exception:
                pass
    add_log(f"{inspector} บันทึกผลตรวจระเบียบห้อง {room} วันที่ {date} ({saved} รายการ)")
    return JSONResponse({"ok": True, "saved": saved + cleared})


# ──────────────── จัดการตัวชี้วัด ────────────────
@app.get("/inspection/criteria", response_class=HTMLResponse)
async def inspection_criteria_page(user_session: Optional[str] = Cookie(None)):
    access, err = _insp_gate(user_session, can_manage_inspection_criteria)
    if err: return err
    items = get_inspection_criteria(active_only=False)
    conn = sqlite3.connect('attendance_pro.db')
    cur = conn.cursor()
    cur.execute("SELECT criterion_id, COUNT(*) FROM inspection_records GROUP BY criterion_id")
    usage = dict(cur.fetchall())
    conn.close()

    rows = ""
    for i, c in enumerate(items):
        state = '<span class="dk-pill ok">เปิดใช้งาน</span>' if c['is_active'] else '<span class="dk-pill mute">ปิดอยู่</span>'
        toggle_label = "ปิด" if c['is_active'] else "เปิด"
        up = f"""<form method="post" action="/api/inspection/criteria/move" style="margin:0;"><input type="hidden" name="cid" value="{c['id']}">
                 <input type="hidden" name="direction" value="up"><button class="dk-btn light sm" {'disabled style="opacity:.35"' if i == 0 else ''}>↑</button></form>"""
        down = f"""<form method="post" action="/api/inspection/criteria/move" style="margin:0;"><input type="hidden" name="cid" value="{c['id']}">
                 <input type="hidden" name="direction" value="down"><button class="dk-btn light sm" {'disabled style="opacity:.35"' if i == len(items) - 1 else ''}>↓</button></form>"""
        rows += f"""<div class="dk-row">
            <div class="dk-ico-box">{_he(c['icon'])}</div>
            <div class="grow"><b>{_he(c['name'])}</b><span>{state} · ตรวจไปแล้ว {usage.get(c['id'], 0)} ครั้ง</span></div>
            <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;justify-content:flex-end;">
                {up}{down}
                <form method="post" action="/api/inspection/criteria/toggle" style="margin:0;"><input type="hidden" name="cid" value="{c['id']}">
                    <button class="dk-btn light sm">{toggle_label}</button></form>
                <form method="post" action="/api/inspection/criteria/delete" style="margin:0;"
                      onsubmit="return confirm('ลบตัวชี้วัด “{_he(c['name'], quote=True)}” ?\\nประวัติผลตรวจเดิมยังคงอยู่ในรายงาน');">
                    <input type="hidden" name="cid" value="{c['id']}"><button class="dk-btn danger sm">ลบ</button></form>
            </div></div>"""

    active_n = sum(1 for c in items if c['is_active'])
    stats = dk_stat("ตัวชี้วัดทั้งหมด", len(items), _ic(_SVG_CLIPBOARD), "blue") + dk_stat("เปิดใช้งาน", active_n, _ic(_SVG_CHECK_C), "green") + \
        dk_stat("ปิดอยู่", len(items) - active_n, _ic(_SVG_PAUSE), "slate") + dk_stat("ผลตรวจที่บันทึกแล้ว", sum(usage.values()), _ic(_SVG_BARS), "violet")
    add_form = f"""<div class="dk-card"><div class="dk-card-title" style="display:flex;align-items:center;gap:6px;">{_ic(_SVG_PLUS, 16)} เพิ่มตัวชี้วัดใหม่</div>
        <form method="post" action="/api/inspection/criteria/add" style="display:grid;grid-template-columns:70px 1fr auto;gap:10px;align-items:end;">
            <div><label class="dk-label">ไอคอน</label><input class="dk-input" name="icon" maxlength="4" placeholder="✅" style="text-align:center;"></div>
            <div><label class="dk-label">ชื่อตัวชี้วัด</label><input class="dk-input" name="name" maxlength="40" required placeholder="เช่น เล็บ, รองเท้า, ถุงเท้า"></div>
            <button class="dk-btn" type="submit">เพิ่ม</button></form></div>"""
    body = (f'<div class="dk-stats">{stats}</div>{add_form}'
            f'<div class="dk-note" style="display:flex;align-items:flex-start;gap:6px;"><span style="flex-shrink:0;margin-top:1px;">{_ic(_SVG_BULB, 15)}</span><span>ตัวชี้วัดที่ “ปิด” จะไม่แสดงในหน้าตรวจ แต่ประวัติเดิมยังอยู่ · ตัวชี้วัดที่ “ลบ” จะหายจากหน้าตรวจ ส่วนประวัติที่เคยบันทึกไว้ยังคงแสดงในรายงาน</span></div>'
            f'<div class="dk-card-title" style="margin:6px 4px 10px;">รายการตัวชี้วัด</div>{rows or dk_empty(_ic(_SVG_CLIPBOARD, 38, 1.5), "ยังไม่มีตัวชี้วัด")}')
    return dk_page("ตัวชี้วัดการตรวจระเบียบ", "เพิ่ม ลบ เปิด/ปิด และจัดลำดับหัวข้อที่ครูใช้ติ๊กผ่าน/ไม่ผ่าน", body,
                   "/inspection" if can_manage_inspection(access) else _insp_back_url(access), icon=_ic(_SVG_SLIDERS, 22))


def _insp_criteria_mutation(user_session, fn):
    access, err = _insp_gate(user_session, can_manage_inspection_criteria)
    if err: return err
    conn = sqlite3.connect('attendance_pro.db')
    try:
        msg, kind = fn(conn.cursor(), access)
        conn.commit()
    finally:
        conn.close()
    return alert_redirect(msg, type=kind, url="/inspection/criteria")


@app.post("/api/inspection/criteria/add")
async def api_inspection_criteria_add(name: str = Form(""), icon: str = Form(""), user_session: Optional[str] = Cookie(None)):
    name = " ".join(name.split())[:40]
    icon = icon.strip()[:4] or "✅"
    def run(cur, access):
        if not name:
            return "กรุณากรอกชื่อตัวชี้วัด", "error"
        cur.execute("SELECT 1 FROM inspection_criteria WHERE name = ?", (name,))
        if cur.fetchone():
            return f"มีตัวชี้วัด “{name}” อยู่แล้ว", "warning"
        cur.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM inspection_criteria")
        nxt = cur.fetchone()[0]
        cur.execute("INSERT INTO inspection_criteria (name, icon, is_active, sort_order, created_by, created_at) VALUES (?,?,1,?,?,?)",
                    (name, icon, nxt, access.get("fullname") or access.get("username"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        return f"เพิ่มตัวชี้วัด “{name}” เรียบร้อยแล้ว", "success"
    return _insp_criteria_mutation(user_session, run)


@app.post("/api/inspection/criteria/toggle")
async def api_inspection_criteria_toggle(cid: int = Form(...), user_session: Optional[str] = Cookie(None)):
    def run(cur, access):
        cur.execute("SELECT name, is_active FROM inspection_criteria WHERE id = ?", (cid,))
        row = cur.fetchone()
        if not row:
            return "ไม่พบตัวชี้วัดนี้", "error"
        new_state = 0 if row[1] else 1
        cur.execute("UPDATE inspection_criteria SET is_active = ? WHERE id = ?", (new_state, cid))
        return f"{'เปิด' if new_state else 'ปิด'}ใช้งานตัวชี้วัด “{row[0]}” แล้ว", "success"
    return _insp_criteria_mutation(user_session, run)


@app.post("/api/inspection/criteria/delete")
async def api_inspection_criteria_delete(cid: int = Form(...), user_session: Optional[str] = Cookie(None)):
    def run(cur, access):
        cur.execute("SELECT name FROM inspection_criteria WHERE id = ?", (cid,))
        row = cur.fetchone()
        if not row:
            return "ไม่พบตัวชี้วัดนี้ (อาจถูกลบไปแล้ว)", "error"
        cur.execute("DELETE FROM inspection_criteria WHERE id = ?", (cid,))
        return f"ลบตัวชี้วัด “{row[0]}” เรียบร้อยแล้ว", "success"
    return _insp_criteria_mutation(user_session, run)


@app.post("/api/inspection/criteria/move")
async def api_inspection_criteria_move(cid: int = Form(...), direction: str = Form(...), user_session: Optional[str] = Cookie(None)):
    def run(cur, access):
        cur.execute("SELECT id FROM inspection_criteria ORDER BY sort_order, id")
        ids = [r[0] for r in cur.fetchall()]
        if cid not in ids or direction not in ("up", "down"):
            return "ไม่พบตัวชี้วัดนี้", "error"
        i = ids.index(cid)
        j = i - 1 if direction == "up" else i + 1
        if 0 <= j < len(ids):
            ids[i], ids[j] = ids[j], ids[i]
        for pos, _id in enumerate(ids, start=1):
            cur.execute("UPDATE inspection_criteria SET sort_order = ? WHERE id = ?", (pos, _id))
        return "จัดลำดับตัวชี้วัดแล้ว", "success"
    return _insp_criteria_mutation(user_session, run)


# ──────────────── รายงาน ────────────────
def _insp_load_records(access: dict, d_from: str, d_to: str, level: str = "", room: str = "") -> list:
    conn = sqlite3.connect('attendance_pro.db')
    cur = conn.cursor()
    cur.execute("""SELECT inspect_date, classroom, student_uid, student_name, student_no, criterion_id, criterion_name, result, inspector_label
                   FROM inspection_records WHERE inspect_date BETWEEN ? AND ? ORDER BY inspect_date DESC, classroom""", (d_from, d_to))
    out = []
    for r in cur.fetchall():
        cls = r[1] or ""
        if not in_inspection_scope(access, cls):
            continue
        if level and get_grade_level(cls) != level:
            continue
        if room and cls != room:
            continue
        out.append({"date": r[0], "room": cls, "uid": r[2], "name": r[3] or "", "no": r[4] or "", "cid": r[5],
                    "crit": r[6] or "", "result": r[7], "by": r[8] or ""})
    conn.close()
    return out


def _insp_report_range(d_from: Optional[str], d_to: Optional[str]):
    today = datetime.now()
    f = _insp_valid_date(d_from) if d_from else (today - timedelta(days=6)).strftime("%Y-%m-%d")
    t = _insp_valid_date(d_to) if d_to else today.strftime("%Y-%m-%d")
    if f > t:
        f, t = t, f
    return f, t


@app.get("/inspection/report", response_class=HTMLResponse)
async def inspection_report_page(date_from: Optional[str] = None, date_to: Optional[str] = None,
                                 level: Optional[str] = "", room: Optional[str] = "", user_session: Optional[str] = Cookie(None)):
    access, err = _insp_gate(user_session, can_view_inspection_report)
    if err: return err
    d_from, d_to = _insp_report_range(date_from, date_to)
    level, room = (level or "").strip(), (room or "").strip()
    if access["role"] == "level_head":
        level = access["level_scope"]
    recs = _insp_load_records(access, d_from, d_to, level, room)

    visible = _insp_visible_students(access)
    levels = sorted(set(get_grade_level(s['class']) for s in visible), key=_insp_level_key)
    rooms = sorted(set(s['class'] for s in visible if not level or get_grade_level(s['class']) == level))
    lv_opts = '<option value="">ทุกระดับชั้น</option>' + "".join(
        f'<option value="{_he(l, quote=True)}" {"selected" if l == level else ""}>{_he(l)}</option>' for l in levels)
    rm_opts = '<option value="">ทุกห้อง</option>' + "".join(
        f'<option value="{_he(r, quote=True)}" {"selected" if r == room else ""}>{_he(r)}</option>' for r in rooms)
    lv_field = "" if access["role"] == "level_head" else f'<div><label class="dk-label">ระดับชั้น</label><select name="level" class="dk-select">{lv_opts}</select></div>'
    if access["role"] == "level_head":
        lv_field = f'<div><label class="dk-label">ระดับชั้น</label><input class="dk-input" value="{_he(level)}" disabled></div>'
    filter_form = f"""<div class="dk-card"><form method="get" action="/inspection/report" class="dk-filter">
        <div><label class="dk-label">ตั้งแต่วันที่</label><input type="date" name="date_from" value="{d_from}" class="dk-input"></div>
        <div><label class="dk-label">ถึงวันที่</label><input type="date" name="date_to" value="{d_to}" class="dk-input"></div>
        {lv_field}
        <div><label class="dk-label">ห้อง</label><select name="room" class="dk-select">{rm_opts}</select></div>
        <button class="dk-btn" type="submit">แสดงรายงาน</button></form></div>"""

    total = len(recs)
    passed = sum(1 for r in recs if r['result'] == 'pass')
    failed = total - passed
    rate = round(passed * 100 / total) if total else 0
    students_checked = len(set(r['uid'] for r in recs))
    stats = (dk_stat("ผลตรวจทั้งหมด", total, _ic(_SVG_CLIPBOARD), "blue") + dk_stat("อัตราผ่าน", f"{rate}%", _ic(_SVG_MEDAL), "green")
             + dk_stat("ไม่ผ่าน (รายการ)", failed, _ic(_SVG_ALERT), "red") + dk_stat("นักเรียนที่ถูกตรวจ", students_checked, _ic(_SVG_BACKPACK), "violet"))

    # อัตราผ่านรายตัวชี้วัด
    per_c = {}
    for r in recs:
        d = per_c.setdefault(r['cid'], {"name": r['crit'], "p": 0, "f": 0})
        d["p" if r['result'] == 'pass' else "f"] += 1
    crit_html = ""
    for d in sorted(per_c.values(), key=lambda x: x["name"]):
        n = d["p"] + d["f"]
        pct = round(d["p"] * 100 / n) if n else 0
        crit_html += f'<div class="dk-rate-row"><span>{_he(d["name"])}</span><div class="dk-track"><i style="width:{pct}%"></i></div><em>{pct}%</em></div>'
    crit_card = f'<div class="dk-card"><div class="dk-card-title">อัตราผ่านรายตัวชี้วัด<small>ไม่ผ่าน {failed} / {total}</small></div>{crit_html or dk_empty(_ic(_SVG_INBOX, 38, 1.5), "ไม่มีข้อมูลในช่วงนี้")}</div>'

    # แนวโน้มรายวัน (อัตราผ่าน)
    per_day = {}
    for r in recs:
        d = per_day.setdefault(r['date'], [0, 0])
        d[0] += 1 if r['result'] == 'pass' else 0
        d[1] += 1
    days = sorted(per_day)[-31:]
    trend_card = ""
    if days:
        bars = "".join(f'<div title="{_insp_thai_date(d)} · ผ่าน {round(per_day[d][0] * 100 / per_day[d][1])}%" style="height:{max(6, round(per_day[d][0] * 100 / per_day[d][1]))}%"></div>' for d in days)
        trend_card = f'<div class="dk-card"><div class="dk-card-title">แนวโน้มอัตราผ่านรายวัน</div><div class="dk-trend">{bars}</div><div class="dk-trend-lbl"><span>{_insp_thai_date(days[0])}</span><span>{_insp_thai_date(days[-1])}</span></div></div>'

    # สรุปรายห้อง
    per_room = {}
    for r in recs:
        d = per_room.setdefault(r['room'], {"n": 0, "f": 0, "s": set()})
        d["n"] += 1
        d["f"] += 1 if r['result'] == 'fail' else 0
        d["s"].add(r['uid'])
    room_rows = "".join(
        f'<tr><td><b>{_he(k)}</b></td><td>{len(v["s"])}</td><td>{v["n"]}</td><td>{v["f"]}</td>'
        f'<td><span class="dk-pill {"ok" if v["n"] and (v["n"] - v["f"]) * 100 / v["n"] >= 90 else "warn"}">{round((v["n"] - v["f"]) * 100 / v["n"]) if v["n"] else 0}%</span></td></tr>'
        for k, v in sorted(per_room.items()))
    room_card = ""
    if room_rows:
        room_card = f"""<div class="dk-card"><div class="dk-card-title">สรุปรายห้อง</div><div class="dk-tablewrap"><table class="dk-table">
            <thead><tr><th>ห้อง</th><th>ตรวจ (คน)</th><th>ผลตรวจ</th><th>ไม่ผ่าน</th><th>อัตราผ่าน</th></tr></thead><tbody>{room_rows}</tbody></table></div></div>"""

    # นักเรียนที่ไม่ผ่านบ่อย
    per_stu = {}
    for r in recs:
        if r['result'] != 'fail':
            continue
        d = per_stu.setdefault(r['uid'], {"name": r['name'], "room": r['room'], "no": r['no'], "crit": {}, "days": set()})
        d["crit"][r['crit']] = d["crit"].get(r['crit'], 0) + 1
        d["days"].add(r['date'])
    fail_rows = ""
    for d in sorted(per_stu.values(), key=lambda x: (-len(x["days"]), x["room"], x["name"]))[:100]:
        chips = " ".join(f'<span class="dk-pill bad">{_he(k)} ×{v}</span>' for k, v in sorted(d["crit"].items()))
        fail_rows += f'<tr><td><b>{_he(d["name"])}</b><br><span style="font-size:11.5px;color:#64748b;">{_he(d["room"])} · เลขที่ {_he(d["no"])}</span></td><td>{len(d["days"])} วัน</td><td>{chips}</td></tr>'
    fail_card = (f'<div class="dk-card"><div class="dk-card-title">นักเรียนที่ไม่ผ่านระเบียบ<small>{len(per_stu)} คน</small></div><div class="dk-tablewrap"><table class="dk-table">'
                 f'<thead><tr><th>นักเรียน</th><th>วันที่ไม่ผ่าน</th><th>หัวข้อที่ไม่ผ่าน</th></tr></thead><tbody>{fail_rows}</tbody></table></div></div>'
                 if fail_rows else f'<div class="dk-card">{dk_empty(_ic(_SVG_SMILE, 38, 1.5), "ไม่มีนักเรียนที่ไม่ผ่านระเบียบในช่วงนี้")}</div>')

    qs = urllib.parse.urlencode({"date_from": d_from, "date_to": d_to, "level": level, "room": room})
    actions = f'<a href="/inspection/report.csv?{qs}" class="dk-btn hero">{_ic(_SVG_DOWNLOAD, 15)} CSV</a>'
    if can_manage_inspection(access):
        actions += f'<a href="/inspection" class="dk-btn hero">{_ic(_SVG_CLIPBOARD, 15)} ตรวจระเบียบ</a>'
    body = f'<div class="dk-stats">{stats}</div>{filter_form}<div class="dk-grid c2">{crit_card}{trend_card}</div>{room_card}{fail_card}'
    return dk_page("รายงานการตรวจระเบียบ", f"{_insp_thai_date(d_from)} – {_insp_thai_date(d_to)}", body, _insp_back_url(access), actions, icon=_ic(_SVG_BARS, 22))


def _csv_safe(v) -> str:
    s = str(v if v is not None else "")
    return "'" + s if s[:1] in ("=", "+", "-", "@") else s


@app.get("/inspection/report.csv")
async def inspection_report_csv(date_from: Optional[str] = None, date_to: Optional[str] = None,
                                level: Optional[str] = "", room: Optional[str] = "", user_session: Optional[str] = Cookie(None)):
    access, err = _insp_gate(user_session, can_view_inspection_report)
    if err: return err
    d_from, d_to = _insp_report_range(date_from, date_to)
    level = access["level_scope"] if access["role"] == "level_head" else (level or "").strip()
    recs = _insp_load_records(access, d_from, d_to, level, (room or "").strip())
    buf = _io.StringIO()
    w = _csv.writer(buf)
    w.writerow(["วันที่", "ห้อง", "เลขที่", "ชื่อ-สกุล", "ตัวชี้วัด", "ผล", "ผู้ตรวจ"])
    for r in recs:
        w.writerow([_csv_safe(r['date']), _csv_safe(r['room']), _csv_safe(r['no']), _csv_safe(r['name']), _csv_safe(r['crit']),
                    "ผ่าน" if r['result'] == 'pass' else "ไม่ผ่าน", _csv_safe(r['by'])])
    return Response(content=("﻿" + buf.getvalue()).encode("utf-8"), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="inspection_{d_from}_{d_to}.csv"'})


# ──────────────── มุมมองนักเรียน (อ่านอย่างเดียว) ────────────────
@app.get("/student/inspection", response_class=HTMLResponse)
async def student_inspection_page(user_session: Optional[str] = Cookie(None)):
    if not user_session or not user_session.startswith("student_"):
        return RedirectResponse(url="/login", status_code=303)
    uid = urllib.parse.unquote(user_session.replace("student_", "", 1))
    me = next((s for s in get_sorted_master_students() if s['uid'] == uid), None)
    if not me:
        resp = RedirectResponse(url="/login", status_code=303)
        resp.delete_cookie(key="user_session")
        return resp
    since = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    conn = sqlite3.connect('attendance_pro.db')
    cur = conn.cursor()
    cur.execute("""SELECT inspect_date, criterion_name, result, inspector_label FROM inspection_records
                   WHERE student_uid = ? AND inspect_date >= ? ORDER BY inspect_date DESC, criterion_id""", (uid, since))
    recs = cur.fetchall()
    conn.close()
    total = len(recs)
    fails = sum(1 for r in recs if r[2] == 'fail')
    rate = round((total - fails) * 100 / total) if total else 0
    stats = (dk_stat("ตรวจแล้ว (30 วัน)", total, _ic(_SVG_CLIPBOARD), "blue") + dk_stat("อัตราผ่าน", f"{rate}%" if total else "-", _ic(_SVG_MEDAL), "green")
             + dk_stat("ไม่ผ่าน", fails, _ic(_SVG_ALERT), "red") + dk_stat("ห้อง", _he(me['class']), _ic(_SVG_SCHOOL), "violet"))
    by_day = {}
    for d, crit, res, by in recs:
        by_day.setdefault(d, []).append((crit, res, by))
    days_html = ""
    for d, items in by_day.items():
        pills = " ".join(f'<span class="dk-pill {"ok" if res == "pass" else "bad"}">{"✓" if res == "pass" else "✗"} {_he(c or "-")}</span>' for c, res, _ in items)
        who = _he(items[0][2] or "-")
        days_html += f'<div class="dk-row"><div class="grow"><b>{_insp_thai_date(d)}</b><span>ผู้ตรวจ: {who}</span><div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;">{pills}</div></div></div>'
    body = (f'<div class="dk-stats">{stats}</div>'
            + (days_html or f'<div class="dk-card">{dk_empty(_ic(_SVG_INBOX, 38, 1.5), "ยังไม่มีผลตรวจระเบียบใน 30 วันที่ผ่านมา")}</div>'))
    return dk_page("ผลตรวจระเบียบของฉัน", f"{_he(me['name'])} · ย้อนหลัง 30 วัน", body, "/student/dashboard",
                   extra=realtime_notify_script(uid), icon=_ic(_SVG_CLIPBOARD, 22))



THAI_WEEKDAYS = {1: "จันทร์", 2: "อังคาร", 3: "พุธ", 4: "พฤหัสบดี", 5: "ศุกร์", 6: "เสาร์", 7: "อาทิตย์"}

# ==========================================
# 🔌 STUDENT OTP/QR CHECK-IN PAGE
# ==========================================
@app.get("/checkin", response_class=HTMLResponse)
async def student_checkin_page(group_id: Optional[int] = None):
    m_cfg = get_maintenance_status()
    if m_cfg["is_active"] == 1:
        return generate_maintenance_html(m_cfg["mode_type"])
        
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    
    # ดึงรายวิชาที่มี OTP เซสชันที่เปิดใช้งานอยู่
    cursor.execute("""
        SELECT cg.group_id, cg.group_name 
        FROM course_groups cg
        JOIN otp_sessions os ON cg.group_id = os.group_id
        WHERE os.is_active = 1
    """)
    active_groups = cursor.fetchall()
    conn.close()
    
    group_options = ""
    for g in active_groups:
        sel = "selected" if group_id and group_id == g[0] else ""
        group_options += f"<option value='{g[0]}' {sel}>{g[1]}</option>"
        
    no_active_warning = ""
    if not active_groups:
        no_active_warning = """
        <div style="background:rgba(239, 68, 68, 0.15); border:1px solid rgba(239, 68, 68, 0.3); color:#f87171; border-radius:12px; padding:15px; font-size:13.5px; font-weight:700; margin-bottom:15px; text-align:center; line-height:1.6;">
            ⚠️ ในขณะนี้ยังไม่มีคลาสเรียนใดเปิดลงทะเบียนเช็กชื่อด่วนด้วย OTP/QR ในระบบครับ
        </div>
        """
        
    return f"""
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>เช็กชื่อเข้าเรียนด้วย OTP | K-School</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sarabun:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --navy-900: #020617;
            --navy-800: #0f172a;
            --navy-700: #1e293b;
            --navy-600: #2563eb;
            --gold: #d4af37;
            --gold-light: #f2d879;
            --surface: rgba(255, 255, 255, 0.08);
            --border: rgba(255, 255, 255, 0.15);
            --text: #f8fafc;
            --text-soft: #94a3b8;
            --radius: 20px;
        }}
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{
            font-family:'Sarabun', 'Inter', sans-serif;
            background: radial-gradient(circle at top, #0f172a 0%, #020617 100%);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .glass-card {{
            background: rgba(15, 23, 42, 0.65);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 35px 28px;
            width: 100%;
            max-width: 440px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        .glass-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; width: 100%; height: 4px;
            background: linear-gradient(90deg, var(--gold), var(--gold-light), var(--gold));
        }}
        .logo-img {{
            height: 80px;
            width: auto;
            margin-bottom: 18px;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
        }}
        h2 {{
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 6px;
            letter-spacing: 0.5px;
            color: #fff;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        p.subtitle {{
            font-size: 13.5px;
            color: var(--text-soft);
            margin-bottom: 24px;
            font-weight: 500;
        }}
        label {{
            font-size: 12.5px;
            font-weight: 700;
            color: #cbd5e1;
            display: block;
            text-align: left;
            margin-bottom: 6px;
            padding-left: 2px;
        }}
        input, select {{
            width: 100%;
            padding: 12.5px 14px;
            border: 1.5px solid var(--border);
            border-radius: 12px;
            font-family: 'Sarabun', sans-serif;
            font-size: 14.5px;
            background: rgba(15, 23, 42, 0.4);
            color: white;
            margin-bottom: 14px;
            outline: none;
            transition: all 0.2s;
        }}
        input:focus, select:focus {{
            border-color: var(--gold);
            box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.2);
            background: rgba(15, 23, 42, 0.6);
        }}
        input[id="otp"] {{
            text-align: center;
            font-size: 24px;
            font-weight: 800;
            letter-spacing: 6px;
            color: var(--gold-light);
            border: 2px solid rgba(212, 175, 55, 0.3);
            text-shadow: 0 0 8px rgba(242, 216, 121, 0.3);
        }}
        input[id="otp"]::placeholder {{
            font-size: 15px;
            font-weight: 500;
            letter-spacing: 0;
            color: #475569;
            text-shadow: none;
        }}
        .btn-submit {{
            background: linear-gradient(135deg, var(--gold), #b8962e);
            color: #020617;
            width: 100%;
            padding: 14px;
            font-size: 15px;
            font-weight: 800;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            border-bottom: 3px solid #8a6e1e;
            font-family: 'Sarabun', sans-serif;
            letter-spacing: 0.5px;
            transition: all 0.15s;
            margin-top: 10px;
            box-shadow: 0 6px 20px rgba(212, 175, 55, 0.2);
        }}
        .btn-submit:active {{
            transform: translateY(2px);
            border-bottom-width: 1px;
            box-shadow: 0 2px 10px rgba(212, 175, 55, 0.1);
        }}
        .success-box {{
            display: none;
            text-align: center;
            padding: 10px 0;
        }}
        .success-box .success-icon {{
            font-size: 64px;
            margin-bottom: 15px;
            animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }}
        @keyframes popIn {{
            from {{ transform: scale(0.5); opacity: 0; }}
            to {{ transform: scale(1); opacity: 1; }}
        }}
        .success-box h3 {{
            color: #10b981;
            font-size: 20px;
            font-weight: 800;
            margin-bottom: 8px;
        }}
        .success-box p {{
            font-size: 14px;
            color: var(--text-soft);
            line-height: 1.6;
        }}
        /* 🔔 Toast แจ้งเตือนแบบไม่บล็อกหน้าจอ (แทน alert() ของเบราว์เซอร์) */
        .pg-toast-wrap {{ position: fixed; top: 0; left: 0; right: 0; z-index: 9999; display: flex; flex-direction: column; align-items: center; padding-top: max(env(safe-area-inset-top, 0px), 14px); pointer-events: none; }}
        .pg-toast {{
            pointer-events: auto;
            display: flex; align-items: center; gap: 10px;
            background: rgba(15, 23, 42, 0.92);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border);
            border-left: 4px solid var(--gold);
            border-radius: 14px;
            padding: 13px 16px;
            max-width: 90vw;
            width: 360px;
            box-shadow: 0 12px 30px -8px rgba(0,0,0,0.5);
            color: #fff; font-size: 13.5px; font-weight: 600;
            transform: translateY(-120%);
            transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1);
            margin-bottom: 8px;
        }}
        .pg-toast.show {{ transform: translateY(0); }}
        .pg-toast.pg-error {{ border-left-color: #ef4444; }}
        .pg-toast.pg-warning {{ border-left-color: #f59e0b; }}
        .pg-toast .pg-toast-icon {{ font-size: 18px; flex-shrink: 0; }}
    </style>
</head>
<body>
    {PAGE_LOADER}
    <div class="pg-toast-wrap" id="pgToastWrap"></div>

<div class="glass-card">
    <div id="form-area">
        <img src="{LOGO_URL}" class="logo-img">
        <h2>ลงทะเบียนเข้าเรียนด้วย OTP</h2>
        <p class="subtitle">เช็กชื่อเข้าเรียนด้วยตนเองผ่านมือถือ</p>
        
        {no_active_warning}
        
        <div id="inputs-group" style="{ 'display:none;' if not active_groups else '' }">
            <label>เลือกกลุ่มวิชา</label>
            <select id="group_id" required>
                {group_options}
            </select>
            
            <label>ชื่อ-นามสกุลนักเรียน</label>
            <input type="text" id="student_name" placeholder="กรอกชื่อ-นามสกุลจริงของคุณ" autocomplete="off" required>
            
            <label>เลขที่</label>
            <input type="text" id="student_no" placeholder="ตัวอย่าง: 15" autocomplete="off" required>
            
            <label>ระดับชั้นเรียน</label>
            <input type="text" id="classroom" placeholder="ตัวอย่าง: ม.5/2" autocomplete="off" required>
            
            <label>รหัส OTP 4 หลัก</label>
            <input type="text" id="otp" placeholder="กรอกรหัสจากครูผู้สอน" maxlength="4" autocomplete="off" required>
            
            <button class="btn-submit" onclick="submitCheckin()">⚡ ยืนยันข้อมูลเช็กชื่อ</button>
        </div>
    </div>
    
    <div class="success-box" id="success-box">
        <div class="success-icon">🎉</div>
        <h3>เช็กชื่อสำเร็จแล้ว!</h3>
        <p id="success-message">ระบบได้ลงบันทึกเวลาเรียนและส่งสัญญาณแจ้งเตือนไปยังครูผู้สอนเรียบร้อยแล้ว ขอให้มีความสุขกับการเรียนวันนี้</p>
    </div>
</div>

<script>
function pageToast(message, type) {{
    type = type || 'info';
    const icons = {{ success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' }};
    const wrap = document.getElementById('pgToastWrap');
    const el = document.createElement('div');
    el.className = 'pg-toast pg-' + type;
    el.innerHTML = '<span class="pg-toast-icon">' + (icons[type] || 'ℹ️') + '</span><span>' + message + '</span>';
    wrap.appendChild(el);
    requestAnimationFrame(() => el.classList.add('show'));
    setTimeout(() => {{
        el.classList.remove('show');
        setTimeout(() => el.remove(), 300);
    }}, 3200);
}}

async function submitCheckin() {{
    const name = document.getElementById('student_name').value.trim();
    const no = document.getElementById('student_no').value.trim();
    const cls = document.getElementById('classroom').value.trim();
    const otp = document.getElementById('otp').value.trim();
    const gid = document.getElementById('group_id').value;
    
    if (!name || !no || !cls || !otp || !gid) {{
        pageToast('กรุณากรอกข้อมูลให้ครบถ้วนทุกช่องครับ', 'warning');
        return;
    }}
    
    const btn = document.querySelector('.btn-submit');
    btn.disabled = true;
    btn.textContent = '⏱️ กำลังบันทึกข้อมูล...';
    
    try {{
        const res = await fetch('/api/student/checkin', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                student_name: name,
                student_no: no,
                classroom: cls,
                otp: otp,
                group_id: parseInt(gid)
            }})
        }});
        
        const data = await res.json();
        if (res.ok && data.ok) {{
            document.getElementById('form-area').style.display = 'none';
            document.getElementById('success-message').innerHTML = `<b>นักเรียน:</b> ${{name}} เลขที่ ${{no}} ห้อง ${{cls}}<br>ได้ทำการลงทะเบียนเข้าเรียนสำเร็จเรียบร้อยแล้ว!`;
            document.getElementById('success-box').style.display = 'block';
        }} else {{
            pageToast('เช็กชื่อไม่สำเร็จ: ' + (data.error || 'เกิดข้อผิดพลาดไม่ทราบสาเหตุ'), 'error');
            btn.disabled = false;
            btn.textContent = '⚡ ยืนยันข้อมูลเช็กชื่อ';
        }}
    }} catch(e) {{
        pageToast('การเชื่อมต่อล้มเหลว กรุณาลองใหม่อีกครั้ง', 'error');
        btn.disabled = false;
        btn.textContent = '⚡ ยืนยันข้อมูลเช็กชื่อ';
    }}
}}
</script>

</body>
</html>
    """

# ==========================================
# 🏖️ LEAVE REQUEST — นักเรียนยื่นคำร้องลา
# ==========================================
@app.get("/leave", response_class=HTMLResponse)
async def leave_request_page():
    m_cfg = get_maintenance_status()
    if m_cfg["is_active"] == 1:
        return HTMLResponse(generate_maintenance_html(m_cfg["mode_type"]))
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    # เลือกเฉพาะวิชาที่มีการมอบหมายนักเรียนไว้ (วิชาที่กำหนดไว้)
    cursor.execute("""
        SELECT DISTINCT cg.group_id, cg.group_name 
        FROM course_groups cg
        JOIN group_assignments ga ON cg.group_id = ga.group_id
        ORDER BY cg.group_name
    """)
    groups = cursor.fetchall()
    conn.close()
    group_options = "".join([f"<option value='{g[0]}'>{g[1]}</option>" for g in groups])
    return f"""
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ยื่นคำร้องลา | K-School</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sarabun:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:'Sarabun',sans-serif; background:#f1f5f9; color:#1e293b; min-height:100vh; }}
        .topbar {{ background:linear-gradient(135deg,#1e3a8a,#0f172a); color:white; padding:16px 20px; border-bottom:3px solid #d4af37; display:flex; align-items:center; gap:12px; }}
        .topbar h1 {{ font-size:17px; font-weight:700; }}
        .container {{ max-width:520px; margin:0 auto; padding:20px 16px; }}
        .card {{ background:white; border-radius:14px; padding:24px; box-shadow:0 2px 8px rgba(0,0,0,0.06); border:1px solid #e2e8f0; margin-bottom:20px; }}
        .card h2 {{ font-size:15px; font-weight:700; color:#0f172a; margin-bottom:18px; padding-bottom:10px; border-bottom:2px solid #e2e8f0; display:flex; align-items:center; gap:8px; }}
        label {{ font-size:13px; font-weight:700; color:#475569; display:block; margin-bottom:5px; }}
        input, select, textarea {{ width:100%; padding:12px; border:1px solid #cbd5e1; border-radius:8px; font-family:'Sarabun',sans-serif; font-size:14px; color:#0f172a; background:white; margin-bottom:14px; box-sizing:border-box; }}
        textarea {{ resize:vertical; min-height:90px; }}
        .btn-submit {{ background:linear-gradient(135deg,#1e3a8a,#0f172a); color:white; width:100%; padding:14px; font-size:15px; font-weight:700; border:none; border-radius:10px; cursor:pointer; border-bottom:3px solid #0f172a; }}
        .btn-submit:active {{ transform:translateY(2px); border-bottom-width:1px; }}
        .info-box {{ background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:14px; margin-bottom:18px; font-size:13px; color:#1e40af; line-height:1.6; }}
        .success-box {{ display:none; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:12px; padding:24px; text-align:center; }}
        .success-box .icon {{ font-size:48px; margin-bottom:10px; }}
        .success-box h3 {{ color:#166534; font-size:18px; margin-bottom:6px; }}
        .success-box p {{ color:#15803d; font-size:13.5px; }}
        .pg-toast-wrap {{ position:fixed; top:0; left:0; right:0; z-index:9999; display:flex; flex-direction:column; align-items:center; padding-top:max(env(safe-area-inset-top,0px),14px); pointer-events:none; }}
        .pg-toast {{ pointer-events:auto; display:flex; align-items:center; gap:10px; background:rgba(15,23,42,0.94); border-left:4px solid #d4af37; border-radius:12px; padding:13px 16px; max-width:90vw; width:360px; box-shadow:0 12px 30px -8px rgba(0,0,0,0.4); color:#fff; font-size:13.5px; font-weight:600; transform:translateY(-120%); transition:transform .3s cubic-bezier(.34,1.56,.64,1); margin-bottom:8px; }}
        .pg-toast.show {{ transform:translateY(0); }}
        .pg-toast.pg-error {{ border-left-color:#ef4444; }}
        .pg-toast.pg-warning {{ border-left-color:#f59e0b; }}
    </style>
</head>
<body>
<div class="pg-toast-wrap" id="pgToastWrap"></div>
<div class="topbar">
    <a href="/login" style="color:#d4af37; font-size:20px; text-decoration:none;">←</a>
    <h1>📋 ยื่นคำร้องขอลา</h1>
</div>
<div class="container">
    <div class="info-box">
        📌 กรอกคำร้องลาล่วงหน้า แอดมินจะตรวจสอบและอนุมัติ<br>
        เมื่ออนุมัติแล้ว ระบบจะบันทึกสถานะ <b>"ลา"</b> ให้อัตโนมัติในวันที่ระบุ
    </div>
    <div class="card">
        <h2>📝 แบบฟอร์มคำร้องลา</h2>
        <div id="form-area">
            <label>ชื่อ-นามสกุล</label>
            <input type="text" id="student_name" placeholder="กรอกชื่อ-นามสกุลของคุณ" required>
            <label>เลขที่</label>
            <input type="text" id="student_no" placeholder="เช่น 12" required>
            <label>ชั้น/ห้อง</label>
            <input type="text" id="classroom" placeholder="เช่น ม.5/2" required>
            <label>วิชา / กลุ่มเรียน</label>
            <select id="group_id">
                {group_options}
            </select>
            <label>วันที่ต้องการลา</label>
            <input type="date" id="leave_date" required>
            <label>ประเภทการลา</label>
            <select id="leave_type">
                <option value="ลาป่วย">🤒 ลาป่วย</option>
                <option value="ลากิจ">📌 ลากิจ</option>
                <option value="อื่นๆ">📝 อื่นๆ</option>
            </select>
            <label>เหตุผลการลา</label>
            <textarea id="reason" placeholder="อธิบายเหตุผลการลาของคุณ..."></textarea>
            <button class="btn-submit" onclick="submitLeave()">📤 ยื่นคำร้องลา</button>
        </div>
        <div class="success-box" id="success-box">
            <div class="icon">✅</div>
            <h3>ยื่นคำร้องดำเนินการเสร็จสิ้น!</h3>
            <p>แอดมินจะตรวจสอบและอนุมัติคำร้องของคุณ<br>เมื่ออนุมัติแล้วระบบจะบันทึกสถานะ "ลา" ให้อัตโนมัติ</p>
        </div>
    </div>
</div>
<script>
function pageToast(message, type) {{
    type = type || 'info';
    const icons = {{ success:'✅', error:'❌', warning:'⚠️', info:'ℹ️' }};
    const wrap = document.getElementById('pgToastWrap');
    const el = document.createElement('div');
    el.className = 'pg-toast pg-' + type;
    el.innerHTML = '<span>' + (icons[type] || 'ℹ️') + '</span><span>' + message + '</span>';
    wrap.appendChild(el);
    requestAnimationFrame(() => el.classList.add('show'));
    setTimeout(() => {{ el.classList.remove('show'); setTimeout(() => el.remove(), 300); }}, 3200);
}}
async function submitLeave() {{
    const name = document.getElementById('student_name').value.trim();
    const no = document.getElementById('student_no').value.trim();
    const cls = document.getElementById('classroom').value.trim();
    const gid = document.getElementById('group_id').value;
    const date = document.getElementById('leave_date').value;
    const leaveType = document.getElementById('leave_type').value;
    const reason = document.getElementById('reason').value.trim();
    if (!name || !no || !cls || !date) {{ pageToast('กรุณากรอกข้อมูลให้ครบทุกช่อง', 'warning'); return; }}
    const res = await fetch('/api/leave/submit', {{
        method:'POST',
        headers:{{'Content-Type':'application/json'}},
        body: JSON.stringify({{student_name:name, student_no:no, classroom:cls, group_id:parseInt(gid), leave_date:date, leave_type:leaveType, reason:reason}})
    }});
    const data = await res.json();
    if (data.ok) {{
        document.getElementById('form-area').style.display = 'none';
        document.getElementById('success-box').style.display = 'block';
    }} else {{ pageToast('เกิดข้อผิดพลาด: ' + data.error, 'error'); }}
}}
</script>
</body>
</html>
"""

@app.post("/api/leave/submit")
async def api_leave_submit(request: Request):
    m_cfg = get_maintenance_status()
    if m_cfg["is_active"] == 1:
        return JSONResponse({"ok": False, "error": "ระบบปิดอยู่"})
    data = await request.json()
    student_name = data.get("student_name", "").strip()
    student_no = data.get("student_no", "").strip()
    classroom = data.get("classroom", "").strip()
    group_id = int(data.get("group_id", 0))
    leave_date = data.get("leave_date", "")
    leave_type = data.get("leave_type", "อื่นๆ").strip() or "อื่นๆ"
    if leave_type not in ("ลาป่วย", "ลากิจ", "อื่นๆ"):
        leave_type = "อื่นๆ"
    reason = data.get("reason", "").strip()
    if not all([student_name, student_no, classroom, leave_date]):
        return JSONResponse({"ok": False, "error": "ข้อมูลไม่ครบ"})
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT group_name FROM course_groups WHERE group_id=?", (group_id,))
    g = cursor.fetchone()
    group_name = g[0] if g else ""
    submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""INSERT INTO leave_requests
        (student_name, student_no, classroom, group_id, group_name, leave_date, leave_type, reason, status, submitted_at)
        VALUES (?,?,?,?,?,?,?,?,'pending',?)""",
        (student_name, student_no, classroom, group_id, group_name, leave_date, leave_type, reason, submitted_at))
    conn.commit()
    conn.close()
    return JSONResponse({"ok": True})

LEAVE_TYPE_BADGE = {
    "ลาป่วย": '<span style="background:#fef2f2;color:#b91c1c;border:1px solid #fecaca;padding:2px 8px;border-radius:20px;font-size:11px;font-weight:700;">🤒 ลาป่วย</span>',
    "ลากิจ":  '<span style="background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;padding:2px 8px;border-radius:20px;font-size:11px;font-weight:700;">📌 ลากิจ</span>',
    "อื่นๆ":  '<span style="background:#f8fafc;color:#475569;border:1px solid #e2e8f0;padding:2px 8px;border-radius:20px;font-size:11px;font-weight:700;">📝 อื่นๆ</span>',
}

@app.get("/admin/leave_requests", response_class=HTMLResponse)
async def admin_leave_requests(leave_type: Optional[str] = None, user_session: Optional[str] = Cookie(None)):
    access, redirect = require_discipline_access(user_session)
    if redirect: return redirect
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT req_id, student_name, student_no, classroom, group_name,
        leave_date, reason, status, submitted_at, leave_type FROM leave_requests ORDER BY submitted_at DESC""")
    rows = cursor.fetchall()
    conn.close()
    # 🎓 หัวหน้าระดับเห็นเฉพาะคำร้องของนักเรียนในระดับชั้นที่รับผิดชอบ
    if access["role"] == "level_head":
        rows = [r for r in rows if in_discipline_scope(access, r[3])]
    # 🩺 ตัวกรองตามประเภทการลา
    if leave_type in ("ลาป่วย", "ลากิจ", "อื่นๆ"):
        rows = [r for r in rows if (r[9] or "อื่นๆ") == leave_type]

    filter_tabs = ""
    for lbl, val in [("ทั้งหมด", ""), ("🤒 ลาป่วย", "ลาป่วย"), ("📌 ลากิจ", "ลากิจ"), ("📝 อื่นๆ", "อื่นๆ")]:
        active = "background:#1e3a8a;color:white;" if (leave_type or "") == val else "background:#f1f5f9;color:#475569;"
        filter_tabs += f'<a href="/admin/leave_requests{"?leave_type="+val if val else ""}" style="{active}padding:6px 14px;border-radius:20px;font-size:12.5px;font-weight:700;text-decoration:none;">{lbl}</a>'

    status_badge = {
        "pending":  '<span style="background:#fef9c3;color:#854d0e;border:1px solid #fde047;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:700;">⏳ รออนุมัติ</span>',
        "approved": '<span style="background:#f0fdf4;color:#166534;border:1px solid #86efac;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:700;">✅ อนุมัติแล้ว</span>',
        "rejected": '<span style="background:#fff1f2;color:#9f1239;border:1px solid #fecdd3;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:700;">❌ ปฏิเสธ</span>',
    }

    table_rows = ""
    for r in rows:
        req_id, name, no, cls, grp, date, reason, status, submitted, ltype = r
        badge = status_badge.get(status, status)
        type_badge = LEAVE_TYPE_BADGE.get(ltype or "อื่นๆ", LEAVE_TYPE_BADGE["อื่นๆ"])
        actions = ""
        if status == "pending":
            actions = f"""
            <div style="display:flex;gap:6px;justify-content:center;">
                <a href="/api/admin/leave/approve?req_id={req_id}" class="btn"
                   style="background:#10b981;color:white;padding:5px 10px;border-radius:6px;font-size:12px;font-weight:700;"
                   onclick="return confirm('อนุมัติคำร้องลาของ {name} วันที่ {date}?')">✅ อนุมัติ</a>
                <a href="/api/admin/leave/reject?req_id={req_id}" class="btn"
                   style="background:#ef4444;color:white;padding:5px 10px;border-radius:6px;font-size:12px;font-weight:700;"
                   onclick="return confirm('ปฏิเสธคำร้องนี้?')">❌ ปฏิเสธ</a>
            </div>"""
        else:
            actions = f'<span style="color:#94a3b8;font-size:12px;">ดำเนินการแล้ว</span>'

        table_rows += f"""<tr>
            <td style="text-align:left;font-weight:600;">{name}<br><span style="color:#94a3b8;font-size:12px;">เลขที่ {no} · {cls}</span></td>
            <td>{grp}<br><span style="color:#3b82f6;font-size:12.5px;font-weight:700;">{date}</span></td>
            <td>{type_badge}</td>
            <td style="text-align:left;font-size:12.5px;color:#475569;max-width:140px;">{reason or '-'}</td>
            <td>{badge}</td>
            <td>{actions}</td>
        </tr>"""

    pending_count = sum(1 for r in rows if r[7] == "pending")
    back_url = "/admin/dashboard" if access["role"] == "admin" else f"/app/dashboard?user={urllib.parse.quote(access['username'])}"
    scope_note = ""
    if access["role"] == "level_head":
        scope_note = f'<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:10px 16px;margin-bottom:12px;font-size:12.5px;color:#1e40af;">🎓 คุณกำลังดูเฉพาะคำร้องของนักเรียนระดับชั้น <b>{access["level_scope"] or "(ยังไม่ระบุระดับ)"}</b></div>'
    return f"""
    <html>{STYLE_HEADER}
    <body>
    <div class="navbar">
        <h1>📋 คำร้องขอลา</h1>
        <a href="{back_url}" class="btn btn-secondary">← กลับ</a>
    </div>
    <div class="main-container" style="max-width:860px;">
        {scope_note}
        {"" if not pending_count else f'<div style="background:#fef9c3;border:1px solid #fde047;border-radius:10px;padding:12px 16px;margin-bottom:16px;font-weight:700;color:#854d0e;font-size:14px;">⏳ มีคำร้องรออนุมัติ {pending_count} รายการ</div>'}
        <div class="card">
            <h2>📋 รายการคำร้องลาทั้งหมด</h2>
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px;">{filter_tabs}</div>
            <div style="overflow-x:auto;border-radius:8px;border:1px solid #e2e8f0;">
                <table>
                    <thead><tr>
                        <th style="text-align:left;">นักเรียน</th>
                        <th>วิชา / วันที่ลา</th>
                        <th>ประเภท</th>
                        <th>เหตุผล</th>
                        <th>สถานะ</th>
                        <th>การดำเนินการ</th>
                    </tr></thead>
                    <tbody>{table_rows if table_rows else "<tr><td colspan='6' style='color:#94a3b8;'>ยังไม่มีคำร้อง</td></tr>"}</tbody>
                </table>
            </div>
        </div>
        <div style="text-align:center;color:#94a3b8;font-size:12px;margin-top:12px;">KK STUDIO GROUP · K-School Leave System</div>
    </div>
    </body></html>
    """

@app.get("/api/admin/leave/approve")
async def api_leave_approve(req_id: int, user_session: Optional[str] = Cookie(None)):
    access, redirect = require_discipline_access(user_session)
    if redirect: return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT student_name, student_no, classroom, group_name, leave_date, reason, leave_type FROM leave_requests WHERE req_id=?", (req_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return alert_redirect("ไม่พบคำร้องนี้ในระบบ", type="error")
    name, no, cls, grp, date, reason, ltype = row
    ltype = ltype or "อื่นๆ"
    if not in_discipline_scope(access, cls):
        conn.close()
        return alert_redirect("คุณไม่มีสิทธิ์อนุมัติคำร้องของนักเรียนนอกระดับชั้นที่รับผิดชอบ", type="error", url="/admin/leave_requests")
    reviewed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE leave_requests SET status='approved', reviewed_at=? WHERE req_id=?", (reviewed_at, req_id))
    
    # แปลงวันที่จาก YYYY-MM-DD เป็น DD/MM/YYYY สำหรับตาราง logs
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d/%m/%Y")
    except: formatted_date = date

    # ตรวจว่ายังไม่มีบันทึกวันนี้ก่อนแล้วค่อยเพิ่ม
    cursor.execute("""SELECT log_id FROM attendance_logs
        WHERE student_name=? AND group_name=? AND date=?""", (name, grp, formatted_date))
    existing = cursor.fetchone()
    
    checker_tag = f"ระบบ ({ltype}: {reason})" if reason else f"ระบบ (อนุมัติใบลา - {ltype})"
    
    if not existing:
        cursor.execute("""INSERT INTO attendance_logs
            (group_name, student_name, student_no, classroom, status, date, checked_by, log_time)
            VALUES (?,?,?,?,?,?,?,?)""",
            (grp, name, no, cls, "ลา", formatted_date, checker_tag, datetime.now().strftime("%H:%M:%S")))
    else:
        cursor.execute("""UPDATE attendance_logs SET status='ลา', checked_by=?
            WHERE log_id=?""", (checker_tag, existing[0]))
    conn.commit()
    conn.close()

    # 🔴 แจ้งเตือนแบบเรียลไทม์ให้นักเรียนคนที่ยื่นคำร้องทราบทันทีว่าใบลาได้รับอนุมัติแล้ว
    leave_uid = find_student_uid(name, no, cls)
    if leave_uid:
        await push_student_notify(
            title="✅ ใบลาของคุณได้รับการอนุมัติแล้ว",
            message=f"{grp} · วันที่ {formatted_date} ({ltype}: {reason})" if reason else f"{grp} · วันที่ {formatted_date}",
            tone="success",
            target_uids=[leave_uid],
        )

    return alert_redirect('อนุมัติคำร้องเรียบร้อยแล้ว ระบบบันทึกสถานะ "ลา" ให้แล้ว', type="success", url="/admin/leave_requests")

@app.get("/api/admin/leave/reject")
async def api_leave_reject(req_id: int, user_session: Optional[str] = Cookie(None)):
    access, redirect = require_discipline_access(user_session)
    if redirect: return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT student_name, student_no, classroom, group_name FROM leave_requests WHERE req_id=?", (req_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return alert_redirect("ไม่พบคำร้องนี้ในระบบ", type="error")
    name, no, cls, grp = row
    if not in_discipline_scope(access, cls):
        conn.close()
        return alert_redirect("คุณไม่มีสิทธิ์ดำเนินการคำร้องของนักเรียนนอกระดับชั้นที่รับผิดชอบ", type="error", url="/admin/leave_requests")
    reviewed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE leave_requests SET status='rejected', reviewed_at=? WHERE req_id=?", (reviewed_at, req_id))
    conn.commit()
    conn.close()

    # 🔴 แจ้งเตือนแบบเรียลไทม์ให้นักเรียนทราบทันทีว่าใบลาไม่ได้รับอนุมัติ
    leave_uid = find_student_uid(name, no, cls)
    if leave_uid:
        await push_student_notify(
            title="❌ ใบลาของคุณไม่ได้รับการอนุมัติ",
            message=f"{grp} — กรุณาติดต่อครูผู้สอนหรือฝ่ายกิจการนักเรียนเพื่อสอบถามรายละเอียด",
            tone="danger",
            target_uids=[leave_uid],
        )

    return alert_redirect("ปฏิเสธคำร้องเรียบร้อยแล้ว", type="success", url="/admin/leave_requests")

# ==========================================
# 🔐 ADMIN — จัดการสิทธิ์ผู้ใช้แบบ Role-based (ปรับได้จากหน้าเว็บ ไม่ต้องแก้โค้ด)
# ==========================================
ROLE_LABEL_TH = {"teacher": "👩‍🏫 ครูผู้สอน", "level_head": "🎓 หัวหน้าระดับ", "affairs": "🛡️ ฝ่ายกิจการนักเรียน"}

@app.get("/admin/permissions", response_class=HTMLResponse)
async def admin_permissions_page(user_session: Optional[str] = Cookie(None)):
    if user_session != "admin":
        return RedirectResponse(url="/login", status_code=303)
    matrix = get_permission_matrix()

    rows_html = ""
    for perm_key, meta in PERMISSIONS.items():
        cells = ""
        for role in CONFIGURABLE_ROLES:
            checked = "checked" if matrix[role][perm_key] else ""
            cells += f'<td style="text-align:center;"><input type="checkbox" name="{role}__{perm_key}" {checked} style="width:20px;height:20px;cursor:pointer;"></td>'
        rows_html += f'<tr><td style="text-align:left;font-weight:600;font-size:13px;">{meta["label"]}</td>{cells}</tr>'

    role_headers = "".join([f'<th>{ROLE_LABEL_TH[r]}</th>' for r in CONFIGURABLE_ROLES])

    return f"""
    <html>{STYLE_HEADER}
    <body>
    <div class="navbar">
        <h1>🔐 จัดการสิทธิ์ผู้ใช้ (Role-based)</h1>
        <a href="/admin/dashboard" class="btn btn-secondary">← กลับ</a>
    </div>
    <div class="main-container" style="max-width:820px;">
        <div class="card">
            <h2>🧩 ตารางสิทธิ์การเข้าถึง</h2>
            <p style="font-size:12.5px;color:#64748b;margin-bottom:16px;line-height:1.6;">
                ✅ ติ๊กเพื่อ "เปิด" สิทธิ์ให้บทบาทนั้นเข้าถึงเมนู/ฟีเจอร์ที่ระบุ · 👑 ผู้ดูแลระบบ (Admin) มีสิทธิ์ทุกอย่างเสมอ ไม่ต้องตั้งค่า
            </p>
            <form method="post" action="/api/admin/permissions/update">
                <div style="overflow-x:auto;border-radius:8px;border:1px solid #e2e8f0;">
                    <table>
                        <thead><tr><th style="text-align:left;">สิทธิ์การใช้งาน</th>{role_headers}</tr></thead>
                        <tbody>{rows_html}</tbody>
                    </table>
                </div>
                <button type="submit" class="btn-submit" style="margin-top:18px;">💾 บันทึกการตั้งค่าสิทธิ์</button>
            </form>
        </div>
        <div style="text-align:center;color:#94a3b8;font-size:12px;margin-top:12px;">KK STUDIO GROUP · K-School RBAC</div>
    </div>
    </body></html>
    """

@app.post("/api/admin/permissions/update")
async def api_update_permissions(request: Request, user_session: Optional[str] = Cookie(None)):
    if user_session != "admin":
        return HTMLResponse("Unauthorized", status_code=401)
    form = await request.form()
    checked_keys = set(form.keys())
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    for role in CONFIGURABLE_ROLES:
        for perm_key in PERMISSIONS:
            allowed = 1 if f"{role}__{perm_key}" in checked_keys else 0
            cursor.execute(
                "INSERT INTO role_permissions (role, perm_key, allowed) VALUES (?,?,?) "
                "ON CONFLICT(role, perm_key) DO UPDATE SET allowed=excluded.allowed",
                (role, perm_key, allowed)
            )
    conn.commit()
    conn.close()
    add_log("แอดมินปรับปรุงตารางสิทธิ์ผู้ใช้ (Role-based Permissions)")
    return alert_redirect("บันทึกการตั้งค่าสิทธิ์เรียบร้อยแล้ว", type="success", url="/admin/permissions")


def require_analytics_access(user_session: Optional[str]):
    """ใช้ต้นทางฟังก์ชัน route: คืน (access, redirect_or_None) — ใช้เช็คสิทธิ์เข้าหน้าแดชบอร์ดสถิติ"""
    access = get_access(user_session)
    if not access["authenticated"] or not can_view_analytics(access):
        return access, RedirectResponse(url="/login", status_code=303)
    return access, None


def _analytics_classroom_ok(access: dict, classroom: str) -> bool:
    """กรองข้อมูลตามขอบเขตระดับชั้นของหัวหน้าระดับ (level_head เห็นเฉพาะระดับตน)"""
    if access.get("role") == "level_head" and access.get("level_scope"):
        return get_grade_level(classroom or "") == access["level_scope"]
    return True


# ==========================================
# 📈 ADVANCED ANALYTICS DASHBOARD — สถิติ/กราฟภาพรวมระบบ
# ==========================================
@app.get("/admin/analytics", response_class=HTMLResponse)
async def admin_analytics_page(user_session: Optional[str] = Cookie(None)):
    access, redirect = require_analytics_access(user_session)
    if redirect: return redirect
    back_url = "/admin/dashboard" if access["role"] == "admin" else f"/app/dashboard?user={urllib.parse.quote(access['username'])}"
    scope_note = ""
    if access["role"] == "level_head":
        scope_note = f'<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:10px 16px;margin-bottom:16px;font-size:12.5px;color:#1e40af;">🎓 สถิติที่แสดงเฉพาะระดับชั้น <b>{access["level_scope"] or "(ยังไม่ระบุระดับ)"}</b></div>'

    # 🧮 คำนวณ KPI ภาพรวม
    summary = get_conduct_summary()
    if access.get("role") == "level_head" and access.get("level_scope"):
        summary = [s for s in summary if get_grade_level(s.get("class", "")) == access["level_scope"]]
    total_students = len(summary)
    avg_score = round(sum(s["score"] for s in summary) / total_students, 1) if total_students else 0
    at_risk = [s for s in summary if s["score"] < 70]
    top5 = sorted(summary, key=lambda s: s["score"], reverse=True)[:5]
    bottom5 = sorted(summary, key=lambda s: s["score"])[:5]

    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    today_val = datetime.now().strftime("%d/%m/%Y")
    cursor.execute("SELECT status, classroom FROM attendance_logs WHERE date=?", (today_val,))
    today_logs = [r for r in cursor.fetchall() if _analytics_classroom_ok(access, r[1])]
    present_today = sum(1 for s, _ in today_logs if s in ("มา", "สาย"))
    total_today = len(today_logs)
    attendance_rate_today = round(present_today / total_today * 100, 1) if total_today else None
    cursor.execute("SELECT COUNT(*) FROM leave_requests WHERE status='pending'")
    pending_leave = cursor.fetchone()[0]
    conn.close()

    def leaderboard_row(s, rank, is_top):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
        color = "#15803d" if is_top else "#b91c1c"
        return f"""<div style="display:flex;align-items:center;gap:10px;padding:9px 4px;border-bottom:1px solid var(--border);">
            <span style="font-weight:800;width:26px;text-align:center;">{medal}</span>
            <div style="flex:1;min-width:0;">
                <div style="font-size:13px;font-weight:700;color:#1e293b;">{s['name']}</div>
                <div style="font-size:11px;color:#94a3b8;">{s['class']} · เลขที่ {s['no']}</div>
            </div>
            <div style="font-weight:800;color:{color};font-size:15px;">{s['score']}</div>
        </div>"""

    top5_html = "".join(leaderboard_row(s, i + 1, True) for i, s in enumerate(top5)) or "<p style='color:#94a3b8;text-align:center;padding:16px;font-size:12.5px;'>ยังไม่มีข้อมูล</p>"
    bottom5_html = "".join(leaderboard_row(s, i + 1, False) for i, s in enumerate(bottom5)) or "<p style='color:#94a3b8;text-align:center;padding:16px;font-size:12.5px;'>ยังไม่มีข้อมูล</p>"

    # 🗺️ แผนที่ uid -> ชื่อ/ห้อง ฝังไว้ให้ฝั่ง client ใช้แปะชื่อในฟีดสด (ไม่ต้องยิง API ซ้ำ)
    import json as _json
    uid_map = {s["uid"]: f"{s['name']} ({s['class']})" for s in get_sorted_master_students()}
    uid_map_json = _json.dumps(uid_map, ensure_ascii=False)

    return f"""
    <html>{STYLE_HEADER}
    <body>
    <div class="navbar">
        <h1>📈 แดชบอร์ดสถิติขั้นสูง</h1>
        <a href="{back_url}" class="btn btn-secondary">← กลับ</a>
    </div>
    <div class="main-container" style="max-width:920px;">
        {scope_note}

        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:10px; margin-bottom:18px;">
            <div class="card" style="text-align:center; padding:14px 8px;">
                <div style="font-size:22px;">🧑‍🎓</div>
                <div style="font-size:20px;font-weight:800;color:#1e293b;">{total_students}</div>
                <div style="font-size:11px;color:#64748b;">นักเรียนทั้งหมด</div>
            </div>
            <div class="card" style="text-align:center; padding:14px 8px;">
                <div style="font-size:22px;">🎖️</div>
                <div style="font-size:20px;font-weight:800;color:#1d4ed8;">{avg_score}</div>
                <div style="font-size:11px;color:#64748b;">คะแนนประพฤติเฉลี่ย</div>
            </div>
            <div class="card" style="text-align:center; padding:14px 8px;">
                <div style="font-size:22px;">🚨</div>
                <div style="font-size:20px;font-weight:800;color:#dc2626;">{len(at_risk)}</div>
                <div style="font-size:11px;color:#64748b;">นักเรียนที่ควรเฝ้าระวัง</div>
            </div>
            <div class="card" style="text-align:center; padding:14px 8px;">
                <div style="font-size:22px;">📅</div>
                <div style="font-size:20px;font-weight:800;color:#16a34a;">{f"{attendance_rate_today}%" if attendance_rate_today is not None else "-"}</div>
                <div style="font-size:11px;color:#64748b;">อัตรามาเรียนวันนี้</div>
            </div>
            <div class="card" style="text-align:center; padding:14px 8px;">
                <div style="font-size:22px;">📋</div>
                <div style="font-size:20px;font-weight:800;color:#a16207;">{pending_leave}</div>
                <div style="font-size:11px;color:#64748b;">คำร้องลารอตรวจสอบ</div>
            </div>
        </div>

        <div class="card">
            <h2>🔴 เหตุการณ์สดทั่วโรงเรียน <span id="live-dot" style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#22c55e;margin-left:6px;"></span></h2>
            <div id="live-feed" style="max-height:260px; overflow-y:auto; display:flex; flex-direction:column-reverse; gap:8px;">
                <p style="color:#94a3b8;text-align:center;padding:20px 0;font-size:12.5px;">🔌 กำลังรอเหตุการณ์... (ลองหักคะแนน/มอบหมายการบ้าน/อนุมัติใบลา จากอีกแท็บดูได้เลย)</p>
            </div>
        </div>

        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
            <div class="card" style="padding:14px;">
                <h2 style="font-size:14px;">🏆 ท็อป 5 คะแนนดีเด่น</h2>
                {top5_html}
            </div>
            <div class="card" style="padding:14px;">
                <h2 style="font-size:14px;">⚠️ ท็อป 5 ที่ควรเฝ้าระวัง</h2>
                {bottom5_html}
            </div>
        </div>

        <div class="card">
            <h2>📊 แนวโน้มการเช็กชื่อ (14 วันล่าสุด)</h2>
            <canvas id="trendChart" height="110"></canvas>
        </div>
        <div class="card">
            <h2>🩺 สัดส่วนประเภทการลา</h2>
            <canvas id="leaveChart" height="140"></canvas>
        </div>
        <div class="card">
            <h2>🚨 นักเรียนขาดเรียนบ่อยที่สุด (Top 10)</h2>
            <canvas id="absentChart" height="140"></canvas>
        </div>
        <div class="card">
            <h2>🎖️ การกระจายคะแนนความประพฤติ</h2>
            <canvas id="conductChart" height="140"></canvas>
        </div>
        <div style="text-align:center;color:#94a3b8;font-size:12px;margin:12px 0 20px;">KK STUDIO GROUP · K-School Analytics</div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.4/chart.umd.min.js"></script>
    <script>
        const palette = {{ มา:'#10b981', สาย:'#f59e0b', ลา:'#3b82f6', ขาด:'#ef4444' }};

        async function loadTrend() {{
            const res = await fetch('/api/analytics/attendance_trend');
            const d = await res.json();
            new Chart(document.getElementById('trendChart'), {{
                type: 'line',
                data: {{
                    labels: d.labels,
                    datasets: Object.keys(d.series).map(k => ({{
                        label: k, data: d.series[k], borderColor: palette[k] || '#64748b',
                        backgroundColor: (palette[k] || '#64748b') + '22', tension: 0.35, fill: true
                    }}))
                }},
                options: {{ responsive:true, plugins:{{legend:{{position:'bottom'}}}}, scales:{{y:{{beginAtZero:true}}}} }}
            }});
        }}

        async function loadLeaveBreakdown() {{
            const res = await fetch('/api/analytics/leave_breakdown');
            const d = await res.json();
            new Chart(document.getElementById('leaveChart'), {{
                type: 'doughnut',
                data: {{ labels: d.labels, datasets: [{{ data: d.values, backgroundColor: ['#ef4444','#3b82f6','#94a3b8'] }}] }},
                options: {{ responsive:true, plugins:{{legend:{{position:'bottom'}}}} }}
            }});
        }}

        async function loadTopAbsent() {{
            const res = await fetch('/api/analytics/top_absent');
            const d = await res.json();
            new Chart(document.getElementById('absentChart'), {{
                type: 'bar',
                data: {{ labels: d.labels, datasets: [{{ label:'จำนวนครั้งที่ขาด', data: d.values, backgroundColor:'#ef4444' }}] }},
                options: {{ responsive:true, indexAxis:'y', plugins:{{legend:{{display:false}}}}, scales:{{x:{{beginAtZero:true, ticks:{{stepSize:1}}}}}} }}
            }});
        }}

        async function loadConduct() {{
            const res = await fetch('/api/analytics/conduct_distribution');
            const d = await res.json();
            new Chart(document.getElementById('conductChart'), {{
                type: 'bar',
                data: {{ labels: d.labels, datasets: [{{ label:'จำนวนนักเรียน', data: d.values, backgroundColor:['#10b981','#3b82f6','#f59e0b','#ef4444'] }}] }},
                options: {{ responsive:true, plugins:{{legend:{{display:false}}}}, scales:{{y:{{beginAtZero:true, ticks:{{stepSize:1}}}}}} }}
            }});
        }}

        loadTrend(); loadLeaveBreakdown(); loadTopAbsent(); loadConduct();

        // 🔴 ฟีดเหตุการณ์สดทั่วโรงเรียน — แอดมินเห็นทุกอีเวนต์ไม่ว่าจะส่งหาใคร (ต่างจากฝั่งนักเรียนที่กรองเฉพาะของตัวเอง)
        const UID_MAP = {uid_map_json};
        function connectLiveFeed() {{
            const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
            let ws;
            try {{ ws = new WebSocket(protocol + window.location.host + '/ws/notify'); }} catch(e) {{ return; }}
            const feed = document.getElementById('live-feed');
            const dot = document.getElementById('live-dot');
            ws.onopen = function() {{ dot.style.background = '#22c55e'; }};
            ws.onclose = function() {{ dot.style.background = '#94a3b8'; setTimeout(connectLiveFeed, 3000); }};
            ws.onmessage = function(event) {{
                let data;
                try {{ data = JSON.parse(event.data); }} catch(e) {{ return; }}
                if (data.type !== 'student_notify') return;
                if (feed.children.length === 1 && feed.children[0].tagName === 'P') {{ feed.innerHTML = ''; }}
                const who = (Array.isArray(data.target_uids) && data.target_uids.length === 1) ? (UID_MAP[data.target_uids[0]] || '') :
                            (data.target_uid ? (UID_MAP[data.target_uid] || '') :
                            (data.broadcast_all ? 'นักเรียนทุกคน' : (Array.isArray(data.target_uids) ? `${{data.target_uids.length}} คน` : '')));
                const now = new Date();
                const timeStr = now.toLocaleTimeString('th-TH', {{hour:'2-digit', minute:'2-digit', second:'2-digit'}});
                const toneColors = {{ success:'#15803d', danger:'#b91c1c', info:'#1d4ed8' }};
                const c = toneColors[data.tone] || '#1d4ed8';
                const row = document.createElement('div');
                row.style.cssText = 'padding:8px 10px; border-left:3px solid ' + c + '; background:#f8fafc; border-radius:6px; animation: fadeIn .4s ease;';
                row.innerHTML = `<div style="font-size:12.5px;font-weight:700;color:${{c}};">${{data.title}}</div>
                    <div style="font-size:11.5px;color:#475569;margin-top:2px;">${{data.message}}${{who ? ' · ' + who : ''}}</div>
                    <div style="font-size:10px;color:#94a3b8;margin-top:2px;">🕐 ${{timeStr}}</div>`;
                feed.insertBefore(row, feed.firstChild);
                while (feed.children.length > 30) {{ feed.removeChild(feed.lastChild); }}
            }};
        }}
        connectLiveFeed();
    </script>
    <style>@keyframes fadeIn {{ from {{ opacity:0; transform:translateY(-6px); }} to {{ opacity:1; transform:translateY(0); }} }}</style>
    </body></html>
    """


@app.get("/api/analytics/attendance_trend")
async def api_analytics_attendance_trend(days: int = 14, user_session: Optional[str] = Cookie(None)):
    access, redirect = require_analytics_access(user_session)
    if redirect: return JSONResponse({"labels": [], "series": {}}, status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT classroom, status, date FROM attendance_logs")
    logs = cursor.fetchall()
    conn.close()

    today = datetime.now().date()
    date_labels = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        date_labels.append(d.strftime("%d/%m"))
    counts = {k: {lbl: 0 for lbl in date_labels} for k in ("มา", "สาย", "ลา", "ขาด")}

    for classroom, status, date_str in logs:
        if not _analytics_classroom_ok(access, classroom):
            continue
        if status not in counts:
            continue
        try:
            d_obj = datetime.strptime(date_str, "%d/%m/%Y").date()
        except Exception:
            continue
        delta_days = (today - d_obj).days
        if 0 <= delta_days < days:
            lbl = d_obj.strftime("%d/%m")
            if lbl in counts[status]:
                counts[status][lbl] += 1

    series = {status: [counts[status][lbl] for lbl in date_labels] for status in counts}
    return JSONResponse({"labels": date_labels, "series": series})


@app.get("/api/analytics/leave_breakdown")
async def api_analytics_leave_breakdown(user_session: Optional[str] = Cookie(None)):
    access, redirect = require_analytics_access(user_session)
    if redirect: return JSONResponse({"labels": [], "values": []}, status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT classroom, leave_type FROM leave_requests")
    rows = cursor.fetchall()
    conn.close()
    tally = {"ลาป่วย": 0, "ลากิจ": 0, "อื่นๆ": 0}
    for classroom, ltype in rows:
        if not _analytics_classroom_ok(access, classroom):
            continue
        tally[ltype if ltype in tally else "อื่นๆ"] += 1
    return JSONResponse({"labels": list(tally.keys()), "values": list(tally.values())})


@app.get("/api/analytics/top_absent")
async def api_analytics_top_absent(limit: int = 10, user_session: Optional[str] = Cookie(None)):
    access, redirect = require_analytics_access(user_session)
    if redirect: return JSONResponse({"labels": [], "values": []}, status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT student_name, classroom, status FROM attendance_logs WHERE status='ขาด'")
    rows = cursor.fetchall()
    conn.close()
    tally = {}
    for name, classroom, status in rows:
        if not _analytics_classroom_ok(access, classroom):
            continue
        tally[name] = tally.get(name, 0) + 1
    top = sorted(tally.items(), key=lambda x: x[1], reverse=True)[:limit]
    return JSONResponse({"labels": [t[0] for t in top], "values": [t[1] for t in top]})


@app.get("/api/analytics/conduct_distribution")
async def api_analytics_conduct_distribution(user_session: Optional[str] = Cookie(None)):
    access, redirect = require_analytics_access(user_session)
    if redirect: return JSONResponse({"labels": [], "values": []}, status_code=401)
    summary = get_conduct_summary()
    if access.get("role") == "level_head" and access.get("level_scope"):
        summary = [s for s in summary if get_grade_level(s.get("class", "")) == access["level_scope"]]
    buckets = {"90-100": 0, "70-89": 0, "50-69": 0, "ต่ำกว่า 50": 0}
    for s in summary:
        score = s["score"]
        if score >= 90: buckets["90-100"] += 1
        elif score >= 70: buckets["70-89"] += 1
        elif score >= 50: buckets["50-69"] += 1
        else: buckets["ต่ำกว่า 50"] += 1
    return JSONResponse({"labels": list(buckets.keys()), "values": list(buckets.values())})



# ==========================================
# 📊 RISK TAGGING — วิเคราะห์กลุ่มเสี่ยง
# ==========================================
def get_student_risk_tags(student_name: str, group_name: str = None) -> list:
    """คำนวณ tag กลุ่มเสี่ยงจากประวัติการเข้าเรียน"""
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    if group_name:
        cursor.execute("""SELECT status FROM attendance_logs
            WHERE student_name=? AND group_name=?""", (student_name, group_name))
    else:
        cursor.execute("SELECT status FROM attendance_logs WHERE student_name=?", (student_name,))
    records = [r[0] for r in cursor.fetchall()]
    conn.close()
    if not records:
        return []
    total = len(records)
    absent = records.count("ขาด")
    late = records.count("สาย")
    leave = records.count("ลา")
    absent_rate = absent / total
    late_rate = late / total
    tags = []
    if absent >= 3 or absent_rate >= 0.3:
        tags.append(("🔴 ขาดบ่อย", "#fef2f2", "#dc2626", "#fecaca"))
    if leave >= 3 or (leave + absent) / total >= 0.4:
        tags.append(("🟠 ลาบ่อย", "#fff7ed", "#ea580c", "#fed7aa"))
    if late >= 4 or late_rate >= 0.35:
        tags.append(("🟡 สายบ่อย", "#fefce8", "#ca8a04", "#fef08a"))
    if absent == 0 and late == 0 and total >= 3:
        tags.append(("🟢 เข้าเรียนดี", "#f0fdf4", "#16a34a", "#bbf7d0"))
    
    # เพิ่มแท็กสถานะการลาล่าสุด
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT reason FROM leave_requests WHERE student_name=? AND status='approved' ORDER BY leave_date DESC LIMIT 1", (student_name,))
    last_leave = cursor.fetchone()
    conn.close()
    if last_leave:
        tags.append((f"📋 ลา: {last_leave[0]}", "#eff6ff", "#1e40af", "#bfdbfe"))

    return tags

def _compute_risk_tags_from_records(records: list, last_leave_reason: Optional[str]) -> list:
    """คำนวณ tag จาก records ที่ดึงมาแล้ว (ไม่ query DB ซ้ำ) — ใช้ร่วมกับ get_all_students_risk_tags"""
    tags = []
    if records:
        total = len(records)
        absent = records.count("ขาด")
        late = records.count("สาย")
        leave = records.count("ลา")
        absent_rate = absent / total
        late_rate = late / total
        if absent >= 3 or absent_rate >= 0.3:
            tags.append(("🔴 ขาดบ่อย", "#fef2f2", "#dc2626", "#fecaca"))
        if leave >= 3 or (leave + absent) / total >= 0.4:
            tags.append(("🟠 ลาบ่อย", "#fff7ed", "#ea580c", "#fed7aa"))
        if late >= 4 or late_rate >= 0.35:
            tags.append(("🟡 สายบ่อย", "#fefce8", "#ca8a04", "#fef08a"))
        if absent == 0 and late == 0 and total >= 3:
            tags.append(("🟢 เข้าเรียนดี", "#f0fdf4", "#16a34a", "#bbf7d0"))
    if last_leave_reason:
        tags.append((f"📋 ลา: {last_leave_reason}", "#eff6ff", "#1e40af", "#bfdbfe"))
    return tags

def get_all_students_risk_tags(group_name: str = None) -> dict:
    """
    ⚡ เวอร์ชันเร็ว: ดึงข้อมูล attendance_logs และ leave_requests 'ครั้งเดียว' สำหรับนักเรียนทุกคน
    แทนที่จะเปิด DB connection แยกทีละคน (ของเดิมทำให้หน้า dashboard หน่วงมากเมื่อนักเรียนเยอะ)
    คืนค่าเป็น dict: { student_name: [tags...] }
    """
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()

    if group_name:
        cursor.execute("SELECT student_name, status FROM attendance_logs WHERE group_name=?", (group_name,))
    else:
        cursor.execute("SELECT student_name, status FROM attendance_logs")
    records_by_student = {}
    for sname, status in cursor.fetchall():
        records_by_student.setdefault(sname, []).append(status)

    # ดึง "การลาที่อนุมัติล่าสุด" ของทุกคนในรอบเดียว โดยเรียงตามวันที่ล่าสุดก่อน
    cursor.execute("SELECT student_name, reason FROM leave_requests WHERE status='approved' ORDER BY leave_date DESC")
    last_leave_by_student = {}
    for sname, reason in cursor.fetchall():
        if sname not in last_leave_by_student:
            last_leave_by_student[sname] = reason

    conn.close()

    all_names = set(records_by_student.keys()) | set(last_leave_by_student.keys())
    result = {}
    for name in all_names:
        result[name] = _compute_risk_tags_from_records(
            records_by_student.get(name, []),
            last_leave_by_student.get(name)
        )
    return result

# ==========================================
# 📤 EXPORT EXCEL — ดาวน์โหลดรายงาน
# ==========================================
@app.get("/api/admin/export_excel")
async def export_excel(user_session: Optional[str] = Cookie(None), group_name: str = ""):
    if user_session != "admin":
        return HTMLResponse("Unauthorized", status_code=401)
    
    try:
        import io
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
        from openpyxl.utils import get_column_letter

        conn = sqlite3.connect('attendance_pro.db')
        cursor = conn.cursor()

        if group_name:
            cursor.execute("SELECT DISTINCT group_name FROM attendance_logs WHERE group_name=?", (group_name,))
        else:
            cursor.execute("SELECT DISTINCT group_name FROM attendance_logs ORDER BY group_name")
        groups = [r[0] for r in cursor.fetchall()]

        if not groups:
            conn.close()
            return alert_redirect("ยังไม่มีข้อมูลประวัติการเช็กชื่อในระบบ", type="warning")

        wb = Workbook()
        # ตรวจสอบว่ามี Sheet อยู่หรือไม่ก่อนลบ
        if len(wb.sheetnames) > 0:
            default_sheet = wb.active
            # เราจะใช้ Sheet แรกที่มีอยู่แล้วแทนการลบและสร้างใหม่เพื่อความชัวร์
            first_grp = groups[0]
            safe_title = "".join([c for c in first_grp if c.isalnum() or c in ' '])[:31].strip() or "Report"
            ws = wb.active
            ws.title = safe_title
        else:
            ws = wb.create_sheet("Report")

        for idx, grp in enumerate(groups):
            if idx == 0:
                ws = wb.active
            else:
                safe_title = "".join([c for c in grp if c.isalnum() or c in ' '])[:31].strip() or f"Report {idx+1}"
                # ป้องกันชื่อ Sheet ซ้ำ
                if safe_title in wb.sheetnames: safe_title = f"{safe_title}_{idx}"
                ws = wb.create_sheet(title=safe_title)

            # สไตล์สำหรับหัวตาราง
            header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True)
            center_align = Alignment(horizontal="center", vertical="center")
            border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

            # ส่วนหัวรายงาน
            ws.merge_cells('A1:E1')
            ws['A1'] = f"K-School · รายงานเช็กชื่อคลาสวิชา: {grp}"
            ws['A1'].font = Font(size=14, bold=True, color="1E3A8A")
            
            ws['A2'] = f"ออกรายงานเมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            ws['A2'].font = Font(italic=True, color="64748B")

            # ดึงข้อมูลวันที่และนักเรียน
            cursor.execute("SELECT DISTINCT date FROM attendance_logs WHERE group_name=? ORDER BY date ASC", (grp,))
            dates = [r[0] for r in cursor.fetchall()]
            
            # แก้ไข: ดึงรายชื่อนักเรียนแบบไม่ซ้ำโดยใช้กลุ่มของ ชื่อ, เลขที่, และห้อง
            cursor.execute("""SELECT student_name, student_no, classroom FROM attendance_logs 
                              WHERE group_name=? 
                              GROUP BY student_name, student_no, classroom
                              ORDER BY CAST(student_no AS INTEGER)""", (grp,))
            students = cursor.fetchall()

            # Header Row
            headers = ["เลขที่", "ชื่อ-นามสกุล", "ชั้น/ห้อง"] + dates + ["มา", "สาย", "ลา", "ขาด", "รวม", "กลุ่มเสี่ยง"]
            ws.append([]) # เว้นบรรทัด
            ws.append(headers)
            
            header_row_idx = 4
            for col_idx, val in enumerate(headers, 1):
                cell = ws.cell(row=header_row_idx, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = center_align
                cell.border = border

            # แก้ไข: ดึงข้อมูลการเช็กชื่อมาเก็บไว้ใน Map โดยใช้ (ชื่อ, เลขที่, ห้อง, วันที่) เพื่อป้องกันชื่อซ้ำแต่คนละคน
            cursor.execute("SELECT student_name, student_no, classroom, date, status FROM attendance_logs WHERE group_name=?", (grp,))
            log_map = {(r[0], r[1], r[2], r[3]): r[4] for r in cursor.fetchall()}

            # ⚡ ดึง risk tags ของนักเรียนทั้งกลุ่มครั้งเดียว แทนการ query แยกทีละคน
            group_risk_tags = get_all_students_risk_tags(grp)

            # ใส่ข้อมูลนักเรียน
            for sname, sno, scls in students:
                row_data = [sno, sname, scls]
                cnt = {"มา": 0, "สาย": 0, "ลา": 0, "ขาด": 0}
                for d in dates:
                    # แก้ไข: ใช้คีย์ที่ระบุตัวตนนักเรียนได้ชัดเจนขึ้น
                    st = log_map.get((sname, sno, scls, d), "-")
                    row_data.append(st)
                    if st in cnt: cnt[st] += 1
                
                total = sum(cnt.values())
                tags = group_risk_tags.get(sname, [])
                tag_str = " / ".join([t[0] for t in tags]) if tags else "ปกติ"
                row_data += [cnt["มา"], cnt["สาย"], cnt["ลา"], cnt["ขาด"], total, tag_str]
                ws.append(row_data)
                
                curr_row = ws.max_row
                for c_idx in range(1, len(headers) + 1):
                    cell = ws.cell(row=curr_row, column=c_idx)
                    cell.border = border
                    if c_idx != 2: cell.alignment = center_align

            # ปรับขนาดคอลัมน์ (แก้บัค ####)
            column_widths = [8, 25, 12] + [12]*len(dates) + [8, 8, 8, 8, 8, 15]
            for i, width in enumerate(column_widths, 1):
                ws.column_dimensions[get_column_letter(i)].width = width

        conn.close()
        
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        fname = f"kschool_report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        from fastapi.responses import Response as FResponse
        return FResponse(
            content=output.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={fname}"}
        )
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"❌ Excel Export Error: {error_msg}")
        return HTMLResponse(f"<h3>เกิดข้อผิดพลาดในการสร้างไฟล์ Excel</h3><pre>{e}</pre><p>โปรดตรวจสอบว่าได้ติดตั้งไลบรารี openpyxl หรือยัง</p>")

# ==========================================

@app.get("/admin/announcements", response_class=HTMLResponse)
async def admin_announcements_page(user_session: Optional[str] = Cookie(None)):
    if user_session != "admin":
        return RedirectResponse(url="/login", status_code=303)

    conn = sqlite3.connect("attendance_pro.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, body, level, created_at, is_active FROM announcements ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    level_meta = {
        "normal": {"bg": "#eff6ff", "border": "#bfdbfe", "text": "#1e40af", "icon": "📣", "label": "ทั่วไป"},
        "important": {"bg": "#fffbeb", "border": "#fde68a", "text": "#92400e", "icon": "⚠️", "label": "สำคัญ"},
        "urgent": {"bg": "#fef2f2", "border": "#fecaca", "text": "#991b1b", "icon": "🚨", "label": "ด่วนมาก"},
    }

    cards = ""
    for id_, title, body, level, created_at, is_active in rows:
        m = level_meta.get(level, level_meta["normal"])
        opacity = "1" if is_active else "0.5"
        status_label = "🟢 กำลังแสดง" if is_active else "⚪ ซ่อนอยู่"
        cards += f"""
        <div style="background:{m['bg']}; border:1px solid {m['border']}; border-left:4px solid {m['text']}; border-radius:14px; padding:16px; margin-bottom:12px; opacity:{opacity};">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:10px; margin-bottom:6px;">
                <div style="font-weight:800; font-size:14.5px; color:{m['text']};">{m['icon']} {title}</div>
                <span style="font-size:10.5px; font-weight:700; color:{m['text']}; white-space:nowrap;">{status_label}</span>
            </div>
            <div style="font-size:13px; color:#475569; line-height:1.6; margin-bottom:10px;">{body}</div>
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <span style="font-size:11px; color:#94a3b8; font-weight:600;">🕐 {created_at} · ระดับ: {m['label']}</span>
                <div style="display:flex; gap:6px;">
                    <a href="/api/admin/announcement/toggle?id={id_}" class="btn btn-secondary" style="padding:5px 10px; font-size:11px;">{"🙈 ซ่อน" if is_active else "👁️ แสดง"}</a>
                    <a href="/api/admin/announcement/delete?id={id_}" class="btn btn-danger" style="padding:5px 10px; font-size:11px;" onclick="return confirm('ยืนยันลบประกาศนี้?')">🗑️ ลบ</a>
                </div>
            </div>
        </div>
        """

    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> 📢 ประกาศข่าวสาร</h1>
            <a href="/admin/dashboard" class="btn btn-secondary">⬅ กลับหน้าควบคุม</a>
        </div>
        <div class="main-container">
            <div class="card">
                <h2>➕ เพิ่มประกาศใหม่</h2>
                <form action="/api/admin/announcement/add" method="post">
                    <label style="font-size:12.5px; font-weight:700; color:#475569;">หัวข้อประกาศ:</label>
                    <input type="text" name="title" placeholder="เช่น แจ้งปิดเรียนกรณีพิเศษ" required>
                    <label style="font-size:12.5px; font-weight:700; color:#475569;">รายละเอียด:</label>
                    <textarea name="body" placeholder="รายละเอียดประกาศ" required style="min-height:80px;"></textarea>
                    <label style="font-size:12.5px; font-weight:700; color:#475569;">ระดับความสำคัญ:</label>
                    <select name="level" required>
                        <option value="normal">📣 ทั่วไป</option>
                        <option value="important">⚠️ สำคัญ</option>
                        <option value="urgent">🚨 ด่วนมาก</option>
                    </select>
                    <button type="submit" class="btn-submit">📢 เผยแพร่ประกาศ</button>
                </form>
            </div>
            <div class="card">
                <h2>📋 ประกาศทั้งหมด ({len(rows)})</h2>
                {cards if cards else "<p style='color:#94a3b8; text-align:center; padding:20px 0;'>ยังไม่มีประกาศในระบบ</p>"}
            </div>
        </div>
    </body></html>
    """

@app.post("/api/admin/announcement/add")
async def api_add_announcement(title: str = Form(...), body: str = Form(...), level: str = Form(...), user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return HTMLResponse("Unauthorized", status_code=401)
    created_at = datetime.now().strftime("%d/%m/%Y %H:%M")
    conn = sqlite3.connect("attendance_pro.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO announcements (title, body, level, created_at, is_active) VALUES (?,?,?,?,1)", (title.strip(), body.strip(), level, created_at))
    conn.commit()
    conn.close()

    # 🔴 แจ้งเตือนแบบเรียลไทม์ให้นักเรียนทุกคนทราบทันทีว่ามีประกาศใหม่
    level_icon = {"urgent": "🚨", "important": "⚠️"}.get(level, "📣")
    await push_student_notify(
        title=f"{level_icon} ประกาศใหม่: {title.strip()}",
        message=body.strip()[:120] + ("…" if len(body.strip()) > 120 else ""),
        tone="danger" if level == "urgent" else ("info" if level == "important" else "info"),
        all_students=True,
    )

    return alert_redirect("เพิ่มประกาศเรียบร้อยแล้ว", type="success", url="/admin/announcements")

@app.get("/api/admin/announcement/toggle")
async def api_toggle_announcement(id: int, user_session: Optional[str] = Cookie(None)):
    if user_session != "admin":
        return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect("attendance_pro.db")
    cursor = conn.cursor()
    cursor.execute("SELECT is_active FROM announcements WHERE id=?", (id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE announcements SET is_active=? WHERE id=?", (0 if row[0] else 1, id))
        conn.commit()
    conn.close()
    return RedirectResponse(url="/admin/announcements", status_code=303)

@app.get("/api/admin/announcement/delete")
async def api_delete_announcement(id: int, user_session: Optional[str] = Cookie(None)):
    if user_session != "admin":
        return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect("attendance_pro.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM announcements WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/admin/announcements", status_code=303)

def _parse_dt_flex(s: str) -> datetime:
    """🕐 พาร์สวันเวลาจากหลายรูปแบบที่ใช้กระจายอยู่ในระบบ (ประกาศ/คะแนนความประพฤติ/การบ้าน/ใบลา) ให้เรียงลำดับร่วมกันได้"""
    if not s:
        return datetime.min
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return datetime.min

@app.get("/app/notifications", response_class=HTMLResponse)
async def app_notifications_page(user_session: Optional[str] = Cookie(None)):
    """🔔 หน้าแจ้งเตือน สไตล์รายการ์ด (ไอคอนซ้าย / หัวข้อสีน้ำเงิน / รายละเอียดใต้หัวข้อ / วันเวลา / ลูกศรขวา)
    ฝั่งนักเรียน: รวมทุกอีเวนต์ที่เกี่ยวกับตัวเอง (คะแนนความประพฤติ / การบ้านใหม่ / ผลใบลา / ประกาศทั่วไป) เรียงตามเวลาล่าสุด
    ฝั่งครู: แสดงเฉพาะประกาศทั่วไป (เหมือนเดิม)"""
    if not user_session or not (user_session.startswith("student_") or user_session.startswith("teacher_")):
        return RedirectResponse(url="/login", status_code=303)
    role = "student" if user_session.startswith("student_") else "teacher"
    back_url = "/student/dashboard" if role == "student" else None
    teacher_user = urllib.parse.unquote(user_session.replace("teacher_", "", 1)) if role == "teacher" else None
    if role == "teacher":
        back_url = f"/app/dashboard?user={urllib.parse.quote(teacher_user)}"

    level_meta = {
        "normal": {"bg": "#eff6ff", "text": "#1e40af", "icon": "📣"},
        "important": {"bg": "#fffbeb", "text": "#92400e", "icon": "⚠️"},
        "urgent": {"bg": "#fef2f2", "text": "#991b1b", "icon": "🚨"},
    }

    conn = sqlite3.connect("attendance_pro.db")
    cursor = conn.cursor()

    # 📣 ประกาศทั่วไป — ใช้ร่วมกันทั้งครูและนักเรียน
    cursor.execute("SELECT title, body, level, created_at FROM announcements WHERE is_active=1")
    feed = []
    for title, body, level, created_at in cursor.fetchall():
        m = level_meta.get(level, level_meta["normal"])
        feed.append({"icon": m["icon"], "bg": m["bg"], "text": m["text"], "title": title, "desc": body, "time": created_at, "sort": _parse_dt_flex(created_at)})

    if role == "student":
        uid = urllib.parse.unquote(user_session.replace("student_", "", 1))
        me = next((s for s in get_sorted_master_students() if s['uid'] == uid), None)

        # 🎖️ คะแนนความประพฤติ (หัก/เพิ่ม/คืน) — ของตัวเองทั้งหมด
        for h in get_conduct_history(uid):
            is_plus = h['points'] >= 0
            sign = "+" if is_plus else ""
            feed.append({
                "icon": "🏅", "bg": "#f0fdf4" if is_plus else "#fef2f2", "text": "#15803d" if is_plus else "#b91c1c",
                "title": f"{'ได้รับ' if is_plus else 'ถูกหัก'}คะแนนความประพฤติ {sign}{h['points']} คะแนน",
                "desc": f"{h['reason']} · โดย: {h['recorded_by']}",
                "time": h['created_at'], "sort": _parse_dt_flex(h['created_at']),
            })

        # 📚 การบ้านใหม่ — เฉพาะกลุ่มวิชาที่ตัวเองอยู่
        if me:
            cursor.execute("""
                SELECT a.title, a.due_date, a.created_at, cg.group_name
                FROM assignments a
                JOIN group_assignments ga ON ga.group_id = a.group_id
                JOIN course_groups cg ON cg.group_id = a.group_id
                WHERE ga.student_uid = ? AND a.is_active = 1
            """, (uid,))
            for title, due_date, created_at, group_name in cursor.fetchall():
                due_txt = f" (กำหนดส่ง {due_date})" if due_date else ""
                feed.append({
                    "icon": "📚", "bg": "#eff6ff", "text": "#1d4ed8",
                    "title": f"การบ้านใหม่: {group_name}",
                    "desc": f"{title}{due_txt}",
                    "time": created_at, "sort": _parse_dt_flex(created_at),
                })

            # 📋 ผลการพิจารณาใบลาของตัวเอง (อนุมัติ/ปฏิเสธ)
            cursor.execute("""
                SELECT group_name, leave_date, status, reviewed_at, reason
                FROM leave_requests
                WHERE student_name=? AND student_no=? AND classroom=? AND status IN ('approved','rejected') AND reviewed_at IS NOT NULL
            """, (me['name'], me['no'], me['class']))
            for group_name, leave_date, status, reviewed_at, reason in cursor.fetchall():
                approved = status == "approved"
                feed.append({
                    "icon": "✅" if approved else "❌", "bg": "#f0fdf4" if approved else "#fef2f2", "text": "#15803d" if approved else "#b91c1c",
                    "title": f"ใบลา{'ได้รับการอนุมัติ' if approved else 'ไม่ได้รับการอนุมัติ'}",
                    "desc": f"{group_name} · วันที่ {leave_date}" + (f" ({reason})" if reason else ""),
                    "time": reviewed_at, "sort": _parse_dt_flex(reviewed_at),
                })

    conn.close()
    feed.sort(key=lambda x: x["sort"], reverse=True)

    items_html = ""
    for it in feed:
        items_html += f"""
        <div class="nt-item">
            <div class="nt-icon" style="background:{it['bg']};color:{it['text']};">{it['icon']}</div>
            <div class="nt-body">
                <div class="nt-title">{it['title']}</div>
                <div class="nt-desc">{it['desc']}</div>
                <div class="nt-time">🗓️ {it['time']}</div>
            </div>
            <div class="nt-chevron">›</div>
        </div>"""

    return f"""
    <html>{STYLE_HEADER}
    <style>
        body {{ background: var(--surface-muted); }}
        .nt-header {{
            display:flex; align-items:center; gap:14px; padding: calc(env(safe-area-inset-top,0px) + 16px) 16px 16px;
            background: var(--surface); border-bottom: 1px solid var(--border);
        }}
        .nt-header a {{ font-size:20px; color: var(--navy-800); text-decoration:none; }}
        .nt-header h1 {{ margin:0; font-size:17px; font-weight:800; color: var(--navy-800); flex:1; text-align:center; margin-right:20px; }}
        .nt-list {{ max-width:640px; margin:0 auto; padding: 8px 0 24px; }}
        .nt-item {{
            display:flex; align-items:flex-start; gap:12px; padding:16px;
            background: var(--surface); border-bottom: 1px solid var(--border);
        }}
        .nt-icon {{
            width:44px; height:44px; border-radius:50%; flex-shrink:0;
            display:flex; align-items:center; justify-content:center; font-size:19px;
        }}
        .nt-body {{ flex:1; min-width:0; }}
        .nt-title {{ font-size:14.5px; font-weight:800; color:#2563eb; margin-bottom:4px; }}
        .nt-desc {{ font-size:12.5px; color:#475569; line-height:1.5; margin-bottom:6px; }}
        .nt-time {{ font-size:11px; color:#94a3b8; font-weight:600; }}
        .nt-chevron {{ font-size:20px; color:#cbd5e1; flex-shrink:0; padding-top:8px; }}
    </style>
    <body>
        <div class="nt-header">
            <a href="{back_url}">‹</a>
            <h1>แจ้งเตือน</h1>
        </div>
        <div class="nt-list">
            {items_html if items_html else "<p style='color:#94a3b8;text-align:center;padding:40px 0;'>ยังไม่มีการแจ้งเตือน</p>"}
        </div>
    </body></html>
    """

@app.get("/api/announcements")
async def api_get_announcements():
    """API ดึงประกาศที่แสดงอยู่ (ใช้ในหน้าครู)"""
    conn = sqlite3.connect("attendance_pro.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, body, level FROM announcements WHERE is_active=1 ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    return JSONResponse([{"id": r[0], "title": r[1], "body": r[2], "level": r[3]} for r in rows])

# ==========================================
# 🆕 ROUND 1: ผลการเรียน/คะแนนเก็บ · ตารางเรียน · การบ้าน · ชำระเงิน
# (นักเรียน + ครู เป็นผู้ใช้หลัก / ชำระเงินให้แอดมินเป็นผู้บันทึกสถานะ)
# ==========================================

# ---------- 🏫 ครู: ศูนย์กลางรายวิชา (เลือกเข้าเช็กชื่อ/ตารางเรียน/การบ้าน/ผลการเรียน) ----------
@app.get("/app/classroom/{group_id}", response_class=HTMLResponse)
async def app_classroom_hub(group_id: int, user: str, user_session: Optional[str] = Cookie(None)):
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return RedirectResponse(url="/login", status_code=303)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT group_name, teacher_username FROM course_groups WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return alert_redirect("ไม่พบกลุ่มวิชานี้", type="error", url=f"/app/dashboard?user={urllib.parse.quote(user)}")
    group_name, owner = row
    if owner != user:
        return alert_redirect("คุณไม่มีสิทธิ์เข้าถึงกลุ่มวิชานี้", type="error", url=f"/app/dashboard?user={urllib.parse.quote(user)}")

    qs = f"?user={urllib.parse.quote(user)}"
    return f"""
    <html>{STYLE_HEADER}
    {ADMIN_HOME_STYLE}
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> 📚 {group_name}</h1>
            <a href="/app/dashboard{qs}" class="btn btn-secondary">⬅ กลับ</a>
        </div>
        <div class="main-container">
            <div class="ah-grid3">
                <a href="/app/rollcall/{group_id}{qs}" class="ah-cell">
                    <div class="ah-cell-icon-wrap" style="background:#eff6ff;color:#1d4ed8;">📶</div>
                    <span class="ah-cell-label">เช็กชื่อ</span>
                </a>
                <a href="/app/timetable/{group_id}{qs}" class="ah-cell">
                    <div class="ah-cell-icon-wrap" style="background:#fef9c3;color:#a16207;">🗓️</div>
                    <span class="ah-cell-label">ตารางเรียน</span>
                </a>
                <a href="/app/homework/{group_id}{qs}" class="ah-cell">
                    <div class="ah-cell-icon-wrap" style="background:#fdf4ff;color:#a21caf;">📖</div>
                    <span class="ah-cell-label">การบ้าน</span>
                </a>
                <a href="/app/grades/{group_id}{qs}" class="ah-cell">
                    <div class="ah-cell-icon-wrap" style="background:#f0fdf4;color:#15803d;">📊</div>
                    <span class="ah-cell-label">ผลการเรียน</span>
                </a>
            </div>
        </div>
    </body></html>
    """

# ---------- 🗓️ ตารางเรียน (ครูจัดการ / นักเรียนดู) ----------
@app.get("/app/timetable/{group_id}", response_class=HTMLResponse)
async def app_timetable_manage(group_id: int, user: str, user_session: Optional[str] = Cookie(None)):
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return RedirectResponse(url="/login", status_code=303)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT group_name, teacher_username FROM course_groups WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    if not row or row[1] != user:
        conn.close()
        return alert_redirect("ไม่มีสิทธิ์เข้าถึง", type="error", url=f"/app/dashboard?user={urllib.parse.quote(user)}")
    group_name = row[0]
    cursor.execute("SELECT slot_id, day_of_week, start_time, end_time, room FROM timetable_slots WHERE group_id=? ORDER BY day_of_week, start_time", (group_id,))
    slots = cursor.fetchall()
    conn.close()

    uq = urllib.parse.quote(user)
    rows_html = "".join([f"""
        <tr>
            <td style="text-align:left;">วัน{THAI_WEEKDAYS.get(s[1], s[1])}</td>
            <td>{s[2]} - {s[3]}</td>
            <td>{s[4] or '-'}</td>
            <td><a href="/api/teacher/timetable/delete?slot_id={s[0]}&user={uq}&group_id={group_id}" class="btn btn-danger" style="padding:4px 10px;font-size:11px;" onclick="return confirm('ลบคาบเรียนนี้?')">ลบ</a></td>
        </tr>""" for s in slots])

    day_options = "".join([f'<option value="{k}">วัน{v}</option>' for k, v in THAI_WEEKDAYS.items()])

    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> 🗓️ ตารางเรียน — {group_name}</h1>
            <a href="/app/classroom/{group_id}?user={uq}" class="btn btn-secondary">⬅ กลับ</a>
        </div>
        <div class="main-container">
            <div class="card">
                <h2>➕ เพิ่มคาบเรียน</h2>
                <form action="/api/teacher/timetable/add" method="post">
                    <input type="hidden" name="group_id" value="{group_id}">
                    <input type="hidden" name="user" value="{user}">
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">วัน:</label>
                    <select name="day_of_week" required>{day_options}</select>
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">เวลาเริ่ม:</label>
                    <input type="time" name="start_time" required>
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">เวลาสิ้นสุด:</label>
                    <input type="time" name="end_time" required>
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">ห้อง/สถานที่:</label>
                    <input type="text" name="room" placeholder="เช่น ห้อง 204">
                    <button type="submit" class="btn-submit">💾 บันทึกคาบเรียน</button>
                </form>
            </div>
            <div class="card">
                <h2>📋 ตารางเรียนทั้งหมด ({len(slots)})</h2>
                <table><thead><tr><th style="text-align:left;">วัน</th><th>เวลา</th><th>ห้อง</th><th>จัดการ</th></tr></thead>
                <tbody>{rows_html if rows_html else "<tr><td colspan='4' style='color:#94a3b8;text-align:center;'>ยังไม่มีตารางเรียน</td></tr>"}</tbody></table>
            </div>
        </div>
    </body></html>
    """

@app.post("/api/teacher/timetable/add")
async def api_timetable_add(group_id: int = Form(...), user: str = Form(...), day_of_week: int = Form(...),
                             start_time: str = Form(...), end_time: str = Form(...), room: str = Form(""),
                             user_session: Optional[str] = Cookie(None)):
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT teacher_username FROM course_groups WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    if not row or row[0] != user:
        conn.close()
        return alert_redirect("ไม่มีสิทธิ์", type="error", url=f"/app/dashboard?user={urllib.parse.quote(user)}")
    cursor.execute("INSERT INTO timetable_slots (group_id, day_of_week, start_time, end_time, room, created_by, created_at) VALUES (?,?,?,?,?,?,?)",
                   (group_id, day_of_week, start_time, end_time, room.strip(), user, datetime.now().strftime("%d/%m/%Y %H:%M")))
    conn.commit()
    conn.close()
    return alert_redirect("เพิ่มคาบเรียนเรียบร้อยแล้ว", type="success", url=f"/app/timetable/{group_id}?user={urllib.parse.quote(user)}")

@app.get("/api/teacher/timetable/delete")
async def api_timetable_delete(slot_id: int, group_id: int, user: str, user_session: Optional[str] = Cookie(None)):
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT teacher_username FROM course_groups WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    if row and row[0] == user:
        cursor.execute("DELETE FROM timetable_slots WHERE slot_id=?", (slot_id,))
        conn.commit()
    conn.close()
    return RedirectResponse(url=f"/app/timetable/{group_id}?user={urllib.parse.quote(user)}", status_code=303)

@app.get("/student/timetable", response_class=HTMLResponse)
async def student_timetable(user_session: Optional[str] = Cookie(None)):
    if not user_session or not user_session.startswith("student_"):
        return RedirectResponse(url="/login", status_code=303)
    uid = urllib.parse.unquote(user_session.replace("student_", "", 1))
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT t.day_of_week, t.start_time, t.end_time, t.room, g.group_name
        FROM timetable_slots t
        JOIN group_assignments ga ON ga.group_id = t.group_id
        JOIN course_groups g ON g.group_id = t.group_id
        WHERE ga.student_uid = ?
        ORDER BY t.day_of_week, t.start_time""", (uid,))
    slots = cursor.fetchall()
    conn.close()

    by_day = {d: [] for d in range(1, 8)}
    for s in slots:
        by_day[s[0]].append(s)

    day_blocks = ""
    for d in range(1, 6):  # แสดง จันทร์-ศุกร์ เป็นหลัก (วันเรียนปกติ)
        items = by_day[d]
        rows = "".join([f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border);">
                <div>
                    <div style="font-weight:800;font-size:13.5px;">{it[4]}</div>
                    <div style="font-size:11.5px;color:#94a3b8;">📍 {it[3] or '-'}</div>
                </div>
                <div style="font-weight:700;font-size:12.5px;color:#2563eb;white-space:nowrap;">{it[1]} - {it[2]}</div>
            </div>""" for it in items])
        day_blocks += f"""
        <div class="card" style="margin-bottom:12px;">
            <h2 style="margin-bottom:4px;">📅 วัน{THAI_WEEKDAYS[d]}</h2>
            {rows if rows else "<p style='color:#94a3b8;font-size:12.5px;padding:8px 0;'>ไม่มีคาบเรียน</p>"}
        </div>"""

    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> 🗓️ ตารางเรียนของฉัน</h1>
            <a href="/student/dashboard" class="btn btn-secondary">⬅ กลับ</a>
        </div>
        <div class="main-container">{day_blocks}</div>
    </body></html>
    """

# ---------- 📖 การบ้าน (ครูมอบหมาย/ดูงานที่ส่ง / นักเรียนดู-ส่งงาน) ----------
@app.get("/app/homework/{group_id}", response_class=HTMLResponse)
async def app_homework_manage(group_id: int, user: str, user_session: Optional[str] = Cookie(None)):
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return RedirectResponse(url="/login", status_code=303)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT group_name, teacher_username FROM course_groups WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    if not row or row[1] != user:
        conn.close()
        return alert_redirect("ไม่มีสิทธิ์เข้าถึง", type="error", url=f"/app/dashboard?user={urllib.parse.quote(user)}")
    group_name = row[0]
    cursor.execute("SELECT COUNT(*) FROM group_assignments WHERE group_id=?", (group_id,))
    total_students = cursor.fetchone()[0]
    cursor.execute("SELECT assignment_id, title, detail, due_date, is_active FROM assignments WHERE group_id=? ORDER BY assignment_id DESC", (group_id,))
    hw_rows = cursor.fetchall()

    uq = urllib.parse.quote(user)
    cards = ""
    for a_id, title, detail, due_date, is_active in hw_rows:
        cursor.execute("SELECT COUNT(*) FROM assignment_submissions WHERE assignment_id=?", (a_id,))
        submitted_count = cursor.fetchone()[0]
        cards += f"""
        <div class="card" style="margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <h2 style="margin:0;">📖 {title}</h2>
                <span style="font-size:11px;color:#94a3b8;white-space:nowrap;">ส่งแล้ว {submitted_count}/{total_students}</span>
            </div>
            <p style="color:#475569;font-size:13px;line-height:1.6;">{detail}</p>
            <div style="font-size:11.5px;color:#94a3b8;margin-bottom:10px;">📅 กำหนดส่ง: {due_date or 'ไม่ระบุ'}</div>
            <div style="display:flex;gap:6px;">
                <a href="/app/homework/{group_id}/{a_id}/submissions?user={uq}" class="btn btn-secondary" style="padding:6px 12px;font-size:12px;">👁️ ดูงานที่ส่ง</a>
                <a href="/api/teacher/homework/delete?assignment_id={a_id}&group_id={group_id}&user={uq}" class="btn btn-danger" style="padding:6px 12px;font-size:12px;" onclick="return confirm('ลบการบ้านนี้?')">🗑️ ลบ</a>
            </div>
        </div>"""
    conn.close()

    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> 📖 การบ้าน — {group_name}</h1>
            <a href="/app/classroom/{group_id}?user={uq}" class="btn btn-secondary">⬅ กลับ</a>
        </div>
        <div class="main-container">
            <div class="card">
                <h2>➕ มอบหมายการบ้านใหม่</h2>
                <form action="/api/teacher/homework/add" method="post">
                    <input type="hidden" name="group_id" value="{group_id}">
                    <input type="hidden" name="user" value="{user}">
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">หัวข้อ:</label>
                    <input type="text" name="title" placeholder="เช่น แบบฝึกหัดบทที่ 3" required>
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">รายละเอียด:</label>
                    <textarea name="detail" placeholder="รายละเอียดงาน" style="min-height:80px;" required></textarea>
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">กำหนดส่ง:</label>
                    <input type="date" name="due_date">
                    <button type="submit" class="btn-submit">📤 มอบหมายงาน</button>
                </form>
            </div>
            <div class="card"><h2 style="margin:0;">📋 การบ้านทั้งหมด ({len(hw_rows)})</h2></div>
            {cards if cards else "<p style='color:#94a3b8;text-align:center;padding:20px 0;'>ยังไม่มีการบ้าน</p>"}
        </div>
    </body></html>
    """

@app.post("/api/teacher/homework/add")
async def api_homework_add(group_id: int = Form(...), user: str = Form(...), title: str = Form(...),
                            detail: str = Form(...), due_date: str = Form(""), user_session: Optional[str] = Cookie(None)):
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT teacher_username, group_name FROM course_groups WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    if not row or row[0] != user:
        conn.close()
        return alert_redirect("ไม่มีสิทธิ์", type="error", url=f"/app/dashboard?user={urllib.parse.quote(user)}")
    group_name = row[1]
    cursor.execute("INSERT INTO assignments (group_id, title, detail, due_date, created_by, created_at, is_active) VALUES (?,?,?,?,?,?,1)",
                   (group_id, title.strip(), detail.strip(), due_date, user, datetime.now().strftime("%d/%m/%Y %H:%M")))
    # 🔴 แจ้งเตือนแบบเรียลไทม์ให้นักเรียนทุกคนในกลุ่มวิชานี้ทันที
    cursor.execute("SELECT student_uid FROM group_assignments WHERE group_id=?", (group_id,))
    target_uids = [r[0] for r in cursor.fetchall()]
    conn.commit()
    conn.close()
    if target_uids:
        due_txt = f" (กำหนดส่ง {due_date})" if due_date else ""
        await push_student_notify(
            title=f"📚 การบ้านใหม่: {group_name}",
            message=f"{title.strip()}{due_txt}",
            tone="info",
            target_uids=target_uids,
        )
    return alert_redirect("มอบหมายการบ้านเรียบร้อยแล้ว", type="success", url=f"/app/homework/{group_id}?user={urllib.parse.quote(user)}")

@app.get("/api/teacher/homework/delete")
async def api_homework_delete(assignment_id: int, group_id: int, user: str, user_session: Optional[str] = Cookie(None)):
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT teacher_username FROM course_groups WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    if row and row[0] == user:
        cursor.execute("DELETE FROM assignments WHERE assignment_id=?", (assignment_id,))
        cursor.execute("DELETE FROM assignment_submissions WHERE assignment_id=?", (assignment_id,))
        conn.commit()
    conn.close()
    return RedirectResponse(url=f"/app/homework/{group_id}?user={urllib.parse.quote(user)}", status_code=303)

@app.get("/app/homework/{group_id}/{assignment_id}/submissions", response_class=HTMLResponse)
async def app_homework_submissions(group_id: int, assignment_id: int, user: str, user_session: Optional[str] = Cookie(None)):
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return RedirectResponse(url="/login", status_code=303)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT teacher_username FROM course_groups WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    if not row or row[0] != user:
        conn.close()
        return alert_redirect("ไม่มีสิทธิ์", type="error", url=f"/app/dashboard?user={urllib.parse.quote(user)}")
    cursor.execute("SELECT title FROM assignments WHERE assignment_id=?", (assignment_id,))
    title_row = cursor.fetchone()
    title = title_row[0] if title_row else "การบ้าน"
    cursor.execute("SELECT student_uid FROM group_assignments WHERE group_id=?", (group_id,))
    group_uids = {r[0] for r in cursor.fetchall()}
    cursor.execute("SELECT student_uid, content, submitted_at FROM assignment_submissions WHERE assignment_id=?", (assignment_id,))
    subs = {r[0]: {"content": r[1], "submitted_at": r[2]} for r in cursor.fetchall()}
    conn.close()

    all_students = [s for s in get_sorted_master_students() if s['uid'] in group_uids]
    rows = ""
    for s in all_students:
        sub = subs.get(s['uid'])
        if sub:
            rows += f"""<tr>
                <td style="text-align:left;">{s['name']}<br><span style="font-size:11px;color:#94a3b8;">{s['class']} เลขที่ {s['no']}</span></td>
                <td style="text-align:left;font-size:12.5px;">{sub['content']}</td>
                <td style="font-size:11px;color:#15803d;font-weight:800;white-space:nowrap;">✅ ส่งแล้ว<br>{sub['submitted_at']}</td>
            </tr>"""
        else:
            rows += f"""<tr>
                <td style="text-align:left;">{s['name']}<br><span style="font-size:11px;color:#94a3b8;">{s['class']} เลขที่ {s['no']}</span></td>
                <td style="text-align:left;color:#94a3b8;">-</td>
                <td style="font-size:11px;color:#b91c1c;font-weight:800;">⏳ ยังไม่ส่ง</td>
            </tr>"""

    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> 👁️ งานที่ส่ง — {title}</h1>
            <a href="/app/homework/{group_id}?user={urllib.parse.quote(user)}" class="btn btn-secondary">⬅ กลับ</a>
        </div>
        <div class="main-container">
            <div class="card" style="overflow-x:auto;">
                <table><thead><tr><th style="text-align:left;">นักเรียน</th><th style="text-align:left;">คำตอบ</th><th>สถานะ</th></tr></thead>
                <tbody>{rows if rows else "<tr><td colspan='3' style='color:#94a3b8;text-align:center;'>ยังไม่มีนักเรียนในกลุ่มนี้</td></tr>"}</tbody></table>
            </div>
        </div>
    </body></html>
    """

@app.get("/student/homework", response_class=HTMLResponse)
async def student_homework(user_session: Optional[str] = Cookie(None)):
    if not user_session or not user_session.startswith("student_"):
        return RedirectResponse(url="/login", status_code=303)
    uid = urllib.parse.unquote(user_session.replace("student_", "", 1))
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT a.assignment_id, a.title, a.detail, a.due_date, g.group_name,
                       s.content, s.submitted_at
        FROM assignments a
        JOIN course_groups g ON g.group_id = a.group_id
        JOIN group_assignments ga ON ga.group_id = a.group_id AND ga.student_uid = ?
        LEFT JOIN assignment_submissions s ON s.assignment_id = a.assignment_id AND s.student_uid = ?
        WHERE a.is_active = 1
        ORDER BY a.assignment_id DESC""", (uid, uid))
    hw_rows = cursor.fetchall()
    conn.close()

    cards = ""
    for a_id, title, detail, due_date, group_name, content, submitted_at in hw_rows:
        if content:
            status_html = f"""<div style='font-size:11.5px;color:#15803d;font-weight:800;margin-bottom:8px;'>✅ ส่งแล้วเมื่อ {submitted_at}</div>
            <div style='background:#f0fdf4;border-radius:10px;padding:10px;font-size:12.5px;color:#334155;'>{content}</div>"""
        else:
            status_html = f"""
            <form action="/api/student/homework/submit" method="post">
                <input type="hidden" name="assignment_id" value="{a_id}">
                <textarea name="content" placeholder="พิมพ์คำตอบ/บันทึกงานของคุณที่นี่" style="min-height:70px;" required></textarea>
                <button type="submit" class="btn-submit">📤 ส่งงาน</button>
            </form>"""
        cards += f"""
        <div class="card" style="margin-bottom:12px;">
            <div style="font-size:11px;color:#94a3b8;font-weight:700;margin-bottom:2px;">{group_name}</div>
            <h2 style="margin:0 0 6px;">📖 {title}</h2>
            <p style="color:#475569;font-size:13px;line-height:1.6;">{detail}</p>
            <div style="font-size:11.5px;color:#94a3b8;margin-bottom:10px;">📅 กำหนดส่ง: {due_date or 'ไม่ระบุ'}</div>
            {status_html}
        </div>"""

    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> 📖 การบ้านของฉัน</h1>
            <a href="/student/dashboard" class="btn btn-secondary">⬅ กลับ</a>
        </div>
        <div class="main-container">
            {cards if cards else "<p style='color:#94a3b8;text-align:center;padding:20px 0;'>ยังไม่มีการบ้าน</p>"}
        </div>
    </body></html>
    """

@app.post("/api/student/homework/submit")
async def api_student_homework_submit(assignment_id: int = Form(...), content: str = Form(...), user_session: Optional[str] = Cookie(None)):
    if not user_session or not user_session.startswith("student_"):
        return HTMLResponse("Unauthorized", status_code=401)
    uid = urllib.parse.unquote(user_session.replace("student_", "", 1))
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO assignment_submissions (assignment_id, student_uid, content, submitted_at)
        VALUES (?,?,?,?)
        ON CONFLICT(assignment_id, student_uid) DO UPDATE SET content=excluded.content, submitted_at=excluded.submitted_at""",
        (assignment_id, uid, content.strip(), datetime.now().strftime("%d/%m/%Y %H:%M")))
    conn.commit()
    conn.close()
    return alert_redirect("ส่งงานเรียบร้อยแล้ว", type="success", url="/student/homework")

# ---------- 📊 ผลการเรียน/คะแนนเก็บ (ครูจัดการ / นักเรียนดู) ----------
@app.get("/app/grades/{group_id}", response_class=HTMLResponse)
async def app_grades_manage(group_id: int, user: str, user_session: Optional[str] = Cookie(None)):
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return RedirectResponse(url="/login", status_code=303)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT group_name, teacher_username, grades_visibility FROM course_groups WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    if not row or row[1] != user:
        conn.close()
        return alert_redirect("ไม่มีสิทธิ์เข้าถึง", type="error", url=f"/app/dashboard?user={urllib.parse.quote(user)}")
    group_name = row[0]
    visibility = row[2] or "hidden"
    cursor.execute("SELECT item_id, item_name, max_score, category FROM grade_items WHERE group_id=? ORDER BY item_id", (group_id,))
    items = cursor.fetchall()
    cursor.execute("SELECT student_uid FROM group_assignments WHERE group_id=?", (group_id,))
    group_uids = {r[0] for r in cursor.fetchall()}
    if items:
        item_ids = [it[0] for it in items]
        placeholders = ",".join("?" * len(item_ids))
        cursor.execute(f"SELECT item_id, student_uid, score FROM grade_scores WHERE item_id IN ({placeholders})", item_ids)
        score_map = {(r[0], r[1]): r[2] for r in cursor.fetchall()}
    else:
        score_map = {}
    conn.close()

    students = [s for s in get_sorted_master_students() if s['uid'] in group_uids]
    uq = urllib.parse.quote(user)

    visibility_labels = {"all": "🟢 นักเรียนดูคะแนนได้ทุกคน", "hidden": "🔒 นักเรียนยังดูคะแนนไม่ได้", "custom": "🟡 เปิดดูได้เฉพาะบางคน"}
    visibility_note = f"""
    <div class="card" style="background:#f8fafc;border:1px solid #e2e8f0;">
        <p style="margin:0;font-size:12.5px;color:#475569;">
            👁️ สถานะการดูคะแนนของนักเรียน: <b>{visibility_labels.get(visibility, visibility)}</b><br>
            <span style="color:#94a3b8;">การเปิด/ปิดให้นักเรียนดูคะแนนวิชานี้ ตั้งค่าได้ที่หน้าแอดมิน ➜ จัดการการมองเห็นคะแนน</span>
        </p>
    </div>"""

    # 📊 ตารางคะแนนแบบกรอกสด (คล้าย Excel) แยกหมวด: คะแนนเก็บ / กลางภาค / ปลายภาค
    # แต่ละช่องคือ <input> ตัวเลขที่ auto-save ทันทีตอนออกจากช่อง (blur) ผ่าน AJAX ทีละช่อง
    # ไม่ใช้ฟอร์มเดียวยิงทีเดียวทั้งตาราง เพื่อเลี่ยงปัญหาฟอร์มมี field เกิน 1000 ช่องตอนนักเรียน/รายการคะแนนเยอะ
    collect_items = [it for it in items if it[3] == "คะแนนเก็บ"]
    midterm_items = [it for it in items if it[3] == "กลางภาค"]
    final_items = [it for it in items if it[3] == "ปลายภาค"]
    collect_max_total = sum(it[2] for it in collect_items)
    midterm_max_total = sum(it[2] for it in midterm_items)
    final_max_total = sum(it[2] for it in final_items)

    def item_th(it):
        return f"""<th class="gr-th">
                <div style="display:flex;align-items:center;justify-content:center;gap:6px;">
                    <span>{it[1]}</span>
                    <a href="/app/grades/{group_id}/edit_item?item_id={it[0]}&user={uq}"
                       title="แก้ไขชื่อ/คะแนนเต็ม"
                       style="color:#2563eb;text-decoration:none;font-size:11px;font-weight:800;">✎</a>
                    <a href="/api/teacher/grades/delete_item?item_id={it[0]}&group_id={group_id}&user={uq}"
                       onclick="return confirm('ลบรายการคะแนนนี้? (ลบแล้วคะแนนของทุกคนในคอลัมน์นี้จะหายไปด้วย)')"
                       style="color:#f87171;text-decoration:none;font-size:11px;font-weight:800;">✕</a>
                </div>
                <a href="/app/grades/{group_id}/edit_item?item_id={it[0]}&user={uq}" style="text-decoration:none;">
                    <span style="font-weight:600;color:#94a3b8;font-size:10.5px;">เต็ม {it[2]:g} ✎</span>
                </a>
            </th>"""

    # แถวหัวตารางบรรทัดที่ 1 (หมวดใหญ่แบบ merge cell)
    top_header = '<th class="gr-th" rowspan="2" style="text-align:left;position:sticky;left:0;background:#f1f5f9;">นักเรียน</th>'
    if collect_items:
        top_header += f'<th class="gr-th" colspan="{len(collect_items)}">คะแนนเก็บ</th><th class="gr-th" rowspan="2">คะแนนเก็บเต็ม<br><span style="font-weight:600;color:#94a3b8;">{collect_max_total:g}</span></th>'
    if midterm_items:
        top_header += f'<th class="gr-th" colspan="{len(midterm_items)}">ผลสอบกลางภาค</th><th class="gr-th" rowspan="2">กลางภาคเต็ม<br><span style="font-weight:600;color:#94a3b8;">{midterm_max_total:g}</span></th>'
    if final_items:
        top_header += f'<th class="gr-th" colspan="{len(final_items)}">ผลสอบปลายภาค</th><th class="gr-th" rowspan="2">ปลายภาคเต็ม<br><span style="font-weight:600;color:#94a3b8;">{final_max_total:g}</span></th>'
    if collect_items:
        top_header += '<th class="gr-th" rowspan="2">ผลรวม<br>คะแนนเก็บ</th>'
    top_header += '<th class="gr-th" rowspan="2">ผลรวม<br>คะแนน</th>'

    sub_header = "".join(item_th(it) for it in collect_items) + "".join(item_th(it) for it in midterm_items) + "".join(item_th(it) for it in final_items)

    def make_cell(it, uid, css_class):
        item_id, item_name, max_score, category = it
        cur_score = score_map.get((item_id, uid))
        return f"""<td class="gr-td">
            <div class="gr-cell-wrap">
                <input type="number" step="0.5" min="0" max="{max_score:g}"
                       class="gr-input {css_class}" data-item-id="{item_id}" data-uid="{uid}" data-max="{max_score:g}"
                       value="{'' if cur_score is None else f'{cur_score:g}'}"
                       oninput="updateRowTotals(this)" onblur="saveGradeCell(this)">
                <span class="gr-max">/{max_score:g}</span>
            </div>
        </td>"""

    # จัดกลุ่มนักเรียนเป็นรายห้อง (ขึ้นเป็นรายห้องตามที่ต้องการ)
    students_by_class = {}
    for s in students:
        students_by_class.setdefault(s['class'], []).append(s)

    classroom_tables = ""
    for classroom, class_students in students_by_class.items():
        table_rows = ""
        for s in class_students:
            uid = s['uid']
            collect_cells = "".join(make_cell(it, uid, "gr-collect") for it in collect_items)
            midterm_cells = "".join(make_cell(it, uid, "gr-mid") for it in midterm_items)
            final_cells = "".join(make_cell(it, uid, "gr-final") for it in final_items)

            collect_got = sum(score_map.get((it[0], uid)) or 0 for it in collect_items)
            midterm_got = sum(score_map.get((it[0], uid)) or 0 for it in midterm_items)
            final_got = sum(score_map.get((it[0], uid)) or 0 for it in final_items)
            grand_got = collect_got + midterm_got + final_got

            extra_cells = ""
            if collect_items:
                extra_cells += f'<td class="gr-td gr-computed" data-row-sum="collect">{collect_got:g}/{collect_max_total:g}</td>'
            extra_cells += f'<td class="gr-td gr-computed" data-row-sum="grand">{grand_got:g}</td>'

            table_rows += f"""<tr data-uid="{uid}">
                <td class="gr-td" style="text-align:left;position:sticky;left:0;background:#fff;">
                    {s['name']}<br><span style="font-size:11px;color:#94a3b8;">เลขที่ {s['no']}</span>
                </td>{collect_cells}
                {f'<td class="gr-td gr-static">{collect_max_total:g}</td>' if collect_items else ''}
                {midterm_cells}
                {f'<td class="gr-td gr-static">{midterm_max_total:g}</td>' if midterm_items else ''}
                {final_cells}
                {f'<td class="gr-td gr-static">{final_max_total:g}</td>' if final_items else ''}
                {extra_cells}
            </tr>"""

        classroom_tables += f"""
        <div class="card" style="overflow-x:auto;">
            <h2>🏫 ห้อง {classroom} ({len(class_students)} คน)</h2>
            <table class="gr-table">
                <thead><tr>{top_header}</tr><tr>{sub_header}</tr></thead>
                <tbody>{table_rows if table_rows else "<tr><td style='color:#94a3b8;text-align:center;'>ไม่มีนักเรียนในห้องนี้</td></tr>"}</tbody>
            </table>
        </div>"""

    if not items:
        classroom_tables = "<div class='card'><p style='color:#94a3b8;text-align:center;padding:20px 0;'>ยังไม่มีรายการคะแนน — เพิ่มรายการด้านบนก่อน แล้วตารางกรอกคะแนนจะปรากฏที่นี่</p></div>"
    elif not students:
        classroom_tables = "<div class='card'><p style='color:#94a3b8;text-align:center;padding:20px 0;'>ยังไม่มีนักเรียนในกลุ่มนี้</p></div>"

    return f"""
    <html>{STYLE_HEADER}
    <style>
        .gr-table {{ border-collapse:collapse; width:100%; font-size:13px; }}
        .gr-table .gr-th, .gr-table .gr-td {{ border:1px solid #e2e8f0; padding:6px 4px; text-align:center; white-space:nowrap; }}
        .gr-table .gr-th {{ background:#f1f5f9; font-size:12px; color:#334155; }}
        .gr-cell-wrap {{ display:flex; align-items:center; justify-content:center; gap:2px; }}
        .gr-input {{ width:48px; border:1px solid #cbd5e1; border-radius:5px; padding:4px 2px; text-align:center; font-size:13px; }}
        .gr-input.gr-saved {{ border-color:#22c55e; background:#f0fdf4; }}
        .gr-input.gr-error {{ border-color:#ef4444; background:#fef2f2; }}
        .gr-max {{ font-size:11px; color:#94a3b8; font-weight:700; }}
        .gr-static {{ color:#64748b; font-weight:700; background:#f8fafc; }}
        .gr-computed {{ color:#1d4ed8; font-weight:800; background:#eff6ff; }}
    </style>
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> 📊 ผลการเรียน — {group_name}</h1>
            <a href="/app/classroom/{group_id}?user={uq}" class="btn btn-secondary">⬅ กลับ</a>
        </div>
        <div class="main-container">
            {visibility_note}
            <div class="card">
                <h2>➕ เพิ่มรายการคะแนน (คอลัมน์เดียว)</h2>
                <form action="/api/teacher/grades/add_item" method="post">
                    <input type="hidden" name="group_id" value="{group_id}">
                    <input type="hidden" name="user" value="{user}">
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">ชื่อรายการ:</label>
                    <input type="text" name="item_name" placeholder="เช่น ครั้งที่ 1, สอบกลางภาค" required>
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">คะแนนเต็ม:</label>
                    <input type="number" step="0.5" name="max_score" placeholder="เช่น 10" required>
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">หมวดหมู่:</label>
                    <select name="category">
                        <option value="คะแนนเก็บ">คะแนนเก็บ</option>
                        <option value="กลางภาค">กลางภาค</option>
                        <option value="ปลายภาค">ปลายภาค</option>
                    </select>
                    <button type="submit" class="btn-submit">💾 เพิ่มรายการ</button>
                </form>
            </div>

            <div class="card">
                <h2>⚡ เพิ่มหลายคอลัมน์พร้อมกัน (แบบเร็ว)</h2>
                <p style="font-size:12px;color:#64748b;margin:0 0 8px;">
                    พิมพ์เป็น <b>ชื่อ:คะแนนเต็ม</b> คั่นด้วยจุลภาค เช่น
                    <code>ครั้งที่1:10, ครั้งที่2:10, ครั้งที่3:10</code> (แล้วค่อยเพิ่ม "กลางภาค" กับ "ปลายภาค" แยกหมวดต่างหากด้านบน)
                </p>
                <form action="/api/teacher/grades/bulk_add_items" method="post">
                    <input type="hidden" name="group_id" value="{group_id}">
                    <input type="hidden" name="user" value="{user}">
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">รายการ (ชื่อ:คะแนนเต็ม, ...):</label>
                    <textarea name="items_bulk" rows="2" placeholder="เช่น ครั้งที่1:10, ครั้งที่2:10, ครั้งที่3:10" required style="width:100%;padding:10px;border:1px solid #cbd5e1;border-radius:8px;font-size:13.5px;"></textarea>
                    <label style="font-size:12.5px;font-weight:700;color:#475569;margin-top:8px;display:block;">หมวดหมู่ (ของทุกรายการที่พิมพ์):</label>
                    <select name="category">
                        <option value="คะแนนเก็บ">คะแนนเก็บ</option>
                        <option value="กลางภาค">กลางภาค</option>
                        <option value="ปลายภาค">ปลายภาค</option>
                    </select>
                    <button type="submit" class="btn-submit">⚡ เพิ่มทั้งหมด</button>
                </form>
            </div>

            <div class="card" style="background:#eff6ff;border:1px solid #bfdbfe;">
                <p style="margin:0;font-size:12.5px;color:#1e40af;">
                    💡 กรอกคะแนนในตารางด้านล่างได้เหมือน Excel เลย — พิมพ์ตัวเลขแล้วกด Tab/Enter หรือคลิกออกจากช่อง ระบบจะคำนวณ "ผลรวมคะแนนเก็บ" กับ "ผลรวมคะแนน" ให้ทันที แล้วบันทึกอัตโนมัติ (ช่องจะขึ้นกรอบเขียวเมื่อบันทึกสำเร็จ)
                </p>
            </div>

            {classroom_tables}
        </div>
        <script>
        function updateRowTotals(input) {{
            const tr = input.closest('tr');
            if (!tr) return;
            const sum = (sel) => Array.from(tr.querySelectorAll(sel)).reduce((acc, el) => acc + (parseFloat(el.value) || 0), 0);
            const collectGot = sum('.gr-collect');
            const midGot = sum('.gr-mid');
            const finalGot = sum('.gr-final');
            const grand = collectGot + midGot + finalGot;

            const collectCell = tr.querySelector('[data-row-sum="collect"]');
            if (collectCell) {{
                const maxTxt = collectCell.textContent.split('/')[1] || '0';
                collectCell.textContent = (Math.round(collectGot * 100) / 100) + '/' + maxTxt;
            }}
            const grandCell = tr.querySelector('[data-row-sum="grand"]');
            if (grandCell) {{
                grandCell.textContent = (Math.round(grand * 100) / 100);
            }}
        }}

        async function saveGradeCell(input) {{
            const itemId = input.dataset.itemId;
            const uid = input.dataset.uid;
            const maxVal = parseFloat(input.dataset.max);
            let val = input.value.trim();

            if (val !== "" && parseFloat(val) > maxVal) {{
                input.classList.remove('gr-saved');
                input.classList.add('gr-error');
                alert('คะแนนที่กรอก (' + val + ') เกินคะแนนเต็ม (' + maxVal + ')');
                return;
            }}

            const body = new URLSearchParams();
            body.set('group_id', '{group_id}');
            body.set('user', '{user}');
            body.set('item_id', itemId);
            body.set('student_uid', uid);
            body.set('score', val);

            try {{
                const res = await fetch('/api/teacher/grades/ajax_set_score', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                    body: body.toString()
                }});
                const data = await res.json();
                if (data.ok) {{
                    input.classList.remove('gr-error');
                    input.classList.add('gr-saved');
                    setTimeout(() => input.classList.remove('gr-saved'), 1200);
                }} else {{
                    input.classList.add('gr-error');
                }}
            }} catch (e) {{
                input.classList.add('gr-error');
            }}
        }}
        </script>
    </body></html>
    """


@app.post("/api/teacher/grades/add_item")
async def api_grades_add_item(group_id: int = Form(...), user: str = Form(...), item_name: str = Form(...),
                               max_score: float = Form(...), category: str = Form("คะแนนเก็บ"), user_session: Optional[str] = Cookie(None)):
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT teacher_username FROM course_groups WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    if not row or row[0] != user:
        conn.close()
        return alert_redirect("ไม่มีสิทธิ์", type="error", url=f"/app/dashboard?user={urllib.parse.quote(user)}")
    cursor.execute("INSERT INTO grade_items (group_id, item_name, max_score, category, created_by, created_at) VALUES (?,?,?,?,?,?)",
                   (group_id, item_name.strip(), max_score, category, user, datetime.now().strftime("%d/%m/%Y %H:%M")))
    conn.commit()
    conn.close()
    return alert_redirect("เพิ่มรายการคะแนนเรียบร้อยแล้ว", type="success", url=f"/app/grades/{group_id}?user={urllib.parse.quote(user)}")

@app.get("/app/grades/{group_id}/edit_item", response_class=HTMLResponse)
async def app_grades_edit_item_page(group_id: int, item_id: int, user: str, user_session: Optional[str] = Cookie(None)):
    """✎ หน้าแก้ไขรายการคะแนนที่มีอยู่แล้ว — เปลี่ยนชื่อ / คะแนนเต็ม / หมวดหมู่ได้อิสระ ไม่ล็อกไว้ที่ค่าใดค่าหนึ่ง"""
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return RedirectResponse(url="/login", status_code=303)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT teacher_username FROM course_groups WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    if not row or row[0] != user:
        conn.close()
        return alert_redirect("ไม่มีสิทธิ์เข้าถึง", type="error", url=f"/app/dashboard?user={urllib.parse.quote(user)}")
    cursor.execute("SELECT item_id, item_name, max_score, category FROM grade_items WHERE item_id=? AND group_id=?", (item_id, group_id))
    it = cursor.fetchone()
    if not it:
        conn.close()
        return alert_redirect("ไม่พบรายการคะแนนนี้", type="error", url=f"/app/grades/{group_id}?user={urllib.parse.quote(user)}")
    # 🔎 หาคะแนนสูงสุดที่นักเรียนคนใดคนหนึ่งกรอกไว้แล้วในรายการนี้ (เตือนถ้าตั้งคะแนนเต็มใหม่ต่ำกว่านี้)
    cursor.execute("SELECT MAX(score) FROM grade_scores WHERE item_id=?", (item_id,))
    highest_entered = cursor.fetchone()[0]
    conn.close()

    _, item_name, max_score, category = it
    uq = urllib.parse.quote(user)
    warn_html = ""
    if highest_entered is not None:
        warn_html = f"""<div class="card" style="background:#fffbeb;border:1px solid #fde68a;">
            <p style="margin:0;font-size:12.5px;color:#92400e;">
                ⚠️ ตอนนี้มีนักเรียนที่ได้คะแนนสูงสุด <b>{highest_entered:g}</b> ในรายการนี้แล้ว —
                ถ้าตั้งคะแนนเต็มใหม่ให้ต่ำกว่านี้ ระบบจะปรับลดคะแนนที่เกินให้เท่ากับคะแนนเต็มใหม่โดยอัตโนมัติ
            </p>
        </div>"""

    category_options = "".join([
        f'<option value="{c}" {"selected" if c == category else ""}>{c}</option>'
        for c in ["คะแนนเก็บ", "กลางภาค", "ปลายภาค"]
    ])

    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> ✎ แก้ไขรายการคะแนน</h1>
            <a href="/app/grades/{group_id}?user={uq}" class="btn btn-secondary">⬅ กลับ</a>
        </div>
        <div class="main-container">
            {warn_html}
            <div class="card">
                <h2>✎ {item_name}</h2>
                <form action="/api/teacher/grades/edit_item" method="post">
                    <input type="hidden" name="group_id" value="{group_id}">
                    <input type="hidden" name="user" value="{user}">
                    <input type="hidden" name="item_id" value="{item_id}">
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">ชื่อรายการ:</label>
                    <input type="text" name="item_name" value="{item_name}" required>
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">คะแนนเต็ม (ตั้งได้ตามต้องการ ไม่จำกัดค่า):</label>
                    <input type="number" step="0.5" min="0.5" name="max_score" value="{max_score:g}" required>
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">หมวดหมู่:</label>
                    <select name="category">{category_options}</select>
                    <button type="submit" class="btn-submit">💾 บันทึกการแก้ไข</button>
                </form>
            </div>
        </div>
    </body></html>
    """

@app.post("/api/teacher/grades/edit_item")
async def api_grades_edit_item(group_id: int = Form(...), user: str = Form(...), item_id: int = Form(...),
                                item_name: str = Form(...), max_score: float = Form(...),
                                category: str = Form("คะแนนเก็บ"), user_session: Optional[str] = Cookie(None)):
    """✎ แก้ไขชื่อ/คะแนนเต็ม/หมวดหมู่ของรายการคะแนนที่มีอยู่แล้ว — ครูปรับคะแนนเต็มใหม่ได้อิสระ ไม่ตายตัว"""
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return HTMLResponse("Unauthorized", status_code=401)
    item_name = item_name.strip()
    if not item_name:
        return alert_redirect("กรุณาระบุชื่อรายการ", type="error", url=f"/app/grades/{group_id}?user={urllib.parse.quote(user)}")
    if max_score <= 0:
        return alert_redirect("คะแนนเต็มต้องมากกว่า 0", type="error", url=f"/app/grades/{group_id}?user={urllib.parse.quote(user)}")

    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT teacher_username FROM course_groups WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    if not row or row[0] != user:
        conn.close()
        return alert_redirect("ไม่มีสิทธิ์", type="error", url=f"/app/dashboard?user={urllib.parse.quote(user)}")
    cursor.execute("SELECT item_id FROM grade_items WHERE item_id=? AND group_id=?", (item_id, group_id))
    if not cursor.fetchone():
        conn.close()
        return alert_redirect("ไม่พบรายการคะแนนนี้", type="error", url=f"/app/grades/{group_id}?user={urllib.parse.quote(user)}")

    # 🧮 ถ้าคะแนนเต็มใหม่ต่ำกว่าคะแนนที่นักเรียนบางคนได้ไปแล้ว ให้ปรับลดคะแนนส่วนเกินลงมาเท่ากับคะแนนเต็มใหม่ (กันคะแนนเกินเต็ม)
    cursor.execute("UPDATE grade_scores SET score=? WHERE item_id=? AND score>?", (max_score, item_id, max_score))
    clamped = cursor.rowcount

    cursor.execute("UPDATE grade_items SET item_name=?, max_score=?, category=? WHERE item_id=? AND group_id=?",
                   (item_name, max_score, category, item_id, group_id))
    conn.commit()
    conn.close()

    msg = f"แก้ไขรายการคะแนนเรียบร้อยแล้ว (คะแนนเต็มใหม่: {max_score:g})"
    if clamped:
        msg += f" — ปรับลดคะแนนของนักเรียน {clamped} คนที่เกินคะแนนเต็มใหม่ให้แล้ว"
    return alert_redirect(msg, type="success", url=f"/app/grades/{group_id}?user={urllib.parse.quote(user)}")

@app.post("/api/teacher/grades/set_score")
async def api_grades_set_score(group_id: int = Form(...), user: str = Form(...), item_id: int = Form(...),
                                student_uid: str = Form(...), score: float = Form(...), user_session: Optional[str] = Cookie(None)):
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT teacher_username FROM course_groups WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    if not row or row[0] != user:
        conn.close()
        return alert_redirect("ไม่มีสิทธิ์", type="error", url=f"/app/dashboard?user={urllib.parse.quote(user)}")
    cursor.execute("""INSERT INTO grade_scores (item_id, student_uid, score) VALUES (?,?,?)
        ON CONFLICT(item_id, student_uid) DO UPDATE SET score=excluded.score""", (item_id, student_uid, score))
    conn.commit()
    conn.close()
    return alert_redirect("บันทึกคะแนนเรียบร้อยแล้ว", type="success", url=f"/app/grades/{group_id}?user={urllib.parse.quote(user)}")

@app.post("/api/teacher/grades/bulk_add_items")
async def api_grades_bulk_add_items(group_id: int = Form(...), user: str = Form(...), items_bulk: str = Form(...),
                                     category: str = Form("คะแนนเก็บ"), user_session: Optional[str] = Cookie(None)):
    """⚡ เพิ่มรายการคะแนนหลายคอลัมน์พร้อมกัน เช่น 'ครั้งที่1:10, ครั้งที่2:10, กลางภาค:30/30' """
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT teacher_username FROM course_groups WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    if not row or row[0] != user:
        conn.close()
        return alert_redirect("ไม่มีสิทธิ์", type="error", url=f"/app/dashboard?user={urllib.parse.quote(user)}")

    added = 0
    skipped = []
    created_at = datetime.now().strftime("%d/%m/%Y %H:%M")
    for chunk in items_bulk.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ":" not in chunk:
            skipped.append(chunk)
            continue
        name_part, score_part = chunk.rsplit(":", 1)
        name_part = name_part.strip()
        score_part = score_part.strip()
        # รองรับทั้ง "10" และ "30/30" (เอาตัวเลขหลัง / เป็นคะแนนเต็ม)
        if "/" in score_part:
            score_part = score_part.split("/")[-1].strip()
        try:
            max_score = float(score_part)
        except ValueError:
            skipped.append(chunk)
            continue
        if not name_part or max_score <= 0:
            skipped.append(chunk)
            continue
        cursor.execute("INSERT INTO grade_items (group_id, item_name, max_score, category, created_by, created_at) VALUES (?,?,?,?,?,?)",
                       (group_id, name_part, max_score, category, user, created_at))
        added += 1
    conn.commit()
    conn.close()

    if added and not skipped:
        return alert_redirect(f"เพิ่มรายการคะแนนสำเร็จ {added} รายการ", type="success", url=f"/app/grades/{group_id}?user={urllib.parse.quote(user)}")
    elif added and skipped:
        return alert_redirect(f"เพิ่มสำเร็จ {added} รายการ (ข้าม {len(skipped)} รายการที่รูปแบบไม่ถูกต้อง)", type="warning", url=f"/app/grades/{group_id}?user={urllib.parse.quote(user)}")
    else:
        return alert_redirect("ไม่พบรายการที่ถูกต้อง กรุณาใช้รูปแบบ 'ชื่อ:คะแนนเต็ม' คั่นด้วยจุลภาค", type="error", url=f"/app/grades/{group_id}?user={urllib.parse.quote(user)}")

@app.post("/api/teacher/grades/ajax_set_score")
async def api_grades_ajax_set_score(group_id: int = Form(...), user: str = Form(...), item_id: int = Form(...),
                                     student_uid: str = Form(...), score: str = Form(""), user_session: Optional[str] = Cookie(None)):
    """✏️ บันทึกคะแนนทีละช่องแบบ AJAX (ใช้กับตารางกรอกคะแนนสไตล์ Excel) — คืนค่าเป็น JSON เสมอ"""
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT teacher_username FROM course_groups WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    if not row or row[0] != user:
        conn.close()
        return JSONResponse({"ok": False, "error": "forbidden"}, status_code=403)

    score = score.strip()
    if score == "":
        # ✅ เคลียร์ช่องคะแนน (ลบแถวคะแนนของนักเรียนคนนี้ในรายการนี้)
        cursor.execute("DELETE FROM grade_scores WHERE item_id=? AND student_uid=?", (item_id, student_uid))
        conn.commit()
        conn.close()
        return JSONResponse({"ok": True, "cleared": True})

    try:
        score_val = float(score)
    except ValueError:
        conn.close()
        return JSONResponse({"ok": False, "error": "invalid_score"}, status_code=400)

    cursor.execute("SELECT max_score FROM grade_items WHERE item_id=? AND group_id=?", (item_id, group_id))
    item_row = cursor.fetchone()
    if not item_row:
        conn.close()
        return JSONResponse({"ok": False, "error": "item_not_found"}, status_code=404)
    if score_val < 0 or score_val > item_row[0]:
        conn.close()
        return JSONResponse({"ok": False, "error": "out_of_range"}, status_code=400)

    cursor.execute("""INSERT INTO grade_scores (item_id, student_uid, score) VALUES (?,?,?)
        ON CONFLICT(item_id, student_uid) DO UPDATE SET score=excluded.score""", (item_id, student_uid, score_val))
    conn.commit()
    conn.close()
    return JSONResponse({"ok": True, "score": score_val})

@app.get("/api/teacher/grades/delete_item")
async def api_grades_delete_item(item_id: int, group_id: int, user: str, user_session: Optional[str] = Cookie(None)):
    if not user_session or user_session != f"teacher_{urllib.parse.quote(user)}":
        return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT teacher_username FROM course_groups WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    if not row or row[0] != user:
        conn.close()
        return alert_redirect("ไม่มีสิทธิ์", type="error", url=f"/app/dashboard?user={urllib.parse.quote(user)}")
    cursor.execute("DELETE FROM grade_scores WHERE item_id=?", (item_id,))
    cursor.execute("DELETE FROM grade_items WHERE item_id=? AND group_id=?", (item_id, group_id))
    conn.commit()
    conn.close()
    return alert_redirect("ลบรายการคะแนนเรียบร้อยแล้ว", type="success", url=f"/app/grades/{group_id}?user={urllib.parse.quote(user)}")

@app.get("/student/grades", response_class=HTMLResponse)
async def student_grades(user_session: Optional[str] = Cookie(None)):
    if not user_session or not user_session.startswith("student_"):
        return RedirectResponse(url="/login", status_code=303)
    uid = urllib.parse.unquote(user_session.replace("student_", "", 1))
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT g.group_id, g.group_name, g.grades_visibility FROM course_groups g
        WHERE g.group_id IN (SELECT group_id FROM group_assignments WHERE student_uid=?)""", (uid,))
    my_groups = cursor.fetchall()

    rows_html = ""
    for g_id, g_name, visibility in my_groups:
        visibility = visibility or "hidden"
        can_view = visibility == "all"
        if visibility == "custom":
            cursor.execute("SELECT 1 FROM grade_visible_students WHERE group_id=? AND student_uid=?", (g_id, uid))
            can_view = cursor.fetchone() is not None

        if not can_view:
            rows_html += f"""<tr>
                <td style="text-align:left;">📘 {g_name}</td>
                <td colspan="3" style="color:#94a3b8;font-size:12px;">🔒 ยังไม่เปิดให้ดูคะแนน</td>
            </tr>"""
            continue

        cursor.execute("""SELECT gi.item_id, gi.max_score, gi.category, gs.score
            FROM grade_items gi
            LEFT JOIN grade_scores gs ON gs.item_id = gi.item_id AND gs.student_uid = ?
            WHERE gi.group_id = ?""", (uid, g_id))
        items = cursor.fetchall()

        collect_got = sum(sc or 0 for _, mx, cat, sc in items if cat == "คะแนนเก็บ")
        collect_max = sum(mx for _, mx, cat, sc in items if cat == "คะแนนเก็บ")
        mid_got = sum(sc or 0 for _, mx, cat, sc in items if cat == "กลางภาค")
        mid_max = sum(mx for _, mx, cat, sc in items if cat == "กลางภาค")
        final_got = sum(sc or 0 for _, mx, cat, sc in items if cat == "ปลายภาค")
        final_max = sum(mx for _, mx, cat, sc in items if cat == "ปลายภาค")
        grand_got = collect_got + mid_got + final_got
        grand_max = collect_max + mid_max + final_max

        final_col = f"""<td>{final_got:g}/{final_max:g}</td>""" if final_max else ""
        rows_html += f"""<tr>
            <td style="text-align:left;">📘 {g_name}</td>
            <td>{collect_got:g}/{collect_max:g}</td>
            <td>{mid_got:g}/{mid_max:g}</td>
            {final_col}
            <td style="font-weight:800;color:#2563eb;">{grand_got:g}/{grand_max:g}</td>
        </tr>"""
    conn.close()

    return f"""
    <html>{STYLE_HEADER}
    <style>
        .my-grades-table {{ border-collapse:collapse; width:100%; font-size:13px; }}
        .my-grades-table th, .my-grades-table td {{ border:1px solid #e2e8f0; padding:10px 8px; text-align:center; }}
        .my-grades-table th {{ background:#f1f5f9; color:#334155; font-size:12px; }}
    </style>
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> 📊 ผลการเรียนของฉัน</h1>
            <a href="/student/dashboard" class="btn btn-secondary">⬅ กลับ</a>
        </div>
        <div class="main-container">
            <div class="card" style="overflow-x:auto;">
                <table class="my-grades-table">
                    <thead><tr>
                        <th style="text-align:left;">วิชา</th>
                        <th>คะแนนเก็บ</th>
                        <th>กลางภาค</th>
                        <th>รวมทั้งหมด</th>
                    </tr></thead>
                    <tbody>{rows_html if rows_html else "<tr><td colspan='4' style='color:#94a3b8;text-align:center;'>ยังไม่มีข้อมูลผลการเรียน</td></tr>"}</tbody>
                </table>
            </div>
        </div>
    </body></html>
    """

# ---------- 💳 ชำระเงิน (แอดมินบันทึกรายการ/สถานะ / นักเรียนดูยอด) ----------
@app.get("/admin/payments", response_class=HTMLResponse)
async def admin_payments_page(user_session: Optional[str] = Cookie(None)):
    if user_session != "admin":
        return RedirectResponse(url="/login", status_code=303)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT payment_id, student_uid, item_name, amount, status, due_date FROM payments ORDER BY payment_id DESC")
    rows = cursor.fetchall()
    conn.close()

    students = get_sorted_master_students()
    student_map = {s['uid']: s for s in students}
    student_options = "".join([f'<option value="{s["uid"]}">{s["name"]} ({s["class"]} เลขที่ {s["no"]})</option>' for s in students])

    cards = ""
    for p_id, uid, item_name, amount, status, due_date in rows:
        s = student_map.get(uid, {"name": uid, "class": "-", "no": "-"})
        is_paid = status == "paid"
        cards += f"""
        <div class="card" style="margin-bottom:10px; border-left:4px solid {'#15803d' if is_paid else '#b91c1c'};">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <div style="font-weight:800;font-size:14px;">{item_name}</div>
                    <div style="font-size:12px;color:#64748b;">{s['name']} · {s['class']} เลขที่ {s['no']}</div>
                </div>
                <span style="font-weight:800;color:{'#15803d' if is_paid else '#b91c1c'};font-size:12.5px;white-space:nowrap;">{'✅ ชำระแล้ว' if is_paid else '⏳ ยังไม่ชำระ'}</span>
            </div>
            <div style="font-size:13px;margin:8px 0;">💰 {amount:g} บาท · กำหนดชำระ: {due_date or 'ไม่ระบุ'}</div>
            <div style="display:flex;gap:6px;">
                <a href="/api/admin/payment/toggle?payment_id={p_id}" class="btn btn-secondary" style="padding:5px 10px;font-size:11px;">{'↩️ ยกเลิกชำระ' if is_paid else '✅ บันทึกว่าชำระแล้ว'}</a>
                <a href="/api/admin/payment/delete?payment_id={p_id}" class="btn btn-danger" style="padding:5px 10px;font-size:11px;" onclick="return confirm('ลบรายการนี้?')">🗑️ ลบ</a>
            </div>
        </div>"""

    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> 💳 ชำระเงิน</h1>
            <a href="/admin/dashboard" class="btn btn-secondary">⬅ กลับหน้าควบคุม</a>
        </div>
        <div class="main-container">
            <div class="card">
                <h2>➕ เพิ่มรายการเรียกเก็บเงิน</h2>
                <form action="/api/admin/payment/add" method="post">
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">นักเรียน:</label>
                    <select name="student_uid" required>{student_options}</select>
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">รายการ:</label>
                    <input type="text" name="item_name" placeholder="เช่น ค่าเทอม 1/2569" required>
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">จำนวนเงิน (บาท):</label>
                    <input type="number" step="0.01" name="amount" required>
                    <label style="font-size:12.5px;font-weight:700;color:#475569;">กำหนดชำระ:</label>
                    <input type="date" name="due_date">
                    <button type="submit" class="btn-submit">💾 เพิ่มรายการ</button>
                </form>
            </div>
            <div class="card"><h2 style="margin:0;">📋 รายการทั้งหมด ({len(rows)})</h2></div>
            {cards if cards else "<p style='color:#94a3b8;text-align:center;padding:20px 0;'>ยังไม่มีรายการ</p>"}
        </div>
    </body></html>
    """

@app.post("/api/admin/payment/add")
async def api_payment_add(student_uid: str = Form(...), item_name: str = Form(...), amount: float = Form(...),
                           due_date: str = Form(""), user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO payments (student_uid, item_name, amount, status, due_date, recorded_by, created_at) VALUES (?,?,?,?,?,?,?)",
                   (student_uid, item_name.strip(), amount, "unpaid", due_date, "admin", datetime.now().strftime("%d/%m/%Y %H:%M")))
    conn.commit()
    conn.close()
    return alert_redirect("เพิ่มรายการเรียบร้อยแล้ว", type="success", url="/admin/payments")

@app.get("/api/admin/payment/toggle")
async def api_payment_toggle(payment_id: int, user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM payments WHERE payment_id=?", (payment_id,))
    row = cursor.fetchone()
    if row:
        new_status = "unpaid" if row[0] == "paid" else "paid"
        paid_at = datetime.now().strftime("%d/%m/%Y %H:%M") if new_status == "paid" else None
        cursor.execute("UPDATE payments SET status=?, paid_at=? WHERE payment_id=?", (new_status, paid_at, payment_id))
        conn.commit()
    conn.close()
    return RedirectResponse(url="/admin/payments", status_code=303)

@app.get("/api/admin/payment/delete")
async def api_payment_delete(payment_id: int, user_session: Optional[str] = Cookie(None)):
    if user_session != "admin": return HTMLResponse("Unauthorized", status_code=401)
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM payments WHERE payment_id=?", (payment_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/admin/payments", status_code=303)

@app.get("/student/payments", response_class=HTMLResponse)
async def student_payments(user_session: Optional[str] = Cookie(None)):
    if not user_session or not user_session.startswith("student_"):
        return RedirectResponse(url="/login", status_code=303)
    uid = urllib.parse.unquote(user_session.replace("student_", "", 1))
    conn = sqlite3.connect('attendance_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, amount, status, due_date, paid_at FROM payments WHERE student_uid=? ORDER BY payment_id DESC", (uid,))
    rows = cursor.fetchall()
    conn.close()

    total_unpaid = sum(r[1] for r in rows if r[2] != "paid")
    cards = ""
    for item_name, amount, status, due_date, paid_at in rows:
        is_paid = status == "paid"
        cards += f"""
        <div class="card" style="margin-bottom:10px;border-left:4px solid {'#15803d' if is_paid else '#b91c1c'};">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-weight:800;font-size:14px;">{item_name}</div>
                <span style="font-weight:800;color:{'#15803d' if is_paid else '#b91c1c'};font-size:12.5px;white-space:nowrap;">{'✅ ชำระแล้ว' if is_paid else '⏳ ยังไม่ชำระ'}</span>
            </div>
            <div style="font-size:13px;color:#475569;margin-top:6px;">💰 {amount:g} บาท</div>
            <div style="font-size:11.5px;color:#94a3b8;margin-top:4px;">{'ชำระเมื่อ ' + paid_at if is_paid and paid_at else 'กำหนดชำระ: ' + (due_date or 'ไม่ระบุ')}</div>
        </div>"""

    return f"""
    <html>{STYLE_HEADER}
    <body>
        <div class="navbar">
            <h1><img src="{LOGO_URL}" class="nav-logo"> 💳 การชำระเงินของฉัน</h1>
            <a href="/student/dashboard" class="btn btn-secondary">⬅ กลับ</a>
        </div>
        <div class="main-container">
            <div class="card" style="text-align:center;margin-bottom:14px;">
                <div style="font-size:13px;color:#64748b;">ยอดค้างชำระทั้งหมด</div>
                <div style="font-size:24px;font-weight:800;color:{'#15803d' if total_unpaid==0 else '#b91c1c'};">{total_unpaid:g} บาท</div>
            </div>
            {cards if cards else "<p style='color:#94a3b8;text-align:center;padding:20px 0;'>ยังไม่มีรายการชำระเงิน</p>"}
        </div>
    </body></html>
    """

# ==========================================
# 🚫 [404 NOT FOUND — K-Techinteractive Style]
# ==========================================
from fastapi import Request as _Request
from fastapi.exceptions import HTTPException as _HTTPException
from starlette.exceptions import HTTPException as _StarletteHTTPException

NOT_FOUND_PAGE = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>404 — K-Techinteractive</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=Noto+Sans+Thai:wght@400;600;700;800&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Inter','Noto Sans Thai',sans-serif;
    background: #0a0f1e;
    min-height: 100vh; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 24px; overflow: hidden;
    color: #e2e8f0;
  }
  /* animated background grid */
  body::before {
    content: ""; position: fixed; inset: 0;
    background-image:
      linear-gradient(rgba(96,165,250,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(96,165,250,0.04) 1px, transparent 1px);
    background-size: 48px 48px;
    animation: gridMove 20s linear infinite;
    pointer-events: none;
  }
  @keyframes gridMove { 0%{background-position:0 0} 100%{background-position:48px 48px} }
  /* glow blobs */
  .blob1,.blob2 {
    position: fixed; border-radius: 50%; filter: blur(80px); pointer-events:none; opacity: 0.35;
  }
  .blob1 { width:400px;height:400px; background:radial-gradient(circle,#1d4ed8,transparent); top:-80px; right:-80px; animation: float1 8s ease-in-out infinite; }
  .blob2 { width:300px;height:300px; background:radial-gradient(circle,#7c3aed,transparent); bottom:-60px; left:-60px; animation: float2 10s ease-in-out infinite; }
  @keyframes float1 { 0%,100%{transform:translate(0,0)} 50%{transform:translate(-30px,20px)} }
  @keyframes float2 { 0%,100%{transform:translate(0,0)} 50%{transform:translate(20px,-25px)} }

  .container {
    position: relative; text-align: center; z-index: 1;
    max-width: 480px; width: 100%;
  }

  /* Brand badge */
  .brand {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(12px); border-radius: 100px;
    padding: 6px 16px; font-size: 12px; font-weight: 700;
    color: rgba(255,255,255,0.6); letter-spacing: 1.5px; text-transform: uppercase;
    margin-bottom: 32px;
  }
  .brand-dot { width: 7px; height: 7px; background: #3b82f6; border-radius: 50%; animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(0.8)} }

  /* 404 number */
  .error-code {
    font-size: clamp(90px,22vw,140px); font-weight: 900; line-height: 0.9;
    background: linear-gradient(135deg,#60a5fa,#818cf8,#c084fc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; letter-spacing: -4px;
    filter: drop-shadow(0 0 40px rgba(96,165,250,0.4));
    animation: shimmer 3s ease-in-out infinite;
  }
  @keyframes shimmer {
    0%,100%{ filter: drop-shadow(0 0 30px rgba(96,165,250,0.3)); }
    50%{ filter: drop-shadow(0 0 60px rgba(129,140,248,0.6)); }
  }

  .divider {
    width: 60px; height: 3px; margin: 24px auto 24px;
    background: linear-gradient(90deg,#3b82f6,#8b5cf6);
    border-radius: 100px;
  }

  .title {
    font-size: 20px; font-weight: 800; color: #f1f5f9; margin-bottom: 10px;
  }
  .desc {
    font-size: 14px; color: #64748b; line-height: 1.7; margin-bottom: 10px;
  }
  .path-badge {
    display: inline-block; background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px; padding: 5px 14px;
    font-family: 'SF Mono','Fira Code',monospace; font-size: 13px;
    color: #94a3b8; margin-bottom: 32px; word-break: break-all;
  }

  .btn-group { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }
  .btn {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 12px 24px; border-radius: 12px; font-size: 14px; font-weight: 700;
    text-decoration: none; transition: transform .15s, box-shadow .15s;
    cursor: pointer; border: none;
  }
  .btn:active { transform: scale(0.96); }
  .btn-primary {
    background: linear-gradient(135deg,#2563eb,#4f46e5);
    color: #fff; box-shadow: 0 4px 20px rgba(37,99,235,0.4);
  }
  .btn-primary:hover { box-shadow: 0 6px 28px rgba(37,99,235,0.55); }
  .btn-ghost {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
    color: #94a3b8;
  }
  .btn-ghost:hover { background: rgba(255,255,255,0.1); color: #e2e8f0; }

  .footer-note {
    margin-top: 48px; font-size: 11px; color: #334155; letter-spacing: 0.5px;
  }
  .footer-note span { color: #3b82f6; font-weight: 700; }
</style>
</head>
<body>
<div class="blob1"></div>
<div class="blob2"></div>
<div class="container">
  <div class="brand">
    <div class="brand-dot"></div>
    K-TECHINTERACTIVE
  </div>
  <div class="error-code">404</div>
  <div class="divider"></div>
  <div class="title">ไม่พบการเรียกใช้ / ที่ไม่พบ</div>
  <div class="desc">หน้าที่คุณกำลังค้นหาอาจถูกย้าย ลบออก<br>หรือยังไม่ได้รับการพัฒนาในระบบนี้</div>
  <div class="path-badge" id="req-path">—</div>
  <div class="btn-group">
    <a href="/student/dashboard" class="btn btn-primary">
      <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>
      กลับหน้าหลัก
    </a>
    <button onclick="history.back()" class="btn btn-ghost">
      <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="15,18 9,12 15,6"/></svg>
      ย้อนกลับ
    </button>
  </div>
  <div class="footer-note">powered by <span>K-Techinteractive</span> · K-School Enterprise</div>
</div>
<script>
  // แสดง path ที่ผู้ใช้พยายามเข้าถึง
  document.getElementById('req-path').textContent = window.location.pathname + (window.location.search || '');
</script>
</body>
</html>"""

@app.exception_handler(404)
async def not_found_handler(request: _Request, exc: _StarletteHTTPException):
    return HTMLResponse(NOT_FOUND_PAGE, status_code=404)

@app.exception_handler(_StarletteHTTPException)
async def http_exception_handler(request: _Request, exc: _StarletteHTTPException):
    if exc.status_code == 404:
        return HTMLResponse(NOT_FOUND_PAGE, status_code=404)
    # สำหรับ error อื่นๆ แสดงหน้า error ทั่วไป
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="th"><head><meta charset="UTF-8"><title>เกิดข้อผิดพลาด {exc.status_code}</title>
<style>body{{background:#0a0f1e;color:#e2e8f0;font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center;padding:24px;}}.code{{font-size:80px;font-weight:900;color:#3b82f6;margin-bottom:16px;}}.msg{{color:#94a3b8;margin:8px 0 24px;}}.btn{{background:#2563eb;color:#fff;padding:10px 24px;border-radius:10px;text-decoration:none;font-weight:700;}}</style>
</head><body>
<div><div class="code">{exc.status_code}</div>
<h2 style="margin-bottom:8px;">เกิดข้อผิดพลาด</h2>
<p class="msg">{exc.detail}</p>
<a href="/" class="btn">กลับหน้าหลัก</a>
<p style="margin-top:40px;font-size:11px;color:#334155;">powered by <span style="color:#3b82f6;">K-Techinteractive</span></p>
</div></body></html>""", status_code=exc.status_code)


async def main():
    init_db()
    # กำหนดค่า uvicorn และรันเซิร์ฟเวอร์
    config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="warning")
    server = uvicorn.Server(config)
    
    # รัน FastAPI server ในลูปหลัก
    server_task = asyncio.create_task(server.serve())
    
    # ลองรัน Discord Bot ในลักษณะ Background Task
    token = 'MTUxMDQ4NDg2MDg0ODgzNjcxMA.GpTvdb.4Ho5L3eqtzpXvyXlhVEzBnpFMFaPSUv21NyPz0'
    if token:
        try:
            print("📡 [DISCORD BOT] กำลังพยายามเข้าสู่ระบบ...")
            await bot.start(token)
        except Exception as e:
            print(f"⚠️ [DISCORD BOT ERROR] ไม่สามารถเริ่มทำงานบ็อตดิสคอร์ดได้: {e}")
            print("🚀 [FastAPI SERVER] เว็บไซต์ยังคงรันตามปกติที่ Port 8080")
            await server_task
    else:
        print("⚠️ [DISCORD BOT WARNING] ไม่พบ Token เริ่มต้นเซิร์ฟเวอร์เว็บอย่างเดียว")
        await server_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 หยุดการทำงานของเซิร์ฟเวอร์เรียบร้อย")
