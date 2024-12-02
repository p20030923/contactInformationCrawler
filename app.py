import re
import sqlite3
import tkinter
from tkinter import messagebox
from tkinter import scrolledtext
import requests

def connect_db() -> None:
    """建立一個資料庫連接"""
    conn = sqlite3.connect('contacts.db')
    conn.row_factory = sqlite3.Row  # 使查詢結果可以用欄位名稱來存取
    return conn

def insert_text() -> None:
    """ScrolledText 顯示"""
    scrolled_text.delete(1.0, tkinter.END) # 若重複抓取則先清空畫面
    url =  entry.get()
    if url != "https://csie.ncut.edu.tw/content.php?key=86OP82WJQO":
        messagebox.showerror("網路錯誤", "無法取得網頁 : 404")
    else:
        content = f"{'姓名':{chr(12288)}<4}{'職稱':{chr(12288)}<16}Email" + "\n" + "-" * 60 + "\n"
        for i in range(len(name_list)):
            content += f'{name_list[i]}\t{job_list[i]}\t\t\t\t{emails_list[i]}\n'
        scrolled_text.insert(tkinter.END, content)

# 使用 with 來處理資料庫連接與建立
with connect_db() as conn:
    cursor = conn.cursor()  # 建立 cursor 物件
    cursor.execute("""CREATE TABLE IF NOT EXISTS contacts (
        iid INTEGER PRIMARY KEY,    -- 編號 主鍵，唯一且不可為 NULL
        name TEXT NOT NULL,         -- 姓名 必須有值
        title TEXT NOT NULL,        -- 職稱 必須有值
        email TEXT NOT NULL UNIQUE  -- Email 必須有值，唯一
    )""")

URL = "https://csie.ncut.edu.tw/content.php?key=86OP82WJQO"

response = requests.get(URL)
# 描述 Email 的正規表示式物件 pattern
pattern = re.compile(r'\b[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
# pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
match_list = pattern.findall(response.text)  # 從網頁原始碼中尋找所有 Email
seen = set() # 由 set 確認去除重複的 Email 且不改變順序
emails_list = []
for item in match_list:
    if item not in seen:
        emails_list.append(item)
        seen.add(item)

# 描述姓名的正規表示式物件 pattern
pattern = re.compile(r'<div class="member_name"><a href="[^"]+">([^<]+)</a>')
match_list = pattern.findall(response.text)  # 從網頁原始碼中尋找所有姓名
name_list = match_list
name_list = [item.strip() for item in name_list]

# 描述職稱的正規表示式物件 pattern
pattern = re.compile(r'<div class="member_info_content">([^<]+)</div>')
match_list = pattern.findall(response.text)  # 從網頁原始碼中尋找所有職稱
group_size = 4  # 去除多餘資料
job_list = [match_list[i] for i in range(0, len(match_list), group_size)]

for i in range(len(name_list)):
    print(f'{name_list[i]} {job_list[i]} {emails_list[i]}')
    # 使用 with 來處理資料庫連接與寫入
    with connect_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO contacts (name, title, email) VALUES (?, ?, ?)", (name_list[i], job_list[i], emails_list[i]))
        except sqlite3.DatabaseError as e:
            print(f"資料庫操作發生錯誤: {e}")
        except Exception as e:
            print(f'發生其它錯誤 {e}')
        conn.commit()  # 寫入資料
    print("資料已寫入")

# 建立主視窗
form = tkinter.Tk()
form.title("聯絡資訊爬蟲")
form.geometry("640x480")

# 設置行列權重
form.columnconfigure(1, weight=1)  # 讓 URL 輸入框可水平拉伸
form.rowconfigure(1, weight=1)  # 讓 ScrolledText 可垂直拉伸

# 固定 URL 標籤和預設輸入框
url_label = tkinter.Label(form, text="URL:")
url_label.grid(row=0, column=0, padx=5, pady=5)
entry = tkinter.Entry(form, width=75)
entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
entry.insert(0, "https://csie.ncut.edu.tw/content.php?key=86OP82WJQO")

# 抓取按鈕
fetch_button = tkinter.Button(form, text="抓取", command=insert_text)
fetch_button.grid(row=0, column=2, padx=5, pady=5)

# 使用 ScrolledText
scrolled_text = scrolledtext.ScrolledText(form, width=87, height=33, wrap=tkinter.WORD)
scrolled_text.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

# 執行主循環
form.mainloop()