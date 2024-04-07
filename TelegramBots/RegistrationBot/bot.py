# Импорт бота из модуля utils
from utils import bot, create_files_if_not_exist
# Импорт обработчиков событий start, admin и callback_handler из модуля handlers
from handlers import start, admin, callback_handler
create_files_if_not_exist()
print('Files is create')

# Вывод сообщения о запуске бота
print('Bot is started')

# Запуск бота с параметром none_stop=True, чтобы бот автоматически перезапускался в случае возникновения ошибок
bot.polling(none_stop=True)
