import sqlite3 as sq
from bot.models.drivers import Driver
from bot.models.passenger import User

db = sq.connect('ride_app.db')
cur = db.cursor()

async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS users ("
                "user_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "tg_id TEXT UNIQUE, "
                "full_name TEXT, "
                "phone TEXT, "
                "role TEXT)")
    
    cur.execute("CREATE TABLE IF NOT EXISTS drivers ("
                "driver_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "tg_id INTEGER UNIQUE, "
                "full_name TEXT, "
                "phone TEXT, "
                "role TEXT, "
                "car_model TEXT, "
                "license_plate TEXT)")
    
    cur.execute("CREATE TABLE IF NOT EXISTS rides ("
                "ride_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "user_id INTEGER, "
                "driver_id INTEGER, "
                "start_location TEXT, "
                "destination TEXT, "
                "estimated_arrival INTEGER, "  # in minutes
                "fare_estimate INTEGER, "  # in currency
                "status TEXT, "  # pending, accepted, completed, cancelled, etc.
                "FOREIGN KEY (user_id) REFERENCES users(user_id), "
                "FOREIGN KEY (driver_id) REFERENCES drivers(driver_id))")
    
    cur.execute("CREATE TABLE IF NOT EXISTS ratings ("
                "rating_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "user_id INTEGER, "
                "driver_id INTEGER, "
                "rating INTEGER, "
                "FOREIGN KEY (user_id) REFERENCES users(user_id), "
                "FOREIGN KEY (driver_id) REFERENCES drivers(driver_id))")

async def signup_user(user):
    if user["role"] == 'passenger':
        db.execute("INSERT INTO users (tg_id, full_name, phone, role) VALUES (?, ?, ?, ?)",
                            (user["tg_id"], user["full_name"], user["phone"], user["role"]))
        db.commit()
        print("User signed up successfully.")
        return True
    elif user["role"] == 'driver':

        db.execute("INSERT INTO drivers (tg_id, full_name, phone, role, car_model, license_plate) VALUES (?, ?, ?, ?, ?, ?)",
                            (user["tg_id"], user["full_name"], user["phone"], user["role"], user["car_model"], user["license_plate"]))
        db.commit()
        print("Driver signed up successfully.")
        return True
    else:
        print("Invalid role specified.")
        return False


async def login_user(tg_id):
    # Check in the users table
    user_query =  db.execute("SELECT * FROM users WHERE tg_id=?", (tg_id,))
    user_data =  user_query.fetchone()

    if user_data:
        user = User(*user_data)
        return user

    # If not found in the users table, check in the drivers table
    driver_query =  db.execute("SELECT * FROM drivers WHERE tg_id=?", (tg_id,))
    driver_data =  driver_query.fetchone()

    if driver_data:
        driver = Driver(*driver_data)
        return driver

    return {}


async def update_user(tg_id, new_full_name, new_phone):
    user_query = db.execute("SELECT * FROM users WHERE tg_id=?", (tg_id,))
    user = user_query.fetchone()

    if user:
        db.execute("UPDATE users SET full_name=?, phone=? WHERE tg_id=?",
                         (new_full_name, new_phone, tg_id))
        print("User information updated successfully.")
        db.commit()
        return True
    else:
        print("User not found.")
        return False

async def get_user(tg_id):
    # Fetch user details based on the Telegram ID
    user_query = db.execute("SELECT * FROM users WHERE tg_id=?", (tg_id,))
    user = user_query.fetchone()
    
    return User(*user) 

async def get_driver(tg_id):
    user_query = db.execute("SELECT * FROM drivers WHERE tg_id=?", (tg_id,))
    user = user_query.fetchone()
    
    return Driver(*user)

async def get_all_drivers():
    # Fetch all drivers from the database
    cursor = db.execute("SELECT * FROM drivers")
    rows = cursor.fetchall()

    drivers = []
    for row in rows:
        driver = Driver(*row)
        drivers.append(driver)

    return drivers

async def request_ride(user_id, start_location, destination, travel_time):
    # Generate estimated arrival time and fare estimate (example values)

    fare_estimate = 5 * travel_time # currency

    # Set the ride status to 'pending' when a ride is requested
    status = 'pending'

    # Insert data into the rides table and retrieve the ID
    cur.execute("INSERT INTO rides (user_id, start_location, destination, estimated_arrival, fare_estimate, status) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, start_location, destination, travel_time, fare_estimate, status))
    ride_id = cur.lastrowid
    db.commit()

    # Return the ride ID
    return ride_id
    
async def accept_ride(driver_id, ride_id):
    # Check if the ride is pending and not already accepted
    cur.execute("SELECT * FROM rides WHERE ride_id=? AND status='pending'", (ride_id,))
    ride = cur.fetchone()

    if ride:
        # Update the ride status to 'accepted' and assign the driver to the ride
        cur.execute("UPDATE rides SET status='accepted', driver_id=? WHERE ride_id=?", (driver_id, ride_id))
        db.commit()
        print("Ride accepted successfully!")
        return True
    else:
        print("Ride is already accepted or not pending.")
        return False

async def get_recent_driver_details(user_id):
    cur.execute("""
        SELECT d.driver_id, d.full_name, d.phone, r.ride_id
        FROM rides AS r
        INNER JOIN drivers AS d ON r.driver_id = d.driver_id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
        LIMIT 1
    """, (user_id,))

    driver_data = cur.fetchone()

    if driver_data:
        return {
            "id": driver_data[0],
            "full_name": driver_data[1],
            "phone_number": driver_data[2],
            "ride_id": driver_data[3],
        }

    return {}

async def submit_rating(user_id, rating):
    # Get the latest ride details for the user
    cur.execute("SELECT driver_id, id FROM rides WHERE user_id=? ORDER BY created_at DESC LIMIT 1", (user_id,))
    ride_data = cur.fetchone()

    if not ride_data:
        print("No recent ride found for user")
        return []

    driver_id, ride_id = ride_data

    # Check if user has already rated the driver
    cur.execute("SELECT * FROM ratings WHERE user_id=? AND ride_id=? AND driver_id=?", (user_id, ride_id, driver_id))
    existing_rating = cur.fetchone()

    # Determine if update or insert is needed
    if existing_rating:
        operation = "UPDATE"
        update_data = (rating, user_id, ride_id, driver_id)
        message = "Rating updated successfully!"
    else:
        operation = "INSERT"
        insert_data = (user_id, ride_id, driver_id, rating)
        message = "Rating submitted successfully!"

    # Execute the appropriate SQL statement
    if operation == "UPDATE":
        cur.execute("UPDATE ratings SET rating=? WHERE user_id=? AND ride_id=? AND driver_id=?", update_data)
    else:
        cur.execute("INSERT INTO ratings (user_id, ride_id, driver_id, rating) VALUES (?, ?, ?, ?)", insert_data)

    db.commit()
    print(message)
    
    
async def get_ride_history(user_id, role):
    # Validate role input
    if role not in ["passenger", "driver"]:
        raise ValueError(f"Invalid role provided: {role}")

    # Define separate queries based on role
    if role == "passenger":
        query = """
        SELECT r.*, d.full_name AS driver_name, d.phone AS driver_phone
        FROM rides AS r
        INNER JOIN drivers AS d ON r.driver_id = d.tg_id
        WHERE r.user_id = ?
        """
    else:
        query = """
        SELECT r.*, u.full_name AS passenger_name, u.phone AS passenger_phone
        FROM rides AS r
        INNER JOIN users AS u ON r.user_id = u.tg_id
        WHERE r.driver_id = ?
        """
    # Execute the appropriate query and return results
    cur.execute(query, (user_id,))
    ride_history = cur.fetchall()

    return ride_history


async def mark_ride_completed(ride_id, role):
    # Check if the ride exists
    cur.execute("SELECT * FROM rides WHERE ride_id=?", (ride_id,))
    ride = cur.fetchone()

    if ride:
        if role == 'user':
            # Update ride status to 'completed' by the user
            cur.execute("UPDATE rides SET status='completed' WHERE ride_id=?", (ride_id,))
            db.commit()
            print("Ride marked as completed by the user.")
            return True
        elif role == 'driver':
            # Update ride status to 'completed' by the driver
            cur.execute("UPDATE rides SET status='completed' WHERE ride_id=?", (ride_id,))
            db.commit()
            print("Ride marked as completed by the driver.")
            return True
        else:
            print("Invalid role specified.")
            return False
    else:
        print("Ride not found.")
        return False
