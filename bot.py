import os
from io import BytesIO
import discord
from discord import app_commands
from discord.ext import commands
import warnings
from datetime import datetime
from dotenv import load_dotenv
import pytz
from data import *
from help import *
import traceback
import threading
import time
import random
warnings.simplefilter('ignore')

OLD_PITCHES = {'mlr':old_mlr_data(), 'milr':old_milr_data(), 'mln':old_mln_data(), 'catcher':old_catcher_data()}
full_pitches = {'mlr':update_mlr_data(OLD_PITCHES['mlr']),
                'milr':update_milr_data(OLD_PITCHES['milr']),
                'mln':update_mln_data(OLD_PITCHES['mln']),
                'catcher':update_catcher_data(OLD_PITCHES['catcher'])}

guilds = {
    'MLR Athletics':{'league':'mlr', 'name':'mark schihne', 'hitter':'mark schihne', 'pitches':set_pitcher('mark schihne', full_pitches['mlr']), 'swings':set_hitter('mark schihne', full_pitches['mlr'])},
    'Kansas City Kitties':{'league':'mln', 'name':'noodle arm odoyle', 'pitches':set_pitcher('noodle arm odoyle', full_pitches['mln']), 'catcher':'dave steib', 'throws':set_catcher('dave steib', full_pitches['catcher'])},
    'n8_n\'s server':{'league':'mlr', 'name':'mark schihne', 'hitter':'mark schihne', 'pitches':set_pitcher('mark schihne', full_pitches['mlr']), 'swings':set_hitter('mark schihne', full_pitches['mlr'])},
    'Fake Mariners':{'league':'mlr', 'name':'brent chillwater', 'pitches':set_pitcher('brent chillwater', full_pitches['mlr'])}
}

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix = '!', intents = intents)

def update_numbers():
    global full_pitches, guilds
    
    while True:
        now = datetime.now(pytz.timezone('America/Denver')) 
        try:
            full_pitches = {'mlr':update_mlr_data(OLD_PITCHES['mlr']),
                            'milr':update_milr_data(OLD_PITCHES['milr']),
                            'mln':update_mln_data(OLD_PITCHES['mln']),
                            'catcher':update_catcher_data(OLD_PITCHES['catcher'])}
            
            for guild in guilds:
                guilds[guild]['pitches'] = set_pitcher(guilds[guild]['name'], full_pitches[guilds[guild]['league']])

            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Pitches are now updated!")
        except Exception as e:  
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Error updating pitches: {e}")
            traceback.print_exc()
        
        time.sleep(10)

update_thread = threading.Thread(target = update_numbers)
update_thread.start()

@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f'Synced {len(synced)} commands')
    print(f'{bot.user} is now running!')

@bot.event
async def on_message(message):
    user_message = str(message.content)

    if message.author == bot.user:
        return
    elif message.author.id == 566239287713202187 and 'hello' in user_message.lower():
        await message.channel.send('it actually worked this time dumbass did you finally learn the difference between an int and a string')
    elif message.author.id == 1001561315036368957 and 'hello' in user_message.lower():
        await message.channel.send('you remind me of triples in that we love you')
    elif message.author.id == 243821280833437706 and 'hello' in user_message.lower():
        await message.channel.send('What the fuck did you just fucking say about me, you little bitch? I\'ll have you know I graduated top of my class in the Navy Seals, and I\'ve been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills. I am trained in gorilla warfare and I\'m the top sniper in the entire US armed forces. You are nothing to me but just another target. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words. You think you can get away with saying that shit to me over the Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your life. You\'re fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven hundred ways, and that\'s just with my bare hands. Not only am I extensively trained in unarmed combat, but I have access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution your little \"clever\" comment was about to bring down upon you, maybe you would have held your fucking tongue. But you couldn\'t, you didn\'t, and now you\'re paying the price, you goddamn idiot. I will shit fury all over you and you will drown in it. You\'re fucking dead, kiddo.')
    elif 'hello' in user_message.lower():
        await message.channel.send('yeah im here wtf do you want')
    elif 'scouting' in user_message.lower() and random.random() < 0.1:
        await message.channel.send('the scouting could be wrong, no offense')
    else:
        return

@bot.tree.command(name = 'help')
async def help(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(help_response)

@bot.tree.command(name = 'invite')
async def invite(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(invite_link)

@bot.tree.command(name = 'setpitcher')
@app_commands.describe(name = 'pitcher\'s name')
async def setpitcher(interaction: discord.Interaction, name: str):
    global guilds
    await interaction.response.defer()
    name = name.lower()
    league = guilds[interaction.guild.name]['league'].lower()
    pitcher_id = full_pitches[league].loc[full_pitches[league]['Pitcher'] == name, 'Pitcher ID']

    if pitcher_id.empty or pitcher_id.iloc[0] not in full_pitches[league]['Pitcher ID'].values:
        await interaction.followup.send('that pitcher has never pitched or does not exist.')
        return
    else:
        guilds[interaction.guild.name]['pitches'] = set_pitcher(name, full_pitches[league]) 
        guilds[interaction.guild.name]['name'] = name
        await interaction.followup.send(f'pitcher successfully set to {name}!')
        return
    
@bot.tree.command(name = 'sethitter')
@app_commands.describe(name = 'hitter\'s name')
async def setpitcher(interaction: discord.Interaction, name: str):
    global guilds
    await interaction.response.defer()
    name = name.lower()
    league = guilds[interaction.guild.name]['league'].lower()
    hitter_id = full_pitches[league].loc[full_pitches[league]['Hitter'] == name, 'Hitter ID']

    if hitter_id.empty or hitter_id.iloc[0] not in full_pitches[league]['Hitter ID'].values:
        await interaction.followup.send('that hitter has never swung or does not exist.')
        return
    else:
        guilds[interaction.guild.name]['swings'] = set_hitter(name, full_pitches[league]) 
        guilds[interaction.guild.name]['hitter'] = name
        await interaction.followup.send(f'hitter successfully set to {name}!')
        return
    
@bot.tree.command(name = 'setcatcher')
@app_commands.describe(name = 'catcher\'s name')
async def setpitcher(interaction: discord.Interaction, name: str):
    global guilds
    await interaction.response.defer()
    name = name.lower()
    league = guilds[interaction.guild.name]['league'].lower()

    if league == 'mln':
        catcher_id = full_pitches['catcher'].loc[full_pitches['catcher']['Catcher'] == name, 'Catcher ID']
        if catcher_id.empty or catcher_id.iloc[0] not in full_pitches['catcher']['Catcher ID'].values:
            await interaction.followup.send('that catcher has never thrown or does not exist.')
            return
        else:
            guilds[interaction.guild.name]['throws'] = set_catcher(name, full_pitches['catcher']) 
            guilds[interaction.guild.name]['catcher'] = name
            await interaction.followup.send(f'catcher successfully set to {name}!')
            return
    else:
        await interaction.followup.send(f'theres no catcher numbers here dummy!')
        return

@bot.tree.command(name = 'recent')
async def recent(interaction: discord.Interaction):
    await interaction.response.defer()
    guild = interaction.guild.name
    await interaction.followup.send(recent_list(guilds[guild]['name'], guilds[guild]['league'], guilds[guild]['pitches']))

@bot.tree.command(name = 'pitchtrend')
async def pitchtrend(interaction: discord.Interaction):
    await interaction.response.defer()
    guild = interaction.guild.name
    buffer = BytesIO()
    chart = pitch_trend(guilds[guild]['name'], guilds[guild]['league'], guilds[guild]['pitches'])
    chart.savefig(buffer, format = 'png')
    buffer.seek(0)
    file = discord.File(buffer, filename = 'output.png')
    await interaction.followup.send(file = file)

bot.run(TOKEN)