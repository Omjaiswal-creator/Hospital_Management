import mysql.connector
from mysql.connector import Error
import re
import datetime
import getpass
import os
import time
from tabulate import tabulate
import colorama
from colorama import Fore, Style

class HospitalManagementSystem:
    def __init__(self):
        colorama.init()
        self.initialize_connection()
        
    def initialize_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='Your Password',
                database='Your database name'
            )
            self.cursor = self.connection.cursor(dictionary=True)
            self.setup_database()
        except Error as e:
            print(f"{Fore.RED}Database connection error: {e}{Style.RESET_ALL}")
            self.connection = None

    def setup_database(self):
        tables = [
            """CREATE TABLE IF NOT EXISTS patients (
                patient_id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                date_of_birth DATE NOT NULL,
                gender ENUM('Male', 'Female', 'Other') NOT NULL,
                contact_number VARCHAR(15) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                address TEXT,
                blood_group VARCHAR(5),
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS doctors (
                doctor_id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                specialization VARCHAR(100) NOT NULL,
                contact_number VARCHAR(15) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                department VARCHAR(100) NOT NULL,
                joining_date DATE NOT NULL,
                consultation_fee DECIMAL(10,2) NOT NULL
            )""",
            
            """CREATE TABLE IF NOT EXISTS appointments (
                appointment_id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT NOT NULL,
                doctor_id INT NOT NULL,
                appointment_date DATE NOT NULL,
                appointment_time TIME NOT NULL,
                status ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
                reason VARCHAR(255),
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS medical_records (
                record_id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT NOT NULL,
                doctor_id INT NOT NULL,
                diagnosis TEXT,
                prescription TEXT,
                treatment_plan TEXT,
                visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS billing (
                bill_id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                payment_status ENUM('Pending', 'Paid', 'Overdue') DEFAULT 'Pending',
                bill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
            )"""
        ]
        
        for table in tables:
            self.cursor.execute(table)
        self.connection.commit()

    def validate_email(self, email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None
    
    def validate_phone(self, phone):
        phone_regex = r'^\+?1?\d{10,14}$'
        return re.match(phone_regex, phone) is not None

    def display_loading(self, action):
        animation = "|/-\\"
        for i in range(10):
            time.sleep(0.1)
            print(f"{Fore.CYAN}\r{action} {animation[i % len(animation)]}", end="")
        print(f"\r{' ' * 50}", end="")
        print(f"\r{Fore.GREEN}{action} Complete!{Style.RESET_ALL}")

    def add_patient(self):
        try:
            self.clear_screen()
            print(f"\n{Fore.CYAN}=== Add New Patient ==={Style.RESET_ALL}")
            first_name = input(f"{Fore.YELLOW}First Name: {Style.RESET_ALL}")
            last_name = input(f"{Fore.YELLOW}Last Name: {Style.RESET_ALL}")
            
            while True:
                dob = input(f"{Fore.YELLOW}Date of Birth (YYYY-MM-DD): {Style.RESET_ALL}")
                try:
                    datetime.datetime.strptime(dob, '%Y-%m-%d')
                    break
                except ValueError:
                    print(f"{Fore.RED}Invalid date format. Use YYYY-MM-DD{Style.RESET_ALL}")
            
            gender = input(f"{Fore.YELLOW}Gender (Male/Female/Other): {Style.RESET_ALL}").capitalize()
            
            while True:
                contact_number = input(f"{Fore.YELLOW}Contact Number: {Style.RESET_ALL}")
                if self.validate_phone(contact_number):
                    break
                print(f"{Fore.RED}Invalid phone number.{Style.RESET_ALL}")
            
            while True:
                email = input(f"{Fore.YELLOW}Email Address: {Style.RESET_ALL}")
                if self.validate_email(email):
                    break
                print(f"{Fore.RED}Invalid email address.{Style.RESET_ALL}")
            
            address = input(f"{Fore.YELLOW}Home Address: {Style.RESET_ALL}")
            blood_group = input(f"{Fore.YELLOW}Blood Group: {Style.RESET_ALL}")
            
            query = """
            INSERT INTO patients 
            (first_name, last_name, date_of_birth, gender, 
            contact_number, email, address, blood_group) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (first_name, last_name, dob, gender, 
                      contact_number, email, address, blood_group)
            
            self.display_loading("Registering patient")
            self.cursor.execute(query, params)
            self.connection.commit()
            
            patient_id = self.cursor.lastrowid
            print(f"{Fore.GREEN}Patient registration successful! Patient ID: {patient_id}{Style.RESET_ALL}")
            time.sleep(1)
        
        except Error as e:
            print(f"{Fore.RED}Registration failed: {e}{Style.RESET_ALL}")
            self.connection.rollback()

    def add_doctor(self):
        try:
            self.clear_screen()
            print(f"\n{Fore.CYAN}=== Add New Doctor ==={Style.RESET_ALL}")
            first_name = input(f"{Fore.YELLOW}First Name: {Style.RESET_ALL}")
            last_name = input(f"{Fore.YELLOW}Last Name: {Style.RESET_ALL}")
            specialization = input(f"{Fore.YELLOW}Medical Specialization: {Style.RESET_ALL}")
            
            while True:
                contact_number = input(f"{Fore.YELLOW}Contact Number: {Style.RESET_ALL}")
                if self.validate_phone(contact_number):
                    break
                print(f"{Fore.RED}Invalid phone number.{Style.RESET_ALL}")
            
            while True:
                email = input(f"{Fore.YELLOW}Email Address: {Style.RESET_ALL}")
                if self.validate_email(email):
                    break
                print(f"{Fore.RED}Invalid email address.{Style.RESET_ALL}")
            
            department = input(f"{Fore.YELLOW}Department: {Style.RESET_ALL}")
            
            while True:
                try:
                    consultation_fee = float(input(f"{Fore.YELLOW}Consultation Fee: {Style.RESET_ALL}"))
                    break
                except ValueError:
                    print(f"{Fore.RED}Invalid fee amount.{Style.RESET_ALL}")
            
            while True:
                joining_date = input(f"{Fore.YELLOW}Joining Date (YYYY-MM-DD): {Style.RESET_ALL}")
                try:
                    datetime.datetime.strptime(joining_date, '%Y-%m-%d')
                    break
                except ValueError:
                    print(f"{Fore.RED}Invalid date format.{Style.RESET_ALL}")
            
            query = """
            INSERT INTO doctors 
            (first_name, last_name, specialization, contact_number, 
            email, department, joining_date, consultation_fee) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (first_name, last_name, specialization, 
                      contact_number, email, department, joining_date, consultation_fee)
            
            self.display_loading("Registering doctor")
            self.cursor.execute(query, params)
            self.connection.commit()
            
            doctor_id = self.cursor.lastrowid
            print(f"{Fore.GREEN}Doctor registration successful! Doctor ID: {doctor_id}{Style.RESET_ALL}")
            time.sleep(1)
        
        except Error as e:
            print(f"{Fore.RED}Registration failed: {e}{Style.RESET_ALL}")
            self.connection.rollback()

    def book_appointment(self):
        try:
            self.clear_screen()
            print(f"\n{Fore.CYAN}=== Book Appointment ==={Style.RESET_ALL}")
            
            patient_id = input(f"{Fore.YELLOW}Enter Patient ID: {Style.RESET_ALL}")
            self.cursor.execute("SELECT patient_id, first_name, last_name FROM patients WHERE patient_id = %s", (patient_id,))
            patient_result = self.cursor.fetchone()
            
            if not patient_result:
                print(f"{Fore.RED}Error: Patient ID {patient_id} does not exist. Please register the patient first.{Style.RESET_ALL}")
                time.sleep(2)
                return
            else:
                print(f"{Fore.GREEN}Patient: {patient_result['first_name']} {patient_result['last_name']}{Style.RESET_ALL}")
            
            doctor_id = input(f"{Fore.YELLOW}Enter Doctor ID: {Style.RESET_ALL}")
            self.cursor.execute("SELECT doctor_id, first_name, last_name, specialization FROM doctors WHERE doctor_id = %s", (doctor_id,))
            doctor_result = self.cursor.fetchone()
            
            if not doctor_result:
                print(f"{Fore.RED}Error: Doctor ID {doctor_id} does not exist. Please register the doctor first.{Style.RESET_ALL}")
                time.sleep(2)
                return
            else:
                print(f"{Fore.GREEN}Doctor: {doctor_result['first_name']} {doctor_result['last_name']} ({doctor_result['specialization']}){Style.RESET_ALL}")
            
            while True:
                appointment_date = input(f"{Fore.YELLOW}Appointment Date (YYYY-MM-DD): {Style.RESET_ALL}")
                try:
                    date_obj = datetime.datetime.strptime(appointment_date, '%Y-%m-%d')
                    if date_obj.date() < datetime.datetime.now().date():
                        print(f"{Fore.RED}Appointment date cannot be in the past.{Style.RESET_ALL}")
                        continue
                    break
                except ValueError:
                    print(f"{Fore.RED}Invalid date format. Use YYYY-MM-DD{Style.RESET_ALL}")
            
            while True:
                appointment_time = input(f"{Fore.YELLOW}Appointment Time (HH:MM): {Style.RESET_ALL}")
                try:
                    datetime.datetime.strptime(appointment_time, '%H:%M')
                    break
                except ValueError:
                    print(f"{Fore.RED}Invalid time format. Use HH:MM (24-hour format){Style.RESET_ALL}")
                    
            reason = input(f"{Fore.YELLOW}Reason for Visit: {Style.RESET_ALL}")
            
            query = """
            INSERT INTO appointments 
            (patient_id, doctor_id, appointment_date, appointment_time, reason) 
            VALUES (%s, %s, %s, %s, %s)
            """
            
            params = (patient_id, doctor_id, appointment_date, appointment_time, reason)
            
            self.display_loading("Booking appointment")
            self.cursor.execute(query, params)
            self.connection.commit()
            
            appointment_id = self.cursor.lastrowid
            print(f"{Fore.GREEN}Appointment booked successfully! Appointment ID: {appointment_id}{Style.RESET_ALL}")
            time.sleep(1)
        
        except Error as e:
            print(f"{Fore.RED}Booking failed: {e}{Style.RESET_ALL}")
            self.connection.rollback()

    def add_medical_record(self):
        try:
            self.clear_screen()
            print(f"\n{Fore.CYAN}=== Add Medical Record ==={Style.RESET_ALL}")
            
            patient_id = input(f"{Fore.YELLOW}Patient ID: {Style.RESET_ALL}")
            self.cursor.execute("SELECT patient_id, first_name, last_name FROM patients WHERE patient_id = %s", (patient_id,))
            patient_result = self.cursor.fetchone()
            
            if not patient_result:
                print(f"{Fore.RED}Error: Patient ID {patient_id} does not exist.{Style.RESET_ALL}")
                time.sleep(2)
                return
            else:
                print(f"{Fore.GREEN}Patient: {patient_result['first_name']} {patient_result['last_name']}{Style.RESET_ALL}")
            
            doctor_id = input(f"{Fore.YELLOW}Doctor ID: {Style.RESET_ALL}")
            self.cursor.execute("SELECT doctor_id, first_name, last_name, specialization FROM doctors WHERE doctor_id = %s", (doctor_id,))
            doctor_result = self.cursor.fetchone()
            
            if not doctor_result:
                print(f"{Fore.RED}Error: Doctor ID {doctor_id} does not exist.{Style.RESET_ALL}")
                time.sleep(2)
                return
            else:
                print(f"{Fore.GREEN}Doctor: {doctor_result['first_name']} {doctor_result['last_name']} ({doctor_result['specialization']}){Style.RESET_ALL}")
                
            diagnosis = input(f"{Fore.YELLOW}Diagnosis: {Style.RESET_ALL}")
            prescription = input(f"{Fore.YELLOW}Prescription: {Style.RESET_ALL}")
            treatment_plan = input(f"{Fore.YELLOW}Treatment Plan: {Style.RESET_ALL}")
            
            query = """
            INSERT INTO medical_records 
            (patient_id, doctor_id, diagnosis, prescription, treatment_plan) 
            VALUES (%s, %s, %s, %s, %s)
            """
            
            params = (patient_id, doctor_id, diagnosis, prescription, treatment_plan)
            
            self.display_loading("Adding medical record")
            self.cursor.execute(query, params)
            self.connection.commit()
            
            record_id = self.cursor.lastrowid
            print(f"{Fore.GREEN}Medical record added successfully! Record ID: {record_id}{Style.RESET_ALL}")
            time.sleep(1)
        
        except Error as e:
            print(f"{Fore.RED}Record addition failed: {e}{Style.RESET_ALL}")
            self.connection.rollback()

    def generate_bill(self):
        try:
            self.clear_screen()
            print(f"\n{Fore.CYAN}=== Generate Patient Bill ==={Style.RESET_ALL}")
            
            patient_id = input(f"{Fore.YELLOW}Patient ID: {Style.RESET_ALL}")
            self.cursor.execute("SELECT patient_id, first_name, last_name FROM patients WHERE patient_id = %s", (patient_id,))
            patient_result = self.cursor.fetchone()
            
            if not patient_result:
                print(f"{Fore.RED}Error: Patient ID {patient_id} does not exist.{Style.RESET_ALL}")
                time.sleep(2)
                return
            else:
                print(f"{Fore.GREEN}Patient: {patient_result['first_name']} {patient_result['last_name']}{Style.RESET_ALL}")
                
            while True:
                try:
                    total_amount = float(input(f"{Fore.YELLOW}Total Bill Amount: {Style.RESET_ALL}"))
                    break
                except ValueError:
                    print(f"{Fore.RED}Invalid amount.{Style.RESET_ALL}")
            
            payment_options = ['Pending', 'Paid', 'Overdue']
            print(f"{Fore.CYAN}Payment Status Options:{Style.RESET_ALL}")
            for i, option in enumerate(payment_options, 1):
                print(f"{i}. {option}")
            
            while True:
                try:
                    choice = int(input(f"{Fore.YELLOW}Select payment status (1-3): {Style.RESET_ALL}"))
                    if 1 <= choice <= 3:
                        payment_status = payment_options[choice-1]
                        break
                    else:
                        print(f"{Fore.RED}Invalid choice. Please select 1-3.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")
            
            query = """
            INSERT INTO billing 
            (patient_id, total_amount, payment_status) 
            VALUES (%s, %s, %s)
            """
            
            params = (patient_id, total_amount, payment_status)
            
            self.display_loading("Generating bill")
            self.cursor.execute(query, params)
            self.connection.commit()
            
            bill_id = self.cursor.lastrowid
            print(f"{Fore.GREEN}Bill generated successfully! Bill ID: {bill_id}{Style.RESET_ALL}")
            time.sleep(1)
            
            self.print_bill(bill_id, patient_result, total_amount, payment_status)
        
        except Error as e:
            print(f"{Fore.RED}Bill generation failed: {e}{Style.RESET_ALL}")
            self.connection.rollback()
    
    def print_bill(self, bill_id, patient, amount, status):
        print(f"\n{Fore.CYAN}{'=' * 50}")
        print(f"{' ' * 15}HOSPITAL BILL RECEIPT")
        print(f"{'=' * 50}{Style.RESET_ALL}")
        print(f"Bill ID: {bill_id}")
        print(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"Patient: {patient['first_name']} {patient['last_name']} (ID: {patient['patient_id']})")
        print(f"{Fore.CYAN}{'-' * 50}{Style.RESET_ALL}")
        print(f"Amount Due: ${amount:.2f}")
        print(f"Payment Status: {status}")
        print(f"{Fore.CYAN}{'-' * 50}")
        print(f"{'=' * 50}{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def view_patients(self):
        try:
            self.clear_screen()
            self.cursor.execute("SELECT * FROM patients")
            patients = self.cursor.fetchall()
            
            if not patients:
                print(f"{Fore.YELLOW}No patients found.{Style.RESET_ALL}")
                time.sleep(2)
                return
            
            print(f"\n{Fore.CYAN}=== Patient List ==={Style.RESET_ALL}")
            
            headers = ["ID", "Name", "Date of Birth", "Gender", "Contact", "Email", "Blood Group"]
            table_data = []
            
            for patient in patients:
                table_data.append([
                    patient['patient_id'],
                    f"{patient['first_name']} {patient['last_name']}",
                    patient['date_of_birth'],
                    patient['gender'],
                    patient['contact_number'],
                    patient['email'],
                    patient['blood_group'] or "N/A"
                ])
            
            print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        
        except Error as e:
            print(f"{Fore.RED}Error retrieving patients: {e}{Style.RESET_ALL}")
            time.sleep(2)
    
    def view_doctors(self):
        try:
            self.clear_screen()
            self.cursor.execute("SELECT * FROM doctors")
            doctors = self.cursor.fetchall()
            
            if not doctors:
                print(f"{Fore.YELLOW}No doctors found.{Style.RESET_ALL}")
                time.sleep(2)
                return
            
            print(f"\n{Fore.CYAN}=== Doctor List ==={Style.RESET_ALL}")
            
            headers = ["ID", "Name", "Specialization", "Department", "Contact", "Email", "Fee ($)"]
            table_data = []
            
            for doctor in doctors:
                table_data.append([
                    doctor['doctor_id'],
                    f"{doctor['first_name']} {doctor['last_name']}",
                    doctor['specialization'],
                    doctor['department'],
                    doctor['contact_number'],
                    doctor['email'],
                    f"{doctor['consultation_fee']:.2f}"
                ])
            
            print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        
        except Error as e:
            print(f"{Fore.RED}Error retrieving doctors: {e}{Style.RESET_ALL}")
            time.sleep(2)
    
    def view_appointments(self):
        try:
            self.clear_screen()
            query = """
            SELECT a.appointment_id, a.appointment_date, a.appointment_time, a.status, a.reason,
                   p.patient_id, CONCAT(p.first_name, ' ', p.last_name) as patient_name,
                   d.doctor_id, CONCAT(d.first_name, ' ', d.last_name) as doctor_name,
                   d.specialization
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN doctors d ON a.doctor_id = d.doctor_id
            ORDER BY a.appointment_date, a.appointment_time
            """
            
            self.cursor.execute(query)
            appointments = self.cursor.fetchall()
            
            if not appointments:
                print(f"{Fore.YELLOW}No appointments found.{Style.RESET_ALL}")
                time.sleep(2)
                return
            
            print(f"\n{Fore.CYAN}=== Appointment List ==={Style.RESET_ALL}")
            
            headers = ["ID", "Date", "Time", "Patient", "Doctor", "Status", "Reason"]
            table_data = []
            
            for appt in appointments:
                status_color = Fore.GREEN if appt['status'] == 'Completed' else (Fore.YELLOW if appt['status'] == 'Scheduled' else Fore.RED)
                table_data.append([
                    appt['appointment_id'],
                    appt['appointment_date'],
                    appt['appointment_time'],
                    f"{appt['patient_name']} (ID: {appt['patient_id']})",
                    f"{appt['doctor_name']} ({appt['specialization']})",
                    f"{status_color}{appt['status']}{Style.RESET_ALL}",
                    appt['reason']
                ])
            
            print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        
        except Error as e:
            print(f"{Fore.RED}Error retrieving appointments: {e}{Style.RESET_ALL}")
            time.sleep(2)
    
    def manage_appointments(self):
        try:
            self.clear_screen()
            print(f"\n{Fore.CYAN}=== Manage Appointments ==={Style.RESET_ALL}")
            
            appointment_id = input(f"{Fore.YELLOW}Enter Appointment ID: {Style.RESET_ALL}")
            
            self.cursor.execute("""
                SELECT a.*, 
                       CONCAT(p.first_name, ' ', p.last_name) as patient_name,
                       CONCAT(d.first_name, ' ', d.last_name) as doctor_name
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN doctors d ON a.doctor_id = d.doctor_id
                WHERE a.appointment_id = %s
            """, (appointment_id,))
            
            appointment = self.cursor.fetchone()
            
            if not appointment:
                print(f"{Fore.RED}Appointment not found.{Style.RESET_ALL}")
                time.sleep(2)
                return
            
            print(f"\n{Fore.CYAN}Appointment Details:{Style.RESET_ALL}")
            print(f"ID: {appointment['appointment_id']}")
            print(f"Date: {appointment['appointment_date']}")
            print(f"Time: {appointment['appointment_time']}")
            print(f"Patient: {appointment['patient_name']}")
            print(f"Doctor: {appointment['doctor_name']}")
            print(f"Status: {appointment['status']}")
            print(f"Reason: {appointment['reason']}")
            
            print(f"\n{Fore.CYAN}Update Options:{Style.RESET_ALL}")
            print("1. Update Status")
            print("2. Reschedule Appointment")
            print("3. Cancel Appointment")
            print("4. Back to Main Menu")
            
            choice = input(f"\n{Fore.YELLOW}Select an option (1-4): {Style.RESET_ALL}")
            
            if choice == '1':
                print(f"\n{Fore.CYAN}Status Options:{Style.RESET_ALL}")
                print("1. Scheduled")
                print("2. Completed")
                print("3. Cancelled")
                
                status_choice = input(f"{Fore.YELLOW}Select new status (1-3): {Style.RESET_ALL}")
                status_options = ['Scheduled', 'Completed', 'Cancelled']
                
                if status_choice in ['1', '2', '3']:
                    new_status = status_options[int(status_choice) - 1]
                    
                    self.cursor.execute(
                        "UPDATE appointments SET status = %s WHERE appointment_id = %s",
                        (new_status, appointment_id)
                    )
                    self.connection.commit()
                    print(f"{Fore.GREEN}Appointment status updated to {new_status}.{Style.RESET_ALL}")
                    time.sleep(1)
                else:
                    print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
            
            elif choice == '2':
                new_date = input(f"{Fore.YELLOW}New Date (YYYY-MM-DD): {Style.RESET_ALL}")
                new_time = input(f"{Fore.YELLOW}New Time (HH:MM): {Style.RESET_ALL}")
                
                try:
                    datetime.datetime.strptime(new_date, '%Y-%m-%d')
                    datetime.datetime.strptime(new_time, '%H:%M')
                    
                    self.cursor.execute(
                        "UPDATE appointments SET appointment_date = %s, appointment_time = %s WHERE appointment_id = %s",
                        (new_date, new_time, appointment_id)
                    )
                    self.connection.commit()
                    print(f"{Fore.GREEN}Appointment rescheduled to {new_date} at {new_time}.{Style.RESET_ALL}")
                    time.sleep(1)
                except ValueError:
                    print(f"{Fore.RED}Invalid date or time format.{Style.RESET_ALL}")
            
            elif choice == '3':
                confirm = input(f"{Fore.RED}Are you sure you want to cancel this appointment? (y/n): {Style.RESET_ALL}")
                if confirm.lower() == 'y':
                    self.cursor.execute(
                        "UPDATE appointments SET status = 'Cancelled' WHERE appointment_id = %s",
                        (appointment_id,)
                    )
                    self.connection.commit()
                    print(f"{Fore.GREEN}Appointment cancelled.{Style.RESET_ALL}")
                    time.sleep(1)
        
        except Error as e:
            print(f"{Fore.RED}Error managing appointment: {e}{Style.RESET_ALL}")
            self.connection.rollback()
            time.sleep(2)
    
    def view_medical_records(self):
        try:
            self.clear_screen()
            patient_id = input(f"{Fore.YELLOW}Enter Patient ID: {Style.RESET_ALL}")
            
            self.cursor.execute("SELECT patient_id, first_name, last_name FROM patients WHERE patient_id = %s", (patient_id,))
            patient = self.cursor.fetchone()
            
            if not patient:
                print(f"{Fore.RED}Patient not found.{Style.RESET_ALL}")
                time.sleep(2)
                return
            
            query = """
            SELECT mr.*, CONCAT(d.first_name, ' ', d.last_name) as doctor_name
            FROM medical_records mr
            JOIN doctors d ON mr.doctor_id = d.doctor_id
            WHERE mr.patient_id = %s
            ORDER BY mr.visit_date DESC
            """
            
            self.cursor.execute(query, (patient_id,))
            records = self.cursor.fetchall()
            
            if not records:
                print(f"{Fore.YELLOW}No medical records found for this patient.{Style.RESET_ALL}")
                time.sleep(2)
                return
            
            print(f"\n{Fore.CYAN}=== Medical Records for {patient['first_name']} {patient['last_name']} ==={Style.RESET_ALL}")
            
            for i, record in enumerate(records, 1):
                print(f"\n{Fore.CYAN}Record #{i} - {record['visit_date']}{Style.RESET_ALL}")
                print(f"Doctor: {record['doctor_name']}")
                print(f"Diagnosis: {record['diagnosis']}")
                print(f"Prescription: {record['prescription']}")
                print(f"Treatment Plan: {record['treatment_plan']}")
                print(f"{Fore.CYAN}{'-' * 50}{Style.RESET_ALL}")
            
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        
        except Error as e:
            print(f"{Fore.RED}Error retrieving medical records: {e}{Style.RESET_ALL}")
            time.sleep(2)
    
    def view_billing_history(self):
        try:
            self.clear_screen()
            patient_id = input(f"{Fore.YELLOW}Enter Patient ID: {Style.RESET_ALL}")
            
            self.cursor.execute("SELECT patient_id, first_name, last_name FROM patients WHERE patient_id = %s", (patient_id,))
            patient = self.cursor.fetchone()
            
            if not patient:
                print(f"{Fore.RED}Patient not found.{Style.RESET_ALL}")
                time.sleep(2)
                return
            
            query = """
            SELECT * FROM billing
            WHERE patient_id = %s
            ORDER BY bill_date DESC
            """
            
            self.cursor.execute(query, (patient_id,))
            bills = self.cursor.fetchall()
            
            if not bills:
                print(f"{Fore.YELLOW}No billing records found for this patient.{Style.RESET_ALL}")
                time.sleep(2)
                return
            
            print(f"\n{Fore.CYAN}=== Billing History for {patient['first_name']} {patient['last_name']} ==={Style.RESET_ALL}")
            
            headers = ["Bill ID", "Date", "Amount ($)", "Status"]
            table_data = []
            
            for bill in bills:
                status_color = Fore.GREEN if bill['payment_status'] == 'Paid' else (Fore.YELLOW if bill['payment_status'] == 'Pending' else Fore.RED)
                table_data.append([
                    bill['bill_id'],
                    bill['bill_date'],
                    f"{bill['total_amount']:.2f}",
                    f"{status_color}{bill['payment_status']}{Style.RESET_ALL}"
                ])
            
            print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        
        except Error as e:
            print(f"{Fore.RED}Error retrieving billing records: {e}{Style.RESET_ALL}")
            time.sleep(2)
    
    def update_patient(self):
        try:
            self.clear_screen()
            print(f"\n{Fore.CYAN}=== Update Patient Information ==={Style.RESET_ALL}")
            
            patient_id = input(f"{Fore.YELLOW}Enter Patient ID: {Style.RESET_ALL}")
            
            self.cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
            patient = self.cursor.fetchone()
            
            if not patient:
                print(f"{Fore.RED}Patient not found.{Style.RESET_ALL}")
                time.sleep(2)
                return
            
            print(f"\n{Fore.CYAN}Current Patient Information:{Style.RESET_ALL}")
            print(f"ID: {patient['patient_id']}")
            print(f"Name: {patient['first_name']} {patient['last_name']}")
            print(f"Date of Birth: {patient['date_of_birth']}")
            print(f"Gender: {patient['gender']}")
            print(f"Contact: {patient['contact_number']}")
            print(f"Email: {patient['email']}")
            print(f"Address: {patient['address']}")
            print(f"Blood Group: {patient['blood_group'] or 'N/A'}")
            
            print(f"\n{Fore.CYAN}Update Options:{Style.RESET_ALL}")
            print("1. Contact Number")
            print("2. Email Address")
            print("3. Home Address")
            print("4. Blood Group")
            print("5. Back to Main Menu")
            
            choice = input(f"\n{Fore.YELLOW}Select an option (1-5): {Style.RESET_ALL}")
            
            if choice == '1':
                while True:
                    new_contact = input(f"{Fore.YELLOW}New Contact Number: {Style.RESET_ALL}")
                    if self.validate_phone(new_contact):
                        break
                    print(f"{Fore.RED}Invalid phone number.{Style.RESET_ALL}")
                
                self.cursor.execute(
                    "UPDATE patients SET contact_number = %s WHERE patient_id = %s",
                    (new_contact, patient_id)
                )
                self.connection.commit()
                print(f"{Fore.GREEN}Contact number updated successfully.{Style.RESET_ALL}")
            
            elif choice == '2':
                while True:
                    new_email = input(f"{Fore.YELLOW}New Email Address: {Style.RESET_ALL}")
                    if self.validate_email(new_email):
                        break
                    print(f"{Fore.RED}Invalid email address.{Style.RESET_ALL}")
                
                self.cursor.execute(
                    "UPDATE patients SET email = %s WHERE patient_id = %s",
                    (new_email, patient_id)
                )
                self.connection.commit()
                print(f"{Fore.GREEN}Email address updated successfully.{Style.RESET_ALL}")
            
            elif choice == '3':
                new_address = input(f"{Fore.YELLOW}New Home Address: {Style.RESET_ALL}")
                
                self.cursor.execute(
                    "UPDATE patients SET address = %s WHERE patient_id = %s",
                    (new_address, patient_id)
                )
                self.connection.commit()
                print(f"{Fore.GREEN}Home address updated successfully.{Style.RESET_ALL}")
            
            elif choice == '4':
                new_blood_group = input(f"{Fore.YELLOW}New Blood Group: {Style.RESET_ALL}")
                
                self.cursor.execute(
                    "UPDATE patients SET blood_group = %s WHERE patient_id = %s",
                    (new_blood_group, patient_id)
                )
                self.connection.commit()
                print(f"{Fore.GREEN}Blood group updated successfully.{Style.RESET_ALL}")
            
            time.sleep(1)
        
        except Error as e:
            print(f"{Fore.RED}Error updating patient information: {e}{Style.RESET_ALL}")
            self.connection.rollback()
            time.sleep(2)

    def update_bill_status(self):
        try:
            self.clear_screen()
            print(f"\n{Fore.CYAN}=== Update Bill Payment Status ==={Style.RESET_ALL}")
            
            bill_id = input(f"{Fore.YELLOW}Enter Bill ID: {Style.RESET_ALL}")
            
            self.cursor.execute("""
                SELECT b.*, CONCAT(p.first_name, ' ', p.last_name) as patient_name
                FROM billing b
                JOIN patients p ON b.patient_id = p.patient_id
                WHERE b.bill_id = %s
            """, (bill_id,))
            
            bill = self.cursor.fetchone()
            
            if not bill:
                print(f"{Fore.RED}Bill not found.{Style.RESET_ALL}")
                time.sleep(2)
                return
            
            print(f"\n{Fore.CYAN}Current Bill Information:{Style.RESET_ALL}")
            print(f"Bill ID: {bill['bill_id']}")
            print(f"Patient: {bill['patient_name']} (ID: {bill['patient_id']})")
            print(f"Amount: ${bill['total_amount']:.2f}")
            print(f"Date: {bill['bill_date']}")
            print(f"Current Status: {bill['payment_status']}")
            
            print(f"\n{Fore.CYAN}New Payment Status Options:{Style.RESET_ALL}")
            print("1. Pending")
            print("2. Paid")
            print("3. Overdue")
            
            choice = input(f"\n{Fore.YELLOW}Select new status (1-3): {Style.RESET_ALL}")
            status_options = ['Pending', 'Paid', 'Overdue']
            
            if choice in ['1', '2', '3']:
                new_status = status_options[int(choice) - 1]
                
                self.cursor.execute(
                    "UPDATE billing SET payment_status = %s WHERE bill_id = %s",
                    (new_status, bill_id)
                )
                self.connection.commit()
                print(f"{Fore.GREEN}Payment status updated to {new_status}.{Style.RESET_ALL}")
                time.sleep(1)
            else:
                print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
        
        except Error as e:
            print(f"{Fore.RED}Error updating bill status: {e}{Style.RESET_ALL}")
            self.connection.rollback()
            time.sleep(2)
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_menu(self):
        self.clear_screen()
        print(f"\n{Fore.CYAN}{'=' * 50}")
        print(f"{' ' * 10}HOSPITAL MANAGEMENT SYSTEM")
        print(f"{'=' * 50}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}1. {Fore.WHITE}Patient Management{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}a. {Fore.WHITE}Register New Patient{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}b. {Fore.WHITE}View All Patients{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}c. {Fore.WHITE}Update Patient Information{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}2. {Fore.WHITE}Doctor Management{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}a. {Fore.WHITE}Register New Doctor{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}b. {Fore.WHITE}View All Doctors{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}3. {Fore.WHITE}Appointment Management{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}a. {Fore.WHITE}Book New Appointment{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}b. {Fore.WHITE}View All Appointments{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}c. {Fore.WHITE}Manage Appointment Status{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}4. {Fore.WHITE}Medical Records{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}a. {Fore.WHITE}Add New Medical Record{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}b. {Fore.WHITE}View Patient Medical History{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}5. {Fore.WHITE}Billing{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}a. {Fore.WHITE}Generate New Bill{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}b. {Fore.WHITE}View Billing History{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}c. {Fore.WHITE}Update Payment Status{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}6. {Fore.RED}Exit System{Style.RESET_ALL}")
    
    def run(self):
        if not self.connection:
            print(f"{Fore.RED}Cannot start system without database connection.{Style.RESET_ALL}")
            return
        
        while True:
            self.display_menu()
            choice = input(f"\n{Fore.YELLOW}Enter your choice: {Style.RESET_ALL}")
            
            if choice == '1a':
                self.add_patient()
            elif choice == '1b':
                self.view_patients()
            elif choice == '1c':
                self.update_patient()
            elif choice == '2a':
                self.add_doctor()
            elif choice == '2b':
                self.view_doctors()
            elif choice == '3a':
                self.book_appointment()
            elif choice == '3b':
                self.view_appointments()
            elif choice == '3c':
                self.manage_appointments()
            elif choice == '4a':
                self.add_medical_record()
            elif choice == '4b':
                self.view_medical_records()
            elif choice == '5a':
                self.generate_bill()
            elif choice == '5b':
                self.view_billing_history()
            elif choice == '5c':
                self.update_bill_status()
            elif choice == '6':
                self.clear_screen()
                print(f"\n{Fore.CYAN}Thank you for using the Hospital Management System. Goodbye!{Style.RESET_ALL}")
                if self.connection:
                    self.connection.close()
                break
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
                time.sleep(1)

if __name__ == "__main__":
    system = HospitalManagementSystem()
    system.run()