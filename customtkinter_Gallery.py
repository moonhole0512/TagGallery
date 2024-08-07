import customtkinter as ctk
import sqlite3
from PIL import Image, ImageTk
from CTkMessagebox import CTkMessagebox
import os
import math
import subprocess
import NAIimageViwer
import traceback
import ctypes

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class FullscreenImageViewer:
    def __init__(self, master, image_list, current_index):
        self.master = master
        self.image_list = image_list
        self.current_index = current_index

        # DPI 인식 설정
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        
        # 실제 화면 해상도 가져오기
        user32 = ctypes.windll.user32
        self.screen_width = user32.GetSystemMetrics(0)
        self.screen_height = user32.GetSystemMetrics(1)

        # 창 설정
        self.master.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.master.overrideredirect(True)  # 창 테두리 제거
        self.master.lift()
        self.master.wm_attributes("-topmost", True)
        #self.master.focus_force()

        self.master.bind("<Escape>", self.close_viewer)
        self.master.bind("<Right>", self.next_image)
        self.master.bind("<Left>", self.previous_image)

        self.canvas = ctk.CTkCanvas(self.master, highlightthickness=0, bg="black")
        self.canvas.pack(fill=ctk.BOTH, expand=True)

        self.current_image = None
        self.show_current_image()
        
        # 포커스를 설정하기 위한 추가 코드
        self.master.after(0, self.set_focus)

    def set_focus(self):
        self.master.focus_force()
        self.master.focus_set()

    def show_current_image(self):
        img_path = self.image_list[self.current_index][2]
        if not os.path.exists(img_path):
            print(f"이미지 파일을 찾을 수 없습니다: {img_path}")
            return

        try:
            with Image.open(img_path) as img:
                # 이미지 크기 조정
                img_ratio = img.width / img.height
                screen_ratio = self.screen_width / self.screen_height

                if img_ratio > screen_ratio:
                    new_width = self.screen_width
                    new_height = int(new_width / img_ratio)
                else:
                    new_height = self.screen_height
                    new_width = int(new_height * img_ratio)

                img = img.resize((new_width, new_height), Image.LANCZOS)
                self.current_image = ImageTk.PhotoImage(img)

                # 이전 이미지 삭제
                self.canvas.delete("all")
                
                # 이미지를 중앙에 배치
                x = (self.screen_width - new_width) // 2
                y = (self.screen_height - new_height) // 2
                
                # 캔버스에 이미지 생성
                self.canvas.create_image(x, y, anchor="nw", image=self.current_image)
                
                # 캔버스 크기 조정
                self.canvas.config(width=self.screen_width, height=self.screen_height)
        except Exception as e:
            print(f"이미지를 불러오는 중 오류 발생: {e}")

    def next_image(self, event):
        self.current_index = (self.current_index + 1) % len(self.image_list)
        self.show_current_image()

    def previous_image(self, event):
        self.current_index = (self.current_index - 1) % len(self.image_list)
        self.show_current_image()

    def close_viewer(self, event):
        self.master.destroy()

class ImageGalleryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TagGallery_V1.0")
        #self.geometry("1450x1000")
        self.geometry("1340x960")
        
        self.searchList = []
        self.currentPage = 1
        self.maxDisplay = 30
        
        self.dbNo = 0
        self.dbPath = ""
        
        self.image_references = {'thumbnails': [], 'selected': []}
        
        self.create_widgets()

    def create_widgets(self):
        # 상단 프레임 생성 
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill=ctk.X, padx=5, pady=(5, 0))  # 하단 패딩 제거

        # Tags 라벨과 입력 필드
        self.tag_label = ctk.CTkLabel(top_frame, text="Tags")
        self.tag_label.pack(side=ctk.LEFT)
        
        self.textbox_tags = ctk.CTkEntry(top_frame, width=680)
        self.textbox_tags.pack(side=ctk.LEFT, padx=(0, 5))
        self.textbox_tags.bind("<Return>", lambda event: self.search_images(1))
        
        # 검색 버튼
        self.search_button = ctk.CTkButton(top_frame, text="검색", command=lambda: self.search_images(1), width=50, height=28)
        self.search_button.pack(side=ctk.LEFT)

        # 정렬 콤보박스
        self.order_var = ctk.StringVar(value="DESC")
        self.order_combobox = ctk.CTkComboBox(top_frame, variable=self.order_var, values=["DESC","ASC","RANDOM"], width=100)
        self.order_combobox.pack(side=ctk.LEFT)
        
        # 플랫폼 콤보박스
        self.Platorder_var = ctk.StringVar(value="ALL")
        self.Platorder_combobox = ctk.CTkComboBox(top_frame, variable=self.Platorder_var, values=["ALL","NAI","DIF","None"], width=70)
        self.Platorder_combobox.pack(side=ctk.LEFT)
        
        self.page_label = ctk.CTkLabel(top_frame, text="")
        self.page_label.pack(side=ctk.RIGHT, padx=(5, 5))
        
        self.currentpagebox = ctk.CTkEntry(top_frame, width=50)
        self.currentpagebox.pack(side=ctk.RIGHT)
        self.currentpagebox.bind("<Return>", lambda event: self.pageinput())
        
        self.next_button = ctk.CTkButton(top_frame, text="다음", command=self.next_page, width=50, height=28)
        self.next_button.pack(side=ctk.RIGHT)

        self.pre_button = ctk.CTkButton(top_frame, text="이전", command=self.prev_page, width=50, height=28)
        self.pre_button.pack(side=ctk.RIGHT)

        # 메인 컨텐츠 영역 (이미지 영역과 선택된 이미지 영역을 포함)
        main_content = ctk.CTkFrame(self)
        main_content.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        # 이미지 영역 (왼쪽)
        self.img_area = ctk.CTkFrame(main_content)
        self.img_area.pack(side=ctk.LEFT, fill=ctk.BOTH, padx=(0, 5), pady=0)
        
        # 오른쪽 영역 (선택된 이미지와 태그)
        right_area = ctk.CTkFrame(main_content)
        right_area.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=0, pady=0)
        
        # 선택된 이미지 영역 (오른쪽 상단)
        self.selectimg_area = ctk.CTkFrame(right_area)
        self.selectimg_area.pack(fill=ctk.BOTH, expand=True, padx=0, pady=0)
        self.bind("<Delete>", self.deleteImg)
        
        # 선택된 이미지 태그 텍스트 (오른쪽 하단)
        self.selected_img_tag_text = ctk.CTkTextbox(right_area, wrap="word")
        self.selected_img_tag_text.pack(fill=ctk.BOTH, pady=(5, 0), padx=0)

        self.search_images(0)

    def pageinput(self):
        current_value = self.currentpagebox.get()
        
        if current_value.isdigit() and int(current_value) != 0:
            self.currentPage = int(current_value)
            self.update_page()
    
    def deleteImg(self, event):
        print("삭제함수 들어옴")
        print(f"삭제대상[{self.dbNo}] - {self.dbPath}")
        if CTkMessagebox(title="선택된 이미지 삭제", message="선택한 이미지를 삭제합니다.", icon="question", option_1="Yes", option_2="No").get() == "Yes":
            print("삭제진행")
            conn = sqlite3.connect("image_gallery.db")
            cursor = conn.cursor()
    
            try:
                cursor.execute("SELECT * FROM NAIimgInfo WHERE no = ?", (self.dbNo,))
                record = cursor.fetchone()
                if not record:
                    print(f"Error: 레코드가 존재하지 않습니다. (no={self.dbNo})")
                    return
            
                if not os.path.exists(self.dbPath):
                    print(f"Error: 파일이 존재하지 않습니다. ({self.dbPath})")
                    return
            
                cursor.execute("DELETE FROM NAIimgInfo WHERE no = ?", (self.dbNo,))
                print(f"레코드 삭제 성공 (no={self.dbNo})")
            
                os.remove(self.dbPath)
                print(f"파일 삭제 성공 ({self.dbPath})")
            
                conn.commit()
                
                self.search_images(0)
                self.update_page()
            
            except Exception as ex:
                print(f"Error: {ex}")
            
            finally:
                conn.close()
        else:
            print("삭제취소")
        
    def sqlTagSearch(self, searchTags, order='DESC', plat='ALL'):
        conn = sqlite3.connect("image_gallery.db")
        cursor = conn.cursor()
        
        tags_list = searchTags.split(',')

        conditions = []
        for tag in tags_list:
            conditions.append("tags LIKE ?")
        
        query_condition = " AND ".join(conditions)
        
        platform_query = " "
        if plat == 'NAI':
            platform_query = " and platform='NovelAI' "
        elif plat == 'DIF':
            platform_query = " and platform='StableDiffution' "
        elif plat == 'None':
            platform_query = " and platform='' "
        
        query = ""
        if order == 'RANDOM':
            query = f"SELECT * FROM NAIimgInfo WHERE {query_condition} {platform_query} ORDER BY RANDOM()"
        else:
            query = f"SELECT * FROM NAIimgInfo WHERE {query_condition} {platform_query} ORDER BY makeTime {order} "

        cursor.execute(query, ['%' + tag.strip() + '%' for tag in tags_list])
        
        result = cursor.fetchall()
        
        conn.close()
        
        return result if result else ['검색결과가 없습니다.']

    def search_images(self, searchtype):
        if searchtype == 1:
            self.currentPage = 1
        print("검색호출")
        print(self.textbox_tags.get())
        self.searchList = self.sqlTagSearch(self.textbox_tags.get(), self.order_var.get(), self.Platorder_var.get())
        print(f"검색 결과 : {len(self.searchList)}")
        max_page = math.ceil(len(self.searchList) / self.maxDisplay)
        if self.currentPage > max_page:
            self.currentPage = max_page
            ctk.CTkMessagebox(title="Warning", message="최대 페이지를 초과했습니다.", icon="warning")
        
        self.update_page()

    def update_page(self):
        max_page = math.ceil(len(self.searchList) / self.maxDisplay)
        if self.currentPage > max_page:
            self.currentPage = max_page
            ctk.CTkMessagebox(title="Warning", message="최대 페이지를 초과했습니다.", icon="warning")
        
        self.page_label.configure(text=f"/{max_page}")
        self.currentpagebox.delete(0, "end")
        self.currentpagebox.insert(0, self.currentPage)

        start_idx = (self.currentPage - 1) * self.maxDisplay
        end_idx = start_idx + self.maxDisplay
        current_images = self.searchList[start_idx:end_idx]
        
        self.display_images(current_images)
        
    def on_image_click(self, event, dbno, path, tags):
        # 이전에 선택된 이미지 삭제
        for widget in self.selectimg_area.winfo_children():
            widget.destroy()
    
        selected_img = Image.open(path)
    
        # `selectimg_area`의 예상 크기 설정
        area_width = 550  # 또는 self.selectimg_area.winfo_width() 값 사용
        area_height = 700  # 또는 self.selectimg_area.winfo_height() 값 사용
    
        # 이미지의 가로세로 비율 계산
        img_ratio = selected_img.size[0] / selected_img.size[1]
        area_ratio = area_width / area_height
    
        # `selectimg_area`에 이미지를 맞추기 위한 크기 계산
        if img_ratio > area_ratio:
            # 이미지의 가로가 더 넓을 경우, 가로를 기준으로 조정
            new_width = area_width
            new_height = int(area_width / img_ratio)
        else:
            # 이미지의 세로가 더 길거나 같을 경우, 세로를 기준으로 조정
            new_height = area_height
            new_width = int(area_height * img_ratio)
    
        # 이미지 크기 조정
        selected_img = selected_img.resize((new_width, new_height), Image.LANCZOS)
    
        # 중앙에 배치하기 위해 여백 계산
        padx = (area_width - new_width) // 2
        pady = (area_height - new_height) // 2
    
        # 이미지를 CTkImage로 변환하여 라벨에 설정
        selected_img = ctk.CTkImage(light_image=selected_img, size=(new_width, new_height))
        selectimg_label = ctk.CTkLabel(self.selectimg_area, image=selected_img, text="")
        selectimg_label.image = selected_img
        selectimg_label.grid(row=0, column=0, padx=padx, pady=pady, sticky='nsew')
        selectimg_label.bind("<Double-Button-1>", self.show_big_image)
    
        # 태그 정보 업데이트
        self.selected_img_tag_text.delete("1.0", "end")
        self.selected_img_tag_text.insert("1.0", tags)
    
        # 데이터베이스 정보 업데이트
        self.dbNo = dbno
        self.dbPath = path


    def show_big_image(self, event):
        if self.dbPath:
            current_index = next((i for i, img in enumerate(self.searchList) if img[2] == self.dbPath), None)
            if current_index is not None:
                viewer_window = ctk.CTkToplevel(self)
                viewer_window.withdraw()  # 임시로 창 숨기기
                viewer = FullscreenImageViewer(viewer_window, self.searchList, current_index)
                viewer_window.deiconify()  # 설정 완료 후 창 표시
                viewer_window.protocol("WM_DELETE_WINDOW", viewer_window.destroy)
                viewer_window.mainloop()
            else:
                print("현재 이미지를 searchList에서 찾을 수 없습니다.")
        else:
            print("선택된 이미지가 없습니다.")

    def display_images(self, image_paths):
        for widget in self.img_area.winfo_children():
            widget.destroy()
        self.image_references['thumbnails'] = []
        for i, img_path in enumerate(image_paths):
            img = Image.open(img_path[2])
            img = img.resize((150, 150), Image.LANCZOS)
            img = ctk.CTkImage(light_image=img, size=(150, 150))
            self.image_references['thumbnails'].append(img)
            label = ctk.CTkLabel(self.img_area, image=img, text="")
            label.image = img
            label.grid(row=i // 5, column=i % 5, padx=1, pady=1)
            label.bind("<Double-Button-1>", lambda event, path=img_path[2]: self.open_external_program(path))
            label.bind("<Button-1>", lambda event, dbno=img_path[0], path=img_path[2], tags=img_path[1]: self.on_image_click(event, dbno, path, tags))

    def open_external_program(self, img_path):
        os.startfile(img_path)
        #program_path = ""
        #with open("settings.txt", 'r') as file:
        #    lines = file.readlines()
        #    program_path = lines[2].strip().split('=')[1]
        #
        #subprocess.Popen([program_path, img_path])

    def next_page(self):
        self.currentPage += 1
        self.update_page()

    def prev_page(self):
        if self.currentPage > 1:
            self.currentPage -= 1
            self.update_page()
#####메인 실행부#####
if __name__ == "__main__":
    try:
        print("[Classification Start]")
        NAIimageViwer.initFirstStart()
        NAIimageViwer.classification()
    except Exception as ex:
        print('Classification Error', ex)
        traceback.print_exc()
        input("에러가 발생해서 종료되었습니다. 에러문구를 확인해주세요.")
    print("[Classification done]")

    try:
        app = ImageGalleryApp()
        app.mainloop()
    except Exception as ex:
        print('Viewer Error', ex)
        traceback.print_exc()
        input("에러가 발생해서 종료되었습니다. 에러문구를 확인해주세요.")

