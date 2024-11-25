import tkinter as tk
from tkinter import messagebox, PhotoImage, simpledialog
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import json
import time
import os
import shutil
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
# ======================================================================
def extract_paragraphs(soup):
    paragraphs = []
    for p in soup.find_all('p'):
        paragraphs.append(p.text.strip())
    return paragraphs
# =======================================================================
def extract_lists(soup):
    list_items = []
    for ul in soup.find_all('ul'):
        for li in ul.find_all('li'):
            list_items.append(li.text.strip())
    return list_items
# ======================================================================
def extract_links(soup):
    links = []
    for a in soup.find_all('a'):
        href = a.get('href')
        if href:  # Check if href exists
            links.append(href)
    return links
# ======================================================================
def extract_images(soup):
    image_sources = []
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:  # Check if src exists
            image_sources.append(src)
    return image_sources
# =========================================================================
def extract_content(soup):
    return {
        "Headings": extract_headings(soup),
        "Paragraphs": extract_paragraphs(soup),
        "Lists": extract_lists(soup),
        "Links": extract_links(soup),
        "Images": extract_images(soup),
    }
# =======================================================================
def filedailon(filepath):
    """Check if a file exists before attempting to overwrite or access it."""
    return os.path.exists(filepath)
# ========================================================================
def save_data(data, url, destination_folder):
    """Save the extracted data to JSON files in the specified destination folder."""
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    parsed_url = urlparse(url)
    page_name = parsed_url.path.strip('/').replace('/', '_') or "home"
    netloc = parsed_url.netloc.replace('.', '_')
    json_file_name = netloc + ".json"
    json_path = os.path.join(destination_folder, json_file_name)
    structured_data = {page_name: data}
    # Debugging print to ensure correct saving process
    print("Saving data for " + url + " to " + json_path)
  # Debugging line
    print("Extracted Data:", structured_data)  # Debugging line
    if filedailon(json_path):  # Check if the file exists
        try:
            with open(json_path, 'r') as json_file:
                existing_data = json.load(json_file)  # Load existing data
                print("Existing data loaded from " + json_path)
            # Merge the new data with the existing data, appending the new page
            if page_name in existing_data:
                print("Data for " + page_name + " already exists, updating...")
                existing_data[page_name].update(structured_data[page_name])  # Update if data already exists
            else:
                print("Adding new data for " + page_name + "...")
                existing_data.update(structured_data)  # Add the new page data
                with open(json_path, 'w') as json_file:
                    json.dump(existing_data, json_file, indent=4)  # Save the updated data back to the file
            print("Updated data saved to " + json_path)
        except json.JSONDecodeError as e:
            print("Error loading existing data: " + str(e))
  # Error handling if existing data can't be loaded
            # If the file is empty or corrupted, save the structured data directly
            with open(json_path, 'w') as json_file:
                json.dump(structured_data, json_file, indent=4)
            print("Saved new data to " + json_path + " due to load error.")
    else:
        # If the JSON file does not exist, create it and save the structured data
        with open(json_path, 'w') as json_file:
            json.dump(structured_data, json_file, indent=4)
        print("Created new file and saved data to " + json_path)
 # Debugging line
# =====================================================================
def move_file(file_path, target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    try:
        shutil.move(file_path, target_dir)
        print("Moved " + file_path + " to " + target_dir)
    except Exception as e:
        print("Error moving file " + file_path + ": " + str(e))
# =====================================================================
def scrape_page(url, destination_folder, visited):
    """Scrape a single page, save its data, and return its links."""
    if url in visited:  # Skip already visited URLs
        return []
    print("Scraping " + url + "...")
    html_content = fetch_webpage(url)
    if html_content is None:
        return []
    soup = BeautifulSoup(html_content, 'html.parser')
    data = extract_content(soup)
    # Save data to a unique file
    save_data(data, url, destination_folder)
    visited.add(url)  # Mark the URL as visited
    return extract_links(soup)  # Return all links on the page
def scrape_website_recursive(start_url, destination_folder, visited, max_depth=2, current_depth=0):
    """Recursively scrape all pages starting from the given URL."""
    if current_depth > max_depth:
        return
    print("Scraping depth " + str(current_depth) + ": " + start_url)
    # Scrape the current page
    links = scrape_page(start_url, destination_folder, visited)
    # Resolve and recursively scrape all links on the current page
    for link in links:
        full_url = urljoin(start_url, link)  # Resolve relative links
        parsed_url = urlparse(full_url)
        if parsed_url.netloc:  # Only scrape valid links
            scrape_website_recursive(full_url, destination_folder, visited, max_depth, current_depth + 1)
def start_scraping():
    """GUI function to start scraping."""
    url_input = url_text.get("1.0", "end").strip()
    destination_input = destination_entry.get().strip()

    if not url_input:
        messagebox.showwarning("Input Error", "Please enter at least one URL!")
        return
    if not destination_input:
        messagebox.showwarning("Input Error", "Please enter at least one destination folder!")
        return
    # Get URLs and destination folders
    urls = [url.strip() for url in url_input.split(",")]
    destinations = [folder.strip() for folder in destination_input.split(",")]
    # Map each URL to a destination folder
    url_folder_mapping = {}
    for idx, url in enumerate(urls):
        folder_choice = simpledialog.askstring(
            "Choose Folder",
           "Select folder for URL " + url + ":\n" + ', '.join(destinations),
            parent=window
        )
        if folder_choice and folder_choice.strip() in destinations:
            url_folder_mapping[url] = folder_choice.strip()
        else:
            messagebox.showwarning("Invalid Folder", "Invalid folder choice. Using default folder.")
            url_folder_mapping[url] = destinations[0]  # Default to first folder
    # Start recursive scraping
    visited = set()
    for url, folder in url_folder_mapping.items():
        scrape_website_recursive(url, folder, visited, max_depth=3)  # Adjust max_depth as needed
    messagebox.showinfo("Scraping Complete", "Scraped all URLs successfully!")
# ====================================================================================================
# GUI setup
# GUI setup
window = tk.Tk()
window.title("Web Scraper Tool")
window.geometry("600x500")
# Custom fonts and colors
primary_color = "#4CAF50"  # Green
secondary_color = "#f0f0f0"  # Light Gray
text_color = "#ffffff"  # White
button_hover_color = "#45A049"  # Darker green for button hover
# Add a styled background
if os.path.exists("bg.png"):
    bg_image = PhotoImage(file="bg.png")
    background_label = tk.Label(window, image=bg_image)
    background_label.place(relwidth=1, relheight=1)
else:
    window.configure(bg=secondary_color)
# Frame for the content
frame = tk.Frame(window, bg="#ffffff", bd=5, relief="groove")
frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=400)
# Title label with a larger font
title_label = tk.Label(
    frame,
    text="🕸 Web Scraper Tool",
    font=("Helvetica", 20, "bold"),
    bg=primary_color,
    fg=text_color,
    pady=10
)
title_label.pack(fill="x")
# Spacing between sections
def add_spacer(height):
    tk.Label(frame, bg="#ffffff", height=height).pack()
# Add input for URLs
add_spacer(1)
tk.Label(
    frame, text="Enter URLs (comma-separated):", font=("Helvetica", 12), bg="#ffffff", fg="#333333"
).pack(anchor="w", padx=20)
url_text = tk.Text(frame, height=5, width=50, font=("Helvetica", 11))
url_text.pack(padx=20, pady=5)
# Add input for destination folders
add_spacer(1)
tk.Label(
    frame, text="Destination Folders (comma-separated):", font=("Helvetica", 12), bg="#ffffff", fg="#333333"
).pack(anchor="w", padx=20)
destination_entry = tk.Entry(frame, width=50, font=("Helvetica", 11))
destination_entry.pack(padx=20, pady=5)
# Add a styled button with hover effect
def on_enter(e):
    scrape_button["bg"] = button_hover_color
def on_leave(e):
    scrape_button["bg"] = primary_color
scrape_button = tk.Button(
    frame,
    text="Start Scraping",
    bg=primary_color,
    fg=text_color,
    font=("Helvetica", 14, "bold"),
    padx=20,
    pady=5,
    relief="raised",
    command=start_scraping
)
scrape_button.pack(pady=20)
scrape_button.bind("<Enter>", on_enter)
scrape_button.bind("<Leave>", on_leave)

# Add a footer
footer_label = tk.Label(
    window,
    text="Powered by Web Scraper| G21",
    font=("Helvetica", 10),
    bg=secondary_color,
    fg="#555555")
footer_label.pack(side="bottom", pady=10)
window.mainloop()
