import discord 
from discord.ext import commands
import views
from config import ALLOWED_CHANNEL_ID, TAG

class Client(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.synced = False #stop bot from syncing commands multiple times


    #This is an event that triggers when the bot has connected to the server
    async def on_ready(self):
        print(f"Logged on as {self.user}!")
        print("Application ID:", self.application_id)


    #When someone sends a message in the server this bot responds to it.
    async def on_message(self, message):
        #stopping the bot from responding to itself
        if message.author == self.user:
            return
        
        if message.channel.id != ALLOWED_CHANNEL_ID:
            print(f"message.channel.id = {message.channel.id}, ALLOWED_CHANNEL_ID = {ALLOWED_CHANNEL_ID}")
            return
        
        if message.attachments:
            attachment_url = message.attachments[0].url

        if message.content.strip().lower() == TAG.lower():
            await message.channel.send(f'Hi there {message.author} please reply with your info: \n'
                                       'Note: Please send the photo in a separate message below, thank you <3', 
                                       view=views.View(attachment_url if message.attachments else None))
        await self.process_commands(message)


        for attachment in message.attachments:
            print("Filename:", attachment.filename)
            print("URL:", attachment.url)
            print("Content type:", attachment.content_type)

        #await client.process_commands(message) <-- removed to avoid double handling 6:52pm Feb 7th

        #this prints to the terminal
        print(f"Message from {message.author}: {message.content}")

#allow bot to access intents
intents = discord.Intents.default()
intents.message_content = True