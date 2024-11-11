from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
import random
import logging
import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

API_KEY = os.getenv('API_KEY')  # Get the API key from the environment variable

# Function to fetch weather data
def get_weather(location):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        city = data["name"]
        country = data["sys"]["country"]
        temp = data["main"]["temp"]
        weather_desc = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        
        # Format the weather information
        weather_info = (
            f"Weather in {city}, {country}:\n"
            f"Temperature: {temp}°C\n"
            f"Condition: {weather_desc.capitalize()}\n"
            f"Humidity: {humidity}%"
        )
        return weather_info
    else:
        print(response.status_code)
        return "Sorry, I couldn't retrieve the weather information. Please try again later."



# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Access the Telegram bot token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# List of sample quotes
quotes = [
    "The best way to predict the future is to create it. - Peter Drucker",
    "Success is not the key to happiness. Happiness is the key to success.",
    "Don't watch the clock; do what it does. Keep going.",
    "Believe you can and you're halfway there. - Theodore Roosevelt",
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
    "It always seems impossible until it’s done. - Nelson Mandela",
    "Success usually comes to those who are too busy to be looking for it. - Henry David Thoreau",
    "Don't be afraid to give up the good to go for the great. - John D. Rockefeller",
    "You miss 100% of the shots you don’t take. - Wayne Gretzky",
    "The harder you work for something, the greater you'll feel when you achieve it. - Unknown",
    "Do not wait to strike till the iron is hot, but make it hot by striking. - William Butler Yeats",
    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
    "The best way to predict the future is to create it. - Peter Drucker",
    "It does not matter how slowly you go, as long as you do not stop. - Confucius",
    "Dream big and dare to fail. - Norman Vaughan",
    "Act as if what you do makes a difference. It does. - William James",
    "What lies behind us and what lies before us are tiny matters compared to what lies within us. - Ralph Waldo Emerson",
    "Happiness is not something ready made. It comes from your own actions. - Dalai Lama",
    "Don't limit your challenges. Challenge your limits. - Unknown"
]

atasozler = [
    "Geleceği tahmin etmenin en iyi yolu onu yaratmaktır. - Peter Drucker",
    "Başarı mutluluğun anahtarı değildir. Mutluluk başarının anahtarıdır.",
    "Saate bakma; onun yaptığını yap. Devam et.",
    "Yapabileceğine inan ve yarı yoldasın demektir.",
    "Harika işler yapmanın tek yolu yaptığın işi sevmektir. - Steve Jobs",
    "Başarı nihai değildir, başarısızlık ölümcül değildir: Önemli olan devam etme cesaretidir. - Winston Churchill",
    "Yapılıncaya kadar her şey imkansız görünür. - Nelson Mandela",
    "Başarı genellikle onu aramakla meşgul olanlara gelir. - Henry David Thoreau",
    "Harika olanı bırakıp harika olanı elde etmekten korkma. - John D. Rockefeller",
    "Atmadığın şutların %100'ünü kaçırırsın. - Wayne Gretzky",
    "Bir şey için ne kadar çok çalışırsan, başardığında o kadar büyük hissedersin. - Anonim",
    "Demiri tavında dövmek için bekleme, döverek ısıt. - William Butler Yeats",
    "Gelecek, hayallerinin güzelliğine inananlara aittir. - Eleanor Roosevelt",
    "Geleceği tahmin etmenin en iyi yolu onu yaratmaktır. - Peter Drucker",
    "Ne kadar yavaş gittiğin önemli değil, yeter ki durma. - Konfüçyüs",
    "Büyük hayaller kur ve başarısızlığa cesaret et. - Norman Vaughan",
    "Yaptığın şeyin bir fark yarattığı gibi davran. Yaratır. - William James",
    "Arkamızda ve önümüzde olanlar, içimizde olanlarla karşılaştırıldığında önemsiz şeylerdir. - Ralph Waldo Emerson",
    "Mutluluk hazır bir şey değildir. Kendi eylemlerinizden gelir. - Dalai Lama",
    "Zorluklarınızı sınırlamayın. Sınırlarınıza meydan okuyun. - Anonim"
]



# List to store chat IDs of users who start the bot
subscribed_users = set()
user_languages = {} 
language = None  # Define language as a global variable

# Define your send_quote function (ensure it is async)
async def send_quote(app: Application):
    print("Sending quote...")
    for chat_id in subscribed_users:
        # Check the language of the user
        user_language = user_languages.get(chat_id, None)
        # Select the appropriate list of quotes based on the language
        if user_language == "EN":
            quote = random.choice(quotes)  # English quotes
        elif user_language == "TR":
            quote = random.choice(atasozler)  # Turkish quotes
        else:
            # Default to English quotes if no language is selected
            quote = random.choice(quotes)

        # Send the selected quote to the user
        await app.bot.send_message(chat_id=chat_id, text=quote)

async def send_morning_message(app):
    message_en = "Good morning! ☀️ Hope you have a fantastic day ahead!"
    message_tr = "Günaydın! ☀️ Günün harika geçsin!"
    for chat_id in subscribed_users:
        if user_languages[chat_id]:
           user_language = user_languages[chat_id]
           if user_language=='EN':
              await app.bot.send_message(chat_id=chat_id, text=message_en)
           if user_language=='TR':
              await app.bot.send_message(chat_id=chat_id, text=message_tr)

# Function to send a good night message
async def send_goodnight_message(app):
    message_en = "Good night! 🌙 Wishing you peaceful dreams!"
    message_tr = "İyi geceler! 🌙 Huzurlu rüyalar dilerim!"
    for chat_id in subscribed_users:
        if user_languages[chat_id]:
           user_language = user_languages[chat_id]
           if user_language=='EN':
              await app.bot.send_message(chat_id=chat_id, text=message_en)
           if user_language=='TR':
              await app.bot.send_message(chat_id=chat_id, text=message_tr)



async def keyword_response(update: Update, context: CallbackContext):
    message_text = update.message.text.lower()
    chat_id = update.message.chat_id

    if user_languages[chat_id]:
       user_language = user_languages[chat_id]

       if user_language == 'EN':

            if "quote" in message_text:
                await update.message.reply_text("Here's an inspiring quote for you!")
                print("Sending quote...")
                quote = random.choice(quotes)
                await update.message.reply_text(quote)
            elif "hello" in message_text or "hi" in message_text:
                await update.message.reply_text(f"Hello {update.effective_user.first_name}!")
            elif "thank" in message_text:
                await update.message.reply_text("You're welcome dear! I'm here to make your day better!")
            elif "bye" in message_text:
                await update.message.reply_text("Bye dear! Hope to see you again soon!")
            elif 'how are you' in message_text:
                await update.message.reply_text("Thanks dear, I'm doing great! What about you ?")
            elif 'im fine' in message_text or "i'm fine" in message_text:
                await update.message.reply_text("Great !")
            elif 'im not fine' in message_text or "i'm not fine" in message_text or 'im bad' in message_text or "i'm bad" in message_text:
                await update.message.reply_text("Hope you will be good !🙏🏻")    
            else:
                await update.message.reply_text('I am not a human being to understand every word 🙈. Type "/help" to see what I can do 🥸')

       elif user_language == 'TR':

            if "atasoz" in message_text or "atasöz" in message_text:
                await update.message.reply_text("İşte sana ilham verici bir atasöz!")
                print("Sending quote...")
                quote = random.choice(atasozler)
                await context.application.bot.send_message(chat_id=chat_id, text=quote)
            elif "merhaba" in message_text or "selam" in message_text:
                await update.message.reply_text(f"Merhaba {update.effective_user.first_name}!")
            elif "teşekkür" in message_text or "sağol" in message_text:
                await update.message.reply_text("Rica ederim canım")
            elif "naber" in message_text or "nasılsın" in message_text:
                await update.message.reply_text("İyiyimm sen ?")
            elif "Iyiyim" in message_text or "İyiyim" in message_text:
                await update.message.reply_text("Hep iyi ol 🙏🏻")
            elif "kötüyüm" in message_text or "iyi değilim" in message_text:
                await update.message.reply_text("iyi olmanı dilerim 🙏🏻")
            elif "görüşürüz" in message_text or "hoşça kal" in message_text:
                await update.message.reply_text("Görüşürüz!")

            else :
                await update.message.reply_text('Ben bir insan değilim ki her lafı anlayayım 🙈. Neler yapabildiğimi görmek için "/help" yaz 🥸')

    else:
        await update.message.reply_text('You have to choose your language first ! Please enter "EN" or "TR". \n Öncelikle sohbet dilini seçmeniz gerekiyor! Lütfen "EN" veya "TR" girin.')

    

# Define your start function
async def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if chat_id not in subscribed_users:
        subscribed_users.add(chat_id)
    user_first_name = update.message.from_user.first_name
    await update.message.reply_text(
        f'Hello, {user_first_name}! Welcome to the bot! Please type "EN" to continue in English.\n'
        f'Merhaba, {user_first_name}, hoş geldin! Türkçe devam etmek için lütfen "TR" gir.'
    )
    user_languages[chat_id] = None 

# Define the /weather command function
async def weather(update: Update, context: CallbackContext):
    if context.args:
        location = " ".join(context.args)  # Get location from the command arguments
        weather_info = get_weather(location)  # Fetch weather data
        await update.message.reply_text(weather_info)  # Send weather info to the user
    else:
        await update.message.reply_text("Please provide a location. For example, /weather London")

# Define the function to handle user language selection
async def set_language(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    user_first_name = update.message.from_user.first_name
    
    # Only process language selection if it's not set
    
    user_message = update.message.text.strip().upper()
    
    if user_message == "EN":
        user_languages[chat_id] = "EN"
        await update.message.reply_text(
            f"Great, {user_first_name}! You have selected English. Here's what this bot can do:\n"
            "- Send inspiring quotes\n"
            "- Share the weather updates\n"
            "- Answer your questions\n\n"
            "Just type your command or question!"
        )
    elif user_message == "TR":
        user_languages[chat_id] = "TR"
        await update.message.reply_text(
            f"Harika, {user_first_name}! Türkçeyi seçtiniz. Bu robotun yapabilecekleri şunlardır:\n"
            "- İlham verici alıntılar gönder\n"
            "- Hava durumu güncellemelerini paylaş\n"
            "- Sorularınızı cevapla\n\n"
            "Sadece komutunuzu veya soruyu yazın!"
        )
    else:
        await update.message.reply_text(
            "Please type either 'EN' for English or 'TR' for Turkish to proceed."
        )

# Define your main function
def main():
    # Set up the bot
    app = Application.builder().token(TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))
    
    # This handler listens for "EN" or "TR" messages only once after /start
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(EN|TR)$"), set_language))

    # This handler responds to general keywords after language selection
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, keyword_response))

    # Create the scheduler
    scheduler = BackgroundScheduler()

    # Scheduler to send a quote daily at a specified time (18:19)
    # Add the job to the scheduler
    scheduler.add_job(lambda: asyncio.run(send_quote(app)), 'cron', hour=14, minute=34)  # Adjust to your desired time

    # Add morning message job at 8:00 AM
    scheduler.add_job(lambda: asyncio.run(send_morning_message(app)), 'cron', hour=8, minute=0)

    # Add good night message job at 10:00 PM (22:00)
    scheduler.add_job(lambda: asyncio.run(send_goodnight_message(app)), 'cron', hour=22, minute=0)

    scheduler.start()

    # Run the bot
    app.run_polling()

if __name__ == '__main__':
    main()
