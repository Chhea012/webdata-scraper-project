import tkinter as tk
from tkinter import messagebox, PhotoImage, filedialog
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json
import os
import requests

def fetch_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print("Error fetching " + url + ": " + str(e))
        return None
# ==================================================================================
def extract_headings(soup):
    headings = []
    for i in range(1, 7):
        headings_in_level = soup.find_all('h' + str(i))
        for h in headings_in_level:
            headings.append(h.text.strip())
    return headings
# ==================================================================================
def extract_paragraphs(soup):
    paragraphs = []
    for p in soup.find_all('p'):
        paragraphs.append(p.text.strip())
    return paragraphs
# =================================================================================
def extract_lists(soup):
    list_items = []
    for ul in soup.find_all('ul'):
        for li in ul.find_all('li'):
            list_items.append(li.text.strip())
    return list_items
# ===================================================================================
def extract_links(soup):
    links = []
    for a in soup.find_all('a'):
        href = a.get('href')
        if href:
            links.append(href)
    return links
# ======================================================================================
def extract_images(soup):
    image_sources = []
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            image_sources.append(src)
    return image_sources
# ====================================================================================
def extract_content(soup):
    return {
        "Headings": extract_headings(soup),
        "Paragraphs": extract_paragraphs(soup),
        "Lists": extract_lists(soup),
        "Links": extract_links(soup),
        "Images": extract_images(soup),
    }
# ===========================================================================
def file_exists(filepath):
    return os.path.exists(filepath)
def write_json_file(data, file_path):
    try:
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print("Data successfully written to " + file_path)
    except IOError as e:
        print("Error writing to file " + file_path + ": " + str(e))
# ==============================================================================
def merge_json_data(existing_data, new_data, page_name):
    if page_name in existing_data:
        print("Data for " + page_name + " already exists. Updating existing data...")
        existing_data[page_name].update(new_data[page_name])
    else:
        print("Adding new data for " + page_name + "...")
        existing_data.update(new_data)
    return existing_data
# ========================================================================================
def save_data(data, url, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    parsed_url = urlparse(url)
    page_name = parsed_url.path.strip('/').replace('/', '_') or "home"
    netloc = parsed_url.netloc.replace('.', '_')
    json_file_name = netloc + ".json"
    json_path = os.path.join(destination_folder, json_file_name)
    structured_data = {page_name: data}
    print("Saving data for " + url + " to " + json_path)
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as json_file:
                existing_data = json.load(json_file)
            merged_data = merge_json_data(existing_data, structured_data, page_name)
            write_json_file(merged_data, json_path)
        except json.JSONDecodeError as e:
            print("Error loading existing data: " + str(e) + ". Overwriting file with new data...")
            write_json_file(structured_data, json_path)
    else:
        write_json_file(structured_data, json_path)
# ======================================================================================
def scrape_page(url, destination_folder, visited):
    if url in visited:
        return []
    print("Scraping " + url + "...")
    html_content = fetch_webpage(url)
    if not html_content:
        return []
    soup = BeautifulSoup(html_content, 'html.parser')
    data = extract_content(soup)
    save_data(data, url, destination_folder)
    visited.add(url)
    return extract_links(soup)
# =================================================================================================
def scrape_website_recursive(start_url, destination_folder, visited, max_depth=2, current_depth=0):
    if current_depth > max_depth:
        return
    print("Scraping depth " + str(current_depth) + ": " + start_url)
    links = scrape_page(start_url, destination_folder, visited)
    for link in links:
        full_url = urljoin(start_url, link)
        parsed_url = urlparse(full_url)
        if parsed_url.netloc:
            scrape_website_recursive(full_url, destination_folder, visited, max_depth, current_depth + 1)
# =====================================================================================================
def start_scraping():
    url_input = url_text.get("1.0", "end").strip()
    if not url_input:
        messagebox.showwarning("Input Error", "Please enter at least one URL!")
        return
    urls = [url.strip() for url in url_input.split(",")]
    visited = set()
    for url in urls:
        destination_folder = filedialog.askdirectory(title="Select a folder for " + url)
        if not destination_folder:
            messagebox.showwarning("Folder Error", "Please select a destination folder for " + url + "!")
            return
        scrape_website_recursive(url, destination_folder, visited, max_depth=3)
    messagebox.showinfo("Scraping Complete", "Scraping completed successfully! All data has been saved.")
# ==================================================================================================
# UI Enhancements

window = tk.Tk()
window.title("🕸 Web Scraper Tool")
window.geometry("650x500")
# window.resizable(False, False)
primary_color = "#6c5ce7"
secondary_color = "#dfe6e9"
text_color = "#ffffff"
button_hover_color = "#a29bfe"
highlight_color = "#ffeaa7"
if os.path.exists("bg.png"):
    bg_image = PhotoImage(file="bg.png")
    background_label = tk.Label(window, image=bg_image)
    background_label.place(relwidth=1, relheight=1)
else:
    window.configure(bg=secondary_color)
# Main content frame
frame = tk.Frame(window, bg="#ffffff", bd=10, relief="solid", padx=20, pady=20)
frame.place(relx=0.5, rely=0.5, anchor="center", width=550, height=400)
# Title label
title_label = tk.Label(
    frame,
    text="🕸 Web Scraper Tool",
    font=("Helvetica", 24, "bold"),
    bg=primary_color,
    fg=text_color,
    pady=10,
    relief="flat"
)
title_label.pack(fill="x", pady=10)

def add_spacer(height):
    tk.Label(frame, bg="#ffffff", height=height).pack()

# URL input area
add_spacer(1)
tk.Label(
    frame, text="Enter URLs (comma-separated):", font=("Helvetica", 12), bg="#ffffff", fg="#333333"
).pack(anchor="w", padx=20)
url_text = tk.Text(frame, height=5, width=50, font=("Helvetica", 11), bd=1, relief="solid", wrap="word")
url_text.pack(padx=20, pady=5)
add_spacer(1)
def on_button_hover(e):
    scrape_button["bg"] = button_hover_color
def on_button_leave(e):
    scrape_button["bg"] = primary_color
scrape_button = tk.Button(
    frame,
    text="Start Scraping",
    bg=primary_color,
    fg=text_color,
    font=("Helvetica", 14, "bold"),
    padx=20,
    pady=10,
    relief="flat",
    command=start_scraping,
    bd=0,
    highlightthickness=0,
    activebackground=button_hover_color
)
scrape_button.pack(pady=20)
scrape_button.bind("<Enter>", on_button_hover)
scrape_button.bind("<Leave>", on_button_leave)
# Footer
footer_label = tk.Label(
    window,
    text="Powered by Web Scraper | G21",
    font=("Helvetica", 10),
    bg=secondary_color,
    fg="#555555"
)
footer_label.pack(side="bottom", pady=10)
window.mainloop()

