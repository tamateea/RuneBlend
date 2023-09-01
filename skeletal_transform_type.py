from enum import Enum


class SkeletalTransformType(Enum):
    TYPE_0 = 0
    BONE = 1
    TYPE_2 = 2
    TYPE_3 = 3
    ALPHA = 4
    TYPE_5 = 5



def get_transform_type_for_id(transform_type):
    if transform_type < 0 or transform_type > SkeletalTransformType.TYPE_5.value:
        return SkeletalTransformType.TYPE_0
    return SkeletalTransformType(transform_type)


CURVE_COUNTS = [0, 9, 3, 6, 1, 3]


def get_curve_count(transform_type):
    return CURVE_COUNTS[transform_type]
