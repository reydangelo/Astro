import discord
import sys
sys.path.append(r'')
from utils import utils
import lyricsgenius
from discord.app_commands import Group, command
from discord.ext import commands
from discord import app_commands


class music(commands.Cog):
    def __init__(self, client):
        self.client = client

    genius = lyricsgenius.Genius('', timeout= 10)


    @app_commands.command(name = 'disconnect')
    async def disconnect(self, interaction : discord.Interaction):

        await interaction.response.defer()

        if interaction.user.voice == None :

            await interaction.followup.send('You are not in any voice channels.')

            return

        if utils(self.client).isUsing(interaction) == True and interaction.user.voice.channel != interaction.guild.voice_client.channel:
            
            await interaction.followup.send('You are not in the same voice channel.')

            return

        await interaction.guild.voice_client.disconnect()
        await interaction.followup.send('Bai!')

        try :

            self.client.queues.pop(f"{str(interaction.guild.id)}")
            self.client.guild_status["active_servers"].remove(str(interaction.guild.id))
            self.client.guild_status["now_playing"].remove(str(interaction.guild.id))

        except :
            
            pass

        try :
            self.client.guild_status["loop_song"].remove(str(interaction.guild.id))
        except :
            self.client.guild_status["loop_queue"].remove(str(interaction.guild.id))

        


    
    @app_commands.command(name= 'play')
    async def play(self, interaction : discord.Interaction, search : str):

        await interaction.response.defer()

        if interaction.user.voice == None :

                    await interaction.followup.send('You are not in any voice channels.')

                    return

        if utils(self.client).isUsing(interaction) == True and interaction.user.voice.channel != interaction.guild.voice_client.channel:
            
            await interaction.followup.send('You are not in the same voice channel.')

            return


        if utils(self.client).isUsing(interaction) == True :
    
            if utils(self.client).isPlaying(interaction) == False:

                target = utils(self.client).yt_search(search)

                self.client.guild_status["now_playing"].append(str(interaction.guild.id))

                self.client.queues[f"{str(interaction.guild.id)}"].append(target["title"])

                await utils(self.client).play_music(interaction, search)

                return

        
            if utils(self.client).isPlaying(interaction) == True:
                
                target = utils(self.client).yt_search(search)

                self.client.queues[f"{str(interaction.guild.id)}"].append(target["title"])

                await interaction.followup.send(f'`{target["title"]}` added to the queue.')

                return
                
        if utils(self.client).isUsing(interaction) == False :

            if interaction.guild.voice_client == None: 

                await interaction.user.voice.channel.connect()

            await utils(self.client).play_music(interaction, search)

            self.client.queues[f"{str(interaction.guild.id)}"] = []

            self.client.guild_status["active_servers"].append(str(interaction.guild.id))

            self.client.guild_status["now_playing"].append(str(interaction.guild.id))

            target = utils(self.client).yt_search(search)

            self.client.queues[f"{str(interaction.guild.id)}"].append(target["title"])
    

    @app_commands.command(name = 'queue')
    async def queue(self, interaction : discord.Interaction):
         
        await interaction.response.defer()

        try :

            que = f'Now Playing: `{self.client.queues[str(interaction.guild.id)][0]}` \n \n>>> '

            x = 1

            for songs in self.client.queues[f"{str(interaction.guild.id)}"]:

                if songs == self.client.queues[str(interaction.guild.id)][0]:
                    continue

                que += f"{x}. {songs} \n"

                x += 1

            emb = discord.Embed(title= 'Music Queue', description= que, color = discord.Color.from_str('0x2F3136') )
            if str(interaction.guild.id) in self.client.guild_status["loop_song"] :
                footer = 'looping : one'

            elif str(interaction.guild.id) in self.client.guild_status["loop_queue"]:
                footer = 'looping : queue'

            else :
                footer = 'loop : disabled'

            emb.set_footer(text = footer)

            await interaction.followup.send(embed = emb)
            
        except : 

            await interaction.followup.send('There are no songs playing right now.')


    @app_commands.command(name = 'skip')
    async def skip(self, interaction : discord.Interaction):

        await interaction.response.defer()

        if interaction.user.voice == None :

            await interaction.followup.send('You are not in any voice channels.')

            return

        if utils(self.client).isUsing(interaction) == True and interaction.user.voice.channel != interaction.guild.voice_client.channel:
            
            await interaction.followup.send('You are not in the same voice channel.')

            return
        
        interaction.guild.voice_client.stop()

        if str(interaction.guild.id) in self.client.guild_status["loop_song"]:

            target = utils(self.client).yt_search(self.client.queues[(str(interaction.guild.id))][0])

            interaction.voice_client.play(discord.FFmpegPCMAudio(target["url"], **utils(self.client).FFMPEG_OPTIONS))

            return

        if len(self.client.queues[str(interaction.guild.id)]) == 1:

            self.client.queues[str(interaction.guild.id)].pop(0)

            self.client.guild_status["now_playing"].remove(str(interaction.guild.id))

        elif len(self.client.queues[str(interaction.guild.id)]) >= 2:

            await utils(self.client).play_music (interaction, self.client.queues[str(interaction.guild.id)][1])

            self.client.queues[str(interaction.guild.id)].pop(0)

        await interaction.followup.send('Skipped!')

    
    @app_commands.command(name = 'stop')
    async def stop(self, interaction : discord.Interaction):

        await interaction.response.defer()

        if interaction.user.voice == None :

            await interaction.followup.send('You are not in any voice channels.')

            return

        if utils(self.client).isUsing(interaction) == True and interaction.user.voice.channel != interaction.guild.voice_client.channel:
            
            await interaction.followup.send('You are not in the same voice channel.')

            return
        
        interaction.guild.voice_client.stop()

        await interaction.followup.send('Stopped and queue cleared too.')
		
        try:
            
        	self.client.queues[str(interaction.guild.id)].clear()
        	self.client.guild_status["now_playing"].remove(str(interaction.guild.id))
            
        except:
            pass

        try :
            self.client.guild_status["loop_queue"].remove(str(interaction.guild.id))
        except :
            self.client.guild_status["loop_song"].remove(str(interaction.guild.id))


    @app_commands.command(name = 'pause')
    async def pause(self, interaction : discord.Interaction):

        await interaction.response.defer()

        if interaction.user.voice == None :

            await interaction.response.send_message('You are not in any voice channels.')

            return

        if utils(self.client).isUsing(interaction) == True and interaction.user.voice.channel != interaction.guild.voice_client.channel:
            
            await interaction.response.send_message('You are not in the same voice channel.')

            return
        
        await interaction.followup.send('Paused.')
        interaction.guild.voice_client.pause()

    @app_commands.command()
    async def resume(self, interaction : discord.Interaction ):

        await interaction.response.defer()

        if interaction.user.voice == None :

            await interaction.followup.send('You are not in any voice channels.')

            return

        if utils(self.client).isUsing(interaction) == True and interaction.user.voice.channel != interaction.guild.voice_client.channel:
            
            await interaction.followup.send('You are not in the same voice channel.')

            return
            
        await interaction.followup.send('Resuimg...')
        interaction.guild.voice_client.resume()

    @app_commands.command()
    async def remove(self, interaction : discord.Interaction, arg : int):

        await interaction.response.defer()

        if interaction.user.voice == None :

            await interaction.followup.send('You are not in any voice channels.')

            return

        if utils(self.client).isUsing(interaction) == True and interaction.user.voice.channel != interaction.guild.voice_client.channel:
            
            await interaction.followup.send('You are not in the same voice channel.')

            return
        
        try : 
            
            await interaction.followup.send(f'`{ self.client.queues[str(interaction.guild.id)][arg]}` removed from queue.')

            self.client.queues[str(interaction.guild.id)].pop(arg)

        except :

            await interaction.followup.send('⁉️')

    
    @app_commands.command()
    async def move(self, interaction: discord.Interaction, arg1 : int, arg2 : int):

        await interaction.response.defer()

        if interaction.user.voice == None :

            await interaction.followup.send('You are not in any voice channels.')

            return

        if utils(self.client).isUsing(interaction) == True and interaction.user.voice.channel != interaction.guild.voice_client.channel:
            
            await interaction.followup.send('You are not in the same voice channel.')

            return
        
        try : 
            
            self.client.queues[str(interaction.guild.id)][arg2 ], self.client.queues[str(interaction.guild.id)][arg1 ] = self.client.queues[str(interaction.guild.id)][arg1 ], self.client.queues[str(interaction.guild.id)][arg2 ]
            
            await interaction.followup.send(f'Track `{arg1}` moved to `{arg2}`.')

        except :

            await interaction.followup.send('⁉️')

    loop_group = Group(name = 'loop', description= 'loop parent command')

    @loop_group.command(name = 'one')
    async def loop_one(self, interaction : discord.Interaction):
        
        self.client.guild_status["loop_song"].append(str(interaction.guild.id))

        if interaction.guild.id in self.client.guild_status["loop_queue"]:

            self.client.guild_status["loop_queue"].remove(str(interaction.guild.id))

        await interaction.response.send_message('Looping current song.')



    @loop_group.command(name = 'queue')
    async def loop_queue(self, interaction : discord.Interaction):
        
        self.client.guild_status["loop_queue"].append(str(interaction.guild.id))

        if interaction.guild.id in self.client.guild_status["loop_song"]:

            self.client.guild_status["loop_song"].remove(str(interaction.guild.id))

        await interaction.response.send_message('Looping queue.')

    @loop_group.command(name = 'off')
    async def loop_off(self, interaction : discord.Interaction):

        if str(interaction.guild.id) in self.client.guild_status["loop_song"]:

            self.client.guild_status["loop_song"].remove(str(interaction.guild.id))

        if str(interaction.guild.id) in self.client.guild_status["loop_queue"]:
    
            self.client.guild_status["loop_queue"].remove(str(interaction.guild.id))

        await interaction.response.send_message('Loop disabled.')


    @app_commands.command(name= 'lyrics')
    async def lyrics(self, interaction : discord.Interaction, title : str, artist : str):

        await interaction.response.defer()

        target = self.genius.search_song(title = title, artist = artist)


        starting_point = 0

        for ch in target.lyrics:

                if ch != '[':
                    
                    starting_point += 1

                else :

                    break
            
        unformatted = target.lyrics[starting_point:]

        lyrics = unformatted.replace('[', ' \n[')

        lyrics = lyrics.replace(']', ']\n ')

        lyrics = lyrics.replace('4Embed', '')


        if len(lyrics) > 4096:

            end_point = 4000

            for i in lyrics[4000:4096]:

                if i != '\n':

                    end_point += 1

                else :

                    break



            lyrics1 = lyrics[:end_point]

            lyrics2 = lyrics[end_point:]

            embed1 = discord.Embed(color = discord.Color.from_str('0x2F3136'), title= f'{target.title} - {target.artist}', description= lyrics1)

            embed2 = discord.Embed(color = discord.Color.from_str('0x2F3136'), title= f'{target.title} - {target.artist}', description= lyrics2)

            await interaction.followup.send(embed = embed1)
            await interaction.channel.send(embed = embed2)

        else :
            

            embed = discord.Embed(color = discord.Color.from_str('0x2F3136'), title= f'{target.title} - {target.artist}', description= lyrics)

            await interaction.followup.send(embed = embed)



    

async def setup(client):
    await client.add_cog(music(client))

