from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types  import CallbackQuery

from bot.keyboards.keyboards import (
  passenger_kb, 
  driver_kb, 
  edit_profile_kb,
)
from bot.db import database as db
from bot.states.ride_booking_state import BookRideState
from bot.states.registration_state import RegistrationState


user_info_router = Router()
user_data= {}

# Handle edit profile
@user_info_router.callback_query(RegistrationState.registered)
async def process_role(query: CallbackQuery, state: FSMContext):
    user = await db.login_user(query.from_user.id)
    user_data["role"] = user.role
    query_data = query.data
    
    res = await db.get_ride_history(query.from_user.id, user_data["role"])
    if query_data == "edit_profile":
        await state.set_state(RegistrationState.edit_profile)
        name = " " + user.full_name
        phone = " " + user.phone
        await query.message.edit_text(f"Your Profile! \n Full Name: {name} \n Phone no.: {phone}", reply_markup=edit_profile_kb.as_markup())
        return
    elif query_data == "book_ride":
        await state.set_state(BookRideState.start_location)
        await query.message.edit_text("Enter Start Location: ")
    elif query_data == "ride_history":
        
        user_or_driver = "Passenger" if user_data["role"] == "driver" else "Driver"
        if len(res)>0:
            ride_id, phone_number, driver_id, start_location, destination, travel_time, fare_estimate, status, driver_name, driver_phone_number = res[0]
            edited_text = (
                f"🚗 R I D E  H I S T O R Y 🚗\n\n"
                f"{user_or_driver}: {driver_name}\n"
                f"{user_or_driver} Phone: {driver_phone_number}\n\n"
                f"Ride ID: {ride_id}\n"
                f"Start Location: {start_location}\n"
                f"Destination: {destination}\n"
                f"Travel Time: {travel_time}\n"
                f"Fare Estimate: {fare_estimate} ETB"
            )
            await query.message.edit_text(edited_text)
        else:
            await query.message.edit_text("No ride history")
            

    elif query_data == "rate_driver":
        res = await db.get_recent_driver_details(query.from_user.id)
        print(res)

# Handle edit profile
@user_info_router.callback_query(RegistrationState.edit_profile)
async def process_role(query: CallbackQuery, state: FSMContext):
    data = query.data
    if data == "name":
        await state.set_state(RegistrationState.edit_name)
        await query.message.edit_text("Enter your full name:")
    elif data == "phone":
        await state.set_state(RegistrationState.edit_phone_number)
        await query.message.edit_text("Enter your phone number:")
    else:
        await state.set_state(RegistrationState.registered)
        
        if user_data["role"] == "driver":
            await  query.message.edit_text("Welcome Back Driver!", reply_markup=driver_kb.as_markup())
        else:
            await  query.message.edit_text("Welcome Back Passenger!", reply_markup=passenger_kb.as_markup())

@user_info_router.message(RegistrationState.edit_phone_number)
async def process_phone_number(message: Message, state: FSMContext):
    user = await db.login_user(message.from_user.id)
    new_phone = message.text
    token = message.from_user.id
    
    await db.update_user(token, user.full_name, new_phone)
    await message.answer("Your phone Edited Successfully", reply_markup=edit_profile_kb.as_markup())
    await state.set_state(RegistrationState.edit_profile)

@user_info_router.message(RegistrationState.edit_name)
async def process_name(message: Message, state: FSMContext):
    new_name = message.text
    token = message.from_user.id
    user = await db.login_user(token)

    await db.update_user(token, new_name, user.phone )
    await message.answer("Your Name Edited Successfully", reply_markup=edit_profile_kb.as_markup())
    await state.set_state(RegistrationState.edit_profile)