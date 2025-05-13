import cv2
from pyzbar import pyzbar
import webbrowser
from datetime import datetime
import os
import winsound  # For Windows beep sound (use alternative for Linux/Mac)

# Open webcam (use 0 for default camera)
cap = cv2.VideoCapture(0)

# Create daily log file
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
file_path = os.path.join(log_dir, f"scanned_codes_{datetime.now().strftime('%Y-%m-%d')}.txt")
file = open(file_path, "a")

scanned_codes = set()  # Track already scanned codes

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    codes = pyzbar.decode(gray)  # Detect QR codes and barcodes

    for code in codes:
        code_data = code.data.decode('utf-8')
        code_type = code.type

        if code_data not in scanned_codes:
            scanned_codes.add(code_data)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"[{timestamp}] {code_type}: {code_data}\n")
            file.flush()

            print(f"[{timestamp}] {code_type} detected: {code_data}")
            winsound.Beep(1000, 150)  # Beep sound on scan

            # Smart handling of known formats
            if code_data.startswith(("http://", "https://")):
                webbrowser.open(code_data)
            elif code_data.startswith("upi://"):
                print("UPI link detected! Open this QR code on a mobile device with Google Pay or PhonePe.")
            else:
                print(f"{code_type} detected. Code is: {code_data}")

        # Draw bounding box and label
        (x, y, w, h) = code.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 200, 0), 2)
        label = f"{code_type}: {code_data}"
        cv2.putText(frame, label, (x, y - 12), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 200, 0), 2)

    cv2.imshow("Live QR & Barcode Scanner", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
file.close()
cap.release()
cv2.destroyAllWindows()
