import os
import logging
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# .env फाइल से डेटा लोड करना
load_dotenv()

API_ID = int(os.getenv("API_ID")) if os.getenv("API_ID") else None
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID")) if os.getenv("OWNER_ID") else None

# एरर ट्रैकिंग के लिए लॉगिंग सेटअप
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

DB_FILE = "bot_database.db"

def init_db():
    """डेटाबेस और सभी ज़रूरी टेबल्स बनाना"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            chat_id INTEGER,
            user_id INTEGER,
            first_name TEXT,
            PRIMARY KEY (chat_id, user_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bot_admin_groups (
            chat_id INTEGER PRIMARY KEY,
            chat_title TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_member(chat_id, user_id, first_name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO members VALUES (?, ?, ?)', (chat_id, user_id, first_name))
    conn.commit()
    conn.close()

def get_members(chat_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, first_name FROM members WHERE chat_id = ?', (chat_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_admin_group(chat_id, chat_title):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO bot_admin_groups VALUES (?, ?)', (chat_id, chat_title))
    conn.commit()
    conn.close()

def remove_admin_group(chat_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM bot_admin_groups WHERE chat_id = ?', (chat_id,))
    conn.commit()
    conn.close()

def get_admin_groups():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT chat_id, chat_title FROM bot_admin_groups')
    rows = cursor.fetchall()
    conn.close()
    return rows

# बॉट क्लाइंट शुरू करना
app = Client("mention_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    """/start - यूजर और ओनर के लिए बटन के साथ वेलकम मैसेज"""
    user = message.from_user
    chat_type = message.chat.type.name
    bot_user = await client.get_me()
    add_url = f"https://t.me/{bot_user.username}?startgroup=true"

    if chat_type == "PRIVATE":
        if user.id == OWNER_ID:
            owner_welcome = (
                f"👋 **नमस्ते बॉस, आपका स्वागत है!**\n\n"
                f"⚙️ **ओनर पैनल्स एक्टिवेटेड:**\n"
                f"• ग्रुप लिस्ट देखने के लिए `/mygroups` लिखें।\n"
                f"• सभी ग्रुप्स में मैसेज भेजने के लिए `/broadcast [मैसेज]` लिखें।\n"
                f"• सभी कमांड्स जानने के लिए `/help` टाइप करें।"
            )
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("➕ Add Me To Your Group ➕", url=add_url)]])
            await message.reply_text(owner_welcome, reply_markup=keyboard, parse_mode="Markdown")
        else:
            user_welcome = (
                f"👋 **हेलो {user.first_name}!**\n\n"
                f"🤖 मैं एक शक्तिशाली **मेंशन बॉट (Mention Bot)** हूँ।\n\n"
                f"📌 **मैं आपकी क्या मदद कर सकता हूँ?**\n"
                f"• मुझे अपने टेलीग्राम ग्रुप में जोड़ें और एडमिन बनाएं।\n"
                f"• ग्रुप के पुराने मेंबर्स को लोड करने के लिए `@scrape` लिखें।\n"
                f"• ग्रुप में सभी को टैग करने के लिए सीधे `@all` या `@tagall` लिखें।\n"
                f"• पूरी जानकारी के लिए `/help` टाइप करें।"
            )
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("➕ Add Me To Your Group ➕", url=add_url)]])
            await message.reply_text(user_welcome, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.reply_text(f"🤖 **बॉट एक्टिव है!**", parse_mode="Markdown")

@app.on_message(filters.command("help"))
async def help_command(client, message):
    """/help - हेल्प मेनू और ओनर बटन"""
    user = message.from_user
    bot_user = await client.get_me()
    
    help_text = (
        f"📖 **बॉट हेल्प गाइड (Help Menu)**\n\n"
        f"👥 **ग्रुप टैगिंग शब्द:**\n"
        f"• `@scrape` - ग्रुप के सभी पुराने सदस्यों को एक क्लिक में लोड करने के लिए। (केवल एडमिन्स के लिए)\n"
        f"• `@all` या `@tagall` - ग्रुप के सभी सदस्यों को टैग करने के लिए। (केवल एडमिन्स के लिए)\n"
        f"• `@admin` या `@admins` - ग्रुप के सभी एडमिन्स को अलर्ट भेजने के लिए।\n\n"
        f"🤖 **सामान्य कमांड्स:**\n"
        f"• `/start` - बॉट शुरू करने के लिए।\n"
        f"• `/help` - हेल्प मैनुअल देखने के लिए।"
    )

    if user.id == OWNER_ID:
        help_text += (
            f"\n\n👑 **ओनर स्पेशल कमांड्स:**\n"
            f"• `/mygroups` - एडमिन ग्रुप्स की लिस्ट देखें।\n"
            f"• `/broadcast [मैसेज]` - सभी ग्रुप्स में मैसेज भेजें।"
        )

    buttons = []
    add_url = f"https://t.me/{bot_user.username}?startgroup=true"
    buttons.append([InlineKeyboardButton("➕ Add Me To Your Group ➕", url=add_url)])
    
    if OWNER_ID:
        owner_chat_url = f"tg://user?id={OWNER_ID}"
        buttons.append([InlineKeyboardButton("👨‍💻 Contact Owner", url=owner_chat_url)])
        
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(help_text, reply_markup=reply_markup, parse_mode="Markdown")

@app.on_message(filters.text)
async def handle_text_and_tags(client, message):
    """ग्रुप टेक्स्ट स्कैन करना, टैगिंग संभालना और प्राइवेट चैट में वार्निंग देना"""
    if not message.text:
        return

    chat_id = message.chat.id
    chat_type = message.chat.type  # Enum ऑब्जेक्ट सुरक्षित तरीके से लिया
    user = message.from_user
    
    # Anonymous admin या Channel post के केस में सुरक्षा चेक
    if not user:
        return

    message_text = message.text.strip().lower()

    is_scrape_trigger = message_text == "@scrape"
    is_tagall_trigger = message_text.startswith("@all") or message_text.startswith("@tagall")
    is_admin_trigger = message_text.startswith("@admin") or message_text.startswith("@admins")

    if is_scrape_trigger or is_tagall_trigger or is_admin_trigger:
        # 📌 सुरक्षा चेक: प्राइवेट चैट वार्निंग (Enum आधारित चेक)
        if chat_type == enums.ChatType.PRIVATE:
            await message.reply_text("❌ **कृपया इस कमांड का उपयोग केवल टेलीग्राम ग्रुप में करें!** Private चैट में टैगिंग काम नहीं करती है।")
            return

        # एडमिन वेरिफिकेशन चेक
        is_admin = False
        try:
            async for admin in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                if admin.user.id == user.id:
                    is_admin = True
                    break
        except Exception:
            await message.reply_text("⚠️ मुझे ग्रुप एडमिन परमिशन दें ताकि मैं फीचर्स चला सकूँ।")
            return

        # 1. @scrape - पुराने मेंबर्स लोड करने का मैजिक फीचर
        if is_scrape_trigger:
            if not is_admin and user.id != OWNER_ID:
                await message.reply_text("❌ यह कमांड सिर्फ ग्रुप एडमिन्स के लिए है!")
                return

            status_msg = await message.reply_text("⏳ ग्रुप के सभी पुराने मेंबर्स की लिस्ट निकाली जा रही है, कृपया प्रतीक्षा करें...")
            count = 0
            try:
                async for member in client.get_chat_members(chat_id):
                    if member.user and not member.user.is_bot:
                        save_member(chat_id, member.user.id, member.user.first_name)
                        count += 1
                await status_msg.edit_text(f"✅ **सफलतापूर्वक लोड पूरा हुआ!**\n\n🎯 कुल `{count}` पुराने और नए मेंबर्स को डेटाबेस में सेव कर लिया गया है। अब आप `@all` कमांड का उपयोग कर सकते हैं।")
            except Exception as e:
                await status_msg.edit_text(f"⚠️ एरर आई: {e}\n(सुनिश्चित करें कि बॉट एडमिन है और उसके पास मेंबर्स देखने की परमिशन है।)")

        # 2. @all या @tagall प्रोसेसिंग
        elif is_tagall_trigger:
            if not is_admin and user.id != OWNER_ID:
                await message.reply_text("❌ सिर्फ ग्रुप एडमिन्स ही सबको टैग कर सकते हैं!")
                return

            saved_members = get_members(chat_id)
            if not saved_members:
                await message.reply_text("⚠️ डेटाबेस खाली है। पहले `@scrape` लिखकर पुराने मेंबर्स लोड करें।")
                return

            orig_text = message.text.strip()
            user_msg = orig_text.replace("@all", "").replace("@TAGALL", "").replace("@tagall", "").replace("@ALL", "").strip()
            base_text = f"📢 **अटेंशन प्लीज!**\n{user_msg}\n\n" if user_msg else "📢 **अटेंशन प्लीज!**\n\n"
            
            current_text = base_text
            msg_count = 0
            for u_id, f_name in saved_members:
                safe_name = f_name.replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                current_text += f"[{safe_name}](tg://user?id={u_id}) "
                msg_count += 1
                if msg_count >= 40:  # 40 मेंबर्स के बाद नया मैसेज भेजना
                    await client.send_message(chat_id=chat_id, text=current_text, parse_mode=enums.ParseMode.MARKDOWN)
                    current_text = base_text # बेस टेक्स्ट को रीसेट पर भी बनाए रखें ताकि संदर्भ न खोए
                    msg_count = 0
            if current_text and current_text != base_text:
                await client.send_message(chat_id=chat_id, text=current_text, parse_mode=enums.ParseMode.MARKDOWN)

        # 3. @admin या @admins प्रोसेसिंग
        elif is_admin_trigger:
            try:
                orig_text = message.text.strip()
                user_msg = orig_text
                for kw in ["@admin", "@admins", "@ADMIN", "@ADMINS"]:
                    user_msg = user_msg.replace(kw, "")
                user_msg = user_msg.strip()

                text = f"⚠️ **एडमिन अलर्ट!**\n{user_msg}\n\n" if user_msg else "⚠️ **ग्रुप एडमिन्स ध्यान दें:**\n\n"
                async for admin in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                    if admin.user and not admin.user.is_bot:
                        safe_name = admin.user.first_name.replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                        text += f"[{safe_name}](tg://user?id={admin.user.id}) "
                await message.reply_text(text, parse_mode=enums.ParseMode.MARKDOWN)
            except Exception as e:
                logger.error(f"Error in tag_admins: {e}")

    # सामान्य मैसेज आने पर ग्रुप यूजर को डेटाबेस में ऑटो-सेव करना (Enum का सही उपयोग)
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP] and not user.is_bot:
        save_member(chat_id, user.id, user.first_name)
        

@app.on_message(filters.new_chat_members)
async def welcome_and_bot_add(client, message):
    """ग्रुप में नया मेंबर आने पर वेलकम OR बॉट खुद ऐड हो तो थैंक्स बटन"""
    chat_id = message.chat.id
    chat_title = message.chat.title
    bot_user = await client.get_me()
    
    for new_member in message.new_chat_members:
        if new_member.id == bot_user.id:
            thanks_text = (
                f"💖 **थैंक्यू मुझे इस ग्रुप में ऐड करने के लिए!**\n\n"
                f"🤖 मैं इस ग्रुप के सभी मेंबर्स को टैग करने में आपकी मदद करूँगा।\n\n"
                f"⚙️ **महत्वपूर्ण:** कृपया मुझे ग्रुप में **Admin** बनाएं ताकि पुराने मेंबर्स को लोड करने के लिए `@scrape` कमांड काम कर सके!"
            )
            add_url = f"https://t.me/{bot_user.username}?startgroup=true"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("➕ Add Me To Your Group ➕", url=add_url)]])
            await message.reply_text(thanks_text, reply_markup=keyboard, parse_mode="Markdown")
            return

        if not new_member.is_bot:
            save_member(chat_id, new_member.id, new_member.first_name)
            welcome_text = (
                f"🎉 **ग्रुप में आपका स्वागत है, [{new_member.first_name}](tg://user?id={new_member.id})!**\n\n"
                f"🤖 *मदद के लिए ग्रुप में `/help` टाइप करें या सीधे `@all` लिखकर सबको टैग करें।*"
            )
            await message.reply_text(welcome_text, parse_mode="Markdown")

# --- ओनर एक्सक्लूसिव कमांड्स और ट्रैकर्स ---

@app.on_chat_member_updated()
async def track_bot_status(client, update):
    """ट्रैक करना कि बॉट कहाँ एडमिन बना या हटा"""
    if not update.new_chat_member or update.new_chat_member.user.id != (await client.get_me()).id:
        return
    chat_id = update.chat.id
    chat_title = update.chat.title
    new_status = update.new_chat_member.status.name

    if new_status in ["ADMINISTRATOR", "OWNER"]:
        add_admin_group(chat_id, chat_title)
    else:
        remove_admin_group(chat_id)

@app.on_message(filters.command("mygroups"))
async def list_my_groups(client, message):
    """/mygroups - ओनर ग्रुप लिस्ट"""
    if message.from_user.id != OWNER_ID:
        await message.reply_text("❌ आप ओनर नहीं हैं।")
        return
    admin_groups = get_admin_groups()
    if not admin_groups:
        await update.message.reply_text("📁 बॉट अभी कहीं भी एडमिन नहीं है।")
        return
    response = "📋 **बॉस, मैं इन सभी ग्रुप्स में एडमिन हूँ:**\n\n"
    for c_id, title in admin_groups:
        response += f"🔹 **{title}** (ID: `{c_id}`)\n"
    await message.reply_text(response, parse_mode="Markdown")

@app.on_message(filters.command("broadcast"))
async def broadcast_command(client, message):
    """/broadcast - ओनर ब्रॉडकास्ट"""
    if message.from_user.id != OWNER_ID:
        return
    broadcast_msg = " ".join(message.command[1:])
    if not broadcast_msg:
        await message.reply_text("⚠️ कृपया मैसेज लिखें।")
        return
    admin_groups = get_admin_groups()
    success_count = 0
    for chat_id, title in admin_groups:
        try:
            await client.send_message(chat_id=chat_id, text=f"📢 **बॉट ओनर की सूचना:**\n\n{broadcast_msg}")
            success_count += 1
        except Exception:
            pass
    await message.reply_text(f"✅ ब्रॉडकास्ट पूरा हुआ! सफल: {success_count} ग्रुप्स।")

if __name__ == "__main__":
    init_db()
    print("🤖 ऑल-इन-वन एडवांस मेंशन बॉट चालू हो गया है...")
    app.run()
          
