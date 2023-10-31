import json

# JSONEncoder의 확장 클래스를 정의합니다.
# 이 클래스는 Python의 set 객체를 JSON으로 인코딩하기 위한 로직을 포함합니다.
class ExtendedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # obj가 set 객체의 인스턴스일 경우, JSON 표현을 반환합니다.
        # 여기에서는 "__set__": True를 통해 set 객체임을 표시하고,
        # set의 원소들을 "values" 키에 튜플로 저장합니다.
        if isinstance(obj, set):
            return {"__set__": True, "values": tuple(obj)}
        return obj

# JSONDecoder의 확장 클래스를 정의합니다.
# 이 클래스는 JSON으로 인코딩된 set 객체를 다시 Python의 set 객체로 디코딩하기 위한 로직을 포함합니다.
class ExtendedJSONDecoder(json.JSONDecoder):
    def __init__(self, **kwargs):
        # object_hook를 통해 _object_hook 메소드를 등록합니다.
        kwargs.setdefault("object_hook", self._object_hook)
        super().__init__(**kwargs)

    @staticmethod
    def _object_hook(dct):
        # "__set__" 키가 dct에 있으면, 해당 JSON 객체는 set 객체로 디코딩됩니다.
        # "values" 키에 저장된 튜플을 Python의 set으로 변환합니다.
        if '__set__' in dct:
            return set(dct['values'])
        return dct
