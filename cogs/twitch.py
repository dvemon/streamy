import discord, requests, asyncio
from discord.ext import commands, tasks
from discord.ext.commands import bot
from discord import TextChannel

from main import owner_id, is_admin
from cogs.database import *

twitch_client_id = 'CLIENT ID'
twitch_auth_token = 'AUTH TOKEN'

class twitch(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def get_stream_info(self, channel):
        twitch_api = 'https://api.twitch.tv/helix/streams?user_login=' + channel

        headers = { 'Authorization' : 'Bearer ' + twitch_auth_token, 
                    'Client-Id' : twitch_client_id }

        response = requests.get(twitch_api, headers=headers).json()

        if not response['data']:
            return False

        r = response['data'][0]
        
        return { 'thumbnail' : r['thumbnail_url'],
                 'viewers' : r['viewer_count'],
                 'title' : r['title'],
                 'game' : r['game_id'], 
                 'name' : r['user_name'] }

    async def get_game_info(self, game_id):
        twitch_api = 'https://api.twitch.tv/helix/games?id=' + game_id

        headers = { 'Authorization' : 'Bearer ' + twitch_auth_token, 
                    'Client-Id' : twitch_client_id }

        response = requests.get(twitch_api, headers=headers).json()

        return response['data'][0]['name']

    async def do_notify(self, ctx):
        while True:
            db_list = await database(ctx).read_db()
            mylist = db_list

            with open('database.csv', 'w', newline='') as clear:
                pass

            for x in range(0, len(db_list)):
                stream_channel = db_list[x][2]
                stream_info = await twitch(self).get_stream_info(stream_channel)

                try:
                    if (stream_info):
                        with open('database.csv', 'a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow([mylist[x][0], mylist[x][1], mylist[x][2], 'true', mylist[x][4], mylist[x][5]])

                        if mylist[x][3] == 'true':
                            continue
                        
                        game_name = await twitch(self).get_game_info(stream_info['game'])

                        embed = discord.Embed(colour=0x7a00e6, timestamp=ctx.message.created_at)
                        embed.set_author(name=str(stream_info['name']) + ' has gone live!', url='https://twitch.tv/' + stream_channel)
                        embed.set_image(url=str(stream_info['thumbnail'].format(width=1920, height=1080)))
                        embed.add_field(name=game_name, value=stream_info['title'])
                        embed.set_footer(text='Powered by Streamy')
                        
                        channel = self.client.get_channel(int(mylist[x][1]))

                        await channel.send('@everyone')
                        await channel.send(embed=embed)

                    else:
                        with open('database.csv', 'a', newline='') as file:
                                writer = csv.writer(file)
                                writer.writerow([mylist[x][0], mylist[x][1], mylist[x][2], 'false', mylist[x][4], mylist[x][5]])

                except:
                    continue

            print('checked streams')

            servercount = str(len(self.client.guilds))
            await self.client.change_presence(activity=discord.Game('s?help | ' + servercount + ' guilds'))
            
            await asyncio.sleep(300)

    async def update_stats(self, ctx):
        while True:
            db_list = await database(ctx).read_db()

            for x in range(0, len(db_list)):
                stream_channel = db_list[x][2]
                stream_info = await twitch(self).get_stream_info(stream_channel)

                try:
                    if (stream_info and db_list[x][4] == 'true'):
                        vc_channel = self.client.get_channel(int(db_list[x][5]))
                        await vc_channel.edit(name='LIVE: ' + str(stream_info['viewers']))

                    elif not stream_info and db_list[x][4] == 'true':
                        vc_channel = self.client.get_channel(int(db_list[x][5]))
                        await vc_channel.edit(name='OFFLINE')

                except:
                    continue

            print('updated stats')
            await asyncio.sleep(120)

    @commands.command()
    async def setup(self, ctx):
        if not is_admin(ctx):
            await ctx.send('> You must be an admin to use this command.')
            return

        guild_id = ctx.message.author.guild.id

        def check(m):
            return m.author == ctx.author

        try:
            await ctx.send('Which text channel would you like Twitch streams to be announced in?')
            channel = await self.client.wait_for('message', check=check, timeout=20)
            channel = await commands.TextChannelConverter().convert(ctx, channel.content)
            
            await ctx.send('Please enter the name of the Twitch streamer.')
            streamer = await self.client.wait_for('message', check=check, timeout=20)

            await ctx.send('Would you like me to setup a stream statistics channel?')
            
            vc_channel = await self.client.wait_for('message', check=check, timeout=20)

            if vc_channel.content.lower() in ['y', 'yes']:
                overwrites={ctx.guild.default_role: discord.PermissionOverwrite(connect=False)}
                category = await ctx.guild.create_category(name=f'twitch.tv/{streamer.content}')
                vc_channel_id = await ctx.guild.create_voice_channel(name='OFFLINE', overwrites=overwrites, category=category)
                await database(ctx).exists_db(guild_id)
                await database(ctx).write_db(guild_id, channel.id, streamer.content, 'true', vc_channel_id.id)

            elif vc_channel.content.lower() in ['n', 'no']:
                await database(ctx).exists_db(guild_id)
                await database(ctx).write_db(guild_id, channel.id, streamer.content, 'false')

            else:
                await ctx.send('I did not understand that, continuing with setup.')
                await database(ctx).exists_db(guild_id)
                await database(ctx).write_db(guild_id, channel.id, streamer.content, 'false')
            
            await ctx.send(f'> Setup complete! Twitch streams for {streamer.content} will now be announced in <#{channel.id}>')

        except asyncio.TimeoutError:
            await ctx.send('> You waited too long! Aborting setup.')

    @commands.command()
    async def start(self, ctx):
        if ctx.message.author.id not in owner_id:
            return

        self.client.loop.create_task(self.do_notify(ctx))
        self.client.loop.create_task(self.update_stats(ctx))

        await ctx.send('> Checking streams\n> Updating stats')

def setup(client):
    client.add_cog(twitch(client))
