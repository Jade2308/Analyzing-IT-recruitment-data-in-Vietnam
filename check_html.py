from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

print("🌐 Đang mở ITViec...")
driver.get("https://itviec.com/it-jobs")

# Chờ 5 giây cho trang load xong
print("⏳ Chờ trang load...")
time.sleep(5)

# Lấy HTML trang
soup = BeautifulSoup(driver.page_source, "html.parser")

# ── Thử tìm các thẻ khác nhau ──
print("\n🔍 Đang tìm thẻ chứa danh sách JD...")

# Thử 1
test1 = soup.select("h3.title a")
print(f"  h3.title a          → {len(test1)} kết quả")

# Thử 2
test2 = soup.select("a.title")
print(f"  a.title             → {len(test2)} kết quả")

# Thử 3
test3 = soup.select("div.job-card")
print(f"  div.job-card        → {len(test3)} kết quả")

# Thử 4
test4 = soup.select("div[data-job-id]")
print(f"  div[data-job-id]    → {len(test4)} kết quả")

# Thử 5
test5 = soup.select("article")
print(f"  article             → {len(test5)} kết quả")

# Thử 6
test6 = soup.select("h2 a")
print(f"  h2 a                → {len(test6)} kết quả")

# Thử 7 — Tìm tất cả thẻ có chứa chữ "job"
test7 = soup.select("[class*='job']")
print(f"  [class*='job']      → {len(test7)} kết quả")

# In thử class của 3 thẻ đầu
if test7:
    print("\n📋 Class của 3 thẻ đầu có chữ 'job':")
    for tag in test7[:3]:
        print(f"    <{tag.name} class='{tag.get('class')}'>")

# Lưu HTML để xem thử
with open("page_source.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)
print("\n💾 Đã lưu HTML vào file: page_source.html")

driver.quit()
print("🔒 Xong!")