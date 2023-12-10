import random

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types  import (
    CallbackQuery,   
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.formatting import (
    as_line, 
    as_list,
    as_marked_section,
    HashTag,
    as_key_value,
    Bold
)


from bot.keyboards.ride_booking_kbs import (
    Action,
    RideBookingCallbackData,
    
    AcceptRideKb,
    MarkRideCompletedKb,
    RateDriverKb,
    CancelRideKb,
)
from bot.keyboards.keyboards  import (
    book_kb,
)
from bot.db import database as db
from bot.bot_instance import bot
from bot.states.ride_booking_state import BookRideState


# Define the form router
booking_router = Router()
data = {}

# Registration process
@booking_router.message(BookRideState.booking)
async def start_booking(message: Message, state: FSMContext):
    await message.answer("Enter Your Starting location: ")
    await state.set_state(BookRideState.start_location)

# Registration process
@booking_router.message(BookRideState.start_location)
async def process_start_location(message: Message, state: FSMContext):
    data["start"] = message.text
    await state.set_state(BookRideState.destination_location)
    await message.answer("Enter your destination:")

def generate_random_travel_time():
    return random.randint(10, 60)
    
@booking_router.message(BookRideState.destination_location)
async def process_destination(message: Message, state: FSMContext):
    data["destination"] = message.text
    
    travel_time = generate_random_travel_time()
    start = data["start"]
    dest = data["destination"]
    
    await state.set_state(BookRideState.booking)
    
    
    await message.answer(
        f"It might take approximately {travel_time} minutes to travel from {start} to {dest}.", 
        reply_markup=book_kb.as_markup()
    )   


builder = InlineKeyboardBuilder()

@booking_router.callback_query(BookRideState.booking)
async def process_send_alert(query:CallbackQuery, state:FSMContext ):
    
    users = await db.get_all_drivers()
    start = data["start"]
    dest = data["destination"]
    
    travel_time = generate_random_travel_time()
    ride_id = await db.request_ride(query.from_user.id, start, dest, travel_time)
    
    accept_kb = AcceptRideKb(query.from_user.id, ride_id)
    
    for user in users:
        await bot.send_message(
            user.tg_id, f"Hi {user.full_name}, there is a new ride  from {start} to {dest}!",
            reply_markup= accept_kb.as_markup()
    )
    await state.set_state(BookRideState.rating)

    await query.message.edit_text("Booking ...")
    
@booking_router.callback_query(RideBookingCallbackData.filter(F.ride_status == Action.accept))
async def process_accept(query: CallbackQuery, callback_data: RideBookingCallbackData):
    user_id = callback_data.user_id
    ride_id = callback_data.ride_id
    driver_id = query.from_user.id
    
    user = await db.get_user(user_id)
    driver = await db.get_driver(driver_id)
    res = await db.accept_ride(driver_id, ride_id)

    passemger_message = (
        f"Dear {user.full_name}, Your Ride Has Been Accepted! 🚗\n\n"
        f"Driver's Name: {driver.full_name}\n"
        f"Vehicle Model: {driver.car_model}\n"
        f"License Plate Number: {driver.license_plate}\n\n"
    )
    cancel_ride_kb = CancelRideKb(user_id, driver_id)
    
    await bot.send_message(
        user_id, 
        passemger_message,
        reply_markup=cancel_ride_kb.as_markup()
    )
    completed_ride_kb = MarkRideCompletedKb(user_id, driver_id)
    if res:
        await bot.send_message(
            driver_id,
            f"You've accepted a ride request. Please proceed to the pickup location. 🚗",
            reply_markup=completed_ride_kb.as_markup()
        )
    else:
        await bot.send_message(
            driver_id,
            f"🚗 Ride is already accepted or not pending.",
        )
 
@booking_router.callback_query(RideBookingCallbackData.filter(F.ride_status == Action.completed))
async def process_completed_ride(query: CallbackQuery, callback_data: RideBookingCallbackData, state:FSMContext):
    user_id = callback_data.user_id
    driver_id = callback_data.driver_id
    print(callback_data.driver_rated)
    user = await db.get_user(user_id)
    driver = await db.get_driver(driver_id)
    passemger_message = (
        f"Dear {user.full_name}, Your Ride Has Completed! 🚗\n\n"
        f"Driver's Name: {driver.full_name}\n"
        f"Vehicle Model: {driver.car_model}\n"
        f"License Plate Number: {driver.license_plate}\n\n"
        f"\n\n🤩 R A T E 🚖 D R I V E R 🤩\n\n"
    )
    
    rating_kb = RateDriverKb(user_id, driver_id)
    await bot.send_message(
        user_id, 
        passemger_message,
        reply_markup=rating_kb.as_markup()
    )
    await query.message.edit_text("The Ride Is Completed")
    await state.set_state(BookRideState.rating)
    
@booking_router.callback_query(RideBookingCallbackData.filter(F.ride_status == Action.cancelled))
async def process_completed_ride(query: CallbackQuery, callback_data: RideBookingCallbackData, state:FSMContext):
    user_id = callback_data.user_id
    driver_id = callback_data.driver_id

    user = await db.get_user(user_id)
    driver = await db.get_driver(driver_id)
    passemger_message = (
        f"Dear {user.full_name}, You have Cancelled Your Ride! 🚗\n\n"
        f"Driver's Name: {driver.full_name}\n"
        f"Vehicle Model: {driver.car_model}\n"
        f"License Plate Number: {driver.license_plate}\n\n"
        f"\n\n🤩 R A T E 🚖 D R I V E R 🤩\n\n"
    )
    
    rating_kb = RateDriverKb(user_id, driver_id)
    await bot.send_message(
        user_id, 
        passemger_message,
        reply_markup=rating_kb.as_markup()
    )
    
    await bot.send_message(
        driver_id,  
        f"The Ride Cancelled By Passenger {user.full_name}",
    )
   
@booking_router.callback_query(RideBookingCallbackData.filter(F.ride_status == Action.rating))
async def process_rating(query: CallbackQuery, callback_data: RideBookingCallbackData):
    user_id = callback_data.user_id
    driver_id = callback_data.driver_id
    rate = callback_data.driver_rated
    
    user = await db.get_user(user_id)
    driver = await db.get_driver(driver_id)
    print(rate)
    
    driver_message  = (
        f"🚖 Dear {driver.full_name}\n\n"
        f"🚖 Passenger {user.full_name} R A T E D   Y O U   {rate} 🤩"
    )
    
    await bot.send_message(
        driver_id, 
        driver_message,
    )
    
   
    passenger_message  = (
        f"🚖 Rating Saved\n\n"
        f"🚖 Thanks For Using RideShare"
    )
    
    await bot.send_message(
        user_id,  
        passenger_message,
    )
    
   