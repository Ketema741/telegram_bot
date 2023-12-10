from enum import Enum
from aiogram.utils.keyboard import   InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class Action(str, Enum):
  accept = "accept"
  completed = "completed"
  rating = "rating"
  cancelled = "cancelled"
   
    
class RideBookingCallbackData(CallbackData, prefix="ride_boking"):
  ride_status: str
  user_id: int
  driver_id: int
  ride_id: int
  rating:str
  driver_rated:str
  

accpet_ride_kb = InlineKeyboardBuilder()

def AcceptRideKb(user_id, ride_id):
  return accpet_ride_kb.button(        
    text="Accept Ride", 
    callback_data=RideBookingCallbackData(
      ride_status="accept", 
      user_id=user_id, 
      ride_id=ride_id, 
      driver_id=0, 
      rating="", 
      driver_rated="0"
    )
  )
  
cancel_ride_kb = InlineKeyboardBuilder()

def CancelRideKb(user_id, driver_id):
  return cancel_ride_kb.button(        
    text="❎ Cancel Ride", 
    callback_data=RideBookingCallbackData(
      ride_status="cancelled", 
      rating="",
      driver_id=driver_id,
      user_id=user_id, 
      ride_id=0, 
      driver_rated="0"
    )
  )
  
completed_ride_kb = InlineKeyboardBuilder()
def MarkRideCompletedKb(user_id, driver_id):
  return completed_ride_kb.button(
    text=f"✅ Mark A Ride Completed", 
    callback_data=RideBookingCallbackData(
      ride_status="completed", 
      user_id=user_id, 
      driver_id=driver_id, 
      ride_id=0,
      rating="", 
      driver_rated="0"
    )
  )

rating_kb = InlineKeyboardBuilder()
def RateDriverKb(user_id, driver_id):
  rating_kb.button(
    text=f"⭐️",     
    callback_data=RideBookingCallbackData(
      ride_status="rating", 
      user_id=user_id, 
      driver_id=driver_id, 
      ride_id=0,
      rating="", 
      driver_rated="1"
    )
  )
  rating_kb.button(
    text=f"⭐️",     
    callback_data=RideBookingCallbackData(
      ride_status="rating", 
      user_id=user_id, 
      driver_id=driver_id, 
      ride_id=0,
      rating="", 
      driver_rated="2"
    )
  )
  rating_kb.button(
    text=f"⭐️",     
    callback_data=RideBookingCallbackData(
      ride_status="rating", 
      user_id=user_id, 
      driver_id=driver_id, 
      ride_id=0,
      rating="", 
      driver_rated="3"
    )
  )
  rating_kb.button(
    text=f"⭐️",     
    callback_data=RideBookingCallbackData(
      ride_status="rating", 
      user_id=user_id, 
      driver_id=driver_id, 
      ride_id=0,
      rating="", 
      driver_rated="4"
    )
  )
  rating_kb.button(
    text=f"⭐️",     
    callback_data=RideBookingCallbackData(
      ride_status="rating", 
      user_id=user_id, 
      driver_id=driver_id, 
      ride_id=0,
      rating="", 
      driver_rated="5"
    )
  )
  rating_kb.adjust(5, 2)
  
  return rating_kb