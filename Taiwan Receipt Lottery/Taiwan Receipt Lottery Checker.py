from bs4 import BeautifulSoup
import requests

# 爬取本期統一發票中獎號碼
def lottery_numbers_crawler():
    # 財政部網站(自動更新至最新一期)
    url = 'http://invoice.etax.nat.gov.tw/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}
    req = requests.get(url, headers=headers)
    req.encoding = "utf8"
    soup = BeautifulSoup(req.text, 'html.parser')

    # 只爬最新一期號碼(area1, area2為上期)
    current_period = soup.select("div[id='area1'] h2")[1].text
    nums = soup.select("div[id='area1']")[0].select("tr span")
    x = [i.text for i in nums]

    # 建立中獎號碼字典
    lottery_nums = {'1000萬': x[0],
                   '200萬': x[1],
                   '其他獎': x[2].split('、'),
                   '200元': x[3]}

    return current_period, lottery_nums

# 確認發票是否中獎
def receipt_number_check(lottery_nums, my_number):
    number = my_number.split("-")[1]
    minimum_prize = list(map(lambda x: x[-3:], lottery_nums["其他獎"]))
    other_prize = {8:"20萬", 7:"4萬", 6:"1萬", 5:'4000', 4:'1000', 3:'200'}
    # 1000萬
    if number == lottery_nums["1000萬"]:
        result = "1000萬"
    # 200萬
    elif number == lottery_nums["200萬"]:
        result = "200萬"
    # 200元(增開六獎)
    elif number[-3:] == lottery_nums["200元"]:
        result = '200'
    else:
        if number[-3:] not in minimum_prize:
            result = "Sorry! You're not the chosen ones this time!"
        # 其他獎項
        else:
            check_result = []
            for i in range(3, 9):
                output = list(map(lambda x: x[-i:], lottery_nums["其他獎"]))
                n = number[-i:]
                if n in output:
                    check_result.append(len(n))
                else:
                    break
            result = other_prize[max(check_result)]

    return result

if __name__ == '__main__':
    my_number = 'AB-12345747'
    current_period, lottery_nums = lottery_numbers_crawler()
    check_result = receipt_number_check(lottery_nums, my_number)
    output = """民國{0} \n{1} \n\nInvoice number: {2} \nprize: {3}"""\
            .format(current_period, lottery_nums, my_number, check_result)

    print(output)