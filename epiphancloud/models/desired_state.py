class DesiredState:
    def __init__(self, desired_state:dict):
        _type = desired_state.get('Type')
        _timestamp = desired_state.get('StateTime')
        self._params = desired_state.get('Params', {})

        if _type is None:
            raise Exception('DesiredState type is not defined')

        if _timestamp is None:
            raise Exception('DesiredState timestamp is not defined')

        self._type = _type
        self._timestamp = float(_timestamp)

    @property
    def type(self) -> str:
        return self._type

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def params(self) -> dict:
        return self._params
