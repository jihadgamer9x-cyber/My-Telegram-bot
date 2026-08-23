import os
import base64
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import openai

# ----------------- CONFIGURATION -----------------
BOT_TOKEN = "8904105345:AAHw-ShWmp1NAo37oOZGDl2g8i0wEJZwTTo"
BOT_USERNAME = "@tradingby4xbot"
BOT_NAME = "Trading By 4X"
ADMIN_USERNAME = "@freeincomesupport4x"

# আপনার দেওয়া OpenAI API Key
OPENAI_API_KEY = "Sk-proj-EBz9n_VRkjMWbhBMS9Q0xrMK5yiBkwQcCQ9M4Qx5Sa0hvhLXbV70EA6jUEsEDASiYtEPCD5XDNT3BlbkFJ_6v_43TvmZvCEgx4u1Miuw7DSOF8keOqp6nSXHrPOygTsKeX8To-VM54QtzS44pdbrff5PrIoA"
openai.api_key = OPENAI_API_KEY

# লগিং সেটআপ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ইমেজ বেস৬৪ এনকোডিং ফাংশন
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# /start কমান্ড
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        f"👋 Welcome to **{BOT_NAME}**!\n\n"
        "📈 Quotex বা অন্য যেকোনো Binary Trading চার্টের স্ক্রিনশট (SS) পাঠান।\n"
        "বট চার্টটি অ্যানালাইসিস করে আপনাকে সিগন্যাল প্রদান করবে।\n\n"
        f"💬 Admin Support: {ADMIN_USERNAME}"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

# ফটো প্রসেসিং
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("🔍 Analyzing chart screenshot... Please wait.")
    file_path = "chart_temp.jpg"
    
    try:
        # ছবি ডাউনলোড করা
        photo_file = await update.message.photo[-1].get_file()
        await photo_file.download_to_drive(file_path)
        
        # বেস৬৪ এনকোড
        base64_image = encode_image(file_path)
        
        # OpenAI Vision API কল (gpt-4o মডেল)
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": (
                                "You are an expert Binary Options trader. Analyze this candlestick chart screenshot. "
                                "Provide a trading signal response in the following structured Bengali format:\n\n"
                                "📊 **Signal Report - Trading By 4X**\n"
                                "--- \n"
                                "🟢/🔴 **Signal:** [CALL (UP) / PUT (DOWN)]\n"
                                "⏱ **Timeframe:** [1 Min / 2 Min / 5 Min]\n"
                                "🎯 **Accuracy:** [e.g., 85%]\n"
                                "📉 **Trend:** [Uptrend / Downtrend / Sideways]\n"
                                "💡 **Reason:** [Short technical analysis summary in Bengali]\n\n"
                                "⚠️ *Trading carries financial risk.*"
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=400
        )
        
        signal_result = response.choices[0].message.content
        
        # ব্যবহৃত ছবি মুছে ফেলা
        if os.path.exists(file_path):
            os.remove(file_path)
            
        await status_msg.edit_text(signal_result, parse_mode="Markdown")
        
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        await status_msg.edit_text(f"❌ **Error:** সিগন্যাল প্রসেস করতে ব্যর্থ হয়েছে। API Key সক্রিয় আছে কিনা এবং অ্যাকাউন্টে ক্রেডিট আছে কিনা চেক করুন।\n\nSupport: {ADMIN_USERNAME}")

# মেইন ফাংশন
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print(f"{BOT_NAME} ({BOT_USERNAME}) is running...")
    app.run_polling()
