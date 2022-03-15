from time import sleep
import json
import sys
from channel import Channel
from src.utils import time
from src.config import *
import vk
from telegram import Bot

poster_bot = Bot(token=tg_poster_bot_key)
sleep_time = 90
timeout = 25


def send2supervisor(text, bot):
    try:
        bot.send_message(chat_id=supervisor_id, text=text, timeout=timeout)
    except Exception as sending_ex:
        print('SENDING ERROR:', sending_ex)


def update_channels(json_path, vk_api):
    channels = []
    with open(json_path, 'r') as JSON:
        json_dict = json.load(JSON)
    for channel_id in json_dict['channel']:
        channel = json_dict['channel'][channel_id]
        new_channel = Channel(vk_id=channel_id, tg_id=channel['tg_id'],
                                  last_post_id=channel['last_post_id'],
                                  print_url=channel['print_url'],
                                  bot=poster_bot, vk_api=vk_api,
                                  timeout=timeout,
                                  include_photo=channel['include_photo'],
                                  include_video=channel['include_video'])
        channels.append(new_channel)
    return channels


def run_channels(channels, json_path):
    for channel in channels:
        result = channel.run(json_path)
        if not result['ok']:
            send2supervisor(text=str(result), bot=poster_bot)


def run_mirror(json_path, vk_api):
    updated_channels = update_channels(json_path, vk_api)
    run_channels(updated_channels, json_path)


def get_vk_api(key_idx):
    key_idx = key_idx % len(vk_app_keys)
    session = vk.Session(access_token=vk_app_keys[key_idx])
    return vk.API(session)


if __name__ == "__main__":
    key_index = 0
    vk_api = get_vk_api(key_index)
    json_filepath = sys.argv[1] if len(sys.argv) > 1 else 'channel.json'
    print('Starting at ' + time())
    while True:
        try:
            run_mirror(json_path=json_filepath, vk_api=vk_api)
            sleep(sleep_time)
        except vk.exceptions.VkAPIError as many_requests:
            print('VK_EXCEPTION', many_requests)
            key_index += 1
            print('NEW KEY INDEX:', key_index % len(vk_app_keys))
            sleep(2)
            send2supervisor(text='NEW KEY INDEX: ' + str(key_index), bot=poster_bot)
            vk_api = get_vk_api(key_index)
        except Exception as ex:
            print('GENERAL ERROR:', str(ex))
            send2supervisor(text=str(ex), bot=poster_bot)
            sleep(sleep_time)
