import asyncio
import aiohttp
import config
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters

# استدعاء بياناتك من ملف الإعدادات
TOKEN = config.API_TOKEN
ADMIN_ID = config.ADMIN_ID

async def check_email(session, email):
    # محرك فحص تيك توك السريع
    url = f"https://api.tiktok.com/v1/auth/check_email/?email={email}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("is_available") == True:
                    return email
    except:
        pass
    return None

async def handle_list(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return

    file = await context.bot.get_file(update.message.document.file_id)
    content = await file.download_as_bytearray()
    emails = content.decode('utf-8').splitlines()
    
    await update.message.reply_text(f"🚀 تم استلام {len(emails)} إيميل.\nبدأ الفحص السحابي السريع (Alpha Mode)...")
    
    # تقسيم العمل لمجموعات (Workers) لزيادة السرعة
    async with aiohttp.ClientSession() as session:
        tasks = []
        for email in emails:
            tasks.append(check_email(session, email.strip()))
        
        # تنفيذ الفحص المتوازي
        results = await asyncio.gather(*tasks)
        
        hits = [res for res in results if res]
        if hits:
            for hit in hits:
                await context.bot.send_message(chat_id=ADMIN_ID, text=f"🎯 صيد جديد: {hit}")
        else:
            await update.message.reply_text("❌ انتهى الفحص.. القائمة مستهلكة بالكامل.")

def main():
    print("--- The Alpha Hunter is Online ---")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.Document.ALL, handle_list))
    app.run_polling()

if __name__ == '__main__':
    main()
          
