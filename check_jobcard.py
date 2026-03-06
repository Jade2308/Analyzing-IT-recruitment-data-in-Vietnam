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

print("⏳ Chờ trang load...")
time.sleep(5)

soup = BeautifulSoup(driver.page_source, "html.parser")

# Lấy tất cả job-card
job_cards = soup.select("div.job-card")
print(f"\n✅ Tìm thấy {len(job_cards)} job-card")

# Xem chi tiết thẻ đầu tiên
print("\n📋 NỘI DUNG JOB-CARD ĐẦU TIÊN:")
print("=" * 60)
print(job_cards[0].prettify()[:2000])  # In 2000 ký tự đầu
print("=" * 60)

# Thử tìm link trong job-card
print("\n🔍 Tìm link (thẻ <a>) trong job-card đầu tiên:")
links = job_cards[0].select("a")
for link in links:
    print(f"  href='{link.get('href', '')}' | text='{link.get_text(strip=True)[:50]}'")

driver.quit()
print("\n🔒 Xong!")