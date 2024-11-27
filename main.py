import tkinter as tk
from tkinter import messagebox, filedialog
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json
import os
import shutil
import requests

# Function to fetch webpage content
def fetch_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print("Error fetching " + url + ": " + str(e))
        return None

# =====================================================================
def extract_headings(soup):
    headings = []
    # Loop through heading tags from h1 to h6
    for i in range(1, 7):
        headings_in_level = soup.find_all('h' + str(i))
        for h in headings_in_level:
            headings.append(h.text.strip())
    return headings

# ====================================================================
def extract_paragraphs(soup):
    paragraphs = []
    for p in soup.find_all('p'):
        paragraphs.append(p.text.strip())
    return paragraphs

# ====================================================================
def extract_lists(soup):
    list_items = []
    for ul in soup.find_all('ul'):
        for li in ul.find_all('li'):
            list_items.append(li.text.strip())
    return list_items

# ====================================================================
def extract_links(soup):
    links = []
    for a in soup.find_all('a'):
        href = a.get('href')
        if href:  # Check if href exists
            links.append(href)
    return links

# ====================================================================
def extract_images(soup):
    image_sources = []
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:  # Check if src exists
            image_sources.append(src)
    return image_sources

# ====================================================================
def extract_content(soup):
    return {
        "Headings": extract_headings(soup),
        "Paragraphs": extract_paragraphs(soup),
        "Lists": extract_lists(soup),
        "Links": extract_links(soup),
        "Images": extract_images(soup),
    }

# ===================================================================================
# Check if file exists
def file_exists(filepath):
    return os.path.exists(filepath)

# ===================================================================================
# Save scraped data as JSON
def save_to_file(data, file_path):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print("Data successfully saved to " + file_path)
    except IOError as e:
        print("Error writing to " + file_path + ": " + str(e))

# ===================================================================================
def merge_data(existing_data, new_data):
    for key, value in new_data.items():
        if key in existing_data:
            print("Updating data for " + str(key) + "...")
            existing_data[key].update(value)
        else:
            print("Adding new data for " + str(key) + "...")
            existing_data[key] = value
    return existing_data

# ===================================================================================
def save_data(data, url, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    parsed_url = urlparse(url)
    page_name = parsed_url.path.strip('/').replace('/', '_') or "home"
    domain = parsed_url.netloc.replace('.', '_')
    file_name = domain + ".json"
    file_path = os.path.join(folder, file_name)
    structured_data = {page_name: data}
    print("Preparing to save data for " + url + " to " + file_path)
    if file_exists(file_path):
        try:
            with open(file_path, 'r') as file:
                existing_data = json.load(file)
            updated_data = merge_data(existing_data, structured_data)
            save_to_file(updated_data, file_path)
        except json.JSONDecodeError:
            print("Error reading " + file_path + ". Overwriting with new data.")
            save_to_file(structured_data, file_path)
    else:
        save_to_file(structured_data, file_path)

# =======================================================================
# Scrape a single page
def scrape_page(url, folder, visited):
    if url in visited:
        return []
    print("Scraping " + url + "...")
    content = fetch_webpage(url)
    if content is None:
        return []
    soup = BeautifulSoup(content, 'html.parser')
    data = extract_content(soup)
    save_data(data, url, folder)
    visited.add(url)
    return extract_links(soup)

# =======================================================================
# Recursively scrape website
def scrape_website_recursive(start_url, folder, visited, max_depth=2, depth=0):
    if depth > max_depth:
        return
    print("Scraping depth " + str(depth) + ": " + start_url)
    links = scrape_page(start_url, folder, visited)
    for link in links:
        full_url = urljoin(start_url, link)
        if urlparse(full_url).netloc:
            scrape_website_recursive(full_url, folder, visited, max_depth, depth + 1)

# =======================================================================
# Folder selection function
def select_folder():
    global folder_path
    selected_folder = filedialog.askdirectory(title="Select Destination Folder")
    if selected_folder:
        folder_path.set(selected_folder)
        folder_label.config(text="Folder: " + selected_folder)

# =======================================================================
# Start scraping process
def start_scraping():
    url_input = url_text.get("1.0", "end").strip()
    if not url_input:
        messagebox.showwarning("Input Error", "Please enter at least one URL!")
        return
    if not folder_path.get():
        messagebox.showwarning("Folder Error", "Please select a destination folder!")
        return
    urls = [url.strip() for url in url_input.split(",")]
    visited = set()
    for url in urls:
        scrape_website_recursive(url, folder_path.get(), visited, max_depth=3)
    messagebox.showinfo("Scraping Complete", "Scraping completed successfully!")

# =======================================================================
# Create the main application window
window = tk.Tk()
window.title("Web Scraper Tool")
window.geometry("700x600")
window.configure(bg="#2C3E50")

# Global folder path variable
folder_path = tk.StringVar()

# Styling
def style_button(btn):
    btn.configure(
        bg="#3498DB", fg="#FFFFFF", font=("Arial", 12, "bold"),
        activebackground="#2980B9", activeforeground="#FFFFFF",
        bd=0, relief="flat", padx=10, pady=5, cursor="hand2"
    )
    btn.bind("<Enter>", lambda e: btn.config(bg="#2980B9"))
    btn.bind("<Leave>", lambda e: btn.config(bg="#3498DB"))

# Header
header = tk.Label(
    window, text="🌐 Web Scraper Tool", font=("Arial", 24, "bold"),
    bg="#34495E", fg="#ECF0F1", pady=15
)
header.pack(fill="x")

# Frame for input
frame = tk.Frame(window, bg="#ECF0F1", bd=5, relief="groove")
frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=400)

# Input section
tk.Label(frame, text="Enter URLs (comma-separated):", font=("Arial", 12), bg="#ECF0F1").pack(anchor="w", padx=20, pady=5)
url_text = tk.Text(frame, height=5, width=60, font=("Arial", 11), bd=1, relief="solid")
url_text.pack(padx=20, pady=5)

# Folder selection
folder_button = tk.Button(frame, text="Select Folder", command=select_folder)
style_button(folder_button)
folder_button.pack(pady=10)

folder_label = tk.Label(frame, text="No folder selected", font=("Arial", 10), bg="#ECF0F1", fg="#7F8C8D")
folder_label.pack()

# Start Scraping button
scrape_button = tk.Button(frame, text="Start Scraping", command=start_scraping)
style_button(scrape_button)
scrape_button.pack(pady=20)

# Footer
footer = tk.Label(
    window, text="© 2024 Web Scraper Tool | Powered by Python",
    font=("Arial", 10), bg="#2C3E50", fg="#95A5A6"
)
footer.pack(side="bottom", pady=10)

# Run the application
window.mainloop()
