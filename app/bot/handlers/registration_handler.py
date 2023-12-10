from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from aiogram.types.keyboard_button import KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.types  import CallbackQuery


from bot.keyboards.keyboards import (
    passenger_kb, 
    driver_kb, 
    role_kb,
)
from bot.db import database as db
from bot.handlers.book_ride_handler import booking_router
from bot.handlers.user_info_handler import user_info_router
from bot.states.registration_state import RegistrationState


# Define the form router
form_router = Router()
form_router.include_router(booking_router)
form_router.include_router(user_info_router)

# Global state for storing user data (optional)
user_data = {}
token = ""

# Registration process
@form_router.message(CommandStart())
async def start_registration(message: Message, state: FSMContext):
    await db.db_start()
    token = message.from_user.id

    user = await db.login_user(token)

    
    if not  user:
        user_data["tg_id"] = token
    else:
        user_data["role"] = user.role
   
        
    state_to_set = RegistrationState.registered if user else RegistrationState.name
    await state.set_state(state_to_set)
    
    if user:
        if user.role == "driver":
            await message.answer("Welcome Back Driver!", reply_markup=driver_kb.as_markup())
        else:
            await message.answer("Welcome Back Passenger!", reply_markup=passenger_kb.as_markup())
    else:
        await message.answer("Welcome to A2SV Ride Share! Enter your full name:", reply_markup=ReplyKeyboardRemove())


# Registration process
@form_router.message(RegistrationState.register)
async def process_register(message: Message, state: FSMContext):
    await state.set_state(RegistrationState.name)
    await message.answer("Enter your full name:")
    
    
phone_number_button = KeyboardButton(
    text="Share Phone Number",
    request_contact=True,
)
reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[phone_number_button]])


@form_router.message(RegistrationState.name)
async def process_name(message: Message, state: FSMContext):
    user_data["full_name"] = message.text
    await state.set_state(RegistrationState.phone_number)
    await message.answer("Share your phone number", reply_markup=reply_markup)

# Handle phone number sharing
@form_router.message(RegistrationState.phone_number)
async def process_phone_number(message: Message, state: FSMContext):
    user_data["phone"] = message.contact.phone_number
    await state.set_state(RegistrationState.role)
    print(user_data)
    await message.answer("Choose your role:", reply_markup=role_kb.as_markup())


# Handle role selection
@form_router.callback_query(RegistrationState.role)
async def process_role(query: CallbackQuery, state: FSMContext):
    role = query.data
    user_data["role"] = role
    
    if role =="passenger":
        await db.signup_user(user_data)
        await query.message.edit_text("You Are Registered", reply_markup=passenger_kb.as_markup())
        await state.set_state(RegistrationState.registered)
    else:
        await state.set_state(RegistrationState.car_model)
        await query.message.edit_text("Enter Your Car Model: ")
        
# Handle model selection
@form_router.message(RegistrationState.car_model)
async def process_car_model(message: Message, state: FSMContext):
    user_data["car_model"] = message.text

    await state.set_state(RegistrationState.license)
    await message.answer("Enter license plate number: ")

    
# Handle model selection
@form_router.message(RegistrationState.license)
async def process_license(message: Message, state: FSMContext):
    user_data["license_plate"] = message.text
    
    await db.signup_user(user_data)
    await message.answer("You Have Registered Successfully", reply_markup=driver_kb.as_markup())
    await state.set_state(RegistrationState.registered)

 