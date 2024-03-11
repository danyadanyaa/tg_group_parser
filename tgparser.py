import json
import os

from telethon import TelegramClient
from datetime import datetime, date


async def is_valid_date(date_str, date_format="%Y-%m-%d"):
    try:
        parsed_date = datetime.strptime(date_str, date_format).date()
        today = date.today()
        return parsed_date <= today
    except ValueError:
        return False


async def get_data(channel):
    all_msg, photos = [], []
    prv_grp = 0
    msg_dict = {}
    async for message in client.iter_messages(channel, limit=10000):
        if message.date.date() < datetime.strptime(ARG_DATE, '%Y-%m-%d').date():
            break
        if message.grouped_id:
            if message.grouped_id == prv_grp or prv_grp == 0:
                if message.photo:
                    await message.download_media(file=f'./tgparser/{message.photo.id}')
                    photos.append({'photo': str(message.photo.id) + '.jpg'})
                if message.message:
                    msg = message.to_dict()
                    msg_dict['message'] = msg['message']
                msg_dict['date'] = str(message.date.date())
            else:
                if msg_dict:
                    msg_dict['photo'] = photos
                    all_msg.append(msg_dict)
                photos = []
                msg_dict = {}
                msg = message.to_dict()
                if message.message:
                    all_msg.append({'message': msg['message']})
                    msg_dict = {}
                if message.photo:
                    await message.download_media(file=f'./tgparser/{message.photo.id}')
                    photos.append({'photo': str(message.photo.id) + '.jpg'})
                msg_dict['date'] = str(message.date.date())
            prv_grp = message.grouped_id
        else:
            if msg_dict:
                msg_dict['photo'] = photos
                all_msg.append(msg_dict)
                msg_dict = {}
                photos = []
            msg = message.to_dict()
            if message.photo:
                await message.download_media(file=f'./tgparser/{message.photo.id}')
                all_msg.append(
                    {'message': msg['message'],
                     'photo': [{'photo': str(message.photo.id) + '.jpg'}],
                     'date': str(message.date.date())}
                )
            else:
                all_msg.append({'message': msg['message'], 'date': str(message.date.date())})
    if msg_dict:
        msg_dict['photo'] = photos
        all_msg.append(msg_dict)
    for l in all_msg:
        l['resource'] = channel.username

    return all_msg


api_id = 1  # данные с https://my.telegram.org/ лучше наверное зарегистрировать новый аккаунт
api_hash = 'a'
client = TelegramClient('testsr', api_id, api_hash)


ARG_DATE = os.getenv('ARG_DATE')
ARG_GROUP = os.getenv('ARG_GROUP')


async def main():
    if not ARG_DATE or not ARG_GROUP:
        raise Exception('Необходимо указать переменные ARG_DATE и ARG_GROUP')

    if not await is_valid_date(ARG_DATE):
        raise Exception(f'Неверный формат даты {ARG_DATE}')

    channel = await client.get_entity(ARG_GROUP)
    messages = await get_data(channel)

    print(json.dumps(messages, ensure_ascii=False, indent=4))


if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
