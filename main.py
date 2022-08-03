import json
import time
import os
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import csv
from selenium.webdriver.common.by import By


def write_csv(data):
    with open('instagram-info.csv', 'a', encoding="utf-8", newline='') as file:
        order = [
            'comment_count',
            'likes_count',
            'comment_text',
            'image_url'
        ]
        writer = csv.DictWriter(file, fieldnames=order)
        writer.writerow(data, )


def get_html(url):
    driver = uc.Chrome()
    driver.maximize_window()

    op = uc.ChromeOptions()
    op.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                    ' AppleWebKit/537.36 (KHTML, like Gecko)'
                    ' Chrome/102.0.0.0 Safari/537.36')

    try:
        driver.get(url)

        time.sleep(6)
        while True:
            with open('site.html', 'w', encoding="utf-8") as file:
                file.write(driver.page_source)

            break

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def get_data_if_need_authorization(url, login, password):
    driver = uc.Chrome()
    driver.maximize_window()

    op = uc.ChromeOptions()
    op.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                    ' AppleWebKit/537.36 (KHTML, like Gecko)'
                    ' Chrome/102.0.0.0 Safari/537.36')

    try:
        driver.get(url)
        time.sleep(3)

        login_input = driver.find_element("name", "username")
        login_input.send_keys(str(login))

        time.sleep(2)

        password_input = driver.find_element("name", "password")
        password_input.send_keys(str(password))

        time.sleep(2)

        driver.find_element(By.XPATH,
                            "/html/body/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[3]/button").click()

        time.sleep(6)

        driver.get(url)
        time.sleep(10)

        data = driver.page_source

        with open('site.html', 'w', encoding='UTF-8') as file:
            file.write(data)

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def json_response_from_html(html_path):
    soup = BeautifulSoup(html_path, 'lxml')

    block = soup.find('pre').text
    json_data = json.loads(block)
    edges_data = json_data['data']['user']['edge_owner_to_timeline_media']['edges']
    for data in edges_data:
        comment_count = data['node']['edge_media_to_comment']['count']
        likes_count = data['node']['edge_media_preview_like']['count']
        comment_text = data['node']['edge_media_to_caption']['edges'][0]['node']['text']
        image_url = data['node']['thumbnail_src']

        data = {
            'comment_count': comment_count,
            'likes_count': likes_count,
            'comment_text': comment_text,
            'image_url': image_url
        }

        write_csv(data)


def main():
    count = int(input('Сколько постов хотим спарсить?: '))
    try:
        os.remove('instagram-info.csv')
    except FileNotFoundError:
        print('csv file doesnt find')
        print('overwrite new csv')
    time.sleep(2)
    url = 'https://www.instagram.com/graphql/query/?query_hash=69cba40317214236af40e7efa697781d&variables=%7B%22id%' \
          '22%3A%2243802564195%22%2C%22first%22%3A{}%2C%22after%22%3A%22QVFDclhUOHRnSEw4ZDZ5akN3MGZxcU9UeEpuQ0t3Tlh' \
          'hWldHclYwcWJLRkFNWkpDSm0xdENPeVpZWjNrQmEwNjhPRkI1MGVkelNYTEd3WlA3aGdkRzM2bQ%3D%3D%22%7D'.format(count)

    get_html(url)
    print('HTML done')
    try:
        print('Wait...')
        with open('site.html', 'r', encoding='UTF-8') as file:
            json_response_from_html(file.read())
        print("Done")
    except AttributeError:
        login_data = str(input('Login: '))
        password_data = str(input('Password: '))
        get_data_if_need_authorization(url, login_data, password_data)
        print('Wait...')
        with open('site.html', 'r', encoding='UTF-8') as file:
            json_response_from_html(file.read())
        print("Done with authorization")


if __name__ == '__main__':
    main()
