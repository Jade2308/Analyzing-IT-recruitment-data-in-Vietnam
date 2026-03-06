from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

print("⏳ Đang khởi động trình duyệt...")

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

print("🌐 Đang mở ITViec...")
driver.get("https://itviec.com/it-jobs")

time.sleep(3)

print("📄 Tiêu đề trang:", driver.title)
print("✅ Selenium hoạt động bình thường!")

driver.quit()
print("🔒 Đã đóng trình duyệt")