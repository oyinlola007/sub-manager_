import sqlite3, asyncio, os, time, requests, json, sys
import discord

import cogs.config as config
import cogs.strings as strings
import cogs.db as db
import cogs.smtp_mail_sender as mail_sender
import cogs.getSubscriptions as fetcher

db.initializeDB()

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

loop = 1


@client.event
async def on_member_join(member):
    try:
        embed=discord.Embed(description=strings.SUB_MESSAGE)
        await member.send(embed=embed)
    except:
        pass


@client.event
async def on_ready():
    print(strings.LOGGED_IN.format(client.user))


@client.event
async def on_message(message):
    if message.content.lower().startswith('!link') and str(message.channel.type) == 'private':
        try:
            mail = message.content.split()[1]
            try:
                db.get_customer_id(mail)
                cursor = db.get_customer(mail)
                for row in cursor:
                    if row[2] != "":
                        await message.channel.send(strings.ACCOUNT_ALREADY_LINKED)
                    else:
                        db.update_discord_id(str(message.author.id), str(message.author.name), mail)
                        await message.channel.send(strings.ACCOUNT_SUCCESSFULLY_LINKED)
                    break
            except:
                await message.channel.send(strings.EMAIL_ABSENT)
        except:
            await message.channel.send(strings.WRONG_FORMAT)

    elif message.content.lower() == '!portal' and str(message.channel.type) == 'private':
        try:
            customer_id = db.get_customer_id_from_discord_id(str(message.author.id))
            try:
                r = requests.post(config.PORTAL_LINK.format(customer_id, message.channel.id), headers=config.HEADERS)
                data = json.loads(r.text)
                await message.author.send(strings.PORTAL_MESSAGE.format(data["url"]))
            except Exception as e:
                await message.author.send(strings.PORTAL_ERROR.format(e))
        except:
            await message.author.send(strings.CUSTOMER_NOT_FOUND)

    elif message.content.lower().startswith('!admin_link') and message.author.id in config.ADMINS:
        try:
            mail = message.content.split()[1]
            id_ = message.content.split()[2]

            guild = discord.utils.get(client.guilds, id=config.GUILD_ID)

            try:
                member = await guild.fetch_member(int(id_))
                discord_id = member.id
                try:
                    db.get_customer_id(mail)
                    get = db.get_customer(mail)
                    for row in get:
                        if row[2] != "":
                            await message.channel.send(strings.ACCOUNT_ALREADY_LINKED)
                        else:
                            db.update_email(str(message.author.id), mail)
                            await message.channel.send(strings.ACCOUNT_SUCCESSFULLY_LINKED)
                        break
                except:
                    await message.channel.send(strings.EMAIL_ABSENT)
            except:
                await message.channel.send(strings.ID_NOT_FOUND)
        except:
            await message.channel.send(strings.WRONG_FORMAT_ADMIN)

    elif message.content.lower().startswith('!delete') and message.author.id in config.ADMINS:
        try:
            mail = message.content.split()[1]
            db.delete_customer(mail)
            await message.channel.send(strings.USER_DELETED)

        except:
            await message.channel.send(strings.EMAIL_ABSENT)


    elif message.content.lower().startswith('!unlink'):
        try:
            guild = discord.utils.get(client.guilds, id=config.GUILD_ID)
            mail = message.content.split()[1]
            if db.get_customer_status(mail) != "0":
                discord_id = db.get_customer_discord_id(mail)
                if len(discord_id)  > 1:
                    for role in ["Flo Pro", "Lite"]:
                        try:
                            member = await guild.fetch_member(int(discord_id))
                            role = discord.utils.get(guild.roles, name=role)
                            await member.remove_roles(role)
                        except:
                            pass
            db.update_discord_id("", "", mail)
            await message.channel.send(strings.USER_UNLINKED)
        except:
            await message.channel.send(strings.EMAIL_ABSENT)

    elif message.content.lower() == '!resync':
        try:
            guild = discord.utils.get(client.guilds, id=config.GUILD_ID)
            discord_id = str(message.author.id)

            customer_ids = db.get_customers_from_discord_id(discord_id)

            for row in customer_ids:
                customer_id = row[0]

                data = db.get_subscription_by_customer_id(customer_id)
                for row in data:
                    sub_id = row[0]
                    customer_id = row[1]
                    end = int(row[2])
                    product_name = row[4]
                    activation_status = row[6].strip()


                    if "xxx Pro Membership" in product_name:
                        role = "Flo Pro"
                    elif "xxx Lite" in product_name:
                        role = "Lite"

                    else:
                        continue

                    cursor = db.select_customers(customer_id)

                    email = ""

                    for row in cursor:
                        email = row[1]
                        discord_id = row[2]
                        status = row[4]

                    if email == "":
                        continue

                    #if time.time() < end and status != "1" and discord_id != "" and activation_status == "active":
                    if discord_id != "" and activation_status == "active":
                        member = await guild.fetch_member(int(discord_id))
                        role = discord.utils.get(guild.roles, name=role)
                        await member.add_roles(role)
                        await member.send(strings.SUB_ACTIVATED)

                        admin = await guild.fetch_member(int(config.ADMINS[1]))
                        await admin.send(f"```gave {member.name} role```")

                        db.update_customer_status(customer_id, "1")
        except:
            pass



    elif message.content.lower().startswith('!help '):
        content = message.content.replace("!help ", "")
        channel = client.get_channel(config.HELP_CHANNEL)
        embed = discord.Embed(color=0xFF0000, description=f"**{content}**")
        embed.set_author(name=message.author.name, url=f"https://discordapp.com/users/{message.author.id}", icon_url=message.author.avatar_url)
        await channel.send(embed=embed)
        await message.channel.send(strings.REQUEST_SENT)

    try:
        if message.content == "!get_db":
            await message.channel.send(file=discord.File(config.DATABASE_NAME))
    except:
        pass


async def user_metrics_background_task():
    await client.wait_until_ready()
    global loop

    while True:
        guild = discord.utils.get(client.guilds, id=config.GUILD_ID)

        if int(time.time()) % 30 == 0:
            if loop == 1:
                loop = 2
                try:
                    fetcher.get_products()
                except Exception as e:
                    member = await guild.fetch_member(int(config.ADMINS[1]))
                    await member.send(f"```error fetching products {e}```")
            elif loop == 2:
                loop = 3
                try:
                    fetcher.get_customers()
                except Exception as e:
                    member = await guild.fetch_member(int(config.ADMINS[1]))
                    await member.send(f"```error fetching customers {e}```")
            elif loop == 3:
                loop = 1
                try:
                    fetcher.get_subscriptions()
                except Exception as e:
                    member = await guild.fetch_member(int(config.ADMINS[1]))
                    await member.send(f"```error fetching subs {e}```")


        data = db.get_all_subs()
        for row in data:
            try:
                sub_id = row[0]
                customer_id = row[1]
                end = int(row[2])
                product_name = row[4]
                activation_status = row[6].strip()


                if "xxx Pro Membership" in product_name:
                    role = "Flo Pro"
                elif "xxx Lite" in product_name:
                    role = "Lite"

                else:
                    continue

                cursor = db.select_customers(customer_id)

                email = ""

                for row in cursor:
                    email = row[1]
                    discord_id = row[2]
                    status = row[4]

                if email == "":
                    continue

                if db.get_email_count(email) == 0:
                    try:
                        mail_sender.send_mail(email)
                        member = await guild.fetch_member(int(config.ADMINS[1]))
                        await member.send(f"```{email}```")

                        #await member.send(file=discord.File(config.DATABASE_NAME))

                    except Exception as e:
                        member = await guild.fetch_member(int(config.ADMINS[1]))
                        await member.send(f"```{e}```")

                    db.insert_email(email)
                    db.update_status(sub_id, "sent mail")

                #if time.time() < end and status != "1" and discord_id != "" and activation_status == "active":
                if status != "1" and discord_id != "" and activation_status == "active":
                    member = await guild.fetch_member(int(discord_id))
                    role = discord.utils.get(guild.roles, name=role)
                    await member.add_roles(role)
                    await member.send(strings.SUB_ACTIVATED)

                    admin = await guild.fetch_member(int(config.ADMINS[1]))
                    await admin.send(f"```gave {member.name} role```")

                    db.update_customer_status(customer_id, "1")

                #if (time.time() > end + 86400 or activation_status != "active") and status == "1" and discord_id != "" :
                if (activation_status != "active" or time.time() > end + 86400 * 3) and status == "1" and discord_id != "" :
                    member = await guild.fetch_member(int(discord_id))
                    role = discord.utils.get(guild.roles, name=role)
                    await member.remove_roles(role)
                    await member.send(strings.SUB_EXPIRED)
                    db.update_customer_status(customer_id, "0")

                    admin = await guild.fetch_member(int(config.ADMINS[1]))
                    await admin.send(f"```removed {member.name} role```")

                    #delete subscription when sub expired
                    db.delete_subscription(customer_id)
            except:
                pass


        await asyncio.sleep(1)


client.loop.create_task(user_metrics_background_task())
client.run(config.DISCORD_TOKEN)

