import cv2
import numpy as np
import argparse
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise

class HorizonStabilizer:
    def __init__(self, camera_matrix=None, dist_coeffs=None, fov=105):
        """
        Initialize the stabilizer.
        camera_matrix: 3x3 camera intrinsic matrix
        dist_coeffs: distortion coefficients
        fov: field of view in degrees
        """
        if camera_matrix is None:
            # Assume default for 105° FOV, resolution 1920x1080
            fx = 1920 / (2 * np.tan(np.radians(fov/2)))
            fy = fx
            cx, cy = 960, 540
            self.camera_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float32)
        else:
            self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs if dist_coeffs is not None else np.zeros(5)

        # Kalman filter for roll angle
        self.kf = KalmanFilter(dim_x=2, dim_z=1)  # state: [angle, angular_velocity]
        self.kf.x = np.array([0., 0.])  # initial state
        self.kf.F = np.array([[1., 1.], [0., 1.]])  # state transition
        self.kf.H = np.array([[1., 0.]])  # measurement
        self.kf.P *= 1000.  # covariance
        self.kf.R = 5  # measurement noise
        self.kf.Q = Q_discrete_white_noise(dim=2, dt=1, var=0.1)  # process noise

        self.prev_time = 0

    def undistort_frame(self, frame):
        """Undistort the frame using camera parameters."""
        h, w = frame.shape[:2]
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(self.camera_matrix, self.dist_coeffs, (w, h), 1, (w, h))
        undistorted = cv2.undistort(frame, self.camera_matrix, self.dist_coeffs, None, new_camera_matrix)
        return undistorted

    def detect_horizon(self, frame):
        """
        Improved horizon detection using probabilistic Hough transform.
        Returns angle in degrees or None.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=100, maxLineGap=10)

        if lines is not None:
            candidates = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(y2 - y1) < 50:  # Nearly horizontal
                    angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                    if abs(angle) < 45:  # Within reasonable range
                        candidates.append(angle)
            if candidates:
                # Use median to reduce outliers
                return np.median(candidates)
        return None

    def update_imu(self, roll, pitch, yaw, timestamp):
        """Update with IMU data. Returns predicted angle."""
        dt = timestamp - self.prev_time if self.prev_time else 0.033  # assume 30fps
        self.prev_time = timestamp
        self.kf.F[0,1] = dt
        self.kf.predict()
        self.kf.update(roll)  # measure roll
        return self.kf.x[0]

    def fuse_data(self, imu_angle, visual_angle, confidence=0.5):
        """Fuse IMU and visual data."""
        if visual_angle is not None:
            # Weighted fusion
            fused = (1 - confidence) * imu_angle + confidence * visual_angle
        else:
            fused = imu_angle
        return fused

    def stabilize_frame(self, frame, correction_angle):
        """Apply stabilization."""
        height, width = frame.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, correction_angle, 1.0)
        stabilized = cv2.warpAffine(frame, rotation_matrix, (width, height))
        return stabilized

    def process_frame(self, frame, imu_data, timestamp):
        """Process a single frame: undistort, detect, fuse, stabilize."""
        undistorted = self.undistort_frame(frame)
        visual_angle = self.detect_horizon(undistorted)
        imu_angle = self.update_imu(imu_data[0], imu_data[1], imu_data[2], timestamp)  # roll, pitch, yaw
        correction_angle = self.fuse_data(imu_angle, visual_angle)
        stabilized = self.stabilize_frame(undistorted, -correction_angle)
        return stabilized, correction_angle

def simulate_imu(frame_count, dt=0.033):
    """Simulate IMU data."""
    roll = 5 * np.sin(frame_count * 0.1 * dt)
    pitch = 3 * np.cos(frame_count * 0.05 * dt)
    yaw = 0
    return roll, pitch, yaw

def main(video_path, output_path=None):
    stabilizer = HorizonStabilizer()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video")
        return

    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_count = 0
    start_time = cv2.getTickCount() / cv2.getTickFrequency()
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        timestamp = cv2.getTickCount() / cv2.getTickFrequency() - start_time
        imu_data = simulate_imu(frame_count, 1/fps if 'fps' in locals() else 0.033)
        stabilized, correction = stabilizer.process_frame(frame, imu_data, timestamp)

        cv2.imshow('Stabilized', stabilized)
        if output_path:
            out.write(stabilized)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frame_count += 1

    cap.release()
    if output_path:
        out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Horizon Stabilization Module')
    parser.add_argument('--video', required=True, help='Path to input video')
    parser.add_argument('--output', help='Path to output stabilized video')
    args = parser.parse_args()
    main(args.video, args.output)