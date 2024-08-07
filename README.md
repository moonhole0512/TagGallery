## <프로그램 사용목적 및 정보>  
-NAI, stablediffusion 등에서 만들어진 이미지 정리 및 태그 검색  
-PNG 확장자의 파일만 지원 (jpeg로 만들어진파일을 png로 변환해도 사용가능한경우 있음)  
-태그 추출시 exif가 없는 경우에도 습득  
-가로 2000px 넘는 이미지는 태그 추출하지 않음 (프로그램 멈출가능성 및 업스케일 이미지는 원본 생성 태그가 지워져서 추출불가)    


## <실행방법>  
https://github.com/moonhole0512/TagGallery/releases/tag/TagGallery_v1.0  
릴리즈에서 실행파일을 다운받습니다.  
<img width="167" alt="1" src="https://github.com/user-attachments/assets/6b0590f7-9424-42fb-9ee4-1dbb47174430">  

프로그램을 처음실행하면 분류할 폴더를 지정해야합니다.
AI로 생성한 이미지가 들어있는 폴더를 지정해주세요.
![image](https://github.com/user-attachments/assets/05e7fc7f-cff2-49b8-8087-162a470acbc0)

정리된 이미지가 저장될 폴더를 지정해주세요.
![image](https://github.com/user-attachments/assets/7f2a8ebb-38c5-4585-9516-9f90fe0aac1d)

정리가 완료되면 다음과 같이 프로그램이 실행됩니다.
<img width="1007" alt="4" src="https://github.com/user-attachments/assets/3ce9ae85-303e-43b5-9891-061d02481029">

## <태그 정보 확인>
이미지를 선택하면 오른쪽 하단에 이미지 생성에 사용된 정보가 표기됩니다. 예시는 제일 아래쪽에 붙여두겠습니다.  
(프롬프트, 네거티브 프롬프트, step 샘플러, 등)  
![image](https://github.com/user-attachments/assets/c6012eca-444c-4f74-b74a-856176caedea)

## <검색기능>
쉼표(,)로 구분하여 태그검색을 진행합니다.  
아래의 경우 holo 와 marin 을 포함한 모든 결과를 표시합니다. (ex: hololive, marina)  
<현재 고급검색은 불가능합니다. 누가 대신 만들어주면 좋겠어요.>  
<img width="708" alt="image" src="https://github.com/user-attachments/assets/84812f95-888d-42b3-95d6-943c0fe59563">  

정렬은 생성된이미지의 날짜기준으로 "오름차순,내림차순,랜덤"을 지원합니다.  
![image](https://github.com/user-attachments/assets/7c98be9e-ead7-490d-b85d-d7197b8eda4d)  

NAI만 검색하거나 DIF(StableDiffusion), ALL, None(태그추출 실패) 로 검색가능합니다.  
![image](https://github.com/user-attachments/assets/03d2492e-11ab-4b40-b8ca-b26871229a39)  

## <페이지이동>
이전, 다음 버튼으로 이동하거나 직접 페이지를 숫자로 입력후 엔터로 이동가능합니다.  
![image](https://github.com/user-attachments/assets/8eeb8a58-d387-4fc8-b51c-ff0ce54567ae)  

## <전체화면 보기>
오른쪽에 표시되는 이미지를 더블클릭하면 전체화면으로 감상할 수 있습니다. 순서는 검색결과 순으로 표시됩니다.  
왼쪽 방향키 - 이전 이미지  
오른쪽 방향키 - 다음 이미지  
ESC - 전체화면 종료.  
![image](https://github.com/user-attachments/assets/a954e199-6626-4877-837c-1e7ea2508c6c)  

## <이미지 삭제>
왼쪽의 작은 이미지를 선택하고 키보드의 delete를 누르면 확인창이 나오고  
나오는 팝업창에서 확인을 누르면 해당 이미지를 삭제합니다.  
![image](https://github.com/user-attachments/assets/a0b5305b-672a-41b7-9400-343cd2945c3d)  

## <정리된 폴더>
정리된 이미지는 아래와 같이 지정된 폴더에 이미지가 생성된 날짜와 NAI인지 StableDiffusion인지에따라 정리됩니다.  
태그 추출에 실패한 이미지는 None폴더에 저장됩니다.  
![image](https://github.com/user-attachments/assets/7af57115-681a-49b9-ae16-64cf9293251f)  
![image](https://github.com/user-attachments/assets/4bf88fa6-f09d-43c3-8d89-0d1a4d496bb4)  

## <태그정보 표기 예시>  
Software : NovelAI  
================================[prompt]=====================================  
1girl, himari (blue archive), {{artist:kakure eria}}, blue archive (copyright), black gloves, flower, gloves, hair flower, hair ornament, hair tubes, hairband, halo, jacket, loafers, pointy ears, powered wheelchair, purple eyes, robe, shoes, striped, striped hairband, wheelchair, white hair, white jacket, great quality, aesthetic, absurdres, uncensored  
  
==============================[negativeprompt]===============================  
{{{{{{worst quality, bad quality}}}}}}, {{{{bad hands}}}}, {{{bad eyes}}},{{{undetailed eyes}}}},{{abs,rib,abdominal,rib line,muscle definition,muscle separation,sharp body line}},{{wide hips,narrow waist}}, text, error, extra digit, fewer digits, jpeg artifacts, signature, watermark, username, reference, {{unfinished}},{{unclear fingertips}}, {{twist}}, {{Squiggly}}, {{Grumpy}} , {{incomplete}}, {{Imperfect Fingers}}, Disorganized colors ,Cheesy, {{very displeasing}}, {{mess}}, {{Approximate}}, {{Sloppiness}} ,{{{{{futanari, dickgirl}}}}},  
step : 28  
seed : 2129564675  
CFG scale : 5.0  
Prompt Guidance Rescale : 0.0  
height : 1216  
width : 832  
Sampler : k_euler_ancestral  
SMEA : True  
SMEA+DYN : False  
Source : Stable Diffusion XL C1E1DE52  
Title : AI generated image  


## <초기화방법>
settings.txt (처음에 지정한 폴더 경로 기록)  
image_gallery.db (이미지 정리한 db)  
실행파일 경로에 상기 두개의 파일이 생성되어있을겁니다. 두개를 지우면 프로그램은 초기화됩니다.  
![image](https://github.com/user-attachments/assets/20704fc6-6d6f-4565-b803-5bac3513cf33)
