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

    def interpolate(self, t):
        """Return a position inside the interval 
           which interpolates between a and b.  i.e.
           If t==0 then return a
           If t==1 then return b
           If 0<t<1 then return a value inside the interval
        """
        return (1.0-t)*self.a + t*self.b

    def offset(self, dist):
        self.a -= dist
        self.b += dist