from datetime import date
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import List  ### New import
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+mysqlconnector://{os.environ.get('DB_PW')}@localhost/mechanic_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Create a base class for our models
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)  # Instantiate your SQLAlchemy database
db.init_app(app)  # adding our db extension to our app


service_mechanics = db.Table(
    "service_mechanics",
    Base.metadata,
    db.Column("service_id", db.ForeignKey("service_tickets.id")),
    db.Column("mechanic_id", db.ForeignKey("mechanics.id")),
)


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(250), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(15), nullable=False)

    service_tickets: Mapped[List["Service_Ticket"]] = db.relationship(
        back_populates="customer"
    )


class Service_Ticket(Base):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(db.String(17), nullable=False, unique=True)
    service_date: Mapped[date] = mapped_column(db.Date)
    service_desc: Mapped[str] = mapped_column(db.String(500), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customers.id"))

    customer: Mapped["Customer"] = db.relationship(back_populates="service_tickets")
    mechanics: Mapped[List["Mechanic"]] = db.relationship(
        secondary=service_mechanics, back_populates="service_tickets"
    )


class Mechanic(Base):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(250), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(15), nullable=False)
    salary: Mapped[float] = mapped_column(db.Float, nullable=False)

    service_tickets: Mapped[List["Service_Ticket"]] = db.relationship(
        secondary=service_mechanics, back_populates="mechanics"
    )


with app.app_context():
    db.create_all()


app.run()
