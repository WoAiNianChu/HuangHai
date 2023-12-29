import requests
import json
import math
from prettytable import PrettyTable

print("#################################")
print("#                               #")
print("#     青岛黄海学院洗衣机详情    #")
print("#                               #")
print("#################################")

def get_remaining_time(goodsId):
    url = "https://yshz-user.haier-ioc.com/goods/stateList"
    payload = json.dumps({"goodsId": goodsId})
    response = requests.post(url, data=payload, headers=headers)
    data = response.json()
    state_list = data["data"]["stateList"]
    for state in state_list:
        if state["stateName"] in ["设备运行", "筒清洁"]:
            return (state["stateName"], state["time"])
    return ("未知状态", "未知时间")  # 返回一个默认值

while True:  # Start of the infinite loop
    url = "https://yshz-user.haier-ioc.com/position/nearPosition"
    headers = {
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.12(0x17000c21) NetType/WIFI Language/zh_CN",
        'Content-Type': "application/json",
        'Accept-Language': "zh-cn"
    }

    payload = {
        "lng": 120.1107406616211,
        "lat": 35.925567626953125,
        "categoryCode": "00",
        "page": 1,
        "pageSize": 10
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    total_pages = math.ceil(data['data']['total'] / data['data']['pageSize'])

    all_items = []

    for page in range(1, total_pages + 1):
        payload['page'] = page
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        items = data['data']['items']
        for item in items:
            if "黄岛" not in item['name'] and "创智之家" not in item['name']:
                all_items.append([
                    item['id'],
                    item['name'],
                    "营业中" if item['state'] == 1 else "非营业",
                    item['idleCount'],
                    "可以" if item['enableReserve'] else "不可以"
                ])

    all_items.sort(key=lambda x: x[1])

    table = PrettyTable(["序号", "ID", "名称", "状态", "空闲数量", "预约状态"])
    for counter, item in enumerate(all_items, start=1):
        table.add_row([counter] + item)

    print(table)

    while True:
        user_input = input("请输入序号或'q'退出: ")
        if user_input.lower() == 'q':
            exit(0)
        elif user_input.isdigit() and 1 <= int(user_input) <= len(all_items):
            selected_id = all_items[int(user_input)-1][0]
            break
        else:
            print("输入的序号无效，请重新输入。")

    url = "https://yshz-user.haier-ioc.com/position/deviceDetailPage"
    payload = json.dumps({
        "positionId": selected_id,
        "categoryCode": "00",
        "page": 1,
        "floorCode": "",
        "pageSize": 10
    })

    response = requests.post(url, data=payload, headers=headers)
    data = response.json()
    items = data["data"]["items"]

    unused_items = sorted((item for item in items if item["state"] == 1), key=lambda x: x["name"])

    table = PrettyTable(["洗衣机名称", "状态", "预约信息"])

    if not unused_items:
        print("当前没有可用的洗衣机。")
        items_with_time = [(item["name"], get_remaining_time(item["id"]), item) for item in items]
        items_with_time.sort(key=lambda x: (x[1][0] == '桶自洁', x[1][1]))
        for name, (state, time), item in items_with_time:
            enable_reserve = item["enableReserve"]
            if enable_reserve:
                reserve_msg = "可以预约"
            else:
                reserve_msg = "不支持预约"
            table.add_row([name, f"{state}剩余时间: {time}", reserve_msg])
    else:
        for item in unused_items:
            name = item["name"]
            enable_reserve = item["enableReserve"]
            if enable_reserve:
                reserve_msg = "可以预约"
            else:
                reserve_msg = "不支持预约"
            table.add_row([name, "当前未在使用", reserve_msg])

    print(table)
    
    input("按回车键继续...")  # Wait for the user to press enter before continuing
