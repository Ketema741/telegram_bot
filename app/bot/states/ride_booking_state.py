from aiogram.fsm.state import State, StatesGroup

class BookRideState(StatesGroup):
    booking = State()
    start_location = State()
    destination_location = State()
    accepting = State()
    accept = State()
    rating = State()