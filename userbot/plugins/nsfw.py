# By @kirito6969 for PepeBot
# Don't edit credits Madafaka
"""
This module can search images in danbooru and send in to the chat!
──「 **Danbooru Search** 」──
"""

import asyncio
import html
import os
import urllib
from urllib.parse import quote as urlencode

import aiohttp
import bs4
import requests
from bs4 import BeautifulSoup
from pySmartDL import SmartDL
from telethon.errors.rpcerrorlist import WebpageCurlFailedError, YouBlockedUserError
from urlextract import URLExtract

from userbot import catub

from ..helpers.functions import age_verification
from ..helpers.utils import _catutils
from . import edit_delete, edit_or_reply, reply_id

session = aiohttp.ClientSession()
plugin_category = "fun"


@catub.cat_cmd(
    pattern="ani(mu|nsfw) ?(.*)",
    command=("ani", plugin_category),
    info={
        "header": "Contains NSFW 🔞.\nTo search images in danbooru!",
        "usage": [
            "{tr}animu <query>",
            "{tr}aninsfw <nsfw query>",
        ],
        "examples": [
            "{tr}animu naruto",
            "{tr}aninsfw boku no pico",
        ],
    },
)
async def danbooru(message):
    "Get anime charecter pic or nsfw"
    reply_to = await reply_id(message)
    if await age_verification(message, reply_to):
        return
    await edit_or_reply(message, "`Processing…`")
    rating = "Explicit" if "nsfw" in message.pattern_match.group(1) else "Safe"
    search_query = message.pattern_match.group(2)
    params = {
        "limit": 1,
        "random": "true",
        "tags": f"Rating:{rating} {search_query}".strip(),
    }

    with requests.get(
        "http://danbooru.donmai.us/posts.json", params=params
    ) as response:
        if response.status_code == 200:
            response = response.json()
        else:
            await edit_delete(
                message,
                f"`An error occurred, response code:` **{response.status_code}**",
                4,
            )
            return

    if not response:
        await edit_delete(message, f"`No results for query:` __{search_query}__", 4)
        return

    valid_urls = [
        response[0][url]
        for url in ["file_url", "large_file_url", "source"]
        if url in response[0].keys()
    ]

    if not valid_urls:
        await edit_delete(
            message, f"`Failed to find URLs for query:` __{search_query}__", 4
        )
        return
    for image_url in valid_urls:
        try:
            await message.client.send_file(
                message.chat_id, image_url, reply_to=reply_to
            )
            await message.delete()
            return
        except Exception as e:
            await edit_or_reply(message, f"{e}")
    await edit_delete(
        message, f"``Failed to fetch media for query:` __{search_query}__", 4
    )


@catub.cat_cmd(
    pattern="boobs(?: |$)(.*)",
    command=("boobs", plugin_category),
    info={
        "header": "NSFW 🔞\nYou know what it is, so do I !",
        "usage": "{tr}boobs",
        "examples": "{tr}boobs",
    },
)
async def boobs(e):
    "Search boobs"
    reply_to = await reply_id(e)
    if await age_verification(e, reply_to):
        return
    a = await edit_or_reply(e, "`Sending boobs...`")
    nsfw = requests.get("http://api.oboobs.ru/noise/1").json()[0]["preview"]
    urllib.request.urlretrieve(f"http://media.oboobs.ru/{nsfw}", "*.jpg")
    os.rename("*.jpg", "boobs.jpg")
    await e.client.send_file(e.chat_id, "boobs.jpg", reply_to=reply_to)
    os.remove("boobs.jpg")
    await a.delete()


@catub.cat_cmd(
    pattern="butts(?: |$)(.*)",
    command=("butts", plugin_category),
    info={
        "header": "NSFW 🔞\nBoys and some girls are like to Spank this 🍑",
        "usage": "{tr}butts",
        "examples": "{tr}butts",
    },
)
async def butts(e):
    "Search beautiful butts"
    reply_to = await reply_id(e)
    if await age_verification(e, reply_to):
        return
    a = await edit_or_reply(e, "`Sending beautiful butts...`")
    nsfw = requests.get("http://api.obutts.ru/butts/10/1/random").json()[0]["preview"]
    urllib.request.urlretrieve(f"http://media.obutts.ru/{nsfw}", "*.jpg")
    os.rename("*.jpg", "butts.jpg")
    await e.client.send_file(e.chat_id, "butts.jpg", reply_to=reply_to)
    os.remove("butts.jpg")
    await a.delete()


PENIS_TEMPLATE = """
🍆🍆
🍆🍆🍆
  🍆🍆🍆
    🍆🍆🍆
     🍆🍆🍆
       🍆🍆🍆
        🍆🍆🍆
         🍆🍆🍆
          🍆🍆🍆
          🍆🍆🍆
      🍆🍆🍆🍆
 🍆🍆🍆🍆🍆🍆
 🍆🍆🍆  🍆🍆🍆
    🍆🍆       🍆🍆
"""


@catub.cat_cmd(
    pattern=r"(?:penis|dick)\s?(.)?",
    command=("dick", plugin_category),
    info={
        "header": "NSFW 🔞\nThis is Something EPIC that horny girls wanna see for sure ! 🌚",
        "usage": "{tr}dick",
        "examples": "{tr}dick",
    },
)
async def emoji_penis(e):
    emoji = e.pattern_match.group(1)
    o = await edit_or_reply(e, "`Dickifying...`")
    message = PENIS_TEMPLATE
    if emoji:
        message = message.replace("🍆", emoji)
    await o.edit(message)


@catub.cat_cmd(
    pattern="(loli|nloli|sloli) ?(.*)?",
    command=("loli", plugin_category),
    info={
        "header": "Contains NSFW 🔞.\nTo search Loli images. Thanks to lolicon API!",
        "description": "If you are not a Loli person then Fuck You!\nI am not responsible for anything if FBI catches u :)",
        "usage": [
            "{tr}loli - Gets a mixed loli image",
            "{tr}sloli - Gets a SFW only image",
            "{tr}nloli - Gets a NSFW only image",
        ],
    },
)
async def loli(event):
    match = event.pattern_match.group(1)
    word = event.pattern_match.group(2)
    reply_to = await reply_id(event)
    if await age_verification(event, reply_to):
        return
    if mode := match:
        mode = 0 if mode.startswith("s") else 1
    else:
        mode = 2
    async with session.get(
        f"https://api.lolicon.app/setu/v2?num=1&r18={mode}&keyword={urlencode(word)}"
    ) as resp:
        data = await resp.json()
    if not data["data"][0]:
        return await edit_delete(
            event, "***Unknown Error occured while fetching data***", 3
        )
    data = data["data"][0]
    pic = data["urls"]["original"]
    title = f'{data["title"]} by {data["author"]}'
    adult = f'{data["r18"]}'
    caption = f'<a href="https://pixiv.net/artworks/{data["pid"]}">{html.escape(data["title"])}</a> by <a href="https://pixiv.net/users/{data["uid"]}">{html.escape(data["author"])}</a>\n'
    tags = f'{html.escape(", ".join(data["tags"]))}' if data["tags"] else None
    lol = f"<b>{caption}</b>\n<b>✘ Title:</b> <i>{title}</i>\n<b>✘ Adult:</b> <i>{adult}</i>\n<b>✘ Tags:</b> <i>{tags}</i>"
    await event.delete()
    await event.client.send_file(
        event.chat_id, file=pic, caption=lol, parse_mode="html"
    )


# Created by @Jisan7509
# All rights reserved.
@catub.cat_cmd(
    pattern="xlist(?:\s|$)([\s\S]*)",
    command=("xlist", plugin_category),
    info={
        "header": "Get a list of porn videos from xvideo",
        "usage": [
            "{tr}xlist",
            "{tr}xlist <search> <count> ",
            "{tr}xlist <search> ; <count> ; <page no>",
        ],
        "examples": [
            "{tr}xlist",
            "{tr}xlist stepsis ; 10",
            "{tr}xlist stepsis ; 10 ; 3",
        ],
    },
)
async def cat(event):
    """Send a list of xvideos posts"""
    reply_to = await reply_id(event)
    intxt = event.pattern_match.group(1)
    page = 0
    xcount = None
    if intxt and ";" in intxt:
        try:
            xtext, xcount, page = intxt.split(";")
        except ValueError:
            xtext, xcount = intxt.split(";")
    elif intxt:
        xtext = intxt
    else:
        xtext = "stepsis"
    if await age_verification(event, reply_to):
        return
    page = requests.get(f"https://www.xvideos.com/?k={xtext}&p={int(page)}")
    soup = BeautifulSoup(page.text, "lxml")
    col = soup.findAll("div", {"class": "thumb"})
    if not col:
        return await edit_delete(
            event, "`No links found for that query , try differnt search...`", 60
        )
    await edit_or_reply(event, "**Just hold a min you horny kid...**")
    listlink = []
    listname = []
    for i in col:
        a = i.find("a")
        tmplink = a.get("href")
        links = f"https://www.xvideos.com{tmplink}"
        listlink.append(links)
        name = tmplink.split("/")[2]
        listname.append(name)
    await edit_or_reply(
        event,
        f"**{len(listlink)} results found for {xtext} :\nSending {xcount} results out of them.**",
    )
    string = f"<b>Showing {xcount}/{len(listlink)} results for {xtext}.</b>\n\n"
    mylink = listlink[: int(xcount)] if xcount else listlink
    for count, (l, n) in enumerate(zip(mylink, listname), start=1):
        req = requests.get(l)
        soup = BeautifulSoup(req.text, "lxml")
        soups = soup.find("div", {"id": "video-player-bg"})
        for a in soups.find_all("a", href=True):
            link = a["href"]
        string += (
            f"<b><i>{count}. <a href = {link}>{n.replace('_',' ').title()}</a></b>\n"
        )
    await edit_or_reply(event, string, parse_mode="html")


@catub.cat_cmd(
    pattern="linkdl(?: |$)([\s\S]*)",
    command=("linkdl", plugin_category),
    info={
        "header": "download porn video or gif in bulk or single from xvideos, imgur or redgif or direct link.\n\nFor multiple link give one space between links or reply to to any link contain text, like listporn or xlist post",
        "usage": "{tr}linkdl <input link /reply to link>",
        "examples": "{tr}linkdl https://redgifs.com/watch/virtuousgorgeousindianspinyloach https://i.imgur.com/3Ffkon9.gifv",
    },
)
async def wants_ur_noods(event):  # sourcery no-metrics
    """Download ~~porns~~ *posts from link"""
    reply_to = await reply_id(event)
    intxt = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    if not intxt and reply:
        intxt = reply.text
    if not intxt:
        return await edit_delete(
            event,
            "**ಠ∀ಠ  Reply to valid link or give valid link url as input...you moron!!**",
        )
    extractor = URLExtract()
    plink = extractor.find_urls(intxt)
    await edit_or_reply(event, "** Just hold a sec u horny kid...**")
    if await age_verification(event, reply_to):
        return
    i = 0
    for m in plink:
        if not m.startswith("https://"):
            return await edit_delete(
                event, "**(ノಠ益ಠ)ノ Give me a vaid link to download**"
            )
        if "xvideo" in m:
            if ".mp4" not in m:
                req = requests.get(m)
                soup = BeautifulSoup(req.text, "lxml")
                soups = soup.find("div", {"id": "video-player-bg"})
                for a in soups.find_all("a", href=True):
                    m = a["href"]
            await edit_or_reply(
                event,
                "**Just hold your candel & sit tight, It will take some time...**",
            )

            if not os.path.isdir("./xvdo"):
                os.mkdir("./xvdo")
            xvdo = SmartDL(m, "./xvdo/porn.mp4", progress_bar=False)
            xvdo.start(blocking=False)
            xvdo.wait("finished")
            media_url = "./xvdo/porn.mp4"
        elif "https://i.imgur.com" in m and m.endswith(".gifv"):
            media_url = m.replace(".gifv", ".mp4")
        elif "https://redgifs.com/watch" in m:
            try:
                source = requests.get(m)
                soup = BeautifulSoup(source.text, "lxml")
                links = [
                    itm["content"] for itm in soup.findAll("meta", property="og:video")
                ]
                try:
                    media_url = links[1]
                except IndexError:
                    media_url = links[0]
            except IndexError:
                media_url = m
        else:
            media_url = m
        try:
            sandy = await event.client.send_file(
                event.chat_id, media_url, reply_to=reply_to
            )
            if media_url.endswith((".mp4", ".gif")):
                await _catutils.unsavegif(event, sandy)
            if os.path.exists(media_url):
                os.remove(media_url)
            await edit_or_reply(
                event, f"**Download Started.\n\nFile Downloaded :  {i+1}/{len(plink)}**"
            )
            await asyncio.sleep(2)
        except WebpageCurlFailedError:
            await event.client.send_message(
                event.chat_id, f"**Value error!!..Link is :** {m}"
            )
        i += 1
        if i == len(plink):
            await event.delete()
            if os.path.isdir("./xvdo"):
                os.rmdir("./xvdo")


@catub.cat_cmd(
    pattern="xvdo ?(.*)",
    command=("xvdo", plugin_category),
    info={
        "header": "Generate direct download link from xvideos",
        "usage": "{tr}xvdo <xvideos link>",
    },
)
async def xvid(message):
    reply_to = await reply_id(message)
    if await age_verification(message, reply_to):
        return
    editer = await edit_or_reply(message, "`Please Wait.....`")
    msg = message.pattern_match.group(1)
    if not msg:
        await edit_delete(message, "`Enter xvideos url bish`")
        return
    try:
        req = requests.get(msg)
        soup = bs4.BeautifulSoup(req.content, "html.parser")

        soups = soup.find("div", {"id": "video-player-bg"})
        link = ""
        for a in soups.find_all("a", href=True):
            link = a["href"]
        await editer.edit(f"**HERE IS YOUR LINK 🌚**\n\n`{link}`")
    except Exception:
        await edit_delete(message, "**Something went wrong**")


@catub.cat_cmd(
    pattern="xsearch ?(.*)",
    command=("xsearch", plugin_category),
    info={
        "header": "Xvideo Searcher",
        "description": "Search sax videos from xvideos",
        "usage": "{tr}xsearch <search query>",
        "examples": "{tr}xsearch pure taboo",
    },
)
async def xvidsearch(message):
    await edit_or_reply(message, "`Please Wait.....`")
    reply_to = await reply_id(message)
    if await age_verification(message, reply_to):
        return
    msg = message.pattern_match.group(1)
    if not msg:
        await edit_delete(message, "`BTC! What i am supposed to search`")
        return
    try:
        qu = msg.replace(" ", "+")
        page = requests.get(f"https://www.xvideos.com/?k={qu}").content
        soup = bs4.BeautifulSoup(page, "html.parser")
        col = soup.findAll("div", {"class": "thumb"})

        links = ""

        for i in col:
            a = i.find("a")
            link = a.get("href")

            semd = link.split("/")[2]

            links += f"<a href='https://www.xvideos.com{link}'>• {semd.upper()}</a>\n"
        await edit_or_reply(
            message,
            f"<b>Search Query:</b> <code>{msg}</code>\n\n" + links,
            parse_mode="HTML",
            link_preview=False,
        )

    except Exception:
        await edit_delete(message, "**Something Went Wrong**")


# By @P_4_PEEYUSH
# Heavily Modified and fixed By @kirito6969 for pepecat


@catub.cat_cmd(
    pattern="xxshort",
    command=("xxshort", plugin_category),
    info={
        "header": "NSFW",
        "description": "Try Yourself!",
        "usage": "{tr}xxshort",
    },
)
async def _(event):
    if event.fwd_from:
        return
    reply_to_id = await reply_id(event)
    chat = -1001578788009
    k = await edit_or_reply(event, "`Checking...`")
    async with event.client.conversation(chat) as conv:
        try:
            await conv.send_message("🤪")
            response = await conv.get_response()
            await event.client.send_message(
                event.chat_id, response, reply_to=reply_to_id
            )
            await k.delete()
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await edit_delete(event, "```Unblock @OpGufaBot```")
            return


@catub.cat_cmd(
    pattern="xxlong",
    command=("xxlong", plugin_category),
    info={
        "header": "NSFW",
        "description": "Try Yourself!",
        "usage": "{tr}xxlong",
    },
)
async def _(event):
    if event.fwd_from:
        return
    reply_to_id = await reply_id(event)
    await event.get_reply_message()
    chat = -1001578788009
    k = await edit_or_reply(event, "`Checking...`")
    async with event.client.conversation(chat) as conv:
        try:
            await conv.send_message("😏")
            response = await conv.get_response()
            await event.client.send_message(
                event.chat_id, response, reply_to=reply_to_id
            )
            await k.delete()
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await edit_delete(event, "```Unblock @OpGufaBot```")
            return


@catub.cat_cmd(
    pattern="xpic",
    command=("xpic", plugin_category),
    info={
        "header": "NSFW",
        "description": "Try Yourself!",
        "usage": "{tr}xpic",
    },
)
async def _(event):
    if event.fwd_from:
        return
    reply_to_id = await reply_id(event)
    await event.get_reply_message()
    chat = -1001578788009
    k = await edit_or_reply(event, "```Checking...```")
    async with event.client.conversation(chat) as conv:
        try:
            await conv.send_message("💋")
            response = await conv.get_response()
            await event.client.send_message(
                event.chat_id, response, reply_to=reply_to_id
            )
            await k.delete()
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await edit_delete(event, "```Unblock @OpGufaBot```")
            return


@catub.cat_cmd(
    pattern="xnxx",
    command=("xnxx", plugin_category),
    info={
        "header": "NSFW",
        "description": "Try Yourself!",
        "usage": "{tr}xnxx",
    },
)
async def _(event):
    if event.fwd_from:
        return
    reply_to_id = await reply_id(event)
    chat = -1001578788009
    k = await edit_or_reply(event, "```Checking...```")
    async with event.client.conversation(chat) as conv:
        try:
            await conv.send_message("💋2016 Videolar🔞")
            response = await conv.get_response()
            await event.client.send_message(
                event.chat_id, response, reply_to=reply_to_id
            )
            await k.delete()
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await edit_delete(event, "```Unblock @SeXn1bot```")
            return


@catub.cat_cmd(
    pattern="picx",
    command=("picx", plugin_category),
    info={
        "header": "NSFW",
        "description": "Try Yourself!",
        "usage": "{tr}picx",
    },
)
async def _(event):
    if event.fwd_from:
        return
    reply_to_id = await reply_id(event)
    chat = -1001578788009
    k = await edit_or_reply(event, "```Checking...```")
    async with event.client.conversation(chat) as conv:
        try:
            await conv.send_message("♨️Old photo👙")
            response = await conv.get_response()
            await event.client.send_message(
                event.chat_id, response, reply_to=reply_to_id
            )
            await k.delete()
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await edit_delete(event, "```Unblock @SeXn1bot```")
            return


@catub.cat_cmd(
    pattern="les",
    command=("les", plugin_category),
    info={
        "header": "NSFW",
        "description": "Try Yourself!",
        "usage": "{tr}les",
    },
)
async def _(event):
    if event.fwd_from:
        return
    reply_to_id = await reply_id(event)
    chat = -1001578788009
    k = await edit_or_reply(event, "```Checking...```")
    async with event.client.conversation(chat) as conv:
        try:
            await conv.send_message("🔞Uz_sex♨️")
            response = await conv.get_response()
            await event.client.send_message(
                event.chat_id, response, reply_to=reply_to_id
            )
            await k.delete()
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await edit_delete(event, "```Unblock @SeXn1bot```")
            return


@catub.cat_cmd(
    pattern="lis",
    command=("lis", plugin_category),
    info={
        "header": "NSFW",
        "description": "Try Yourself!",
        "usage": "{tr}lis",
    },
)
async def _(event):
    if event.fwd_from:
        return
    reply_to_id = await reply_id(event)
    chat = -1001578788009
    k = await edit_or_reply(event, "```Checking...```")
    async with event.client.conversation(chat) as conv:
        try:
            await conv.send_message("🔞SeX_Vido🚷")
            response = await conv.get_response()
            await event.client.send_message(
                event.chat_id, response, reply_to=reply_to_id
            )
            await k.delete()
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await edit_delete(event, "```Unblock @SeXn1bot```")
            return
