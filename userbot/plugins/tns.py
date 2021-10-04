from userbot.utils import admin_cmd


@bot.on(admin_cmd(incoming=True))
async def _(event):
    if not event.is_private and event.chat_id == -1001592228587:
        pluto = await event.client.forward_messages(-1001445526942, event.message)
        await event.client.pin_message(-1001445526942, pluto)
