import discord
import os

class MyClient(discord.Client):
    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))


    async def on_menssage(self, message):
        print("Message from {0.author}: {0.content".format(message))
        if message.content == "!regras":
            await message.channel.send(f"{message.author.name} Leis do Servidor: {os.linesep}1 - Não dara spoiler")

client = MyClient()
client.run("    ")