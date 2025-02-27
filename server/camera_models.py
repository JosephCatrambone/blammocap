import math
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

    @classmethod
    def from_fov(cls, fov: float, resolution_x: int, resolution_y: int):
        aspect_ratio = resolution_x/resolution_y
        return cls(focal_x=aspect_ratio*math.tan(fov))

    def to_matrix(self):
        return numpy.array([[self.focal_x, 0, self.image_width/-2.0], [0.0, self.focal_y, self.image_height/-2.0], [0.0, 0.0, 1.0]])


@dataclass
class CameraExtrinsics:
    left: numpy.array
    up: numpy.array
    forward: numpy.array
    camera_position: numpy.array

    @classmethod
    def from_lookat(cls, eye, lookat, up):
        """
        # Eye is the camera position.  Lookat is the point upon which the camera is focusing.  Up is the global world-up.
        # -z is forward.  +y is up.  +x is right.
        # +z is backward.  -y is down.  -x is left.
        rev_camera_direction = numpy.array(eye) - numpy.array(lookat)
        norm_rev_camera_direction = normalize(rev_camera_direction)
        camera_right = normalize(numpy.cross(up, norm_rev_camera_direction))  # Represents +x in camera space.
        camera_up = numpy.cross(norm_rev_camera_direction, camera_right)
        return cls(left=-camera_right, up=camera_up, forward=norm_rev_camera_direction, camera_position=rev_camera_direction)
        """
        eye = numpy.array(eye)
        forward = normalize(numpy.array(lookat) - eye)
        left = numpy.cross(forward, normalize(up))
        camera_up = numpy.cross(left, forward)
        return cls(left=left, up=camera_up, forward=forward, camera_position=eye)


    def to_matrix(self):
        """
        right = -self.left
        direction = self.forward
        basis_partial = numpy.eye(4)
        basis_partial[0,0:3] = right
        basis_partial[1,0:3] = self.up
        basis_partial[2,0:3] = direction
        translation_partial = numpy.eye(4)
        translation_partial[0:3,-1] = -self.camera_position
        return basis_partial @ translation_partial
        """
        partial = numpy.eye(4)
        partial[0, 0:3] = self.left
        partial[1, 0:3] = self.up
        partial[2, 0:3] = -self.forward
        partial[0:3, -1] = -self.camera_position
        return partial


@dataclass
class CameraModel:
    intrinsics: CameraIntrinsics
    extrinsics: CameraExtrinsics

    def transform_points(self, points):
        # Given a matrix of nx3, transform the points in accordance with the intrinsics and extrinsics.
        assert points.shape[1] == 3
        points = numpy.hstack((points, numpy.ones((points.shape[0], 1), dtype=points.dtype)))
        points = (self.extrinsics.to_matrix() @ points.T)[0:3,:].T
        points = self.intrinsics.to_matrix() @ points
        return points
        points /= points[:,2]
        return points[:,:2]
