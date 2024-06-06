import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import feedparser
import opml
import sqlite3
import xml.etree.ElementTree as ET
import webbrowser
import threading

# Função para criar e conectar ao banco de dados SQLite
def create_db():
    conn = sqlite3.connect('feeds.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS feeds (
                      id INTEGER PRIMARY KEY,
                      url TEXT NOT NULL UNIQUE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS items (
                      id INTEGER PRIMARY KEY,
                      feed_id INTEGER,
                      title TEXT,
                      link TEXT,
                      description TEXT,
                      pub_date TEXT,
                      UNIQUE(feed_id, title),
                      FOREIGN KEY(feed_id) REFERENCES feeds(id))''')
    conn.commit()
    return conn

# Função para importar feeds de um arquivo OPML
def import_opml(file_path, conn):
    try:
        print("Arquivo OPML:", file_path)  # Adicionando mensagem de depuração
        tree = ET.parse(file_path)
        root = tree.getroot()
        feeds = []
        for outline in root.findall('.//outline'):
            if 'xmlUrl' in outline.attrib:
                feeds.append(outline.attrib['xmlUrl'])
        print("Feeds encontrados:", feeds)  # Adicionando mensagem de depuração
        for feed in feeds:
            add_feed(feed, conn)
        update_feeds(conn)
        return feeds
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao importar OPML: {e}")
        return []

# Função para adicionar feed ao banco de dados
def add_feed(url, conn):
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO feeds (url) VALUES (?)', (url,))
        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "URL do feed já existe no banco de dados.")

# Função para listar todos os feeds
def list_feeds(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT id, url FROM feeds')
    feeds = cursor.fetchall()
    return feeds

# Função para excluir feed
def delete_feed(feed_id, conn):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM feeds WHERE id = ?', (feed_id,))
    cursor.execute('DELETE FROM items WHERE feed_id = ?', (feed_id,))
    conn.commit()

# Função para atualizar feeds
def update_feeds(conn, button):
    local_conn = sqlite3.connect('feeds.db')
    cursor = local_conn.cursor()
    cursor.execute('SELECT id, url FROM feeds')
    feeds = cursor.fetchall()
    for feed_id, feed_url in feeds:
        d = feedparser.parse(feed_url)
        for entry in d.entries:
            try:
                published = entry.published if 'published' in entry else None
                cursor.execute('INSERT INTO items (feed_id, title, link, description, pub_date) VALUES (?, ?, ?, ?, ?)',
                               (feed_id, entry.title, entry.link, entry.description, published))
            except sqlite3.IntegrityError:
                continue
    local_conn.commit()
    local_conn.close()
    button.config(text="Feed Atualizado", style="TButton.Green.TButton")
    button.after(3000, lambda: button.config(text="Atualizar Feeds", style="TButton.TButton"))

# Função para exibir feeds na interface gráfica
def show_feeds(conn, listbox):
    listbox.delete(0, tk.END)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, link FROM items ORDER BY pub_date DESC')
    items = cursor.fetchall()
    if not items:
        listbox.insert(tk.END, "Nenhuma notícia encontrada.")
    for item in items:
        title = item[1]
        link = item[2]
        listbox.insert(tk.END, f"{title}-{link}")

def open_link(event):
    widget = event.widget
    index = widget.curselection()[0]
    link = widget.get(index).split('-')[1].strip()
    webbrowser.open_new(link)

def read_news(event, conn):
    widget = event.widget
    index = widget.curselection()[0]
    item_data = widget.get(index).split('-')
    if len(item_data) != 2:
        messagebox.showerror('Erro', 'Item de feed inválido.')
        return
    item_id = item_data[0].strip()
    cursor = conn.cursor()
    cursor.execute('SELECT description FROM items WHERE id=?', (item_id,))
    description = cursor.fetchone()
    if description:
        messagebox.showinfo('Notícia', description[0])
    else:
        messagebox.showerror('Erro', 'Descrição não encontrada.')

# Função para abrir e importar arquivo OPML
def open_opml(conn, listbox):
    file_path = filedialog.askopenfilename(filetypes=[("OPML files", "*.opml")])
    if file_path:
        feeds = import_opml(file_path, conn)
        if not feeds:
            messagebox.showerror("Erro", "Nenhum feed encontrado no arquivo OPML.")
            return
        show_feeds(conn, listbox)
        messagebox.showinfo("Importação Completa", "Feeds importados com sucesso!")

def main():
    conn = create_db()
    
    root = tk.Tk()
    root.title("Leitor de Feed RSS")
    root.geometry("800x600")

    root.iconbitmap('icone.ico')

    style = ttk.Style()
    style.theme_use("clam")  # Use o tema clam

    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    listbox_frame = ttk.Frame(frame)
    listbox_frame.pack(fill=tk.BOTH, expand=True)

    listbox_scrollbar = ttk.Scrollbar(listbox_frame)
    listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(listbox_frame, yscrollcommand=listbox_scrollbar.set, font=("Arial", 12))
    listbox.pack(fill=tk.BOTH, expand=True)

    listbox_scrollbar.config(command=listbox.yview)

    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Importar OPML", command=lambda: open_opml(conn, listbox))
    filemenu.add_separator()
    filemenu.add_command(label="Listar Feeds", command=lambda: show_feeds_list(conn, listbox))
    menubar.add_cascade(label="Arquivo", menu=filemenu)

    update_button = ttk.Button(root, text="Atualizar Feeds", command=lambda: update_feeds(conn, update_button))
    update_button.pack(pady=5)

    root.config(menu=menubar)

    # Atualizar os feeds e mostrar na inicialização
    update_feeds(conn, update_button)
    show_feeds(conn, listbox)

    listbox.bind('<Double-Button-1>', lambda event, conn=conn: open_link(event))
    listbox.bind('<Button-3>', lambda event, conn=conn: read_news(event, conn))

    root.mainloop()

def show_feeds_list(conn, listbox):
    feeds = list_feeds(conn)
    if feeds:
        root = tk.Toplevel()
        root.title("Lista de Feeds")

        frame = ttk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        treeview = ttk.Treeview(frame, columns=("ID", "URL"), show="headings", selectmode="browse")
        treeview.heading("ID", text="ID")
        treeview.heading("URL", text="URL")

        for feed in feeds:
            treeview.insert("", "end", values=(feed[0], feed[1]))

        treeview.pack(fill=tk.BOTH, expand=True)

        delete_button = ttk.Button(root, text="Excluir Feed", command=lambda: delete_selected_feed(treeview, conn, listbox))
        delete_button.pack(pady=5)

        add_button = ttk.Button(root, text="Adicionar Feed", command=lambda: add_new_feed(conn, listbox))
        add_button.pack(pady=5)

    else:
        messagebox.showinfo("Lista de Feeds", "Nenhum feed cadastrado.")

def add_new_feed(conn, listbox):
    url = simpledialog.askstring("Adicionar Feed", "Digite a URL do novo feed:")
    if url:
        add_feed(url, conn)
        update_feeds(conn)
        show_feeds(conn, listbox)

def delete_selected_feed(treeview, conn, listbox):
    selected_item = treeview.selection()
    if selected_item:
        feed_id = treeview.item(selected_item)['values'][0]
        delete_feed(feed_id, conn)
        show_feeds(conn, listbox)
        treeview.delete(selected_item)
    else:
        messagebox.showerror("Erro", "Nenhum feed selecionado.")

if __name__ == "__main__":
    main()