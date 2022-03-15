from telegram import InputMediaPhoto


class Post:
    def __init__(self, post_dict, bot, timeout, print_url, include_photo=True, include_video=True):
        self.post_dict = post_dict
        self.id = post_dict['id']
        self.owner_id = str(post_dict['from_id'])
        self.text = post_dict['text']
        self.include_photo = include_photo
        self.include_video = include_video
        self.photos, self.video_urls = self.get_media()
        self.url = 'https://vk.com/wall{}_{}'.format(self.owner_id, self.id)
        self.print_url = print_url
        self.poster_bot = bot
        self.timeout = timeout

    @staticmethod
    def best_photo_key(photo_keys):
        photo_keys_int = [int(key[6:]) for key in photo_keys]
        best_photo_key = 'photo_' + str(max(photo_keys_int))
        return best_photo_key

    def get_media(self):
        photos, videos = [], []
        if (self.include_photo or self.include_video) and self.post_dict.get('attachments'):
            for attachment in self.post_dict['attachments']:
                if self.include_photo:
                    if attachment['type'] == 'photo':
                        photo_keys = [key for key in attachment['photo'].keys() if 'photo' in key]
                        biggest_photo = attachment['photo'][self.best_photo_key(photo_keys)]
                        photos.append(biggest_photo)
                if self.include_video:
                    if attachment['type'] == 'video':
                        video = attachment['video']
                        owner_id = video['owner_id']
                        video_id = video['id']
                        video_url = 'https://vk.com/video{}_{}'.format(owner_id, video_id)
                        videos.append(video_url)
        return photos, videos

    def send(self, tg_id):
        text_with_video_urls = self.text

        if self.include_video:
            for video_url in self.video_urls:
                text_with_video_urls += '\n' + video_url

        if self.print_url:
            text_with_video_urls += '\n' + self.url

        multimedia = []
        if self.photos:
            for photo in self.photos:
                multimedia.append(InputMediaPhoto(photo))

        if text_with_video_urls and multimedia and self.include_photo:
            # if text and multimedia exist
            if len(text_with_video_urls) < 1024:
                # adding text as a caption to the first multimedia
                first_media = multimedia[0]
                first_media.caption = text_with_video_urls
                multimedia[0] = first_media
                self.poster_bot.send_media_group(chat_id=tg_id, media=multimedia)

            else:
                # sending text and multimedia separately
                if len(text_with_video_urls) <= 3900:
                    self.poster_bot.send_message(chat_id=tg_id, text=text_with_video_urls)
                else:
                    for i in range(0, len(text_with_video_urls), 3900):
                        self.poster_bot.send_message(chat_id=tg_id, text=text_with_video_urls[i:i + 3900])
                self.poster_bot.send_media_group(chat_id=tg_id, media=multimedia)
        elif multimedia and self.include_photo:
            # there is no text in post
            # sending only multimedia
            self.poster_bot.send_media_group(chat_id=tg_id, media=multimedia)
        elif text_with_video_urls:
            # there is no multimedia in post
            # sending only text
            if len(text_with_video_urls) <= 3900:
                self.poster_bot.send_message(chat_id=tg_id, text=text_with_video_urls)
            else:
                for i in range(0, len(text_with_video_urls), 3900):
                    self.poster_bot.send_message(chat_id=tg_id, text=text_with_video_urls[i:i+3900])
