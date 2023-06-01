from env import BOT_TOKEN
import aiogram
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from geopy.geocoders import Nominatim
from geopy import distance

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

geolocator = Nominatim(user_agent="PoleNumberBot")

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Welcome to the Pole Number Bot! Please enter the name of a place.")

@dp.message_handler()
async def get_pole_numbers(message: types.Message):
    place_name = message.text
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

            reply_message = f"The latitude locations for {place_name} are:\n"
            reply_message += f"North Latitude: {north_latitude:.6f}\n"
            reply_message += f"South Latitude: {south_latitude:.6f}\n"
            reply_message += f"East Longitude: {east_longitude:.6f}\n"
            reply_message += f"West Longitude: {west_longitude:.6f}\n"
            await message.reply(reply_message)
        else:
            await message.reply("No results found for the provided place name.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

