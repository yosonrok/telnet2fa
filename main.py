import telnetlib
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# Telnet 目标主机信息
HOST = "220.130.112.242"


def telnet_login(host, username, password, mfa_code, result_label, progress_bar, countdown_label):
    """Telnet 登录操作，并显示登录进度"""
    try:
        # 连接到 Telnet 服务器
        tn = telnetlib.Telnet(host)

        # 发送用户名
        tn.read_until(b"login: ")
        result_label.config(text="送出帳號...")
        tn.write(username.encode('ascii') + b"\n")
        time.sleep(1)

        # 发送密码
        tn.read_until(b"password: ")
        result_label.config(text="送出密碼...")
        tn.write(password.encode('ascii') + b"\n")
        time.sleep(1)

        # 发送 MFA 验证码
        tn.read_until(b"token code: ")
        result_label.config(text="送出驗證碼...")
        tn.write(mfa_code.encode('ascii') + b"\n")
        result_label.update()  # 强制刷新 GUI 显示

        # 等待服务器响应
        time.sleep(2)
        output = tn.read_very_eager()

        if b"Authentication is successful" in output:
            result_label.config(text="認證成功，請重新連接。")
            start_countdown(progress_bar, countdown_label)  # 开始倒计时
        else:
            result_label.config(text="認證失敗，請檢查用戶名、密碼或 MFA 驗證碼。")

        tn.close()

    except Exception as e:
        result_label.config(text=f"Telnet 连接失败: {e}")


def on_submit(username_entry, password_entry, mfa_entry, result_label, progress_bar, countdown_label):
    """获取用户输入并进行 Telnet 登录"""
    username = username_entry.get()
    password = password_entry.get()
    mfa_code = mfa_entry.get()

    # 检查是否填写完整
    if not username or not password or not mfa_code:
        messagebox.showwarning("錯誤", "請填寫所有欄位！")
        return

    # 清空结果标签并开始登录
    result_label.config(text="開始 Telnet 連接...")
    result_label.update()  # 更新 GUI 显示
    telnet_login(HOST, username, password, mfa_code, result_label, progress_bar, countdown_label)

    # 清空 MFA 输入框
    mfa_entry.delete(0, tk.END)


def start_countdown(progress_bar, countdown_label):
    """启动 60 秒倒计时并更新进度条"""
    countdown_label.config(text="60 秒倒數...")
    progress_bar['value'] = 0  # 重置进度条
    update_progress(progress_bar, countdown_label, 60)  # 开始倒计时


def update_progress(progress_bar, countdown_label, remaining_time):
    """更新倒计时进度条"""
    if remaining_time > 0:
        progress_bar['value'] += 100 / 60  # 更新进度条
        countdown_label.config(text=f"{remaining_time} 秒倒數中...")
        progress_bar.update()  # 更新进度条显示
        countdown_label.after(1000, update_progress, progress_bar, countdown_label, remaining_time - 1)  # 每秒更新
    else:
        countdown_label.config(text="倒數完成。")
        reset_progress(progress_bar, countdown_label)  # 倒计时结束后重置进度条和标签


def reset_progress(progress_bar, countdown_label):
    """倒计时结束后重置进度条和倒计时标签"""
    countdown_label.after(1000, lambda: countdown_label.config(text=""))  # 1秒后清空倒计时标签
    progress_bar['value'] = 0  # 重置进度条
    progress_bar.update()  # 更新进度条显示


def create_gui():
    """创建 GUI 界面"""
    root = tk.Tk()
    root.title("Telnet 登入")
    root.geometry("400x300")  # 固定窗口大小
    root.resizable(False, False)  # 禁止调整窗口大小

    # 用户名标签和输入框
    tk.Label(root, text="用戶名:").pack(pady=5)
    username_entry = tk.Entry(root, width=30)
    username_entry.pack(pady=5)

    # 密码标签和输入框
    tk.Label(root, text="密碼:").pack(pady=5)
    password_entry = tk.Entry(root, width=30, show="*")
    password_entry.pack(pady=5)

    # MFA 验证码标签和输入框
    tk.Label(root, text="MFA 驗證碼:").pack(pady=5)
    mfa_entry = tk.Entry(root, width=30)
    mfa_entry.pack(pady=5)

    # MFA 验证码输入框按 Enter 键执行
    mfa_entry.bind("<Return>",
                   lambda event: on_submit(username_entry, password_entry, mfa_entry, result_label, progress_bar,
                                           countdown_label))

    # 确认按钮
    submit_button = tk.Button(root, text="確認",
                              command=lambda: on_submit(username_entry, password_entry, mfa_entry, result_label,
                                                        progress_bar, countdown_label))
    submit_button.pack(pady=10)

    # 结果显示区域
    result_label = tk.Label(root, text="", wraplength=400, justify="left")
    result_label.pack(pady=10)

    # 倒计时进度条
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode='determinate')
    progress_bar.pack(pady=10)

    # 倒计时显示
    countdown_label = tk.Label(root, text="", wraplength=400, justify="center")
    countdown_label.pack(pady=10)

    # 启动 GUI 循环
    root.mainloop()


if __name__ == "__main__":
    create_gui()
