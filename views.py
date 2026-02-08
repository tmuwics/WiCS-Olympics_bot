from datetime import datetime, timezone
import discord 
from discord.ext import commands
from sheet import *
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
        await interaction.response.defer(ephemeral=True)

        points = 10
        email = self.student_email.value
        exec_role = self.exec_role.value
        location = self.location.value

        try:
            rows = await find_in_DB_async(email)

            if len(rows) > 0:
                if submission_exists(email, exec_role):
                    await interaction.followup.send(
                        "❌ You've already submitted info for this exec role!",
                        ephemeral=True
                    )
                    return

                await update_db_async(email, points, exec_role, location)

            else:
                await sheetdb_append_async({
                    "Name": self.name.value,
                    "Student_Email": email,
                    "Location": self.location.value,
                    "Instagram": self.Instagram.value,
                    "Exec_Role": exec_role,
                    "Points": points,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                })

            await interaction.followup.send(
                f"✅ Saved!\n"
                f"**Name:** {self.name.value}\n"
                f"**Student Email:** {self.student_email.value}\n"
                f"**Location:** {self.location.value}\n"
                f"**Points:** {points}",
                ephemeral=True
            )


        except Exception as e:
            await interaction.followup.send(
                f"🚫 Something went wrong while saving.\n`{e}`",
                ephemeral=True
            )
