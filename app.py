from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change for production!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///busbooking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Bus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    seats_available = db.Column(db.Integer, default=40)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passenger_name = db.Column(db.String(100), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    seats_booked = db.Column(db.Integer, nullable=False)
    bus = db.relationship('Bus')

class BookingForm(FlaskForm):
    passenger_name = StringField('Your Name', validators=[DataRequired()])
    seats_booked = IntegerField('Number of Seats', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Book')

@app.before_first_request
def create_tables():
    db.create_all()
    if not Bus.query.first():
        buses = [
            Bus(name='Express Line', seats_available=40),
            Bus(name='City Shuttle', seats_available=30),
            Bus(name='Night Rider', seats_available=20)
        ]
        db.session.add_all(buses)
        db.session.commit()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/buses')
def view_buses():
    buses = Bus.query.all()
    return render_template('buses.html', buses=buses)

@app.route('/book/<int:bus_id>', methods=['GET', 'POST'])
def book_bus(bus_id):
    bus = Bus.query.get_or_404(bus_id)
    form = BookingForm()
    form.seats_booked.validators[1].max = bus.seats_available
    if form.validate_on_submit():
        seats = form.seats_booked.data
        if seats <= bus.seats_available:
            booking = Booking(
                passenger_name=form.passenger_name.data,
                bus_id=bus.id,
                seats_booked=seats
            )
            bus.seats_available -= seats
            db.session.add(booking)
            db.session.commit()
            flash('Booking successful!', 'success')
            return redirect(url_for('view_bookings'))
        else:
            flash('Not enough seats available.', 'danger')
    return render_template('book.html', bus=bus, form=form)

@app.route('/bookings')
def view_bookings():
    bookings = Booking.query.all()
    return render_template('bookings.html', bookings=bookings)

if __name__ == '__main__':
    app.run(debug=True)