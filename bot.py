import json
import os
import random
import math
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
        
        
## Help 
@bot.command()
async def Help(ctx):
    menu = [
        ["Chatting", "Typing in chat awards you with a random amount of gold!"],
        ["-balance", "Shows your gold balance"],
        ["-work", "Gives a random amount between 1 - 100 gold"],
        ["-coinflip number, half, max", "Flips a gold. Heads and you win what you wager and vice-versa"],
        ["-leaderboard", "Shows the top 10 richest users in the server"],
        ["-lotto", "1 in a million chance to win a large jackpot. Costs 100 gold to play. Jackpot increases if you lose!"],
        ["-jackpot", "Shows the current jackpot"],
        ["-pvp @user", "Use this against another user. You will win or lose a random amount of available gold based on opponent's balance!"],
        ["-givegold @user number", "If you have enough gold to give, this command will give the target user your gold."]
    ]
    em = discord.Embed(title = f"Commands Menu", color=discord.Color.blue() )
    for item in menu:
        em.add_field(name = item[0], value = item[1], inline=False)
    await ctx.send(embed = em)
    return
        
## Economy
@bot.command()
async def balance(ctx):
    await open_account(ctx.author)
    guilds = await get_bank_data()
    user = ctx.author
    
    wallet_amount = guilds[str(user.guild.id)][str(user.id)]["wallet"]
    
    em = discord.Embed(title = f"{ctx.author.name}'s  balance", color=discord.Color.blue())
    em.add_field(name = "Gold balance", value = f"{wallet_amount} gold")
    await ctx.send(embed = em)
    
@bot.command()
async def work(ctx):
    user = ctx.author
    await open_account(user)
    guilds = await get_bank_data()
    earnings = random.randrange(101)
    
    await ctx.channel.send(f"{user.mention} has earned {earnings} gold!")
    
    guilds[str(user.guild.id)][str(user.id)]["wallet"] += earnings
    
    with open("eco.json", "w") as f:
        json.dump(guilds, f)
        
async def open_account(user):
    guilds = await get_bank_data()
    if guilds.get(str(user.guild.id)) == None:
        guilds[str(user.guild.id)] = {}
        
    if str(user.id) not in guilds[str(user.guild.id)]:
        guilds[str(user.guild.id)][str(user.id)] = {}
        guilds[str(user.guild.id)][str(user.id)]["wallet"] = 0
        
    with open("eco.json", "w") as f:
        json.dump(guilds, f)
    return True

async def get_bank_data():
    with open("eco.json", "r") as f:
        guilds = json.load(f)   
    return guilds 

@bot.command()
async def coinflip(ctx, *arg):
    user = ctx.author
    guilds = await get_bank_data()
    wallet_amount = guilds[str(user.guild.id)][str(user.id)]["wallet"]
    if arg == (): 
        await ctx.send("Provide a wager amount in numbers")
        return
    if arg[0] == "max":
        arg = int(wallet_amount), #comma turns assigned into tuple
    elif arg[0] == "half":
        arg = int(wallet_amount)/2, #comma turns assigned into tuple
    elif int(arg[0]) < 0:
        await ctx.send(f"Nice try, {user.mention} you loser")
        return
    elif int(wallet_amount) < int(arg[0]):
        await ctx.send(f"You're broke, {user.mention}")
        return
    # elif int(arg[0]) > 10000:
    #     await ctx.send("You can only bet 10000 gold at a time")
    #     return
    
    flip_result = random.randint(0, 1)
    if flip_result == 0:
        guilds[str(user.guild.id)][str(user.id)]["wallet"] -= int(arg[0])
        with open("eco.json", "w") as f:
            json.dump(guilds, f)
        await get_bank_data()
        new_balance = guilds[str(user.guild.id)][str(user.id)]["wallet"]
        em = discord.Embed(title = f"{ctx.author.name} flipped TAILS!", color=discord.Color.red())
        em.add_field(name = "Lost Wager", value = arg[0])
        em.add_field(name = "New Balance", value = new_balance)
        await ctx.send(embed = em)
    else:
        guilds[str(user.guild.id)][str(user.id)]["wallet"] += int(arg[0])
        with open("eco.json", "w") as f:
            json.dump(guilds, f)
        await get_bank_data()
        new_balance = guilds[str(user.guild.id)][str(user.id)]["wallet"]
        em = discord.Embed(title = f"{ctx.author.name} flipped HEADS!", color=discord.Color.green())
        em.add_field(name = "Winnings", value = arg[0])
        em.add_field(name = "New Balance", value = new_balance)
        await ctx.send(embed = em)
    return True
    
@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content[0] == "-":
        return
    user = message.author
    await open_account(user)
    print("test", user.guild.id)
    guilds = await get_bank_data()

    random_multiplier = random.randint(1,3)
    msg_len = len(message.content)
    if msg_len > 200:
        msg_len = 200
    earnings = random_multiplier * msg_len
    
    guilds[str(user.guild.id)][str(user.id)]["wallet"] += earnings
    with open("eco.json", "w") as f:
        json.dump(guilds, f)
    return

@bot.command()
async def leaderboard(ctx, x=10):
    user = ctx.author
    with open('eco.json', 'r') as f:
    
        guilds = json.load(f)
    
    leaderboard = {}
    total=[]
    for guy in list(guilds[str(user.guild.id)]):
        if guy == "jackpot":
           continue
        name = int(guy)
        total_amt = guilds[str(user.guild.id)][str(guy)]["wallet"]
        leaderboard[total_amt] = name
        total.append(total_amt)
    

    total = sorted(total,reverse=True)
  

    em = discord.Embed(
        title = f'Top {x} richest members in {ctx.guild.name}',
        description = 'The richest people in this server',
        color=discord.Color.orange()
    )
  
    index = 1
    for amt in total:
        id_ = leaderboard[amt]
        member = await bot.fetch_user(id_)  
        em.add_field(name = f'{index}: {member}', value = f'{amt} gold', inline=False)
    
        if index == x:
            break
        else:
            index += 1
      
    await ctx.send(embed = em)
  
  
@bot.command()
async def lotto(ctx):
    user = ctx.author
    guilds = await get_bank_data()
    wallet_amount = guilds[str(user.guild.id)][str(user.id)]["wallet"]
    if wallet_amount < 100:
        await ctx.send(f"A lotto ticket costs 100 gold. \nYou only have {wallet_amount} gold, {user.mention}!")
        return
    jackpot = guilds["jackpot"]
    winning_num = random.randint(1,101)
    user_drawing = random.randint(1,101)
    if winning_num == user_drawing:
        guilds[str(user.guild.id)][str(user.id)]["wallet"] += jackpot
        em = discord.Embed(
            title = f"{user} drew {user_drawing}. The winning number was {winning_num}!",
            color=discord.Color.teal()
        )
        with open("eco.json", "w") as f:
            json.dump(guilds, f)
        await get_bank_data()
        new_balance = guilds[str(user.guild.id)][str(user.id)]["wallet"]
        em.add_field(name = f"You have won the {jackpot} gold jackpot!", value = f"Your new balance is {new_balance}", inline=False)
        guilds["jackpot"] = 1000000
        with open("eco.json", "w") as f:
            json.dump(guilds, f)
    else:
        jackpot += 50
        guilds["jackpot"] += 50
        guilds[str(user.guild.id)][str(user.id)]["wallet"] -= 100
        with open("eco.json", "w") as f:
            json.dump(guilds, f)
        await get_bank_data()
        new_balance = guilds[str(user.guild.id)][str(user.id)]["wallet"]
        em = discord.Embed(
            title = f"{user} drew {user_drawing}. The winning number was {winning_num}!",
            color=discord.Color.red()
        )
        em.add_field(name = f"You paid 100 gold for a ticket.\nYour ticket doesn't match the winning number.. \nSorry, better luck next time! \nYou now have {new_balance} gold.", value = f"The jackpot is now {jackpot}", inline=False)
    
    await ctx.send(embed = em)
    
@bot.command()
async def jackpot(ctx):
    user = ctx.author
    users = await get_bank_data()
    jackpot = users["jackpot"]
    wallet = users[str(user.guild.id)][str(user.id)]["wallet"]
    em = discord.Embed(
        title = f"The jackpot is currently {jackpot} gold!"
    )
    em.add_field(name = f"Feelin' lucky?", value= f"You currently have {wallet} gold. \nIt costs 100 gold to play. \nType -lotto to try your luck!")
    await ctx.send(embed = em)

@bot.command()
async def pvp(ctx, target: discord.Member):
    user = ctx.author
    guilds = await get_bank_data()
    your_wallet = guilds[str(user.guild.id)][str(user.id)]["wallet"]
    their_wallet = guilds[str(target.guild.id)][str(target.id)]["wallet"]
    your_roll = random.randint(1, 101)
    their_roll = random.randint(1, 101)
    bounty = (random.randint(10, 31)) / 100
    
    
    if your_roll > their_roll:
        
        earnings = math.ceil(their_wallet * bounty)
        guilds[str(user.guild.id)][str(user.id)]["wallet"] += earnings
        guilds[str(user.guild.id)][str(target.id)]["wallet"] -= earnings
        
        with open("eco.json", "w") as f:
            json.dump(guilds, f)
        await get_bank_data()
        your_new_balance = guilds[str(user.guild.id)][str(user.id)]["wallet"]
        their_new_balance = guilds[str(user.guild.id)][str(target.id)]["wallet"]
        em = discord.Embed(
        title = f"You defeated {target}!",
        color=discord.Color.green()
    )
        em.add_field(name = f"You rolled {your_roll} and {target} rolled {their_roll}", value = f"{target} gave you {earnings} gold to leave them alone. You now have {your_new_balance} gold and {target} has {their_new_balance} gold left")
        await ctx.send(embed = em)
        
    elif your_roll == their_roll:
        em = discord.Embed(
        title = f"{user} and {target} ended up in a draw! \nNo winner."
    )
        # em.add_field(name = f"")
        await ctx.send(embed = em)
        
    else:
        
        losses = math.ceil(your_wallet * bounty)
        guilds[str(user.guild.id)][str(user.id)]["wallet"] -= losses
        guilds[str(user.guild.id)][str(target.id)]["wallet"] += losses
        
        with open("eco.json", "w") as f:
            json.dump(guilds, f)
        await get_bank_data()
        your_new_balance = guilds[str(user.guild.id)][str(user.id)]["wallet"]
        their_new_balance = guilds[str(user.guild.id)][str(target.id)]["wallet"]
        
        em = discord.Embed(
        title = f"{target} has defeated you!",
        color=discord.Color.red()
    )
        em.add_field(name = f"You rolled {your_roll} and {target} rolled {their_roll}" , value = f"You gave {target} {losses} gold to leave you alone. You now have {your_new_balance} gold left and {target} has {their_new_balance} gold")
        await ctx.send(embed = em)
        
@bot.command()
async def addgold(ctx, target: discord.Member, gold):
    user = ctx.author
    guilds = await get_bank_data()
    if str(user.id) == "137812388614373376":
        guilds[str(user.guild.id)][str(target.id)]["wallet"] += int(gold)
        
        with open("eco.json", "w") as f:
            json.dump(guilds, f)
        await get_bank_data()
            
        new_balance = guilds[str(user.guild.id)][str(target.id)]["wallet"]
        await ctx.send(f"Admin has added {gold} gold to {target.mention}'s wallet. \n They now have {new_balance} gold.")
    else:
        await ctx.send("Unauthorized user")
    
@bot.command()
async def givegold(ctx, target: discord.Member, gold):
    user = ctx.author
    guilds = await get_bank_data()
    if int(gold) < 0:
        await ctx.send(f"You cannot give negative gold")
        return
    elif guilds[str(user.guild.id)][str(user.id)]["wallet"] < int(gold):
        await ctx.send(f"You don't have enough gold to give")
    else:
        guilds[str(user.guild.id)][str(user.id)]["wallet"] -= int(gold)
        guilds[str(user.guild.id)][str(target.id)]["wallet"] += int(gold)
        with open("eco.json", "w") as f:
            json.dump(guilds, f)
        await get_bank_data()
        
        your_new_balance = guilds[str(user.guild.id)][str(user.id)]["wallet"]
        target_new_balance = guilds[str(user.guild.id)][str(target.id)]["wallet"]
        await ctx.send(f"{user.mention} has given {gold} gold to {target.mention}. \n{user} now has {your_new_balance} gold \n{target} now has {target_new_balance} gold")
        
        
bot.run(token)