import pandas as pd

# Đọc file CSV
df = pd.read_csv("data/raw/itviec_jobs.csv", encoding="utf-8-sig")

print("=" * 50)
print("📊 THÔNG TIN DATASET")
print("=" * 50)

print(f"\n✅ Tổng số JD     : {len(df)}")
print(f"✅ Số cột         : {len(df.columns)}")
print(f"✅ Tên các cột    : {list(df.columns)}")

print("\n" + "=" * 50)
print("📋 TỶ LỆ DỮ LIỆU TRỐNG (missing)")
print("=" * 50)
for col in df.columns:
    missing = df[col].isna().sum() + (df[col] == "").sum()
    pct = missing / len(df) * 100
    status = "✅" if pct < 30 else "⚠️" if pct < 60 else "❌"
    print(f"  {status} {col:<15}: {missing}/{len(df)} trống ({pct:.1f}%)")

print("\n" + "=" * 50)
print("🏆 TOP 10 VỊ TRÍ PHỔ BIẾN")
print("=" * 50)
print(df["job_title"].value_counts().head(10).to_string())

print("\n" + "=" * 50)
print("🛠️  TOP 15 KỸ NĂNG PHỔ BIẾN")
print("=" * 50)
# Tách skills ra từng kỹ năng riêng
all_skills = []
for skills in df["skills"].dropna():
    for skill in skills.split("|"):
        skill = skill.strip()
        if skill:
            all_skills.append(skill)

skill_counts = pd.Series(all_skills).value_counts().head(15)
print(skill_counts.to_string())

print("\n" + "=" * 50)
print("📍 PHÂN BỐ THEO ĐỊA ĐIỂM")
print("=" * 50)
print(df["location"].value_counts().head(10).to_string())