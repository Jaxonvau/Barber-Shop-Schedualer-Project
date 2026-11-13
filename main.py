from dataclasses import dataclass
from drafter import *
from bakery import assert_equal

set_website_title("Oleo Gentlemen’s Salon")
set_site_information(
    author="Jaxon Vaughan",
    description="schedual an apointment to get your hair cut.",
    sources="Thanks to the oleo gentalmans salon.",
    planning=["FinalProject.py", "Barber.pdf"],
    links=["https://github.com/Jaxonvau/Barber-Shop-Schedualer-project"]
)
hide_debug_information()
set_website_framed(False)

@dataclass
class Appointment:
    """this is the appointment class"""
    customer_name: str
    barber: str
    date: str
    time: str


@dataclass
class State:
    customer_names: str
    selected_barber: str
    selected_date: str
    appointments: list[Appointment]
    selected_time: str
    selected_appointment: int
    message: str



times = ["9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM", "1:00 PM", "1:30 PM", "2:00 PM", "2:30 PM"]


def available(appointments: list[Appointment], barber: str, date: str, time: str, skip: int) -> bool:
    """this checks whether an appointment uses thie same time chosen."""
    for i in range(len(appointments)):
        appointment = appointments[i]
        if i != skip:
            if appointment.barber == barber and appointment.date == date and appointment.time == time:
                return False
    return True


def update_appointment(appointments: list[Appointment], number: int, date: str, time: str) -> list[Appointment]:
    """this returns a list that has the changed appointment."""
    new_list = []
    for i in range(len(appointments)):
        appointment = appointments[i]
        if i == number:
            new_list.append(Appointment(appointment.customer_name, appointment.barber, date, time))
        else:
            new_list.append(appointment)
    return new_list


@route
def index(state: State) -> Page:
    """home page"""
    return Page(state, ["Welcome to Oleo Gentlemen's Salon", state.message, Button("Book Appointment", book_appointment), Button("Manage Appointment", manage)])


@route
def book_appointment(state: State) -> Page:
    """barber selection"""
    state.message = ""
    state.customer_names = ""
    state.selected_date = ""
    return Page(state, ["Select your barber:", SelectBox("barber", ["Jostin", "Julien", "Blue", "Jose", "Elizabeth"]), Button("Continue", book), Button("Back to Home", index)])


@route
def book(state: State, barber: str) -> Page:
    """this is the booking information"""
    state.selected_barber = barber
    return Page(state, ["Barber: " + barber, "Name:", TextBox("name"), "Date:", TextBox("date", kind="date"), "Time:", SelectBox("time", times), Button("Check Availability", check_if_available), Button("Back to Home", index)])


@route
def check_if_available(state: State, name: str, date: str, time: str) -> Page:
    if name.strip() == "" or date == "":
        state.message = "Please enter your name and date."
        return index(state)

    if not available(state.appointments, state.selected_barber, date, time, -1):
        state.message = "That time is taken. Please choose another time."
        return index(state)

    state.customer_names = name.strip()
    state.selected_date = date
    state.selected_time = time

    return Page(state, [
        "Is this appointment correct?",
        "Name: " + state.customer_names,
        "Barber: " + state.selected_barber,
        "Date: " + date,
        "Time: " + time,
        Button("Confirm", confirm),
        Button("Start Over", book_appointment)
    ])


@route
def confirm(state: State) -> Page:
    """save the appointment"""
    if state.customer_names == "" or state.selected_date == "":
        state.message = "Please fill out the booking form first."
        return index(state)
    if not available(state.appointments, state.selected_barber,
                     state.selected_date, state.selected_time, -1):
        state.message = "That appointment time is already booked."
        return index(state)
    state.appointments.append(Appointment(state.customer_names,
        state.selected_barber, state.selected_date, state.selected_time))
    state.message = "Your appointment is booked!"
    return index(state)


@route
def manage(state: State) -> Page:
    """look for an appointment by name"""
    state.selected_appointment = -1
    return Page(state, ["Enter your name:", TextBox("name"), Button("Find Appointment", find), Button("Back to Home", index)])


@route
def find(state: State, name: str) -> Page:
    """this lists the appointments for this customer"""
    content: list = ["Your appointments:"]
    numbers = []
    for i in range(len(state.appointments)):
        appointment = state.appointments[i]
        if appointment.customer_name.lower() == name.strip().lower():
            numbers.append(str(i + 1))
            content.append(str(i + 1) + ": " + appointment.barber + " - " + appointment.date + " - " + appointment.time)
    if len(numbers) == 0:
        state.message = "No appointment found for that name."
        return index(state)
    content.append("Choose the appointment number:")
    content.append(SelectBox("number", numbers))
    content.append(Button("Manage This Appointment", reschedule))
    content.append(Button("Back to Home", index))
    return Page(state, content)


@route
def reschedule(state: State, number: str) -> Page:
    """show the appointment that will be changed"""
    if not number.isdigit():
        return manage(state)
    if int(number) < 1 or int(number) > len(state.appointments):
        return manage(state)
    state.selected_appointment = int(number) - 1
    appointment = state.appointments[state.selected_appointment]
    return Page(state, ["Name: " + appointment.customer_name, "Barber: " + appointment.barber, "Date:", TextBox("date", appointment.date, kind="date"), "Time:", SelectBox("time", times, appointment.time), Button("Reschedule", save_changes), Button("Cancel Appointment", cancel), Button("Back to Home", index)])


@route
def save_changes(state: State, date: str, time: str) -> Page:
    """save the new date and time if they are available"""
    number = state.selected_appointment
    if number < 0 or number >= len(state.appointments):
        return manage(state)
    if date == "":
        state.message = "Please enter a date. Your appointment has not changed."
        return index(state)
    appointment = state.appointments[number]
    if not available(state.appointments, appointment.barber, date, time, number):
        state.message = "That time is taken. Your appointment has not changed."
        return index(state)
    state.appointments = update_appointment(state.appointments, number, date, time)
    state.selected_appointment = -1
    state.message = "Your appointment has been rescheduled."
    return index(state)


@route
def cancel(state: State) -> Page:
    """this removes the selected appointment"""
    number = state.selected_appointment
    if number < 0 or number >= len(state.appointments):
        return manage(state)
    new_list = []
    for i in range(len(state.appointments)):
        if i != number:
            new_list.append(state.appointments[i])
    state.appointments = new_list
    state.selected_appointment = -1
    state.message = "Your appointment has been canceled."
    return index(state)

# unit tests
test_appointments = [Appointment("Alex", "Jostin", "2026-12-01", "9:00 AM")]
assert_equal(available(test_appointments, "Jostin", "2026-12-01", "9:00 AM", -1), False)
assert_equal(available(test_appointments, "Julien", "2026-12-01", "9:00 AM", -1), True)
assert_equal(available(test_appointments, "Jostin", "2026-12-01", "9:00 AM", 0), True)
assert_equal(update_appointment(test_appointments, 0, "2026-12-02", "10:00 AM"), [Appointment("Alex", "Jostin", "2026-12-02", "10:00 AM")])

start_server(State(
    customer_names="",
    selected_barber="Jostin",
    selected_date="",
    appointments=[],
    selected_time="9:00 AM",
    selected_appointment=-1,
    message=""
))






