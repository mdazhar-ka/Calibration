# src/evaluate_calibration.py
import cv2
import numpy as np
import glob
import os

# --- Configurations (Match your setup) ---
CHECKERBOARD = (8, 6)  # Target inner vertices (height, width)
output_dir = 'Intrinsic\\data\\raw_images'
FRAME_SIZE = (1920, 1080)  # Explicitly defined to prevent scoping bugs

# Prepare object points based on your grid dimension
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[1], 0:CHECKERBOARD[0]].T.reshape(-1, 2)

objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

# UPDATED: Matches your actual file naming convention
images = sorted(glob.glob(os.path.join(output_dir, 'Capture_for_calib_*.jpg')))
valid_images = []

print(f"Found {len(images)} total images matching pattern in '{output_dir}'.")
print("Extracting corners...")

for fname in images:
    img = cv2.imread(fname)
    if img is None:
        continue
    gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray_frame, (CHECKERBOARD[1], CHECKERBOARD[0]), None)
    
    if ret:
        objpoints.append(objp)
        # Refine subpixel accuracy
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners2 = cv2.cornerSubPix(gray_frame, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
        valid_images.append(fname)
    else:
        print(f"❌ Could not find chessboard corners in: {os.path.basename(fname)}")

if len(valid_images) == 0:
    print("\nError: Chessboard corners could not be extracted from any image.")
    print("Verify that your grid matches the config: 6 rows and 9 columns of INNER corners.")
    exit()

# Initial global calibration using fixed frame sizes
print(f"\nComputing global calibration parameters using {len(valid_images)} frames...")
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, FRAME_SIZE, None, None)

print(f"\nOverall Global RMS Error: {ret:.4f} pixels")
print("\n--- Per-Frame Reprojection Error Analysis ---")

errors = []
for i in range(len(valid_images)):
    # Project the 3D object points back onto the 2D image plane
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    
    # Reshape both arrays to identical (N, 2) dimensions for a clean matrix subtraction
    p_extracted = imgpoints[i].reshape(-1, 2)
    p_projected = imgpoints2.reshape(-1, 2)
    
    # Calculate the Root Mean Square (RMS) error for this specific frame
    error = np.sqrt(np.mean(np.sum((p_extracted - p_projected) ** 2, axis=1)))
    errors.append((valid_images[i], error))

# Sort images by their error contribution (highest error first)
errors.sort(key=lambda x: x[1], reverse=True)

for rank, (name, err) in enumerate(errors, 1):
    status = "⚠️ OUTLIER (Delete)" if rank <= 3 else "✅ GOOD"
    print(f"[{rank:02d}] {os.path.basename(name)} -> Error: {err:.4f} pixels | {status}")