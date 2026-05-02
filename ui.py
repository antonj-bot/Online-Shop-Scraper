import tkinter as tk
from tkinter import ttk
import main
root = tk.Tk()
root.title("Online Shop Scraper")   
root.geometry("800x400")


frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0, sticky="nsew")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frame.columnconfigure(0, weight=0)
frame.columnconfigure(1, weight=1)



#Header
header = ttk.Label(frame, text="Welcome to Online Shop Scraper", anchor="center", justify="center", font=("Helvetica", 20, "bold"))
header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=25)




#Choose a platform label
platform_label = ttk.Label(frame, text="Choose a Platform: ", font=("Helvetica", 10))
platform_label.grid(row=1, column=0, sticky="e")




#Platform Dropdown
platform_dropdown = ttk.Combobox(
    frame,
    values=["Shopee", "Lazada", "Amazon"],
    state="readonly",
    width=25
)
platform_dropdown.set("Select a platform ")
platform_dropdown.grid(row=1, column=1, sticky="w")


# Input field (initially hidden)
input_label = ttk.Label(frame, text="Enter Item:", font=("Helvetica", 10))
entry = ttk.Entry(frame, width=30)

#instructions label
instruction_label = ttk.Label(frame, text="please include color ex: Red", font=("Helvetica", 8), foreground="gray")

# When the user selects a platform from the dropdown, this function is triggered. It shows the input field and sets up a listener to check if the user has entered any text, which will then show the "Proceed" button.
def once_shop_is_selected(event):
    # Show the input field for the item keyword along with instructions
    input_label.grid(row=2, column=0, sticky="e", padx=(0, 5), pady=(5, 0))
    instruction_label.grid(row=3, column=1, sticky="w")
    entry.grid(row=2, column=1, sticky="w")
    # This function checks if the entry field has any text. If it does, it shows the "Proceed" button; otherwise, it hides it.
    def check_entry(event):
        if entry.get().strip():
            proceed_button.grid(row=6, column=1, sticky="w", pady=(5, 0))
            
        else:
            proceed_button.grid_remove()
    
    entry.bind("<KeyRelease>", check_entry)
    
    
# Bind the platform selection event to the dropdown
platform_dropdown.bind("<<ComboboxSelected>>", once_shop_is_selected)

    

def get_selected_site():
    return platform_dropdown.get()


def on_proceed():
    selected_site = platform_dropdown.get()
    keyword = entry.get().strip()
    
 
    main.handle_proceed(selected_site, keyword)

# Proceed button (initially hidden)
proceed_button = ttk.Button(frame, text="Proceed", command=on_proceed)  












root.mainloop()