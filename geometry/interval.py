import sys

class Interval:
    def __init__(self, a=sys.float_info.max, b=-sys.float_info.max):
        self.a = a
        self.b = b

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

    def length(self):
        l = self.b-self.a
        if l < 0.0:
            return 0.0
        return l

    def middle(self):
        return (self.a+self.b)/2.0

    def offset(self, dist):
        self.a -= dist
        self.b += dist