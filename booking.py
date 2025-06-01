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
    date_bookings = bookings[bookings["Date"] == date_str]

    # Block day if already has 6 bookings
    if len(date_bookings) >= MAX_TEAMS_PER_DAY:
        return []

    available = []
    for slot in all_slots:
        count = len(date_bookings[date_bookings["Time Slot"] == slot])
        if count < MAX_TEAMS_PER_SLOT:
            available.append(slot)
    return available

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
st.info("Each session is 2 hours. A school may book a maximum of 2 sessions on different days. "
        "Each time slot can hold up to 3 teams. Each day can host a maximum of 6 teams.")

school = st.text_input("School Name")
contact = st.text_input("Contact Email or Phone")

# Only show dates with availability
available_dates = get_dates_with_availability()

if not available_dates:
    st.error("❌ No available dates in the next 30 days.")
    st.stop()

date = st.selectbox("Choose an available date", available_dates)
available_slots = get_available_slots(str(date))

if not available_slots:
    st.warning("⚠ No slots left for this day. Please choose another date.")
    st.stop()

time_slot = st.selectbox("Choose a time slot", available_slots)

if st.button("Book This Slot"):
    bookings = load_bookings()
    school_bookings = bookings[bookings["School"] == school]

    # Check if the school already booked 2 times
    if len(school_bookings) >= SESSIONS_PER_SCHOOL:
        st.error(f"❌ {school} has already booked {SESSIONS_PER_SCHOOL} sessions.")
        st.stop()

    # Ensure school is not booking the same date twice
    if str(date) in school_bookings["Date"].values:
        st.error(f"❌ {school} has already booked a session on {date}. Please select a different day.")
        st.stop()

    # Check if the school is trying to double-book same time slot
    if ((school_bookings["Date"] == str(date)) & (school_bookings["Time Slot"] == time_slot)).any():
        st.error(f"❌ {school} has already booked this slot.")
        st.stop()

    new_booking = {
        "School": school,
        "Contact": contact,
        "Date": str(date),
        "Time Slot": time_slot
    }
    save_booking(new_booking)
    st.success(f"✅ Booking confirmed for {school} on {date} at {time_slot}.")
