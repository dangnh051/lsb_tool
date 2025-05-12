from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import os

class LSBStegoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Công cụ Giấu Tin LSB")
        self.root.geometry("600x500")
        self.create_widgets()

    def create_widgets(self):
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Frame cho Giấu tin
        hide_frame = ttk.LabelFrame(main_frame, text="Giấu Tin", padding="10")
        hide_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)

        # Nhập tin nhắn
        ttk.Label(hide_frame, text="Tin nhắn:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.message_entry = ttk.Entry(hide_frame, width=50)
        self.message_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Chọn ảnh đầu vào
        ttk.Label(hide_frame, text="Ảnh đầu vào:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.hide_input_var = tk.StringVar()
        self.hide_input_entry = ttk.Entry(hide_frame, textvariable=self.hide_input_var, width=40)
        self.hide_input_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(hide_frame, text="Chọn", command=self.browse_hide_input).grid(row=1, column=2, padx=5)

        # Nút giấu tin
        ttk.Button(hide_frame, text="Giấu Tin", command=self.hide_message).grid(row=2, column=0, columnspan=3, pady=10)

        # Frame cho Tách tin
        extract_frame = ttk.LabelFrame(main_frame, text="Tách Tin", padding="10")
        extract_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)

        # Chọn ảnh đầu vào
        ttk.Label(extract_frame, text="Ảnh đầu vào:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.extract_input_var = tk.StringVar()
        self.extract_input_entry = ttk.Entry(extract_frame, textvariable=self.extract_input_var, width=40)
        self.extract_input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(extract_frame, text="Chọn", command=self.browse_extract_input).grid(row=0, column=2, padx=5)

        # Nút tách tin
        ttk.Button(extract_frame, text="Tách Tin", command=self.extract_message).grid(row=1, column=0, columnspan=3, pady=10)

        # Nhãn trạng thái
        self.status_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.status_var, wraplength=500).grid(row=2, column=0, pady=10)

    def browse_hide_input(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            self.hide_input_var.set(file_path)

    def browse_extract_input(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            self.extract_input_var.set(file_path)

    def hide_message(self):
        input_path = self.hide_input_var.get()
        message = self.message_entry.get()
        output_path = "output.png"  # Ảnh đầu ra cố định

        if not input_path or not message:
            error_msg = "Vui lòng nhập tin nhắn và chọn ảnh đầu vào!"
            print(f"Lỗi: {error_msg}")
            self.status_var.set(f"Lỗi: {error_msg}")
            messagebox.showerror("Lỗi", error_msg)
            return

        try:
            img = Image.open(input_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            pixels = img.load()
            width, height = img.size

            binary_message = ''.join(format(byte, '08b') for byte in message.encode('utf-8'))
            binary_message += '00000000'  # Null terminator

            if len(binary_message) > width * height:
                error_msg = "Tin nhắn quá dài để giấu trong ảnh!"
                print(f"Lỗi: {error_msg}")
                self.status_var.set(f"Lỗi: {error_msg}")
                messagebox.showerror("Lỗi", error_msg)
                raise ValueError(error_msg)

            index = 0
            for y in range(height):
                for x in range(width):
                    if index >= len(binary_message):
                        break
                    r, g, b = pixels[x, y]
                    r = (r & 0xFE) | int(binary_message[index])
                    pixels[x, y] = (r, g, b)
                    index += 1

            img.save(output_path)
            success_msg = f"Tin nhắn đã được giấu thành công vào {output_path}"
            print(success_msg)
            self.status_var.set(success_msg)
            messagebox.showinfo("Thành công", success_msg)

        except Exception as e:
            error_msg = f"Không thể giấu tin nhắn: {e}"
            print(f"Lỗi: {error_msg}")
            self.status_var.set(f"Lỗi: {e}")
            messagebox.showerror("Lỗi", error_msg)

    def extract_message(self):
        input_path = self.extract_input_var.get()

        if not input_path:
            error_msg = "Vui lòng chọn ảnh đầu vào!"
            print(f"Lỗi: {error_msg}")
            self.status_var.set(f"Lỗi: {error_msg}")
            messagebox.showerror("Lỗi", error_msg)
            return

        try:
            img = Image.open(input_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            pixels = img.load()
            width, height = img.size

            byte_buffer = []
            message = ""
            max_length = 1000  # Giới hạn độ dài tin nhắn

            for y in range(height):
                for x in range(width):
                    if len(byte_buffer) // 8 >= max_length:
                        break
                    r, _, _ = pixels[x, y]
                    bit = r & 1
                    byte_buffer.append(str(bit))
                    if len(byte_buffer) == 8:
                        byte_str = ''.join(byte_buffer)
                        byte = int(byte_str, 2)
                        if byte == 0:
                            success_msg = f"Tin nhắn trích xuất: {message}"
                            print(success_msg)
                            self.status_var.set(success_msg)
                            messagebox.showinfo("Tin nhắn", success_msg)
                            return
                        message += chr(byte)
                        byte_buffer = []

            warning_msg = "Không tìm thấy tin nhắn hoặc tin nhắn quá dài!"
            print(warning_msg)
            self.status_var.set(warning_msg)
            messagebox.showwarning("Cảnh báo", warning_msg)

        except Exception as e:
            error_msg = f"Không thể trích xuất tin nhắn: {e}"
            print(f"Lỗi: {error_msg}")
            self.status_var.set(f"Lỗi: {e}")
            messagebox.showerror("Lỗi", error_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = LSBStegoApp(root)
    root.mainloop()