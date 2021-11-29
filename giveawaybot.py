from telegram import *
from telegram.ext import *
import telegram, telegram.ext, psycopg, uuid, logging, datetime, html, traceback

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

u = Updater('TOKEN')
j = u.job_queue

#Connecting to the database
conn=psycopg.connect(host="localhost",user="postgres",dbname="test",password="gigabyte1")
cur=conn.cursor()

def start(update: Update, context:CallbackContext):
    if update.effective_chat.type!='private': 
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hey! I am alive :) PM me for any kind of help 😉")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'''🎉 All about <b>GiveawayBot</b> 🎉

<b>Hold giveaways quickly and easily!</b>

Hello! I'm <b>GiveawayBot</b>, and I'm here to make it as easy as possible to hold giveaways on your Telegram group/channel! I was created by <a href='tg://user?id=2056511700'>Aditya</a> <code>(2056511700)</code> using the <a href='https://github.com/python-telegram-bot/python-telegram-bot'>Python-telegram-bot</a> library (13.8.1) and <a href='https://www.postgresql.org/'>Postgresql database</a> (14.1). Check out my commands by typing <code>!ghelp</code>''', parse_mode=ParseMode.HTML, disable_web_page_preview=True)

def ghelp(update: Update, context:CallbackContext):
    if update.effective_chat.type=='private': 
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'''🎉 GiveawayBot commands: 

<b>!ginvite</b> - shows how to invite the bot
<b>!gabout</b> - shows info about the bot

<u>Giveaway</u>:

<b>!gcreate</b> - creates a giveaway (interactive setup)
<b>!gstart {html.escape('<time>')} [winners]w [prize]</b> - starts a giveaway
<b>!gend [messageId]</b> - ends (picks a winner for) the specified or latest giveaway in the current channel
<b>!greroll [messageId]</b> - re-rolls the specified or latest giveaway in the current channel
<b>!glist</b> - lists active giveaways on the channel

Do not include {html.escape('<>')} nor [] - {html.escape('<>')} means required and [] means optional.
For additional help contact <a href='tg://user?id=2056511700'>Aditya</a>
''', parse_mode=ParseMode.HTML)

def ginvite(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='''🎉 Hello! I'm <b>GiveawayBot</b>! I help to make giveaways quick and easy!
You can add me to your group with this link:

🔗 https://t.me/dctggiveawaybot?startgroup=true

Check out my commands by typing <code>!ghelp</code>''')
def button(update: Update, context: CallbackContext): # There is no use of this function as of now, will implement this when telegram releases message reactions as mentioned here - https://t.me/contest_ru/17
    query = update.callback_query
    choice = query.data
    query.answer
    msg=update.effective_message.message_id
    user_id=update.callback_query.from_user.id
    if choice=='1':
        members=context.bot.get_chat_member(chat_id=update.effective_chat.id, user_id=user_id)
        member=['administrator', 'creator', 'member', 'restricted', 'owner']
        if members.status in member:
            cur.execute(f"SELECT giveaway_id FROM giveaway WHERE chat_id={update.effective_chat.id} AND message_id={msg}")
            row=cur.fetchall()
            cur.execute(f'''INSERT INTO giveaway (users_id) 
            ''')
            conn.commit()
            update.callback_query.answer(text='Participation successful!', show_alert=True)
        else:
            update.callback_query.answer(text='Join the channel to participate', show_alert=True)


def gstart(update: Update, context: CallbackContext):
    chat=update.effective_chat
    user=update.effective_user
    if chat.type=='private':
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"💥 This command cannot be used in Private Messages!")
    else:
        user_says=' '.join(context.args)
        keyboard=[[InlineKeyboardButton('🎉', callback_data='1')]]
        user_says=user_says.split(' ')
        item=user_says[2:]
        now=datetime.datetime.now()
        seconds=False
        minutes=False
        hours=False
        days=False
        try:
            tym=user_says[0]
        except:
            context.bot.send_message(chat_id=chat.id, text=f'''💥 Please include a length of time, and a number of winners and a prize! Example usage: <code>/gstart 30m 5w Awesome T-Shirt</code>''', parse_mode=ParseMode.HTML)
        try:
            winners=user_says[1].split('w')
            winners=int(winners[0])
        except: 
            winners=1
            item=user_says[1:]   
        try:
            if tym.endswith('s'):
                seconds=True
                tym=tym.split('s')
                added=now+datetime.timedelta(seconds=int(tym[0]))
                tym1=tym[0]
                tym=f'{tym[0]} Seconds'
            elif tym.endswith('m'):
                minutes=True
                tym=tym.split('m')
                added=now+datetime.timedelta(minutes=int(tym[0]))
                tym1=tym[0]
                tym=f'{tym[0]} Minutes'
            elif tym.endswith('h'):
                hours=True
                tym=tym.split('h')
                added=now+datetime.timedelta(hours=int(tym[0]))
                tym1=tym[0]
                tym=f'{tym[0]} Hours'
            elif tym.endswith('d'):
                days=True
                tym=tym.split('d')
                added=now+datetime.timedelta(days=int(tym[0]))
                tym1=tym[0]
                tym=f'{tym[0]} Days'
        except:
            context.bot.send_message(chat_id=chat.id, text=f'''💥 Failed to parse time from <code>{tym}</code>
Example usage: <code>/gstart 30m 5w Awesome T-Shirt</code>''', parse_mode=ParseMode.HTML)
        try:
            if now.strftime('%d %m %Y')==added.strftime('%d %m %Y'):
                end=added.strftime('Today at %I:%M %p')
            else:
                end=added.strftime('%m/%d/%Y')
            item=str(item)
            item=item.replace('[', '').replace(']', '').replace("'", '').replace(",", '')
            msg=context.bot.send_message(chat_id=chat.id, text=f'''🎉 GIVEAWAY 🎉

<b>{item}</b>

React with 🎉 to enter!
Ends: in {tym} ({added.strftime("%B %d, %Y %I:%M %p")})
Hosted by: <a href='tg://user?id={user.id}'>{user.first_name}</a>

<i>{winners} Winner(s) | Ends at • {end}</i>
        ''', parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
            tym1=int(tym1)
            name=str(chat.id)+str(msg.message_id)
            if seconds==True:
                j.run_once(callback, tym1, context=[chat.id, msg.message_id], name=name)
            elif minutes==True:
                j.run_once(callback, tym1*60, context=[chat.id, msg.message_id], name=name)
            elif hours==True:
                j.run_once(callback, tym1*60*60, context=[chat.id, msg.message_id], name=name)
            elif days==True:
                j.run_once(callback, tym1*60*60*24, context=[chat.id, msg.message_id], name=name)

            try:
                table=f'''CREATE TABLE giveaway(
                id BIGSERIAL NOT NULL PRIMARY KEY,
                chat_id BIGINT NOT NULL,
                message_id BIGINT NOT NULL,
                item_name TEXT,
                winners INT
                )
                '''
                cur.execute(table)
                cur.execute("INSERT INTO giveaway (chat_id, message_id, item_name, winners) VALUES (%s, %s, %s, %s)", (chat.id, msg.message_id, str(item), winners))
            except psycopg.errors.DuplicateTable:
                cur.execute("ROLLBACK")
                cur.execute("INSERT INTO giveaway (chat_id, message_id, item_name, winners) VALUES (%s, %s, %s, %s)", (chat.id, msg.message_id, str(item), winners))
            conn.commit() 
        except Exception:
            print(traceback.format_exc())

def callback(context: telegram.ext.CallbackContext):
    details=context.job.context
    chat_id=details[0]
    message_id=details[1]
    cur.execute(f"SELECT item_name FROM giveaway WHERE chat_id={chat_id} AND message_id={message_id}")
    row=cur.fetchall()
    item_name=row[0][0]
    context.bot.send_message(chat_id=chat_id, text=f"Congratulation you won <b>{item_name}</b>", parse_mode=ParseMode.HTML)
    cur.execute(f"DELETE FROM giveaway WHERE chat_id={chat_id} AND message_id={message_id}")
    conn.commit()

def gend(update: Update, context: CallbackContext):
    chat=update.effective_chat
    user=update.effective_user
    members=context.bot.get_chat_member(chat_id=chat.id, user_id=user.id)
    allowed=['administrator', 'creator', 'owner']
    if members.status not in allowed:
        context.bot.send_message(chat_id=chat.id, text="You don't have administrator privileges")
    else:
        try:
            user_says=' '.join(context.args)
            user_says= user_says.split(' ')
            message_id=user_says[0]
            if message_id == '' or ' ':
                try:
                    cur.execute(f'SELECT message_id FROM giveaway WHERE id=(SELECT MAX(id) FROM giveaway)')
                    row=cur.fetchall()
                    message_id=str(row[0][0])
                except:
                    context.bot.send_message(chat_id=chat.id, text=f"There is not any giveaway running in this chat!")
            chat=str(chat.id)
            current_jobs = j.get_jobs_by_name(chat+message_id)
            for job in current_jobs:
                job.run(context.dispatcher)
                job.schedule_removal()
        except:
            context.bot.send_message(chat_id=chat.id, text=f"There is not any giveaway running in this chat with that giveaway id!")

def greroll(update: Update, context: CallbackContext):
    allowed=['administrator', 'creator', 'owner']
    member=context.bot.get_chat_member(chat_id=update.effective_chat.id, user_id=update.effective_user.id)
    if member.status not in allowed:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You don't have administrator privileges")
    else:
        try:
            user_says=' '.join(context.args)
            user_says= user_says.split(' ')
            giveaway_id=user_says[0]
            if giveaway_id == '' or ' ':
                try:
                    cur.execute(f'SELECT giveaway_id FROM giveaway WHERE chat_id={update.effective_chat.id} AND id=(SELECT MAX(id) FROM giveaway)')
                    row=cur.fetchall()
                    giveaway_id=row[0][0] 
                except:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f"There is no giveaway with that giveaway id in this chat")
        except:
            pass

def glist(update: Update, context: CallbackContext):
    chat=update.effective_chat
    try:
        cur.execute(f'SELECT message_id FROM giveaway where chat_id={chat.id}')
        message_id=cur.fetchall()
        message_ids=[]
        message_list=[]
        for ids in message_id:
            message_ids.append(ids[0])
        for i in message_ids:
            cur.execute(f"SELECT winners FROM giveaway WHERE message_id={i} AND chat_id={chat.id}")
            winner=cur.fetchall()
            for win in winner:
                winners=win[0]
            cur.execute(f"SELECT item_name FROM giveaway WHERE message_id={i} AND chat_id={chat.id}")
            items_name=cur.fetchall()
            for item in items_name:
                itemname=item[0]
            message_to_send=f"<code>{i}</code> | <b>{winners}</b> Winners | Prize: <b>{itemname}</b> |"
            message_list.append(message_to_send)
        message_to_send='\n'.join(message_list)
        context.bot.send_message(chat_id=chat.id, text=message_to_send, parse_mode=ParseMode.HTML)
    except:
        context.bot.send_message(chat_id=chat.id, text='💥 There are no giveaways running on the channel!', parse_mode=ParseMode.HTML)

def greroll(update: Update, context: CallbackContext):
    pass

if __name__ == '__main__':
    dp = u.dispatcher
    dp.add_handler(PrefixHandler(['!', '/'], ['start', 'gabout'], start))
    dp.add_handler(PrefixHandler(['!', '/'], 'ginvite', ginvite))
    dp.add_handler(PrefixHandler(['!', '/'], 'ghelp', ghelp))
    dp.add_handler(PrefixHandler(['!', '/'], 'gstart', gstart))
    dp.add_handler(PrefixHandler(['!', '/'], 'gend', gend))
    dp.add_handler(PrefixHandler(['!', '/'], 'glist', glist))
    dp.add_handler(PrefixHandler(['!', '/'], 'greroll', greroll))
    dp.add_handler(CallbackQueryHandler(button))
    u.start_polling()
    u.idle()
