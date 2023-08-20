import discord
import os
import sys
import subprocess
from discord.ext import commands
from discord import app_commands

class general(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.queues = {}
        self.client.guild_status = {"active_servers" : [], "now_playing" : [], "loop_song" : [], "loop_queue" : []}




    @commands.command(name='sync', hidden = True)
    @commands.is_owner()
    async def _sync(self, ctx):
        synced = await self.client.tree.sync()
        await ctx.send(f'`{len(synced)}` commands synced successfully.')


    @commands.command(name='reload', hidden = True)
    @commands.is_owner()
    async def reload(self, ctx, extension):
        await self.client.reload_extension(f'cogs.{extension}')
        await ctx.send(f'Cog: `{extension}` reloaded successfully.')

    @app_commands.command(name= 'ping')
    async def ping(self, interaction : discord.Interaction):
        await interaction.response.send_message(f'Pong! Latency : `{round(self.client.latency * 1000)}ms`')

    @app_commands.command(name = 'help')
    async def help(self, interaction : discord.Interaction):
        
        embed = discord.Embed(colour= discord.Color.from_str('0x2F3136'), title= 'Astro\'s Help', description= 'This bot is coded for the purpose to stream music from Youtube for you!')
        embed.add_field(name = 'Developed by:', value= '<@692994778136313896> (ID : 692994778136313896)', inline=True )
        embed.add_field(name = 'Ping', value= f'{round(self.client.latency * 1000)}ms' , inline= True)
        embed.add_field(name = 'Commands: ', value= '`play`, `pause`, `resume`, `skip`, `stop`,\n`move`, `remove`, `queue`, `disconnect`,\n`help`, `loop [one|queue|off]`', inline= False)
        embed.set_footer(text= 'If any (bugs/errors) were found, please contact the developer.')

        await interaction.response.send_message(embed = embed)

    @commands.command(aliases = ['rs'])
    @commands.is_owner()
    async def restart(self, ctx):

        await ctx.send("Restarting...")
        subprocess.Popen('python main.py', shell= True)
        await self.client.close()
        

    @app_commands.command(name = 'invite')
    async def invite(self, interaction : discord.Interaction):
        
        await interaction.response.send_message('https://discord.com/api/oauth2/authorize?client_id=1007621512104247347&permissions=2167729216&scope=bot', ephemeral = True)

    



async def setup(client):
    await client.add_cog(general(client))
    