import tkinter
import tkinter.filedialog
import pymupdf
import json
import os
from PIL import Image, ImageTk


# 视图类
class WidVision:
    # 创建成员变量
    def __init__(self, wid: tkinter.Tk):
        self._wid = wid
        self._index = 0
        self._file = ""
        self._txt_page = tkinter.StringVar(value="-")
        self._val_check = tkinter.BooleanVar(value=True)
        self._val_scale = tkinter.DoubleVar(value=1.0)

        self.switch_top(True)
        self.switch_alpha(True)

        wid.bind("<FocusIn>", lambda event: self.switch_alpha(True))
        wid.bind("<FocusOut>", lambda event: self.switch_alpha(False))
        wid.protocol("WM_DELETE_WINDOW", self.on_event_Close)

        self.init_wid(wid)
        wid.update_idletasks()
        self.read_conf()

    # 初始化窗口
    def init_wid(self, wid):
        self._label = tkinter.Label(wid)
        self._label.pack(fill="both", expand=True)

        self._label.bind("<Button-1>", lambda event: self.on_click_prev())
        self._label.bind("<Button-3>", lambda event: self.on_click_next())

        tkinter.Label(wid, textvariable=self._txt_page).pack(side="left", padx=10)
        tkinter.Button(wid, text="上一页", command=self.on_click_prev).pack(
            side="left", padx=10
        )
        tkinter.Button(wid, text="下一页", command=self.on_click_next).pack(
            side="left", padx=10
        )
        tkinter.Button(wid, text="新书", command=self.on_select_pdf).pack(
            side="left", padx=10
        )
        tkinter.Checkbutton(
            wid, text="置顶", variable=self._val_check, command=self.on_check
        ).pack(side="left", padx=10)
        tkinter.Scale(
            wid,
            from_=0.1,
            to_=1.0,
            resolution=0.1,
            orient="horizontal",
            variable=self._val_scale,
            command=self.on_alpha,
        ).pack(side="left", padx=10)

    # 切换透明度
    def switch_alpha(self, show):
        if show:
            self._wid.wm_attributes("-alpha", self._val_scale.get())
        else:
            self._wid.wm_attributes("-alpha", 0.1)

    # 切换窗口置顶模式
    def switch_top(self, show):
        self._wid.wm_attributes("-topmost", show)

    # 显示PDF
    def show_pdf(self):
        page = self._doc[self._index]
        pix = page.get_pixmap()

        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pdf_page_image = ImageTk.PhotoImage(image)
        self._label.config(image=pdf_page_image)
        self._label.image = pdf_page_image
        self._txt_page.set("当前页数： %s / %d" % (self._index + 1, len(self._doc)))

    # 写入配置
    def write_conf(self):
        data = {"file": str(self._file), "index": int(self._index)}
        print(self._file, str(self._file))
        with open("conf.json", "w") as file:
            json.dump(data, file, indent=4)

    # 读取配置
    def read_conf(self):
        if os.path.exists("conf.json"):
            with open("conf.json", "r") as file:
                data = json.load(file)
                self.load_pdf(str(data["file"]))
                self._index = int(data["index"])
                self.show_pdf()

    # 重载PDF
    def load_pdf(self, file):
        self._doc = pymupdf.open(file)
        self._index = 0
        self._file = file
        self.show_pdf()
        self.write_conf()

    # 置顶点击
    def on_check(self):
        self.switch_top(self._val_check.get())

    # 滑动透明
    def on_alpha(self, str):
        self.switch_alpha(True)

    # 上一页
    def on_click_prev(self):
        if self._index > 0:
            self._index -= 1
            self.show_pdf()

    # 下一页
    def on_click_next(self):
        self._index += 1
        self.show_pdf()

    # 新书
    def on_select_pdf(self):
        pdf_file = tkinter.filedialog.askopenfilename(
            title="choose file", filetypes=[("PDF", "*.pdf"), ("所有文件", "*.*")]
        )
        if pdf_file:
            self.load_pdf(pdf_file)

    # 鼠标滚轮
    def on_event_MouseWheel(self, event):
        if event.delte > 0:
            self.on_click_next()
        else:
            self.on_click_prev()

    # 关闭窗口
    def on_event_Close(self):
        try:
            self.write_conf()
        finally:
            self._wid.destroy()


# 主程序
def main():
    wid = tkinter.Tk()
    wid.wm_title("vision book")
    WidVision(wid)
    wid.mainloop()


# 入口
if __name__ == "__main__":
    main()
