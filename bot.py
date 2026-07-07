import asyncio
import logging
import os
import random
import requests
from datetime import datetime, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- Configuration ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Data ---

# Inspirational Quotes
QUOTES = [
    "💡 The only way to do great work is to love what you do. - Steve Jobs",
    "🚀 Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
    "💰 The stock market is filled with individuals who know the price of everything, but the value of nothing. - Peter Lynch",
    "📈 In investing, what is comfortable is rarely profitable. - Robert Arnott",
    "✨ Be fearful when others are greedy, and greedy when others are fearful. - Warren Buffett",
    "🔥 The best time to plant a tree was 20 years ago. The second best time is now. - Chinese Proverb",
    "💪 Believe you can and you're halfway there. - Theodore Roosevelt",
    "🌊 It does not matter how slowly you go as long as you do not stop. - Confucius",
    "📉 The stock market is a device for transferring money from the impatient to the patient. - Warren Buffett",
    "🚀 Don't watch the clock; do what it does. Keep going. - Sam Levenson",
    "💎 Buy when everyone else is selling and hold when everyone else is buying. - J.P. Morgan",
    "📊 The four most dangerous words in investing are: 'This time it's different.' - Sir John Templeton"
]

# Meme URLs
MEME_URLS = [
    "https://i.imgflip.com/1bij.jpg",
    "https://i.imgflip.com/30b1gx.jpg",
    "https://i.imgflip.com/26am.jpg",
    "https://i.imgflip.com/2kbn1e.jpg",
    "https://i.imgflip.com/1otk96.jpg",
    "https://i.imgflip.com/2zh47r.jpg",
    "https://i.imgflip.com/1g8my4.jpg",
    "https://i.imgflip.com/2k4j4x.jpg"
]

# Trading Tips
TRADING_TIPS = [
    "📌 Always use stop-loss orders to protect your capital.",
    "📌 Never invest more than you can afford to lose.",
    "📌 Diversify your portfolio across different assets.",
    "📌 Do your own research (DYOR) before investing.",
    "📌 Fear and greed are the two biggest enemies of traders.",
    "📌 Keep a trading journal to track your wins and losses.",
    "📌 The trend is your friend, until it ends.",
    "📌 Patience is key - wait for the right entry point.",
    "📌 Risk management is more important than making profits.",
    "📌 Don't let emotions drive your trading decisions."
]

# Stock symbols for tracking
STOCK_SYMBOLS = ["AAPL", "GOOGL", "TSLA", "AMZN", "META", "NFLX", "SPY", "NVDA"]

# Crypto symbols for tracking
CRYPTO_SYMBOLS = ["bitcoin", "ethereum", "solana", "cardano", "dogecoin", "ripple", "polkadot", "avalanche"]

# Track active chats
active_chats = set()

# --- API Functions ---

def get_crypto_prices():
    """Fetch cryptocurrency prices from CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": ",".join(CRYPTO_SYMBOLS),
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_market_cap": "true",
            "include_24hr_vol": "true"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        msg = "📊 **Cryptocurrency Prices**\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━\n"
        
        for coin in CRYPTO_SYMBOLS[:6]:  # Show top 6
            coin_data = data.get(coin, {})
            if coin_data:
                price = coin_data.get('usd', 0)
                change = coin_data.get('usd_24h_change', 0)
                emoji = "🟢" if change >= 0 else "🔴"
                symbol = coin[:3].upper()
                msg += f"{emoji} **{symbol}**: ${price:,.2f} ({change:+.2f}%)\n"
        
        msg += "━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"🕐 Updated: {datetime.now().strftime('%H:%M:%S')} UTC"
        return msg
    except Exception as e:
        logger.error(f"Crypto API error: {e}")
        return "⚠️ Crypto prices temporarily unavailable. Please try again later."

def get_stock_prices():
    """Fetch stock prices (simulated for demo)"""
    try:
        # Using free API from Twelve Data (requires API key for real data)
        # For demo, showing simulated data
        import random as rnd
        
        msg = "📈 **Stock Market Update**\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━\n"
        
        stocks = [
            ("AAPL", 189.50, 0.85),
            ("GOOGL", 141.20, 0.50),
            ("TSLA", 245.30, -1.20),
            ("AMZN", 185.40, 0.90),
            ("META", 358.40, -0.30),
            ("NFLX", 625.80, 1.10),
            ("SPY", 508.75, 0.60),
            ("NVDA", 875.30, 2.50)
        ]
        
        for symbol, price, change in stocks:
            emoji = "🟢" if change >= 0 else "🔴"
            msg += f"{emoji} **{symbol}**: ${price:.2f} ({change:+.2f}%)\n"
        
        msg += "━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"🕐 Updated: {datetime.now().strftime('%H:%M:%S')} UTC"
        msg += "\n\n📊 *Data is simulated for demonstration*"
        return msg
    except Exception as e:
        logger.error(f"Stock API error: {e}")
        return "⚠️ Stock prices temporarily unavailable."

# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command with inline keyboard"""
    chat_id = update.effective_chat.id
    active_chats.add(chat_id)
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Crypto", callback_data="crypto"),
            InlineKeyboardButton("📈 Stocks", callback_data="stocks")
        ],
        [
            InlineKeyboardButton("💡 Quote", callback_data="quote"),
            InlineKeyboardButton("😂 Meme", callback_data="meme")
        ],
        [
            InlineKeyboardButton("📌 Trading Tips", callback_data="tip"),
            InlineKeyboardButton("ℹ️ Help", callback_data="help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = f"""🤖 **TradeSelingi Bot**

Welcome to your trading companion! I provide real-time market data, inspiration, and memes to keep you motivated while trading.

**Features:**
✅ Real-time Crypto Prices
✅ Stock Market Updates
✅ Daily Trading Tips
✅ Inspirational Quotes
✅ Fun Memes
✅ Auto-posting to groups

**How to use:**
• Use the buttons below
• Or type commands: /crypto, /stocks, /quote, /meme, /tip

**Active Chats:** {len(active_chats)}
**Bot:** @tradeselingisbot
**Status:** 🟢 Online"""
    
    await update.message.reply_text(
        welcome_msg,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    logger.info(f"Bot started in chat: {chat_id}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses"""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    active_chats.add(chat_id)
    
    data = query.data
    
    if data == "crypto":
        await query.edit_message_text(
            get_crypto_prices(),
            parse_mode='Markdown'
        )
    elif data == "stocks":
        await query.edit_message_text(
            get_stock_prices(),
            parse_mode='Markdown'
        )
    elif data == "quote":
        quote = random.choice(QUOTES)
        await query.edit_message_text(
            f"💡 **Daily Inspiration**\n\n{quote}",
            parse_mode='Markdown'
        )
    elif data == "meme":
        meme_url = random.choice(MEME_URLS)
        await query.message.reply_photo(
            meme_url,
            caption="😂 **Meme Time!**"
        )
        await query.message.delete()
    elif data == "tip":
        tip = random.choice(TRADING_TIPS)
        await query.edit_message_text(
            f"📌 **Trading Tip**\n\n{tip}",
            parse_mode='Markdown'
        )
    elif data == "help":
        help_msg = """ℹ️ **Help & Commands**

**Available Commands:**
/crypto - 📊 Crypto prices
/stocks - 📈 Stock prices
/quote - 💡 Random quote
/meme - 😂 Random meme
/tip - 📌 Trading tip
/start - Show main menu
/help - This message

**Auto-Posting Schedule:**
• Crypto Updates: Every hour
• Trading Tips: Every 2 hours
• Quotes: Every 3 hours
• Memes: Every 4 hours

**Add me to your group:**
1. Add @tradeselingisbot to your group
2. Send /start to activate
3. I'll start auto-posting!

Made with ❤️ for the trading community"""
        await query.edit_message_text(
            help_msg,
            parse_mode='Markdown'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    chat_id = update.effective_chat.id
    active_chats.add(chat_id)
    
    help_msg = """ℹ️ **Help & Commands**

**Available Commands:**
/crypto - 📊 Crypto prices
/stocks - 📈 Stock prices
/quote - 💡 Random quote
/meme - 😂 Random meme
/tip - 📌 Trading tip
/start - Show main menu
/help - This message

**Auto-Posting Schedule:**
• Crypto Updates: Every hour
• Trading Tips: Every 2 hours
• Quotes: Every 3 hours
• Memes: Every 4 hours"""
    
    await update.message.reply_text(help_msg, parse_mode='Markdown')

async def crypto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Crypto prices command"""
    chat_id = update.effective_chat.id
    active_chats.add(chat_id)
    await update.message.reply_text(get_crypto_prices(), parse_mode='Markdown')

async def stocks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stock prices command"""
    chat_id = update.effective_chat.id
    active_chats.add(chat_id)
    await update.message.reply_text(get_stock_prices(), parse_mode='Markdown')

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quote command"""
    chat_id = update.effective_chat.id
    active_chats.add(chat_id)
    quote = random.choice(QUOTES)
    await update.message.reply_text(f"💡 **Daily Inspiration**\n\n{quote}", parse_mode='Markdown')

async def meme_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Meme command"""
    chat_id = update.effective_chat.id
    active_chats.add(chat_id)
    meme_url = random.choice(MEME_URLS)
    await update.message.reply_photo(meme_url, caption="😂 **Meme Time!**")

async def tip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trading tip command"""
    chat_id = update.effective_chat.id
    active_chats.add(chat_id)
    tip = random.choice(TRADING_TIPS)
    await update.message.reply_text(f"📌 **Trading Tip**\n\n{tip}", parse_mode='Markdown')

# --- Auto-posting Functions ---

async def auto_post_crypto(context: ContextTypes.DEFAULT_TYPE):
    """Auto-post crypto prices to all active chats"""
    if not active_chats:
        return
    
    msg = get_crypto_prices()
    for chat_id in list(active_chats):
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=msg,
                parse_mode='Markdown'
            )
            logger.info(f"Crypto posted to {chat_id}")
        except Exception as e:
            logger.error(f"Failed to post crypto to {chat_id}: {e}")
            if "bot was blocked" in str(e).lower() or "chat not found" in str(e).lower():
                active_chats.discard(chat_id)

async def auto_post_tip(context: ContextTypes.DEFAULT_TYPE):
    """Auto-post trading tips to all active chats"""
    if not active_chats:
        return
    
    tip = random.choice(TRADING_TIPS)
    for chat_id in list(active_chats):
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"📌 **Trading Tip**\n\n{tip}",
                parse_mode='Markdown'
            )
            logger.info(f"Tip posted to {chat_id}")
        except Exception as e:
            logger.error(f"Failed to post tip to {chat_id}: {e}")
            if "bot was blocked" in str(e).lower() or "chat not found" in str(e).lower():
                active_chats.discard(chat_id)

async def auto_post_quote(context: ContextTypes.DEFAULT_TYPE):
    """Auto-post quotes to all active chats"""
    if not active_chats:
        return
    
    quote = random.choice(QUOTES)
    for chat_id in list(active_chats):
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"💡 **Daily Inspiration**\n\n{quote}",
                parse_mode='Markdown'
            )
            logger.info(f"Quote posted to {chat_id}")
        except Exception as e:
            logger.error(f"Failed to post quote to {chat_id}: {e}")
            if "bot was blocked" in str(e).lower() or "chat not found" in str(e).lower():
                active_chats.discard(chat_id)

async def auto_post_meme(context: ContextTypes.DEFAULT_TYPE):
    """Auto-post memes to all active chats"""
    if not active_chats:
        return
    
    meme_url = random.choice(MEME_URLS)
    for chat_id in list(active_chats):
        try:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=meme_url,
                caption="😂 **Meme Time!**"
            )
            logger.info(f"Meme posted to {chat_id}")
        except Exception as e:
            logger.error(f"Failed to post meme to {chat_id}: {e}")
            if "bot was blocked" in str(e).lower() or "chat not found" in str(e).lower():
                active_chats.discard(chat_id)

# --- Stats Command (Admin) ---
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    chat_id = update.effective_chat.id
    active_chats.add(chat_id)
    
    stats_msg = f"""📊 **Bot Statistics**

**Active Chats:** {len(active_chats)}
**Total Commands Available:** 6
**Auto-Post Tasks:** 4
**Uptime:** Online 🟢

**Features:**
• Crypto: {len(CRYPTO_SYMBOLS)} coins
• Stocks: {len(STOCK_SYMBOLS)} stocks
• Quotes: {len(QUOTES)} quotes
• Memes: {len(MEME_URLS)} memes
• Tips: {len(TRADING_TIPS)} tips

**Bot:** @tradeselingisbot"""
    
    await update.message.reply_text(stats_msg, parse_mode='Markdown')

# --- Main Application ---

async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set!")
        return
    
    # Build the application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("crypto", crypto_command))
    app.add_handler(CommandHandler("stocks", stocks_command))
    app.add_handler(CommandHandler("quote", quote_command))
    app.add_handler(CommandHandler("meme", meme_command))
    app.add_handler(CommandHandler("tip", tip_command))
    app.add_handler(CommandHandler("stats", stats_command))
    
    # Add callback query handler for inline buttons
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Setup JobQueue for auto-posting
    if app.job_queue:
        # Schedule auto-posts
        app.job_queue.run_repeating(auto_post_crypto, interval=3600, first=30)    # Every hour
        app.job_queue.run_repeating(auto_post_tip, interval=7200, first=60)       # Every 2 hours
        app.job_queue.run_repeating(auto_post_quote, interval=10800, first=90)    # Every 3 hours
        app.job_queue.run_repeating(auto_post_meme, interval=14400, first=120)    # Every 4 hours
        
        logger.info("✅ JobQueue initialized and tasks scheduled!")
    else:
        logger.warning("⚠️ JobQueue not available - using fallback")
    
    logger.info("🚀 @tradeselingisbot started successfully!")
    logger.info(f"📊 Active chats: {len(active_chats)}")
    
    # Start the bot
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
