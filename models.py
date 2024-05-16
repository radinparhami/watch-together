# WARNING!
# ❌ don't use session as a global variable like this example:
#       session = Session(engine)
#       with session as s: ...
# ✅ use this syntax always:
#       with Session(engine) as s: ...


from sqlalchemy import Column, Integer, String, SmallInteger, ForeignKey, create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, relationship, MappedColumn
from sqlalchemy.orm.exc import DetachedInstanceError

engine = create_engine(
    f'mysql://root:@localhost/watch_together?charset=utf8mb4',
    future=True, pool_pre_ping=True, pool_recycle=280,
)
try:
    engine.connect()
except OperationalError:
    print("Connection to MySQL failed")
    print(f"Address: {engine.url}")
    exit(-1)


# with engine.connect() as connection:
#     connection.execute('SET max_allowed_packet=67108864;')
class BaseModel(DeclarativeBase):

    def __repr__(self) -> str:
        return self._repr(id=self.id)

    def _repr(self, **fields) -> str:
        '''
        Helper for __repr__
        '''
        field_strings = []
        at_least_one_attached_attribute = False
        for key, field in fields.items():
            try:
                field_strings.append(f'{key}={field!r}')
            except DetachedInstanceError:
                field_strings.append(f'{key}=DetachedInstanceError')
            else:
                at_least_one_attached_attribute = True
        if at_least_one_attached_attribute:
            return f"{self.__class__.__name__}({', '.join(field_strings)})"
        return f"<{self.__class__.__name__} {id(self)}>"


class User(BaseModel):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False, unique=True)
    password = Column(String(162), nullable=False)
    public_id = Column(String(36), nullable=False, unique=True)

    connections = relationship("Connection", back_populates="user")

    def __repr__(self):
        return self._repr(id=self.id, name=self.name, password=self.password, public_id=self.public_id)


class Type(BaseModel):
    __tablename__ = 'type'
    id = Column(SmallInteger, primary_key=True)
    name = Column(String(16), unique=True, nullable=False)

    def __repr__(self):
        return self._repr(id=self.id, name=self.name)


class Status(BaseModel):
    __tablename__ = 'status'
    id = Column(SmallInteger, primary_key=True)
    name = Column(String(16), unique=True, nullable=False)

    def __repr__(self):
        return self._repr(id=self.id, name=self.name)


class Room(BaseModel):
    __tablename__ = 'room'
    id: MappedColumn = Column(Integer, primary_key=True)
    link: MappedColumn = Column(String(32), nullable=False)
    video_hash: MappedColumn = Column(String(32), nullable=False)

    status_id: MappedColumn = Column(SmallInteger, ForeignKey('status.id'), nullable=False)
    status = relationship("Status")

    connections = relationship("Connection", back_populates="room")

    def __repr__(self):
        return self._repr(id=self.id, link=self.link, video_hash=self.video_hash, status=self.status)


class Connection(BaseModel):
    __tablename__ = 'connections'
    id: MappedColumn = Column(Integer, primary_key=True)

    user_id: MappedColumn = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="connections")

    room_id: MappedColumn = Column(Integer, ForeignKey("room.id"), nullable=False)
    room = relationship("Room", back_populates="connections")

    type_id: MappedColumn = Column(SmallInteger, ForeignKey('type.id'), nullable=False)
    type = relationship("Type")

    def __repr__(self):
        return self._repr(id=self.id, user=self.user, room=self.room, type=self.type)


#  -- Load All STATIC DATAS --
class TYPES:
    OWNER = Type(name='owner')
    CLIENT = Type(name='client')
    ALL = ["OWNER", "CLIENT"]


class STATUS:
    CLOSED = Status(name='closed')
    OPEN = Status(name='open')
    ALL = ["CLOSED", "OPEN"]


if __name__ == "__main__":
    inp = input("Do ypu wanna drop_all? [Y/N]: ")
    if inp.lower() == "y":
        BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)

# for type_name in TYPES.ALL:
#     tn = TYPES().__getattribute__(type_name)
#     with Session(engine) as s:
#         if not s.query(Type).filter_by(name=tn.name).first():
#             s.add(tn), s.commit()
#
# for state in STATUS.ALL:
#     st = STATUS().__getattribute__(state)
#     with Session(engine) as s:
#         if not s.query(Status).filter_by(name=st.name).first():
#             s.add(st), s.commit()
