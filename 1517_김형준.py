import subprocess, sys

def ensure_package(pkg_name, import_name=None):
    if import_name is None:
        import_name = pkg_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[INFO] {pkg_name} 패키지가 없어 설치합니다...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])
        print(f"[INFO] {pkg_name} 설치 완료!")

# 필요한 패키지들 자동 설치
ensure_package("pillow", "PIL")

import tkinter as tk
import json
from pathlib import Path
from PIL import Image, ImageTk
from tkinter import messagebox,simpledialog,ttk
import webbrowser as br

Val = {
    "ItemList" : [],
    "cwd" : None,
}

Root = Path.cwd() / 'Data'
Val["cwd"] = Root
Root.mkdir(exist_ok = True)
FolderOpenImagePath = Path("image") / "folder_open.png"
FolderCloseImagePath = Path("image") / "folder_close.png"
FileOpenImagePath = Path("image") / "file_open.png"
FileCloseImagePath = Path("image") / "file_close.png"

FolderOpenImage = Image.open(FolderOpenImagePath)
FolderCloseImage = Image.open(FolderCloseImagePath)
FileOpenImage = Image.open(FileOpenImagePath)
FileCloseImage = Image.open(FileCloseImagePath)

def ReadAll():
    for a in Val["cwd"].iterdir():
        if a.is_dir() == True:
            Val["ItemList"].append({"type" : "folder","name" : a,"Loc" : None})
        elif a.is_file() == True:
            Val["ItemList"].append({"type" : "file","name" : a,"Loc" : None})

def LoadJson(path):
    return json.loads(path.read_text(encoding="utf-8"))

def Save2Json(path,data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2),encoding="utf-8")

def Locate(SearchText = ""):
    sy,gapy = 100,80
    Loc = [165,350,535,720]
    cnt = -1
    ycnt = 0
    Val["ItemList"] = []
    canvas = tk.Canvas(Win,bg = "#ffffff")
    canvas.pack(fill="both",expand=True)
    canvas.delete("all")
    canvas.focus_set()
    canvas.selected_img = None
    canvas.selected_rect = None
    canvas.selected_type = None
    canvas.selected_name = None
    ReadAll()
    SearchVal = tk.StringVar(value=SearchText)
    def Search(event=None):
        Text = SearchVal.get().strip()
        canvas.destroy()
        Locate(Text)
        return "break"
    SearchAsk = tk.Entry(canvas,textvariable=SearchVal,width=30)
    SearchButton = tk.Button(canvas,text="검색",command=Search)
    canvas.create_window(720,30,window=SearchAsk)
    canvas.create_window(840,30,window=SearchButton)
    SearchAsk.bind("<Return>",Search)
    def AddFolder():
        FName = simpledialog.askstring('폴더 추가','폴더명 : ')
        if not FName:
            return
        (Val["cwd"] / FName).mkdir(parents=True,exist_ok=True)
        Val["ItemList"] = []
        canvas.destroy()
        Locate("")
    def AddUrl():
        Askwin = tk.Toplevel(canvas)
        Askwin.title('URL 추가')
        Askwin.geometry('520x380')
        Askwin.resizable(False,False)
        Askwin.grab_set()
        ttk.Label(Askwin, text="이름").grid(row=0, column=0, sticky="w")
        ChugaTitle = tk.Entry(Askwin,width=48)
        ChugaTitle.grid(row=1, column=0, sticky="w")
        ttk.Label(Askwin, text="Url").grid(row=2, column=0, sticky="w")
        ChugaUrl = tk.Entry(Askwin,width=48)
        ChugaUrl.grid(row=3, column=0, sticky="w")
        ttk.Label(Askwin, text="메모").grid(row=4, column=0, sticky="w")
        ChugaMemo = tk.Text(Askwin, width=48, height=10, wrap="word")
        ChugaMemo.grid(row=5, column=0, sticky="nsew")
        def PressOk():
            CChugaTitle = ChugaTitle.get().strip()
            if not CChugaTitle:
                messagebox.showwarning('경고창',message='이름을 입력하세요')
                return
            CChugaUrl = ChugaUrl.get().strip()
            if not CChugaUrl:
                messagebox.showwarning('경고창',message='URL을 입력하세요')
                return
            CChugaMemo = ChugaMemo.get("1.0","end-1c").strip()
            if not CChugaMemo:
                messagebox.showwarning('경고창',message='메모를 입력하세요')
                return
            SaveData = {
                "Name" : CChugaTitle,
                "Url" : CChugaUrl,
                "Memo" : CChugaMemo
            }
            Save2Json(Val["cwd"] / (CChugaTitle+".json"),SaveData)
            Askwin.destroy()
            Val["ItemList"] = []
            canvas.destroy()
            Locate("")
        OkButton = ttk.Button(Askwin,text='저장',command=PressOk)
        OkButton.grid(row=6,column=0,sticky='e')
    AddMenu = tk.Menu(canvas,tearoff=0)
    AddMenu.add_command(label='폴더 추가',command=AddFolder)
    AddMenu.add_command(label='URL 추가',command=AddUrl)
    def AddFloat(event):
        try:
            AddMenu.tk_popup(event.x_root,event.y_root)
        finally:
            AddMenu.grab_release()
    def GoUp():
        if Val["cwd"] == Root:
            return
        Val["cwd"] = Val["cwd"].parent
        Val["ItemList"] = []
        canvas.destroy()
        Locate("")
    def TabGoUp(event):
        if Val["cwd"] == Root:
            return
        Val["cwd"] = Val["cwd"].parent
        Val["ItemList"] = []
        canvas.destroy()
        Locate("")
        return "break"
    UpButton = tk.Button(canvas,text="   <   ",command=GoUp)
    #print(Val["cwd"])
    canvas.create_window(30,30,window=UpButton)
    def ClickBack(event):
        Now = canvas.find_withtag("current")
        if Now:
            if "Folder/File" in canvas.gettags(Now[0]):
                return
        if canvas.selected_img is not None:
            if canvas.selected_type == "folder":
                canvas.itemconfig(canvas.selected_img,image=FolderCloseIcon)
            elif canvas.selected_type == "file":
                canvas.itemconfig(canvas.selected_img,image=FileCloseIcon)
            canvas.selected_img = None
        if canvas.selected_rect is not None:
            canvas.itemconfig(canvas.selected_rect, outline="#FFFFFF")
            canvas.selected_rect = None
        canvas.selected_type = None
        canvas.selected_name = None
    def Edit(event=None):
        if canvas.selected_name is None or canvas.selected_type is None:
            return "break"
        EditPath = canvas.selected_name
        if canvas.selected_type == "folder":
            PrevPath = EditPath.name
            CFName = simpledialog.askstring('폴더명 수정','수정 폴더명 : ',initialvalue=PrevPath)
            if not CFName:
                return "break"
            ChangePath = EditPath.parent / CFName
            EditPath.rename(ChangePath)
            Val["ItemList"] = []
            canvas.destroy()
            Locate(SearchText)
            return "break"
        elif canvas.selected_type == "file":
            Data = LoadJson(EditPath)
            Editwin = tk.Toplevel(canvas)
            Editwin.title('URL 수정')
            Editwin.geometry('520x380')
            Editwin.resizable(False,False)
            Editwin.grab_set()

            PrevName = tk.StringVar(value=Data.get("Name",EditPath.stem))
            PrevUrl = tk.StringVar(value=Data.get("Url",""))

            ttk.Label(Editwin, text="이름").grid(row=0, column=0, sticky="w")
            ChugaTitle = tk.Entry(Editwin,textvariable=PrevName,width=48)
            ChugaTitle.grid(row=1, column=0, sticky="w")
            ttk.Label(Editwin, text="Url").grid(row=2, column=0, sticky="w")
            ChugaUrl = tk.Entry(Editwin,textvariable=PrevUrl,width=48)
            ChugaUrl.grid(row=3, column=0, sticky="w")
            ttk.Label(Editwin, text="메모").grid(row=4, column=0, sticky="w")
            ChugaMemo = tk.Text(Editwin, width=48, height=10, wrap="word")
            ChugaMemo.grid(row=5, column=0, sticky="nsew")
            ChugaMemo.insert("1.0",Data.get("Memo",""))
            def PressOk():
                CChugaTitle = ChugaTitle.get().strip()
                if not CChugaTitle:
                    messagebox.showwarning('경고창',message='이름을 입력하세요')
                    return
                CChugaUrl = ChugaUrl.get().strip()
                if not CChugaUrl:
                    messagebox.showwarning('경고창',message='URL을 입력하세요')
                    return
                CChugaMemo = ChugaMemo.get("1.0","end-1c").strip()
                if not CChugaMemo:
                    messagebox.showwarning('경고창',message='메모를 입력하세요')
                    return
                NewData = {
                    "Name" : CChugaTitle,
                    "Url" : CChugaUrl,
                    "Memo" : CChugaMemo
                }
                PrevPath = EditPath
                NowPath = PrevPath.with_name(CChugaTitle+".json")
                PrevPath.rename(NowPath)
                Save2Json(NowPath,NewData)
                Editwin.destroy()
                Val["ItemList"] = []
                canvas.destroy()
                Locate(SearchText)
            OkButton = ttk.Button(Editwin,text='저장',command=PressOk)
            OkButton.grid(row=6,column=0,sticky='e')
            return "break"
    canvas.bind("<Button-1>",ClickBack)
    canvas.bind("<Button-3>",AddFloat)
    canvas.bind("<Tab>",TabGoUp)
    canvas.bind("<F2>",Edit)
    def Functions(Img,Rect,Type,Name):
        def On(event):
            if Type == "folder":
                canvas.itemconfig(Img,image=FolderOpenIcon)
            elif Type == "file":
                canvas.itemconfig(Img,image=FileOpenIcon)
        def Off(event):
            if canvas.selected_img == Img:
                return
            if Type == "folder":
                canvas.itemconfig(Img,image=FolderCloseIcon)
            elif Type == "file":
                canvas.itemconfig(Img,image=FileCloseIcon)
        def OneClick(event):
            if canvas.selected_img is not None:
                if canvas.selected_type == "folder":
                    canvas.itemconfig(canvas.selected_img,image=FolderCloseIcon)
                elif canvas.selected_type == "file":
                    canvas.itemconfig(canvas.selected_img,image=FileCloseIcon)
            if canvas.selected_rect is not None:
                canvas.itemconfig(canvas.selected_rect, outline="#FFFFFF")
            canvas.selected_img = Img
            canvas.selected_type = Type
            canvas.selected_name = Name

            if Type == "folder":
                canvas.itemconfig(Img,image=FolderOpenIcon)
            elif canvas.selected_type == "file":
                canvas.itemconfig(Img,image=FileOpenIcon)

            if Rect is not None:
                canvas.selected_rect = Rect
                canvas.itemconfig(Rect,outline = "#A47764")
            else:
                canvas.selected_rect = None
        def TwoClick(event):
            if Type == "folder":
                Val["cwd"] = Name
                Val["ItemList"] = []
                canvas.destroy()
                Locate("")
            elif Type == "file":
                Data = LoadJson(Name)
                br.open(Data.get("Url").strip(),new = 2)
        def ShowInfo(event):
            if Type == "file":
                Data = LoadJson(Name)
                Infowin = tk.Toplevel(canvas)
                Infowin.title('URL 정보')
                Infowin.geometry('520x380')
                Infowin.resizable(False,False)
                Infowin.grab_set()
                ttk.Label(Infowin,text="이름").grid(row=0,column=0,sticky="w")
                ttk.Label(Infowin,text=Data.get("Name","")).grid(row=1,column=0,sticky="w")
                ttk.Label(Infowin,text="Url").grid(row=2,column=0,sticky="w")
                Url = ttk.Label(Infowin,text=Data.get("Url",""),foreground="blue",cursor="hand2")
                Url.grid(row=3,column=0,sticky="w")
                ttk.Label(Infowin,text="메모").grid(row=4,column=0,sticky="w")
                Memo = tk.Text(Infowin,width=48,height=10,wrap="word")
                Memo.grid(row=5,column=0,sticky="nsew")
                Memo.insert("1.0",Data.get("Memo",""))

                def OpenUrl(event):
                    br.open(Data.get("Url").strip(),new = 2)
                Url.bind("<Button-1>",OpenUrl)
            else:
                return
        def EnterKey(event = None):
            if canvas.selected_name is None and canvas.selected_type is None:
                SearchAsk.focus_set()
                SearchAsk.icursor(tk.END)
                return "break"
            if canvas.selected_type == "folder" and canvas.selected_name is not None:
                Val["cwd"] = canvas.selected_name
                Val["ItemList"] = []
                canvas.destroy()
                Locate("")
                return "break"
        canvas.bind("<Shift-Return>",ShowInfo)
        canvas.bind("<Return>",EnterKey)
        return On,Off,OneClick,TwoClick
    def FindSearch():
        return list(Root.rglob("*.json"))
    SearchLow = SearchText.lower().strip()
    ShowItem = []
    if not SearchLow:
        ShowItem = Val["ItemList"]
    else:
        cand = []
        for Url in FindSearch():
            Data = LoadJson(Url)
            NameVal = Url.stem.lower()
            MemoVal = str(Data.get("Memo","")).lower()
            Ok = SearchLow in NameVal or SearchLow in MemoVal
            if Ok:
                cand.append({"type":"file", "name":Url, "Loc":None})
        if not cand:
            messagebox.showerror("검색","검색 결과가 없습니다.")
            SearchVal.set("")
            canvas.destroy()
            Locate("")
            return
        ShowItem = cand
    for item in ShowItem:
        cnt+=1
        if cnt>=4:
            cnt = 0
            ycnt+=1
        if item["type"] == "folder":
            img = canvas.create_image(Loc[cnt],sy+(100+gapy)*ycnt,image = FolderCloseIcon)
        elif item["type"] == "file":
            img = canvas.create_image(Loc[cnt],sy+(100+gapy)*ycnt,image = FileCloseIcon)
        canvas.create_text(Loc[cnt],sy+(100+gapy)*ycnt+60,text=item["name"].name,font=('Arial',10))
        canvas.addtag_withtag("Folder/File", img)
        
        rect = canvas.create_rectangle(Loc[cnt]-70,sy+(100+gapy)*ycnt-70,Loc[cnt]+70,sy+(100+gapy)*ycnt+70,fill="#FFFFFF",outline="#FFFFFF",width=5)
        canvas.tag_lower(rect)

        On,Off,OneClick,TwoClick = Functions(img,rect,item["type"],item["name"])
        canvas.tag_bind(img,"<Enter>",On)
        canvas.tag_bind(img,"<Leave>",Off)
        canvas.tag_bind(img,"<Button-1>",OneClick)
        canvas.tag_bind(img,"<Double-Button-1>",TwoClick)
Win = tk.Tk()
Win.title("메모 앱")
Win.geometry("900x700")
Win.resizable(False, False)

FolderOpenIcon = ImageTk.PhotoImage(FolderOpenImage.resize((100,100)))
FolderCloseIcon = ImageTk.PhotoImage(FolderCloseImage.resize((100,100)))
FileOpenIcon = ImageTk.PhotoImage(FileOpenImage.resize((100,100)))
FileCloseIcon = ImageTk.PhotoImage(FileCloseImage.resize((100,100)))

Locate("")

Win.mainloop()