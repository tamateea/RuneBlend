from typing import List
from curve_interp_type import get_interp_type_for_id

class CurvePoint:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.field2 = 0
        self.field3 = 0
        self.field4 = 0
        self.field5 = 0
        self.next = None

    def decode(self, buffer, version):
        self.x = buffer.read_short()
        self.y = buffer.read_float()
        self.field2 = buffer.read_float()
        self.field3 = buffer.read_float()
        self.field4 = buffer.read_float()
        self.field5 = buffer.read_float()


class Curve:
    def __init__(self, id):
        self.id = id
        self.type = 0
        self.start_interp_type = None
        self.end_interp_type = None
        self.bool = False
        self.points = []
        self.start_tick = 0
        self.end_tick = 0
        self.values = []
        self.min_value = 0
        self.max_value = 0
        self.no_interp = False
        self.point_index = 0
        self.point_index_updated = True
        self.interp_bool = False
        self.interp_v0 = 0
        self.interp_v1 = 0
        self.interp_v2 = 0
        self.interp_v3 = 0
        self.interp_v4 = 0
        self.interp_v5 = 0
        self.interp_v6 = 0
        self.interp_v7 = 0
        self.interp_v8 = 0
        self.interp_v9 = 0

    def decode(self, buffer, version):
        count = buffer.read_unsigned_short()
        self.type = buffer.read_unsigned_byte()
        self.start_interp_type = get_interp_type_for_id(buffer.read_unsigned_byte())
        self.end_interp_type = get_interp_type_for_id(buffer.read_unsigned_byte())
        self.bool = buffer.read_unsigned_byte() != 0#isTimeInterpolate

        self.points = [CurvePoint() for _ in range(count)]
        last_point = None
        for i in range(count):
            point = CurvePoint()
            point.decode(buffer, version)
            self.points[i] = point
            if last_point:
                last_point.next = point
            last_point = point

    def load(self):
        if not self.points:
            return

        self.start_tick = self.points[0].x
        self.end_tick = self.points[-1].x
        self.values = [0.0] * (self.get_tick_duration() + 1)

        for t in range(self.start_tick, self.end_tick + 1):
            self.values[t - self.start_tick] = interpolate_curve(self, t)

        self.points = None
        self.min_value = interpolate_curve(self, self.start_tick - 1)
        self.max_value = interpolate_curve(self, self.end_tick + 1)

    def get_value(self, t):
        if t < self.start_tick:
            return self.min_value
        elif t > self.end_tick:
            return self.max_value
        else:
            return self.values[t - self.start_tick]

    def get_curve_index2(self, t):
        if not self.points:
            return self.point_index
        if (
                0 <= self.point_index < len(self.points) and
                self.points[self.point_index].x <= t and
                (not self.points[self.point_index].next or self.points[self.point_index].next.x <= t)
        ):
            return self.point_index
        if t < self.start_tick or t > self.end_tick:
            return -1

        point_count = len(self.points)
        new_curve_index = self.point_index
        if point_count > 0:
            start_point_index = 0
            end_point_index = point_count - 1

            while start_point_index <= end_point_index:
                point_index = (start_point_index + end_point_index) >> 1
                if t < self.points[point_index].x:
                    if t > self.points[point_index - 1].x:
                        new_curve_index = point_index - 1
                        break
                    end_point_index = point_index - 1
                else:
                    if t <= self.points[point_index].x:
                        new_curve_index = point_index
                        break
                    if t < self.points[point_index + 1].x:
                        new_curve_index = point_index
                        break
                    start_point_index = point_index + 1

        if self.point_index != new_curve_index:
            self.point_index = new_curve_index
            self.point_index_updated = True

        return self.point_index

    def get_point_index(self, t):
        if not self.points:
            return self.point_index
        if (
                self.point_index < 0 or
                not (self.points[self.point_index].x <= t) or
                (self.points[self.point_index].next and self.points[self.point_index].next.x <= t)
        ):
            if self.start_tick <= t <= self.end_tick:
                point_count = len(self.points)
                new_point_index = self.point_index
                if point_count > 0:
                    start_point_index = 0
                    end_point_index = point_count - 1

                    while start_point_index <= end_point_index:
                        point_index = (start_point_index + end_point_index) >> 1
                        if t < self.points[point_index].x:
                            if t > self.points[point_index - 1].x:
                                new_point_index = point_index - 1
                                break
                            end_point_index = point_index - 1
                        else:
                            if t <= self.points[point_index].x:
                                new_point_index = point_index
                                break
                            if t < self.points[point_index + 1].x:
                                new_point_index = point_index
                                break
                            start_point_index = point_index + 1

                    if self.point_index != new_point_index:
                        self.point_index = new_point_index
                        self.point_index_updated = True

                return self.point_index
            else:
                return -1
        else:
            return self.point_index

    def get_curve_point(self, t):
        if not self.points:
            return None
        index = self.get_point_index(t)
        if 0 <= index < len(self.points):
            return self.points[index]
        return None

    def get_point_count(self):
        if self.points:
            return len(self.points)
        return 0

    def get_tick_duration(self):
        return self.end_tick - self.start_tick

