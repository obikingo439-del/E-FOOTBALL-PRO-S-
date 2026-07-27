import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    ContextTypes, filters, ConversationHandler, CallbackQueryHandler
)
import datetime

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Config
TOKEN = "8198794299:AAF6nTX1Rgz_JFpQ_I2MpKuFxpkJMtPdgbI"  
ADMIN_ID = 5973242012           

# States for Conversation Flow
(
    SELL_PRICE, SELL_PLAYERS, SELL_PHOTO,
    TEAM_PHOTO, TEAM_MANAGER, TEAM_ISSUE,
    PLAYER_NAME, PLAYER_PHOTO, PLAYER_WEAKNESS,
    FEEDBACK_TEXT, QUESTION_TEXT
) = range(11)

# መልእክት ለማጥፋት የሚረዳ Helper Function
async def try_delete_msg(context, chat_id, msg_id):
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
    except Exception:
        pass

# Main Menu Keyboard
def main_menu_keyboard():
    keyboard = [
        [KeyboardButton("🎮 COIN ለመግዛት"), KeyboardButton("$ አካውንት ለመሸጥ")],
        [KeyboardButton("🔧 Team Build ለማስደረግ"), KeyboardButton("👟 Player Progression")],
        [KeyboardButton("💬 ማንኛውንም ጥያቄ ለመጠየቅ (Contact Admin)")],
        [KeyboardButton("📂 አስተያየት ለመስጠት (Feedback)"), KeyboardButton("💳 አካውንት ሽያጭ")],
        [KeyboardButton("👤 ፕሮፋይል"), KeyboardButton("🏠 ዋና ማውጫ (Main Menu)")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"ሰላም {user_name}! ወደ ቦቱ እንኳን ደህና መጡ። እባክዎ ከታች ካሉት አማራጮች አንዱን ይምረጡ፡",
        reply_markup=main_menu_keyboard()
    )

# ----------------- 1. COIN ለመግዛት -----------------
async def buy_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📩 Admin ለማናገር", url="https://t.me/Scoobycute4")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎮 COIN ለመግዛት አድሚኑን ያናግሩ፡", reply_markup=reply_markup)

# ----------------- 2. 💳 አካውንት ሽያጭ -----------------
async def account_sales_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sales_text = (
        "💳 **የሚሸጡ አካውንቶች ዝርዝር፦**\n\n"
        "🔥 **Account 1:** eFootball Account - OVR 102 (Price: 1500 ETB)\n"
        "🔥 **Account 2:** eFootball Account - OVR 100 (Price: 1000 ETB)\n\n"
        "መግዛት ከፈለጉ ከታች ያለውን **`🛒 ለመግዛት`** የሚለውን ቁልፍ ይጫኑ!"
    )
    
    keyboard = [[InlineKeyboardButton("🛒 ለመግዛት", url="https://t.me/Scoobycute4")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    account_photo_url = "https://picsum.photos/800/400" 

    await update.message.reply_photo(
        photo=account_photo_url,
        caption=sales_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ----------------- 3. $ አካውንት ለመሸጥ (FORM) -----------------
async def sell_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Welcome! የምትሸጡበትን ዋጋ ያስቀምጡ (ቁጥር ብቻ)፡")
    context.user_data['last_msg_id'] = msg.message_id
    return SELL_PRICE

async def sell_price_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await try_delete_msg(context, update.effective_chat.id, context.user_data.get('last_msg_id'))
    await try_delete_msg(context, update.effective_chat.id, update.message.message_id)

    if not update.message.text.isdigit():
        msg = await update.message.reply_text("እባክዎ ዋጋውን በቁጥር ብቻ ያስገቡ!")
        context.user_data['last_msg_id'] = msg.message_id
        return SELL_PRICE
    
    context.user_data['sell_price'] = update.message.text
    msg = await update.message.reply_text("ዋጋው በትክክል ተመዝግቧል።\nእባክዎ team ውስጥ ያሉ የሶስት ምርጥ ተጫዋቾች ስም ያስቀምጡ፡")
    context.user_data['last_msg_id'] = msg.message_id
    return SELL_PLAYERS

async def sell_players_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await try_delete_msg(context, update.effective_chat.id, context.user_data.get('last_msg_id'))
    await try_delete_msg(context, update.effective_chat.id, update.message.message_id)

    context.user_data['sell_players'] = update.message.text
    msg = await update.message.reply_text("የተጫዋቾች ስም ተመዝግቧል።\nእባክዎ የአካውንቱን Screen shot ያስገቡ (ምስል ብቻ)፡")
    context.user_data['last_msg_id'] = msg.message_id
    return SELL_PHOTO

async def sell_photo_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await try_delete_msg(context, update.effective_chat.id, context.user_data.get('last_msg_id'))

    if not update.message.photo:
        await try_delete_msg(context, update.effective_chat.id, update.message.message_id)
        msg = await update.message.reply_text("እባክዎ ምስል (Photo) ብቻ ይላኩ!")
        context.user_data['last_msg_id'] = msg.message_id
        return SELL_PHOTO
    
    await try_delete_msg(context, update.effective_chat.id, update.message.message_id)
    context.user_data['sell_photo'] = update.message.photo[-1].file_id
    
    summary = (
        "📋 **የአካውንት ሽያጭ መረጃ፡**\n\n"
        f"❓ **የምትሸጡበት ዋጋ፦** {context.user_data['sell_price']} ETB\n"
        f"❓ **የ 3 ምርጥ ተጫዋቾች ስም፦** {context.user_data['sell_players']}\n"
        "❓ **የአካውንቱ Screen shot፦** ተያይዟል 🖼\n\n"
        "ላኪ፦ @Scoobycute4"
    )
    
    keyboard = [[InlineKeyboardButton("✏️ ማስተካከያ", callback_data="redo_sell")]]
    await update.message.reply_photo(
        photo=context.user_data['sell_photo'],
        caption=summary,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# ----------------- 4. TEAM BUILD (FORM) -----------------
async def team_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("✌️ Welcome!\nእባክዎትን የቡድንዎን ምስል (Squad Screenshot) ያያይዙ (ምስል ብቻ)፡")
    context.user_data['last_msg_id'] = msg.message_id
    return TEAM_PHOTO

async def team_photo_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await try_delete_msg(context, update.effective_chat.id, context.user_data.get('last_msg_id'))

    if not update.message.photo:
        await try_delete_msg(context, update.effective_chat.id, update.message.message_id)
        msg = await update.message.reply_text("እባክዎትን ምስል (Photo) ብቻ ይላኩ!")
        context.user_data['last_msg_id'] = msg.message_id
        return TEAM_PHOTO
    
    await try_delete_msg(context, update.effective_chat.id, update.message.message_id)
    context.user_data['team_photo'] = update.message.photo[-1].file_id
    msg = await update.message.reply_text("የቡድንዎ ምስል ገብቷል።\nእባክዎትን የሚጠቀሙትን አሰልጣኝ ስም (Manager Name) ያስቀምጡ፡")
    context.user_data['last_msg_id'] = msg.message_id
    return TEAM_MANAGER

async def team_manager_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await try_delete_msg(context, update.effective_chat.id, context.user_data.get('last_msg_id'))
    await try_delete_msg(context, update.effective_chat.id, update.message.message_id)

    context.user_data['team_manager'] = update.message.text
    msg = await update.message.reply_text("የአሰልጣኝ ስም ገብቷል።\nእባክዎትን በቡድንዎ ላይ ያጋጠመዎትን ችግር (ለምሳሌ: መከላከል አልቻልኩም...) በጽሁፍ ያስቀምጡ፡")
    context.user_data['last_msg_id'] = msg.message_id
    return TEAM_ISSUE

async def team_issue_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await try_delete_msg(context, update.effective_chat.id, context.user_data.get('last_msg_id'))
    await try_delete_msg(context, update.effective_chat.id, update.message.message_id)

    context.user_data['team_issue'] = update.message.text
    
    summary = (
        "📋 **የ Team Build ጥያቄ ማጠቃለያ፦**\n\n"
        "❓ **የቡድንዎ ምስል (Squad Screenshot)፦** ተያይዟል 🖼\n"
        f"❓ **የሚጠቀሙት አሰልጣኝ ስም (Manager Name)፦** {context.user_data['team_manager']}\n"
        f"❓ **በቡድንዎ ላይ ያጋጠመዎት ችግር፦** {context.user_data['team_issue']}\n\n"
        "ላኪ፦ @Scoobycute4"
    )
    
    keyboard = [[InlineKeyboardButton("✏️ ማስተካከያ", callback_data="redo_team")]]
    await update.message.reply_photo(
        photo=context.user_data['team_photo'],
        caption=summary,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# ----------------- 5. PLAYER PROGRESSION (FORM) -----------------
async def player_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Welcome!\nእባክዎ የተጫዋቹን ስም ያስገቡ፡")
    context.user_data['last_msg_id'] = msg.message_id
    return PLAYER_NAME

async def player_name_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await try_delete_msg(context, update.effective_chat.id, context.user_data.get('last_msg_id'))
    await try_delete_msg(context, update.effective_chat.id, update.message.message_id)

    context.user_data['player_name'] = update.message.text
    msg = await update.message.reply_text("እባክዎ የተጫዋቹን ምስል ያስገቡ (ምስል ብቻ)፡")
    context.user_data['last_msg_id'] = msg.message_id
    return PLAYER_PHOTO

async def player_photo_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await try_delete_msg(context, update.effective_chat.id, context.user_data.get('last_msg_id'))

    if not update.message.photo:
        await try_delete_msg(context, update.effective_chat.id, update.message.message_id)
        msg = await update.message.reply_text("እባክዎ ምስል (Photo) ብቻ ያስገቡ!")
        context.user_data['last_msg_id'] = msg.message_id
        return PLAYER_PHOTO
    
    await try_delete_msg(context, update.effective_chat.id, update.message.message_id)
    context.user_data['player_photo'] = update.message.photo[-1].file_id
    msg = await update.message.reply_text("እባክዎ የተጫዋቹን ደካማ ጎን በጽሑፍ ያስቀምጡ፡")
    context.user_data['last_msg_id'] = msg.message_id
    return PLAYER_WEAKNESS

async def player_weakness_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await try_delete_msg(context, update.effective_chat.id, context.user_data.get('last_msg_id'))
    await try_delete_msg(context, update.effective_chat.id, update.message.message_id)

    context.user_data['player_weakness'] = update.message.text
    
    summary = (
        "📋 **የ Player Progression ጥያቄ ማጠቃለያ፦**\n\n"
        f"❓ **የተጫዋቹ ስም፦** {context.user_data['player_name']}\n"
        "❓ **የተጫዋቹ ምስል፦** ተያይዟል 🖼\n"
        f"❓ **የተጫዋቹ ደካማ ጎን፦** {context.user_data['player_weakness']}\n\n"
        "ላኪ፦ @Scoobycute4"
    )
    
    keyboard = [[InlineKeyboardButton("📤 አሞላሉን ላክ", callback_data="send_player_form")]]
    await update.message.reply_photo(
        photo=context.user_data['player_photo'],
        caption=summary,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# ----------------- 6. 📂 አስተያየት ለመስጠት -----------------
async def feedback_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("እባክዎ አስተያየትዎን እና ማስተካከል ያለብንን ነገር በጽሁፍ ይጻፉልን፡")
    context.user_data['last_msg_id'] = msg.message_id
    return FEEDBACK_TEXT

async def feedback_text_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await try_delete_msg(context, update.effective_chat.id, context.user_data.get('last_msg_id'))
    await try_delete_msg(context, update.effective_chat.id, update.message.message_id)

    user = update.effective_user
    feedback = update.message.text
    
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📂 **አዲስ አስተያየት ተልኳል!**\n\n**ከ፦** @{user.username} (ID: {user.id})\n**አስተያየት፦** {feedback}"
    )
    await update.message.reply_text("አስተያየትዎ በትክክል ደርሶናል! አመሰግናለሁ።")
    return ConversationHandler.END

# ----------------- 7. 💬 ጥያቄ ለመጠየቅ (በቀን 1 ጊዜ) -----------------
async def question_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = str(datetime.date.today())
    last_date = context.user_data.get('last_question_date')
    
    if last_date == today:
        await update.message.reply_text("⚠️ ጥያቄ መጠየቅ የሚችሉት በቀን አንድ ጊዜ ብቻ ነው። እባክዎ ነገ ድጋሚ ይሞክሩ!")
        return ConversationHandler.END
    
    msg = await update.message.reply_text("እባክዎ የሚጠይቁትን ጥያቄ በጽሁፍ ያስገቡ (በቀን 1 ጊዜ ብቻ መጠየቅ ይችላሉ)፡")
    context.user_data['last_msg_id'] = msg.message_id
    return QUESTION_TEXT

async def question_text_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await try_delete_msg(context, update.effective_chat.id, context.user_data.get('last_msg_id'))
    await try_delete_msg(context, update.effective_chat.id, update.message.message_id)

    user = update.effective_user
    question = update.message.text
    today = str(datetime.date.today())
    
    context.user_data['last_question_date'] = today
    
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"💬 **አዲስ ጥያቄ ቀርቧል!**\n\n**ከ፦** @{user.username} (ID: {user.id})\n**ጥያቄ፦** {question}"
    )
    await update.message.reply_text("ጥያቄዎ ለአድሚኑ ደርሷል! መልሱን በቅርቡ ያገኛሉ።")
    return ConversationHandler.END

# ----------------- 👤 PROFILES & MENU -----------------
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👤 **የእርስዎ ፕሮፋይል መረጃ፡**\n\n"
        f"**ስም፦** {user.first_name}\n"
        f"**Username፦** @{user.username if user.username else 'የለውም'}\n"
        f"**ID Number፦** `{user.id}`",
        parse_mode="Markdown"
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሂደቱ ተሰርዟል፣ ወደ ዋና ማውጫ ተመልሰዋል።", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

# Callback query handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "send_player_form":
        user = query.from_user
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=context.user_data.get('player_photo'),
            caption=(
                f"👟 **አዲስ የ Player Progression ጥያቄ!**\n\n"
                f"**ከ፦** @{user.username} (ID: {user.id})\n"
                f"**የተጫዋች ስም፦** {context.user_data.get('player_name')}\n"
                f"**ደካማ ጎን፦** {context.user_data.get('player_weakness')}"
            )
        )
        await query.edit_message_caption(caption="✅ መረጃው በትክክል ለአድሚኑ ተልኳል!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    sell_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^(\\$ አካውንት ለመሸጥ)$'), sell_start)],
        states={
            SELL_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sell_price_step)],
            SELL_PLAYERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, sell_players_step)],
            SELL_PHOTO: [MessageHandler(filters.PHOTO, sell_photo_step)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    team_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^(🔧 Team Build ለማስደረግ)$'), team_start)],
        states={
            TEAM_PHOTO: [MessageHandler(filters.PHOTO, team_photo_step)],
            TEAM_MANAGER: [MessageHandler(filters.TEXT & ~filters.COMMAND, team_manager_step)],
            TEAM_ISSUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, team_issue_step)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    player_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^(👟 Player Progression)$'), player_start)],
        states={
            PLAYER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, player_name_step)],
            PLAYER_PHOTO: [MessageHandler(filters.PHOTO, player_photo_step)],
            PLAYER_WEAKNESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, player_weakness_step)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    feedback_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^(📂 አስተያየት ለመስጠት \\(Feedback\\))$'), feedback_start)],
        states={
            FEEDBACK_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, feedback_text_step)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    question_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^(💬 ማንኛውንም ጥያቄ ለመጠየቅ \\(Contact Admin\\))$'), question_start)],
        states={
            QUESTION_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_text_step)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex('^(🎮 COIN ለመግዛት)$'), buy_coin))
    app.add_handler(MessageHandler(filters.Regex('^(💳 አካውንት ሽያጭ)$'), account_sales_info))
    app.add_handler(MessageHandler(filters.Regex('^(👤 ፕሮፋይል)$'), show_profile))
    app.add_handler(MessageHandler(filters.Regex('^(🏠 ዋና ማውጫ \\(Main Menu\\))$'), start))

    app.add_handler(sell_handler)
    app.add_handler(team_handler)
    app.add_handler(player_handler)
    app.add_handler(feedback_handler)
    app.add_handler(question_handler)
    app.add_handler(CallbackQueryHandler(button_callback))

    print("ቦቱ ሥራ ጀምሯል...")
    app.run_polling()

if __name__ == '__main__':
    main()
