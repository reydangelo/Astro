import discord
import os
from discord.ext import tasks,commands
from discord import app_commands

class bot(commands.Bot):
    def __init__(self):

        intents = discord.Intents.none()
        intents.dm_messages = True
        intents.voice_states = True
        intents.members = True
        intents.guilds = True

        super().__init__(command_prefix = [ ',,', '<@895214322102456340> ' ] , help_command= None, intents = intents)

    async def on_ready(self):
        etc = discord.Activity(type=discord.ActivityType.watching, name="over rey's miserable life")
        await client.change_presence(activity=etc)
        print('I\'m ready senpai!')
        await check_idle.start()

    async def setup_hook(self):
        for file in os.listdir('./cogs'):
            if file.endswith('.py'):
                await self.load_extension(f'cogs.{file[:-3]}')
        await self.load_extension('jishaku')

    	    
    
@tasks.loop(minutes = 5.0)
async def check_idle():
    for vc in client.voice_clients:
        if vc.is_connected() and vc.is_playing() == False:
            await vc.disconnect()
            try :
                self.client.queues.pop(f"{str(vc.channel.guild.id)}")
                self.client.guild_status["active_servers"].remove(str(vc.channel.guild.id))
                self.client.guild_status["now_playing"].remove(str(vc.channel.guild.id))
            except :
                pass
            try :
                self.client.guild_status["loop_song"].remove(str(vc.channel.guild.id))
            except :
                pass
            try :
                self.client.guild_status["loop_queue"].remove(str(vc.channel.guild.id))
            except :
                pass
        
   	
    
    

client = bot()
token = ''               

client.run(token)