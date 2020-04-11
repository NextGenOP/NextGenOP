#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)


import asyncio
from tobrot.helper_funcs.display_progress import humanbytes
import json
import os
import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)


async def extract_youtube_dl_formats(url, user_working_dir):
    command_to_exec = [
        "youtube-dl",
        "--no-warnings",
        "--youtube-skip-dash-manifest",
        "-j",
        url
    ]
    if "hotstar" in url:
        command_to_exec.append("--geo-bypass-country")
        command_to_exec.append("IN")
    LOGGER.info(command_to_exec)
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    LOGGER.info(e_response)
    t_response = stdout.decode().strip()
    LOGGER.info(t_response)
    # https://github.com/rg3/youtube-dl/issues/2630#issuecomment-38635239
    if e_response:
        # logger.warn("Status : FAIL", exc.returncode, exc.output)
        error_message = e_response.replace(
            "Tolong laporkan masalah ini di https://yt-dl.org/bug. Pastikan Anda menggunakan versi terbaru; lihat https://yt-dl.org/update tentang cara memperbarui. Pastikan untuk memanggil youtube-dl dengan flag --verbose dan sertakan output lengkapnya."
        )
        return error_message, None
    if t_response:
        # logger.info(t_response)
        x_reponse = t_response
        response_json = []
        if "\n" in x_reponse:
            for yu_r in x_reponse.split("\n"):
                response_json.append(json.loads(yu_r))
        else:
            response_json.append(json.loads(x_reponse))
        # response_json = json.loads(x_reponse)
        save_ytdl_json_path = user_working_dir + \
            "/" + str("ytdleech") + ".json"
        with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
            json.dump(response_json, outfile, ensure_ascii=False)
        # logger.info(response_json)
        inline_keyboard = []
        for current_r_json in response_json:
            duration = None
            if "duration" in current_r_json:
                duration = current_r_json["duration"]
            if "formats" in current_r_json:
                for formats in current_r_json["formats"]:
                    format_id = formats.get("format_id")
                    format_string = formats.get("format_note")
                    if format_string is None:
                        format_string = formats.get("format")
                    format_ext = formats.get("ext")
                    approx_file_size = ""
                    if "filesize" in formats:
                        approx_file_size = humanbytes(formats["filesize"])
                    dipslay_str_uon = " " + format_string + " (" + format_ext.upper() + ") " + approx_file_size + " "
                    cb_string_video = "{}|{}|{}".format(
                        "video", format_id, format_ext)
                    ikeyboard = []
                    if "drive.google.com" in url:
                        if format_id == "source":
                            ikeyboard = [
                                pyrogram.InlineKeyboardButton(
                                    dipslay_str_uon,
                                    callback_data=(cb_string_video).encode("UTF-8")
                                )
                            ]
                    else:
                        if format_string is not None and not "audio saja" in format_string:
                            ikeyboard = [
                                pyrogram.InlineKeyboardButton(
                                    dipslay_str_uon,
                                    callback_data=(cb_string_video).encode("UTF-8")
                                )
                            ]
                        else:
                            # special weird case :\
                            ikeyboard = [
                                pyrogram.InlineKeyboardButton(
                                    "SVideo [" +
                                    "] ( " +
                                    approx_file_size + " )",
                                    callback_data=(cb_string_video).encode("UTF-8")
                                )
                            ]
                    inline_keyboard.append(ikeyboard)
                if duration is not None:
                    cb_string_64 = "{}|{}|{}".format("audio", "64k", "mp3")
                    cb_string_128 = "{}|{}|{}".format("audio", "128k", "mp3")
                    cb_string = "{}|{}|{}".format("audio", "320k", "mp3")
                    inline_keyboard.append([
                        pyrogram.InlineKeyboardButton(
                            "MP3 " + "(" + "64 kbps" + ")", callback_data=cb_string_64.encode("UTF-8")),
                        pyrogram.InlineKeyboardButton(
                            "MP3 " + "(" + "128 kbps" + ")", callback_data=cb_string_128.encode("UTF-8"))
                    ])
                    inline_keyboard.append([
                        pyrogram.InlineKeyboardButton(
                            "MP3 " + "(" + "320 kbps" + ")", callback_data=cb_string.encode("UTF-8"))
                    ])
            else:
                format_id = current_r_json["format_id"]
                format_ext = current_r_json["ext"]
                cb_string_video = "{}|{}|{}".format(
                    "video", format_id, format_ext)
                inline_keyboard.append([
                    pyrogram.InlineKeyboardButton(
                        "SVideo",
                        callback_data=(cb_string_video).encode("UTF-8")
                    )
                ])
            break
        reply_markup = pyrogram.InlineKeyboardMarkup(inline_keyboard)
        # LOGGER.info(reply_markup)
        succss_mesg = """Pilih format yang diinginkan: 👇
<u>mention</u> <i>perkiraan ukuran file</i>"""
        return succss_mesg, reply_markup
