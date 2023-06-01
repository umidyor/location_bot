import aiogram
import pandas as pd
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from geopy.geocoders import Nominatim
from geopy import distance
import sqlite3

from env import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

geolocator = Nominatim(user_agent="PoleNumberBot")

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Joy nomini kiritng")

@dp.message_handler()
async def get_pole_numbers(message: types.Message):
    place_name = message.text
    if place_name == "/joynominitanlang":
        await message.answer("Lokatsiya tashlang")
        @dp.message_handler(content_types=types.ContentType.LOCATION)
        async def handle_location(message: types.Message):
            location = message.location
            latitude = location.latitude
            longitude = location.longitude

            def is_within_tashkent_region(latitude, longitude):
                data_loc = pd.read_csv("qutb.csv")
                data_loc = data_loc[data_loc["Place"] == place_name]
                if (
                        data_loc['South'].values[0] <= latitude <= data_loc['North'].values[0] and
                        data_loc['West'].values[0] <= longitude <= data_loc['East'].values[0]
                ):
                    return True
                return False

            def get_address(latitude, longitude):
                try:
                    location = geolocator.reverse(f'{latitude}, {longitude}', exactly_one=True)
                    if location:
                        return location.address
                except Exception as e:
                    print(f'Error occurred during geocoding: {str(e)}')

                return "No'malum"

            if is_within_tashkent_region(latitude, longitude):
                address = get_address(latitude, longitude)
                await message.reply(f'Location: {address}')
                await message.reply(f'Bu joy {data_loc["Place"].values[0]}da!')
            else:
                await message.reply(f'Bu joy {data_loc["Place"].values[0]}da emas!')

    else:
        try:
            location = geolocator.geocode(place_name)
            if location is not None:
                latitude = location.latitude
                longitude = location.longitude

                # Calculate latitude positions
                north_latitude = latitude + 0.0001
                south_latitude = latitude - 0.0001

                # Calculate longitude positions
                long_dist = distance.distance((latitude, longitude), (latitude, longitude + 0.0001)).m
                east_longitude = longitude + (0.0001 / long_dist)
                west_longitude = longitude - (0.0001 / long_dist)

                await message.answer(f"Joy nomi olindi\nbuyruq {'/joynominitanlang'}")
                conn = sqlite3.connect('qutb.db')
                cursor = conn.cursor()

                # Ma'lumotlar jadvalidini yaratish
                cursor.execute('''CREATE TABLE IF NOT EXISTS qutb (
                                    Place TEXT,
                                    North REAL,
                                    South REAL,
                                    East REAL,
                                    West REAL
                                )''')

                # CSV fayldan ma'lumotlarni o'qish va bazaga yozish
                df_qutb = pd.DataFrame({
                    'Place': [place_name],
                    'North': [north_latitude],
                    'South': [south_latitude],
                    'East': [east_longitude],
                    'West': [west_longitude]
                })

                df_qutb.to_sql('qutb', conn, if_exists='append', index=False)

                conn.commit()
                conn.close()

                await message.answer("Joy nomini kiritish tugadi!")
            else:
                await message.answer("Joy nomini topib bo'lmadi!")
        except Exception as e:
            print(f'Error occurred during geocoding: {str(e)}')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)



