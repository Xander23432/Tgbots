from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, PrefixHandler, ConversationHandler, MessageHandler, Filters
from pytz import timezone
import telegram
import telegram.ext
import psycopg
import logging
import datetime
import html
import traceback
import os
import json


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


conn = psycopg.connect(host="localhost", user="postgres",
                       dbname="database", password="password", port=5432)
cur = conn.cursor()


def start(update: Update, context: CallbackContext):
    bot = context.bot
    if update.effective_chat.type != "private":
        bot.send_message(chat_id=update.effective_chat.id,
                         text=f"Hey! I am alive :) PM me for any kind of help 😉")
    else:
        bot.send_message(chat_id=update.effective_chat.id, text=f'''🎉 All about <b>GiveawayBot</b> 🎉

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
    bot = context.bot
    if chat.type == "private":
        bot.send_message(chat_id=update.effective_chat.id,
                         text=f"💥 This command cannot be used in Private Messages!")
    else:
        user_says = " ".join(context.args)
        user_says = user_says.split(" ")
        item = user_says[2:]
        try:
            time = user_says[0]
        except:
            bot.send_message(
                chat_id=chat.id, text=f"💥 Please include a length of time, and a number of winners and a prize! \nExample usage: <code>/gstart 30m 5w Awesome T-Shirt</code>", parse_mode=ParseMode.HTML)
        try:
            winners = user_says[1].split("w")
            winners = int(winners[0])

        except:
            winners = 1
            item = user_says[1:]
        if winners > 20 or winners < 1:
            context.bot.send_message(
                chat_id=chat.id, text="💥 Number of winners must be at least 1 and no larger than 20")
        else:
            giveaway_run(time, item, winners, chat.id, user, bot)


def giveaway_run(time, item, winners, chat, user, bot):
    now = datetime.datetime.now()
    keyboard = [[InlineKeyboardButton("🎉", callback_data="1")]]
    seconds = False
    minutes = False
    hours = False
    days = False
    try:
        if time.endswith("s"):
            time = time.split("s")
            time1 = int(time[0])
            if time1 > 2592000:
                bot.send_message(
                    chat_id=chat, text="Giveaways cannot be greater than 30 days!")
            else:
                seconds = True
                added = now+datetime.timedelta(seconds=int(time1))
                time = f"{time1} Seconds"
        elif time.endswith("m"):
            time = time.split("m")
            time1 = int(time[0])
            if time1 > 43200:
                bot.send_message(
                    chat_id=chat, text="Giveaways cannot be greater than 30 days!")
            else:
                minutes = True
                added = now+datetime.timedelta(minutes=int(time1))
                time = f"{time1} Minutes"
        elif time.endswith("h"):
            time = time.split("h")
            time1 = int(time[0])
            if time1 > 720:
                bot.send_message(
                    chat_id=chat, text="Giveaways cannot be greater than 30 days!")
            else:
                hours = True
                added = now+datetime.timedelta(hours=int(time1))
                time = f"{time1} Hours"
        elif time.endswith("d"):
            time = time.split("d")
            time1 = int(time[0])
            if time1 > 30:
                bot.send_message(
                    chat_id=chat, text="Giveaways cannot be greater than 30 days!")
            else:
                days = True
                added = now+datetime.timedelta(days=int(time1))
                time = f"{time1} Days"

    except:
        bot.send_message(
            chat_id=chat, text=f"💥 Failed to parse time from <code>{time}</code> \nExample usage: <code>/gstart 30m 5w Awesome T-Shirt</code>", parse_mode=ParseMode.HTML)
    try:
        if seconds or minutes or hours or days == True:
            if now.strftime("%d %m %Y") == added.strftime("%d %m %Y"):
                end = added.strftime("Today at %I:%M %p")
            else:
                end = added.strftime("%m/%d/%Y")

            item = str(item)
            item = item.replace("[", "").replace("]", "").replace(
                "'", "").replace(",", "")
            msg = bot.send_message(chat_id=chat, text=f'''🎉 GIVEAWAY 🎉

<b>{item}</b>

React with 🎉 to enter!
Ends: in {time} ({added.strftime("%B %d, %Y %I:%M %p")})
Hosted by: <a href="tg://user?id={user.id}">{user.first_name}</a>

<i>{winners} Winner(s) | Ends at • {end}</i>
        ''', parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
            time1 = int(time1)
            name = str(chat)+str(msg.message_id)
            if seconds == True:
                j.run_once(callback, time1, context=[
                    chat, msg.message_id], name=name)
            elif minutes == True:
                j.run_once(callback, time1*60,
                           context=[chat, msg.message_id], name=name)
            elif hours == True:
                j.run_once(callback, time1*60*60,
                           context=[chat, msg.message_id], name=name)
            elif days == True:
                j.run_once(callback, time1*60*60*24,
                           context=[chat, msg.message_id], name=name)
            try:
                cur.execute('''CREATE TABLE giveaway (
                    id BIGSERIAL PRIMARY KEY NOT NULL,
                    chat_id BIGINT NOT NULL,
                    message_id BIGINT NOT NULL,
                    item_name TEXT,
                    winners INT
                    )''')
                cur.execute("INSERT INTO giveaway (chat_id, message_id, item_name, winners) VALUES (%s, %s, %s, %s)",
                            (chat, msg.message_id, str(item), winners))
            except:
                cur.execute("ROLLBACK")
                cur.execute("INSERT INTO giveaway (chat_id, message_id, item_name, winners) VALUES (%s, %s, %s, %s)",
                            (chat, msg.message_id, str(item), winners))
            conn.commit()
        else:
            pass
    except Exception:
        print(traceback.format_exc())


def callback(context: telegram.ext.CallbackContext):
    details = context.job.context
    bot = context.bot
    chat_id = details[0]
    message_id = details[1]
    cur.execute(
        f"SELECT item_name FROM giveaway WHERE chat_id={chat_id} AND message_id={message_id}")
    row = cur.fetchall()
    item_name = row[0][0]
    bot.send_message(
        chat_id=chat_id, text=f"Congratulation you won <b>{item_name}</b>", parse_mode=ParseMode.HTML)
    cur.execute(
        f"DELETE FROM giveaway WHERE chat_id={chat_id} AND message_id={message_id}")
    conn.commit()


def gend(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    bot = context.bot
    if chat.type == "private":
        bot.send_message(
            chat_id=chat.id, text=f"💥 This command cannot be used in Private Messages!")
    else:
        members = bot.get_chat_member(chat_id=chat.id, user_id=user.id)
        allowed = ["administrator", "creator"]
        if members.status not in allowed:
            bot.send_message(
                chat_id=chat.id, text="You don't have administrator privileges")
        else:
            user_says = " ".join(context.args)
            user_says = user_says.split(" ")
            message_id = user_says[0]
            if user_says == [""] or [" "]:
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
                    bot.send_message(
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
                    bot.send_message(
                        chat_id=chat.id, text="💥 That is not a valid message ID! Try running without an ID to use the most recent giveaway in a channel.")


def glist(update: Update, context: CallbackContext):
    chat = update.effective_chat
    bot = context.bot
    if chat.type == 'private':
        bot.send_message(
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
            bot.send_message(
                chat_id=chat.id, text=message_to_send, parse_mode=ParseMode.HTML)
            message_list.clear()
        except:
            bot.send_message(
                chat_id=chat.id, text="💥 There are no giveaways running on the channel!", parse_mode=ParseMode.HTML)


STORE_CHANNEL, STORE_TIME, STORE_WINNER, STORE_ITEM = range(4)


def gcreate(update: Update, context: CallbackContext):
    if update.effective_chat.type == "private":
        update.message.reply_text('''🎉 Alright! Let's set up your giveaway! First, what channel do you want the giveaway in?
You can type <code>!cancel</code> at any time to cancel creation.

<i>Please type the id of the channel</i>''', parse_mode=ParseMode.HTML)
        return STORE_CHANNEL
    else:
        update.message.reply_text(
            "💥 This command can only be used in Private Messages!")
        return ConversationHandler.END


def store_channel(update: Update, context: CallbackContext):
    channel_id = update.message.text
    context.chat_data["channel_id"] = channel_id
    try:
        member = context.bot.get_chat_member(chat_id=int(
            context.chat_data["channel_id"]), user_id=update.effective_user.id)
        allowed = ["administrator", "creator"]
        if member.status in allowed:
            update.message.reply_text(f'''🎉 Sweet! The giveaway will be in <b>{context.bot.get_chat(channel_id).title}</b>! Next, how long should the giveaway last?

<i>Please enter the duration of the giveaway in seconds.
Alternatively, enter a duration in minutes and include an M at the end, or days and include a D.</i>''', parse_mode=ParseMode.HTML)
            return STORE_TIME
    except:
        update.message.reply_text(f'''💥 Uh oh, I couldn't find any channels called '{channel_id}'! Try again!
        
<i>Make sure I am added as an administrator in the channel you are specifying</i>''', parse_mode=ParseMode.HTML)
        del context.chat_data["channel_id"]
        return STORE_CHANNEL


def store_time(update: Update, context: CallbackContext):
    time = update.message.text
    context.chat_data["time"] = time
    time = time.split(" ")[0]
    try:
        if time.endswith("s"):
            time = f'''{int(time.split("s")[0])} seconds'''
        elif time.endswith("m"):
            time = f'''{int(time.split("m")[0])} minutes'''
        elif time.endswith("h"):
            time = f'''{int(time.split("h")[0])} hours'''
        elif time.endswith("d"):
            time = f'''{int(time.split("d")[0])} days'''
        else:
            time = f"{int(time)} seconds"
        update.message.reply_text(f'''🎉 Neat! This giveaway will last <b>{time}</b>! Now, how many winners should there be?

<i>Please enter a number of winners between 1 and 20.</i>''', parse_mode=ParseMode.HTML)
        return STORE_WINNER
    except:
        update.message.reply_text('''💥 Hm. I can't seem to get a number from that. Can you try again?

<i>Please enter the duration of the giveaway in seconds.
Alternatively, enter a duration in minutes and include an M at the end, or days and include a D.</i>''', parse_mode=ParseMode.HTML)
        return STORE_TIME


def store_winner(update: Update, context: CallbackContext):
    try:
        winners = int(update.message.text)
        if winners > 20 or winners < 1:
            update.message.reply_text(
                '''💥 Hey! I can only support 1 to 20 winners!

<i>Please enter a number of winners between 1 and 20.</i>
''', parse_mode=ParseMode.HTML)
            return STORE_WINNER
        else:
            if winners == 1:
                winner = "1 winner"
            else:
                winner = f"{winners} winners"

            context.chat_data['winner'] = winners
            update.message.reply_text(f'''🎉 Ok! {winner} it is! Finally, what do you want to give away?

<i>Please enter the giveaway prize. This will also begin the giveaway.</i>''', parse_mode=ParseMode.HTML)
        return STORE_ITEM
    except:
        update.message.reply_text(
            '''💥 Uh... that doesn't look like a valid number.

<i>Please enter a number of winners between 1 and 20.</i>''', parse_mode=ParseMode.HTML)
        return STORE_WINNER


def store_item(update: Update, context: CallbackContext):
    item = update.message.text
    update.message.reply_text(
        f'''🎉 Done! The giveaway for the <b>{item}</b> is starting in <b>{context.bot.get_chat(int(context.chat_data['channel_id'])).title}</b>''', parse_mode=ParseMode.HTML)

    giveaway_run(time=context.chat_data['time'], item=item, winners=int(context.chat_data['winner']), chat=int(
        context.chat_data['channel_id']), user=update.effective_user, bot=context.bot)

    del context.chat_data['channel_id'], context.chat_data['time'], context.chat_data['winner']
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text('''💥 Alright, I guess we're not having a giveaway after all...

<i>Giveaway creation has been cancelled.</i>''', parse_mode=ParseMode.HTML)
    try:
        del context.chat_data['channel_id'], context.chat_data['time'], context.chat_data['winner']
    except:
        pass
    return ConversationHandler.END


def gcreate_callback(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(f'''💥 Uh oh! You took longer than 2 minutes to respond, <a href="tg://user?id={user.id}">{user.first_name}</a>!

<i>Giveaway creation has been cancelled.</i>''', parse_mode=ParseMode.HTML)
    try:
        del context.chat_data['channel_id'], context.chat_data['time'], context.chat_data['winner']
    except:
        pass
    return ConversationHandler.TIMEOUT


def error_handler(update: object, context: CallbackContext):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )
    context.bot.send_message(chat_id=-719683560, text=message, parse_mode=ParseMode.HTML)
    

if __name__ == "__main__":
    TOKEN=BOTTOKEN
    u = Updater(TOKEN)
    j = u.job_queue
    dp = u.dispatcher
    dp.add_handler(PrefixHandler(["!", "/"], ["start", "gabout"], start))
    dp.add_handler(PrefixHandler(["!", "/"], "ginvite", ginvite))
    dp.add_handler(PrefixHandler(["!", "/"], "ghelp", ghelp))
    dp.add_handler(PrefixHandler(["!", "/"], "gstart", gstart))
    dp.add_handler(PrefixHandler(["!", "/"], "gend", gend))
    dp.add_handler(PrefixHandler(["!", "/"], "glist", glist))
    conv_handler = ConversationHandler(
        entry_points=[PrefixHandler(["!", "/"], "gcreate", gcreate)],
        states={
            STORE_CHANNEL: [MessageHandler(Filters.all and ~Filters.text(["/cancel", "!cancel"]), store_channel)],
            STORE_TIME: [MessageHandler(Filters.all and ~Filters.text(["/cancel", "!cancel"]), store_time)],
            STORE_WINNER: [MessageHandler(Filters.all and ~Filters.text(["/cancel", "!cancel"]), store_winner)],
            STORE_ITEM: [MessageHandler(Filters.all and ~Filters.text(["/cancel", "!cancel"]), store_item)],
            ConversationHandler.TIMEOUT: [
                MessageHandler(Filters.all, gcreate_callback)]
        },
        fallbacks=[PrefixHandler(["!", "/"], "cancel", cancel)],
        allow_reentry=True,
        conversation_timeout=10
    )
    dp.add_handler(conv_handler)
    dp.add_error_handler(error_handler)
    PORT = int(os.environ.get('PORT', 5000))
    u.start_webhook(listen="0.0.0.0",port=int(PORT),url_path=TOKEN, webhook_url="https://yourherokuappname.herokuapp.com/" + TOKEN)
    u.idle()
