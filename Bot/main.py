from service import *

logging.basicConfig(
    filename="logs", filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Test Bot
application = ApplicationBuilder().token('6603834308:AAGyQUx2e1hAOEKV0nnjYIARRb1boN35S-A').build()

# Production Bot
# application = ApplicationBuilder().token('6533544967:AAFAwmNoJHxRMvchwNsg1VX-NeShnUNhpk0').build()

start_handler = CommandHandler('start', post_user_info)

message_handler = MessageHandler(filters.TEXT, messageHandler)

application.add_handler(start_handler)
application.add_handler(message_handler)

application.run_polling()

