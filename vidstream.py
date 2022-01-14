import os
import signal
import sys
import re
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pytgcalls import idle as pyidle
from pytgcalls import PyTgCalls
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityAudio
from pytgcalls.types.input_stream.quality import HighQualityVideo, MediumQualityVideo, LowQualityVideo
from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch
from time import time
from dotenv import load_dotenv
from datetime import datetime
import dotenv

# System Uptime
START_TIME = datetime.utcnow()
TIME_DURATION_UNITS = (
    ('Week', 60 * 60 * 24 * 7),
    ('Day', 60 * 60 * 24),
    ('Hour', 60 * 60),
    ('Min', 60),
    ('Sec', 1)
)
async def _human_time_duration(seconds):
    if seconds == 0:
        return 'inf'
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append('{} {}{}'
                         .format(amount, unit, "" if amount == 1 else "s"))
    return ', '.join(parts)

# VPS 
if os.path.exists(".env"):
    load_dotenv(".env")

# YTDL
# https://github.com/pytgcalls/pytgcalls/blob/dev/example/youtube_dl/youtube_dl_example.py
async def get_youtube_stream(ytlink):
        proc = await asyncio.create_subprocess_exec(
            'youtube-dl',
            '-g',
            '-f',
            # CHANGE THIS BASED ON WHAT YOU WANT
            'best[height<=?720][width<=?1280]',
            f'{ytlink}',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return stdout.decode().split('\n')[0]

# TimePass
async def bash(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout , stderr= await process.communicate()
    return stdout.decode()


# Client and PyTgCalls
API_ID = int(os.getenv("API_ID", "6"))
API_HASH = os.getenv("API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e")
SESSION = os.getenv("SESSION")
CHAT = int(os.getenv("CHAT", "6"))
HNDLR = os.getenv("HNDLR", "!")

bot = Client(SESSION, API_ID, API_HASH)
self_or_contact_filter = filters.create(
    lambda _, __, message:
    (message.from_user and message.from_user.is_contact) or message.outgoing
)
call_py = PyTgCalls(bot)
GROUP_CALL = []


@bot.on_message(self_or_contact_filter & filters.command("vstream", prefixes=f"{HNDLR}"))
async def stream(client, m: Message):
   if len(m.command) < 2:
      await m.reply("`Give A Link/LiveLink/.m3u8 URL/YTLink to Stream from 🎶`")
   else:
      if len(m.command)==2:
         link = m.text.split(None, 1)[1]
         q = HighQualityVideo()
         huehue = await m.reply("`Trying to Stream 💭`")
      elif len(m.command)==3:
         op = m.text.split(None, 1)[1]
         link = op.split(None, 1)[0]
         quality = op.split(None, 1)[1]
         if quality=="720":
            q = HighQualityVideo()
         elif quality=="480":
            q = MediumQualityVideo()
         elif quality=="360":
            q = LowQualityVideo()
         else:
            q = HighQualityVideo()
            await m.reply("`Use 360/480/720`")
         huehue = await m.reply("`Trying to Stream 💭`")
      else:
         await m.reply("`!vstream {link} {720/480/360}`")
      chat_id = m.chat.id

      # Filtering out YouTube URL's
      regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
      match = re.match(regex,link)
      if match:
         try:
            livelink = await get_youtube_stream(link)
         except Exception as e:
            await huehue.edit(f"**YTDL ERROR** \n{e}")
      else:
         livelink = link
      print(livelink)

      # Playing
      if chat_id in GROUP_CALL:
         try:
            await call_py.leave_group_call(chat_id)
            await asyncio.sleep(2)
            await call_py.join_group_call(
               chat_id,
               AudioVideoPiped(
                  livelink,
                  HighQualityAudio(),
                  q
               ),
               stream_type=StreamType().pulse_stream,
            )
            await huehue.delete()
            await m.reply(f"Started [Streaming]({livelink}) in `{chat_id}`", disable_web_page_preview=True)
         except Exception as ep:
            await m.reply(f"{ep}")
      else:
         try:
            await call_py.join_group_call(
               chat_id,
               AudioVideoPiped(
                  livelink,
                  HighQualityAudio(),
                  q
               ),
               stream_type=StreamType().pulse_stream,
            )
            GROUP_CALL.append(chat_id)
            await huehue.delete()
            await m.reply(f"Started [Streaming]({livelink}) in `{chat_id}`", disable_web_page_preview=True)
         except Exception as ep:
            await m.reply(f"{ep}")

@bot.on_message(self_or_contact_filter & filters.command("vplay", prefixes=f"{HNDLR}"))
async def play(client, m: Message):
   replied = m.reply_to_message
   chat_id = m.chat.id
   if replied:
      if replied.document or replied.video:
         huehue = await replied.reply("`Downloading 📩`")
         location = await replied.download()
         if len(m.command) < 2:
            q = HighQualityVideo()
         else:
            pq = m.text.split(None, 1)[1]
            if pq=="720":
               q = HighQualityVideo()
            elif pq=="480":
               q = MediumQualityVideo()
            elif pq=="360":
               q = LowQualityVideo()
            else:
               q = HighQualityVideo()
               await huehue.edit("`Only 720, 480, 360 Allowed` \n`Now Streaming in 720p`")
         if chat_id in GROUP_CALL:
            try:
               await call_py.leave_group_call(chat_id)
               await asyncio.sleep(2)
               await call_py.join_group_call(
                  chat_id,
                  AudioVideoPiped(
                     location,
                     HighQualityAudio(),
                     q
                  ),
                  stream_type=StreamType().local_stream,
               )
               await huehue.delete()
               await replied.reply(f"Started Playing in `{chat_id}`", disable_web_page_preview=True)
            except Exception as ep:
               await m.reply(f"{ep}")
         else:
            try:
               await call_py.join_group_call(
                  chat_id,
                  AudioVideoPiped(
                     location,
                     HighQualityAudio(),
                     q
                  ),
                  stream_type=StreamType().local_stream,
               )
               GROUP_CALL.append(chat_id)
               await huehue.delete()
               await replied.reply(f"Started Playing in `{chat_id}`", disable_web_page_preview=True)
            except Exception as ep:
               await m.reply(f"{ep}")
      else:
         if len(m.command) < 2:
            await replied.reply("`Either Reply to a VIDEO or Give me Query/YT Link to Play`")
         else:
            try:
               query = m.text.split(None, 1)[1]
               hmmop = await m.reply("`Searching 🔎`")
               search = VideosSearch(query, limit=1)
               for result in search.result()["result"]:
                  ytid = result['id']
                  url = f"https://www.youtube.com/watch?v={ytid}"
            except Exception as ey:
               print(ey)
               await m.reply("`Found Nothing :( Try searching something Else.`")
            ytlink = await get_youtube_stream(url)
            print(ytlink)
            # Playing
            if chat_id in GROUP_CALL:
               try:
                  await call_py.leave_group_call(chat_id)
                  await asyncio.sleep(2)
                  await call_py.join_group_call(
                     chat_id,
                     AudioVideoPiped(
                        ytlink,
                        HighQualityAudio(),
                        MediumQualityVideo()
                     ),
                     stream_type=StreamType().pulse_stream,
                  )
                  await hmmop.delete()
                  await m.reply(f"Started [Streaming]({ytlink}) in `{chat_id}`", disable_web_page_preview=True)
               except Exception as ep:
                  await m.reply(f"{ep}")
            else:
               try:
                  await call_py.join_group_call(
                     chat_id,
                     AudioVideoPiped(
                        ytlink,
                        HighQualityAudio(),
                        MediumQualityVideo()
                     ),
                     stream_type=StreamType().pulse_stream,
                  )
                  GROUP_CALL.append(chat_id)
                  await hmmop.delete()
                  await m.reply(f"Started [Streaming]({livelink}) in `{chat_id}`", disable_web_page_preview=True)
               except Exception as ep:
                  await m.reply(f"{ep}")
   
   else:
         if len(m.command) < 2:
            await replied.reply("`Either Reply to a VIDEO or Give me Query/YT Link to Play`")
         else:
            try:
               query = m.text.split(None, 1)[1]
               hmmop = await m.reply("`Searching 🔎`")
               search = VideosSearch(query, limit=1)
               for result in search.result()["result"]:
                  ytid = result['id']
                  url = f"https://www.youtube.com/watch?v={ytid}"
            except Exception as ey:
               print(ey)
               await m.reply("`Found Nothing :( Try searching something Else.`")
            ytlink = await get_youtube_stream(url)
            print(ytlink)
            # Playing
            if chat_id in GROUP_CALL:
               try:
                  await call_py.leave_group_call(chat_id)
                  await asyncio.sleep(2)
                  await call_py.join_group_call(
                     chat_id,
                     AudioVideoPiped(
                        ytlink,
                        HighQualityAudio(),
                        MediumQualityVideo()
                     ),
                     stream_type=StreamType().pulse_stream,
                  )
                  await hmmop.delete()
                  await m.reply(f"Started [Streaming]({ytlink}) in `{chat_id}`", disable_web_page_preview=True)
               except Exception as ep:
                  await m.reply(f"{ep}")
            else:
               try:
                  await call_py.join_group_call(
                     chat_id,
                     AudioVideoPiped(
                        ytlink,
                        HighQualityAudio(),
                        MediumQualityVideo()
                     ),
                     stream_type=StreamType().pulse_stream,
                  )
                  GROUP_CALL.append(chat_id)
                  await hmmop.delete()
                  await m.reply(f"Started [Streaming]({ytlink}) in `{chat_id}`", disable_web_page_preview=True)
               except Exception as ep:
                  await m.reply(f"{ep}")

@bot.on_message(self_or_contact_filter & filters.command("pause", prefixes=f"{HNDLR}"))
async def pause(client, m: Message):
   chat_id = m.chat.id
   await call_py.pause_stream(chat_id)
   await m.reply("`Paused Streaming ⏸️`")

@bot.on_message(self_or_contact_filter & filters.command("resume", prefixes=f"{HNDLR}"))
async def resume(client, m: Message):
   chat_id = m.chat.id
   await call_py.resume_stream(chat_id)
   await m.reply("`Resumed Streaming ▶`") 

@bot.on_message(self_or_contact_filter & filters.command("vstop", prefixes=f"{HNDLR}"))
async def stop(client, m: Message):
   try:
      chat_id = m.chat.id
      if chat_id in GROUP_CALL:
         GROUP_CALL.remove(chat_id)
      else:
         pass
      await call_py.leave_group_call(chat_id)
      await m.reply("`Stopped Streaming ⏹️`")
   except Exception as e:
      print(e)

@bot.on_message(self_or_contact_filter & filters.command("ping", prefixes=f"{HNDLR}"))
async def ping(client, m: Message):
   start = time()
   current_time = datetime.utcnow()
   m_reply = await m.reply_text("`...`")
   delta_ping = time() - start
   uptime_sec = (current_time - START_TIME).total_seconds()
   uptime = await _human_time_duration(int(uptime_sec))
   await m_reply.edit(f"`Pong 🏓!` `{delta_ping * 1000:.3f} ms` \n**Uptime 🔰** - `{uptime}`")

@bot.on_message(self_or_contact_filter & filters.command("killall", prefixes=f"{HNDLR}"))
async def kill(client, m: Message):   
   os.system("pkill ffmpeg")
   try:
      os.system("rm -rf downloads")
   except Exception as e:
      print(e)
   for x in GROUP_CALL:
      await call_py.leave_group_call(x)
      GROUP_CALL.remove(x)
   await m.reply("`Cleaned all the Temporary Files 🗑️ and Stopped All Processes and Left all Voice Chats`")

@bot.on_message(self_or_contact_filter & filters.command("help", prefixes=f"{HNDLR}"))
async def help(client, m: Message):
   await m.reply(f"**🔰DEVELOPER🔰 ↗ [©LEGEND-ANKIT™](https://github.com/LEGEND-ANKIT)** \n\n**🛠 HELP MENU** \n\n`{HNDLR}ping` \n`{HNDLR}vplay query` \n`{HNDLR}vstream link` \n`{HNDLR}vstop` \n`{HNDLR}pause` \n`{HNDLR}resume` \n`{HNDLR}update` \n`{HNDLR}restart`")

@bot.on_message(self_or_contact_filter & filters.command("update", prefixes=f"{HNDLR}"))
async def update(client, m: Message):
   hmm = await bash("git pull -f")
   await m.reply(f"`{hmm}`")
   os.execl(sys.executable, "python3", "-m", "vidstream.py")

@bot.on_message(self_or_contact_filter & filters.command("restart", prefixes=f"{HNDLR}"))
async def restart(client, m: Message):
   umm = await m.reply_text("`Restarting ⚙️...`")
   try:
      asyncio.get_event_loop().create_task(os.kill(os.getpid(), signal.SIGUSR1))
   except Exception as e:
      await umm.edit(f"**An Error Occurred :-** \n`{e}`")



bot.start()
call_py.start()
pyidle()
idle()
