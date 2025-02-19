import os
import pickle

import tkinter as tk
from tkinter import messagebox
import face_recognition


def get_button(window, text, color, command, fg='white'):
    button = tk.Button(
                        window,
                        text=text,
                        activebackground="black",
                        activeforeground="white",
                        fg=fg,
                        bg=color,
                        command=command,
                        height=2,
                        width=20,
                        font=('Helvetica bold', 20)
                    )

    return button


def get_img_label(window):
    label = tk.Label(window)
    label.grid(row=0, column=0)
    return label


def get_text_label(window, text):
    label = tk.Label(window, text=text)
    label.config(font=("sans-serif", 21), justify="left")
    return label


def get_entry_text(window):
    inputtxt = tk.Text(window,
                       height=2,
                       width=15, font=("Arial", 32))
    return inputtxt


def msg_box(title, description):
    messagebox.showinfo(title, description)


def recognize(image, db_dir):
    print("Starting recognition...")
    # Get the encoding of the current face
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        print("No face locations found")
        return 'no_persons_found'

    print(f"Found {len(face_locations)} faces")
    current_face_encoding = face_recognition.face_encodings(image, face_locations)[0]

    # Load all known face encodings from the database
    best_match_distance = float('inf')
    best_match_name = 'unknown_person'
    
    for filename in os.listdir(db_dir):
        print(f"Checking file: {filename}")
        if filename.endswith('.pickle'):
            with open(os.path.join(db_dir, filename), 'rb') as f:
                known_face_encoding = pickle.load(f)
                
                # Compare faces with distance
                face_distance = face_recognition.face_distance([known_face_encoding], current_face_encoding)[0]
                print(f"Face distance for {filename}: {face_distance}")
                
                # Lower threshold for stricter matching (0.5 instead of 0.6)
                if face_distance < 0.5 and face_distance < best_match_distance:
                    best_match_distance = face_distance
                    best_match_name = filename.replace('.pickle', '')

    print(f"Best match: {best_match_name} with distance: {best_match_distance}")
    return best_match_name

# Path to your project directory
project_dir = '/Users/blazee/Documents/Projects/Face Attendance'

# Database directory path
db_dir = os.path.join(project_dir, 'db')

# Log file path
log_path = os.path.join(project_dir, 'log.txt')

# Model directory path
model_dir = os.path.join(project_dir, 'resources', 'anti_spoof_models')