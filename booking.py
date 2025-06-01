import streamlit as st
import pandas as pd
import datetime

# Constants
DATA_FILE = "bookings.csv"
SESSIONS_PER_SCHOOL = 2
SESSION_LENGTH = 2
START_HOUR = 9
END_HOUR = 17
MAX_TEAMS_PER_SLOT = 3
MAX_TEAMS_PER_DAY = 6

# Load or initialize booking data
def load_bookings():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["School", "Contact", "Date", "Time Slot"])

def save_booking(new_booking):
    bookings = load_bookings()
    new_df = pd.DataFrame([new_booking])
    bookings = pd.concat([bookings, new_df], ignore_index=True)
    bookings.to_csv(DATA_FILE, index=False)

def get_all_slots():
    return [f"{hour}:00 - {hour + SESSION_LENGTH}:00" for hour in range(START_HOUR, END_HOUR, SESSION_LENGTH)]

def get_available_slots(date_str):
    all_slots = get_all_slots()
    bookings = load_bookings()
    bookings_on_date = bookings[bookings["Date"] == date_str]

    # Don't allow booking if day already has max teams
    if len(bookings_on_date) >= MAX_TEAMS_PER_DAY:
        return []

    available_slots = []
    for slot in all_slots:
        slot_count = len(bookings_on_date[bookings_on_date["Time Slot"] == slot])
        if slot_count < MAX_TEAMS_PER_SLOT:
            available_slots.append(slot)
    return available_slots

def get_dates_with_availability(days_ahead=30):
    today = datetime.date.today()
    dates = []
    for i in range(days_ahead):
        day = today + datetime.timedelta(days=i)
        if get_available_slots(str(day)):
            dates.append(day)
    return dates

# App UI
st.title("🎓 School Training Slot Booking")
st.info("Each session is 2 hours. A school may book a maximum of 2 sessions on **different days**. Each slot allows up to 3 teams. A day can host a maximum of 6 teams.")

school = st.text_input("School Name")
contact = st.text_input("Contact Email or Phone")

if not school or not contact:
    st.warning("Please enter your school name and contact to proceed.")
    st.stop()

bookings = load_bookings()
school_bookings = bookings[bookings["School"] == school]

# Prevent booking more than 2 sessions
if len(school_bookings) >= SESSIONS_PER_SCHOOL:
    st.error(f"{school} has already booked the maximum of {SESSIONS_PER_SCHOOL} sessions.")
    st.stop()

# Get dates with available slots AND not already booked by the same school
available_dates = [
    date for date in get_dates_with_availability()
    if str(date) not in school_bookings["Date"].tolist()
]

if not available_dates:
    st.error("No eligible dates available (either fully booked or already booked by your school).")
    st.stop()

date = st.selectbox("Choose an available date", available_dates)
available_slots = get_available_slots(str(date))

# Remove slots already booked by the same school on that date
already_booked_slots = school_bookings[school_bookings["Date"] == str(date)]["Time Slot"].tolist()
available_slots = [slot for slot in available_slots if slot not in already_booked_slots]

if not available_slots:
    st.warning("No available time slots for this day.")
    st.stop()

time_slot = st.selectbox("Choose a time slot", available_slots)

if st.button("Book This Slot"):
    # Double-check again
    if str(date) in school_bookings["Date"].tolist():
        st.error("Your school has already booked a session on this date.")
    elif len(school_bookings) >= SESSIONS_PER_SCHOOL:
        st.error(f"{school} has already booked {SESSIONS_PER_SCHOOL} sessions.")
    elif time_slot in already_booked_slots:
        st.error("Your school has already booked this time slot.")
    else:
        new_booking = {
            "School": school,
            "Contact": contact,
            "Date": str(date),
            "Time Slot": time_slot
        }
        save_booking(new_booking)
        st.success(f"✅ Booking confirmed for {date} at {time_slot}!")
