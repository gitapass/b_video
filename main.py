import requests
import re
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import threading

def extract_bvid(url):
    """
    从哔哩哔哩视频链接中提取 bvid
    """
    match = re.search(r"video/(BV[0-9a-zA-Z]+)", url)
    if match:
        return match.group(1)
    else:
        messagebox.showerror("错误", "无法从链接中提取 bvid！")
        return None

def get_video_info(bvid):
    """
    通过 bvid 获取视频信息（包括 cid）
    """
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": f"https://www.bilibili.com/video/{bvid}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        messagebox.showerror("错误", f"获取视频信息失败！状态码: {response.status_code}")
        return None

    data = response.json()
    if data.get("code") != 0:
        messagebox.showerror("错误", f"API 返回错误: {data.get('message')}")
        return None

    return data

def get_play_url(bvid, cid, qn):
    """
    通过 bvid 和 cid 获取视频的播放 URL
    """
    url = f"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn={qn}&type=&otype=json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": f"https://www.bilibili.com/video/{bvid}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        messagebox.showerror("错误", f"获取播放 URL 失败！状态码: {response.status_code}")
        return None

    data = response.json()
    if data.get("code") != 0:
        messagebox.showerror("错误", f"API 返回错误: {data.get('message')}")
        return None

    return data

def download_bilibili_video(video_url, output_file, progress_bar, status_label):
    """
    下载视频并保存到本地
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.bilibili.com/"
    }
    response = requests.get(video_url, headers=headers, stream=True)

    if response.status_code != 200:
        messagebox.showerror("错误", f"下载视频失败！状态码: {response.status_code}")
        return

    total_size = int(response.headers.get("content-length", 0))
    downloaded_size = 0

    with open(output_file, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded_size += len(chunk)
                progress = int((downloaded_size / total_size) * 100)
                progress_bar["value"] = progress
                status_label.config(text=f"下载中: {progress}%")
                root.update_idletasks()  # 更新 GUI

    messagebox.showinfo("成功", f"视频下载成功！保存为: {output_file}")
    status_label.config(text="下载完成")  # 下载完成后更新状态

def start_download():
    """
    开始下载视频
    """
    video_url = entry_url.get()  # 获取用户输入的链接
    if not video_url:
        messagebox.showerror("错误", "请输入哔哩哔哩视频链接！")
        return

    # 获取用户选择的分辨率
    qn = qn_options[qn_var.get()]

    # 提取 bvid
    bvid = extract_bvid(video_url)
    if not bvid:
        return

    # 获取视频信息（包括 cid）
    video_info = get_video_info(bvid)
    if not video_info:
        return

    cid = video_info["data"]["cid"]

    # 获取视频播放 URL
    play_info = get_play_url(bvid, cid, qn)
    if not play_info:
        return

    video_url = play_info["data"]["durl"][0]["url"]

    # 选择保存路径
    output_file = filedialog.asksaveasfilename(
        defaultextension=".mp4",
        filetypes=[("MP4 文件", "*.mp4"), ("所有文件", "*.*")],
        title="保存视频"
    )
    if not output_file:
        return

    # 重置进度条和状态标签
    progress_bar["value"] = 0
    status_label.config(text="准备下载...")
    root.update_idletasks()  # 更新 GUI

    # 使用多线程下载视频
    download_thread = threading.Thread(
        target=download_bilibili_video,
        args=(video_url, output_file, progress_bar, status_label)
    )
    download_thread.start()

# 创建 GUI 界面
root = tk.Tk()
root.title("哔哩哔哩视频下载器")
root.geometry("400x250")

# 输入框和标签
label_url = tk.Label(root, text="哔哩哔哩视频链接:")
label_url.pack(pady=5)

entry_url = tk.Entry(root, width=50)
entry_url.pack(pady=5)

# 分辨率选项
label_qn = tk.Label(root, text="选择分辨率:")
label_qn.pack(pady=5)

# 分辨率选项值
qn_options = {
    "360P": 16,
    "480P": 32,
    "720P": 64,
    "1080P": 80,
    "1080P+": 112,
    "1080P 60FPS": 116
}

qn_var = tk.StringVar()
qn_var.set("1080P")  # 默认分辨率

# 下拉菜单
qn_menu = ttk.Combobox(root, textvariable=qn_var, values=list(qn_options.keys()))
qn_menu.pack(pady=5)

# 下载按钮
button_download = tk.Button(root, text="下载视频", command=start_download)
button_download.pack(pady=10)

# 进度条
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=5)

# 状态标签
status_label = tk.Label(root, text="等待下载...")
status_label.pack(pady=5)

# 运行主循环
root.mainloop()