import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import argparse
import sys
from selenium.common.exceptions import NoSuchElementException
import os

def setup_driver(chrome_path, headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
    service = Service(chrome_path)
    return webdriver.Chrome(service=service, options=chrome_options)

def configure_driver(driver, url):
    driver.get(url)
    # time.sleep(0.5)

def select_option_by_label(driver, label_text, value):
    label = driver.find_element(By.XPATH, f"//label[text()='{label_text}']")
    select_element = label.find_element(By.XPATH, "./following-sibling::select")
    Select(select_element).select_by_value(value)

def enter_text_by_label(driver, label_text, input_text):
    input_element = driver.find_element(By.XPATH, f"//label[contains(text(), '{label_text}')]/following-sibling::input")
    input_element.clear()
    input_element.send_keys(input_text)
    
def enter_textarea(driver, label_text, input_text):
    # 使用 XPath 定位包含指定文本的 label 对应的 textarea 元素
    input_element = driver.find_element(By.XPATH, f"//label[contains(text(), '{label_text}')]/following-sibling::textarea")
    input_element.clear()
    input_element.send_keys(input_text)

def click_button_by_text(driver, button_text):
    button = driver.find_element(By.XPATH, f"//button[text()='{button_text}']")
    button.click()
    # time.sleep(0.1)

def main():
    parser = argparse.ArgumentParser(description='Automate form filling on a DRG website.')
    parser.add_argument('basic_info', help='Comma-separated basic info values.')
    parser.add_argument('diagnosis_codes', help='Comma-separated list of diagnosis codes.')
    parser.add_argument('surgery_codes', help='Comma-separated list of surgery codes.')
    args = parser.parse_args()

    basic_info_parts = args.basic_info.split(',')
    diagnosis_codes = args.diagnosis_codes.split(',')
    surgery_codes = args.surgery_codes.split(',')
    
    print(basic_info_parts)
    print(diagnosis_codes)
    print(surgery_codes)
    # 获取当前脚本所在的文档夹路径
    current_dir = os.path.dirname(os.path.realpath(__file__))

    driver = setup_driver(os.path.join(current_dir, "chromedriver.exe"))
    
    index_path = os.path.join(current_dir, "OpenDRGWeb", "index.html")
    configure_driver(driver, f"file:///{index_path}")

    select_option_by_label(driver, "分组方案", basic_info_parts[0].strip())
    enter_text_by_label(driver, "病案号", basic_info_parts[1].strip())
    select_option_by_label(driver, "性别", basic_info_parts[2].strip())
    enter_text_by_label(driver, "年龄", basic_info_parts[3].strip())
    enter_text_by_label(driver, "年龄天", basic_info_parts[4].strip())
    enter_text_by_label(driver, "出生体重", basic_info_parts[5].strip())
    enter_text_by_label(driver, "科室", basic_info_parts[6].strip())
    enter_text_by_label(driver, "住院天数", basic_info_parts[7].strip())
    select_option_by_label(driver, "离院方式", basic_info_parts[8].strip())
    
    enter_textarea(driver, "诊断编码", ''.join(diagnosis_codes))
    enter_textarea(driver, "手术操作", ''.join(surgery_codes))

    click_button_by_text(driver, "DRG分组")

    # Process and print results
    try:
        td_element = driver.find_element(By.XPATH, "//div[contains(@class, 'div-block')]//table/tbody/tr/td")
        weight_value = td_element.text
    except NoSuchElementException:
        weight_value = ''  # 如果找不到元素，则设置 weight_value 为空字符串
    
    try:
        results = driver.find_elements(By.XPATH, "//div[@class='div-code']")
    except NoSuchElementException:
        results = []
    for result in results:
        modified_text = result.text.replace(" " + weight_value, "")
        print(modified_text)
    
    try:    
        li_elements = driver.find_elements(By.CSS_SELECTOR, "div.div-block > ul > li")
    except NoSuchElementException:
        li_elements = []
    for li in li_elements:
        print(li.text)

    driver.quit()
    

if __name__ == "__main__":
    main()
