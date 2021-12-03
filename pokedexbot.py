from telegram.ext import CallbackContext, Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
import requests
import json
import html
import random
import logging


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


keyboard = [
    [
        InlineKeyboardButton("Data", callback_data='1'),
        InlineKeyboardButton("Randpoke", callback_data='2'),
        InlineKeyboardButton("Shiny", callback_data='3')
    ],
    [
        InlineKeyboardButton("Stats", callback_data='4'),
        InlineKeyboardButton("Move", callback_data='5'),
        InlineKeyboardButton("Cry", callback_data='6')
    ]
]
reply_markup = InlineKeyboardMarkup(keyboard)
help_text = "Here's the commands that bot supports: "

keyboard3 = [[InlineKeyboardButton(
    "Previous", callback_data='15'), InlineKeyboardButton("Next", callback_data='16')]]
reply_markup3 = InlineKeyboardMarkup(keyboard3)


def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Add Pan to your group",
                              url='http://t.me/Mr7PanBot?startgroup=true')],
        [InlineKeyboardButton("Support Group", url='https://t.me/bgmi_pubgnewstate'),
         InlineKeyboardButton("Updates Channel", url='https://t.me/bgmi_pubgnewstate_updates')],
        [InlineKeyboardButton(
            "Source code", url='https://github.com/aditya-yadav-27/TgPokedexbot')],
        [InlineKeyboardButton("Help & commands", url='http://t.me/Mr7PanBot?start=help')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.id)
    user = (update.message.from_user['first_name'])
    master = "<a href='https://t.me/aditya_yadav_27'>Aditya</a>"
    context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://cdn2.bulbagarden.net/upload/thumb/4/42/Sun_Moon_Rotom_Pok%C3%A9dex_artwork.png/300px-Sun_Moon_Rotom_Pok%C3%A9dex_artwork.png',
                           caption=f"Hey {user}, I am The most advance pokedex bot of Telegram made by my master {master}\nType /help to see what I can do!!", reply_markup=reply_markup, parse_mode=ParseMode.HTML)


def help(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s used help command", user.id)
    update.message.reply_text(
        text=help_text, reply_markup=reply_markup)


def button(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data='14'),

        ]
    ]
    reply_markup1 = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    query.answer()
    choice = query.data

    if choice == '14':
        query.edit_message_text(
            text=help_text, reply_markup=reply_markup)
    elif choice == '1':
        query.edit_message_text(
            text=f"<code>/data {html.escape('<pokemon name or id>')}</code>: get data of the specified pokemon", reply_markup=reply_markup1, parse_mode=ParseMode.HTML)
    elif choice == '2':
        query.edit_message_text(
            text=f"<code>/randpoke</code>: get a random pokemon with its animated gif", reply_markup=reply_markup1, parse_mode=ParseMode.HTML)
    elif choice == '3':
        query.edit_message_text(
            text=f"<code>/shiny {html.escape('<pokemon name or id>')}</code>: get a shiny image of the specified pokemon", reply_markup=reply_markup1, parse_mode=ParseMode.HTML)
    elif choice == '4':
        query.edit_message_text(
            text=f"<code>/stats {html.escape('<pokemon name or id>')}</code>: get the stats of specified pokemon", reply_markup=reply_markup1, parse_mode=ParseMode.HTML)
    elif choice == '5':
        query.edit_message_text(
            text=f"<code>/move {html.escape('<move/pokemon name or id>')}</code>: get the details of the specified move or move that the specified pokemon can learn", reply_markup=reply_markup1, parse_mode=ParseMode.HTML)
    elif choice == '6':
        query.edit_message_text(
            text=f'Coming soon..', reply_markup=reply_markup1, parse_mode=ParseMode.HTML)


def data(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_says = ' '.join(context.args)
    logger.info(f"User %s used data command for pokemon {user_says}", user.id)
    try:
        context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action='typing')
        url = "https://pokeapi.co/api/v2/pokemon/{}/"
        final_url = url.format(user_says.casefold())
        response = requests.get(final_url)
        response = response.content
        info = json.loads(response)

        url1 = "https://pokeapi.co/api/v2/pokemon-species/{}/"
        final_url1 = url1.format(user_says.casefold())
        response1 = requests.get(final_url1)
        response1 = response1.content
        info1 = json.loads(response1)
        gender_rate = info1['gender_rate']
        gender_rate1 = f"{100-(100*(gender_rate/8))}% ♂️ | {100*(gender_rate/8)}% ♀️"
        egg_groups = info1['egg_groups']
        counter = info1['hatch_counter']
        catch_rate = info1['capture_rate']
        growth_rate = info1['growth_rate']['name']
        gen = info1['generation']['name']
        gen = gen.split('-')
        if gender_rate == 0:
            gender_rate1 = '100% ♂️'
        elif gender_rate == 8:
            gender_rate1 = '100% ♀️'
        elif gender_rate == -1:
            gender_rate1 = 'Gender unknown'

        abl = info['abilities']
        all_types = info['types']
        name = info['name']
        id1 = info['id']
        height = info['height']
        weight = info['weight']
        base_experience = info['base_experience']
        stata = info['stats']
        groups = ''
        types = ''
        abilities = ''
        for effort in stata:
            eff = ', '.join(f"{effort['effort']}" for effort in stata)
        for group in egg_groups:
            groups = '/'.join(f"{group['name']}".capitalize()
                              for group in egg_groups)
        for abls in abl:
            abilities = ', '.join(
                f"{abls['ability']['name'].capitalize()}" for abls in abl)
        for type in all_types:
            types = ', '.join(
                f"{type['type']['name'].capitalize()}" for type in all_types)
        if '-' in growth_rate:
            growth_rate = growth_rate.split('-')
            growth_rate = f"{growth_rate[0].capitalize()} {growth_rate[1]}"
        else:
            growth_rate = growth_rate
        eff = eff.split(', ')
        proper = user_says.split('-')
        proper1 = proper[0]
        bulba_link = f'https://bulbapedia.bulbagarden.net/wiki/{proper1.capitalize()}_(Pok%C3%A9mon)'
        bulba2 = f"<a href='{bulba_link}'>Bulbapedia</a>"

        caption = f'''<u><b>#{id1} | {name.capitalize()} | {gen[0].capitalize()}-{gen[1].upper()}</b></u>
        <b>Types</b>
        {types}
        
        <b>Abilities</b>
        {abilities}
        
        <b>Gender Ratio</b>                <b>Catch Rate</b>
        {gender_rate1}                     {catch_rate}
                              
        <b>Egg groups</b>                  <b>Hatch Time</b>
        {groups}                           {255*(counter+1)} steps
                                 
        <b>Height/Weight</b>               <b>Growth Rate</b>
        {height/10}m/{weight/10}kg         {growth_rate}
        
        <b>Base-exp</b>                    
        {base_experience} 
                    
                             <b>EV yield</b>
                             Total: {int(eff[0])+int(eff[1])+int(eff[2])+int(eff[3])+int(eff[4])+int(eff[5])}  
        {eff[0]}     {eff[1]}      {eff[2]}      {eff[3]}          {eff[4]}            {eff[5]}
        Hp  Atk  Def  Sp.Atk  Sp.Def  Speed
        
        <b>Evolution Line</b>
        will add soon
        
        <b>Other Forms</b>
        will add soon
Read more about this pokemon on {bulba2}'''

        update.message.reply_document(
            f"https://img.pokemondb.net/artwork/{user_says.casefold()}.jpg", caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup3)

    except:
        update.message.reply_text(
            f"'{user_says}' is not a valid pokemon! try again")


def randpoke(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s used randpoke command", user.id)
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action='typing')
    k = random.randint(1, 898)
    url = "https://pokeapi.co/api/v2/pokemon/{}/"
    final_url = url.format(k)
    response = requests.get(final_url)
    response = response.content
    info = json.loads(response)
    id1 = info['id']
    name = info['name']
    context.bot.send_document(chat_id=update.effective_chat.id,
                              document=f"http://play.pokemonshowdown.com/sprites/xyani/{name}.gif", caption=f"<b>{name.capitalize()} | #{id1}</b>")


def shiny(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_says = ' '.join(context.args)
    logger.info(f"User %s used shiny command for pokemon {user_says}", user.id)
    try:
        url = "https://pokeapi.co/api/v2/pokemon/{}/"
        final_url = url.format(user_says.casefold())
        response = requests.get(final_url)
        response = response.content
        info = json.loads(response)
        name = info['name']
        id1 = info['id']
        context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action="typing")
        update.message.reply_photo(
            f"https://img.pokemondb.net/sprites/home/shiny-2x/jpg/{user_says}.jpg", caption=f"<b>#{id1} | Shiny {name.capitalize()}</b>")

    except:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"{user_says} is not a valid pokemon, try again!")


def stats(update: Update, context: CallbackContext):
    user_says = ' '.join(context.args)
    user = update.message.from_user
    logger.info(f"User %s used stats command for pokemon {user_says}", user.id)
    try:
        context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action="typing")
        url = "https://pokeapi.co/api/v2/pokemon/{}/"
        final_url = url.format(user_says.casefold())
        response = requests.get(final_url)
        response = response.content
        info = json.loads(response)
        poke_name = info['name']
        poke_name = str(poke_name).capitalize()
        poke_id = info['id']
        stata = info['stats']

        name = ''
        base_stat = ''
        for details in stata:
            base_stat = ', '.join(
                f"{details['base_stat']}" for details in stata)
        for details1 in stata:
            name = ', '.join(
                f"{details1['stat']['name']}"for details1 in stata)

        name = name.split(', ')
        base_stat = base_stat.split(', ')
        update.message.reply_text(f'''<b><u>#{poke_id} | {poke_name}</u></b>
      <code>                                             
      {str(name[0]).capitalize()}: {int(base_stat[0])}                
      {str(name[1]).capitalize()}: {int(base_stat[1])}           
      {str(name[2]).capitalize()}: {int(base_stat[2])}         
      {str(name[3]).capitalize()}: {int(base_stat[3])}  
      {str(name[4]).capitalize()}: {int(base_stat[4])} 
      {str(name[5]).capitalize()}: {int(base_stat[5])}          
      </code>
        <b>Total: {int(base_stat[0])+int(base_stat[1])+int(base_stat[2])+int(base_stat[3])+int(base_stat[4])+int(base_stat[5])}</b>
            ''', parse_mode=ParseMode.HTML)

    except:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f'{user_says} is not a valid pokemon! try again')


def move(update: Update, context: CallbackContext):
    user_says = ' '.join(context.args)
    user = update.message.from_user
    logger.info(
        f"User %s used move command for move/pokemon {user_says}", user.id)

    try:
        if ' ' in user_says:
            user_says = user_says.replace(' ', '-')
        context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action='typing')
        url = "https://pokeapi.co/api/v2/move/{}/"
        final_url = url.format(user_says.casefold())
        response = requests.get(final_url)
        response = response.content
        info = json.loads(response)

        id1 = info['id']
        name = info['name']
        accuracy = info['accuracy']
        pp = info['pp']
        priority = info['priority']
        power = info['power']
        generation = info['generation']
        effect_entries = info['effect_entries']
        effect_chance = info['effect_chance']
        type1 = info['type']
        category = info['damage_class']
        target = info['target']
        contest = info['contest_type']
        entry = ''
        for effect in effect_entries:
            entry += f"{effect['short_effect']}"
        ec = '$effect_chance%'
        if ec in entry:
            entry = entry.replace(ec, f'{effect_chance}%')
        else:
            pass

        update.message.reply_text(f'''<b><u>{id1} | {name.capitalize()} | {generation['name'].capitalize()}</u></b>
            <b>Type</b>                        <b>Category</b>
            {type1['name'].capitalize()}       {category['name'].capitalize()}
            <b>Power Points</b>                <b>Base Power</b>
            {pp}                               {power}
            <b>Accuracy</b>                    <b>Target</b>
            {accuracy}%                        {target['name'].capitalize()}
            <b>Contest</b>                     <b>Priority</b>
            {contest['name'].capitalize()}     {priority}
<b>Description</b>
{entry}
            ''', parse_mode=ParseMode.HTML)

    except:
        try:
            url = "https://pokeapi.co/api/v2/pokemon/{}/"
            final_url = url.format(user_says.casefold())
            response = requests.get(final_url)
            response = response.content
            info = json.loads(response)

            url1 = "https://pokeapi.co/api/v2/pokemon-species/{}/"
            final_url1 = url1.format(user_says.casefold())
            response1 = requests.get(final_url1)
            response1 = response1.content
            info1 = json.loads(response1)

            moves = info['moves']
            id1 = info['id']
            name = info['name']
            generation = info1['generation']
            for move in moves:
                moves1 = ', '.join(
                    f"{move['move']['name'].capitalize()}"for move in moves)
                moves1 = moves1.replace('-', ' ')
            update.message.reply_text(f'''<b><u>{id1} | {name.capitalize()} | {generation['name'].capitalize()}</u></b>
Moves {user_says} can learn:
{moves1}''', parse_mode=ParseMode.HTML)
        except:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"{user_says} is not a valid pokemon or move try again!")


if __name__ == '__main__':
    updater = Updater(token='TOKEN')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('data', data))
    dp.add_handler(CommandHandler('randpoke', randpoke))
    dp.add_handler(CommandHandler('shiny', shiny))
    dp.add_handler(CommandHandler('stats', stats))
    dp.add_handler(CommandHandler('move', move))
    dp.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()
