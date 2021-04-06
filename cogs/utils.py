import discord
from discord.ext import commands
from discord.ext.commands import bot

from main import owner_id, is_admin

class utils(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['vote'])
    async def poll(self, ctx, *, args):
        if not is_admin(ctx):
            return

        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="Poll")
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.add_field(name=args, value='‎‎‎\u200b')

        message = await ctx.send(embed=embed)
        
        await message.add_reaction(emoji = "\U0001F44D")
        await message.add_reaction(emoji = "\U0001F44E")

    @commands.command()
    async def status(self, ctx, activity, *, args):
        if ctx.message.author.id not in owner_id:
            return
        
        activity = activity.lower()

        if activity == 'playing':
            await self.client.change_presence(activity=discord.Game(name=args))

        elif activity == 'listening':
            await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=args))

        elif activity == 'watching':
            await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=args))
            
        else:
            await ctx.send('Incorrect activity. Try:\n> Playing, listening or watching.')

    @commands.command()
    async def info(self, ctx, member: discord.Member):
        roles = [role for role in member.roles]
        embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)
    
        embed.set_author(name=f"User Info - {member}")
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
    
        embed.add_field(name="ID:", value=member.id)
        embed.add_field(name="Guild name:", value=member.display_name)
    
        embed.add_field(name="Created at:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p"))
        embed.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p"))
    
        embed.add_field(name=f"Roles ({len(roles)})", value=" ".join([role.mention for role in roles]))
        embed.add_field(name="Top role:", value=member.top_role.mention)
    
        await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx):
        author = ctx.message.author.id
        author = self.client.get_user(author)

        embed = discord.Embed(colour=discord.Color.purple())
        embed.set_author(name='Commands:')
        embed.add_field(name='s?help', value='Displays this message.', inline=False)
        embed.add_field(name='s?setup', value='Used to setup Twitch announcements and stats.', inline=False)
        embed.add_field(name='s?poll', value='Create a reaction poll.', inline=False)
        embed.add_field(name='s?info', value='Display information about a user.', inline=False)

        embed2 = discord.Embed(colour=discord.Color.purple())
        embed2.add_field(name='To get started run the command:', value='s?setup', inline=False)
        embed2.set_footer(text='Powered by Streamy')

        await author.send(embed=embed)
        await author.send(embed=embed2)
        await ctx.send('Please check your DMs for a list of commands.')

def setup(client):
    client.add_cog(utils(client))