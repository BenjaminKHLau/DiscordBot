import json
import os
import random

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Bot
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = Bot(command_prefix="-", intents=intents)

token = os.getenv("DISC_TOKEN")

@bot.event
async def on_ready():
    print(f'{bot.user} is now running!')
    
## Economy
@bot.command()
async def balance(ctx):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    
    wallet_amount = users[str(user.id)]["wallet"]
    
    em = discord.Embed(title = f"{ctx.author.name}'s  balance")
    em.add_field(name = "Wallet balance", value = wallet_amount)
    print(em, "HELLO")
    await ctx.send(embed = em)
    
@bot.command()
async def work(ctx):
    user = ctx.author
    await open_account(user)
    users = await get_bank_data()
    print("WORK")
    earnings = random.randrange(101)
    
    await ctx.channel.send(f"You have earned {earnings} coins!")
    
    users[str(user.id)]["wallet"] += earnings
    
    with open("eco.json", "w") as f:
        json.dump(users, f)
        
async def open_account(user):
    users = await get_bank_data()
            
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        
    with open("eco.json", "w") as f:
        json.dump(users, f)
    return True

async def get_bank_data():
    with open("eco.json", "r") as f:
        users = json.load(f)   
    return users 

@bot.command()
async def coinflip(ctx, *arg):
    user = ctx.author
    users = await get_bank_data()
    wallet_amount = users[str(user.id)]["wallet"]
    if arg is (): 
        await ctx.send("Provide a wager amount in numbers")
        return
    elif int(arg[0]) < 0:
        await ctx.send("Nice try, loser")
        return
    elif int(wallet_amount) < int(arg[0]):
        await ctx.send("You're broke")
        return
    elif int(arg[0]) > 5000:
        await ctx.send("You can only bet 5000 coins at a time")
        return
    
    flip_result = random.randint(0, 1)
    if flip_result == 0:
        users[str(user.id)]["wallet"] -= int(arg[0])
        with open("eco.json", "w") as f:
            json.dump(users, f)
            get_bank_data()
        new_balance = users[str(user.id)]["wallet"]
        await ctx.send(f"You have flipped TAILS and have LOST {arg[0]} coins.  You now have {new_balance}")
    else:
        users[str(user.id)]["wallet"] += int(arg[0])
        with open("eco.json", "w") as f:
            json.dump(users, f)
            get_bank_data()
        new_balance = users[str(user.id)]["wallet"]
        await ctx.send(f"You have flipped HEADS and have won {arg[0]} coins. You now have {new_balance}")
    return True
    
@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content[0] == "-":
        return
    users = await get_bank_data()

    random_multiplier = random.randint(1,10)
    msg_len = len(message.content)
    earnings = random_multiplier * msg_len
    
    users[str(message.author.id)]["wallet"] += earnings
    with open("eco.json", "w") as f:
        json.dump(users, f)

bot.run(token)