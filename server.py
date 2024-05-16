import jwt
from datetime import datetime, timedelta
from re import match
from sqlalchemy.orm import Session
from uuid import uuid4
from websocket_server import WebsocketServer
from werkzeug.security import generate_password_hash, check_password_hash

from models import User, engine
from payload import Payload, Update, Error, verify

server = WebsocketServer("127.0.0.1", 2353)
username_pattern = r"^\w{5,16}$"
password_pattern = r"^\w{8,32}$"
SECRET_KEY = "OR5ewfOJPOA.85244oefoJOP"


def register(update: Update) -> str:
    default_payload = Payload(update=Update(action=update.action))

    match update.data:
        case {
            "username": str(username),
            "password": str(password),
        }:
            errors = [
                (username_pattern, username, "username not matched!"),
                (password_pattern, password, "password not matched!"),
            ]
            for pattern, text, error in errors:  # Pattern check
                if not match(pattern, text):
                    default_payload.error = Error(error)
                    return default_payload.gen

            with Session(engine) as session:
                if session.query(User).filter(User.name == username).first():  # Exist check
                    default_payload.error = Error("User already exists.")
                    return default_payload.gen

                new_user = User(
                    name=username,
                    password=generate_password_hash(password),
                    public_id=str(uuid4())
                )
                session.add(new_user), session.commit()

                default_payload.update.msg = "Successfully registered."
                return default_payload.gen

    default_payload.error.msg = "Internal Server Error!"
    return default_payload.gen


def login(update: Update) -> str:
    default_payload = Payload(update=Update(action=update.action))

    match update.data:
        case {
            "username": str(username),
            "password": str(password),
        }:
            with Session(engine) as session:
                if selected_user := session.query(User).filter(User.name == username).first():  # Exist check
                    if check_password_hash(selected_user.password, password):  # Password-hash check
                        token = jwt.encode({
                            'public_id': selected_user.public_id,  # public_id for identifying the user with jwt
                            'exp': datetime.utcnow() + timedelta(minutes=30)  # expire in 30min later
                        }, SECRET_KEY)
                        default_payload.update.msg = "Successfully login."
                        default_payload.update.data = {"token": token}
                    else:
                        default_payload.error = Error("Wrong Password!")
                else:
                    default_payload.error = Error("User already exists.")
                return default_payload.gen

    default_payload.error.msg = "Internal Server Error!"
    return default_payload.gen


def send_message(c, payload: str):
    return server.send_message(c, payload)


def on_message(c, s, msg):
    print(msg)
    match payload := verify(msg):
        case Payload(status=True):
            update = payload.update
            match update.action:
                case "Register":
                    return send_message(c, register(update))
                case "Login":
                    return send_message(c, login(update))


def new_client(c, s):
    send_message(c, Payload(update=Update(action="Introduce")).gen)


server.set_fn_new_client(new_client)
server.set_fn_message_received(on_message)

print("Server IS RUN")
server.run_forever()
