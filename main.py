import discord
import os
import requests
import json
import wallet

client = discord.Client()


def remove_entry(collection_name):
    name = collection_name.lower()
    if wallet.get_policy(name) is not None:
        wallet.remove_collection(name)
        return "Removed key {0}".format(collection_name)
    else:
        return "No key present with this name {0}".format(collection_name)


def update_complete_database():
    response = requests.get("https://server.jpgstoreapis.com/collection/mostVolume?page=1&take=1000")
    json_data = json.loads(response.text)
    for json_dict in json_data:
        display_name = json_dict["display_name"].lower().replace(" ", "")
        policy_id = json_dict["policy_id"]
        if wallet.get_policy(policy_id) is None:
            wallet.init_collection(display_name, policy_id)
        else:
            print("Collection Name already present {0}".format(display_name))
    return "DB update Successful"


def update_database(name, policy_id):
    name = name.lower()
    if wallet.get_policy(name) is None:
        wallet.init_collection(name, policy_id)
        return "Collection Inserted"
    else:
        return "Collection Already present"


def wallet_info(address):
    try:
        response = requests.get("http://20.241.223.176:8080/user-holdings?address={0}".format(address))
        json_data = json.loads(response.text)
        return embed_wallet_info(json_data)
    except TypeError:
        print("Something went wrong")
        raise


def embed_wallet_info(mapp):
    embed = discord.Embed(
        title="Wallet Worth {0}".format(mapp["walletWorth"]), color=discord.Color.orange())
    for ele in mapp["_userResults"][:10]:
        embed.add_field(name="Collection Name: {0}".format(ele["wallet"]), value="Quantity: {0}".format(ele["holding"]),
                        inline=False)
    return embed


def commands():
    embed = discord.Embed(
        title="Common Bot Commands", color=discord.Color.green())
    embed.add_field(name="Policy ID", value="!policy $collection_name", inline=False)
    embed.add_field(name="Floor", value="!floor $collection_name", inline=False)
    embed.add_field(name="Supply", value="!supply $collection_name", inline=False)
    embed.add_field(name="Collection Info", value="!collection-info $collection_name", inline=False)
    embed.add_field(name="Token Value", value="!token $collection_name", inline=False)
    embed.add_field(name="Add Collection", value="!entry $collection_name $policy_id", inline=False)
    embed.add_field(name="Remove Collection", value="!remove $collection_name", inline=False)
    return embed


def floor(name):
    name = name.lower()
    policy_id = wallet.get_policy(name)
    response = requests.get("https://server.jpgstoreapis.com/collection/{0}/floor".format(policy_id))
    json_data = json.loads(response.text)
    embed = discord.Embed(
        title="Floor for collection", color=discord.Color.green())
    embed.add_field(name=name, value=int(json_data["floor"]) / 1000000, inline=False)
    return embed


def collection_info(name):
    name = name.lower()
    policy_id = wallet.get_policy(name)
    response = requests.get("https://publicapi.cnftpredator.tools/collection-info/{0}".format(policy_id))
    json_data = json.loads(response.text)
    collection_info = json_data["CollectionInfo"]
    embed = discord.Embed(
        title="Collection Info {0}".format(name), color=discord.Color.green())
    embed.add_field(name="Floor", value=collection_info["floor"], inline=False)
    embed.add_field(name="Holder", value=collection_info["holders"], inline=False)
    embed.add_field(name="Supply", value=collection_info["supply"], inline=False)
    embed.add_field(name="Volume", value=collection_info["volumeAllTime"], inline=False)
    return embed


def token(name):
    name = name.lower()
    url = "https://api.coingecko.com/api/v3/simple/price?ids={0}&vs_currencies=usd".format(name)
    response = requests.get(url)
    json_data = json.loads(response.text)
    embed = discord.Embed(
        title="Value", color=discord.Color.orange())
    embed.add_field(name=name, value=json_data[name]["usd"], inline=False)
    return embed


def supply(name):
    name = name.lower()
    policy_id = wallet.get_policy(name)
    response = requests.get("https://server.jpgstoreapis.com/collection/{0}/supply".format(policy_id))
    json_data = json.loads(response.text)
    embed = discord.Embed(
        title="Supply for collection", color=discord.Color.red())
    embed.add_field(name=name, value=json_data["supply"], inline=False)
    return embed


def policy(name):
    name = name.lower()
    policy_id = wallet.get_policy(name)
    embed = discord.Embed(
        title="Policy for collection", color=discord.Color.blue())
    embed.add_field(name=name, value=policy_id, inline=False)
    return embed


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    print("Hello World")
    print(message)
    if message.author == client.user:
        return

    msg = message.content
    print(msg)
    if msg.startswith("!update_db"):
        await message.channel.send(update_complete_database())

    elif msg.startswith("!entry"):
        message_list = msg.split(" ")
        if len(message_list) != 3:
            await message.channel.send("Message length should be 3")
        else:
            await message.channel.send(update_database(message_list[1].lower(), message_list[2].lower()))

    elif msg.startswith('!remove'):
        message_list = msg.split(" ")
        if len(message_list) != 2:
            await message.channel.send("Message length should be 2")
        else:
            await message.channel.send(remove_entry(message_list[1].lower()))

    elif msg.startswith("!wallet-info"):
        print("Wallet info getting collected...")
        message_list = msg.split(" ")
        try:
            if len(message_list) != 2:
                await message.channel.send("Please provide correct number of arguments!")
            else:
                await message.channel.send(embed=wallet_info(message_list[1]))
        except TypeError:
            await message.channel.send("Info Provided Not Correct!")
            raise

    elif msg.startswith("!policy"):
        try:
            message_list = msg.split(" ")
            print(message_list[1].lower())
            matching = wallet.get_matching_collections(message_list[1].lower())
            match = [s for s in matching]
            if len(message_list) != 2:
                await message.channel.send("Argument Size should be exactly 2")
            else:
                if len(match) > 0:
                    for collection in match:
                        await message.channel.send(embed=policy(collection["collection_name"].lower()))
                else:
                    await message.channel.send("Ask admin to register this collection!")
        except KeyError:
            await message.channel.send("Please provide correct key name")
            raise

    elif msg.startswith("!token"):
        message_list = msg.split(" ")
        if len(message_list) != 2:
            await message.channel.send("Argument Size should be exactly 2")
        else:
            try:
                await message.channel.send(embed=token(message_list[1].lower()))
            except KeyError:
                await message.channel.send("Please provide correct token name!")
                raise

    elif msg.startswith("!supply"):
        try:
            message_list = msg.split(" ")
            matching = wallet.get_matching_collections(message_list[1].lower())
            match = [s for s in matching]
            if len(message_list) != 2:
                await message.channel.send("Argument Size should be exactly 2")
            else:
                if len(match) > 0:
                    for collection in match:
                        await message.channel.send(embed=supply(collection["collection_name"].lower()))
                else:
                    await message.channel.send("Ask admin to register this collection!")
        except KeyError:
            await message.channel.send("Please provide correct key name")
            raise

    elif msg.startswith("!collection-info"):
        try:
            message_list = msg.split(" ")
            matching = wallet.get_matching_collections(message_list[1].lower())
            match = [s for s in matching]
            if len(message_list) != 2:
                await message.channel.send("Argument Size should be exactly 2")
            else:
                if len(match) > 0:
                    for collection in match:
                        await message.channel.send(embed=collection_info(collection["collection_name"].lower()))
                else:
                    await message.channel.send("Ask admin to register {0} collection!".format(message_list[1]))
        except KeyError:
            await message.channel.send("Please provide correct key name!")
            raise

    elif msg.startswith("!floor"):
        try:
            message_list = msg.split(" ")
            matching = wallet.get_matching_collections(message_list[1].lower())
            match = [s for s in matching]
            if len(message_list) != 2:
                await message.channel.send("Argument Size should be exactly 2")
            else:
                if len(match) > 0:
                    for collection in match:
                        await message.channel.send(embed=floor(collection["collection_name"].lower()))
                else:
                    await message.channel.send("Ask admin to register this collection!")
        except KeyError:
            await message.channel.send("Please provide correct key name")
            raise

    elif msg.startswith("!command"):
        await message.channel.send(embed=commands())

    elif msg.startswith("!rank"):
        await message.channel.send("Nice Rank Buddy!")

    elif msg.startswith("!"):
        await message.channel.send("Damn, you can't even write a command correct")


def main():
    my_secret = os.environ['WHALE_INFO_KEY']
    client.run(my_secret)


if __name__ == '__main__':
    main()
