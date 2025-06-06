# ascii_gui.py
import tkinter as tk
from tkinter import filedialog, messagebox, OptionMenu, StringVar
from PIL import Image as PILImage
from ascii_converter import image_to_ascii
from ascii_renderer import ascii_to_image
import os
import webbrowser  # これを追加

class AsciiArtApp:
    def __init__(self, root):
        self.root = root
        self.root.title("アスキーアート変換ツール")
        self.root.geometry("800x600")

        self.image_path = None
        self.original_image_width = None
        self.original_image_height = None
        self.ascii_text = ""
        self.color_matrix = []

        self.aspect_ratio_options = ["AAデフォルト補正", "元のアスペクト比"]
        self.aspect_ratio_var = StringVar(value=self.aspect_ratio_options[0])

        self.create_widgets()

    def create_widgets(self):
        control_frame = tk.Frame(self.root)
        # pack() の順番が重要。下の要素を先に pack すると、上に配置されがち
        # control_frame は上部に配置するため、ここで pack
        control_frame.pack(fill="x", pady=5)

        tk.Button(control_frame, text="画像を選択", command=self.select_image).pack(side="left", padx=5, pady=5)

        tk.Label(control_frame, text="幅(文字数):").pack(side="left", padx=(10,0))
        self.width_entry = tk.Entry(control_frame, width=5)
        self.width_entry.insert(0, "100")
        self.width_entry.pack(side="left")

        tk.Label(control_frame, text="文字セット:").pack(side="left", padx=(10,0))
        self.charset_entry = tk.Entry(control_frame, width=20)
        self.charset_entry.insert(0, "@%#*+=-:. ")
        self.charset_entry.pack(side="left")

        tk.Label(control_frame, text="保存アスペクト比:").pack(side="left", padx=(10,0))
        self.aspect_ratio_menu = OptionMenu(control_frame, self.aspect_ratio_var, *self.aspect_ratio_options)
        self.aspect_ratio_menu.pack(side="left")

        tk.Button(control_frame, text="変換", command=self.convert).pack(side="left", padx=10)
        tk.Button(control_frame, text="画像として保存", command=self.save_image).pack(side="left", padx=5)

        # --- お問い合わせ情報表示用のウィジェットを追加 ---
        info_frame = tk.Frame(self.root)
        # ウィンドウの下部に配置するために、expand=False, fill="x", side="bottom" を使用
        info_frame.pack(expand=False, fill="x", pady=5, side="bottom")

        # Textウィジェットを使用することで、テキストの一部にタグを付けて装飾やイベントバインドが可能になります
        self.info_text_box = tk.Text(info_frame, height=1, bg=self.root.cget('bg'), bd=0, state="normal", wrap="word")
        self.info_text_box.pack(side="left", padx=5, pady=5)

        # 表示したいテキストとリンクにするテキストを設定
        info_text = "お問い合わせは : @suzuya_twi (X) まで"
        link_text = "@suzuya_twi"
        link_url = "https://x.com/suzuya_twi"

        # テキストをTextウィジェットに挿入
        self.info_text_box.insert(tk.END, info_text)

        # リンク部分の開始位置と終了位置を計算し、タグを適用
        # Textウィジェットのインデックスは "line.column" 形式
        start_index = info_text.find(link_text)
        if start_index != -1:
            end_index = start_index + len(link_text)
            start_tk_index = f"1.{start_index}"
            end_tk_index = f"1.{end_index}"

            # 'link' というタグを設定します。前景（文字色）を青に、下線を追加
            self.info_text_box.tag_config("link", foreground="blue", underline=True)

            # マウスがリンク上に来たときにカーソルを「手」に変更
            self.info_text_box.tag_bind("link", "<Enter>", lambda e: self.info_text_box.config(cursor="hand2"))
            # マウスがリンクから外れたときにカーソルを元に戻す
            self.info_text_box.tag_bind("link", "<Leave>", lambda e: self.info_text_box.config(cursor=""))

            # 左クリック (<Button-1>) イベントを 'link' タグにバインドし、open_link 関数を呼び出す
            # lambda を使うことで、イベントが発生したときにのみ open_link が実行されるようにする
            self.info_text_box.tag_bind("link", "<Button-1>", lambda e, url=link_url: self.open_link(url))

            # 計算した範囲に 'link' タグを適用
            self.info_text_box.tag_add("link", start_tk_index, end_tk_index)

        # Textウィジェットを読み取り専用
        self.info_text_box.config(state="disabled")
        # --- お問い合わせ情報表示用のウィジェット追加ここまで ---


        text_font = ("Consolas", 8)
        if os.name != 'nt':
            text_font = ("monospace", 8)

        # メインのアスキーアート表示エリア。expand=True で残りのスペースを埋めるようにする
        self.text_box = tk.Text(self.root, font=text_font, bg="black", fg="white", wrap="none")
        # info_frame の前に pack することで、info_frame が下部に固定され、text_box がその上に配置される
        self.text_box.pack(expand=True, fill="both", padx=5, pady=5)


        x_scrollbar = tk.Scrollbar(self.text_box, orient="horizontal", command=self.text_box.xview)
        y_scrollbar = tk.Scrollbar(self.text_box, orient="vertical", command=self.text_box.yview)
        self.text_box.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)

        x_scrollbar.pack(side="bottom", fill="x")
        y_scrollbar.pack(side="right", fill="y")

    # --- リンクを開くための関数を追加 ---
    def open_link(self, url):
        """指定されたURLをシステムのデフォルトブラウザで開く"""
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("エラー", f"ブラウザを開けませんでした:\n{e}")
    # --- リンクを開くための関数追加ここまで ---


    def select_image(self):
        path = filedialog.askopenfilename(
            title="画像ファイルを選択",
            filetypes=[("画像ファイル", "*.png;*.jpg;*.jpeg;*.bmp;*.webp"), ("すべてのファイル", "*.*")]
        )
        if path:
            self.image_path = path
            self.original_image_width = None
            self.original_image_height = None
            try:
                with PILImage.open(path) as img:
                    self.original_image_width, self.original_image_height = img.size
                base_name = os.path.basename(path)
                messagebox.showinfo("画像選択",
                                    f"画像を選択しました：\n{base_name}\n"
                                    f"サイズ: {self.original_image_width}x{self.original_image_height}")
            except FileNotFoundError:
                messagebox.showerror("エラー", f"指定された画像ファイルが見つかりません:\n{path}")
                self.image_path = None
            except Exception as e:
                messagebox.showerror("エラー", f"画像情報の取得に失敗しました: {e}")
                self.image_path = None

    def convert(self):
        if not self.image_path:
            messagebox.showerror("エラー", "画像を先に選択してください。")
            return
        try:
            width_str = self.width_entry.get()
            if not width_str:
                 messagebox.showerror("エラー", "幅を入力してください。")
                 return
            width = int(width_str)

            if width <= 0:
                messagebox.showerror("エラー", "幅は正の整数で指定してください。")
                return
            charset = self.charset_entry.get()
            if not charset:
                messagebox.showerror("エラー", "文字セットを入力してください。")
                return

            self.ascii_text, self.color_matrix = image_to_ascii(self.image_path, width, charset)

            self.text_box.config(state=tk.NORMAL)
            self.text_box.delete("1.0", tk.END)
            self.text_box.insert(tk.END, self.ascii_text)
            self.text_box.config(state=tk.DISABLED)

        except ValueError:
            messagebox.showerror("エラー", "幅には有効な整数を入力してください。")
        except FileNotFoundError as e:
            messagebox.showerror("エラー", str(e))
        except RuntimeError as e:
            messagebox.showerror("変換エラー", str(e))
        except Exception as e:
            messagebox.showerror("予期せぬエラー", f"変換中にエラーが発生しました: {e}")

    def save_image(self):
        if not self.ascii_text or not self.color_matrix:
            messagebox.showerror("エラー", "まずアスキーアートに変換してください。")
            return

        path = filedialog.asksaveasfilename(
            title="アスキーアートを画像として保存",
            defaultextension=".png",
            filetypes=[("PNG画像", "*.png"), ("JPEG画像", "*.jpg"), ("すべてのファイル", "*.*")]
        )
        if path:
            try:
                aspect_option = self.aspect_ratio_var.get()
                original_size_info = None

                if self.original_image_width and self.original_image_height:
                    original_size_info = (self.original_image_width, self.original_image_height)
                elif aspect_option == "元のアスペクト比":
                    messagebox.showwarning("アスペクト比警告",
                                           "「元のアスペクト比」が選択されましたが、元画像のサイズ情報が取得できていません。\n"
                                           "AAデフォルト補正で画像を生成します。")
                    # この場合、renderer側で aspect_option が "元のアスペクト比" であっても
                    # original_image_size が None なのでフォールバック処理される

                img = ascii_to_image(
                    self.ascii_text,
                    self.color_matrix,
                    font_size=10,
                    aspect_ratio_option=aspect_option,
                    original_image_size=original_size_info
                )
                img.save(path)
                messagebox.showinfo("保存完了", f"画像を保存しました：\n{path}")
            except FileNotFoundError as e:
                 messagebox.showerror("保存エラー", f"必要なファイルが見つかりません: {e}")
            except ValueError as e:
                messagebox.showerror("保存エラー", str(e))
            except RuntimeError as e:
                messagebox.showerror("保存エラー", str(e))
            except Exception as e:
                messagebox.showerror("保存エラー", f"画像の保存中にエラーが発生しました: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AsciiArtApp(root)
    root.mainloop()