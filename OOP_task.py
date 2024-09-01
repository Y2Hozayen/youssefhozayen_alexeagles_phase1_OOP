import json
import os
# to add flight sign in as username:admin, password: admin
USERS_FILE = 'users.json'
FLIGHTS_FILES = {
    'egyptair': 'egyptair.json',
    'lufthansa': 'lufthansa.json',
    'qatarairways': 'qatar-airways.json'
}
# Helper function to load data from a JSON file
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            if filename == USERS_FILE:
                return {json.loads(line)['username']: json.loads(line) for line in file}
            else:
                return {json.loads(line)['flight_id']: json.loads(line) for line in file}
    return {}


# Helper function to save data to a JSON file
def save_json(filename, data):
    with open(filename, 'w') as file:
        for key, value in data.items():
            json.dump(value, file)
            file.write('\n')


class Account:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.bookings = []

    def create_user(self, username, password):
        users = load_json(USERS_FILE)
        if username in users:
            print("Username already exists.")
            return 0
        users[username] = {'username': username, 'password': password, 'bookings': []}
        save_json(USERS_FILE, users)
        print(f"User {username} created successfully!")
        return 1

    def login(self, username, password):
        users = load_json(USERS_FILE)
        if username in users and users[username]['password'] == password:
            print(f'Welcome! {username}')
            # Ensure 'bookings' exists for the user
            if 'bookings' not in users[username]:
                users[username]['bookings'] = []  # Initialize with an empty list if not present
                save_json(USERS_FILE, users)  # Update the users.json file
            self.bookings = users[username]['bookings']
            return 1
        else:
            print("Wrong credentials")
        return 0

    def save_user(self):
        users = load_json(USERS_FILE)
        users[self.username]['bookings'] = self.bookings
        save_json(USERS_FILE, users)

    def view_bookings(self):
        if not self.bookings:
            print("No bookings found.")
        else:
            print("Your bookings:")
            for booking in self.bookings:
                print(f"\nFlight ID: {booking['flight_id']}")
                print(f"Airline: {booking['airline']}")
                print(f"Departure Airport: {booking['departure_airport']}")
                print(f"Arrival Airport: {booking['arrival_airport']}")
                print(f"Departure Time: {booking['departure_time']}")
                print(f"Arrival Time: {booking['arrival_time']}")
                print(f"Seats Booked: {booking['seats']}")
                print(f"Meal Option: {'Yes' if booking['meal_option'] else 'No'}")
class Airline:
    def __init__(self, name):
        self.name = name
        self.flights = self.load_flights()

    def load_flights(self):
        return load_json(FLIGHTS_FILES[self.name])

    def save_flights(self):
        save_json(FLIGHTS_FILES[self.name], self.flights)

    def add_flight(self, flight):
        if flight.flight_id in self.flights:
            print("Flight already exists.")
            return 0
        else:
            self.flights[flight.flight_id] = flight.to_dict()
            self.save_flights()
            print(f"Flight {flight.flight_id} added successfully to {self.name}!")
            return 1

    def update_flight(self, flight):
        """Update flight information in the JSON file after booking."""
        self.flights[flight.flight_id] = flight.to_dict()
        self.save_flights()

    def display_flights(self):
        flight_data = load_json(FLIGHTS_FILES[self.name])
        print(json.dumps(flight_data, indent=4))


class Flight:
    def __init__(self, flight_id, departure_airport, arrival_airport, departure_time, arrival_time, seats):
        self.flight_id = flight_id
        self.departure_airport = departure_airport
        self.arrival_airport = arrival_airport
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.seats = seats

    def to_dict(self):
        return {
            "flight_id": self.flight_id,
            "departure_airport": self.departure_airport,
            "arrival_airport": self.arrival_airport,
            "departure_time": self.departure_time,
            "arrival_time": self.arrival_time,
            "seats": self.seats,
        }

    def display(self):
        print(self.to_dict())


def book_flight(account, airline, flight, no_seats, meal_option):
    if flight.seats < no_seats:
        print("Not enough seats available.")
        return 0
    flight.seats -= no_seats  # Deduct the booked seats
    booking_details = {
        'flight_id': flight.flight_id,
        'airline': airline.name,
        'departure_airport': flight.departure_airport,
        'arrival_airport': flight.arrival_airport,
        'departure_time': flight.departure_time,
        'arrival_time': flight.arrival_time,
        'seats': no_seats,
        'meal_option': meal_option
    }
    account.bookings.append(booking_details)
    account.save_user()  # Save updated bookings to the user's file
    print(f"Flight {flight.flight_id} booked successfully with {no_seats} seats and meal option: {meal_option}")

    airline.update_flight(flight)
    return 1


# Main program logic
while True:
    action = int(input("Welcome!\nTo sign in press (1)\nTo create new account press (2)\n"))
    username = input("Enter your name\n")
    password = input("Enter your password\n")
    account = Account(username, password)

    if action == 1:
        if account.login(username=username, password=password):
            break
    elif action == 2:
        if account.create_user(username=username, password=password):
            break

while True:
    service = int(input('Services\nBook flights (1)\nView Bookings (2)\nAdd Flights (3) [admin only]\n:'))

    if service == 3 and account.username != 'admin':
        print("Only admins can add flights")
        continue
    if service in [1, 2, 3]:
        break
    else:
        print("Invalid choice, please try again.")

match service:
    case 1:
        while True:
            airline_name = input("Which airline would you like to fly with? (EgyptAir, Lufthansa, QatarAirways)\n")
            if airline_name.lower() in FLIGHTS_FILES:
                airline = Airline(airline_name)
                break
            else:
                print("Invalid airline name, please try again.")
                continue
        print(f'Flights available for {airline_name}:\n')
        airline.display_flights()
        while True:
            flight_id = input("Which flight would you like to book?\n")
            if flight_id in airline.flights:
                selected_flight_data = airline.flights[flight_id]
                selected_flight = Flight(
                    flight_id=selected_flight_data["flight_id"],
                    departure_airport=selected_flight_data["departure_airport"],
                    arrival_airport=selected_flight_data["arrival_airport"],
                    departure_time=selected_flight_data["departure_time"],
                    arrival_time=selected_flight_data["arrival_time"],
                    seats=selected_flight_data["seats"]
                )
                break
            else:
                print("Invalid flight ID, please try again.")

        seating = int(input("How many seats would you like to book?\n"))
        meal_option = input("Would you like to include a meal? (Yes/No)\n").lower() == 'yes'
        book_flight(account, airline, selected_flight, seating, meal_option)

    case 2:
        account.view_bookings()

    case 3:
        if account.username == 'admin':
            airline_name = input("Enter the airline name (EgyptAir, Lufthansa, QatarAirways):\n")
            while airline_name not in FLIGHTS_FILES:
                airline_name = input("Invalid airline name, please reenter (EgyptAir, Lufthansa, QatarAirways):\n")
            airline = Airline(airline_name)
            new_flight = Flight(
                flight_id=input("Flight ID:\n"),
                departure_airport=input("Departure Airport:\n"),
                arrival_airport=input("Arrival Airport:\n"),
                departure_time=input("Departure Time:\n"),
                arrival_time=input("Arrival Time:\n"),
                seats=int(input("No. of Seats Available:\n"))
            )
            airline.add_flight(new_flight)
