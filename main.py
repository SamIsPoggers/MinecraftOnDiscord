import discord
from discord import app_commands
from discord.ext import tasks


from javascript import require, On
mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')
pvp = require('mineflayer-pvp').plugin
RANGE_GOAL = 1

global movements


intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

global ip, port
ip, port = -1, 25565
global bot



@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1289886572522508422))
    print("Ready!")

    global discord_channel
    discord_channel = client.get_channel(1289886572958842945)


# Add the guild ids in which the slash command will appear.
# If it should be in all, remove the argument, but note that
# it will take some time (up to an hour) to register the
# command if it's for all guilds.
@tree.command(
    name="testcommand",
    description="replies the command",
    guild=discord.Object(id=1289886572522508422)
)
async def testcommand(interaction):
    await interaction.response.send_message("Hello!")

#SET IP AND PORT FOR THE BOT
@tree.command(
    name="ipset",
    description="setip for minecraft bot",
    guild=discord.Object(id=1289886572522508422)
)
async def ipset(interaction, botip: str, botport: int):
    global ip, port
    ip = botip
    port = botport
    await interaction.response.send_message(f'Set IP to {botip} and Port to {botport}')
    print(ip)
    print(port)

#JOIN THE SERVER AS THE BOT
@tree.command(
    name="joinserver",
    description="join server with username",
    guild=discord.Object(id=1289886572522508422)
)
async def joinserver(interaction, username: str):
    global ip, port, bot, discord_channel
    await interaction.response.send_message(f'Joined Server with username {username}')
    bot = mineflayer.createBot({'host': ip,'port': port,'auth': 'offline','username': username})

    bot.loadPlugin(pathfinder.pathfinder)
    bot.loadPlugin(pvp)


    # Listen for chat events and forward messages to Discord
    @On(bot, 'chat')
    def handle_chat(this, username, message, *args):
        if username != bot.username and discord_channel:
            client.loop.create_task(discord_channel.send(f"{username}: {message}"))

    @On(bot, 'spawn')
    def handle(*args):
        global movements
        movements = pathfinder.Movements(bot)

    
#CHAT IN THE SERVER AS THE BOT
@tree.command(
    name="chat",
    description="chat with the bot",
    guild=discord.Object(id=1289886572522508422)
)
async def chat(interaction, chatmessage: str):
    global ip, port, bot
    await interaction.response.send_message(f'said {chatmessage}')
    bot.chat(chatmessage)


#MOVE
@tree.command(
    name="goto",
    description="go to a coordinate",
    guild=discord.Object(id=1289886572522508422)
)
async def chat(interaction, x: int, y:int, z:int):
    global bot, movements
    bot.pathfinder.setMovements(movements)
    bot.pathfinder.setGoal(pathfinder.goals.GoalNear(x, y, z, RANGE_GOAL))


#PVP
@tree.command(
    name="pvp",
    description="pvp a player",
    guild=discord.Object(id=1289886572522508422)
)
async def chat(interaction, username: str):
    global bot
    player = bot.players[username]
    bot.pvp.attack(player.entity)

#PVP STOP
@tree.command(
    name="pvpstop",
    description="stop pvp a player",
    guild=discord.Object(id=1289886572522508422)
)
async def chat(interaction):
    global bot
    bot.pvp.stop()


#MINE COMMAND
@tree.command(
    name="mine",
    description="Mine a specified block type",
    guild=discord.Object(id=1289886572522508422)
)
async def mine(interaction, block: str):
    global bot
    await interaction.response.send_message(f'Trying to mine {block}...')

    # Check if the block is valid
    if block not in bot.registry.itemsByName:
        await interaction.followup.send(f'Block {block} not found in the registry.')
        return

    block_id = bot.registry.itemsByName[block].id

    # Find the nearest block of the specified type
    nearby_blocks = bot.findBlocks({
        'matching': block_id,
        'maxDistance': 64,
        'count': 1
    })

    # Debug output: print nearby blocks
    print(f"Nearby blocks found: {nearby_blocks}")  # Added debug output

    if not nearby_blocks:  # Check if nearby_blocks is empty
        await interaction.followup.send(f'No {block} found nearby.')
        return

    # Get the first block from nearby_blocks
    nearest_block = nearby_blocks[0]
    x, y, z = nearest_block['x'], nearest_block['y'], nearest_block['z']
    await interaction.followup.send(f'Found {block} at ({x}, {y}, {z}). Moving to mine it.')

    # Set goal to the block's location
    bot.pathfinder.setGoal(pathfinder.goals.GoalNear(x, y, z, RANGE_GOAL))

    @On(bot, 'goal_reached')
    def on_goal_reached(*args):
        try:
            bot.chat(f'Reached {block}. Now mining...')
            target_block = bot.blockAt(x, y, z)

            # Check if the block can be mined and its name matches
            if target_block and target_block.name == block:
                bot.collectBlock.collect(target_block, lambda err: handle_dig_response(err, block))
            else:
                bot.chat(f'Error: Found a {target_block.name} instead of {block} at the target location.')
        except Exception as e:
            bot.chat(f'An error occurred while trying to mine: {str(e)}')

def handle_dig_response(err, block):
    if err:
        print(f'Error while mining {block}: {err}')  # Log the error for debugging
        bot.chat(f'Error while mining {block}: {str(err)}')
    else:
        bot.chat(f'Successfully mined {block}.')



client.run('MTI5MTcxNjA0NDUyMzcwMDIzNA.GKhy0p.UUU5vL0oC3zmtR7ODkYn3YCfTnbZHo4_W2zdmU')
