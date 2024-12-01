import pandas as pd
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time

# 读取CSV文件，使用UTF-8编码
places_df = pd.read_csv('place.csv', encoding='utf-8')
# 将place列转换为列表
places = places_df['place'].tolist()

# 设置Edge浏览器的驱动路径，自动打开浏览器
driver = webdriver.Edge(executable_path=r"D:/Program Files (x86)/edgedriver_win64/msedgedriver.exe")

# 打开英文版谷歌地图主页
driver.get("https://www.google.com/maps?hl=en")
# 等待页面加载
time.sleep(5)

# 创建一个空列表来存储结果
results = []

for place_name in places:
    print(f"Searching for: {place_name}")

    try:
        # 找到搜索框并输入地点名称
        search_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//input[@id="searchboxinput"]'))
        )
        search_box.clear()
        search_box.send_keys(place_name)

        # 找到搜索按钮并点击
        search_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//button[@id="searchbox-searchbutton"]'))
        )
        search_button.click()

        # 等待页面加载搜索结果
        time.sleep(5)

        container_element = None

        # 尝试直接查找 'C7xf8b' 元素
        try:
            container_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.C7xf8b'))
            )
            print("Found element with class 'C7xf8b' without clicking.")
        except TimeoutException:
            print("Element with class 'C7xf8b' not found. Attempting to click the first search result.")
            # 如果没有找到 'C7xf8b' 元素，说明有多个结果，需要点击第一个搜索结果
            try:
                search_results = WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.Nv2PK'))
                )
                if len(search_results) > 0:
                    # 点击第一个搜索结果
                    search_results[0].click()
                    # 等待页面加载详细信息
                    time.sleep(5)

                    # 尝试再次查找 'C7xf8b' 元素
                    try:
                        container_element = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.C7xf8b'))
                        )
                        print("Found element with class 'C7xf8b' after clicking the first result.")
                    except TimeoutException:
                        print("Could not find element with class 'C7xf8b' after clicking the first result.")
                else:
                    print("No search results found. Skipping click operation.")
            except TimeoutException:
                print("Could not find the search results.")

        # 成功找到 'C7xf8b' 元素，提取相应信息
        if container_element:
            # 获取元素的HTML内容
            container_html = container_element.get_attribute('outerHTML')

            # 使用BeautifulSoup解析HTML内容，采用html.parser解析器
            soup = BeautifulSoup(container_html, 'html.parser')  # Changed to 'html.parser'
            # 直接获取该div元素（第一个匹配的）
            div = soup.find('div')

            if div:
                # 查找所有带有 aria-label 属性的元素
                aria_elements = div.find_all(attrs={"aria-label": True})

                # 设定天情况
                days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                day_index = 0
                time_start = None

                # 遍历并打印 aria-label 的值
                for element in aria_elements:
                    aria_label = element['aria-label']
                    # Replace non-breaking spaces
                    aria_label = aria_label.replace('\u00A0', ' ')

                    # 获取时间的前部分（如 "6 am" 或 "4 pm"）
                    time_part = aria_label.split(' at ')[-1].strip()

                    # 检查是否是新的一天的开始时间
                    if time_start is None:
                        time_start = time_part
                        print(f"Switching to the next day: {days[day_index]}")
                    elif time_part == time_start:
                        # 如果找到相同的时间，切换到下一天
                        day_index += 1
                        if day_index >= len(days):
                            break
                        print(f"Switching to the next day: {days[day_index]}")

                    # 排除只有百分比的元素
                    if not aria_label.endswith("."):
                        continue

                    # 存储结果为字典
                    results.append({
                        "Place Name": place_name,
                        "Day": days[day_index],
                        "Aria Label": aria_label
                    })
                    print(f"{place_name}, {days[day_index]}: {aria_label}")
            else:
                print("No div element found after locating 'C7xf8b'.")
        else:
            print("Could not find element with class 'C7xf8b' to extract data.")

    except TimeoutException:
        print("Could not find search box or search button.")

    # 等待一段时间再进行下一次搜索，避免被检测为机器人
    time.sleep(random.uniform(5, 10))

# 将结果保存为CSV文件，使用UTF-8编码
results_df = pd.DataFrame(results)
results_df.to_csv('place_popular times.csv', index=False, encoding='utf-8-sig')

# 关闭浏览器
driver.quit()
