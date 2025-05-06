import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import time
from datetime import datetime

def lay_danh_sach_bai_viet():
    url = 'https://baomoi.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = set()
   
    for a in soup.find_all('a', {'href': True}):
        href = a.get('href')
        if href and "baomoi" in href: 
            full_link = href if href.startswith("http") else "https://baomoi.com" + href
            links.add(full_link)

    return list(links)

def lay_thong_tin_bai_viet(url):
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        tieu_de = soup.find('h1').text.strip() if soup.find('h1') else ''
        mo_ta = soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else ''
        hinh_anh_tag = soup.find('meta', {'property': 'og:image'})
        hinh_anh = hinh_anh_tag['content'] if hinh_anh_tag else ''
        noi_dung_tags = soup.select('.content')
        noi_dung = "\n".join(p.text.strip() for p in noi_dung_tags if p.text.strip())

        return {
            'Tiêu đề': tieu_de,
            'Mô tả': mo_ta,
            'Hình ảnh': hinh_anh,
            'Nội dung': noi_dung,
            'Link': url
        }
    except Exception as e:
        print(f"Lỗi lấy bài viết {url}: {e}")
        return None

def thu_thap_va_luu_du_lieu():
    print(f" Bắt đầu thu thập lúc {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    danh_sach_link = lay_danh_sach_bai_viet()
    print(f" Tìm thấy {len(danh_sach_link)} bài viết.")

    if len(danh_sach_link) == 0:
        print(" Không tìm thấy bài viết nào.")
        return

    du_lieu = []
    for link in danh_sach_link:
        print(f"Đang thu thập bài viết từ: {link}")  
        thong_tin = lay_thong_tin_bai_viet(link)
        if thong_tin:
            du_lieu.append(thong_tin)

    if du_lieu:
        df = pd.DataFrame(du_lieu)
        file_name = f"baomoi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(file_name, index=False, encoding='utf-8-sig')
        print(f"Đã lưu vào file: {file_name}")
    else:
        print(" Không có dữ liệu nào được thu thập.")

schedule.every().day.at("06:00").do(thu_thap_va_luu_du_lieu)
thu_thap_va_luu_du_lieu()
print("Đang chờ đến 6h sáng mỗi ngày để thu thập dữ liệu...")

while True:
    schedule.run_pending()
    time.sleep(60)
