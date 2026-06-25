from nicegui import ui
from gui.components.list_edit_area import list_edit_area
from gui.components.cut_screenshot import screencut_button
import cv2
import numpy as np
from modules.utils import logging,istr,CN,EN

def transparent_right_bottom_part_of_image(matlike_image):
    """把图片右下角四分之一区域变为透明色，如果图片只有三个通道，扩充成四通道"""
    if matlike_image.shape[2] == 3:
        # 三通道图，扩展为四通道
        matlike_image = cv2.cvtColor(matlike_image, cv2.COLOR_BGR2BGRA)
    elif len(matlike_image.shape) == 3 and matlike_image.shape[2] == 4:
        # 四通道图，不做处理
        pass
    else:
        logging.error(istr({
            CN: "图片通道数不为3或4，无法处理",
            EN: "The number of channels in the image is not 3 or 4, cannot be processed"
        }))
    
    h, w = matlike_image.shape[:2]
    # 将右下角四分之一区域的alpha通道设为0
    matlike_image[h//2:, w//2:, 3] = 0
    return matlike_image

def pic_list_edit_area(config, datalist, component_desc):
    # 一维的能够添加/删除图片的组件，datalist是一个列表，linedesc是这个列表的描述
    # 直接对列表里的每个元素（图片路径）进行增删改，增删后调用refresh刷新组件
    @ui.refreshable
    def item_list():
        ui.label(component_desc)
        for i in range(len(datalist)):
            with ui.column():
                screencut_button(config, datalist[i], "path", save_folder_path=config.USER_STORAGE_FOLDER, post_process=transparent_right_bottom_part_of_image)
                ui.button(config.get_text("button_delete"), on_click=lambda i=i: action_delete_item(i)).style("margin-left: 10px")
        ui.button(config.get_text("button_add"), on_click=action_add_item).style("margin-top: 10px")
    
    def action_add_item():
        datalist.append({"path": ""})
        item_list.refresh()
    
    def action_delete_item(index):
        datalist.pop(index)
        item_list.refresh()

    item_list()


def set_timetable(config):
    with ui.row():
        ui.link_target("TIME_TABLE")
        ui.label(config.get_text("task_timetable")).style('font-size: x-large')
    
    ui.checkbox(config.get_text("config_smart_timetable_desc")).bind_value(config.userconfigdict, "SMART_TIMETABLE")
    
    with ui.column() as smart_area:
        ui.number(config.get_text("config_weight_of_rewards"), precision=0, step=1).bind_value(config.userconfigdict, "TIMETABLE_WEIGHT_OF_REWARD").style("width: 300px")
        ui.number(config.get_text("config_weight_of_hearts"), precision=0, step=1).bind_value(config.userconfigdict, "TIMETABLE_WEIGHT_OF_HEART").style("width: 300px")
        ui.number(config.get_text("config_weight_of_lock"), precision=0, step=1).bind_value(config.userconfigdict, "TIMETABLE_WEIGHT_OF_LOCK").style("width: 300px")
        pic_list_edit_area(config, config.userconfigdict["TIMETABLE_SPECIAL_STUDENT_PIC"], config.get_text("config_timetable_special_student_pic_desc"))
    smart_area.bind_visibility_from(config.userconfigdict, "SMART_TIMETABLE")
    
    with ui.column() as edit_area:
        list_edit_area(config.userconfigdict["TIMETABLE_TASK"], [config.get_text("config_location"), config.get_text("config_room")], config.get_text("config_desc_timetable"))
    edit_area.bind_visibility_from(config.userconfigdict, "SMART_TIMETABLE", backward=lambda x: not x)