import json
import os
import datetime
import random
import string
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

# ==================== BASE CLASSES ====================
class User(ABC):
    """Abstract base class for all users"""
    def __init__(self, username: str, password: str, user_type: str):
        self.username = username
        self.password = password
        self.user_type = user_type
    
    @abstractmethod
    def display_menu(self):
        pass
    
    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'user_type': self.user_type
        }

class Bike:
    """Bike class representing a rental bike"""
    def __init__(self, bike_id: str, name: str, color: str, plate_number: str, 
                 price_per_day: float, location: str, available: bool = True):
        self.bike_id = bike_id
        self.name = name
        self.color = color
        self.plate_number = plate_number
        self.price_per_day = price_per_day
        self.location = location
        self.available = available
    
    def to_dict(self):
        return {
            'bike_id': self.bike_id,
            'name': self.name,
            'color': self.color,
            'plate_number': self.plate_number,
            'price_per_day': self.price_per_day,
            'location': self.location,
            'available': self.available
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            data['bike_id'],
            data['name'],
            data['color'],
            data['plate_number'],
            data['price_per_day'],
            data['location'],
            data['available']
        )
    
    def __str__(self):
        status = "Available" if self.available else "Rented"
        return (f"ID: {self.bike_id} | {self.name} ({self.color}) | "
                f"Plate: {self.plate_number} | ${self.price_per_day}/day | "
                f"Location: {self.location} | Status: {status}")

class Booking:
    """Booking class representing a bike rental booking"""
    def __init__(self, booking_id: str, customer_username: str, bike_id: str,
                 pickup_location: str, from_date: str, to_date: str,
                 total_amount: float, status: str = "Pending"):
        self.booking_id = booking_id
        self.customer_username = customer_username
        self.bike_id = bike_id
        self.pickup_location = pickup_location
        self.from_date = from_date
        self.to_date = to_date
        self.total_amount = total_amount
        self.status = status  # Pending, Approved, Rejected, Completed
    
    def to_dict(self):
        return {
            'booking_id': self.booking_id,
            'customer_username': self.customer_username,
            'bike_id': self.bike_id,
            'pickup_location': self.pickup_location,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'total_amount': self.total_amount,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            data['booking_id'],
            data['customer_username'],
            data['bike_id'],
            data['pickup_location'],
            data['from_date'],
            data['to_date'],
            data['total_amount'],
            data['status']
        )
    
    def __str__(self):
        return (f"Booking ID: {self.booking_id}\n"
                f"Customer: {self.customer_username}\n"
                f"Bike ID: {self.bike_id}\n"
                f"Pickup: {self.pickup_location}\n"
                f"From: {self.from_date} To: {self.to_date}\n"
                f"Total: ${self.total_amount:.2f}\n"
                f"Status: {self.status}")

# ==================== CUSTOMER CLASS ====================
class Customer(User):
    """Customer class for bike rental customers"""
    def __init__(self, username: str, password: str, name: str = "", 
                 phone: str = "", email: str = ""):
        super().__init__(username, password, "customer")
        self.name = name
        self.phone = phone
        self.email = email
    
    def display_menu(self):
        while True:
            print("\n" + "="*50)
            print("CUSTOMER DASHBOARD")
            print("="*50)
            print("1. View Available Bikes")
            print("2. Book a Bike")
            print("3. View Booking Status")
            print("4. Make Payment")
            print("5. View My Bookings")
            print("6. Logout")
            
            choice = input("\nEnter your choice (1-6): ")
            
            if choice == '1':
                self.view_available_bikes()
            elif choice == '2':
                self.book_bike()
            elif choice == '3':
                self.view_booking_status()
            elif choice == '4':
                self.make_payment()
            elif choice == '5':
                self.view_my_bookings()
            elif choice == '6':
                print("Logging out...")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def view_available_bikes(self):
        """View all available bikes or filter by location"""
        bikes = BikeRentalSystem.load_bikes()
        available_bikes = [bike for bike in bikes if bike.available]
        
        if not available_bikes:
            print("\nNo bikes available at the moment.")
            return
        
        print("\n" + "="*50)
        print("AVAILABLE BIKES")
        print("="*50)
        
        location = input("Enter location to filter (press Enter for all): ").strip()
        
        filtered_bikes = available_bikes
        if location:
            filtered_bikes = [bike for bike in available_bikes 
                            if bike.location.lower() == location.lower()]
        
        if filtered_bikes:
            for bike in filtered_bikes:
                print(bike)
            print(f"\nTotal available bikes: {len(filtered_bikes)}")
        else:
            print(f"\nNo bikes available in {location}")
    
    def book_bike(self):
        """Book a bike for rental"""
        print("\n" + "="*50)
        print("BOOK A BIKE")
        print("="*50)
        
        # Get location
        pickup_location = input("Enter pickup location: ").strip()
        
        # Get dates
        from_date = input("Enter from date (YYYY-MM-DD): ").strip()
        to_date = input("Enter to date (YYYY-MM-DD): ").strip()
        
        # Validate dates
        try:
            from_dt = datetime.datetime.strptime(from_date, "%Y-%m-%d")
            to_dt = datetime.datetime.strptime(to_date, "%Y-%m-%d")
            
            if from_dt > to_dt:
                print("Error: From date must be before To date.")
                return
            if from_dt < datetime.datetime.now():
                print("Error: From date cannot be in the past.")
                return
        except ValueError:
            print("Error: Invalid date format. Use YYYY-MM-DD.")
            return
        
        # Get available bikes in location
        bikes = BikeRentalSystem.load_bikes()
        available_bikes = [bike for bike in bikes 
                          if bike.available and bike.location.lower() == pickup_location.lower()]
        
        if not available_bikes:
            print(f"\nNo bikes available in {pickup_location}")
            return
        
        # Display available bikes
        print(f"\nAvailable bikes in {pickup_location}:")
        for i, bike in enumerate(available_bikes, 1):
            print(f"{i}. {bike}")
        
        # Select bike
        try:
            bike_choice = int(input("\nSelect bike number to book: "))
            if 1 <= bike_choice <= len(available_bikes):
                selected_bike = available_bikes[bike_choice - 1]
                
                # Calculate rental days and amount
                rental_days = (to_dt - from_dt).days + 1
                total_amount = selected_bike.price_per_day * rental_days
                
                print(f"\nBooking Summary:")
                print(f"Bike: {selected_bike.name}")
                print(f"Rental Period: {rental_days} days")
                print(f"Price per day: ${selected_bike.price_per_day}")
                print(f"Total Amount: ${total_amount:.2f}")
                
                confirm = input("\nConfirm booking? (yes/no): ").lower()
                
                if confirm == 'yes':
                    # Generate unique booking ID
                    booking_id = 'BKG' + ''.join(random.choices(string.digits, k=6))
                    
                    # Create booking
                    booking = Booking(
                        booking_id=booking_id,
                        customer_username=self.username,
                        bike_id=selected_bike.bike_id,
                        pickup_location=pickup_location,
                        from_date=from_date,
                        to_date=to_date,
                        total_amount=total_amount,
                        status="Pending"
                    )
                    
                    # Save booking
                    BikeRentalSystem.save_booking(booking)
                    
                    print(f"\n✅ Booking successful!")
                    print(f"Your Booking ID: {booking_id}")
                    print("Status: Pending (Waiting for admin approval)")
                else:
                    print("Booking cancelled.")
            else:
                print("Invalid bike number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    def view_booking_status(self):
        """View booking status by booking ID"""
        print("\n" + "="*50)
        print("VIEW BOOKING STATUS")
        print("="*50)
        
        booking_id = input("Enter your Booking ID: ").strip()
        
        bookings = BikeRentalSystem.load_bookings()
        booking = next((b for b in bookings if b.booking_id == booking_id 
                       and b.customer_username == self.username), None)
        
        if booking:
            print("\n" + "-"*50)
            print(booking)
            print("-"*50)
        else:
            print(f"No booking found with ID: {booking_id}")
    
    def make_payment(self):
        """Make payment for a booking"""
        print("\n" + "="*50)
        print("MAKE PAYMENT")
        print("="*50)
        
        booking_id = input("Enter Booking ID: ").strip()
        
        bookings = BikeRentalSystem.load_bookings()
        booking = next((b for b in bookings if b.booking_id == booking_id 
                       and b.customer_username == self.username), None)
        
        if not booking:
            print(f"No booking found with ID: {booking_id}")
            return
        
        if booking.status != "Approved":
            print(f"Cannot make payment. Booking status is: {booking.status}")
            return
        
        print(f"\nPayment Details:")
        print(f"Booking ID: {booking.booking_id}")
        print(f"Amount to pay: ${booking.total_amount:.2f}")
        
        print("\nSelect payment method:")
        print("1. Credit Card")
        print("2. Debit Card")
        print("3. PayPal")
        print("4. Cancel")
        
        choice = input("\nEnter choice (1-4): ")
        
        if choice in ['1', '2', '3']:
            payment_methods = {1: "Credit Card", 2: "Debit Card", 3: "PayPal"}
            method = payment_methods[int(choice)]
            
            # For demo purposes, simulate payment
            print(f"\nProcessing {method} payment...")
            
            # Update booking status
            booking.status = "Completed"
            
            # Update bike availability
            bikes = BikeRentalSystem.load_bikes()
            for bike in bikes:
                if bike.bike_id == booking.bike_id:
                    bike.available = False
                    break
            
            # Save updated data
            BikeRentalSystem.save_all_data({'bikes': bikes, 'bookings': bookings})
            
            print(f"✅ Payment successful!")
            print(f"Booking {booking_id} is now completed.")
        else:
            print("Payment cancelled.")
    
    def view_my_bookings(self):
        """View all bookings for this customer"""
        print("\n" + "="*50)
        print("MY BOOKINGS")
        print("="*50)
        
        bookings = BikeRentalSystem.load_bookings()
        my_bookings = [b for b in bookings if b.customer_username == self.username]
        
        if not my_bookings:
            print("You have no bookings yet.")
            return
        
        for booking in my_bookings:
            print("\n" + "-"*50)
            print(booking)
            print("-"*50)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'name': self.name,
            'phone': self.phone,
            'email': self.email
        })
        return data

# ==================== ADMIN CLASS ====================
class Admin(User):
    """Admin class for system administration"""
    def __init__(self, username: str, password: str):
        super().__init__(username, password, "admin")
    
    def display_menu(self):
        while True:
            print("\n" + "="*50)
            print("ADMIN DASHBOARD")
            print("="*50)
            print("1. Add Bike")
            print("2. View All Bikes")
            print("3. Update Bike Details")
            print("4. Delete Bike")
            print("5. View All Bookings")
            print("6. Approve/Reject Bookings")
            print("7. View All Customers")
            print("8. Logout")
            
            choice = input("\nEnter your choice (1-8): ")
            
            if choice == '1':
                self.add_bike()
            elif choice == '2':
                self.view_all_bikes()
            elif choice == '3':
                self.update_bike()
            elif choice == '4':
                self.delete_bike()
            elif choice == '5':
                self.view_all_bookings()
            elif choice == '6':
                self.manage_bookings()
            elif choice == '7':
                self.view_all_customers()
            elif choice == '8':
                print("Logging out...")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def add_bike(self):
        """Add a new bike to the system"""
        print("\n" + "="*50)
        print("ADD NEW BIKE")
        print("="*50)
        
        bike_id = 'BIKE' + ''.join(random.choices(string.digits, k=4))
        
        print(f"Bike ID (auto-generated): {bike_id}")
        name = input("Enter bike name: ").strip()
        color = input("Enter bike color: ").strip()
        plate_number = input("Enter plate number: ").strip()
        
        try:
            price_per_day = float(input("Enter price per day ($): ").strip())
        except ValueError:
            print("Invalid price. Please enter a number.")
            return
        
        location = input("Enter location: ").strip()
        
        # Create new bike
        bike = Bike(
            bike_id=bike_id,
            name=name,
            color=color,
            plate_number=plate_number,
            price_per_day=price_per_day,
            location=location,
            available=True
        )
        
        # Save bike
        bikes = BikeRentalSystem.load_bikes()
        bikes.append(bike)
        BikeRentalSystem.save_bikes(bikes)
        
        print(f"\n✅ Bike '{name}' added successfully!")
        print(f"Bike ID: {bike_id}")
    
    def view_all_bikes(self):
        """View all bikes in the system"""
        bikes = BikeRentalSystem.load_bikes()
        
        print("\n" + "="*50)
        print("ALL BIKES")
        print("="*50)
        
        if not bikes:
            print("No bikes in the system.")
            return
        
        for bike in bikes:
            print(bike)
        
        print(f"\nTotal bikes: {len(bikes)}")
    
    def update_bike(self):
        """Update bike details"""
        print("\n" + "="*50)
        print("UPDATE BIKE DETAILS")
        print("="*50)
        
        bike_id = input("Enter Bike ID to update: ").strip()
        
        bikes = BikeRentalSystem.load_bikes()
        bike = next((b for b in bikes if b.bike_id == bike_id), None)
        
        if not bike:
            print(f"No bike found with ID: {bike_id}")
            return
        
        print(f"\nCurrent details of {bike_id}:")
        print(bike)
        print("\nEnter new details (press Enter to keep current):")
        
        name = input(f"Name [{bike.name}]: ").strip()
        if name:
            bike.name = name
        
        color = input(f"Color [{bike.color}]: ").strip()
        if color:
            bike.color = color
        
        plate_number = input(f"Plate number [{bike.plate_number}]: ").strip()
        if plate_number:
            bike.plate_number = plate_number
        
        price = input(f"Price per day [{bike.price_per_day}]: ").strip()
        if price:
            try:
                bike.price_per_day = float(price)
            except ValueError:
                print("Invalid price. Price not updated.")
        
        location = input(f"Location [{bike.location}]: ").strip()
        if location:
            bike.location = location
        
        # Save updated bikes
        BikeRentalSystem.save_bikes(bikes)
        
        print(f"\n✅ Bike {bike_id} updated successfully!")
    
    def delete_bike(self):
        """Delete a bike from the system"""
        print("\n" + "="*50)
        print("DELETE BIKE")
        print("="*50)
        
        bike_id = input("Enter Bike ID to delete: ").strip()
        
        bikes = BikeRentalSystem.load_bikes()
        bike = next((b for b in bikes if b.bike_id == bike_id), None)
        
        if not bike:
            print(f"No bike found with ID: {bike_id}")
            return
        
        print(f"\nBike to delete:")
        print(bike)
        
        confirm = input("\nAre you sure you want to delete this bike? (yes/no): ").lower()
        
        if confirm == 'yes':
            # Check if bike has active bookings
            bookings = BikeRentalSystem.load_bookings()
            active_bookings = [b for b in bookings if b.bike_id == bike_id 
                              and b.status in ["Pending", "Approved"]]
            
            if active_bookings:
                print(f"Cannot delete bike. It has {len(active_bookings)} active booking(s).")
                return
            
            # Remove bike
            bikes = [b for b in bikes if b.bike_id != bike_id]
            BikeRentalSystem.save_bikes(bikes)
            
            print(f"\n✅ Bike {bike_id} deleted successfully!")
        else:
            print("Deletion cancelled.")
    
    def view_all_bookings(self):
        """View all bookings in the system"""
        bookings = BikeRentalSystem.load_bookings()
        
        print("\n" + "="*50)
        print("ALL BOOKINGS")
        print("="*50)
        
        if not bookings:
            print("No bookings in the system.")
            return
        
        for booking in bookings:
            print("\n" + "-"*50)
            print(booking)
            print("-"*50)
        
        print(f"\nTotal bookings: {len(bookings)}")
    
    def manage_bookings(self):
        """Approve or reject pending bookings"""
        print("\n" + "="*50)
        print("MANAGE BOOKINGS")
        print("="*50)
        
        # Get pending bookings
        bookings = BikeRentalSystem.load_bookings()
        pending_bookings = [b for b in bookings if b.status == "Pending"]
        
        if not pending_bookings:
            print("No pending bookings.")
            return
        
        print("\nPENDING BOOKINGS:")
        for i, booking in enumerate(pending_bookings, 1):
            print(f"\n{i}. {booking.booking_id} - Customer: {booking.customer_username}")
            print(f"   Bike ID: {booking.bike_id} | Amount: ${booking.total_amount:.2f}")
        
        try:
            choice = int(input("\nSelect booking number to manage (0 to cancel): "))
            
            if choice == 0:
                return
            
            if 1 <= choice <= len(pending_bookings):
                selected_booking = pending_bookings[choice - 1]
                
                print(f"\nBooking Details:")
                print(selected_booking)
                
                print("\nSelect action:")
                print("1. Approve")
                print("2. Reject")
                print("3. Cancel")
                
                action = input("\nEnter action (1-3): ")
                
                if action == '1':
                    selected_booking.status = "Approved"
                    BikeRentalSystem.save_bookings(bookings)
                    print(f"\n✅ Booking {selected_booking.booking_id} approved!")
                elif action == '2':
                    selected_booking.status = "Rejected"
                    
                    # Make bike available again
                    bikes = BikeRentalSystem.load_bikes()
                    for bike in bikes:
                        if bike.bike_id == selected_booking.bike_id:
                            bike.available = True
                            break
                    
                    BikeRentalSystem.save_all_data({'bikes': bikes, 'bookings': bookings})
                    print(f"\n❌ Booking {selected_booking.booking_id} rejected!")
                else:
                    print("Action cancelled.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    def view_all_customers(self):
        """View all registered customers"""
        customers = BikeRentalSystem.load_users()
        customer_list = [c for c in customers if c.user_type == "customer"]
        
        print("\n" + "="*50)
        print("ALL CUSTOMERS")
        print("="*50)
        
        if not customer_list:
            print("No registered customers.")
            return
        
        for customer in customer_list:
            print(f"\nUsername: {customer.username}")
            print(f"Name: {getattr(customer, 'name', 'N/A')}")
            print(f"Phone: {getattr(customer, 'phone', 'N/A')}")
            print(f"Email: {getattr(customer, 'email', 'N/A')}")
        
        print(f"\nTotal customers: {len(customer_list)}")

# ==================== MAIN SYSTEM CLASS ====================
class BikeRentalSystem:
    """Main system class to manage the bike rental system"""
    
    # File paths for data storage
    USERS_FILE = "users.json"
    BIKES_FILE = "bikes.json"
    BOOKINGS_FILE = "bookings.json"
    
    @staticmethod
    def initialize_files():
        """Initialize data files if they don't exist"""
        files = [BikeRentalSystem.USERS_FILE, 
                BikeRentalSystem.BIKES_FILE, 
                BikeRentalSystem.BOOKINGS_FILE]
        
        for file in files:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    json.dump([], f)
        
        # Create default admin if no users exist
        users = BikeRentalSystem.load_users()
        if not users:
            admin = Admin("admin", "admin123")
            users.append(admin)
            BikeRentalSystem.save_users(users)
            
            # Add some sample bikes for demo
            sample_bikes = [
                Bike("BIKE0001", "Yamaha R15", "Blue", "MH01AB1234", 25.0, "Downtown", True),
                Bike("BIKE0002", "Royal Enfield Classic 350", "Black", "MH02CD5678", 35.0, "Uptown", True),
                Bike("BIKE0003", "Honda CB Shine", "Red", "MH03EF9012", 20.0, "Suburbs", True),
                Bike("BIKE0004", "Bajaj Pulsar 150", "White", "MH04GH3456", 22.0, "Downtown", True),
                Bike("BIKE0005", "KTM Duke 200", "Orange", "MH05IJ7890", 30.0, "Uptown", True)
            ]
            BikeRentalSystem.save_bikes(sample_bikes)
    
    @staticmethod
    def load_users() -> List[User]:
        """Load users from file"""
        try:
            with open(BikeRentalSystem.USERS_FILE, 'r') as f:
                users_data = json.load(f)
            
            users = []
            for user_data in users_data:
                if user_data['user_type'] == 'admin':
                    user = Admin(user_data['username'], user_data['password'])
                else:
                    user = Customer(
                        user_data['username'],
                        user_data['password'],
                        user_data.get('name', ''),
                        user_data.get('phone', ''),
                        user_data.get('email', '')
                    )
                users.append(user)
            return users
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    @staticmethod
    def save_users(users: List[User]):
        """Save users to file"""
        users_data = [user.to_dict() for user in users]
        with open(BikeRentalSystem.USERS_FILE, 'w') as f:
            json.dump(users_data, f, indent=2)
    
    @staticmethod
    def load_bikes() -> List[Bike]:
        """Load bikes from file"""
        try:
            with open(BikeRentalSystem.BIKES_FILE, 'r') as f:
                bikes_data = json.load(f)
            return [Bike.from_dict(bike_data) for bike_data in bikes_data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    @staticmethod
    def save_bikes(bikes: List[Bike]):
        """Save bikes to file"""
        bikes_data = [bike.to_dict() for bike in bikes]
        with open(BikeRentalSystem.BIKES_FILE, 'w') as f:
            json.dump(bikes_data, f, indent=2)
    
    @staticmethod
    def load_bookings() -> List[Booking]:
        """Load bookings from file"""
        try:
            with open(BikeRentalSystem.BOOKINGS_FILE, 'r') as f:
                bookings_data = json.load(f)
            return [Booking.from_dict(booking_data) for booking_data in bookings_data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    @staticmethod
    def save_booking(booking: Booking):
        """Save a single booking to file"""
        bookings = BikeRentalSystem.load_bookings()
        bookings.append(booking)
        
        bookings_data = [b.to_dict() for b in bookings]
        with open(BikeRentalSystem.BOOKINGS_FILE, 'w') as f:
            json.dump(bookings_data, f, indent=2)
    
    @staticmethod
    def save_bookings(bookings: List[Booking]):
        """Save bookings list to file"""
        bookings_data = [b.to_dict() for b in bookings]
        with open(BikeRentalSystem.BOOKINGS_FILE, 'w') as f:
            json.dump(bookings_data, f, indent=2)
    
    @staticmethod
    def save_all_data(data_dict: Dict):
        """Save multiple data types at once"""
        if 'bikes' in data_dict:
            BikeRentalSystem.save_bikes(data_dict['bikes'])
        if 'bookings' in data_dict:
            BikeRentalSystem.save_bookings(data_dict['bookings'])
    
    @staticmethod
    def register_customer():
        """Register a new customer"""
        print("\n" + "="*50)
        print("CUSTOMER REGISTRATION")
        print("="*50)
        
        username = input("Enter username: ").strip()
        
        # Check if username exists
        users = BikeRentalSystem.load_users()
        if any(user.username == username for user in users):
            print("Username already exists. Please choose another.")
            return None
        
        password = input("Enter password: ").strip()
        name = input("Enter your name: ").strip()
        phone = input("Enter phone number: ").strip()
        email = input("Enter email: ").strip()
        
        customer = Customer(username, password, name, phone, email)
        users.append(customer)
        BikeRentalSystem.save_users(users)
        
        print(f"\n✅ Registration successful! Welcome {name}!")
        return customer
    
    @staticmethod
    def login():
        """Login user"""
        print("\n" + "="*50)
        print("LOGIN")
        print("="*50)
        
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        users = BikeRentalSystem.load_users()
        for user in users:
            if user.username == username and user.password == password:
                print(f"\n✅ Login successful! Welcome {username}!")
                return user
        
        print("\n❌ Invalid username or password.")
        return None
    
    @staticmethod
    def run():
        """Main system loop"""
        print("\n" + "="*50)
        print("BIKE RENTAL SYSTEM")
        print("="*50)
        
        # Initialize data files
        BikeRentalSystem.initialize_files()
        
        while True:
            print("\nMAIN MENU")
            print("1. Login")
            print("2. Register (Customer)")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == '1':
                user = BikeRentalSystem.login()
                if user:
                    user.display_menu()
            elif choice == '2':
                customer = BikeRentalSystem.register_customer()
                if customer:
                    customer.display_menu()
            elif choice == '3':
                print("\nThank you for using Bike Rental System. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    # Run the bike rental system
    BikeRentalSystem.run()