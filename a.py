from env import BOT_TOKEN
import sqlite3

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_polling
from geopy.geocoders import Nominatim
from geopy import distance
import pandas as pd

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
        data_loc = pd.read_csv("qutb.csv")
        if not data_loc.empty:
            d = data_loc[data_loc["Place"] == place_name]
            if not d.empty:
                REGION_BOUNDARY = {
                    'north': d["North"].values[0],
                    'south': d["South"].values[0],
                    'west': d["West"].values[0],
                    'east': d["East"].values[0]
                }

                def is_within_tashkent_region(latitude, longitude):
                    if (
                            REGION_BOUNDARY['south'] <= latitude <= REGION_BOUNDARY['north'] and
                            REGION_BOUNDARY['west'] <= longitude <= REGION_BOUNDARY['east']
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

                @dp.message_handler(content_types=types.ContentType.LOCATION)
                async def handle_location(message: types.Message):
                    location = message.location
                    latitude = location.latitude
                    longitude = location.longitude
                    data_loc = pd.read_csv("qutb.csv")

                    if is_within_tashkent_region(latitude, longitude):
                        address = get_address(latitude, longitude)
                        await message.reply(f'Location: {address}')
                        await message.reply(f'Bu joy {data_loc["Place"].values[0]}da!')
                    else:
                        await message.reply(f'Bu joy {data_loc["Place"].values[0]}da emas!')
            else:
                await message.reply("Yaxshi!Lokatsiya tashlang.")
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
                cursor.execute('SELECT * FROM qutb')
                rows = cursor.fetchall()
                data_loc = pd.DataFrame(rows, columns=['Place', 'North', 'South', 'East', 'West'])
                data_loc.to_csv("qutb.csv")

                cursor.close()
                conn.close()

            else:
                await message.reply("Bunday joy nomi topilmadi.")
        except Exception as e:
            await message.reply(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    start_polling(dp, skip_updates=True)



