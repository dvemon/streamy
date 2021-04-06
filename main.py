import discord, os
from discord.ext import commands
from discord.ext.commands import bot

owner_id = [181386549525479424, 744205759214256233]

client = commands.Bot(command_prefix='s?')
client.remove_command('help')

@client.event
async def on_ready():
    print("Bot is online.")

@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'> Loaded {extension}.')

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'> Unloaded {extension}.')

@client.command()
async def reload(ctx, extension):
    client.reload_extension(f'cogs.{extension}')
    await ctx.send(f'> Reloaded {extension}.')

def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')

def is_admin(ctx):
    if ctx.message.author.guild_permissions.administrator:
        return True
    else:
        return False

load_cogs()

client.run('TOKEN HERE')