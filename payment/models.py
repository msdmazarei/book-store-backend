from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, Float, String, JSON, Boolean
from sqlalchemy.orm import relationship

from accounts.models import Account
from user.models import Person
from db_session import Base, PrimaryModel

class Payment(Base,PrimaryModel):
    __tablename__ = 'payments'
    person_id = Column(UUID,ForeignKey(Person.id))
    amount = Column(Float,nullable=False)
    shopping_key = Column(String)
    reference_code = Column(String)
    details = Column(JSON)
    order_details = Column(JSON)
    agent = Column(String)
    used = Column(Boolean,default=False)
    status = Column(String)


class CheckoutPressAccount(Base,PrimaryModel):
    __tablename__ = 'checkout_press_accounts'
    amount = Column(Float,nullable=False)
    payer_id = Column(UUID,ForeignKey(Person.id),nullable=False)
    receiver_id = Column(UUID,ForeignKey(Person.id),nullable=False)
    receiver_account_id = Column(UUID,ForeignKey(Account.id))
    payment_details = Column(JSON)

    receiver = relationship(Person, primaryjoin=receiver_id == Person.id , lazy=True)
