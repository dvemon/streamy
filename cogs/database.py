import discord, csv
from discord.ext import commands
from discord.ext.commands import bot

class database(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def read_db(self):
        lines = list()

        with open('database.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                lines.append(row)

        return lines

    async def write_db(self, guild_id, channel_id, streamer_name, do_vc, voice_channel_id='0'):
        with open('database.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([guild_id, channel_id, streamer_name, 'false', do_vc, voice_channel_id])

    async def test_db(self, guild_id):
        with open('database.csv', 'rb') as inp, open('database.csv', 'wb') as out:
            writer = csv.writer(out)
            for row in csv.reader(inp):
                if row[0] != guild_id:
                    writer.writerow(row)

    async def exists_db(self, guild_id):
        lines = list()

        with open('database.csv', 'r') as inp:
            for row in csv.reader(inp):
                if row[0] != str(guild_id):
                    lines.append(row)

        with open('database.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            for x in range(0, len(lines)):
                writer.writerow([lines[x][0], lines[x][1], lines[x][2], 'false', lines[x][4], lines[x][5]])

def setup(client):
    client.add_cog(database(client))