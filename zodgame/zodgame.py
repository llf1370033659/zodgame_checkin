# encoding=utf8
import os
import re
import sys

import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

def zodgame_checkin(driver, formhash):
    checkin_url = "https://zodgame.xyz/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&inajax=0"    
    checkin_query = """
        (function (){
        var request = new XMLHttpRequest();
        var fd = new FormData();
        fd.append("formhash","%s");
        fd.append("qdxq","kx");
        request.open("POST","%s",false);
        request.withCredentials=true;
        request.send(fd);
        return request;
        })();
        """ % (formhash, checkin_url)
    checkin_query = checkin_query.replace("\n", "")
    driver.set_script_timeout(240)
    resp = driver.execute_script("return " + checkin_query)
    match = re.search('<div class="c">\r\n(.*?)</div>\r\n', resp["response"], re.S)
    message = match[1] if match is not None else "签到失败"
    print(f"【签到】{message}")
    return "恭喜你签到成功!" in message or "您今日已经签到，请明天再来" in message


def zodgame_task(driver, formhash):

    def clear_handles(driver, main_handle):
        handles = driver.window_handles[:]
        for handle in handles:
            if handle != main_handle:
                driver.switch_to.window(handle)
                driver.close()
        driver.switch_to.window(main_handle)
      
    def show_task_reward(driver):
        driver.get("https://zodgame.xyz/plugin.php?id=jnbux")
        try:
            WebDriverWait(driver, 240).until(
                lambda x: x.title != "Just a moment..."
            )
            reward = driver.find_element(By.XPATH, '//li[contains(text(), "点币: ")]').get_attribute("textContent")[:-2]
            print(f"【Log】{reward}")
        except:
            pass

    driver.get("https://zodgame.xyz/plugin.php?id=jnbux")
    WebDriverWait(driver, 240).until(
        lambda x: x.title != "Just a moment..."
    )

    join_bux = driver.find_elements(By.XPATH, '//font[text()="开始参与任务"]')
    if len(join_bux) != 0 :    
        driver.get(f"https://zodgame.xyz/plugin.php?id=jnbux:jnbux&do=join&formhash={formhash}")
        WebDriverWait(driver, 240).until(
            lambda x: x.title != "Just a moment..."
        )
        driver.get("https://zodgame.xyz/plugin.php?id=jnbux")
        WebDriverWait(driver, 240).until(
            lambda x: x.title != "Just a moment..."
        )

    join_task_a = driver.find_elements(By.XPATH, '//a[text()="参与任务"]')
    success = True

    if len(join_task_a) == 0:
        print("【任务】所有任务均已完成。")
        return success
    handle = driver.current_window_handle
    for idx, a in enumerate(join_task_a):
        on_click = a.get_attribute("onclick")
        try:
            function = re.search(r"""openNewWindow(.*?)\(\)""", on_click, re.S)[0]
            script = driver.find_element(By.XPATH, f'//script[contains(text(), "{function}")]').get_attribute("text")
            task_url = re.search(r"""window.open\("(.*)", "newwindow"\)""", script, re.S)[1]
            driver.execute_script(f"""window.open("https://zodgame.xyz/{task_url}")""")
            driver.switch_to.window(driver.window_handles[-1])
            try:
                WebDriverWait(driver, 240).until(
                    lambda x: x.find_elements(By.XPATH, '//div[text()="成功！"]')
                )
            except:
                print(f"【Log】任务 {idx+1} 广告页检查失败。")
                pass

            try:     
                check_url = re.search(r"""showWindow\('check', '(.*)'\);""", on_click, re.S)[1]
                driver.get(f"https://zodgame.xyz/{check_url}")
                WebDriverWait(driver, 240).until(
                    lambda x: len(x.find_elements(By.XPATH, '//p[contains(text(), "检查成功, 积分已经加入您的帐户中")]')) != 0 
                        or x.title == "BUX广告点击赚积分 - ZodGame论坛 - Powered by Discuz!"
                )
            except:
                print(f"【Log】任务 {idx+1} 确认页检查失败。")
                pass

            print(f"【任务】任务 {idx+1} 成功。")
        except Exception as e:
            success = False
            print(f"【任务】任务 {idx+1} 失败。", type(e))
        finally:
            clear_handles(driver, handle)
    
    show_task_reward(driver)

    return success

def parse_cookies(cookie_string):
    cookie_string = cookie_string.strip()
    if cookie_string.lower().startswith("cookie:"):
        cookie_string = cookie_string[len("cookie:"):].strip()
    cookies = []
    for item in cookie_string.split(';'):
        if not item.strip():
            continue
        name, separator, value = item.partition('=')
        if not separator or not name.strip():
            raise ValueError("Invalid Cookie format; copy the complete Cookie request header.")
        cookies.append({"name": name.strip(), "value": value.strip()})
    required = {"qhMq_2132_saltkey", "qhMq_2132_auth"}
    if not required.issubset({cookie['name'] for cookie in cookies if cookie['value']}):
        raise ValueError("Cookie must include nonempty qhMq_2132_saltkey and qhMq_2132_auth.")
    return cookies


def zodgame(cookie_string):
    cookie_dict = parse_cookies(cookie_string)
    options = uc.ChromeOptions()
    options.add_argument("--disable-popup-blocking")
    chrome_kwargs = {"options": options}
    if os.environ.get("CHROME_BINARY"):
        chrome_kwargs["browser_executable_path"] = os.environ["CHROME_BINARY"]
    if os.environ.get("CHROMEDRIVER_BINARY"):
        chrome_kwargs["driver_executable_path"] = os.environ["CHROMEDRIVER_BINARY"]
    if os.environ.get("CHROME_VERSION"):
        chrome_kwargs["version_main"] = int(os.environ["CHROME_VERSION"].split('.')[0])
    if os.environ.get("ZODGAME_HEADLESS") == "1":
        chrome_kwargs["headless"] = True
    driver = uc.Chrome(**chrome_kwargs)

    # Load cookie
    try:
        driver.get("https://zodgame.xyz/")
        driver.delete_all_cookies()
        for cookie in cookie_dict:
            if cookie["name"] in ["qhMq_2132_saltkey", "qhMq_2132_auth"]:
                driver.add_cookie({
                    "domain": "zodgame.xyz",
                    "name": cookie["name"],
                    "value": cookie["value"],
                    "path": "/",
                })

        driver.get("https://zodgame.xyz/")

        WebDriverWait(driver, 240).until(
            lambda x: x.title != "Just a moment..."
        )
        assert len(driver.find_elements(By.XPATH, '//a[text()="用户名"]')) == 0, "Login fails. Please check your cookie."

        formhash = driver.find_element(By.XPATH, '//input[@name="formhash"]').get_attribute('value')
        assert zodgame_checkin(driver, formhash) and zodgame_task(driver, formhash), "Checkin failed or task failed."
    finally:
        driver.quit()
    
if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cookie_string = os.environ.get("ZODGAME_COOKIE") or (sys.argv[1] if len(sys.argv) > 1 else "")
    if not cookie_string:
        raise SystemExit("Missing ZODGAME_COOKIE. Add it as a repository Actions secret.")
    
    zodgame(cookie_string)
