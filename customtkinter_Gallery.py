import tkinter as tk
import sqlite3
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import math
import subprocess
import NAIimageViwer
import traceback
from bigimage import run_image_slider  # bigimage.py에서 필요한 함수 또는 클래스를 import

class ImageGalleryApp:
    def __init__(self, master):
        self.master = master
        self.master.title("이미지 갤러리")
        
        # 창 크기 지정
        self.master.geometry("1450x1000")
        
        # 검색 결과를 저장할 변수
        self.searchList = []
        
        # 페이지 설정
        self.currentPage = 1
        self.maxDisplay = 30
        
        #표시될 이미지 사이즈 정의 =
        self.selectedImgWidth = 600
        self.maxselectedImgWidth = 876
        
        # 선택된 이미지 정보 
        self.dbNo = 0 #프라이머리키 보존
        self.dbPath = "" #파일경로 보존
        
        self.image_references = {'thumbnails': [], 'selected': []}
        
        # UI 구성
        self.create_widgets()

    #창 만들기
    def create_widgets(self):
        self.master.grid_rowconfigure(0, weight=0,minsize=40)  # 두 번째 행의 높이를 150으로 고정

        # 라벨
        self.tag_label = tk.Label(self.master, text="Tags", anchor="e")
        self.tag_label.grid(row=0, column=0, padx=0, pady=0, sticky='news')
        
        # Tags 입력 텍스트박스
        self.textbox_tags = ttk.Entry(self.master)
        self.textbox_tags.grid(row=0, column=1, padx=1, pady=1, sticky='we')
        self.textbox_tags.bind("<Return>", lambda event: self.search_images(1))
        
        # 검색 버튼
        self.search_button = ttk.Button(self.master, text="검색", command=lambda:self.search_images(1))
        self.search_button.grid(row=0, column=2, padx=1, pady=5, sticky='w')

        # 정렬 순서 선택을 위한 드롭다운 메뉴
        self.order_var = tk.StringVar(value="DESC")
        self.order_combobox = ttk.Combobox(self.master, textvariable=self.order_var, values=["DESC","ASC","RANDOM"], width=10)
        self.order_combobox.grid(row=0, column=3, padx=0, pady=5, sticky='w')
        
        # Platform 선택을 위한 드롭다운 메뉴
        self.Platorder_var = tk.StringVar(value="ALL")
        self.Platorder_combobox = ttk.Combobox(self.master, textvariable=self.Platorder_var, values=["ALL","NAI","DIF","None"], width=10)
        self.Platorder_combobox.grid(row=0, column=4, padx=0, pady=5, sticky='w')

        # 이전 버튼
        self.pre_button = ttk.Button(self.master, text="이전", command=self.prev_page)
        #self.pre_button.grid(row=0, column=4, padx=5, pady=5, sticky='e')
        self.pre_button.grid(row=0, column=5, padx=0, pady=0,)

        # 다음 버튼
        self.next_button = ttk.Button(self.master, text="다음", command=self.next_page)
        self.next_button.grid(row=0, column=6, padx=5, pady=5, sticky='w')
        
        # 페이지 입력 텍스트박스
        self.currentpagebox = ttk.Entry(self.master, width=5)
        self.currentpagebox.grid(row=0, column=7, padx=0, pady=0)
        self.currentpagebox.bind("<Return>", lambda event: self.pageinput())
        
        # 페이지 정보 표시 라벨
        self.page_label = tk.Label(self.master, text="")
        self.page_label.grid(row=0, column=8, padx=0, pady=5,sticky='w')

        ##########################################################################################################

        # 이미지 리스트 영역
        self.img_area = tk.Label(self.master)
        self.img_area.grid(row=1, column=0, padx=0, pady=0, columnspan=8, rowspan=4, sticky='n')
        
        # 선택 이미지 표시영역
        #self.selectimg_area = tk.Label(self.master,width=550, bd=1, relief="solid")
        self.selectimg_area = tk.Label(self.master)
        self.selectimg_area.grid(row=0, column=9, padx=0, pady=0, rowspan=4, sticky='news')
        self.selectimg_area.bind("<Delete>", self.deleteImg)
        
        # 선택된 이미지 태그 라벨
        self.selected_img_tag_text = tk.Text(self.master, wrap=tk.WORD, height=7)
        self.selected_img_tag_text.grid(row=4, column=9, padx=0, pady=0, sticky='n')

        # 초기 검색 수행
        self.search_images(0)

    def pageinput(self):
        current_value = self.currentpagebox.get()
        
        if current_value.isdigit() and int(current_value)!=0:
            self.currentPage = int(current_value)
            self.update_page()
    
    #선택한 파일 삭제 진행
    def deleteImg(self, event):
        print("삭제함수 들어옴")
        print(f"삭제대상[{self.dbNo}] - {self.dbPath}")
        if messagebox.askokcancel("선택된 이미지 삭제", "선택한 이미지를 삭제합니다."):
            print("삭제진행")
            ## SQLite 연결
            conn = sqlite3.connect("image_gallery.db")
            cursor = conn.cursor()
    
            try:
                # 레코드 삭제 전에 레코드 존재 여부 확인
                cursor.execute("SELECT * FROM NAIimgInfo WHERE no = ?", (self.dbNo,))
                record = cursor.fetchone()
                if not record:
                    print(f"Error: 레코드가 존재하지 않습니다. (no={self.dbNo})")
                    return
            
                # 파일 삭제 전에 파일 존재 여부 확인
                if not os.path.exists(self.dbPath):
                    print(f"Error: 파일이 존재하지 않습니다. ({self.dbPath})")
                    return
            
                # NAIimgInfo 테이블에서 레코드 삭제
                cursor.execute("DELETE FROM NAIimgInfo WHERE no = ?", (self.dbNo,))
                print(f"레코드 삭제 성공 (no={self.dbNo})")
            
                # 파일 삭제
                os.remove(self.dbPath)
                print(f"파일 삭제 성공 ({self.dbPath})")
            
                # 커밋
                conn.commit()
                
                self.search_images(0) #삭제완료하고 리스트 리프레시
                self.update_page() #페이지 재표시
            
            except Exception as ex:
                print(f"Error: {ex}")
            
            finally:
                # 연결 닫기
                conn.close()
        else:
            print("삭제취소")
        
    #검색 처리 (태그한개, 쉼표로 구분된거도 가능)
    def sqlTagSearch(self, searchTags, order='DESC', plat='ALL'):
        conn = sqlite3.connect("image_gallery.db")
        cursor = conn.cursor()
        
        # 사용자로부터 입력 받은 값을 쉼표로 분리
        tags_list = searchTags.split(',')

        # 입력 받은 값이 여러 개일 경우 AND 검색을 위해 각 값에 대해 LIKE 조건을 생성
        conditions = []
        for tag in tags_list:
            conditions.append("tags LIKE ?")
        
        # 여러 개의 조건을 AND로 연결
        query_condition = " AND ".join(conditions)
        
        #platform 조건문
        platform_query = " "
        if plat=='NAI':
            platform_query = " and platform='NovelAI' "
        elif plat=='DIF':
            platform_query = " and platform='StableDiffution' "
        elif plat=='None':
            platform_query = " and platform='' "
        

        # SQL 쿼리 생성
        query = ""
        if order=='RANDOM':
            query = f"SELECT * FROM NAIimgInfo WHERE {query_condition} {platform_query} ORDER BY RANDOM()" #랜덤 정렬이면
        else:
            query = f"SELECT * FROM NAIimgInfo WHERE {query_condition} {platform_query} ORDER BY makeTime {order} " #랜덤 정렬 아니면

        # 쿼리 수행
        cursor.execute(query, ['%' + tag.strip() + '%' for tag in tags_list])
        
        # 결과 출력
        result = cursor.fetchall()
        
        if not result:
            return ['검색결과가 없습니다.']
        
        conn.close()
        
        return result

    def search_images(self, searchtype):
        if searchtype == 1: #검색을 눌러서 실행되면 현재페이지를 1로 지정, 아니면 페이지수를 유지
            self.currentPage = 1
        # TODO: DB에서 이미지 검색 구현
        # 임시로 더미 데이터를 사용
        print("검색호출")
        #self.searchList = self.sqlTagSearch("")
        print(self.textbox_tags.get())
        self.searchList = self.sqlTagSearch(self.textbox_tags.get(), self.order_var.get(), self.Platorder_var.get()) #####
        print(f"검색 결과 : {len(self.searchList)}")
        #self.currentPage = 1
        max_page = math.ceil(len(self.searchList) / self.maxDisplay)
        if self.currentPage > max_page:
            self.currentPage = max_page
            messagebox.showwarning("경고", "최대 페이지를 초과했습니다.")
        
        # 페이지 갱신
        self.update_page()

    
    def update_page(self):
        max_page = math.ceil(len(self.searchList) / self.maxDisplay)
        if self.currentPage > max_page:
            self.currentPage = max_page
            messagebox.showwarning("경고", "최대 페이지를 초과했습니다.")
        
        # 페이지 정보 표시
        #self.page_label.config(text=f"{self.currentPage}/{max_page}") #현재페이지/최대페이지 표시
        self.page_label.config(text=f"/{max_page}")
        self.currentpagebox.delete(0, "end")
        self.currentpagebox.insert(0, self.currentPage)

        # 현재 페이지에 해당하는 이미지 가져오기
        start_idx = (self.currentPage - 1) * self.maxDisplay
        end_idx = start_idx + self.maxDisplay
        current_images = self.searchList[start_idx:end_idx]
        
        # 이미지 표시
        self.display_images(current_images)
        
    # 한번 클릭 시 실행될 함수 정의 
    def on_image_click(self, event, dbno, path, tags):
        # 선택한 이미지를 selectimg_area에 표시
        selected_img = Image.open(path)
        #selected_img = selected_img.resize((550, 600), Image.ANTIALIAS)
        #이미지 사이즈를 비율에 맞게 조절
        width_percent = (self.selectedImgWidth / float(selected_img.size[0]))
        new_height = int((float(selected_img.size[1]) * float(width_percent)))
        if new_height>self.maxselectedImgWidth : #최대 높이가 벗어나면 줄여버림
            new_height = self.maxselectedImgWidth
        selected_img = selected_img.resize((self.selectedImgWidth, new_height), Image.LANCZOS)
        #selected_img = selected_img.resize((550, 600), Image.LANCZOS)
        selected_img = ImageTk.PhotoImage(selected_img)
        selectimg_label = tk.Label(self.selectimg_area, image=selected_img)
        selectimg_label.image = selected_img
        selectimg_label.grid(row=0, column=0, padx=0, pady=0, sticky='news')
        selectimg_label.bind("<Double-Button-1>", self.show_big_image)
        
        self.selected_img_tag_text.delete(1.0, tk.END)  # Clear previous text
        self.selected_img_tag_text.insert(tk.END, tags)
        
        #선택된 이미지 정보 보존
        self.dbNo = dbno
        self.dbPath = path
        self.selectimg_area.focus_set() #삭제 함수 호출을 위한 포커스 세팅

    def show_big_image(self, event):
        selected_img_path = image_folder_path = r"D:\NAI\Classification_NAI\231224" 
        run_image_slider(selected_img_path)  # bigimage.py에 있는 함수 호출

    def display_images(self, image_paths):
        for widget in self.img_area.winfo_children():
            widget.destroy()
            # 이미지에 대한 참조를 저장하기 위한 리스트 초기화
            self.image_references['thumbnails'] = []
        for i, img_path in enumerate(image_paths):
            img = Image.open(img_path[2])
            #img = img.resize((150, 150), Image.ANTIALIAS)
            img = img.resize((150, 150), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            self.image_references['thumbnails'].append(img)
            label = tk.Label(self.img_area, image=img) #########최초실행시 에러발생라인(설정파일 있으면 에러안남)
            label.image = img  # keep a reference to the image
            label.grid(row=i // 5, column=i % 5, padx=1, pady=1)
            label.bind("<Double-Button-1>", lambda event, path=img_path[2]: self.open_external_program(path))
            # 클릭 시 실행될 함수 정의
            label.bind("<Button-1>", lambda event,dbno=img_path[0], path=img_path[2], tags=img_path[1]: self.on_image_click(event,dbno, path, tags))
            

    def open_external_program(self, img_path):
        # 외부 프로그램 실행 (여기서는 Honeyview 예시)
        program_path = ""
        with open("settings.txt", 'r') as file:
            lines = file.readlines()
            program_path = lines[2].strip().split('=')[1]
        
        subprocess.Popen([program_path, img_path])

    def next_page(self):
        self.currentPage += 1
        self.update_page()

    def prev_page(self):
        if self.currentPage > 1:
            self.currentPage -= 1
            self.update_page()

#####메인 실행부#####
try:
    print("[Classification Start]")
    NAIimageViwer.initFirstStart() #초기 실행 함수 호출
    NAIimageViwer.classification() #이미지 이동 및 db등록
except Exception as ex:
    print('Classification Error', ex)
    traceback.print_exc()
    input("에러가 발생해서 종료되었습니다. 에러문구를 확인해주세요.")
print("[Classification done]")

try:
    if __name__ == "__main__":
        root = tk.Tk()
        app = ImageGalleryApp(root)
        root.mainloop()
except Exception as ex:
    print('Viwer Error', ex)
    traceback.print_exc()
    input("에러가 발생해서 종료되었습니다. 에러문구를 확인해주세요.")

