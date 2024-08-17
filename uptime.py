import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.ext.commands import MissingPermissions, BadArgument
import discord, datetime, time
start_time = time.time()

class Uptime(commands.Cog):
    def __init__(self, client):
        self.client = client
        

       

    @commands.command(pass_context=True)
    async def uptime(self, ctx):
        current_time = time.time()
        difference = int(round(current_time - start_time))
        text = str(datetime.timedelta(seconds=difference))
        embed = discord.Embed(colour=ctx.message.author.top_role.colour)
        embed.add_field(name="Uptime", value=text)
        embed.set_footer(text="Roadman")
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Uptime curent: " + text)






def setup(client):
    client.add_cog(Uptime(client))