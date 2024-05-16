from sqlalchemy.orm import Session

from models import *

with Session(engine) as session:
    # -- users --
    radin = User(name="radin")
    ali = User(name="ali")
    mohsen = User(name="mohsen")
    # -- rooms --
    room_1 = Room(link="opefoweofkwpo", video_hash="123", status=STATUS.OPEN)
    room_2 = Room(link="453t5fqpojftg", video_hash="456", status=STATUS.OPEN)
    # -- connections --
    connection_1 = Connection(user=radin, room=room_1, type=TYPES.OWNER)
    connection_2 = Connection(user=ali, room=room_1, type=TYPES.CLIENT)
    connection_3 = Connection(user=mohsen, room=room_1, type=TYPES.CLIENT)
    connection_4 = Connection(user=ali, room=room_2, type=TYPES.OWNER)
    connection_5 = Connection(user=mohsen, room=room_2, type=TYPES.CLIENT)
    print(connection_1)
    session.add_all(
        [radin, ali, mohsen,
         room_1, room_2,
         connection_1, connection_2, connection_3,
         connection_4, connection_5]
    )
    session.commit()
