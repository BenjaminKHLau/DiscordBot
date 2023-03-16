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
        
## Economy
@bot.command()
async def balance(ctx):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    
    wallet_amount = users[str(user.id)]["wallet"]
    
    em = discord.Embed(title = f"{ctx.author.name}'s  balance", color=discord.Color.blue())
    em.add_field(name = "Wallet balance", value = wallet_amount)
    # print(em, "HELLO")
    await ctx.send(embed = em)
    
@bot.command()
async def work(ctx):
    user = ctx.author
    await open_account(user)
    users = await get_bank_data()
    # print("USER STUFF", ctx, user.nick)
    earnings = random.randrange(101)
    
    await ctx.channel.send(f"{user.mention} has earned {earnings} coins!")
    
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
    #     await ctx.send("You can only bet 10000 coins at a time")
    #     return
    
    flip_result = random.randint(0, 1)
    if flip_result == 0:
        users[str(user.id)]["wallet"] -= int(arg[0])
        with open("eco.json", "w") as f:
            json.dump(users, f)
        await get_bank_data()
        new_balance = users[str(user.id)]["wallet"]
        em = discord.Embed(title = f"{ctx.author.name} flipped TAILS!", color=discord.Color.red())
        em.add_field(name = "Lost Wager", value = arg[0])
        em.add_field(name = "New Balance", value = new_balance)
        await ctx.send(embed = em)
        # await ctx.send(f"{user} flipped TAILS and have LOST {arg[0]} coins.  {user} now has {new_balance}")
    else:
        users[str(user.id)]["wallet"] += int(arg[0])
        with open("eco.json", "w") as f:
            json.dump(users, f)
        await get_bank_data()
        new_balance = users[str(user.id)]["wallet"]
        em = discord.Embed(title = f"{ctx.author.name} flipped HEADS!", color=discord.Color.green())
        em.add_field(name = "Winnings", value = arg[0])
        em.add_field(name = "New Balance", value = new_balance)
        await ctx.send(embed = em)
        # await ctx.send(f"{user} flipped HEADS and have won {arg[0]} coins. {user} now has {new_balance}")
    return True
    
@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content[0] == "-":
        return
    user = message.author
    await open_account(user)
    # print("test", message)
    users = await get_bank_data()

    random_multiplier = random.randint(1,3)
    msg_len = len(message.content)
    if msg_len > 200:
        msg_len = 200
    earnings = random_multiplier * msg_len
    
    users[str(message.author.id)]["wallet"] += earnings
    with open("eco.json", "w") as f:
        json.dump(users, f)
    return

@bot.command()
async def leaderboard(ctx, x=10):
    with open('eco.json', 'r') as f:
    
        users = json.load(f)
    
    leaderboard = {}
    total=[]
  
    for user in list(users):
        if user == "jackpot":
           continue
        name = int(user)
        total_amt = users[str(user)]['wallet']
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
        em.add_field(name = f'{index}: {member}', value = f'{amt} coins', inline=False)
        print(member)
    
        if index == x:
            break
        else:
            index += 1
      
    await ctx.send(embed = em)
  
  
@bot.command()
async def lotto(ctx):
    user = ctx.author
    users = await get_bank_data()
    wallet_amount = users[str(user.id)]["wallet"]
    if wallet_amount < 100:
        await ctx.send(f"A lotto ticket costs 100 coins. \nYou only have {wallet_amount} coins, {user.mention}!")
        return
    # users["jackpot"] = 1000000
    jackpot = users["jackpot"]
    winning_num = random.randint(1,1001)
    user_drawing = random.randint(1,1001)
    with open("eco.json", "w") as f:
        json.dump(users, f)
    if winning_num == user_drawing:
        users[str(user.id)]["wallet"] += jackpot
        jackpot = 1000000
        with open("eco.json", "w") as f:
            json.dump(users, f)
        await get_bank_data()
        em = discord.Embed(
            title = f"{user} drew {user_drawing}. The winning number was {winning_num}!",
            color=discord.Color.teal()
        )
        new_balance = users[str(user.id)]["wallet"]
        em.add_field(name = f"You have won the {jackpot} coin jackpot!", value = f"Your new balance is {new_balance}", inline=False)
    else:
        jackpot += 50
        users["jackpot"] += 50
        users[str(user.id)]["wallet"] -= 100
        with open("eco.json", "w") as f:
            json.dump(users, f)
        await get_bank_data()
        new_balance = users[str(user.id)]["wallet"]
        em = discord.Embed(
            title = f"{user} drew {user_drawing}. The winning number was {winning_num}!",
            color=discord.Color.red()
        )
        em.add_field(name = f"You paid 100 coins for a ticket.\nYour ticket doesn't match the winning number.. \nSorry, better luck next time! \nYou now have {new_balance} coins.", value = f"The jackpot is now {jackpot}", inline=False)
    
    await ctx.send(embed = em)
    
@bot.command()
async def jackpot(ctx):
    user = ctx.author
    users = await get_bank_data()
    jackpot = users["jackpot"]
    wallet = users[str(user.id)]["wallet"]
    # print(jackpot)
    em = discord.Embed(
        title = f"The jackpot is currently {jackpot} coins!"
    )
    em.add_field(name = f"Feelin' lucky?", value= f"You currently have {wallet} coins. \nIt costs 100 coins to play. \nType -lotto to try your luck!")
    await ctx.send(embed = em)

@bot.command()
async def pvp(ctx, target: discord.Member):
    user = ctx.author
    users = await get_bank_data()
    your_wallet = users[str(user.id)]["wallet"]
    their_wallet = users[str(target.id)]["wallet"]
    your_roll = random.randint(1, 101)
    their_roll = random.randint(1, 101)
    bounty = (random.randint(10, 31)) / 100
    
    
    if your_roll > their_roll:
        
        earnings = math.ceil(their_wallet * bounty)
        users[str(user.id)]["wallet"] += earnings
        users[str(target.id)]["wallet"] -= earnings
        
        with open("eco.json", "w") as f:
            json.dump(users, f)
        await get_bank_data()
        your_new_balance = users[str(user.id)]["wallet"]
        their_new_balance = users[str(target.id)]["wallet"]
        em = discord.Embed(
        title = f"You defeated {target}!",
        color=discord.Color.green()
    )
        em.add_field(name = f"You rolled {your_roll} and {target} rolled {their_roll}", value = f"{target} gave you {earnings} coins to leave them alone. You now have {your_new_balance} coins and {target} has {their_new_balance} coins left")
        await ctx.send(embed = em)
        
    elif your_roll == their_roll:
        em = discord.Embed(
        title = f"{user} and {target} ended up in a draw! \nNo winner."
    )
        # em.add_field(name = f"")
        await ctx.send(embed = em)
        
    else:
        
        losses = math.ceil(your_wallet * bounty)
        users[str(user.id)]["wallet"] -= losses
        users[str(target.id)]["wallet"] += losses
        
        with open("eco.json", "w") as f:
            json.dump(users, f)
        await get_bank_data()
        your_new_balance = users[str(user.id)]["wallet"]
        their_new_balance = users[str(target.id)]["wallet"]
        
        em = discord.Embed(
        title = f"{target} has defeated you!",
        color=discord.Color.red()
    )
        em.add_field(name = f"You rolled {your_roll} and {target} rolled {their_roll}" , value = f"You gave {target} {losses} coins to leave you alone. You now have {your_new_balance} coins left and {target} has {their_new_balance} coins")
        await ctx.send(embed = em)
        
    
bot.run(token)