import sys


class Interval:
    def __init__(self, a=sys.float_info.max, b=-sys.float_info.max):
        if a == sys.float_info.max or a < b:
            self.a = a
            self.b = b
        else:
            self.a = b
            self.b = a

    def invalid(self):
        """
        An invalid interval is uninitialized.
        It can be thought of as an intervale containing 
        no points
        """
        return self.b < self.a

    def encompass_interval(self, interval):
        if self.a > interval.a:
            self.a = interval.a
        if self.b < interval.b:
            self.b = interval.b

    def encompass_value(self, value):
        if self.a > value:
            self.a = value
        if self.b < value:
            self.b = value

    def contains_value(self, value):
        assert not self.invalid(), "Invalid interval"
        return self.a <= value and value <= self.b

    def contains_interval(self, interval):
        assert not self.invalid(), "Invalid interval"
        assert self.a <= self.b
        assert interval.a <= interval.b
        return self.a <= interval.a and interval.b <= self.b

    def length(self):
        assert not self.invalid()
        l = self.b - self.a
        if l < 0.0:
            return 0.0
        return l

    def middle(self):
        assert not self.invalid()
        return (self.a + self.b) / 2.0

    def interpolate(self, t):
        """Return a position inside the interval 
           which interpolates between a and b.  i.e.
           If t==0 then return a
           If t==1 then return b
           If 0<t<1 then return a value inside the interval
        """
        assert not self.invalid()
        return (1.0 - t) * self.a + t * self.b

    def offset(self, dist):
        assert not self.invalid()
        self.a -= dist
        self.b += dist
