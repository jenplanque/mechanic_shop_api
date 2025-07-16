from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List
from sqlalchemy import Numeric, Column, Integer


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)  # Instantiate SQLAlchemy database


# Define association tables BEFORE models
service_mechanics = db.Table(
    "service_mechanics",
    Base.metadata,
    db.Column("service_id", db.ForeignKey("service_tickets.id")),
    db.Column("mechanic_id", db.ForeignKey("mechanics.id")),
)

service_inventory = db.Table(
    "service_inventory",
    Base.metadata,
    # db.Model.metadata,
    db.Column("service_id", db.ForeignKey("service_tickets.id")),
    db.Column("item_id", db.ForeignKey("inventory_items.id")),
)


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(250), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(15), nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)

    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(
        back_populates="customer", cascade="all, delete"
    )  # removes associated service tickets when a customer is deleted


class ServiceTicket(Base):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(db.String(17), nullable=False)
    service_date: Mapped[date] = mapped_column(db.Date)
    service_desc: Mapped[str] = mapped_column(db.String(500), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customers.id"))

    customer: Mapped["Customer"] = db.relationship(
        "Customer", back_populates="service_tickets"
    )
    mechanics: Mapped[List["Mechanic"]] = db.relationship(
        "Mechanic", secondary=service_mechanics, back_populates="service_tickets"
    )

    inventory_items: Mapped[List["InventoryItem"]] = db.relationship(
        "InventoryItem", secondary=service_inventory, back_populates="service_tickets"
    )


class Mechanic(Base):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(250), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(15), nullable=False)
    salary: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(
        secondary=service_mechanics, back_populates="mechanics"
    )


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Float(), nullable=False)
    # price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    # item_desc: Mapped[str] = mapped_column(db.String(500), nullable=False)

    # Define association table for InventoryItem and ServiceTicket
    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(
        "ServiceTicket", secondary=service_inventory, back_populates="inventory_items"
    )
