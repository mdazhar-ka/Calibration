import cv2
import time

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Wait 2 seconds for hardware to initialize
time.sleep(2)

# Enable Autofocus (1 = On, 0 = Off)
success = cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)

if success:
    print("Autofocus successfully enabled via OpenCV!")
else:
    # If False, the camera is using OS defaults or doesn't support software toggle
    print("OpenCV command sent. Verifying hardware state...")

# Print the active state (1.0 means Autofocus is enabled)
print(f"Current Autofocus State: {cap.get(cv2.CAP_PROP_AUTOFOCUS)}")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow('Autofocus Video Feed', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
