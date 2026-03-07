from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import random
import os

# =============================================
# CẤU HÌNH
# =============================================
MAX_SAFETY_PAGES = 1000                  # Giới hạn an toàn tối đa (phòng lặp vô hạn)
SAVE_FOLDER  = "data/raw"
OUTPUT_FILE  = "data/raw/itviec_jobs.csv"
COOKIE_FILE  = "data/itviec_cookies.json"

# =============================================
# TẠO TRÌNH DUYỆT
# =============================================
def create_driver():
    options = Options()
    # options.add_argument("--headless")  # Bỏ # nếu muốn chạy ẩn
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

# =============================================
# ĐĂNG NHẬP BẰNG COOKIE
# =============================================
def login_with_cookie(driver):
    """Dùng cookie đã lưu để đăng nhập, không cần nhập tay"""

    if not os.path.exists(COOKIE_FILE):
        print("❌ Không tìm thấy file cookie!")
        print("   → Hãy chạy login_cookie.py trước")
        return False

    print("🍪 Đang đăng nhập bằng cookie...")

    # Phải vào trang trước rồi mới load cookie được
    driver.get("https://itviec.com")
    time.sleep(2)

    # Load cookie vào trình duyệt
    with open(COOKIE_FILE, "r") as f:
        cookies = json.load(f)

    for cookie in cookies:
        # Bỏ các trường có thể gây lỗi
        cookie.pop("sameSite", None)
        cookie.pop("expiry",   None)
        try:
            driver.add_cookie(cookie)
        except Exception:
            pass

    # Reload lại trang để cookie có hiệu lực
    driver.get("https://itviec.com/it-jobs")
    time.sleep(3)

    # Kiểm tra đăng nhập thành công chưa
    if "sign_in" not in driver.current_url:
        print("✅ Đăng nhập bằng cookie thành công!")
        return True
    else:
        print("⚠️ Cookie hết hạn! Hãy chạy lại login_cookie.py")
        return False

# =============================================
# LẤY TỔNG SỐ TRANG
# =============================================
def get_total_pages(driver):
    """Phát hiện tổng số trang phân trang từ trang danh sách đầu tiên"""
    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Tìm các link phân trang chứa số trang
        page_links = soup.select("a[href*='page=']")
        max_page = 1
        for link in page_links:
            href = link.get("href", "")
            link_text = link.get_text(strip=True)
            href_page  = href.split("page=")[-1].split("&")[0]
            for part in [link_text, href_page]:
                try:
                    num = int(part)
                    if num > max_page:
                        max_page = num
                except ValueError:
                    pass

        if max_page > 1:
            print(f"  📑 Phát hiện tổng {max_page} trang")
            return max_page

        # Fallback: tìm thẻ phân trang dạng khác
        pagination = soup.select_one("nav.pagination, ul.pagination, [data-total-pages]")
        if pagination:
            total_attr = pagination.get("data-total-pages")
            if total_attr:
                try:
                    return int(total_attr)
                except ValueError:
                    pass

    except Exception as e:
        print(f"  ⚠️ Không xác định được tổng số trang: {e}")

    return None

# =============================================
# LẤY THÔNG TIN TỪ TRANG DANH SÁCH
# =============================================
def get_jobs_from_page(driver, page):
    """Lấy thông tin JD từ 1 trang danh sách"""
    url = f"https://itviec.com/it-jobs?page={page}"
    jobs = []

    try:
        print(f"\n  📄 Đang mở trang {page}...")
        driver.get(url)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.job-card"))
        )
        time.sleep(random.uniform(2, 3))

        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_cards = soup.select("div.job-card")
        print(f"  ✅ Tìm thấy {len(job_cards)} JD")

        for card in job_cards:
            job = {
                "job_title"   : "",
                "company_name": "",
                "location"    : "",
                "salary"      : "",
                "skills"      : "",
                "url"         : "",
                "source"      : "itviec"
            }

            # --- Tên vị trí ---
            title_tag = card.select_one(
                "h3[data-search--job-selection-target='jobTitle']"
            )
            if title_tag:
                job["job_title"] = title_tag.get_text(strip=True)

            # --- URL chi tiết ---
            slug = card.get("data-search--job-selection-job-slug-value", "")
            if slug:
                job["url"] = f"https://itviec.com/it-jobs/{slug}"

            # --- Tên công ty ---
            for link in card.select("a[href*='/companies/']"):
                text = link.get_text(strip=True)
                if text:
                    job["company_name"] = text
                    break

            # --- Lương ---
            salary_text = ""
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
            job["salary"] = salary_text if salary_text else "Thỏa thuận"

            # --- Kỹ năng ---
            skill_tags = card.select("a[href*='click_source=Skill+tag']")
            job["skills"] = " | ".join([
                s.get_text(strip=True) for s in skill_tags
                if s.get_text(strip=True)
            ])

            if job["job_title"]:
                jobs.append(job)

    except TimeoutException:
        print(f"  ⚠️ Trang {page}: timeout")
    except Exception as e:
        print(f"  ❌ Lỗi trang {page}: {e}")

    return jobs

# =============================================
# LẤY CHI TIẾT TỪNG JD
# =============================================
def get_job_detail(driver, job):
    """Vào trang chi tiết lấy location & description"""
    if not job["url"]:
        return job

    try:
        driver.get(job["url"])
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
        )
        time.sleep(random.uniform(1, 2))

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # --- Địa điểm ---
        for selector in [
            "[class*='location']",
            "[class*='address']",
            "[class*='city']",
            "svg + span",
        ]:
            loc = soup.select_one(selector)
            if loc:
                text = loc.get_text(strip=True)
                if text:
                    job["location"] = text
                    break

        # --- Lương (kiểm tra lại trong trang chi tiết) ---
        if not job["salary"] or job["salary"] == "Thỏa thuận":
            for selector in ["[class*='salary']", "div.salary"]:
                sal = soup.select_one(selector)
                if sal:
                    text = sal.get_text(strip=True)
                    if text and "sign in" not in text.lower():
                        job["salary"] = text
                        break

        # --- Mô tả công việc ---
        for selector in [
            "div.job-description",
            "[class*='description']",
            "[class*='job-detail']",
        ]:
            desc = soup.select_one(selector)
            if desc:
                job["description"] = desc.get_text(
                    separator=" ", strip=True
                )[:500]
                break
        else:
            job["description"] = ""

    except TimeoutException:
        print(f"    ⚠️ Timeout: {job['url']}")
    except Exception as e:
        print(f"    ❌ Lỗi: {e}")

    return job

# =============================================
# CHẠY TOÀN BỘ
# =============================================
def run():
    print("=" * 55)
    print("🚀 BẮT ĐẦU CÀO DỮ LIỆU ITVIEC (CÓ ĐĂNG NHẬP)")
    print("=" * 55)

    os.makedirs(SAVE_FOLDER, exist_ok=True)
    driver   = create_driver()
    all_jobs = []

    try:
        # ── Đăng nhập bằng cookie ──
        logged_in = login_with_cookie(driver)
        if not logged_in:
            print("\n❌ Dừng lại — cần đăng nhập trước!")
            return

        # ── Bước 1: Lấy danh sách JD ──
        # Phát hiện tổng số trang từ trang đầu tiên
        print("\n📌 Bước 1: Xác định tổng số trang...")
        first_page_jobs = get_jobs_from_page(driver, 1)
        total_pages = get_total_pages(driver)
        all_jobs.extend(first_page_jobs)
        time.sleep(random.uniform(2, 3))

        if total_pages:
            print(f"  🗂️  Sẽ cào toàn bộ {total_pages} trang...")
            for page in range(2, total_pages + 1):
                jobs = get_jobs_from_page(driver, page)
                if not jobs:
                    print(f"  ⚠️  Trang {page} không có JD — dừng sớm")
                    break
                all_jobs.extend(jobs)
                time.sleep(random.uniform(2, 3))
        else:
            print("  ⚠️  Không xác định được tổng số trang — cào đến khi hết JD...")
            page = 2
            while page <= MAX_SAFETY_PAGES:
                jobs = get_jobs_from_page(driver, page)
                if not jobs:
                    print(f"  ✅ Trang {page} không có JD — đã cào hết")
                    break
                all_jobs.extend(jobs)
                time.sleep(random.uniform(2, 3))
                page += 1
            else:
                print(f"  ⚠️  Đã đạt giới hạn an toàn {MAX_SAFETY_PAGES} trang")

        print(f"\n✅ Tổng JD thu thập: {len(all_jobs)}")

        # ── Bước 2: Lấy chi tiết từng JD ──
        print(f"\n📌 Bước 2: Lấy chi tiết từng JD...")
        for i, job in enumerate(all_jobs, 1):
            print(f"  [{i:>3}/{len(all_jobs)}] {job['job_title'][:45]}...")
            all_jobs[i-1] = get_job_detail(driver, job)

            # Lưu tạm mỗi 20 JD
            if i % 20 == 0:
                pd.DataFrame(all_jobs).to_csv(
                    OUTPUT_FILE, index=False, encoding="utf-8-sig"
                )
                print(f"  💾 Đã lưu tạm {i} JD")

            time.sleep(random.uniform(2, 3))

    finally:
        driver.quit()
        print("\n🔒 Đã đóng trình duyệt")

    # ── Lưu file cuối cùng ──
    if all_jobs:
        df = pd.DataFrame(all_jobs)
        df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

        print("\n" + "=" * 55)
        print("✅ CÀO DỮ LIỆU HOÀN THÀNH!")
        print(f"📊 Tổng JD       : {len(df)}")
        print(f"💾 Lưu tại       : {OUTPUT_FILE}")
        print("=" * 55)

        # Thống kê nhanh
        has_salary = df[
            (df["salary"] != "Thỏa thuận") &
            (df["salary"] != "") &
            (~df["salary"].str.contains("love", case=False, na=False))
        ]
        print(f"\n💰 JD có thông tin lương : {len(has_salary)}/{len(df)}")
        print(f"📍 JD có địa điểm        : {df['location'].notna().sum()}/{len(df)}")

        print("\n📋 XEM THỬ 5 DÒNG ĐẦU:")
        print(df[["job_title", "company_name",
                  "salary", "location"]].head(5).to_string())
    else:
        print("❌ Không cào được dữ liệu nào!")


if __name__ == "__main__":
    run()