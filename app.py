from groq import Groq
from langchain.document_loaders import PyPDFLoader
from dotenv import load_dotenv
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client with API key
api_key = os.getenv("LLAMA_API_KEY")
if not api_key:
    raise ValueError("API key not found in .env file. Please add LLAMA_API_KEY to your .env file.")

client = Groq(api_key=api_key)

# PDF Processing Functions
def extract_text_from_pdf(pdf_file):
    """Extract all text from a PDF file using LangChain."""
    try:
        loader = PyPDFLoader(pdf_file)
        documents = loader.load()
        text = "\n".join(doc.page_content for doc in documents)
        return text
    except Exception as e:
        return f"Error extracting text: {e}"

def ask_question_to_pdf(pdf_text, question):
    """Ask a question based on the content of the PDF using Llama3."""
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant analyzing PDF content."},
            {"role": "user", "content": f"The PDF contains the following text: {pdf_text[:4000]}..."},
            {"role": "user", "content": question}
        ]
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=0.7,
            max_tokens=200,
            top_p=1,
            stream=False
        )
        
        # Assuming completion is iterable or dictionary-like
        if hasattr(completion, 'choices') and len(completion.choices) > 0:
            return completion.choices[0].message.content
        else:
            return "Unexpected response structure from Llama3 API."
    except Exception as e:
        return f"Error interacting with Llama3: {e}"

# Tkinter GUI Setup
class PDFChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Question Assistant")
        self.root.geometry("500x400")

        self.pdf_text = ""  # Store the extracted text from PDF

        # Frame to hold drag and drop box
        self.upload_frame = tk.Frame(root)
        self.upload_frame.pack(pady=20)

        # Label for instructions to drag and drop
        self.label = tk.Label(self.upload_frame, text="Drag and Drop or Upload a PDF file", pady=10)
        self.label.pack(padx=10, pady=10)

        # Drag-and-drop box for PDF files
        self.drop_box = tk.Label(self.upload_frame, text="Drop PDF Here", relief="solid", width=40, height=5, bg="lightgray")
        self.drop_box.pack(pady=10)

        # Button to upload PDF
        self.upload_button = tk.Button(self.upload_frame, text="Upload PDF", command=self.upload_pdf, width=20)
        self.upload_button.pack(pady=5)

        # Frame to hold question input box
        self.question_frame = tk.Frame(root)
        self.question_frame.pack(pady=10)

        # Textbox for asking questions
        self.question_entry = tk.Entry(self.question_frame, width=50)
        self.question_entry.pack(pady=10)
        self.question_entry.insert(0, "Ask a question here...")

        # Button to ask question
        self.ask_button = tk.Button(self.question_frame, text="Ask Question", command=self.ask_question, width=20)
        self.ask_button.pack(pady=5)

        # Label to show the answer
        self.answer_label = tk.Label(root, text="", wraplength=400)
        self.answer_label.pack(pady=10)

        # Drag and drop support
        root.drop_target_register(DND_FILES)
        root.dnd_bind('<<Drop>>', self.on_drop)

    def upload_pdf(self):
        """Open a file dialog to upload a PDF."""
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.pdf_text = extract_text_from_pdf(file_path)
            if self.pdf_text.startswith("Error"):
                messagebox.showerror("Error", "Failed to extract text from PDF.")
            else:
                messagebox.showinfo("Success", "PDF loaded successfully!")

    def ask_question(self):
        """Get the answer to the user's question based on the uploaded PDF."""
        question = self.question_entry.get().strip()
        if not question:
            messagebox.showwarning("Input Error", "Please enter a question.")
            return

        if not self.pdf_text:
            messagebox.showwarning("No PDF Loaded", "Please upload a PDF first.")
            return

        answer = ask_question_to_pdf(self.pdf_text, question)
        self.answer_label.config(text=f"Answer: {answer}")

    def on_drop(self, event):
        """Handle the drag-and-drop event for PDF files."""
        pdf_file = event.data.strip()
        self.pdf_text = extract_text_from_pdf(pdf_file)
        if self.pdf_text.startswith("Error"):
            messagebox.showerror("Error", "Failed to extract text from PDF.")
        else:
            messagebox.showinfo("Success", "PDF loaded successfully!")

# Main function to create the GUI
def main():
    root = TkinterDnD.Tk()  # Create a TkinterDnD root window
    app = PDFChatbotApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
