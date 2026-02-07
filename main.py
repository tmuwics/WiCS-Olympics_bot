import asyncio
from datetime import datetime
import os, requests
import discord 
from urllib.parse import quote
from dotenv import load_dotenv 

#for the /slash commands
from discord.ext import commands
from discord import ui, app_commands

#loading the .env file
load_dotenv()
TOKEN = os.getenv("WICS_OLYMPICS_TOKEN")
SHEETDB_URL = os.getenv("SHEETDB_URL")
if not SHEETDB_URL:
    raise RuntimeError("SHEETDB_URL is not set. Check your .env file.")

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

        if message.content.strip() == '#ExecFound':
            await message.channel.send(f'Hi there {message.author} please reply with your info: ', view=View())
        await self.process_commands(message)


        #this prints to the terminal
        print(f"Message from {message.author}: {message.content}")

#creating a button
class View(discord.ui.View):

    @discord.ui.button(label="Enter info here!", style=discord.ButtonStyle.blurple)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(InfoModal())

#creating the modal for the form
class InfoModal(discord.ui.Modal, title="WiCS Info Form"):
    name = discord.ui.TextInput(label="Name", placeholder="Your name", max_length=100)
    student_email = discord.ui.TextInput(label="Student Email", placeholder="Your student email", max_length=100)
    Instagram = discord.ui.TextInput(
        label="Instagram (If you posted on IG)", 
        placeholder="(Optional)", 
        max_length=100,
        required = False)
    location = discord.ui.TextInput(
        label="Where did you find them?",
        style=discord.TextStyle.paragraph,
        max_length=500,
        placeholder="eg. DCC 208, LIB 7th floor, ENG 201, etc."
    )

    async def on_submit(self, interaction: discord.Interaction):
        #implement points systems maybe? keeping default 10 points for now
        points = 10

        #append the info to the Google Sheets via SheetDB
        if len(find_in_DB(student_email=self.student_email.value)) > 0:
            add_points(self.student_email.value, points)

        #else create a new record
        else:    
            sheetdb_append({
            "Name": self.name.value,
            "Student_Email": self.student_email.value,
            "Location": self.location.value,
            "Instagram": self.Instagram.value,
            "Points": points,
            "last_updated": datetime.utcnow().isoformat()
            })

        await interaction.response.send_message(
            f"✅ Saved!\n"
            f"**Name:** {self.name.value}\n"
            f"**Student Email:** {self.student_email.value}\n"
            f"**Location:** {self.location.value}\n"
            f"**Points:** {points}",
            ephemeral=True
        )

#check if there is a record in sheets
def find_in_DB(student_email: str):
    encoded_email = quote(student_email, safe="")
    #prolly change mostof these to a global variable
    url = f"{SHEETDB_URL}/search?Student_Email={encoded_email}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def add_points(student_email, points_to_add):
    rows = find_in_DB(student_email)
    current_points = int(rows[0].get("Points", 0))
    new_total = current_points + points_to_add
    sheetdb_update_points(student_email, new_total)
    return new_total, False  

def sheetdb_update_points(student_email, new_points):
    encoded_email = quote(student_email, safe="")
    url = f"{SHEETDB_URL}/Student_Email/{encoded_email}"
    payload = {
        "Points": new_points,
        "last_updated": datetime.utcnow().isoformat()
    }
    r = requests.patch(url, json=payload, timeout=10)
    r.raise_for_status()



#appaned the row to sheet db
def sheetdb_append(row: dict):
    payload = {"data": [row]}
    
    r = requests.post(SHEETDB_URL, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

#allow bot to access intents
intents = discord.Intents.default()
intents.message_content = True

client = Client()
client.run(TOKEN)