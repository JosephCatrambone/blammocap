import numpy
from dataclasses import dataclass


def normalize(c):
    magnitude = numpy.dot(c, c)**0.5
    return c/magnitude


@dataclass
class CameraIntrinsics:
    image_width: int
    image_height: int
    focal_x: float
    focal_y: float

    def to_matrix(self):
        return numpy.array([[self.focal_x, 0, self.image_width/2.0], [0.0, self.focal_y, self.image_height/2.0], [0.0, 0.0, 1.0]])


@dataclass
class CameraExtrinsics:
    left: numpy.array
    up: numpy.array
    forward: numpy.array
    translation: numpy.array

    @classmethod
    def from_lookat(cls, eye, lookat, up):
        # -z is forward.  +y is up.  +x is right.
        # +z is backward.  -y is down.  -x is left.
        dt = numpy.array(lookat) - numpy.array(eye)
        forward = normalize(dt)
        left = normalize(numpy.cross(up, forward))
        #forward = normalize(numpy.cross(n, left))
        # Should dt be -eye dot left.x, up.x, forward.x, -eye dot left.y, up.y, forward.y, -eye dot left.z, up.z, forward.z?
        return cls(left=left, up=up, forward=forward, translation=dt)
    
    def to_matrix(self):
        partial = numpy.vstack([self.left, self.up, self.forward, self.dt]).T
        return numpy.vstack([partial, [0.0, 0.0, 0.0, 1.0]])


@dataclass
class CameraModel:

