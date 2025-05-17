import tkinter as tk
from tkinter import ttk

class MainEditorUI:
	def __init__(self, root):
		self.root = root
		self.loaded = False
		
		self.menu = None
		self.left_panel = None
		self.inspector_panel = None

		self.assets_list = None
		self.hierarchy_list = None

		self._dragging_item = None
		self.folder_spacing = 5

		self.asset_folders = {}
		self.asset_visible_items = []

		self.color_schemes = {
			"dark": {
				"Background": "#1e1e1e",
				"Panel Bg": "#2b2b2b",
				"Panel Label Bg": "#111111",
				"Listbox Bg": "#333333",
				"Listbox Fg": "white",
				"Label Fg": "white",
				"Select Bg": "#555555",
				"Drag Ghost Bg": "#444444",
			},
			"light": {
				"Background": "#f0f0f0",
				"Panel Bg": "#e0e0e0",
				"Panel Label Bg": "#cccccc",
				"Listbox Bg": "#dddddd",
				"Listbox Fg": "black",
				"Label Fg": "black",
				"Select Bg": "#bbbbbb",
				"Drag Ghost Bg": "#999999",
			},
			"midnight": {
				"Background": "#0d1b2a",
				"Panel Bg": "#1b263b",
				"Panel Label Bg": "#415a77",
				"Listbox Bg": "#1e293b",
				"Listbox Fg": "#e0e1dd",
				"Label Fg": "#e0e1dd",
				"Select Bg": "#3a506b",
				"Drag Ghost Bg": "#27374d",
			}
		}
		self.scheme_name = "dark"
		self.scheme = self.color_schemes[self.scheme_name]

		self._drag_ghost_window = None
		self._drag_last_hover_index = None

	def new_project(self): pass
	def open_project(self): pass
	def save_project(self): pass
	def save_as_project(self): pass
	def display_settings(self): pass
	def display_console(self): pass
	def undo_action(self): pass
	def redo_action(self): pass

	def save_exit(self):
		self.save_project()
		self.root.quit()

	def add_asset(self, name, folder=None):
		if not folder:
			self.asset_visible_items.append(name)
		else:
			if folder not in self.asset_folders:
				self.asset_folders[folder] = {"open": True, "items": []}
			self.asset_folders[folder]["items"].append(name)
		self._refresh_asset_list()

	def toggle_folder(self, folder):
		if folder in self.asset_folders:
			self.asset_folders[folder]["open"] = not self.asset_folders[folder]["open"]
			self._refresh_asset_list()

	def _refresh_asset_list(self):
		if not self.assets_list:
			return
		self.assets_list.delete(0, "end")
		for folder, data in self.asset_folders.items():
			prefix = "▼ " if data["open"] else "▶ "
			self.assets_list.insert("end", prefix + folder)
			if data["open"]:
				for item in data["items"]:
					self.assets_list.insert("end", " " * self.folder_spacing + "- " + item)
		for item in self.asset_visible_items:
			self.assets_list.insert("end", item)

	def add_hierarchy_item(self, name):
		if self.hierarchy_list:
			self.hierarchy_list.insert("end", name)

	def remove_selected_hierarchy_item(self):
		if self.hierarchy_list:
			selected = self.hierarchy_list.curselection()
			for index in reversed(selected):
				self.hierarchy_list.delete(index)

	def _on_hierarchy_drag_start(self, event):
		w = event.widget
		index = w.nearest(event.y)
		if index >= 0:
			self._dragging_item = (index, w.get(index))

	def _on_hierarchy_drag_motion(self, event):
		if self._dragging_item:
			index, _ = self._dragging_item
			curr_index = self.hierarchy_list.nearest(event.y)

			if self._drag_last_hover_index is not None and self._drag_last_hover_index != index:
				self.hierarchy_list.itemconfig(self._drag_last_hover_index, fg=self.scheme["Listbox Fg"])

			if curr_index != index:
				self.hierarchy_list.itemconfig(index, bg=self.scheme["Select Bg"])
				self._drag_last_hover_index = index

			if not self._drag_ghost_window:
				self._drag_ghost_window = tk.Toplevel(self.root)
				self._drag_ghost_window.overrideredirect(True)
				self._drag_ghost_window.attributes('-topmost', True)
				self._drag_ghost_label = tk.Label(
					self._drag_ghost_window, 
					text=self._dragging_item[1], 
					bg=self.scheme["Drag Ghost Bg"], 
					fg=self.scheme["Label Fg"], 
					bd=1, relief="solid"
				)
				self._drag_ghost_label.pack()

			self._drag_ghost_window.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

	def _on_hierarchy_drag_drop(self, event):
		if self._dragging_item:
			w = event.widget
			drop_index = w.nearest(event.y)
			orig_index, item = self._dragging_item

			if drop_index != orig_index:
				w.delete(orig_index)
				w.insert(drop_index, item)

			if self._drag_last_hover_index is not None:
				w.itemconfig(self._drag_last_hover_index, bg=self.scheme["Listbox Bg"])
				self._drag_last_hover_index = None

			if self._drag_ghost_window:
				self._drag_ghost_window.destroy()
				self._drag_ghost_window = None

			self._dragging_item = None

	def load_config(self):
		self.root.configure(bg=self.scheme["Background"])

	def load_main_menu(self):
		self.menu = tk.Menu(self.root)

		file_menu = tk.Menu(self.menu, tearoff=0)
		file_menu.add_command(label="New", command=self.new_project)
		file_menu.add_command(label="Open", command=self.open_project)
		file_menu.add_separator()
		file_menu.add_command(label="Save", command=self.save_project)
		file_menu.add_command(label="Save as", command=self.save_as_project)
		file_menu.add_separator()
		file_menu.add_command(label="Exit & Save", command=self.save_exit)
		file_menu.add_command(label="Exit", command=self.root.quit)
		self.menu.add_cascade(label="File", menu=file_menu)

		edit_menu = tk.Menu(self.menu, tearoff=0)
		edit_menu.add_command(label="Undo", command=self.undo_action)
		edit_menu.add_command(label="Redo", command=self.redo_action)
		self.menu.add_cascade(label="Edit", menu=edit_menu)

		window_menu = tk.Menu(self.menu, tearoff=0)
		window_menu.add_command(label="Console", command=self.display_console)
		self.menu.add_cascade(label="Window", menu=window_menu)

		self.root.config(menu=self.menu)

	def load_left_panel(self):
		self.left_panel = tk.Frame(self.root, width=200, bg=self.scheme["Panel Bg"])
		self.left_panel.pack(side="left", fill="y")	

		hierarchy_label = tk.Label(self.left_panel, text="Hierarchy", bg=self.scheme["Panel Label Bg"], fg=self.scheme["Label Fg"], anchor="w")
		hierarchy_label.pack(fill="x")
		self.hierarchy_list = tk.Listbox(
			self.left_panel, bg=self.scheme["Listbox Bg"], fg=self.scheme["Listbox Fg"], selectbackground=self.scheme["Select Bg"]
		)
		self.hierarchy_list.pack(fill="both", expand=True)
		self.hierarchy_list.bind("<Button-1>", self._on_hierarchy_drag_start)
		self.hierarchy_list.bind("<B1-Motion>", self._on_hierarchy_drag_motion)
		self.hierarchy_list.bind("<ButtonRelease-1>", self._on_hierarchy_drag_drop)

		assets_label = tk.Label(self.left_panel, text="Assets", bg=self.scheme["Panel Label Bg"], fg=self.scheme["Label Fg"], anchor="w")
		assets_label.pack(fill="x")
		self.assets_list = tk.Listbox(self.left_panel, bg=self.scheme["Listbox Bg"], fg=self.scheme["Listbox Fg"])
		self.assets_list.pack(fill="both", expand=True)
		self.assets_list.bind("<Double-Button-1>", lambda e: self._on_asset_double_click(e))

	def load_inspector(self):
		self.inspector_panel = tk.Frame(self.root, width=250, bg=self.scheme["Panel Bg"])
		self.inspector_panel.pack(side="right", fill="y")

		inspector_label = tk.Label(self.inspector_panel, text="Inspector", bg=self.scheme["Panel Label Bg"], fg=self.scheme["Label Fg"], anchor="w")
		inspector_label.pack(fill="x")

		inspector_placeholder = tk.Label(self.inspector_panel, text="No object selected", bg=self.scheme["Panel Bg"], fg=self.scheme["Label Fg"])
		inspector_placeholder.pack(pady=10, padx=10)

	def load(self):
		if self.loaded:
			return
		self.load_config()
		self.load_main_menu()
		self.load_left_panel()
		self.load_inspector()
		self.loaded = True

	def _on_asset_double_click(self, event):
		if not self.assets_list:
			return
		index = self.assets_list.curselection()
		if not index:
			return
		text = self.assets_list.get(index[0])
		if text.startswith("▶ ") or text.startswith("▼ "):
			folder = text[2:]
			self.toggle_folder(folder)

	def unload(self):
		if self.menu:
			self.root.config(menu=tk.Menu(self.root))
			self.menu = None
		if self.left_panel:
			self.left_panel.destroy()
			self.left_panel = None
			self.assets_list = None
			self.hierarchy_list = None
			self.asset_folders = {}
			self.asset_visible_items = []
		if self.inspector_panel:
			self.inspector_panel.destroy()
			self.inspector_panel = None
		self.loaded = False

if __name__ == "__main__":
	root = tk.Tk()
	root.geometry("800x600")
	root.title("S.U.P.E FPS")

	editor = MainEditorUI(root)
	editor.load()

	editor.add_hierarchy_item("Camera")
	editor.add_hierarchy_item("Player")
	editor.add_hierarchy_item("Light")

	editor.add_asset("Gun.asset", folder="Prefabs")
	editor.add_asset("Enemy.asset", folder="Prefabs")
	editor.add_asset("Skybox.png", folder="Textures")
	editor.add_asset("README.md")

	root.mainloop()
