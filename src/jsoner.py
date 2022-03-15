import json
from pprint import pprint
import argparse


def add_channel(vk_id, tg_id, print_url, include_photo, include_video, json_file):
    with open(json_file, 'r+') as f:
        data = json.load(f)
        data['channel'][vk_id] = {
            "tg_id": tg_id,
            "last_post_id": "",
            "print_url": int(print_url),
            "include_photo": int(include_photo),
            "include_video": int(include_video)
        }
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()


def delete_channel(vk_id, json_file):
    with open(json_file, 'r+') as f:
        data = json.load(f)
        data['channel'].pop(vk_id)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('json_path')
    args = parser.parse_args()

    json_path = args.json_path
    command = input('command [add]/[del]/[open]: ')
    if command == 'add':
        vk_id = input('vk_id [-12345678]: ')
        tg_id = input('tg_id [@example] : ')
        print_url = input('print_url [1]/[0]: ')
        include_photo = input('include_photo [1/0]: ')
        include_video = input('include_video [1/0]: ')
        add_channel(vk_id, tg_id, print_url, include_photo, include_video, json_path)
    elif command == 'del':
        vk_id = input('vk_id [-12345678]: ')
        delete_channel(vk_id, json_path)
    elif command == 'open':
        pprint(open(json_path).read())
    else:
        print('Wrong command')
