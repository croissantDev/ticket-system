__author__ = "Felix & Olly (he did one thing)"

import asyncio
import csv
import json
import math
import os
import random
import re
import uuid
import time
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher

import aiohttp
import core
import discord
from discord.ext import commands

BYPASS_LIST = [
    767824073186869279,
    249568050951487499,
    323473569008975872,
    381170131721781248,
    329991150712651776,
    307297123869655050,
    346382745817055242,
    211368856839520257,
    1221249361745543168,
    335415340190269440,
    697444795785674783,
]

ROLE_HIERARCHY = [
    "1248340570275971125",
    "1248340594686820403",
    "1333526096683073546",
    "1248340609727729795",
    "1248340626773381240",
    "1248340641117765683",
]

THUMBNAIL = (
    "https://cdn.discordapp.com/attachments/1208495821868245012/1291896171555455027/CleanShot_2024-10-04_"
    "at_23.53.582x.png?ex=6701c391&is=67007211&hm=1138ae2d92387ecde7be34af238bd756462970de2ca6ca559c6aa091f9"
    "32a8ae&"
)
FOOTER = "City Airways Support"

gamepasses = {
    "Rainbow Name": 20855496,
    "Ground Crew": 20976711,
    "Cabin Crew": 20976738,
    "Captain": 20976820,
    "Senior Staff": 20976845,
    "Staff Manager": 20976883,
    "Airport Manager": 20976943,
    "Board of Directors": 21002253,
    "Co Owner": 21002275,
    "First Class": 21006608,
    "Segway Board": 22042259,
}

colours = {
    "green": 0xA9DC76,
    "red": 0xFF6188,
    "yellow": 0xFFD866,
    "light_blue": 0x78DCE8,
    "purple": 0xAB9DF2,
}

channel_options = {
    "Main": "1221162035513917480",
    "Prize Claims": "1213885924581048380",
    "Affiliate": "1196076391242944693",
    "Development": "1196076499137200149",
    "Appeals": "1196076578938036255",
    "Moderator Reports": "1246863733355970612",
}

UNITS = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days", "w": "weeks"}

MOTIVATIONAL_QUOTES = [
    "To toil unyielding is to defy the heavens and earn thy rightful glory.",
    "The weak are but shadows, while the strong etch their names upon stone.",
    "He who fears the wrath of kings shall forever dwell in servitude.",
    "Deny not thy ambitions; for he who grovels shall inherit naught but dust.",
    "Only the bold dare sip from the cup of destiny.",
    "Mercy is oft a veil for cowardice; strike while the iron is hot.",
    "In the forge of adversity, only the resolute are deemed worthy.",
    "The gods aid those who carve their own path with blade and wit.",
    "Hesitation is the dirge of the unworthy; act, or be forgotten.",
    "A throne is never granted; it is seized by the audacious.",
    "The stars weep not for those who falter; rise, or perish in obscurity.",
    "Lo, the meek may inherit the earth, but the strong claim the heavens.",
    "Idleness is the herald of decay; only the industrious shall thrive.",
    "Pity not the fallen; they are but stepping stones for the ambitious.",
    "A man's worth is measured by the foes he dares to challenge.",
    "The silence of the oppressed is the triumph of tyranny; speak, or be chained.",
    "In the arena of life, the lion devours the lamb; be no lamb.",
    "The fates weave for the daring, not for the docile.",
    "To conquer is not cruel; it is the order of the strong over the weak.",
    "Dreams unpursued are but whispers in the wind, meaningless and fleeting.",
    "Shatter thy chains, or be content to rot in servitude.",
    "Gold favors the cunning, not the pious or the hesitant.",
    "A kingdom's glory is built upon the ashes of the defeated.",
    "Suffer not the mediocrity of others to chain thy spirit.",
    "The edge of a sword speaks louder than a hundred pleas.",
    "Seek not the approval of others, for it is a prison for the ambitious.",
    "The path to greatness is paved with the bones of thy failures.",
    "Turn not thy cheek to insults; forbearance breeds contempt.",
    "To reign is to wield power; to follow is to endure obscurity.",
    "The wise sow discord among their rivals to reap unity for themselves.",
    "Your time is limited, so don't waste it living someone else's life",
    "Success is not the final destination; failure is not the end. It is the courage to continue that counts.",
]

BLOXLINK_API_KEY = os.environ.get("BLOXLINK_KEY")
SERVER_ID = "788228600079843338"
HEADERS = {"Authorization": BLOXLINK_API_KEY}

EMOJI_VALUES = {True: "✅", False: "⛔"}
K_VALUE = 0.099

def format_timedelta_verbose(td: timedelta) -> str:
    days = td.days
    total_seconds = td.seconds
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    if not parts:
        return "0 seconds"

    if len(parts) == 1:
        return parts[0]
    return " ".join(parts[:-1]) + " and " + parts[-1]


def format_appeal_result(username, reviewer, result):
    formatted_message = f"{':white_check_mark:' if result else ':negative_squared_cross_mark:'} | **APPEAL PROCESSED**\n\n"
    formatted_message += "> Hello. Your ban appeal has been processed, and here is your result:\n\n"

    formatted_message += f"- Username: {username}\n"
    formatted_message += f"- Reviewed by: {reviewer}\n"
    formatted_message += f"- Result: {'Passed' if result else 'Failed'}\n"
    if result is False:
        formatted_message += "- Notes: You can try to appeal again in 2 weeks (14 days).\n\n\n"

    theother = f"```\n{formatted_message.strip()}\n```"

    return [formatted_message, theother]


async def rank_users_by_tickets_this_month_to_csv(ctx):
    filename = f"monthly_ranking_{uuid.uuid4()}.csv"
    results = []

    print("CSV Generation requested, starting conversion for ROBLOX Usernames")

    time = unix_converter(2.546 * len(results))

    msg = await ctx.reply(f"Started generation, estimated completion: <t:{time}:R>")

    rm = []

    for j, i in enumerate(results):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"https://api.blox.link/v4/public/guilds/788228600079843338/discord-to-roblox/{i[0]}",
                    headers=HEADERS,
            ) as res:
                await asyncio.sleep(1)
                roblox_data = await res.json()
                if "error" in roblox_data:
                    if roblox_data["error"] == "Unknown Member":
                        await ctx.channel.send(
                            f"Discord ID: {i[0]} not in discord, <@{i[0]}> will not be included in pay, but if you need his ticket amount it is: `{i[1]}`"
                        )
                        print(f"{i[0]} NOT IN DISCORD, NOT INCLUDED IN CSV")
                        rm.append(j)
                        continue
                try:
                    roblox_name = roblox_data["resolved"]["roblox"]["name"]
                except Exception as e:
                    await ctx.channel.send(
                        f"Discord ID: {i[0]} giving me an error, <@{i[0]}> will not be included in pay, but if you need his ticket amount it is: `{i[1]}`"
                    )
                    print(f"{i[0]} NOT IN DISCORD, NOT INCLUDED IN CSV")
                    rm.append(j)
                    continue
                i[0] = roblox_name

    rm_set = set(rm)
    results = [item for idx, item in enumerate(results) if idx not in rm_set]

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ROBLOX Username", "Ticket Count", "Rank"])
        for row in results:
            writer.writerow(row)
    await msg.delete()

    return filename


def handle_cooldown_result(future, ctx):
    cooldown = future.result()
    if cooldown is not None:
        return commands.Cooldown(1, cooldown)
    return None


def new_cooldown(ctx):
    if ctx.author.id in BYPASS_LIST:
        return None
    
    return None


def unix_converter(seconds: int) -> int:
    now = datetime.now()
    then = now + timedelta(seconds=seconds)

    return int(then.timestamp())


def convert_to_seconds(text: str) -> int:
    return int(
        timedelta(
            **{
                UNITS.get(m.group("unit").lower(), "seconds"): float(m.group("val"))
                for m in re.finditer(
                    r"(?P<val>\d+(\.\d+)?)(?P<unit>[smhdw]?)",
                    text.replace(" ", ""),
                    flags=re.I,
                )
            }
        ).total_seconds()
    )


class DropDownChannels(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=i[0]) for i in channel_options.items()]

        super().__init__(
            placeholder="Select a channel...",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction):
        category_id = channel_options[self.values[0]]
        category = interaction.guild.get_channel(int(category_id))

        await interaction.channel.edit(category=category, sync_permissions=True)

        await interaction.response.edit_message(
            content="Moved channel successfully.", view=None
        )


class DropDownView(discord.ui.View):
    def __init__(self, dropdown):
        super().__init__()
        self.add_item(dropdown)


def find_most_similar(name):
    return max(
        gamepasses.items(), key=lambda x: SequenceMatcher(None, x[0], name).ratio()
    )


def EmbedMaker(ctx, **kwargs):
    if "colour" not in kwargs:
        color = 0x8E00FF
    else:
        color = colours[kwargs["colour"].lower()]
        del kwargs["colour"]
    e = discord.Embed(**kwargs, colour=color)
    e.set_footer(
        text="City Airways",
        icon_url="https://cdn.discordapp.com/icons/788228600079843338/21fb48653b571db2d1801e29c6b2eb1d.png?size=4096",
    )
    return e


def is_bypass():
    async def predicate(ctx):
        return (
                ctx.author.id in BYPASS_LIST
        )

    return commands.check(predicate)


async def check(ctx):
    if (
            ctx.author.id in BYPASS_LIST
    ):
        return True

    coll = ctx.bot.plugin_db.get_partition(ctx.bot.get_cog("GuidesCommittee"))
    thread = await coll.find_one({"thread_id": str(ctx.thread.channel.id)})
    if thread is not None:
        can_r = ctx.author.bot or str(ctx.author.id) == thread["claimer"]
        if not can_r:
            if "⛔" not in [
                i.emoji for i in ctx.message.reactions
            ]:
                await ctx.message.add_reaction("⛔")
        return can_r
    if "⛔" not in [
        i.emoji for i in ctx.message.reactions
    ]:
        await ctx.message.add_reaction("⛔")
    return False


class GuidesCommittee(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.api.get_plugin_partition(self)
        self.bot.get_command("reply").add_check(check)
        self.bot.get_command("areply").add_check(check)
        self.bot.get_command("fareply").add_check(check)
        self.bot.get_command("freply").add_check(check)
        self.bot.get_command("close").add_check(check)
        self.db_generated = False

        self.bot.frozen = []

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = EmbedMaker(
                ctx,
                title="On Cooldown",
                description=f"You can use this command again <t:{unix_converter(error.retry_after)}:R>",
                colour="red",
            )

            await ctx.send(embed=embed)
        else:
            if isinstance(error, (commands.BadArgument, commands.BadUnionArgument)):
                await ctx.typing()
                await ctx.send(
                    embed=discord.Embed(
                        color=ctx.bot.error_color, description=str(error)
                    )
                )
            elif isinstance(error, commands.CommandNotFound):
                print("CommandNotFound: %s", error)
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send_help(ctx.command)
            elif isinstance(error, commands.CheckFailure):
                for check in ctx.command.checks:
                    if not await check(ctx):
                        if hasattr(check, "fail_msg"):
                            await ctx.send(
                                embed=discord.Embed(
                                    color=ctx.bot.error_color,
                                    description=check.fail_msg,
                                )
                            )
                        if hasattr(check, "permission_level"):
                            corrected_permission_level = ctx.bot.command_perm(
                                ctx.command.qualified_name
                            )
                            print(
                                "User %s does not have permission to use this command: `%s` (%s).",
                                ctx.author.name,
                                ctx.command.qualified_name,
                                corrected_permission_level.name,
                            )
                print("CheckFailure: %s", error)
            elif isinstance(error, commands.DisabledCommand):
                print(
                    "DisabledCommand: %s is trying to run eval but it's disabled",
                    ctx.author.name,
                )
            elif isinstance(error, commands.CommandInvokeError):
                await ctx.send(
                    embed=discord.Embed(
                        color=ctx.bot.error_color,
                        description=f"{str(error)}\nYou might be getting this error during **getinfo** if the user is either\n1. Not in the `main` server\n2. Has no linked account in bloxlink",
                    )
                )
            else:
                await ctx.channel.send(f"{error}, {type(error)}")
                print("Unexpected exception:", error)

            try:
                await ctx.message.clear_reactions()
                await ctx.message.add_reaction("⛔")
            except Exception:
                pass

    @commands.command()
    async def initdb(self, ctx):
        await ctx.reply("Database functionality has been removed.")

    @core.checks.thread_only()
    @core.checks.has_permissions(core.models.PermissionLevel.SUPPORTER)
    @commands.dynamic_cooldown(new_cooldown, type=commands.BucketType.user)
    @commands.command()
    async def claim(self, ctx, bypass: str = None):
        time = ctx.channel.created_at
        time = time.replace(tzinfo=timezone.utc)

        time_now = datetime.now(timezone.utc)

        diff = (time_now - time).total_seconds() * 1000

        timing = random.randint(1000, 1500)

        if diff < timing:
            return await ctx.channel.send("Too fast, please try again")

        if (1 == 5) and (bypass != "bypass"): # Simplified logic since database is removed
            embed = EmbedMaker(
                ctx,
                title="You have done 5 tickets today",
                description=f"You've done 5 tickets today! Doing more will cause management to be notified. However if you wish to claim it run `.claim bypass`",
                colour="red",
            )
            return await ctx.send(embed=embed)


        if (2 >= 6) and (ctx.author.id not in BYPASS_LIST): # Simplified logic
            embed = EmbedMaker(
                ctx,
                title="You have done at least 6 tickets today",
                description=f"You've done at least 6 tickets today! Doing more is not allowed. However, if you wish to claim it then please ask a management member to manually bypass your cooldown",
                colour="red",
            )
            return await ctx.send(embed=embed)

        thread = await self.db.find_one({"thread_id": str(ctx.thread.channel.id)})
        if thread is None:
            await self.db.insert_one(
                {
                    "thread_id": str(ctx.thread.channel.id),
                    "claimer": str(ctx.author.id),
                    "original_name": ctx.channel.name,
                }
            )

            try:
                nickname = ctx.author.display_name
                await ctx.channel.edit(
                    name=f"claimed-{nickname}"
                )

                embed = EmbedMaker(
                    ctx,
                    title="Claimed",
                    description=f"Claimed by {ctx.author.mention}",
                    colour="green",
                )
                await ctx.message.channel.send(embed=embed)

            except discord.errors.Forbidden:
                await ctx.message.reply("I don't have permission to do that, duh.")
        else:
            claimer = thread["claimer"]
            embed = EmbedMaker(
                ctx,
                title="Already Claimed",
                description=f"Already claimed by {(f'<@{claimer}>') if claimer != ctx.author.id else 'you, dumbass'}",
                colour="red",
            )
            await ctx.send(embed=embed)

    @commands.command()
    async def tickets(self, ctx, user: discord.Member, days: int):
        return await ctx.reply("Ticket counting functionality has been removed.")

    @core.checks.thread_only()
    @core.checks.has_permissions(core.models.PermissionLevel.SUPPORTER)
    @commands.command()
    async def unclaim(self, ctx):
        thread = await self.db.find_one({"thread_id": str(ctx.thread.channel.id)})
        if thread is None:
            embed = EmbedMaker(
                ctx,
                title="Already Unclaimed",
                description="This thread is not claimed, you can claim it!",
            )
            return await ctx.message.reply(embed=embed)

        if thread["claimer"] == str(ctx.author.id):
            await self.db.find_one_and_delete({"thread_id": str(ctx.thread.channel.id)})

            try:
                embed = EmbedMaker(
                    ctx,
                    title="Unclaimed",
                    description=f"Unclaimed by {ctx.author.mention}",
                    colour="green",
                )

                await ctx.channel.edit(name=thread["original_name"])

                await ctx.message.reply(embed=embed)

            except discord.errors.Forbidden:
                await ctx.message.reply("I don't have permission to do that")
        else:
            e = discord.Embed(
                title="Unclaim Denied",
                description=f"You're not the claimer of this thread, don't anger chairwoman abbi",
            )
            await ctx.message.reply(embed=e)

    @core.checks.has_permissions(core.models.PermissionLevel.MODERATOR)
    @commands.command()
    async def export(self, ctx):
        await ctx.reply("Export functionality has been removed.")

    @core.checks.thread_only()
    @core.checks.has_permissions(core.models.PermissionLevel.SUPPORTER)
    @commands.command()
    async def takeover(self, ctx):

        if ctx.channel.id in self.bot.frozen:
            return await ctx.channel.send("Channel is frozen")

        roles_taker = [str(i.id) for i in ctx.author.roles]
        roles_to_take_t = []
        for i in range(len(roles_taker)):
            if roles_taker[i] not in ROLE_HIERARCHY:
                roles_to_take_t.append(roles_taker[i])

        for i in roles_to_take_t:
            roles_taker.remove(i)

        thread = await self.db.find_one({"thread_id": str(ctx.thread.channel.id)})

        if thread["claimer"] == str(ctx.author.id):
            embed = EmbedMaker(
                ctx,
                title="Takeover Denied",
                description=f"You have literally claimed this yourself tf u doing",
                colour="red",
            )
            await ctx.channel.send(embed=embed)
            return

        mem = ctx.guild.get_member(thread["claimer"])

        if mem is None:
            mem = await ctx.guild.fetch_member(thread["claimer"])

        roles_claimed = [str(i.id) for i in mem.roles]

        roles_to_take_c = []
        for i in range(len(roles_claimed)):
            if roles_claimed[i] not in ROLE_HIERARCHY:
                roles_to_take_c.append(roles_claimed[i])

        for i in roles_to_take_c:
            roles_claimed.remove(i)

        if (
                ROLE_HIERARCHY.index(roles_taker[-1])
                < ROLE_HIERARCHY.index(roles_claimed[-1])
        ) or (ctx.author.id in BYPASS_LIST):
            await self.db.find_one_and_update(
                {"thread_id": str(ctx.thread.channel.id)},
                {"$set": {"claimer": str(ctx.author.id)}},
            )
            e = EmbedMaker(
                ctx,
                title="Taken over succesfully",
                description=f"Takeover by <@{ctx.author.id}> successful, they now own the ticket. Channel name change can take up to 5 minutes",
            )
            await ctx.channel.send(embed=e)
            try:
                nickname = ctx.author.display_name
                await ctx.channel.edit(name=f"claimed-{nickname}")
            except discord.errors.Forbidden:
                await ctx.message.reply("I couldn't change the channel name sorry")
        else:
            e = EmbedMaker(
                ctx,
                title="Takeover Denied",
                description=f"Takeover denied since the claimer is your superior or the same rank as you, if you need to takeover and this is not letting you, ask management for a manual transfer.",
            )
            await ctx.reply(embed=e)

    async def cog_load(self):
        self.db_generated = False

    async def cog_unload(self):
        cmds = [
            self.bot.get_command("reply"),
            self.bot.get_command("freply"),
            self.bot.get_command("areply"),
            self.bot.get_command("fareply"),
            self.bot.get_command("close"),
        ]
        for i in cmds:
            if check in i.checks:
                print(f"REMOVING CHECK IN {i.name}")
                i.remove_check(check)

        # Removed self.bot.sync_db.close() and self.bot.pool.terminate()
        # as the database connections are no longer being established.

    @commands.command()
    @is_bypass()
    async def freeze(self, ctx: commands.Context):
        if ctx.channel.id not in self.bot.frozen:
            self.bot.frozen.append(ctx.channel.id)

        await ctx.channel.send(
            "This channel is frozen now, `takeover` is **disabled**, `transfer` is **enabled**."
        )

    @commands.command()
    @core.checks.has_permissions(core.models.PermissionLevel.SUPPORTER)
    async def owns(self, ctx, username, *, gamepass):
        conversion_gamepass = False
        conversion_username = False

        try:
            gamepass = int(gamepass)
        except Exception:
            gamepass = gamepass
            conversion_gamepass = True

        try:
            username_id = int(username)
        except Exception:
            username = username
            conversion_username = True

        async with aiohttp.ClientSession() as session:
            if conversion_username is True:
                async with session.post(
                        "https://users.roblox.com/v1/usernames/users",
                        data=json.dumps(
                            {"usernames": [username], "excludeBannedUsers": True}
                        ),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if bool(data["data"]) is False:
                            e = EmbedMaker(
                                ctx,
                                title="Wrong username",
                                description="Please try putting the right **ROBLOX** username",
                            )
                            return await ctx.message.reply(embed=e)
                        if data["data"][0]["requestedUsername"] != username:
                            e = EmbedMaker(
                                ctx,
                                title="Failed checks",
                                description="Error Checking, please try again",
                            )
                            return await ctx.message.reply(embed=e)
                        print(data["data"][0]["id"])
                        username_id = data["data"][0]["id"]

            if conversion_gamepass is True:
                gamepass_id = find_most_similar(gamepass)

            async with session.get(
                    f"https://inventory.roblox.com/v1/users/{username_id}/items/1/{gamepass_id[1]}/is-owned"
            ) as resp:
                if resp.status == 200:
                    owns = await resp.json()

                    if not isinstance(owns, bool):
                        if "errors" in owns.keys():
                            owns = False

                    if owns is True:
                        e = EmbedMaker(
                            ctx,
                            title=f"{EMOJI_VALUES[True]} Ownership Verified",
                            description=f"{gamepass_id[0]} owned by {username}, [link](https://inventory.roblox.com/v1/users/{username_id}/items/1/{gamepass_id[1]}/is-owned)",
                        )
                        return await ctx.message.reply(embed=e)
                    else:
                        e = EmbedMaker(
                            ctx,
                            title=f"{EMOJI_VALUES[False]} Gamepass NOT Owned",
                            description=f"{gamepass_id[0]} **NOT** owned by {username}, [link](https://inventory.roblox.com/v1/users/{username_id}/items/1/{gamepass_id[1]}/is-owned)",
                        )
                        return await ctx.message.reply(embed=e)

    @commands.command()
    @core.checks.thread_only()
    async def getinfo(self, ctx, member: discord.Member = None):
        await ctx.message.add_reaction("<a:loading_f:1249799401958936576>")

        if member is None:
            m_id = ctx.thread.recipient.id
        else:
            m_id = member.id
        gamepasses_owned = {key: "IDK" for key in gamepasses.keys()}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                        f"https://api.blox.link/v4/public/guilds/788228600079843338/discord-to-roblox/{m_id}",
                        headers=HEADERS,
                ) as res:
                    roblox_data = await res.json()
                    roblox_id = roblox_data["robloxID"]

                    # await ctx.channel.send(roblox_data)

                    avatar_url_get = roblox_data["resolved"]["roblox"]["avatar"][
                        "bustThumbnail"
                    ]
            except Exception as e:
                raise e
            async with session.get(avatar_url_get) as res:
                avatar_url_ = await res.json()
                avatar_url = avatar_url_["data"][0]["imageUrl"]

            for i in gamepasses_owned.keys():
                id = gamepasses[i]

                async with session.get(
                        f"https://inventory.roblox.com/v1/users/{roblox_id}/items/1/{id}/is-owned"
                ) as res:
                    owns = await res.json()

                    if not isinstance(owns, bool):
                        if "errors" in owns.keys():
                            owns = False

                    if owns is True:
                        gamepasses_owned[i] = True
                    else:
                        gamepasses_owned[i] = False

        # Past Usernames
        past_usernames = []
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"https://users.roblox.com/v1/users/{roblox_data['robloxID']}/username-history"
            ) as r:
                response = await r.json()

                if "errors" in response.keys():
                    raise KeyError

                past_usernames = [i["name"] for i in response["data"]]

        roblox_name = roblox_data["resolved"]["roblox"]["name"]
        roblox_display_name = roblox_data["resolved"]["roblox"]["displayName"]
        roblox_profile_link = roblox_data["resolved"]["roblox"]["profileLink"]
        roblox_rank_name = roblox_data["resolved"]["roblox"]["groupsv2"]["8619634"][
            "role"
        ]["name"]
        roblox_rank_id = roblox_data["resolved"]["roblox"]["groupsv2"]["8619634"][
            "role"
        ]["rank"]

        embed = discord.Embed(
            title=roblox_name,
            url=roblox_profile_link,
            colour=0x8E00FF,
            timestamp=datetime.now(),
        )

        msg = ""
        for i, j in gamepasses_owned.items():
            msg += f"**{i}**: {EMOJI_VALUES[j]}\n"

        msg.strip()

        embed.add_field(
            name="Discord",
            value=f"**ID**: {m_id}\n**Username**: {ctx.thread.recipient.name}\n**Display Name**: {ctx.thread.recipient.display_name}",
            inline=False,
        )
        embed.add_field(
            name="ROBLOX",
            value=f"**ID**: {roblox_id}\n**Username**: {roblox_name}\n**Display Name**: {roblox_display_name}\n**Rank In Group**: {roblox_rank_name} ({roblox_rank_id})",
            inline=False,
        )

        embed.add_field(
            name="ROBLOX PAST USERNAMES",
            value="None" if len(past_usernames) == 0 else "\n".join(past_usernames),
            inline=False,
        )
        embed.add_field(name="Gamepasses", value=msg, inline=False)

        embed.set_thumbnail(url=avatar_url)

        embed.set_footer(
            text=FOOTER,
            icon_url="https://cdn.discordapp.com/attachments/1208495821868245012/1249743898075463863/Logo.png?ex=66686a34&is=666718b4&hm=f13b57e1fbd96c14bc8123d0a57980791e0f0db267da9ae39911fe50211406e1&",
        )

        await ctx.message.clear_reactions()

        await ctx.reply(embed=embed)

    @commands.command()
    @core.checks.thread_only()
    @core.checks.has_permissions(core.models.PermissionLevel.SUPPORTER)
    async def mover(self, ctx):
        view = DropDownView(DropDownChannels())

        await ctx.send("Choose a channel to move this ticket to", view=view)

    @commands.command()
    @core.checks.thread_only()
    @core.checks.has_permissions(core.models.PermissionLevel.SUPPORTER)
    async def remindme(self, ctx, time: str, *, message: str):
        embed = EmbedMaker(
            ctx,
            title="Remind Me",
            description=f"I will remind you about {message} in {time}",
        )
        m = await ctx.message.reply(embed=embed)

        await asyncio.sleep(convert_to_seconds(time))

        await ctx.channel.send(f"<@{ctx.author.id}>, {message}")

        try:
            await m.delete()
            await ctx.author.send(message)
        except discord.errors.Forbidden:
            pass

    @commands.command()
    @core.checks.thread_only()
    @is_bypass()
    async def transfer(self, ctx, user: discord.Member):
        thread = await self.db.find_one({"thread_id": str(ctx.thread.channel.id)})

        if thread["claimer"] == str(user.id):
            embed = EmbedMaker(
                ctx,
                title="Transfer Denied",
                description=f"<@{user.id}> is the thread claimer",
            )
            await ctx.channel.send(embed=embed)
            return

        await self.db.find_one_and_update(
            {"thread_id": str(ctx.thread.channel.id)},
            {"$set": {"claimer": str(user.id)}},
        )
        e = EmbedMaker(
            ctx,
            title="Transfer",
            description=f"Transfer by <@{user.id}> successful, this ticket is now theirs.",
        )
        await ctx.channel.send(embed=e)
        try:
            nickname = user.display_name

            await ctx.channel.edit(name=f"claimed-{nickname}")

            m = await ctx.message.channel.send(
                f"Successfully renamed."
            )

            await asyncio.sleep(10)

            await m.delete()
        except Exception as e:
            return await ctx.message.channel.send(str(e))

    @commands.Cog.listener()
    async def on_thread_close(
            self, thread, closer, silent, delete_channel, message, scheduled
    ):
        if self.db_generated is False:
            pool = await create_database()
            self.bot.pool = pool
            self.db_generated = True

        channel = closer.dm_channel

        if (str(thread.channel.category_id) == channel_options['Affiliate'] or str(thread.channel.category_id) == channel_options['Prize Claims']):
            timetaken_createtime = thread.channel.created_at
            timetaken_unix = datetime.now(timezone.utc)
            timetaken_actualtime = (timetaken_unix - timetaken_createtime)

            timetaken_string = format_timedelta_verbose(timetaken_actualtime)
            timetaken_logchannel_id = 1362147678200529159

            timetaken_channel = await self.bot.fetch_channel(timetaken_logchannel_id)

            await timetaken_channel.send(f"<@{closer.id}> has closed a ticket within {timetaken_string}.")

        if channel is None:
            channel = await closer.create_dm()

        if thread.recipient.id == closer.id:
            try:
                return await channel.send(
                    "You closed your own ticket, it will not count towards your ticket count. A copy of this message is sent to management."
                )
            except discord.errors.Forbidden:
                return

        await add_tickets(self.bot.pool, closer.id)

        week = await count_user_tickets_this_week(self.bot.pool, closer.id)
        month = await count_user_tickets_this_month(self.bot.pool, closer.id)
        day = await count_user_tickets_today(self.bot.pool, closer.id)

        cooldown = await get_cooldown_time(self.bot.pool, closer.id, True)

        random_number = random.randint(0, 10)

        try:
            await channel.send(
                f"Congratulations on closing your ticket {closer}. This is your ticket number `{day}` today, your ticket"
                f" number `{week}` this week and your ticket number `{month}` this month. Your cooldown "
                f"is: `{cooldown:.1f}` seconds"
            )
            if str(closer.id) == "1208702357425102880":  ## you can do this
                await channel.send(
                    "Hi Ben, this is a special message I have in store for when you close a ticket. I just want to "
                    "extend my heartfelt congratulations, because this job you do is impressive."
                )  # you just messed up indentaton

            if str(closer.id) == "767824073186869279":
                await channel.send(
                    "Great work on the ticket Chairwoman Abbi!"
                )  # for the chairwoman

            if day == 8:
                await channel.send(
                    "⚠ **TICKET 8 WARNING** ⚠\nClosing your 9th ticket will send a message to management where "  # had to add spaces its been bugging me for months = olly
                    "warnings/strikes/demotions might take place, if you have tickets currently claimed **UNCLAIM THEM**"
                )

            if day > 8:
                channelo = await self.bot.fetch_channel(1311111724379672608)
                await channelo.send(
                    f"⚠**MORE THAN 8 WARNING**⚠\n<@{closer.id}> closed more than 8 tickets in a day. This is their ticket number `{day}` today"
                    # neutral pronoun changed to - olly ffs the gc is so progressive be better
                )

            if random_number <= 3:
                quote = random.choice(MOTIVATIONAL_QUOTES)

                embed = discord.Embed(
                    color=colours["light_blue"],
                    description=quote,
                    title="Motivational Quote",
                )

                await channel.send(embed=embed)
        except discord.errors.Forbidden:
            pass

    @commands.command()
    @is_bypass()
    async def hi(self, ctx):
        await ctx.channel.send("Hello there!")  # general kenobi

    @commands.command()
    @core.checks.thread_only()
    async def appealmessage(self, ctx, accept: bool):
        user = ctx.thread.recipient

        # NEED GLOBAL API
        # async with aiohttp.ClientSession() as session:
        #     async with session.get(
        #             f"https://api.blox.link/v4/public/guilds/788228600079843338/discord-to-roblox/{user.id}",
        #             headers=HEADERS,
        #     ) as res:
        #         roblox_data = await res.json()
        #         roblox_id = roblox_data["robloxID"]
        #
        # roblox_name = roblox_data["resolved"]["roblox"]["name"]

        reviewer = ctx.author.display_name

        formatted = f"{user.name} ({user.id})"

        msg = format_appeal_result(formatted, reviewer, accept)

        await ctx.reply(msg[0])
        await ctx.reply(msg[1])


async def wait_for(
        ctx: discord.ext.commands.Context, time: int, embed: discord.Embed
) -> None:
    await asyncio.sleep(time)
    await ctx.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(GuidesCommittee(bot))