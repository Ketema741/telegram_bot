# FSMs for registration and booking
from aiogram.fsm.state import State, StatesGroup

class RegistrationState(StatesGroup):
    name = State()
    password = State()
    confirm_password = State()
    phone_number = State()
    role = State()
    edit_profile = State()
    register = State()
    registered = State()
    edit_phone_number = State()
    edit_name = State()
    car_model = State()
    license = State()
