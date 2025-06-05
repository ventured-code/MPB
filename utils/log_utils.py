from utils.file_utils import load_log_config

log_channels = load_log_config()

async def log_action(guild, content):
    channel_id = log_channels.get(str(guild.id))
    if not channel_id:
        return
    channel = guild.get_channel(channel_id)
    if channel:
        await channel.send(content)
