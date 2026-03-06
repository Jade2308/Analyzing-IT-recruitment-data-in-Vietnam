from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time

# ── Đọc email & password từ file .env ──
load_dotenv()
EMAIL    = os.getenv("ITVIEC_EMAIL")
PASSWORD = os.getenv("ITVIEC_PASSWORD")

print(f"📧 Email   : {EMAIL}")
print(f"🔑 Password: {'*' * len(PASSWORD) if PASSWORD else 'CHƯA CÓ'}")

# ── Tạo trình duyệt ──
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
wait = WebDriverWait(driver, 15)

try:
    # ── BƯỚC 1: Mở trang đăng nhập ──
    print("\n🌐 Mở trang đăng nhập...")
    driver.get("https://itviec.com/sign_in")
    time.sleep(3)

    # ── BƯỚC 2: Nhập email ──
    print("✏️  Nhập email...")
    email_input = wait.until(
        EC.presence_of_element_located((By.ID, "user_email"))
    )
    email_input.clear()
    email_input.send_keys(EMAIL)
    time.sleep(1)

    # ── BƯỚC 3: Nhập password ──
    print("✏️  Nhập password...")
    pass_input = driver.find_element(By.ID, "user_password")
    pass_input.clear()
    pass_input.send_keys(PASSWORD)
    time.sleep(1)

    # ── BƯỚC 4: Bấm nút "Sign In with Email" ──
    print("🖱️  Bấm nút Sign In with Email...")
    login_btn = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//button[@type='submit' and contains(text(), 'Sign In with Email')]"
        ))
    )
    login_btn.click()
    time.sleep(4)

    # ── BƯỚC 5: Kiểm tra đăng nhập thành công chưa ──
    current_url = driver.current_url
    print(f"\n🔗 URL sau đăng nhập: {current_url}")

    if "sign_in" not in current_url:
        print("✅ ĐĂNG NHẬP THÀNH CÔNG!")

        # ── BƯỚC 6: Kiểm tra lương sau khi đăng nhập ──
        print("\n💰 Kiểm tra lương trên trang danh sách...")
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
                "[class*='Salary']",
                "div.salary",
                "span.salary",
                "[data-controller*='salary']",
                "[class*='sign-in-view-salary']",
            ]:
                salary_tag = card.select_one(selector)
                if salary_tag:
                    text = salary_tag.get_text(strip=True)
                    if text and "sign in" not in text.lower():
                        salary_text = text
                        break

            print(f"  [{i}] {title_text[:45]:<45} | 💰 {salary_text}")

    else:
        print("❌ ĐĂNG NHẬP THẤT BẠI!")
        print("   → Kiểm tra lại email/password trong file .env")

    time.sleep(3)

finally:
    driver.quit()
    print("\n🔒 Đóng trình duyệt")