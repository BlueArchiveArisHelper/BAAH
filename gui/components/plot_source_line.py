from nicegui import ui
import json

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


def create_line_chart(storage_data_list):
    """
    创建一个显示credit和diamond随时间变化的折线图。

    参数:
    storage_data_list (list): 包含日期、credit和diamond数据的字典列表。
    """
    dates, credits, diamonds = convert_data(storage_data_list)
    # 配置ECharts选项
    options = {
        
        # 图例配置
        "legend": {
            "data": ['Credit', 'Diamond'],
            "top": 30
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
            }
        },
        
        # y轴配置（双数值轴，因为credit和diamond数值范围差异大）
        "yAxis": [
            {"type": 'value','position':'left'},
            {"type": 'value','position':'right'},
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
                "symbolSize": 8  # 数据点大小
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
                "symbolSize": 8
            }
        ]
    }
    
    # 创建ECharts图表
    chart = ui.echart(options=options)
    return chart

if __name__ in {'__main__',  '__mp_main__'}:
    storage_jsonfile_path = r'C:\Users\sanmu214\myfolder\mycode\BAAH\DATA\USER_STORAGE\STORAGEcc9ffef8.json'
    with open(storage_jsonfile_path, 'r', encoding='utf-8') as f:
        storage_data_json = json.load(f)
    ui.label('Credit and Diamond Over Time')
    create_line_chart(storage_data_json["HISTORY_MONEY_DIAMOND_LIST"])
    ui.run()