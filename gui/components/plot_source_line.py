from nicegui import ui
import json
from datetime import datetime

# 数据转换函数
def convert_data(storage_data_list):
    raw_data = storage_data_list if storage_data_list else []
    dates = []
    credits = []
    diamonds = []
    
    for item in raw_data:
        # 添加日期（直接使用字符串或转换为日期对象）
        dates.append(item['date'])
        
        # 转换credit：滤出数字字符
        credit_value = int(''.join(filter(str.isdigit, item['credit'])))
        credits.append(credit_value)

        # 转换diamond：滤出数字字符
        diamond_value = int(''.join(filter(str.isdigit, item['diamond'])))
        diamonds.append(diamond_value)

    
    return dates, credits, diamonds


def filter_data_by_date(data_list, start_date=None, end_date=None):
    """
    根据日期范围筛选数据
    
    Args:
        data_list: 原始数据列表
        start_date: 开始日期 (YYYY-MM-DD格式字符串)
        end_date: 结束日期 (YYYY-MM-DD格式字符串)
    
    Returns:
        筛选后的数据列表
    """
    if not start_date and not end_date:
        return data_list
        
    filtered_data = []
    for item in data_list:
        item_date = datetime.strptime(item['date'], '%Y-%m-%d')
        
        if start_date and item_date < datetime.strptime(start_date, '%Y-%m-%d'):
            continue
            
        if end_date and item_date > datetime.strptime(end_date, '%Y-%m-%d'):
            continue
            
        filtered_data.append(item)
    
    return filtered_data


def create_line_chart(storage_data_list):
    """
    创建一个显示credit和diamond随时间变化的折线图。

    参数:
    storage_data_list (list): 包含日期、credit和diamond数据的字典列表。
    """

    # 获取最新日期的年份，并设置默认的年份范围
    if storage_data_list:
        # 遍历整个数据列表找到最新的日期
        latest_date = datetime.min
        for item in storage_data_list:
            item_date = datetime.strptime(item['date'], '%Y-%m-%d')
            if item_date > latest_date:
                latest_date = item_date
        if latest_date != datetime.min:
            current_year = latest_date.year
            default_start_date = f"{current_year}-01-01"
            default_end_date = f"{current_year}-12-31"
        else:
            # 如果没有有效日期，使用当前年份
            current_year = datetime.now().year
            default_start_date = f"{current_year}-01-01"
            default_end_date = f"{current_year}-12-31"
    else:
        # 如果没有数据，使用当前年份
        current_year = datetime.now().year
        default_start_date = f"{current_year}-01-01"
        default_end_date = f"{current_year}-12-31"

    # 存储日期筛选值的变量
    with ui.row().classes('items-center gap-4'):
        with ui.input('开始日期/Start Date', placeholder='YYYY-MM-DD', value=default_start_date) as start_date_input:
            with ui.menu().props('no-parent-event') as start_menu:
                with ui.date().bind_value(start_date_input):
                    with ui.row().classes('justify-end'):
                        ui.button('关闭/Close', on_click=start_menu.close).props('flat')
            with start_date_input.add_slot('append'):
                ui.icon('edit_calendar').on('click', start_menu.open).classes('cursor-pointer')
        
        with ui.input('结束日期/End Date', placeholder='YYYY-MM-DD', value=default_end_date) as end_date_input:
            with ui.menu().props('no-parent-event') as end_menu:
                with ui.date().bind_value(end_date_input):
                    with ui.row().classes('justify-end'):
                        ui.button('关闭/Close', on_click=end_menu.close).props('flat')
            with end_date_input.add_slot('append'):
                ui.icon('edit_calendar').on('click', end_menu.open).classes('cursor-pointer')
        
        # 添加筛选按钮
        ui.button('应用筛选/Apply Filter', on_click=lambda: update_chart()).classes('mt-4')
        ui.button('显示全部/Show All', on_click=lambda: (
            setattr(start_date_input, 'value', ''), 
            setattr(end_date_input, 'value', ''),
            update_chart()
        )).classes('mt-4 ml-2')
    
    # 创建初始图表数据
    dates, credits, diamonds = convert_data(storage_data_list)
    
    # 配置ECharts选项
    options = {
        
        # 图例配置
        "legend": {
            "data": ['Credit', 'Diamond'],
            "top": 30,
            "textStyle": {"fontSize": 14}
        },

        # 提示框配置
        "tooltip": {
            "trigger": 'axis',
            ":formatter": """
                function(params) {
                    // params 是一个数组，当 trigger 为 'axis' 时，包含当前横坐标对应的所有系列数据
                    let result = '<div style="font-weight:bold;">' + Array.isArray(params[0].value)?params[0].value[0]:'' + '</div>';
                    for (let i = 0; i < params.length; i++) {
                        // 确保从数据中提取数值部分
                        // 如果数据是 [日期, 数值] 的数组，则取索引1的值
                        let value = Array.isArray(params[i].value) ? params[i].value[1] : params[i].value;
                        // value 每三位添加逗号分隔符
                        value = value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                        // 使用默认的颜色标记 (小圆点)
                        result += '<div>' + params[i].marker + ' ' + params[i].seriesName + ': ' + value + '</div>';
                    }
                    return result;
                }
            """
        },
        
        # x轴配置（日期轴）
        "xAxis": {
            "type": 'time',
            "axisLabel": {
                "formatter": '{yyyy}-{MM}-{dd}',  # 日期格式
                "rotate": -40,  # 倾斜显示避免重叠
                "interval": 0  # 显示所有标签
            },
            "splitLine": {"show": True, "lineStyle": {"color": '#f0f0f0'}}  # 显示网格线
        },
        # y轴配置（双数值轴，因为credit和diamond数值范围差异大）
        "yAxis": [
            {
                "type": 'value',
                "position": 'left',
                "nameTextStyle": {"fontSize": 12},
                "splitLine": {"show": True, "lineStyle": {"color": '#f0f0f0'}}
            },
            {
                "type": 'value',
                "position": 'right',
                "nameTextStyle": {"fontSize": 12},
                "splitLine": {"show": False}  # 右侧Y轴不显示网格线，避免冲突
            }
        ],
        
        # 数据系列配置
        "series": [
            {
                "name": 'Credit',
                "type": 'line',
                "data": [[dates[i], credits[i]] for i in range(len(dates))],
                "yAxisIndex": 0,  # 使用第一个y轴
                "itemStyle": {
                    "color": '#FFD700'  # 金黄色
                },
                "lineStyle": {
                    "color": '#FFD700',
                    "width": 3
                },
                "symbolSize": 8, # 数据点大小
                "showSymbol": False,  # 默认不显示数据点
                "smooth": True,
                "areaStyle": {"color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1, 
                                       "colorStops": [{"offset": 0, "color": "rgba(255, 215, 0, 0.3)"}, 
                                                      {"offset": 1, "color": "rgba(255, 215, 0, 0)"}]}},
                "emphasis": {         # 悬停时的强调效果
                    "focus": 'series'
                }
            },
            {
                "name": 'Diamond',
                "type": 'line',
                "data": [[dates[i], diamonds[i]] for i in range(len(dates))],
                "yAxisIndex": 1,  # 使用第二个y轴
                "itemStyle": {
                    "color": '#1E90FF'  # 蓝色
                },
                "lineStyle": {
                    "color": '#1E90FF',
                    "width": 3
                },
                "symbolSize": 8,
                "showSymbol": False,  # 默认不显示数据点
                "smooth": True,
                "areaStyle": {"color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1, 
                                       "colorStops": [{"offset": 0, "color": "rgba(30, 144, 255, 0.3)"}, 
                                                      {"offset": 1, "color": "rgba(30, 144, 255, 0)"}]}},
                "emphasis": {         # 悬停时的强调效果
                    "focus": 'series'
                }
            }
        ],
        "grid": {"left": '5%', "right": '8%', "bottom": '15%', "top": '10%', "containLabel": True},  # 调整边距
    }
    
    chart = ui.echart(options=options)
    chart.style('height: 600px; width: 100%')
    
    def update_chart():
        # 根据筛选条件更新图表数据
        filtered_data = filter_data_by_date(storage_data_list, start_date_input.value, end_date_input.value)
        dates, credits, diamonds = convert_data(filtered_data)
        
        # 更新图表选项
        chart.options["series"][0]["data"] = [[dates[i], credits[i]] for i in range(len(dates))]
        chart.options["series"][1]["data"] = [[dates[i], diamonds[i]] for i in range(len(dates))]
        chart.update()
    
    update_chart()
    
    return chart

if __name__ in {'__main__',  '__mp_main__'}:
    storage_jsonfile_path = r'C:\Users\sanmu214\myfolder\mycode\BAAH\DATA\USER_STORAGE\STORAGEcc9ffef8.json'
    with open(storage_jsonfile_path, 'r', encoding='utf-8') as f:
        storage_data_json = json.load(f)
    ui.label('Credit and Diamond Over Time')
    create_line_chart(storage_data_json["HISTORY_MONEY_DIAMOND_LIST"])
    ui.run()