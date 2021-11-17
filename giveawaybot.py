from telegram import *
from telegram.ext import *
from telegram.utils import *
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
def ghyll(update: Update, context:CallbackContext):
    if update.effective_chat.type=='private': 
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'''Here's the commands that the bot supports: 
<b>!gstart {html.escape('<time>')} [winners]w [prize]</b> - starts a giveaway
<b>!gend [giveawayId]</b> - ends (picks a winner for) the specified or latest giveaway in the current channel
<b>!greroll [giveawayId]</b> - re-rolls the specified or latest giveaway in the current channel
<b>!glist</b> - lists active giveaways on the server

Do not include {html.escape('<>')} nor [] - {html.escape('<>')} means required and [] means optional.
''', parse_mode=ParseMode.HTML)
    else:
        keyboard=[[InlineKeyboardButton(text='Click here for help!', url=f'http://t.me/dctggiveawaybot?start=ghelp')]]
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Contact me in PM to get the list of available commands.", reply_markup=InlineKeyboardMarkup(keyboard))

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    choice = query.data
    msg=update.effective_message.message_id
    user_id=update.callback_query.from_user.id
    if choice=='1':
        members=context.bot.get_chat_member(chat_id=update.effective_chat.id, user_id=user_id)
        member=['administrator', 'creator', 'member', 'restricted', 'owner']
        if members.status in member:
            cur.execute(f"SELECT giveaway_id FROM giveaway WHERE chat_id={update.effective_chat.id} AND message_id={msg}")
            row=cur.fetchall()
            giveaway_id=row[0][0]
            cur.execute(f"")
            conn.commit()
            update.callback_query.answer(text='Participation successful!', show_alert=True)
        else:
            update.callback_query.answer(text='Join the channel to participate', show_alert=True)


def gstart(update: Update, context: CallbackContext):
    if update.effective_chat.type=='private':
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"💥 This command cannot be used in Private Messages!")
    else:
        giveaway_id=uuid.uuid4()
        user_says=' '.join(context.args)
        keyboard=[[InlineKeyboardButton('🎉', callback_data='1', context=giveaway_id)]]
        user_says=user_says.split(' ')
        item=user_says[2:]
        chat_id=update.effective_chat.id
        now=datetime.datetime.now()
        seconds=False
        minutes=False
        hours=False
        days=False
        try:
            tym=user_says[0]
            winners=user_says[1]
        except:
            context.bot.send_message(chat_id=chat_id, text=f'''💥 Please include a length of time, and a number of winners and a prize! Example usage: <code>/gstart 30m 5w Awesome T-Shirt</code>''', parse_mode=ParseMode.HTML)
        try:
            winners=winners.split('w' or 'W')
            winners=int(winners[0])
        except: 
            winners=1
            item=user_says[1:]   
        try:
            #time
            if tym.endswith('s' or 'S'):
                seconds=True
                tym=tym.split('s' or 'S')
                added=now+datetime.timedelta(seconds=int(tym[0]))
                tym1=tym[0]
                tym=f'{tym[0]} Seconds'
            elif tym.endswith('m' or 'M'):
                minutes=True
                tym=tym.split('m' or 'M')
                added=now+datetime.timedelta(minutes=int(tym[0]))
                tym1=tym[0]
                tym=f'{tym[0]} Minutes'
            elif tym.endswith('h' or 'H'):
                hours=True
                tym=tym.split('h' or 'H')
                added=now+datetime.timedelta(hours=int(tym[0]))
                tym1=tym[0]
                tym=f'{tym[0]} Hours'
            elif tym.endswith('d' or 'D'):
                days=True
                tym=tym.split('d' or 'D')
                added=now+datetime.timedelta(days=int(tym[0]))
                tym1=tym[0]
                tym=f'{tym[0]} Days'
        except:
            context.bot.send_message(chat_id=chat_id, text=f'''💥 Failed to parse time from <code>{tym}</code>
Example usage: <code>/gstart 30m 5w Awesome T-Shirt</code>''', parse_mode=ParseMode.HTML)
        try:
            if now.strftime('%d %m %Y')==added.strftime('%d %m %Y'):
                end=added.strftime('Today at %I:%M %p')
            else:
                end=added.strftime('%m/%d/%Y')
            item=str(item)
            item=item.replace('[', '').replace(']', '').replace("'", '').replace(",", '')
            msg=context.bot.send_message(chat_id=chat_id, text=f'''🎉 GIVEAWAY 🎉
<b>{item}</b>
React with 🎉 to enter!
Ends: in {tym} ({added.strftime("%B %d, %Y %I:%M %p")})
Hosted by: <a href='tg://user?id={update.effective_user.id}'>{update.effective_user.first_name}</a>
{winners} Winner(s) | Ends at • {end}
Giveaway id: <code>{giveaway_id}</code>
        ''', parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
            tym1=int(tym1)
            if seconds==True:
                j.run_once(callback, tym1, context=giveaway_id, name=str(giveaway_id))
            elif minutes==True:
                j.run_once(callback, tym1*60, context=giveaway_id, name=str(giveaway_id))
            elif hours==True:
                j.run_once(callback, tym1*60*60, context=giveaway_id, name=str(giveaway_id))
            elif days==True:
                j.run_once(callback, tym1*60*60*24, context=giveaway_id, name=str(giveaway_id))

            try:
                table=f'''CREATE TABLE giveaway(
                id BIGSERIAL NOT NULL,
                giveaway_id TEXT NOT NULL PRIMARY KEY,
                chat_id BIGINT NOT NULL,
                message_id BIGINT NOT NULL,
                item_name TEXT,
                winners INT,
                users_id TEXT
                )
                '''
                cur.execute(table)
                cur.execute("INSERT INTO giveaway (giveaway_id, chat_id, message_id, item_name, winners) VALUES (%s, %s, %s, %s, %s)", (giveaway_id, chat_id, msg.message_id, str(item), winners))
            except psycopg.errors.DuplicateTable:
                cur.execute("ROLLBACK")
                cur.execute("INSERT INTO giveaway (giveaway_id, chat_id, message_id, item_name, winners) VALUES (%s, %s, %s, %s, %s)", (giveaway_id, chat_id, msg.message_id, str(item), winners))
            conn.commit() 
        except Exception:
            print(traceback.format_exc())

def callback(context: telegram.ext.CallbackContext):
    cur.execute(f"SELECT chat_id, item_name FROM giveaway WHERE giveaway_id='{context.job.context}'")
    row=cur.fetchall()
    chat_id=row[0][0]
    item_name=row[0][1]
    giveaway_id=context.job.context
    context.bot.send_message(chat_id=chat_id, text=f"Congratulation you won <b>{item_name}</b>", parse_mode=ParseMode.HTML)
    j.run_once(reroll_timer, 60*60*24*7, context=giveaway_id)
 

def reroll_timer(context: telegram.ext.CallbackContext):
    cur.execute(f"DELETE FROM giveaway WHERE giveaway_id='{context.job.context}'")
    conn.commit()

def gend(update: Update, context: CallbackContext):
    members=context.bot.get_chat_member(chat_id=update.effective_chat.id, user_id=update.effective_user.id)
    allowed=['administrator', 'creator', 'owner']
    if members.status not in allowed:
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
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f"There is not any giveaway running in this chat!")
            current_jobs = j.get_jobs_by_name(giveaway_id)
            for job in current_jobs:
                job.run(context.dispatcher)
                job.schedule_removal()
            j.run_once(reroll_timer, 60*60*24*7, context=giveaway_id)
        except:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"There is not any giveaway running in this chat with that giveaway id!")

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
    try:
        cur.execute(f'SELECT giveaway_id FROM giveaway where chat_id={update.effective_chat.id}')
        giveaway_id=cur.fetchall()
        giveaway_ids=[]
        message_list=[]
        for ids in giveaway_id:
            giveaway_ids.append(ids[0])
        for i in giveaway_ids:
            cur.execute(f"SELECT winners FROM giveaway where giveaway_id='{i}'")
            winner=cur.fetchall()
            for win in winner:
                winners=win[0]
            cur.execute(f"SELECT item_name FROM giveaway WHERE giveaway_id='{i}'")
            items_name=cur.fetchall()
            for item in items_name:
                itemname=item[0]
            message_to_send=f"<code>{i}</code> | <b>{winners}</b> Winners | Prize: {itemname} |"
            message_list.append(message_to_send)
        message_to_send='\n'.join(message_list)
        context.bot.send_message(chat_id=update.effective_chat.id, text=message_to_send, parse_mode=ParseMode.HTML)
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text='💥 There are no giveaways running on the channel!', parse_mode=ParseMode.HTML)

if __name__ == '__main__':
    dp = u.dispatcher
    dp.add_handler(PrefixHandler(['!', '/'], 'start', start))
    dp.add_handler(PrefixHandler(['!', '/'], 'ghelp', ghyll))
    dp.add_handler(PrefixHandler(['!', '/'], 'gstart', gstart))
    dp.add_handler(PrefixHandler(['!', '/'], 'gend', gend))
    dp.add_handler(PrefixHandler(['!', '/'], 'glist', glist))
    dp.add_handler(CallbackQueryHandler(button))
    u.start_polling()
    u.idle()
