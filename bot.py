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
        ["-work", "Gives a random amount between 1 - 1000 gold"],
        ["-deposit number", "Deposits your gold to your bank account for safekeeping"],
        ["-withdraw number", "Withdraw your gold from your bank account"],
        ["-coinflip number, half, max", "Flips a gold. Heads and you win what you wager and vice-versa"],
        ["-leaderboard", "Shows the top 10 richest users in the server"],
        ["-lotto", "1 in 10000 chance to win a large jackpot. Costs 100 gold to play. Jackpot increases if you lose!"],
        ["-jackpot", "Shows the current jackpot"],
        ["-pvp @user", "Use this against another user. You will win or lose a random amount of available gold based on opponent's balance!"],
        ["-givegold @user number", "If you have enough gold to give, this command will give the target user your gold."],
        ["-bankheist @user","Take a chance to steal from your targets' bank account. \nWARNING: FAILING MAY HAVE HARSH CONSEQUENCES!! \nHas a 1-hour cooldown"]
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
    bank_amount = guilds[str(user.guild.id)][str(user.id)]["bank"]
    
    em = discord.Embed(title = f"{ctx.author.name}'s  balance", color=discord.Color.blue())
    em.add_field(name = "Wallet balance", value = f"{wallet_amount} gold")
    em.add_field(name = "Bank balance", value = f"{bank_amount} gold")
    await ctx.send(embed = em)
    
    
@bot.command()
async def profile(ctx, target: discord.Member):
    await open_account(target)
    guilds = await get_bank_data()
    # user = ctx.author
    
    wallet_amount = guilds[str(target.guild.id)][str(target.id)]["wallet"]
    bank_amount = guilds[str(target.guild.id)][str(target.id)]["bank"]
    
    em = discord.Embed(title = f"{target}'s  balance", color=discord.Color.blue())
    em.add_field(name = "Wallet balance", value = f"{wallet_amount} gold")
    em.add_field(name = "Bank balance", value = f"{bank_amount} gold")
    await ctx.send(embed = em)
    
    
@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def work(ctx):
    user = ctx.author
    await open_account(user)
    guilds = await get_bank_data()
    earnings = random.randrange(1001)
    
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
        guilds[str(user.guild.id)][str(user.id)]["bank"] = 0
        guilds[str(user.guild.id)][str(user.id)]["inventory"] = []
        guilds[str(user.guild.id)][str(user.id)]["hp"] = 100
        guilds[str(user.guild.id)][str(user.id)]["xp"] = 0
        guilds[str(user.guild.id)][str(user.id)]["level"] = 1
        
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
    # print(message.guild, message.channel, message.author, message.content)
    if message.content[0] == "-":
        return
    user = message.author
    await open_account(user)
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
        bank = guilds[str(user.guild.id)][str(id_)]["bank"]
        em.add_field(name = f'{index}: {member}', value = f'Wallet: {amt} gold \n Bank: {bank} gold', inline=False)
    
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
        em.add_field(name = f"You have won the {jackpot} gold jackpot!", value = f"Your new balance is {new_balance} gold", inline=False)
        guilds["jackpot"] = 10000000
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
        em.add_field(name = f"You paid 100 gold for a ticket.\nYour ticket doesn't match the winning number.. \nSorry, better luck next time! \nYou now have {new_balance} gold.", value = f"The jackpot is now {jackpot} gold", inline=False)
    
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
@commands.cooldown(1, 15, commands.BucketType.user)
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
        await ctx.send(f"You don't have enough gold in your wallet to give")
    else:
        guilds[str(user.guild.id)][str(user.id)]["wallet"] -= int(gold)
        guilds[str(user.guild.id)][str(target.id)]["wallet"] += int(gold)
        with open("eco.json", "w") as f:
            json.dump(guilds, f)
        await get_bank_data()
        
        your_new_balance = guilds[str(user.guild.id)][str(user.id)]["wallet"]
        target_new_balance = guilds[str(user.guild.id)][str(target.id)]["wallet"]
        await ctx.send(f"{user.mention} has given {gold} gold to {target.mention}. \n{user} now has {your_new_balance} gold \n{target} now has {target_new_balance} gold")
        
@bot.command()
async def deposit(ctx, gold):
    user = ctx.author
    guilds = await get_bank_data()
    if gold == "max":
        gold = guilds[str(user.guild.id)][str(user.id)]["wallet"]
        # print(gold)
    if int(gold) < 0:
        await ctx.send(f"You cannot deposit negative gold")
        return
    
    elif guilds[str(user.guild.id)][str(user.id)]["wallet"] < int(gold):
        await ctx.send(f"You don't have enough gold to deposit")
    else:
        guilds[str(user.guild.id)][str(user.id)]["wallet"] -= int(gold)
        guilds[str(user.guild.id)][str(user.id)]["bank"] += int(gold)
        with open("eco.json", "w") as f:
            json.dump(guilds, f)
        await get_bank_data()
        
        wallet_new_balance = guilds[str(user.guild.id)][str(user.id)]["wallet"]
        bank_new_balance = guilds[str(user.guild.id)][str(user.id)]["bank"]
        em = discord.Embed(
        title = f"{user} deposited {gold} gold",
        color=discord.Color.teal()
    )
        em.add_field(name = f"Wallet balance", value = f"{wallet_new_balance} gold")
        em.add_field(name = f"Bank balance", value = f"{bank_new_balance} gold")
        await ctx.send(embed = em)
        # await ctx.send(f"{user.mention} has deposited {gold} gold into their bank account. \n{user} now has {bank_new_balance} gold in their bank account")

@bot.command()
async def withdraw(ctx, gold):
    user = ctx.author
    guilds = await get_bank_data()
    if gold == "max":
        gold = guilds[str(user.guild.id)][str(user.id)]["bank"]
    if int(gold) < 0:
        await ctx.send(f"You cannot withdraw negative gold")
        return
    elif guilds[str(user.guild.id)][str(user.id)]["bank"] < int(gold):
        await ctx.send(f"You don't have enough gold to withdraw")
    else:
        guilds[str(user.guild.id)][str(user.id)]["bank"] -= int(gold)
        guilds[str(user.guild.id)][str(user.id)]["wallet"] += int(gold)
        with open("eco.json", "w") as f:
            json.dump(guilds, f)
        await get_bank_data()
        
        wallet_new_balance = guilds[str(user.guild.id)][str(user.id)]["wallet"]
        bank_new_balance = guilds[str(user.guild.id)][str(user.id)]["bank"]
        em = discord.Embed(
        title = f"{user} withdrew {gold} gold",
        color=discord.Color.teal()
    )
        em.add_field(name = f"Wallet balance", value = f"{wallet_new_balance} gold")
        em.add_field(name = f"Bank balance", value = f"{bank_new_balance} gold")
        await ctx.send(embed = em)
        # await ctx.send(f"{user.mention} has withdrew {gold} gold from their bank account. \n{user} now has {bank_new_balance} gold in their wallet")
        
@bot.command()
@commands.cooldown(1, 3600, commands.BucketType.user)
async def bankheist(ctx, target: discord.Member):
    user = ctx.author
    guilds = await get_bank_data()
    roll = random.randint(0,100)
    if user == target:
        await ctx.send("You can't rob yourself!")
        return
    print("====================ROLL=================",user ,roll)
    if roll > 66:
        percentage = random.randint(10, 75)
        bank = guilds[str(user.guild.id)][str(target.id)]["bank"]
        loot = math.ceil(int(bank) * percentage / 100)
        guilds[str(user.guild.id)][str(target.id)]["bank"] -= int(loot)
        guilds[str(user.guild.id)][str(user.id)]["bank"] += int(loot)
        with open("eco.json", "w") as f:
            json.dump(guilds, f)
        await get_bank_data()
        em = discord.Embed(title = f"{user} has successfully raided the bank! {user} has stolen {loot} gold from {target}'s bank vault",
        color=discord.Color.blue()
        )
        new_bank_balance = guilds[str(user.guild.id)][str(user.id)]["bank"]
        em.add_field(name = f"{user}'s new bank balance", value = f"{new_bank_balance} gold")
        await ctx.send(embed = em)
        return
        
    elif 5 < roll < 67:
        em = discord.Embed(
        title = f"{user} got intercepted by the police and has failed the bank heist!",
        color=discord.Color.red()
        )
        await ctx.send(embed = em)
        return
        
    elif roll < 6:
        mybank = guilds[str(user.guild.id)][str(user.id)]["bank"]
        percentage = random.randint(10, 75)
        mistake = math.ceil(int(mybank) * percentage / 100)
        guilds[str(user.guild.id)][str(user.id)]["bank"] -= int(mistake)
        with open("eco.json", "w") as f:
            json.dump(guilds, f)
        # await get_bank_data()
        em = discord.Embed(
        title = f"{user} destroyed {mistake} gold from their own bank vault",
        color=discord.Color.red()
        )
        # em.add_field(name = f"Wallet balance", value = f"{wallet_new_balance} gold")
        await ctx.send(embed = em)
        return
    # await ctx.send('BANK HEIST TEST')
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"{ctx.author.mention} This command is on cooldown, you can try again in {round(error.retry_after)} seconds")
        
@bot.command()
async def createinv(ctx): #this can be used to add new slots / clear inventory / reset stats
    user = ctx.author
    if str(user.id) == "137812388614373376":
        guilds = await get_bank_data()
        
        for guild in guilds:
            if guild == "jackpot":
                continue
            print("is it working?")
            # print(guilds[guild])
            for mem in guilds[guild]:
                print(guilds[guild][mem])
                guilds[guild][mem]["inventory"] = []
                guilds[guild][mem]["hp"] = 100
                guilds[guild][mem]["xp"] = 0
                guilds[guild][mem]["level"] = 1
            print("maybe\n\n\n")
        with open("eco.json", "w") as f:
            json.dump(guilds, f)
    else:
        await ctx.send("Unauthorized user")
    await ctx.send("Work in progress command")
        
        
@bot.command()
async def shop(ctx, item, amt):
    user = ctx.author
    menu = {"potion": 20}
    await ctx.send("SHOP IS UNDER CONSTRUCTION")
    
@bot.command()
async def use(ctx):
    await ctx.send("USE IS UNDER CONSTRUCTION")


@bot.command()
@commands.cooldown(1, 900, commands.BucketType.user)
async def letmeholdthatdollarealquick(ctx, target: discord.Member):
    user = ctx.author
    guilds = await get_bank_data()
    
    if user == target:
        await ctx.send("Yo {user}, go hold someone else's dolla")
        return
    
    roll = random.randint(1, 100)
    print("Roll", user, roll)
    
    
    victim_wallet = guilds[str(user.guild.id)][str(target.id)]["wallet"]
    if victim_wallet < 1:
        em = discord.Embed(
        title = f"{target} doesn't have any money in their wallet...",
        color=discord.Color.blue()
        )
        await ctx.send(embed = em)
        return
    
    if roll >= 80:
        target_wallet = guilds[str(user.guild.id)][str(target.id)]["wallet"]
        guilds[str(user.guild.id)][str(user.id)]["wallet"] += target_wallet
        guilds[str(user.guild.id)][str(target.id)]["wallet"] -= target_wallet
        with open("eco.json", "w") as f:
            json.dump(guilds, f)
            
        await get_bank_data()
        author_wallet = guilds[str(user.guild.id)][str(user.id)]["wallet"]
        target_wallet_nb = guilds[str(user.guild.id)][str(target.id)]["wallet"]
    
    
        em = discord.Embed(
        title = f"{target} exposed their wallet and {user} snatched it and ran off into the distance",
        color=discord.Color.blue()
        )
        em.add_field(name = f"{user}'s new Wallet balance", value = f"{author_wallet} gold")
        em.add_field(name = f"{target}'s new Wallet balance", value = f"{target_wallet_nb} gold")
    
        await ctx.send(embed = em)
        
    elif 50 <= roll <= 80:
        guilds[str(user.guild.id)][str(user.id)]["wallet"] += 1
        guilds[str(user.guild.id)][str(target.id)]["wallet"] -= 1
        with open("eco.json", "w") as f:
            json.dump(guilds, f)
            
        await get_bank_data()
        author_wallet = guilds[str(user.guild.id)][str(user.id)]["wallet"]
        target_wallet_nb = guilds[str(user.guild.id)][str(target.id)]["wallet"]
        em = discord.Embed(
        title = f"{target} gave {user} a dollar and went on their merry way",
        color=discord.Color.blue()
        )
        em.add_field(name = f"{user}'s new Wallet balance", value = f"{author_wallet} gold")
        em.add_field(name = f"{target}'s new Wallet balance", value = f"{target_wallet_nb} gold")
    
        await ctx.send(embed = em)
        
    elif roll < 50:
        em = discord.Embed(
        title = f"{target} told {user} to buzz off.",
        color=discord.Color.blue()
        )
    
        await ctx.send(embed = em)
        

bot.run(token)