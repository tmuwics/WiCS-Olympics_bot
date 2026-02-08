import asyncio
from datetime import datetime
import os, requests
import re
import discord 
from urllib.parse import quote
from dotenv import load_dotenv 
from discord.ext import commands

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
            await message.channel.send(f'Hi there {message.author} please reply with your info: \n'
                                       'Note: Please send the photo in a separate message below, thank you <3', 
                                       view=View())
        await self.process_commands(message)

        for attachment in message.attachments:
            print("Filename:", attachment.filename)
            print("URL:", attachment.url)
            print("Content type:", attachment.content_type)

        #await client.process_commands(message) <-- removed to avoid double handling 6:52pm Feb 7th

        #this prints to the terminal
        print(f"Message from {message.author}: {message.content}")

#creating a button
class View(discord.ui.View):

    @discord.ui.button(label="Enter info here!", style=discord.ButtonStyle.blurple)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(InfoModal())

#creating the modal for the form
class InfoModal(discord.ui.Modal, title="WiCS Info Form"):

    #variables for the form
    name = discord.ui.TextInput(
        label="Name", 
        placeholder="Your name", 
        max_length=100)
    student_email = discord.ui.TextInput(
        label="Student Email", 
        placeholder="Your student email", 
        max_length=100)
    exec_role = discord.ui.TextInput(
        label="Exec Name & Role (Name, Role)", 
        placeholder="Eg. Prachi, President", 
        max_length=100)
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

    #submitting the form
    async def on_submit(self, interaction: discord.Interaction):
        #implement points systems maybe? keeping default 10 points for now
        points = 10

        print(self.student_email.value)
        
        #if the student already exists in the databse
        if len(find_in_DB(self.student_email.value)) > 0: 
            
            #Check if student entered the same exec as before
            if submission_exists(self.student_email.value, self.exec_role.value):
                await interaction.response.send_message(
                    f"❌ You've already submitted info for this exec role!",
                    ephemeral=True
                )
                return
            add_points(self.student_email.value, points)


        #else create a new record
        else:    
            sheetdb_append({
            "Name": self.name.value,
            "Student_Email": self.student_email.value,
            "Location": self.location.value,
            "Instagram": self.Instagram.value,
            "Exec_Role": self.exec_role.value,
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
def find_in_DB(key: str):
    encoded_key = quote(key, safe="")
    #prolly change mostof these to a global variable
    url = f"{SHEETDB_URL}/search?Student_Email={encoded_key}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def submission_exists(student_email: str, exec_role: str) -> bool:
    """
    Returns True if a submission already exists for this
    (student_email + exec_role), otherwise False.
    """
    rows = find_in_DB(student_email)

    target_role = normalize(exec_role)

    for row in rows:
        row_role = normalize(row.get("Exec_Role", ""))

        if row_role == target_role:
            return True

    return False


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

#normalize string text
def normalize(text: str) -> str:
    t = text.strip().lower()
    # normalize comma spacing: "a, b", "a ,b", "a,b" -> "a, b"
    t = re.sub(r"\s*,\s*", ", ", t)
    # collapse any remaining whitespace
    t = " ".join(t.split())
    return t

#allow bot to access intents
intents = discord.Intents.default()
intents.message_content = True

client = Client()
client.run(TOKEN)