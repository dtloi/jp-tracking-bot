#!/Users/Danielloi/anaconda3/bin/python3
import os
from os import listdir

import discord
import datetime
import logging

from discord.ext import commands
from dotenv import load_dotenv
from cassandra.query import ordered_dict_factory
from cassandra.cluster import Cluster

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')
cogs_folder = "./cogs"
cluster = Cluster()
bot.fetch_guilds()

x = datetime.datetime.now()
filename = "log_"+x.strftime("%b_%d_%y")+".log"
logging.basicConfig(filename=filename, level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logging.getLogger('cassandra').setLevel(logging.ERROR)
logging.getLogger('discord').setLevel(logging.ERROR)
logging = logging.getLogger(__name__)

@bot.event
async def on_ready():
    print(bot.user.name + " has connected to Discord!")

#Error handling
@bot.event
async def on_command_error(ctx, error):
    """
    The event triggered when an error is raised while invoking a command.

    Parameters
    ------------
    ctx: commands.Context
        The context used for command invocation.
    error: commands.CommandError
        The Exception raised.
    """

    with open('err.log', 'a') as f:
        user = ctx.message.author.mention
        if ctx.invoked_with == 'rak':
            logging.warning(ctx.invoked_with + ": "+str(error))
            await ctx.send(user+" Usage: !rak [query]")
        elif ctx.invoked_with == 'upf':
            logging.warning(ctx.invoked_with + ": "+str(error))
            await ctx.send(user+" Usage: !upf [query]")
        elif ctx.invoked_with == 'track':
            logging.warning(ctx.invoked_with + ": "+str(error))
            await ctx.send(user+" Usage: !track [website] [query]")
            await ctx.send("Use !website to get a list of available websites")
        elif ctx.invoked_with == 'set':
            logging.warning(ctx.invoked_with + ": "+str(error))
            await ctx.send(user+" Usage: !set")

@bot.command(name="set", help="Sets the channel where the command was called as the postings channel")
async def set(ctx):
    session = cluster.connect("discord")
    update_last = session.prepare(
        """
        Update default_channel Set channel_id = ? where guild_id = ?
        """)
    session.execute(update_last, [ctx.channel.id, ctx.guild.id])

    user = ctx.message.author.mention
    await ctx.send(user+" default channel set to "+ctx.channel.name)
    #print(bot.get_all_channels())

@bot.command(name="kill", help="This kills the Bot")
async def kill(ctx):
    """
    The command kills the bot.

    Parameters
    ------------
    """
    is_owner = await ctx.bot.is_owner(ctx.author)
    if not is_owner:
        return
    await bot.logout()

@bot.command()
async def load(ctx, folder, extension):
    """
    The command loads an extension from a given folder.

    Parameters
    ------------
    folder: str
        The folder name that contains the extension
    extension: str
        The extension name
    """
    is_owner = await ctx.bot.is_owner(ctx.author)
    if not is_owner:
        return
    logging.info("loaded "+extension)
    bot.load_extension(cogs_folder+"/"+folder+"/"+extension)

@bot.command()
async def unload(ctx, folder, extension):
    """
    The command unloads an extension from a given folder.

    Parameters
    ------------
    folder: str
        The folder name that contains the extension
    extension: str
        The extension name
    """
    is_owner = await ctx.bot.is_owner(ctx.author)
    if not is_owner:
        return
    logging.info("unloaded " + extension)
    bot.unload_extension(cogs_folder+"/"+folder+"/"+extension)


#Loads all cogs on bot start
for folder_name in os.listdir("./cogs"):
    #print(folder_name)
    if os.path.isdir("./cogs/"+folder_name) != True:
        #print(folder_name+" is not a folder.")
        continue
    for file_name in os.listdir("./cogs/"+folder_name):
        #print(file_name)
        if file_name.endswith(".py"):
            logging.info("loaded " + file_name)

            bot.load_extension("cogs."+folder_name+"."+file_name[:-3])

bot.run(TOKEN)

#client.run(TOKEN)

