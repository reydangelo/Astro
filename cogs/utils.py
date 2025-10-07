import discord
import asyncio
import yt_dlp
from discord.ext import commands
from discord import app_commands





class utils(commands.Cog):
    def __init__(self, client):
        self.client = client


    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'    
    }
    YDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    def yt_search(self, arg):

        if arg.startswith('https:') == False:

                with yt_dlp.YoutubeDL(self.YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
                    url = info['formats'][0]['url']
                    title = info['title']
            

        else:
            

                with yt_dlp.YoutubeDL(self.YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(arg, download=False)
                    url = info['formats'][0]['url']
                    title = info['title']
            
        
        return {"url" : url, "title" : title}


    async def play_music(self, interaction,  content):

        target = self.yt_search(content)

        self.client.queues[str(interaction.guild.id)] = []

        interaction.guild.voice_client.play(discord.FFmpegPCMAudio(target["url"], **self.FFMPEG_OPTIONS), after = lambda e :  asyncio.run(self.play_queue(interaction)))

        await interaction.followup.send(f'Now Playing: `{target["title"]}`')




    async def play_queue(self, interaction):

        if self.client.queues[str(interaction.guild.id)]:

            if len(self.client.queues[str(interaction.guild.id)]) == 1 :

                if str(interaction.guild.id) not in self.client.guild_status["loop_song"] and str(interaction.guild.id) not in self.client.guild_status["loop_queue"]:

                    self.client.queues.pop(str(interaction.guild.id))
                    self.client.guild_status["active_servers"].remove(str(interaction.guild.id))
                    self.client.guild_status["now_playing"].remove(str(interaction.guild.id))

                    coro  = interaction.channel.send(f'Queue is empty now.', delete_after = 5)

                    fut = asyncio.run_coroutine_threadsafe(coro, self.client.loop)

                    try :
                        
                        fut.result()

                    except:

                        pass

                    return
                

                if str(interaction.guild.id) in self.client.guild_status["loop_song"]:
                            
                    next_song = self.client.queues[str(interaction.guild.id)][0]

                    target = self.yt_search(next_song)

                    interaction.guild.voice_client.play(discord.FFmpegPCMAudio(target["url"], **self.FFMPEG_OPTIONS), after = lambda e :  asyncio.run(self.play_queue(interaction)))

                    coro  = interaction.channel.send(f'Now Playing: `{target["title"]}`')

                    fut = asyncio.run_coroutine_threadsafe(coro, self.client.loop)

                    try :
                        
                        fut.result()

                    except:

                        pass


                    return


            elif len(self.client.queues[str(interaction.guild.id)]) > 1 :


                if str(interaction.guild.id) in self.client.guild_status["loop_song"]:
                            
                    next_song = self.client.queues[str(interaction.guild.id)][0]

                    target = self.yt_search(next_song)

                    interaction.guild.voice_client.play(discord.FFmpegPCMAudio(target["url"], **self.FFMPEG_OPTIONS), after = lambda e :  asyncio.run(self.play_queue(interaction)))

                    coro  = interaction.channel.send(f'Now Playing: `{target["title"]}`')

                    fut = asyncio.run_coroutine_threadsafe(coro, self.client.loop)

                    try :
                        
                        fut.result()

                    except:

                        pass


                    self.client.queues[str(interaction.guild.id)].append(target["title"])

                    return


                if str(interaction.guild.id) in self.client.guild_status["loop_queue"]:

                    self.client.queues[str(interaction.guild.id)].append(self.client.queues[str(interaction.guild.id)][0])

                try:

                    next_song = self.client.queues[str(interaction.guild.id)][1]

                    target = self.yt_search(next_song)

                    interaction.guild.voice_client.play(discord.FFmpegPCMAudio(target["url"], **self.FFMPEG_OPTIONS), after = lambda e :  asyncio.run(self.play_queue(interaction)))

                    coro  = interaction.channel.send(f'Now Playing: `{target["title"]}`')

                    fut = asyncio.run_coroutine_threadsafe(coro, self.client.loop)

                    try :
                        
                        fut.result()

                    except:

                        pass
          
                            
                    self.client.queues[str(interaction.guild.id)].pop(0)

                except Exception as e:

                    print(e)

                    self.client.queues[str(interaction.guild.id)].pop(0)

        else : 

            pass
                                
                
    async def now_playing_msg(self, interaction, song):
        await interaction.channel.send(f'Now Playing: `{song}`')

    def isUsing(self, interaction):

        if str(interaction.guild.id) in self.client.guild_status["active_servers"]:
            return True 

        elif str(interaction.guild.id) not in self.client.guild_status["active_servers"]:
            return False

    def isPlaying(self, interaction):
        if str(interaction.guild.id) in self.client.guild_status["now_playing"]:
            return True 

        elif str(interaction.guild.id) not in self.client.guild_status["now_playing"]:
            return False

    async def general_check(self, interaction):

        if interaction.user.voice == None :

            await interaction.followup.send('You are not in any voice channels.')

            return

        if utils(self.client).isUsing(interaction) == True and interaction.user.voice.channel != interaction.guild.voice_client.channel:
            
            await interaction.followup.send('You are not in the same voice channel.')

            return

    
    async def is_still_using(self, interaction):
            
            if interaction.guild.voice_client.is_connected() and interaction.guild.voice_client.is_playing():

                await asyncio.sleep(300)

                if interaction.guild.voice_client.is_connected() and interaction.guild.voice_client.is_playing() == False :

                    await interaction.guild.voice_client.disconnect()

                    
                    try :

                        self.client.queues.pop(f"{str(interaction.guild.id)}")
                        self.client.guild_status["active_servers"].remove(str(interaction.guild.id))
                        self.client.guild_status["now_playing"].remove(str(interaction.guild.id))

                    except :
                        
                        pass

                    try :
                        self.client.guild_status["loop_song"].remove(str(interaction.guild.id))
                    except :
                        pass
                    try:

                        self.client.guild_status["loop_queue"].remove(str(interaction.guild.id))
                    except :
                        pass

                    return

            


async def setup(client):
    await client.add_cog(utils(client))
    
