import tkinter as tk
from tkinter import messagebox
from xml.etree import ElementTree as ET
import random
import os
import time

class TestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Test d'examen (Xarxes de Dades)")
        self.root.geometry("1200x500")
        self.center_window()
        self.current_question = self.load_progress()
        self.questions = self.load_questions_from_xml("preguntas/preguntas.xml")
        self.shuffle_questions()

        self.label_question = tk.Label(root, text="", wraplength=1160, justify="left", font=("Arial", 16))
        self.label_question.pack(pady=10)

        self.radio_var = tk.StringVar()
        self.radio_var.set(None)

        self.radio_buttons = []
        for i in range(3):
            option = tk.Radiobutton(root, text="", variable=self.radio_var, value="", command=self.check_answer, font=("Arial", 14))
            option.pack()
            self.radio_buttons.append(option)

        self.next_button = tk.Button(root, text="Següent", command=self.next_question, font=("Arial", 14))
        self.next_button.pack(pady=10)

        self.stats_label = tk.Label(root, text="", font=("Arial", 14))
        self.stats_label.pack(side=tk.BOTTOM, pady=10)

        self.timer_label = tk.Label(root, text="", font=("Arial", 14))
        self.timer_label.pack(side=tk.BOTTOM, pady=10)

        self.correct_count = 0  # Comptador de preguntes encertades
        self.incorrect_count = 0  # Comptador de preguntes fallades

        self.start_time = time.time()  # Tiempo de inicio del test
        self.update_timer()  # Inicia la actualización del temporizador

        self.load_question()

        # Configura l'esdeveniment per tancar la finestra principal
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if tk.messagebox.askokcancel("Tancar", "Estàs segur que vols tancar l'aplicació?"):
            # Borra l'arxiu de progrés al tancar la finestra
            self.delete_progress_file()

            # Verifica si la finestra encara existeix abans de intentar destruir-la
            if self.root.winfo_exists():
                self.root.destroy()

            # Elimina l'arxiu de progrés en finalitzar el test
            self.delete_progress_file()

    def delete_progress_file(self):
        try:
            os.remove("progress.txt")
        except FileNotFoundError:
            pass  # No fa res si l'arxiu no existeix

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 1200
        window_height = 500
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    def load_progress(self):
        try:
            with open("progress.txt", "r") as file:
                return int(file.read())
        except FileNotFoundError:
            # Crea l'arxiu "progress.txt" si no existeix, amb el valor inicial de 1
            self.save_progress(1)
            return 1

    def save_progress(self, progress):
        with open("progress.txt", "w") as file:
            file.write(str(progress))

    def load_questions_from_xml(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()
        questions = []

        for question_elem in root.findall(".//pregunta"):
            question = {
                "text": question_elem.find("texto").text,
                "options": [option.text for option in question_elem.findall(".//opcion")],
                "correct_answer": question_elem.find("respuesta_correcta").text
            }
            questions.append(question)

        return questions

    def shuffle_questions(self):
        random.shuffle(self.questions)

    def load_question(self):
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            self.label_question.config(text=question["text"])

            for i, option in enumerate(question["options"]):
                self.radio_buttons[i].config(text=option, value=chr(ord("a") + i), fg="black")

            self.radio_var.set(None)
            self.next_button.config(state=tk.DISABLED)
        else:
            elapsed_time = int(time.time() - self.start_time)
            messagebox.showinfo("Fi del test", f"Has completat el test en {elapsed_time} segons!")

            # Elimina l'arxiu de progrés en finalitzar el test
            self.delete_progress_file()

            self.root.destroy()

    def check_answer(self):
        correct_option = ord(self.questions[self.current_question]["correct_answer"]) - ord("a")
        correct_option_text = self.questions[self.current_question]["options"][correct_option]

        user_answer = self.radio_var.get()
        if user_answer is not None:
            for i, option in enumerate(self.questions[self.current_question]["options"]):
                if user_answer == chr(ord("a") + i):
                    if user_answer == self.questions[self.current_question]["correct_answer"]:
                        self.radio_buttons[i].config(fg="green")
                        self.correct_count += 1
                    else:
                        self.radio_buttons[i].config(fg="red")
                        self.incorrect_count += 1

            if user_answer == self.questions[self.current_question]["correct_answer"]:
                messagebox.showinfo("Resposta Correcta", "Correcte!")
            else:
                messagebox.showinfo("Resposta Incorrecta", f"Incorrecte!")

            self.next_button.config(state=tk.NORMAL)
            self.update_stats_label()

    def is_answer_correct(self, question_index):
        correct_answer = self.questions[question_index]["correct_answer"]
        user_answer = self.radio_var.get()
        return user_answer == correct_answer

    def next_question(self):
        self.current_question += 1
        self.save_progress(self.current_question)  # Guardar el progrés després d'incrementar la pregunta
        self.load_question()

    def update_stats_label(self):
        total_questions = len(self.questions)
        answered_questions = self.current_question
        correct_answers = self.correct_count
        incorrect_answers = self.incorrect_count

        stats_text = f"Total de preguntes: {total_questions}   |  Preguntes contestades: {answered_questions}   |  Correctes: {correct_answers}   |  Incorrectes: {incorrect_answers}"
        self.stats_label.config(text=stats_text)

    def update_timer(self):
        elapsed_time_seconds = int(time.time() - self.start_time)
        elapsed_minutes = elapsed_time_seconds // 60
        elapsed_seconds = elapsed_time_seconds % 60

        timer_text = f"Temps transcorregut: {elapsed_minutes} min {elapsed_seconds} seg"
        self.timer_label.config(text=timer_text)
        self.root.after(1000, self.update_timer)  # Actualiza cada segundo

if __name__ == "__main__":
    root = tk.Tk()
    app = TestApp(root)
    root.mainloop()
