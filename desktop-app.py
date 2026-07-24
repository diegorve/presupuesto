import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import pandas as pd
import re


def clasificar_metodo_pago(texto):
    texto = texto.lower()

    if "banco pichincha" in texto:
        return "EFECTIVO"

    if any(x in texto for x in ["visa", "titanium", "diners"]):
        return "TARJETA_CREDITO"

    return "OTRO"


def procesar_xml(ruta_archivo):

    tree = ET.parse(ruta_archivo)
    root = tree.getroot()

    consumos = []

    patrones = [
        r"trx por ([\d,]+), en ([^,]+)",
        r"Consumiste \$ ([\d,]+) en (.+?) con",
    ]

    for sms in root.findall("sms"):

        body = sms.get("body", "")
        fecha = sms.get("readable_date", "")

        for patron in patrones:

            match = re.search(patron, body, re.IGNORECASE)

            if match:
                monto = float(match.group(1).replace(",", "."))
                comercio = match.group(2).strip()

                consumos.append({
                    "Fecha": fecha,
                    "Comercio": comercio,
                    "Monto": monto,
                    "Método": clasificar_metodo_pago(body)
                })

                break

    return pd.DataFrame(consumos)


class App:

    def __init__(self, root):

        self.root = root
        self.root.title("Analizador de SMS")
        self.root.geometry("1000x600")

        self.df = pd.DataFrame()

        frame_top = tk.Frame(root)
        frame_top.pack(fill="x", padx=10, pady=10)

        tk.Button(
            frame_top,
            text="Seleccionar Backup XML",
            command=self.cargar_archivo
        ).pack(side="left")

        tk.Button(
            frame_top,
            text="Exportar Excel",
            command=self.exportar_excel
        ).pack(side="left", padx=5)

        self.lbl_total = tk.Label(
            frame_top,
            text="Total gastos: $0.00"
        )

        self.lbl_total.pack(side="right")

        columnas = ("Fecha", "Comercio", "Monto", "Método")

        self.tree = ttk.Treeview(
            root,
            columns=columnas,
            show="headings"
        )

        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)

        self.tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    def cargar_archivo(self):

        ruta = filedialog.askopenfilename(
            title="Seleccionar XML",
            filetypes=[("XML", "*.xml")]
        )

        if not ruta:
            return

        try:

            self.df = procesar_xml(ruta)

            for item in self.tree.get_children():
                self.tree.delete(item)

            for _, fila in self.df.iterrows():
                self.tree.insert(
                    "",
                    "end",
                    values=list(fila)
                )

            total = self.df["Monto"].sum()

            self.lbl_total.config(
                text=f"Total gastos: ${total:,.2f}"
            )

            messagebox.showinfo(
                "Proceso completado",
                f"Se encontraron {len(self.df)} consumos."
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )

    def exportar_excel(self):

        if self.df.empty:
            messagebox.showwarning(
                "Aviso",
                "No hay datos para exportar."
            )
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")]
        )

        if not ruta:
            return

        self.df.to_excel(
            ruta,
            index=False
        )

        messagebox.showinfo(
            "Exportación",
            "Archivo Excel generado correctamente."
        )


root = tk.Tk()
app = App(root)
root.mainloop()