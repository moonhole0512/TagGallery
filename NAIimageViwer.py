import os
import sqlite3
import gzip
import json
from tkinter import Tk, filedialog
from PIL import Image, ImageTk
from datetime import datetime
from tkinter import PhotoImage, Scrollbar, Canvas
from tkinter import filedialog
from tkinter import messagebox
from subprocess import call


#####전역 변수 선언부#####
settings_file = "settings.txt" #세팅파일명
db_file = "image_gallery.db" #DB 파일명
image_file_path = "" # 분류할 이미지 경로
des_file_path = "" # 분류된 이미지 경로
#imgProgram = ""
firstStart = False

#####함수 선언부#####
#초기 세팅 진행
def initFirstStart():
    global settings_file, db_file, image_file_path, des_file_path, firstStart
    #세팅파일이 없다면
    if not os.path.exists(settings_file):
        firstStart = True
        # 파일 경로 선택을 위한 Tkinter 창 생성
        root = Tk()
        root.withdraw()  # 창이 표시되지 않도록 함

        # imageFilePath 지정
        image_file_path = filedialog.askdirectory(title="분류되지 않은 이미지 경로 지정")
        
        # desFilePath 지정
        des_file_path = filedialog.askdirectory(title="분류된 이미지 경로 지정")
        
        # 이미지파일 여는 프로그램 지정
        #imgProgram = filedialog.askopenfilename(title="이미지 뷰어 지정",filetypes=[("Executable files", "*.exe"), ("All files", "*.*")])

        # 설정 파일에 경로 저장
        with open(settings_file, 'w') as file:
            file.write(f"imageFilePath={image_file_path}\n")
            file.write(f"desFilePath={des_file_path}\n")
            #file.write(f"imgProgram={imgProgram}\n")
    else:
        # 설정 파일이 이미 있을 경우, 파일에서 경로 읽어오기
        with open(settings_file, 'r') as file:
            lines = file.readlines()
            image_file_path = lines[0].strip().split('=')[1]
            des_file_path = lines[1].strip().split('=')[1]
            #imgProgram = lines[2].strip().split('=')[1]

    #DB 생성
    if not os.path.exists(db_file):
        # SQLite 연결 및 테이블 생성
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE NAIimgInfo
                          (no INTEGER PRIMARY KEY AUTOINCREMENT,
                           tags TEXT,
                           filepath TEXT,
                           makeTime TEXT,
                           platform TEXT)''')
        conn.commit()
        conn.close()
        
    if firstStart: #이유는 모르겠는데 root.destroy() 하니까 최초실행 버그 고쳐짐. 
        root.destroy()

#태그 추출 함수
def read_info_from_image_stealth(image):
    # if tensor, convert to PIL image
    if hasattr(image, 'cpu'):
        image = image.cpu().numpy() #((1, 1, 1280, 3), '<f4')
        image = image[0].astype('uint8') #((1, 1280, 3), 'uint8')
        image = Image.fromarray(image)
    # trying to read stealth pnginfo
    width, height = image.size
    pixels = image.load()

    has_alpha = True if image.mode == 'RGBA' else False
    mode = None
    compressed = False
    binary_data = ''
    buffer_a = ''
    buffer_rgb = ''
    index_a = 0
    index_rgb = 0
    sig_confirmed = False
    confirming_signature = True
    reading_param_len = False
    reading_param = False
    read_end = False
    never_confirmed = True
    for x in range(width):
        for y in range(height):
            if has_alpha:
                r, g, b, a = pixels[x, y]
                buffer_a += str(a & 1)
                index_a += 1
            else:
                r, g, b = pixels[x, y]
            buffer_rgb += str(r & 1)
            buffer_rgb += str(g & 1)
            buffer_rgb += str(b & 1)
            index_rgb += 3
            if confirming_signature:
                if x * height + y > 120 and never_confirmed:
                    return ''
                if index_a == len('stealth_pnginfo') * 8:
                    decoded_sig = bytearray(int(buffer_a[i:i + 8], 2) for i in
                                            range(0, len(buffer_a), 8)).decode('utf-8', errors='ignore')
                    if decoded_sig in {'stealth_pnginfo', 'stealth_pngcomp'}:
                        #print(f"Found signature at {x}, {y}")
                        confirming_signature = False
                        sig_confirmed = True
                        reading_param_len = True
                        mode = 'alpha'
                        if decoded_sig == 'stealth_pngcomp':
                            compressed = True
                        buffer_a = ''
                        index_a = 0
                        never_confirmed = False
                    else:
                        read_end = True
                        break
                elif index_rgb == len('stealth_pnginfo') * 8:
                    decoded_sig = bytearray(int(buffer_rgb[i:i + 8], 2) for i in
                                            range(0, len(buffer_rgb), 8)).decode('utf-8', errors='ignore')
                    if decoded_sig in {'stealth_rgbinfo', 'stealth_rgbcomp'}:
                        #print(f"Found signature at {x}, {y}")
                        confirming_signature = False
                        sig_confirmed = True
                        reading_param_len = True
                        mode = 'rgb'
                        if decoded_sig == 'stealth_rgbcomp':
                            compressed = True
                        buffer_rgb = ''
                        index_rgb = 0
                        never_confirmed = False
            elif reading_param_len:
                if mode == 'alpha':
                    if index_a == 32:
                        param_len = int(buffer_a, 2)
                        reading_param_len = False
                        reading_param = True
                        buffer_a = ''
                        index_a = 0
                else:
                    if index_rgb == 33:
                        pop = buffer_rgb[-1]
                        buffer_rgb = buffer_rgb[:-1]
                        param_len = int(buffer_rgb, 2)
                        reading_param_len = False
                        reading_param = True
                        buffer_rgb = pop
                        index_rgb = 1
            elif reading_param:
                if mode == 'alpha':
                    if index_a == param_len:
                        binary_data = buffer_a
                        read_end = True
                        break
                else:
                    if index_rgb >= param_len:
                        diff = param_len - index_rgb
                        if diff < 0:
                            buffer_rgb = buffer_rgb[:diff]
                        binary_data = buffer_rgb
                        read_end = True
                        break
            else:
                # impossible
                read_end = True
                break
        if read_end:
            break
    geninfo = ''
    if sig_confirmed and binary_data != '':
        # Convert binary string to UTF-8 encoded text
        byte_data = bytearray(int(binary_data[i:i + 8], 2) for i in range(0, len(binary_data), 8))
        try:
            if compressed:
                decoded_data = gzip.decompress(bytes(byte_data)).decode('utf-8')
            else:
                decoded_data = byte_data.decode('utf-8', errors='ignore')
            geninfo = decoded_data
        except:
            pass
    return str(geninfo)

#이미지 가로 사이즈 체크
def checkImgWidth(img):
    #img = Image.open(image_path) # 이미지 열기
    width, _ = img.size # 이미지의 가로 사이즈 체크
    return width

#분류될 이미지경로의 빈폴더 제거
def remove_empty_folders(folder_path):
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):  # 폴더가 비어있으면
                    os.rmdir(dir_path)         # 폴더 삭제
                    print(f"폴더 삭제: {dir_path}")
            except Exception as e:
                print(f"에러 발생: {e}")

def checkPlatformName(img):
    #img = Image.open(png_file) #png 정보 취득을 위해서 이미지를 열어서
    metadata = img.info # 메타정보 취득 
    
    try:
        if 'Comment' in metadata: #NAI 이면
            return metadata['Software']
        elif 'parameters' in metadata: #StableDiffution 이면 
            return "StableDiffution"
        else:
            #img = Image.open(png_file)
            prompts = json.loads(read_info_from_image_stealth(img))
            comment = prompts['Comment']
            hide_comment_dict = json.loads(comment)
            return prompts['Software']
    except Exception as ex:
        return "none"

#이미지 이동 및 DB등록
def classification():
    png_files = [os.path.join(dirpath, filename)
                 for dirpath, dirnames, filenames in os.walk(image_file_path)
                 for filename in filenames if filename.endswith('.png')]
                 
    data_to_insert = []
    
    errorcount = 0
    
    for png_file in png_files:
        try:
            get_tags = ""
            prompts = ""
            makeTimeInfo = datetime.fromtimestamp(os.path.getmtime(png_file)).strftime('%y%m%d_%H%M%S') #파일이 생성된 시간
            platform = ""
            
            # 1. 파일의 생성날짜(YYmmdd)를 취득하고 파일을 desFilePath의 생성날짜 폴더로 이동
            #create_date = datetime.fromtimestamp(os.path.getctime(png_file)).strftime('%y%m%d') #파일이 마지막 생성된 날짜
            create_date = datetime.fromtimestamp(os.path.getmtime(png_file)).strftime('%y%m%d') #파일 최초 생성날짜(수정날짜)
            img = Image.open(png_file) #png 정보 취득을 위해서 이미지를 열어서
            des_folder = os.path.join(des_file_path,checkPlatformName(img), create_date)
            os.makedirs(des_folder, exist_ok=True)
            des_path = os.path.join(des_folder, os.path.basename(png_file))
            if not os.path.exists(des_path): #해당경로에 동일한 파일이 없는경우에만 실행
                if checkImgWidth(img)<=2000: #이미지가 기본생성 사이즈보다 작을때만 수행 (업스케일 이미지는 어짜피 태그 없음)
                    try:
                        #img = Image.open(png_file) #png 정보 취득을 위해서 이미지를 열어서
                        metadata = img.info # 메타정보 취득 
                        
                        if 'Comment' in metadata: #NAI 이면
                            print("NAI-----------------------")
                            
                            comment = metadata['Comment']
                            comment_dict = json.loads(comment)
                            
                            platform = metadata['Software']
                            get_tags = (
                                        f"Software : {metadata['Software']}\n" #NovelAI
                                        f"================================[prompt]=====================================\n{comment_dict['prompt']}\n"
                                        f"==============================[negativeprompt]===============================\n{comment_dict['uc']}\n"
                                        f"step : {comment_dict['steps']}\n"
                                        f"seed : {comment_dict['seed']}\n"
                                        f"CFG scale : {comment_dict['scale']}\n"
                                        f"Prompt Guidance Rescale : {comment_dict['cfg_rescale']}\n"
                                        f"height : {comment_dict['height']}\n"
                                        f"width : {comment_dict['width']}\n"
                                        f"Sampler : {comment_dict['sampler']}\n"
                                        f"SMEA : {comment_dict['sm']}\n"
                                        f"SMEA+DYN : {comment_dict['sm_dyn']}\n"
                                        f"Source : {metadata['Source']}\n" #Stable Diffusion XL C1E1DE52
                                        f"Title : {metadata['Title']}\n" #AI generated image
                                        )
                        elif 'parameters' in metadata: #StableDiffution 이면 
                            print("StableDiffution-----------------------")
                            platform = "StableDiffution"
                            comment = metadata['parameters']
                            get_tags = f"Software : StableDiffution \nPrompt : {metadata['parameters']}"
                        else: #둘다 없으면 스태가노 그라피로
                            print("Hided_EXIF-----------------------")
                            prompts = json.loads(read_info_from_image_stealth(img))
                            comment = prompts['Comment']
                            hide_comment_dict = json.loads(comment)
                            
                            platform = prompts['Software']
                            get_tags = (
                                        f"Software : {prompts['Software']}\n" #NovelAI
                                        f"================================[prompt]=====================================\n{hide_comment_dict['prompt']}\n"
                                        f"==============================[negativeprompt]===============================\n{hide_comment_dict['uc']}\n"
                                        f"step : {hide_comment_dict['steps']}\n"
                                        f"seed : {hide_comment_dict['seed']}\n"
                                        f"CFG scale : {hide_comment_dict['scale']}\n"
                                        f"Prompt Guidance Rescale : {hide_comment_dict['cfg_rescale']}\n"
                                        f"height : {hide_comment_dict['height']}\n"
                                        f"width : {hide_comment_dict['width']}\n"
                                        f"Sampler : {hide_comment_dict['sampler']}\n"
                                        f"SMEA : {hide_comment_dict['sm']}\n"
                                        f"SMEA+DYN : {hide_comment_dict['sm_dyn']}\n"
                                        f"Source : {prompts['Source']}\n" #Stable Diffusion XL C1E1DE52
                                        #f"Title : {prompts['Title']}\n" #AI generated image
                                        )
                            #print("[Debug]")
                            #print(prompts)
                            #get_tags = prompts["Description"]
                    except Exception as ex:
                        print('태그추출중 에러발생 - 빈값으로 넣습니다.', ex)
                        errorcount += 1
                        get_tags = ""
                        
                img.close() #이미지 객체 닫기
                os.rename(png_file, des_path) # 파일 이동
                # 2. 이동된 파일의 전체경로를 취득하여 mPath 변수에 저장
                mPath = os.path.abspath(des_path)
                
                print(f"filepath : {mPath}")
                data_to_insert.append((get_tags, mPath, makeTimeInfo, platform)) # 등록 목록에 추가한다
            else:
                print(f"파일 {os.path.basename(png_file)}이 이미 존재합니다. 스킵합니다.")
        except Exception as ex:
            print('등록중 에러발생', ex)
            traceback.print_exc()
        
        
    #위에서 만든 목록의 데이터를 db에 등록한다.
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.executemany('INSERT INTO NAIimgInfo (tags, filepath, makeTime, platform) VALUES (?, ?, ?, ?)', data_to_insert)
    conn.commit()
    conn.close()
    
    remove_empty_folders(image_file_path) #정리완료된 빈폴더 정리
    print(f"태그추출 실패 건수 : {errorcount}")
    



