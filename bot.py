import logging
import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class TodoBot:
    def __init__(self, filename="tasks.json"):
        self.filename = filename
        self.tasks = self.load_tasks()

    def load_tasks(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading tasks: {e}")
        return []

    def save_tasks(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Error saving tasks: {e}")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await update.message.reply_text(
            f"Привет, {user.first_name}!\n"
            "Я твой To-Do List бот!\n\n"
            "Доступные команды:\n"
            "/start - начать работу\n"
            "/add <задача> - добавить задачу\n"
            "/list - показать все задачи\n"
            "/done <номер> - отметить задачу выполненной\n"
            "/help - помощь"
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
To-Do List Bot - помощь:

/add <текст задачи> - добавить новую задачу
/list - посмотреть все задачи
/done <номер> - отметить задачу выполненной
/help - показать это сообщение

Пример:
/add Купить молоко
/list
/done 1
"""
        await update.message.reply_text(help_text)

    async def add_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text(" Используй: /add <текст задачи>")
            return

        task_text = " ".join(context.args)
        self.tasks.append({
            'text': task_text,
            'completed': False
        })
        self.save_tasks()

        await update.message.reply_text(f"Задача добавлена: {task_text}")

    async def list_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.tasks:
            await update.message.reply_text("Список задач пуст!")
            return

        message = "Твой To-Do List:\n\n"
        for i, task in enumerate(self.tasks, 1):
            status = "Отлично" if task['completed'] else "Ожидание"
            message += f"{i}. {status} {task['text']}\n"

        await update.message.reply_text(message)

    async def done_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        if not context.args:
            await update.message.reply_text("Используй: /done <номер задачи>")
            return

        try:
            task_num = int(context.args[0])
            if 1 <= task_num <= len(self.tasks):
                self.tasks[task_num - 1]['completed'] = True
                self.save_tasks()
                task_text = self.tasks[task_num - 1]['text']
                await update.message.reply_text(f"Задача выполнена: {task_text}")
            else:
                await update.message.reply_text(f"Неверный номер задачи. Доступно: 1-{len(self.tasks)}")
        except ValueError:
            await update.message.reply_text("Введите корректный номер задачи")


def main():
    TOKEN = "8435156880:AAHeaabYxqycxq2mn8zK7e6rLU26rWpEUB0"

    bot = TodoBot()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.help))
    application.add_handler(CommandHandler("add", bot.add_task))
    application.add_handler(CommandHandler("list", bot.list_tasks))
    application.add_handler(CommandHandler("done", bot.done_task))

    application.run_polling()

if __name__ == "__main__":
    main()
