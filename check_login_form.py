from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

print("🌐 Mở trang đăng nhập...")
driver.get("https://itviec.com/sign_in")

WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.TAG_NAME, "form"))
)
time.sleep(3)

soup = BeautifulSoup(driver.page_source, "html.parser")

# ── Tìm tất cả input trong form ──
print("\n📋 TẤT CẢ INPUT TRONG FORM:")
inputs = soup.select("input")
for inp in inputs:
    print(f"  type='{inp.get('type','')}' | id='{inp.get('id','')}' | name='{inp.get('name','')}' | placeholder='{inp.get('placeholder','')}'")

# ── Tìm tất cả button ──
print("\n📋 TẤT CẢ BUTTON:")
buttons = soup.select("button")
for btn in buttons:
    print(f"  type='{btn.get('type','')}' | id='{btn.get('id','')}' | class='{btn.get('class','')}' | text='{btn.get_text(strip=True)}'")

# ── Tìm tất cả thẻ có type=submit ──
print("\n📋 TẤT CẢ NÚT SUBMIT:")
submits = soup.select("[type='submit']")
for s in submits:
    print(f"  tag='{s.name}' | id='{s.get('id','')}' | name='{s.get('name','')}' | class='{s.get('class','')}' | text='{s.get_text(strip=True)}'")

driver.quit()
print("\n🔒 Xong!")