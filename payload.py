from json import dumps, loads

from json.decoder import JSONDecodeError


class Update:
    def __init__(self, data: dict = None, action: str = None, msg: str = None):
        self.data = data
        self.action = action
        self.msg = msg

    @property
    def gen(self):
        return {"data": self.data, "action": self.action, "msg": self.msg}

    def __repr__(self):
        return f"{self.__class__.__name__}(data={self.data!r}, action={self.action!r}, msg={self.msg!r})"


class Error:
    def __init__(self, msg: str = None):
        self.msg = msg

    @property
    def gen(self):
        return {"msg": self.msg}

    def __repr__(self):
        return f"{self.__class__.__name__}(msg={self.msg!r})"


class Payload:
    def __init__(self, status: bool = True, update: Update = None, error: Error = None):
        self.status: bool = status
        self.update: Update | None = update
        self.error: Error | None = error

    @property
    def gen(self):
        result = {"status": self.status, "update": self.update.gen}
        if self.error:
            result["status"] = False
            result.update({"error": self.error.gen})
        return dumps(result)

    def __repr__(self):
        return f"{self.__class__.__name__}(update={self.update!r}, error={self.error!r})"


def verify(payload: str) -> Payload:
    try:
        tmp_res = loads(payload)
    except JSONDecodeError:
        return Payload(status=True)

    match tmp_res:
        case {
            "status": True,
            "update": {
                "data": (dict() | None) as data,
                "action": (str() | None) as action,
                "msg": (str() | None) as update_msg,
            },
        }:
            return Payload(
                update=Update(data=data, action=action, msg=update_msg)
            )

        case {
            "status": False,
            "update": {
                "data": (dict() | None) as data,
                "action": (str() | None) as action,
                "msg": (str() | None) as update_msg,
            },
            "error": {
                "msg": (str() | None) as error_msg,
            }
        }:
            return Payload(
                update=Update(data=data, action=action, msg=update_msg),
                error=Error(msg=error_msg)
            )

        case _:
            return Payload(status=True)
