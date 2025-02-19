import os
import datetime
import pickle

import tkinter as tk
import cv2
from PIL import Image, ImageTk
import face_recognition

import util
from face_test import test


class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")
        
        # Change the main window title
        self.main_window.title("Face Attendance System")

        self.login_button_main_window = util.get_button(self.main_window, 'login', 'green', self.login)
        self.login_button_main_window.place(x=750, y=200)

        self.logout_button_main_window = util.get_button(self.main_window, 'logout', 'red', self.logout)
        self.logout_button_main_window.place(x=750, y=300)

        self.register_new_user_button_main_window = util.get_button(self.main_window, 'register new user', 'gray',
                                                                    self.register_new_user, fg='black')
        self.register_new_user_button_main_window.place(x=750, y=400)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)

        self.db_dir = '/Users/blazee/Documents/Projects/Face Attendance/db'  # Corrected path
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.log_path = '/Users/blazee/Documents/Projects/Face Attendance/log.txt'  # Corrected path

        self.current_user = None  # Add this line to track current user

    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(1)

        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()

        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(20, self.process_webcam)

    def login(self):
        print("Starting login process...")
        if self.most_recent_capture_arr is None or self.most_recent_capture_arr.size == 0:
            print("No image captured")
            util.msg_box('Error', 'No image captured. Please check your webcam.')
            return

        # Check if there are any faces in the captured image
        face_locations = face_recognition.face_locations(self.most_recent_capture_arr)
        print(f"Face locations: {face_locations}")
        
        if not face_locations:
            util.msg_box('Error', 'No face detected. Please try again.')
            return
        
        if len(face_locations) > 1:
            util.msg_box('Error', 'Multiple faces detected. Please ensure only one person is in the frame.')
            return

        print("About to recognize...")
        name = util.recognize(self.most_recent_capture_arr, self.db_dir)
        print(f"Recognition result: {name}")

        if name in ['unknown_person', 'no_persons_found']:
            util.msg_box('Access Denied', 'This user is not registered in the system. Please register first.')
        else:
            util.msg_box('Login Successful', f'Welcome, {name}! You have successfully logged in.')
            with open(self.log_path, 'a') as f:
                f.write(f'{name},{datetime.datetime.now()},in\n')
            self.current_user = name

    def logout(self):
        if hasattr(self, 'current_user') and self.current_user:
            util.msg_box('Logout Successful', f'Goodbye, {self.current_user}! You have been logged out.')
            with open(self.log_path, 'a') as f:
                f.write(f'{self.current_user},{datetime.datetime.now()},out\n')
            self.current_user = None
        else:
            util.msg_box('Error', 'No user is currently logged in.')

    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520+370+120")
        
        # Change the registration window title
        self.register_new_user_window.title("Face Attendance System - New User Registration")

        self.accept_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Accept', 'green', self.accept_register_new_user)
        self.accept_button_register_new_user_window.place(x=750, y=300)

        self.try_again_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Try again', 'red', self.try_again_register_new_user)
        self.try_again_button_register_new_user_window.place(x=750, y=400)

        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label(self.capture_label)

        self.entry_text_register_new_user = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user.place(x=750, y=150)

        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window, 'Please, \ninput username:')
        self.text_label_register_new_user.place(x=750, y=70)

    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def start(self):
        self.main_window.mainloop()

    def accept_register_new_user(self):
        name = self.entry_text_register_new_user.get(1.0, "end-1c").strip()
        
        if not name:
            util.msg_box('Error', 'Please enter a username')
            return

        # Check if user already exists
        if os.path.exists(os.path.join(self.db_dir, f'{name}.pickle')):
            util.msg_box('Error', 'This username is already registered. Please choose a different name.')
            return

        # Check if there are any faces in the captured image
        if self.register_new_user_capture is None:
            util.msg_box('Error', 'Please capture an image first')
            return

        face_locations = face_recognition.face_locations(self.register_new_user_capture)
        if not face_locations:
            util.msg_box('Error', 'No face detected. Please try again.')
            return

        if len(face_locations) > 1:
            util.msg_box('Error', 'Multiple faces detected. Please ensure only one person is in the frame.')
            return

        try:
            embeddings = face_recognition.face_encodings(self.register_new_user_capture)[0]
            
            with open(os.path.join(self.db_dir, f'{name}.pickle'), 'wb') as file:
                pickle.dump(embeddings, file)

            util.msg_box('Registration Successful', f'New user {name} has been registered successfully!')
            self.register_new_user_window.destroy()
        except Exception as e:
            util.msg_box('Error', f'Failed to register user: {str(e)}')

    def login_window(self):
        self.login_window = tk.Toplevel(self.main_window)
        self.login_window.geometry("1200x520+370+120")
        
        # Change the login window title
        self.login_window.title("Face Attendance System - Login")

        # ... existing code ...


if __name__ == "__main__":
    app = App()
    app.start()