import json
from pprint import pprint
from src.utils import time
from src.channel.post import Post


class Channel:
    def __init__(self, vk_id, tg_id, last_post_id, bot, vk_api, timeout, print_url, include_photo, include_video):
        self.vk_id = vk_id
        self.tg_id = tg_id
        self.last_post_id = last_post_id
        self.poster_bot = bot
        self.vk_api = vk_api
        self.timeout = timeout
        self.print_url = print_url
        self.include_photo = include_photo
        self.include_video = include_video

    def get_new_post(self):
        r = self.vk_api.wall.get(owner_id=self.vk_id, count=2, v=5.21)
        index = 1 if r['items'][0].get('is_pinned') else 0
        post = Post(r['items'][index], self.poster_bot, timeout=self.timeout, print_url=self.print_url,
                    include_photo=self.include_photo, include_video=self.include_video)
        return post

    def raw(self):
        r = self.vk_api.wall.get(owner_id=self.vk_id, count=2, v=5.21)
        pprint(r)

    def write_last_post(self, json_path):
        with open(json_path, 'r+') as f:
            data = json.load(f)
            data['channel'][str(self.vk_id)]['last_post_id'] = self.last_post_id
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()

    def run(self, json_path):
        new_post = self.get_new_post()
        if new_post.id != self.last_post_id:
            try:
                print('{} - - [TIME: {}] [POST ID: {}]'.format(str(self.tg_id), time(), str(new_post.id)))
                new_post.send(self.tg_id)
            except Exception as ex:
                if 'wrong type of the web page content' in str(ex).lower():
                    pass
                elif str(ex).lower() != 'timed out':
                    print('ERROR:', str(ex), 'in channel', self.tg_id)
                    return {'ok': False, 'error': str(ex), 'channel': self.tg_id}
            self.last_post_id = new_post.id
            self.write_last_post(json_path)
        return {'ok': True}
