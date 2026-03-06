from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time
import os

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# ── BƯỚC 1: Mở trang đăng nhập ──
print("🌐 Mở trang đăng nhập ITViec...")
driver.get("https://itviec.com/sign_in")

# ── BƯỚC 2: Chờ bạn đăng nhập thủ công ──
print("\n" + "=" * 50)
print("👉 BÂY GIỜ BẠN HÃY:")
print("   1. Nhìn vào cửa sổ Chrome vừa mở")
print("   2. TỰ TAY nhập email và password")
print("   3. Bấm nút 'Sign In with Email'")
print("   4. Chờ đăng nhập xong")
print("=" * 50)
print("\n⏳ Chương trình sẽ tự động tiếp tục sau 30 giây...")
print("   (Bạn có 30 giây để đăng nhập)")

# Đếm ngược 30 giây
for i in range(30, 0, -5):
    print(f"   ⏰ Còn {i} giây...")
    time.sleep(5)

# ── BƯỚC 3: Kiểm tra đã đăng nhập chưa ──
current_url = driver.current_url
print(f"\n🔗 URL hiện tại: {current_url}")

if "sign_in" not in current_url:
    print("✅ ĐĂNG NHẬP THÀNH CÔNG!")

    # ── BƯỚC 4: Lưu cookie ──
    cookies = driver.get_cookies()
    os.makedirs("data", exist_ok=True)
    with open("data/itviec_cookies.json", "w") as f:
        json.dump(cookies, f)
    print(f"💾 Đã lưu {len(cookies)} cookies → data/itviec_cookies.json")

    # ── BƯỚC 5: Kiểm tra lương ngay ──
    print("\n💰 Kiểm tra lương sau khi đăng nhập...")
    driver.get("https://itviec.com/it-jobs")
    time.sleep(4)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_cards = soup.select("div.job-card")

    print(f"\n📋 Lương của 5 JD đầu tiên:")
    print("-" * 70)
    for i, card in enumerate(job_cards[:5], 1):

        # Tên JD
        title = card.select_one("h3")
        title_text = title.get_text(strip=True) if title else "N/A"

        # Tìm lương
        salary_text = "Không tìm thấy"
        for selector in [
            "[class*='salary']",
            "div.salary",
            "span.salary",
            "[data-controller*='salary']",
        ]:
            salary_tag = card.select_one(selector)
            if salary_tag:
                text = salary_tag.get_text(strip=True)
                if text and "sign in" not in text.lower():
                    salary_text = text
                    break

        print(f"  [{i}] {title_text[:45]:<45} | 💰 {salary_text}")

else:
    print("❌ Chưa đăng nhập hoặc đăng nhập thất bại!")
    print("   → Hãy chạy lại và đăng nhập nhanh hơn trong 30 giây")

time.sleep(3)
driver.quit()
print("\n🔒 Đóng trình duyệt")