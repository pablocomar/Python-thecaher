"""Basit masaüstü uygulaması:
- Kullanıcı ad girer
- 1-16 arası rastgele sayı atanır
- Sayıya bağlı JPG görseli gösterilir

Görsel dosyaları varsayılan olarak `images/1.jpg` ... `images/16.jpg`
şeklinde aranır. İstenirse arayüzden tek tek de seçilebilir.
"""

from __future__ import annotations

import random
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk


class NumberImageAssignerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("İsimden Numara Atayıcı (1-16)")
        self.root.geometry("700x560")

        self.current_image: ImageTk.PhotoImage | None = None
        self.image_paths: dict[int, Path] = {}

        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill="both", expand=True)

        # Üst alan: ad girişi
        input_frame = ttk.LabelFrame(container, text="Kullanıcı", padding=10)
        input_frame.pack(fill="x")

        ttk.Label(input_frame, text="Adınız:").grid(row=0, column=0, sticky="w", padx=(0, 8))

        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(input_frame, textvariable=self.name_var, width=35)
        self.name_entry.grid(row=0, column=1, sticky="ew")
        self.name_entry.focus_set()

        assign_btn = ttk.Button(input_frame, text="Numara Ata", command=self.assign_number)
        assign_btn.grid(row=0, column=2, padx=(8, 0))

        input_frame.columnconfigure(1, weight=1)

        # Ayar alanı: görsel klasörü
        settings_frame = ttk.LabelFrame(container, text="Görsel Ayarları", padding=10)
        settings_frame.pack(fill="x", pady=(10, 0))

        info = (
            "Klasör seçerseniz uygulama 1.jpg, 2.jpg ... 16.jpg dosyalarını otomatik yükler.\n"
            "İsterseniz aşağıdan her sayıya ayrı dosya da atayabilirsiniz."
        )
        ttk.Label(settings_frame, text=info).pack(anchor="w")

        row = ttk.Frame(settings_frame)
        row.pack(fill="x", pady=(8, 0))

        ttk.Button(row, text="Klasör Seç", command=self.pick_folder).pack(side="left")
        ttk.Button(row, text="Tek Tek Dosya Ata", command=self.assign_single_files).pack(side="left", padx=(8, 0))

        self.status_var = tk.StringVar(value="Henüz görsel yüklenmedi.")
        ttk.Label(settings_frame, textvariable=self.status_var, foreground="#444").pack(anchor="w", pady=(8, 0))

        # Sonuç alanı
        result_frame = ttk.LabelFrame(container, text="Sonuç", padding=10)
        result_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.result_var = tk.StringVar(value="Lütfen adınızı girip 'Numara Ata' butonuna basın.")
        ttk.Label(result_frame, textvariable=self.result_var, font=("Segoe UI", 12, "bold")).pack(anchor="w")

        self.image_label = ttk.Label(result_frame)
        self.image_label.pack(fill="both", expand=True, pady=(10, 0))

    def pick_folder(self) -> None:
        folder = filedialog.askdirectory(title="JPG dosyalarının olduğu klasörü seçin")
        if not folder:
            return

        selected = Path(folder)
        loaded = 0
        for n in range(1, 17):
            candidate = selected / f"{n}.jpg"
            if candidate.exists():
                self.image_paths[n] = candidate
                loaded += 1

        self.status_var.set(f"Klasörden {loaded}/16 görsel yüklendi: {selected}")

    def assign_single_files(self) -> None:
        for n in range(1, 17):
            file_path = filedialog.askopenfilename(
                title=f"{n} için JPG seç",
                filetypes=[("JPEG files", "*.jpg;*.jpeg"), ("All files", "*.*")],
            )
            if not file_path:
                continue
            self.image_paths[n] = Path(file_path)

        self.status_var.set(f"Toplam atanmış görsel sayısı: {len(self.image_paths)}/16")

    def assign_number(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Eksik Bilgi", "Lütfen önce adınızı girin.")
            return

        number = random.randint(1, 16)
        self.result_var.set(f"{name} için atanan sayı: {number}")
        self.show_image(number)

    def show_image(self, number: int) -> None:
        image_path = self.image_paths.get(number)
        if not image_path:
            self.image_label.configure(text=f"{number} için görsel atanmadı.", image="")
            self.current_image = None
            return

        try:
            img = Image.open(image_path)
            img.thumbnail((640, 400))
            tk_img = ImageTk.PhotoImage(img)
        except Exception as exc:  # noqa: BLE001
            self.image_label.configure(text=f"Görsel açılamadı: {exc}", image="")
            self.current_image = None
            return

        self.current_image = tk_img
        self.image_label.configure(image=self.current_image, text="")


def main() -> None:
    root = tk.Tk()
    app = NumberImageAssignerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
