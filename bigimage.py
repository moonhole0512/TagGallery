# bigimage.py

import os
import tkinter as tk
from PIL import Image, ImageTk

class ImageSliderApp:
    def __init__(self, master, image_folder):
        self.master = master
        self.master.title("Image Slider")
        self.master.geometry("{0}x{1}+0+0".format(
            self.master.winfo_screenwidth(), self.master.winfo_screenheight()))
        self.master.attributes('-fullscreen', True)

        self.image_folder = image_folder
        self.image_list = self.get_image_list()

        self.current_index = 0
        self.current_image = None

        # PhotoImage 객체를 인스턴스 변수로 저장
        self.photo_image = None

        self.create_widgets()

    def create_widgets(self):
        self.canvas = tk.Canvas(self.master, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Right>", self.show_next_image)
        self.canvas.bind("<Left>", self.show_previous_image)
        self.canvas.bind("<Escape>", self.exit_program)

        # 초기에 이미지를 표시할 때도 show_image를 호출하도록 변경
        self.show_image()

        # Canvas에 포커스 주기
        self.canvas.focus_set()

    def get_image_list(self):
        image_list = [f for f in os.listdir(self.image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        return sorted(image_list)

    def show_image(self):
        # 이미지 객체를 생성하기 전에 기존의 객체를 삭제
        if self.photo_image:
            self.canvas.delete(self.photo_image)

        image_path = os.path.join(self.image_folder, self.image_list[self.current_index])
        
        # 이미지가 없는 경우 처리
        if not os.path.exists(image_path):
            print(f"Error: 이미지 파일이 존재하지 않습니다 ({image_path})")
            return
        
        img = Image.open(image_path)

        # 이미지의 가로비율을 유지하면서 화면 가로 및 세로 해상도에 맞게 조절
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        width_percent = screen_width / float(img.size[0])
        new_height = int(float(img.size[1]) * float(width_percent))

        if new_height > screen_height:
            width_percent = screen_height / float(img.size[1])
            new_width = int(float(img.size[0]) * float(width_percent))
            img = img.resize((new_width, screen_height), Image.ANTIALIAS)
        else:
            img = img.resize((screen_width, new_height), Image.ANTIALIAS)

        self.photo_image = ImageTk.PhotoImage(img)

        # 이미지를 중앙에 배치
        x = (screen_width - img.width) // 2
        y = (screen_height - img.height) // 2
        self.canvas.config(width=screen_width, height=screen_height)
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo_image)

    def show_next_image(self, event):
        self.current_index = (self.current_index + 1) % len(self.image_list)
        self.show_image()

    def show_previous_image(self, event):
        self.current_index = (self.current_index - 1) % len(self.image_list)
        self.show_image()

    def exit_program(self, event):
        self.master.destroy()

def run_image_slider(image_folder_path):
    root = tk.Tk()
    app = ImageSliderApp(root, image_folder_path)
    root.mainloop()

if __name__ == "__main__":
    image_folder_path = r"D:\NAI\Classification_NAI\231224"  # 여기에 이미지 폴더 경로를 입력하세요.
    run_image_slider(image_folder_path)
