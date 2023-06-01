import aiogram
from env import BOT_TOKEN
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from geopy.geocoders import Nominatim
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Initialize the bot, dispatcher, and storage
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Create a geocoder instance
geolocator = Nominatim(user_agent="my_bot")

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Welcome! First, write the name of the region you want!")

@dp.message_handler()
async def handle_region_name(message: types.Message):
    region_name = message.text

    # Fetch the location of the region
    region_location = geolocator.geocode(region_name)

    if region_location is None:
        await message.reply("Sorry, I couldn't find the region you entered.")
    else:
        await message.reply("Now drop a location.")

        # Store the region_location in the user's state
        await dp.current_state(chat=message.chat.id, user=message.from_user.id).update_data(region_location=region_location)

        # Switch to the next handler for location dropping
        dp.register_message_handler(handle_location_drop)

async def handle_location_drop(message: types.Message, state):
    user_data = await dp.current_state(chat=message.chat.id, user=message.from_user.id).get_data()
    region_location = user_data.get('region_location')
    location_name = message.text

    # Fetch the location of the dropped location
    dropped_location = geolocator.geocode(location_name)

    if dropped_location is None:
        await message.reply("Sorry, I couldn't find the location you dropped.")
    else:
        # Check if the dropped location is within the region
        if region_location.point.distance(dropped_location.point) <= float(region_location.raw['boundingbox'][2]):
            await message.reply(f"The location '{dropped_location.address}' is within the region '{region_location.address}'.")
        else:
            await message.reply(f"The location '{dropped_location.address}' is not within the region '{region_location.address}'.")

        # Remove the location drop handler
        await dp.current_state(chat=message.chat.id, user=message.from_user.id).reset_state()

# Start the bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

