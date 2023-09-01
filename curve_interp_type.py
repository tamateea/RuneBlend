from enum import Enum


class CurveInterpType(Enum):
    TYPE_0 = 0
    TYPE_1 = 1
    TYPE_2 = 2
    TYPE_3 = 3
    TYPE_4 = 4


def get_interp_type_for_id(interp_id):
    if interp_id < 0 or interp_id > CurveInterpType.TYPE_4.value:
        return CurveInterpType.TYPE_0
    return CurveInterpType(interp_id)
