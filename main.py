import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

ticket_count = 0

class TicketModal(discord.ui.Modal, title="Open a Support Ticket"):
    reason = discord.ui.TextInput(
        label="Reason",
        placeholder="Briefly describe your reason for opening this ticket.",
        style=discord.TextStyle.long,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        global ticket_count
        ticket_count += 1

        ticket_channel_name = f"ticket-{interaction.user.name.lower()}-{ticket_count}"

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        category = discord.utils.get(interaction.guild.categories, name="Tickets")
        if not category:
            category = await interaction.guild.create_category("Tickets")

        ticket_channel = await interaction.guild.create_text_channel(
            name=ticket_channel_name,
            overwrites=overwrites,
            category=category
        )

        embed = discord.Embed(
            title="Ticket Opened",
            description=f"Ticket opened by {interaction.user.mention}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Reason", value=self.reason.value, inline=False)
        embed.set_footer(text="To close this ticket, click the 'Close Ticket' button.")
        await ticket_channel.send(embed=embed, view=TicketCloseView())

        await interaction.response.send_message(
            f"Your ticket has been created at {ticket_channel.mention}!",
            ephemeral=True
        )

class TicketOpenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Open a Ticket",
        style=discord.ButtonStyle.green,
        custom_id="open_ticket_button"
    )
    async def open_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketModal())

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Ticket",
        style=discord.ButtonStyle.red,
        custom_id="close_ticket_button"
    )
    async def close_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing this ticket...", ephemeral=True)
        await interaction.channel.delete()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    bot.add_view(TicketOpenView())

@bot.command(name="ticket_setup")
@commands.has_permissions(manage_channels=True)
async def ticket_setup(ctx):
    category = discord.utils.get(ctx.guild.categories, name="Tickets")
    if not category:
        category = await ctx.guild.create_category("Tickets")

    embed = discord.Embed(
        title="Support Tickets",
        description="Click the button below to open a new support ticket.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=TicketOpenView())
    await ctx.send("Ticket system setup complete!", ephemeral=True, delete_after=5)

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
    .set_footer(Powered By Joker Devlopement 
