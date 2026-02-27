from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

print("⏳ Đang khởi động trình duyệt...")

# Cấu hình
options = Options()
options.add_argument("--start-maximized")

# Khởi động Chrome (tự tải ChromeDriver phù hợp)
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# Mở trang ITViec
print("🌐 Đang mở ITViec...")
driver.get("https://itviec.com/it-jobs")

# Chờ 3 giây
time.sleep(3)

# In tiêu đề trang
print("📄 Tiêu đề trang:", driver.title)
print("🔗 URL hiện tại:", driver.current_url)

# Đóng
driver.quit()
print("✅ Test thành công! Selenium hoạt động bình thường.")