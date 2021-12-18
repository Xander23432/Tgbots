from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, Chat, ChatMember, ChatMemberUpdated, ChatAction
from telegram.ext import Updater, CallbackContext, PrefixHandler, ConversationHandler, MessageHandler, Filters, ChatMemberHandler, CallbackQueryHandler
from ptbcontrib.ptb_sqlalchemy_jobstore import PTBSQLAlchemyJobStore
from ptbcontrib.postgres_persistence import PostgresPersistence
from pytz import timezone
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

conn = psycopg.connect(host="host", user="user",
                       dbname="dbname", password="password", port=port)


cur = conn.cursor()


def member_status(chat, user, context):
    allowed = [ChatMember.ADMINISTRATOR, ChatMember.CREATOR]
    member = context.bot.get_chat_member(chat, user).status
    if member in allowed:
        return "yes"
    else:
        return "no"


def gabout(update: Update, context: CallbackContext):
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    if update.effective_chat.type != Chat.PRIVATE:
        update.message.reply_text(
            "Hey! I am alive :) PM me for any kind of help 😉")
    else:
        update.message.reply_text(f'''🎉 All about <b>GiveawayBot</b> 🎉

<b>Hold giveaways quickly and easily!</b>

Hello! I'm <b>GiveawayBot</b>, and I'm here to make it as easy as possible to hold giveaways on your Telegram group/channel! I was created by <a href='tg://user?id=2056511700'>Aditya</a> <code>(2056511700)</code> using the <a href='https://github.com/python-telegram-bot/python-telegram-bot'>Python-telegram-bot</a> library (13.8.1) and <a href='https://www.postgresql.org/'>Postgresql database</a> (14.1). Check out my commands by typing <code>!ghelp</code>''', parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def ghelp(update: Update, context: CallbackContext):
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    help_text = f'''🎉 GiveawayBot commands: 

<b>!ginvite</b> - shows how to invite the bot
<b>!gabout</b> - shows info about the bot
<b>!gping</b> - shows latency of the bot

<u>Giveaway</u>:

<b>!gcreate</b> - creates a giveaway (interactive setup)
<b>!gstart {html.escape("<time>")} [winners]w [prize]</b> - starts a giveaway
<b>!gend [messageId]</b> - ends (picks a winner for) the specified or latest giveaway in the current channel
<b>!greroll [messageId]</b> - re-rolls the specified or latest giveaway in the current channel
<b>!glist</b> - lists active giveaways on the channel

Do not include {html.escape("<>")} nor [] - {html.escape("<>")} means required and [] means optional.
For additional help contact <a href="tg://user?id=2056511700">Aditya</a>'''
    if update.effective_chat.type in [Chat.PRIVATE]:
        update.message.reply_text(text=help_text, parse_mode=ParseMode.HTML)
    else:
        pass


def ginvite(update: Update, context: CallbackContext):
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    update.message.reply_text('''🎉 Hello! I'm <b>GiveawayBot</b>! I help to make giveaways quick and easy!
You can add me to your group with this link:

🔗 https://t.me/dctggiveawaybot?startgroup=true

Check out my commands by typing <code>!ghelp</code>''', parse_mode=ParseMode.HTML)



def extract_status_change(chat_member_update: ChatMemberUpdated,):
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member",
                                                                       (None, None))
    if status_change is None:
        return None
    old_status, new_status = status_change
    was_member = (old_status in [ChatMember.MEMBER, ChatMember.CREATOR, ChatMember.ADMINISTRATOR, ] or (
        old_status == ChatMember.RESTRICTED and old_is_member is True))
    is_member = (new_status in [ChatMember.MEMBER, ChatMember.CREATOR, ChatMember.ADMINISTRATOR, ] or (
        new_status == ChatMember.RESTRICTED and new_is_member is True))
    return was_member, is_member


def set_timezone(update: Update, context: CallbackContext):
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result
    chat = update.effective_chat
    if chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        if not was_member and is_member:
            context.bot.send_message(chat_id=chat.id, text="Hey! Thanks for adding me in your group, kindly select your timezone to get started!",
                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Select Timezone", callback_data="TZ")]]))


keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("UTC", callback_data="UTC"),
            InlineKeyboardButton("India", callback_data="India"),
            InlineKeyboardButton("Russia", callback_data="Russia")
        ],
        [
            InlineKeyboardButton("Indonesia", callback_data="Indonesia"),
            InlineKeyboardButton("USA", callback_data="USA"),
            InlineKeyboardButton("Brazil", callback_data="Brazil")
        ]
    ]
)


def button(update: Update, context: CallbackContext):
    choice = update.callback_query.data
    timezoneset = False
    if update.effective_chat.type in [Chat.SUPERGROUP, Chat.GROUP]:
        member = member_status(update.effective_chat.id,
                               update.callback_query.from_user.id, context)
    else:
        member = member_status(
            int(context.user_data["chat_id"]), update.callback_query.from_user.id, context)
        context.dispatcher.chat_data[int(
            context.user_data["chat_id"])] = context.chat_data
    if member == 'yes':
        if choice == "TZ":
            update.callback_query.edit_message_text(text="Select your timezone/country\n<b>Note</b>:- If your country/timezone is not mentioned here you can request for yours on our <a href='https://github.com/aditya-yadav-27/Tgbots'>Github</a> profile",
                                                    reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        elif choice == "UTC":
            timezoneset = True
            context.chat_data["timezone"] = "UTC"
        elif choice == "India":
            timezoneset = True
            context.chat_data["timezone"] = "Asia/Kolkata"
        elif choice == "Russia":
            timezoneset = True
            context.chat_data["timezone"] = "Europe/Moscow"
        elif choice == "Indonesia":
            timezoneset = True
            context.chat_data["timezone"] = "Asia/Jakarta"
        elif choice == "USA":
            timezoneset = True
            context.chat_data["timezone"] = "EST"
        elif choice == "Brazil":
            timezoneset = True
            context.chat_data["timezone"] = "Brazil/East"
        if timezoneset == True:
            update.callback_query.answer(text="Timezone set successfully!")
            update.callback_query.edit_message_text(
                f"Successfully set timezone to {choice}")
    else:
        update.callback_query.answer(text="Only admins can use this")


def gconnect(update: Update, context: CallbackContext):
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    if update.effective_chat.type in [Chat.SUPERGROUP, Chat.GROUP, Chat.CHANNEL]:
        member = member_status(update.effective_chat.id,
                               update.effective_user.id, context)
        if member == "yes":
            context.bot.send_chat_action(
                chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            update.message.reply_text(
                f"Successfully connected with <b>{update.effective_chat.title()}</b>", parse_mode=ParseMode.HTML)
        else:
            update.message.reply_text(
                f"Connection to this chat is not allowed")
    else:
        try:
            chat_id = int(" ".join(context.args).split(" ")[0])
            member = member_status(chat_id, update.effective_user.id, context)
            if member == "yes":
                update.message.reply_text(
                    f"Successfully connected with <b>{context.bot.get_chat(chat_id).title}</b>", parse_mode=ParseMode.HTML)
                context.user_data["chat_id"] = chat_id
            else:
                update.message.reply_text(
                    f"Connection to that chat is not allowed")
        except:
            update.message.reply_text(
                "That doesn't seems like a valid chat id, try again!")


def gtimezone(update: Update, context: CallbackContext):
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    if update.effective_chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        member = member_status(update.effective_chat.id,
                               update.effective_user.id, context)
        if member == "yes":
            context.bot.send_message(chat_id=update.effective_chat.id, text="Select your timezone/country\n<b>Note</b>:- If your country/timezone is not mentioned here you can request for yours on our <a href='https://github.com/aditya-yadav-27/Tgbots'>Github</a> profile",
                                     reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        else:
            update.message.reply_text(
                "You don't have administrator privileges")
    elif update.effective_chat.type in [Chat.PRIVATE]:
        try:
            member = member_status(int(
                context.user_data["chat_id"]), update.effective_user.id, context)
            if member == "yes":
                update.message.reply_text("Select your timezone/country\n<b>Note</b>:- If your country/timezone is not mentioned here you can request for yours on our <a href='https://github.com/aditya-yadav-27/Tgbots'>Github</a> profile",
                                          reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            else:
                update.message.reply_text(
                    "You dont have administrator privileges")
        except:
            update.message.reply_text(
                f"use <code>!gconnect {html.escape('<chat_id>')}</code> command first!", parse_mode=ParseMode.HTML)


def gstart(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    context.bot.send_chat_action(
        chat_id=chat.id, action=ChatAction.TYPING)
    if chat.type == Chat.PRIVATE:
        update.message.reply_text(
            f"💥 This command cannot be used in Private Messages!")
    else:
        member = member_status(chat.id, user.id, context)
        if member == "yes":
            try:
                user_says = " ".join(context.args).split(" ")
                item = user_says[2:]
                time = user_says[0]
                if time == "":
                    raise ValueError
                else:
                    try:
                        winners = int(user_says[1].lower().split("w")[0])
                    except:
                        winners = 1
                        item = user_says[1:]
                    if winners > 20 or winners < 1:
                        update.message.reply_text(
                            "💥 Number of winners must be at least 1 and no larger than 20")
                    else:
                        item = " ".join(item)
                        giveaway_run(time, item, winners, chat.id,
                                     user, context, update)
            except:
                update.message.reply_text(
                    f"💥 Please include a length of time, and optionally a number of winners and a prize!\nExample usage: <code>!gstart 30m 5w Awesome T-Shirt</code>", parse_mode=ParseMode.HTML)
        else:
            update.message.repply_text(
                "You don't have administrator privileges")


def giveaway_run(time, item, winners, chat, user, context, update):
    bot = context.bot
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    try:
        now = datetime.datetime.now(timezone(context.chat_data["timezone"]))
        keyboard = [[InlineKeyboardButton("🎉", callback_data="1")]]
        seconds = False
        minutes = False
        hours = False
        days = False
        try:
            time = time.lower()
            if time.endswith("s"):
                splitted_time = time.rsplit("s", 1)
                time1 = int(splitted_time[0])
                if time1 > 1209600 or time1 < 10:
                    update.message.reply_text(
                        "💥 Giveaway time must not be shorter than 10 seconds and no longer than 2 weeks")
                else:
                    seconds = True
                    added = now+datetime.timedelta(seconds=int(time1))
                    time_word = f"{time1} Seconds"
            elif time.endswith("m"):
                splitted_time = time.rsplit("m", 1)
                time1 = int(splitted_time[0])
                if time1 > 20160 or time1 < 1/6:
                    update.message.reply_text(
                        "💥 Giveaway time must not be shorter than 10 seconds and no longer than 2 weeks")
                else:
                    minutes = True
                    added = now+datetime.timedelta(minutes=int(time1))
                    time_word = f"{time1} Minutes"
            elif time.endswith("h"):
                splitted_time = time.rsplit("h", 1)
                time1 = int(splitted_time[0])
                if time1 > 336 or time1 < 1/360:
                    update.message.reply_text(
                        "💥 Giveaway time must not be shorter than 10 seconds and no longer than 2 weeks")
                else:
                    hours = True
                    added = now+datetime.timedelta(hours=int(time1))
                    time_word = f"{time1} Hours"
            elif time.endswith("d"):
                splitted_time = time.rsplit("d", 1)
                time1 = int(splitted_time[0])
                if time1 > 14 or time1 < 1/8640:
                    update.message.reply_text(
                        "💥 Giveaway time must not be shorter than 10 seconds and no longer than 2 weeks")
                else:
                    days = True
                    added = now+datetime.timedelta(days=int(time1))
                    time_word = f"{time1} Days"
            else:
                raise ValueError
        except:
            update.message.reply_text(
                f"💥 Failed to parse time from <code>{time}</code>\nExample usage: <code>/gstart 30m 5w Awesome T-Shirt</code>", parse_mode=ParseMode.HTML)

        if seconds or minutes or hours or days == True:
            if now.strftime("%d %m %Y") == added.strftime("%d %m %Y"):
                end = added.strftime("Today at %I:%M %p")
            else:
                end = added.strftime("%m/%d/%Y")
            msg = bot.send_message(chat_id=chat, text=f'''🎉 GIVEAWAY 🎉

<b>{item}</b>

React with 🎉 to enter!
Ends: in {time_word} ({added.strftime("%B %d, %Y %I:%M %p")})
Hosted by: <a href="tg://user?id={user.id}">{user.first_name}</a>

<i>{winners} Winner(s)| Ends at • {end}</i>
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
                )'''
                            )
                cur.execute("INSERT INTO giveaway (chat_id, message_id, item_name, winners) VALUES (%s, %s, %s, %s)",
                            (chat, msg.message_id, str(item), winners))
            except:
                cur.execute("ROLLBACK")
                cur.execute("INSERT INTO giveaway (chat_id, message_id, item_name, winners) VALUES (%s, %s, %s, %s)",
                            (chat, msg.message_id, str(item), winners))
            conn.commit()
    except:
        update.message.reply_text(
            "Select your timezone first! use <code>!gtimezone</code> command", parse_mode=ParseMode.HTML)


def callback(context: CallbackContext):

    chat_id = context.job.context[0]
    message_id = context.job.context[1]
    context.bot.send_chat_action(
        chat_id=chat_id, action=ChatAction.TYPING)
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
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == Chat.PRIVATE:
        update.message.reply_text(
            f"💥 This command cannot be used in Private Messages!")
    else:
        member = member_status(chat.id, user.id, context)
        if member == "no":
            update.message.reply_text(
                "You don't have administrator privileges")
        else:
            message_id = " ".join(context.args).split(" ")[0]
            if message_id == "":
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
                    update.message.reply_text(
                        f"💥 I couldn't find any recent giveaways in this channel.")
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
                except:
                    update.message.reply_text(
                        "💥 That is not a valid message ID! Try running without an ID to use the most recent giveaway in a channel.")


def glist(update: Update, context: CallbackContext):
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    chat = update.effective_chat
    if chat.type == Chat.PRIVATE:
        update.message.reply_text(
            f"💥 This command cannot be used in Private Messages!")
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
                    remaining = next_run - datetime.datetime.now(
                        timezone(context.chat_data["timezone"]))
                    secs = remaining.total_seconds()
                    if secs < 60:
                        remaining_time = f"<b>{round(secs)}</b> seconds"
                    elif secs >= 60 and secs < 3600:
                        remaining_time = f"<b>{round(secs/60)}</b> minutes"
                    elif secs >= 3600 and secs < 86400:
                        remaining_time = f"<b>{round(secs/3600)}</b> hours"
                    else:
                        remaining_time = f"<b>{round(secs/86400)}</b> days"

                cur.execute(
                    f"SELECT item_name FROM giveaway WHERE message_id={i} AND chat_id={chat.id}")
                items_name = cur.fetchall()
                for item in items_name:
                    itemname = item[0]
                message_list.append(
                    f"<code>{i}</code> | <b>{winners}</b> Winners | Prize: <b>{itemname}</b> | Ends: in {remaining_time}")
            update.message.reply_text(
                "\n".join(message_list), parse_mode=ParseMode.HTML)
            message_list.clear()
            message_ids.clear()
        except:
            print(traceback.format_exc())
            update.message.reply_text(
                "💥 There are no giveaways running on the channel!", parse_mode=ParseMode.HTML)


STORE_CHANNEL, STORE_TIME, STORE_WINNER, STORE_ITEM = range(4)


def gcreate(update: Update, context: CallbackContext):
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    if update.effective_chat.type == Chat.PRIVATE:
        update.message.reply_text('''🎉 Alright! Let's set up your giveaway! First, what channel do you want the giveaway in?
You can type <code>!cancel</code> at any time to cancel creation.

<i>Please type the id of the channel</i>''', parse_mode=ParseMode.HTML)
        return STORE_CHANNEL
    else:
        update.message.reply_text(
            "💥 This command can only be used in Private Messages!")
        return ConversationHandler.END


def store_channel(update: Update, context: CallbackContext):
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    channel_id = update.message.text
    context.chat_data["channel_id"] = channel_id
    try:
        context.user_data["chat_id"]
    except:
        update.message.reply_text(
            "Uuh use <code>!gtimezone</code> command to set the timezone of the specified chat first!", parse_mode=ParseMode.HTML)
        return ConversationHandler.END
    try:
        member = member_status(int(
            context.chat_data["channel_id"]), update.effective_user.id, context)
        if member == "yes":
            update.message.reply_text(f'''🎉 Sweet! The giveaway will be in <b>{context.bot.get_chat(channel_id).title}</b>! Next, how long should the giveaway last?

<i>Please enter the duration of the giveaway in seconds.
Alternatively, enter a duration in minutes and include an M at the end, or days and include a D.</i>''', parse_mode=ParseMode.HTML)
            return STORE_TIME
        else:
            update.message.reply_text(
                "You don't have administrator privileges!")
            return ConversationHandler.END
    except:
        update.message.reply_text(f'''💥 Uh oh, I couldn't find any channels called '{channel_id}'! Try again!
        
<i>Make sure I am added as an administrator in the channel you are specifying</i>''', parse_mode=ParseMode.HTML)
        return STORE_CHANNEL


def store_time(update: Update, context: CallbackContext):
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    time = update.message.text
    context.chat_data["time"] = time
    time = time.split(" ")[0].lower()
    try:
        if time.endswith("s") and int(time.rsplit("s", 1)[0]) >= 10 and int(time.rsplit("s", 1)[0]) <= 1209600:
            time = f'''{int(time.rsplit("s", 1)[0])} seconds'''
        elif time.endswith("m") and int(time.rsplit("m", 1)[0]) >= 1/6 and int(time.rsplit("m", 1)[0]) <= 20160:
            time = f'''{int(time.rsplit("m", 1)[0])} minutes'''
        elif time.endswith("h") and int(time.rsplit("h", 1)[0]) >= 1/360 and int(time.rsplit("h", 1)[0]) <= 336:
            time = f'''{int(time.split("h", 1)[0])} hours'''
        elif time.endswith("d") and int(time.rsplit("d", 1)[0]) >= 1/8640 and int(time.rsplit("d", 1)[0]) <= 14:
            time = f'''{int(time.rsplit("d", 1)[0])} days'''
        else:
            try:
                if int(time) >= 10 and int(time) <= 1209600:
                    time = f"{int(time)} seconds"
                else:
                    raise ValueError
            except:
                update.message.reply_text('''💥 Oh! Sorry! Giveaway time must not be shorter than 10 seconds and no longer than 2 weeks Mind trying again?\n\n<i>Please enter the duration of the giveaway in seconds.\nAlternatively, enter a duration in minutes and include an M at the end, or days and include a D.</i>''', parse_mode=ParseMode.HTML)
                return STORE_TIME
        update.message.reply_text(f'''🎉 Neat! This giveaway will last <b>{time}</b>! Now, how many winners should there be?

<i>Please enter a number of winners between 1 and 20.</i>''', parse_mode=ParseMode.HTML)
        return STORE_WINNER
    except:
        update.message.reply_text('''💥 Hm. I can't seem to get a number from that. Can you try again?

<i>Please enter the duration of the giveaway in seconds.
Alternatively, enter a duration in minutes and include an M at the end, or days and include a D.</i>''', parse_mode=ParseMode.HTML)
        return STORE_TIME


def store_winner(update: Update, context: CallbackContext):
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING)
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
            context.chat_data["winner"] = winners
            update.message.reply_text(f'''🎉 Ok! {winner} it is! Finally, what do you want to give away?

<i>Please enter the giveaway prize. This will also begin the giveaway.</i>''', parse_mode=ParseMode.HTML)
        return STORE_ITEM
    except:
        update.message.reply_text(
            '''💥 Uh... that doesn't look like a valid number.

<i>Please enter a number of winners between 1 and 20.</i>''', parse_mode=ParseMode.HTML)
        return STORE_WINNER


def store_item(update: Update, context: CallbackContext):
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    item = update.message.text
    update.message.reply_text(
        f'''🎉 Done! The giveaway for the <b>{item}</b> is starting in <b>{context.bot.get_chat(int(context.chat_data["channel_id"])).title}</b>''', parse_mode=ParseMode.HTML)

    giveaway_run(time=context.chat_data["time"], item=item, winners=int(context.chat_data["winner"]), chat=int(
        context.chat_data["channel_id"]), user=update.effective_user, context=context, update=update)
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text('''💥 Alright, I guess we're not having a giveaway after all...

<i>Giveaway creation has been cancelled.</i>''', parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def gcreate_callback(update: Update, context: CallbackContext):
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    user = update.effective_user
    update.message.reply_text(f'''💥 Uh oh! You took longer than 2 minutes to respond, <a href="tg://user?id={user.id}">{user.first_name}</a>!

<i>Giveaway creation has been cancelled.</i>''', parse_mode=ParseMode.HTML)
    return ConversationHandler.TIMEOUT


def error_handler(update: object, context: CallbackContext):
    logger.error(msg="Exception while handling an update:",
                 exc_info=context.error)
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )
    context.bot.send_message(
        chat_id=-603250146, text=message, parse_mode=ParseMode.HTML)


if __name__ == "__main__":
    TOKEN = "Yourbottoken
    db_uri = "db_uri"
    u = Updater(TOKEN, persistence=PostgresPersistence(
        url=db_uri), use_context=True)
    j = u.job_queue
    dp = u.dispatcher
    dp.job_queue.scheduler.add_jobstore(
        PTBSQLAlchemyJobStore(dispatcher=dp, url=db_uri,),)
    dp.add_handler(PrefixHandler(["!", "/"], ["start", "gabout"], gabout))
    dp.add_handler(PrefixHandler(["!", "/"], "ginvite", ginvite))
    dp.add_handler(PrefixHandler(["!", "/"], "ghelp", ghelp))
    dp.add_handler(PrefixHandler(["!", "/"], "gstart", gstart))
    dp.add_handler(PrefixHandler(["!", "/"], "gend", gend))
    dp.add_handler(PrefixHandler(["!", "/"], "glist", glist))
    dp.add_handler(PrefixHandler(["!", "/"], "gtimezone", gtimezone))
    dp.add_handler(PrefixHandler(["!", "/"], "gconnect", gconnect))
    conv_handler = ConversationHandler(
        entry_points=[PrefixHandler(["!", "/"], "gcreate", gcreate)],
        states={
            STORE_CHANNEL: [MessageHandler(Filters.all & ~Filters.text(["/cancel", "!cancel"]), store_channel)],
            STORE_TIME: [MessageHandler(Filters.all & ~Filters.text(["/cancel", "!cancel"]), store_time)],
            STORE_WINNER: [MessageHandler(Filters.all & ~Filters.text(["/cancel", "!cancel"]), store_winner)],
            STORE_ITEM: [MessageHandler(Filters.all & ~Filters.text(["/cancel", "!cancel"]), store_item)],
            ConversationHandler.TIMEOUT: [
                MessageHandler(Filters.all, gcreate_callback)]
        },
        fallbacks=[PrefixHandler(["!", "/"], "cancel", cancel)],
        allow_reentry=True,
        conversation_timeout=120,
        name="gcreate_conversation",
        persistent=True
    )
    dp.add_handler(conv_handler)
    dp.add_error_handler(error_handler)
    dp.add_handler(ChatMemberHandler(
        set_timezone, ChatMemberHandler.MY_CHAT_MEMBER))
    dp.add_handler(CallbackQueryHandler(button))
    '''Below commented lines are for deploying the bot on heroku or some other host. In that situation you need to remove u.start_polling()'''
    # PORT = int(os.environ.get("PORT", 5000))
    # u.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN,
    #              webhook_url="https://yourappname.herokuapp.com/" + TOKEN, drop_pending_updates=True)
    u.start_polling()
    u.idle()
