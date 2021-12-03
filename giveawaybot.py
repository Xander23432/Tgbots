from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, PrefixHandler
from pytz import timezone
import telegram
import telegram.ext
import psycopg
import logging
import datetime
import html
import traceback

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

u = Updater("TOKEN")
j = u.job_queue

conn = psycopg.connect(host="localhost", user="postgres",
                       dbname="dbname", password="password")
cur = conn.cursor()


def start(update: Update, context: CallbackContext):
    if update.effective_chat.type != "private":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Hey! I am alive :) PM me for any kind of help 😉")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'''🎉 All about <b>GiveawayBot</b> 🎉

<b>Hold giveaways quickly and easily!</b>

Hello! I'm <b>GiveawayBot</b>, and I'm here to make it as easy as possible to hold giveaways on your Telegram group/channel! I was created by <a href='tg://user?id=2056511700'>Aditya</a> <code>(2056511700)</code> using the <a href='https://github.com/python-telegram-bot/python-telegram-bot'>Python-telegram-bot</a> library (13.8.1) and <a href='https://www.postgresql.org/'>Postgresql database</a> (14.1). Check out my commands by typing <code>!ghelp</code>''', parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def ghelp(update: Update, context: CallbackContext):
    if update.effective_chat.type == "private":
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'''🎉 GiveawayBot commands: 

<b>!ginvite</b> - shows how to invite the bot
<b>!gabout</b> - shows info about the bot
<b>!gping</b> - shows latency of the bot

<u>Giveaway</u>:

<b>!gcreate</b> - creates a giveaway (interactive setup)
<b>!gstart {html.escape('<time>')} [winners]w [prize]</b> - starts a giveaway
<b>!gend [messageId]</b> - ends (picks a winner for) the specified or latest giveaway in the current channel
<b>!greroll [messageId]</b> - re-rolls the specified or latest giveaway in the current channel
<b>!glist</b> - lists active giveaways on the channel

Do not include {html.escape('<>')} nor [] - {html.escape("<>")} means required and [] means optional.
For additional help contact <a href="tg://user?id=2056511700">Aditya</a>
''', parse_mode=ParseMode.HTML)


def ginvite(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='''🎉 Hello! I'm <b>GiveawayBot</b>! I help to make giveaways quick and easy!
You can add me to your group with this link:

🔗 https://t.me/dctggiveawaybot?startgroup=true

Check out my commands by typing <code>!ghelp</code>''', parse_mode=ParseMode.HTML)


def gstart(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"💥 This command cannot be used in Private Messages!")
    else:
        user_says = " ".join(context.args)
        user_says = user_says.split(" ")
        keyboard = [[InlineKeyboardButton("🎉", callback_data="1")]]
        item = user_says[2:]
        now = datetime.datetime.now()
        seconds = False
        minutes = False
        hours = False
        days = False
        try:
            time = user_says[0]
        except:
            context.bot.send_message(
                chat_id=chat.id, text=f"💥 Please include a length of time, and a number of winners and a prize! \nExample usage: <code>/gstart 30m 5w Awesome T-Shirt</code>", parse_mode=ParseMode.HTML)
        try:
            winners = user_says[1].split("w")
            winners = int(winners[0])
        except:
            winners = 1
            item = user_says[1:]
        try:
            if time.endswith("s"):
                time = time.split("s")
                time1 = int(time[0])
                print(time1)
                if time1 > 2592000:
                    context.bot.send_message(
                        chat_id=chat.id, text="Giveaways cannot be greater than 30 days!")
                else:
                    seconds = True
                    added = now+datetime.timedelta(seconds=int(time1))
                    time = f"{time1} Seconds"
            elif time.endswith("m"):
                time = time.split("m")
                time1 = int(time[0])
                if time1 > 43200:
                    context.bot.send_message(
                        chat_id=chat.id, text="Giveaways cannot be greater than 30 days!")
                else:
                    minutes = True
                    added = now+datetime.timedelta(minutes=int(time1))
                    time = f"{time1} Minutes"
            elif time.endswith("h"):
                time = time.split("h")
                time1 = int(time[0])
                if time1 > 720:
                    context.bot.send_message(
                        chat_id=chat.id, text="Giveaways cannot be greater than 30 days!")
                else:
                    hours = True
                    added = now+datetime.timedelta(hours=int(time1))
                    time = f"{time1} Hours"
            elif time.endswith("d"):
                time = time.split("d")
                time1 = int(time[0])
                if time1 > 30:
                    context.bot.send_message(
                        chat_id=chat.id, text="Giveaways cannot be greater than 30 days!")
                else:
                    days = True
                    added = now+datetime.timedelta(days=int(time1))
                    time = f"{time1} Days"

        except:
            context.bot.send_message(
                chat_id=chat.id, text=f"💥 Failed to parse time from <code>{time}</code> \nExample usage: <code>/gstart 30m 5w Awesome T-Shirt</code>", parse_mode=ParseMode.HTML)
        try:
            if seconds or minutes or hours or days == True:
                if now.strftime("%d %m %Y") == added.strftime("%d %m %Y"):
                    end = added.strftime("Today at %I:%M %p")
                else:
                    end = added.strftime("%m/%d/%Y")

                item = str(item)
                item = item.replace("[", "").replace("]", "").replace(
                    "'", "").replace(",", "")
                msg = context.bot.send_message(chat_id=chat.id, text=f'''🎉 GIVEAWAY 🎉

<b>{item}</b>

React with 🎉 to enter!
Ends: in {time} ({added.strftime("%B %d, %Y %I:%M %p")})
Hosted by: <a href="tg://user?id={user.id}">{user.first_name}</a>

<i>{winners} Winner(s) | Ends at • {end}</i>
        ''', parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
                time1 = int(time1)
                name = str(chat.id)+str(msg.message_id)
                if seconds == True:
                    j.run_once(callback, time1, context=[
                        chat.id, msg.message_id], name=name)
                elif minutes == True:
                    j.run_once(callback, time1*60,
                               context=[chat.id, msg.message_id], name=name)
                elif hours == True:
                    j.run_once(callback, time1*60*60,
                               context=[chat.id, msg.message_id], name=name)
                elif days == True:
                    j.run_once(callback, time1*60*60*24,
                               context=[chat.id, msg.message_id], name=name)

                try:
                    cur.execute("INSERT INTO giveaway (chat_id, message_id, item_name, winners) VALUES (%s, %s, %s, %s)",
                                (chat.id, msg.message_id, str(item), winners))
                except psycopg.errors.DuplicateTable:
                    cur.execute("ROLLBACK")
                    cur.execute("INSERT INTO giveaway (chat_id, message_id, item_name, winners) VALUES (%s, %s, %s, %s)",
                                (chat.id, msg.message_id, str(item), winners))
                conn.commit()
            else:
                pass
        except Exception:
            print(traceback.format_exc())


def callback(context: telegram.ext.CallbackContext):
    details = context.job.context
    chat_id = details[0]
    message_id = details[1]
    cur.execute(
        f"SELECT item_name FROM giveaway WHERE chat_id={chat_id} AND message_id={message_id}")
    row = cur.fetchall()
    item_name = row[0][0]
    context.bot.send_message(
        chat_id=chat_id, text=f"Congratulation you won <b>{item_name}</b>", parse_mode=ParseMode.HTML)
    cur.execute(
        f"DELETE FROM giveaway WHERE chat_id={chat_id} AND message_id={message_id}")
    conn.commit()


def gend(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private":
        context.bot.send_message(
            chat_id=chat.id, text=f"💥 This command cannot be used in Private Messages!")
    else:
        members = context.bot.get_chat_member(chat_id=chat.id, user_id=user.id)
        allowed = ["administrator", "creator", "owner"]
        if members.status not in allowed:
            context.bot.send_message(
                chat_id=chat.id, text="You don't have administrator privileges")
        else:
            user_says = " ".join(context.args)
            user_says = user_says.split(" ")
            message_id = user_says[0]
            if user_says == [""]:
                try:
                    cur.execute(
                        f"SELECT message_id FROM giveaway WHERE id=(SELECT MAX(id) FROM giveaway)")
                    row = cur.fetchall()
                    message_id = str(row[0][0])
                    name = str(chat.id)+message_id
                    current_jobs = j.get_jobs_by_name(name)
                    for job in current_jobs:
                        job.run(context.dispatcher)
                        job.schedule_removal()
                except:
                    context.bot.send_message(
                        chat_id=chat.id, text=f"💥 I couldn't find any recent giveaways in this channel.")
            else:
                try:
                    name = str(chat.id)+message_id
                    current_jobs = j.get_jobs_by_name(name)
                    if current_jobs == ():
                        raise ValueError
                    else:
                        for job in current_jobs:
                            job.run(context.dispatcher)
                            job.schedule_removal()
                except ValueError:
                    context.bot.send_message(
                        chat_id=chat.id, text="💥 That is not a valid message ID! Try running without an ID to use the most recent giveaway in a channel.")


def glist(update: Update, context: CallbackContext):
    chat = update.effective_chat
    if chat.type == 'private':
        context.bot.send_message(
            chat_id=chat.id, text=f"💥 This command cannot be used in Private Messages!")
    else:
        try:
            cur.execute(
                f"SELECT message_id FROM giveaway where chat_id={chat.id}")
            message_id = cur.fetchall()
            message_ids = []
            message_list = []
            for ids in message_id:
                message_ids.append(ids[0])
            for i in message_ids:
                cur.execute(
                    f"SELECT winners FROM giveaway WHERE message_id={i} AND chat_id={chat.id}")
                winner = cur.fetchall()
                for win in winner:
                    winners = win[0]
                current_jobs = j.get_jobs_by_name(str(chat.id)+str(i))
                for job in current_jobs:
                    next_run = job.next_t
                    remaining = next_run-datetime.datetime.now(timezone("UTC"))
                    secs = remaining.total_seconds()
                    if secs < 60:
                        remaining_time = f"<b>{round(secs)}</b> seconds"
                    elif secs > 60 and secs < 3600:
                        remaining_time = f"<b>{round(secs/60)}</b> minutes"
                    elif secs > 3600 and secs < 86400:
                        remaining_time = f"<b>{round(secs/3600)}</b> hours"
                    elif secs > 86400:
                        remaining_time = f"<b>{round(secs/86400)}</b> days"
                cur.execute(
                    f"SELECT item_name FROM giveaway WHERE message_id={i} AND chat_id={chat.id}")
                items_name = cur.fetchall()
                for item in items_name:
                    itemname = item[0]
                message_to_send = f"<code>{i}</code> | <b>{winners}</b> Winners | Prize: <b>{itemname}</b> | Ends: in {remaining_time}"
                message_list.append(message_to_send)
            message_to_send = "\n".join(message_list)
            context.bot.send_message(
                chat_id=chat.id, text=message_to_send, parse_mode=ParseMode.HTML)
            message_list.clear()
        except:
            context.bot.send_message(
                chat_id=chat.id, text="💥 There are no giveaways running on the channel!", parse_mode=ParseMode.HTML)


if __name__ == "__main__":
    dp = u.dispatcher
    dp.add_handler(PrefixHandler(["!", "/"], ["start", "gabout"], start))
    dp.add_handler(PrefixHandler(["!", "/"], "ginvite", ginvite))
    dp.add_handler(PrefixHandler(["!", "/"], "ghelp", ghelp))
    dp.add_handler(PrefixHandler(["!", "/"], "gstart", gstart))
    dp.add_handler(PrefixHandler(["!", "/"], "gend", gend))
    dp.add_handler(PrefixHandler(["!", "/"], "glist", glist))
    u.start_polling()
    u.idle()
