import rel
import websocket

from payload import verify, Payload, Update

login_data = {
    "username": "radin",
    "password": "13851385"
}


def on_message(s, msg):
    print(msg)
    match payload := verify(msg):
        case Payload(status=True):
            update = payload.update
            match update.action:
                case "Introduce":
                    s.send(Payload(update=Update(login_data, "Register")).gen)
                case "Register":
                    s.send(Payload(update=Update(login_data, "Login")).gen)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws):
    print("Opened connection")


if __name__ == "__main__":
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "ws://127.0.0.1:2353",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever(dispatcher=rel, reconnect=5)
    rel.signal(2, rel.abort)
    rel.dispatch()
