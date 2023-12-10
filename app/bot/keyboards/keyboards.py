from enum import Enum
from aiogram.utils.keyboard import   InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class Action(str, Enum):
  accept = "accept"
  completed = "completed"
  rating = "rating"
  cancelled = "cancelled"
   
    
class RideBookingCallbackData(CallbackData, prefix="completed_ride"):
  ride_status: str
  user_id: str
  driver_id: str
  ride_id: str
  rating:str
  driver_rated:str

    
passenger_kb = InlineKeyboardBuilder()
passenger_kb.button(text=f"✏️ Edit profile", callback_data="edit_profile")
passenger_kb.button(text=f"🚕 Book Ride", callback_data="book_ride")
passenger_kb.button(text=f"⭐️ Rate Ride", callback_data="rate_driver")
passenger_kb.button(text=f"🛣 History", callback_data="ride_history")
passenger_kb.adjust(2, 2)

driver_kb = InlineKeyboardBuilder()
driver_kb.button(text=f"✏️ Edit profile", callback_data="edit_profile")
driver_kb.button(text=f"🛣 History", callback_data="ride_history")
driver_kb.adjust(2, 2)


new_user_kb = InlineKeyboardBuilder()
new_user_kb.button(text=f"✏️ Register", callback_data="register")
new_user_kb.button(text=f"🚕 Login", callback_data="login")
new_user_kb.adjust(2, 2)

role_kb = InlineKeyboardBuilder()
role_kb.button(text=f"✏️ Passenger", callback_data="passenger")
role_kb.button(text=f"🚕 Driver", callback_data="driver")
role_kb.adjust(2, 2)

edit_profile_kb = InlineKeyboardBuilder()
edit_profile_kb.button(text=f"🎭 Edit Name", callback_data="name")
edit_profile_kb.button(text=f"🤳🏽 Edit Phone", callback_data="phone")
edit_profile_kb.button(text=f"⬅ Back", callback_data="back")
edit_profile_kb.adjust(2, 2)


book_kb = InlineKeyboardBuilder()
book_kb.button(text=f"✅ Book", callback_data="book")
book_kb.button(text=f"❎ Cancel", callback_data="cancel")

