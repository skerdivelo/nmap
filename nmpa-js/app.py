from flask import Flask, request, jsonify, render_template
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import threading
import requests


app = Flask(__name__)

# Global lock for managing WebDriver reuse across threads
driver_lock = threading.Lock()

def get_webdriver():
    """Initialize and return a Selenium WebDriver instance."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service("./chromedriver-win64/chromedriver.exe")  # Path to ChromeDriver
    return webdriver.Chrome(service=service, options=options)

@app.route('/scan', methods=['POST'])
def scan():
    data = request.json
    start_ip = data.get('startIP')
    end_ip = data.get('endIP')
    port = int(data.get('port'))
    endpoint = data.get('endpoint', "")
    do_login = data.get('doLogin', False)

    def generate_ips(start_ip, end_ip):
        start_parts = list(map(int, start_ip.split('.')))
        end_parts = list(map(int, end_ip.split('.')))
        for i in range(start_parts[3], end_parts[3] + 1):
            yield f"{start_parts[0]}.{start_parts[1]}.{start_parts[2]}.{i}"

    scan_results = []
    for ip in generate_ips(start_ip, end_ip):
        url = f"http://{ip}:{port}{endpoint}"
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                scan_results.append(url)
        except requests.RequestException:
            pass

    return jsonify(scan_results)


@app.route('/login', methods=['POST'])
def login_to_servers():
    data = request.json
    urls = data.get('urls')
    username = "tecnico"
    password = data.get('password')

    results = []

    def login_to_server(url):
        retries = 2  # Number of retries for timeouts
        for attempt in range(retries + 1):
            try:
                print(f"Attempting to connect to: {url} (Attempt {attempt + 1})")

                # Step 1: Initialize Selenium WebDriver
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-images")  # Disable images
                options.add_argument("--blink-settings=imagesEnabled=false")  # Further disable image rendering
                service = Service("./chromedriver-win64/chromedriver.exe")
                driver = webdriver.Chrome(service=service, options=options)

                # Step 2: Open the login page
                driver.set_page_load_timeout(60)  # Extend timeout to 60 seconds
                driver.get(url)

                # Step 3: Fill in the login form
                driver.find_element(By.NAME, "username").send_keys(username)
                driver.find_element(By.NAME, "userpass").send_keys(password)
                driver.find_element(By.NAME, "commit").click()

                # Step 4: Wait for the page to load after login
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, "titoloFunzione"))
                )

                # Step 5: Extract the server name
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                titolo_div = soup.find('div', id='titoloFunzione')
                server_name = titolo_div.text.strip() if titolo_div else "Unknown"

                results.append({"url": url, "serverName": server_name, "status": "success"})
                break  # Exit the retry loop on success
            except Exception as e:
                print(f"Error on attempt {attempt + 1} for {url}: {e}")
                if attempt == retries:
                    results.append({"url": url, "reason": str(e), "status": "error"})
            finally:
                if 'driver' in locals():
                    driver.quit()

    # Use threads for faster processing
    threads = [threading.Thread(target=login_to_server, args=(url,)) for url in urls]

    # Start threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    return jsonify(results)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
