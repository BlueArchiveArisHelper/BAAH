import numpy as np
import cv2
import os
import json
from modules.utils import config

# 走格子：https://bluearchive.wikiru.jp/?10%E7%AB%A0

# move: "left", "right", "left-up", "left-down", "right-up", "right-down", "center"
# exhange： 同上，必定交换。不交换的话用move
# portal: 同上，必定传送。不传送的话用move

class GridAnalyzer:
    """
    走格子类型的战斗的分析器
    
    sol_type是关卡的大类，"quest" 或者 "event", 读取某关的json文件，提供分析方法
    
    此类返回的坐标都是以数组为基底的，即左上角为原点，向下为第一轴正方向，向右为第二轴正方向。如果用于opencv的坐标，需要转换先后。
    """
    
    PIXEL_START_YELLOW = ((125, 250, 250), (132, 255, 255))
    """
    开始时的格子黄色
    """
    PIXEL_MAIN_YELLOW = ((163, 248, 250), (177, 255, 255))
    """
    过程中的聚焦队伍的格子黄色
    """
    # 国服的走格子头顶黄色箭头颜色暗一点,有些关卡敌人会有黄色感叹号(16, 219, 255)
    PIXEL_HEAD_YELLOW_CN_DARKER = ((2, 222, 249), (33, 233, 255))
    # 有些关卡敌人会有黄色感叹号，那个的第一位在30或40左右，第二位在220左右。hard关头顶有灯照着时，第一个数字会变暗。
    PIXEL_HEAD_YELLOW = ((4, 223, 254), (33, 235, 255))
    """
    过程中的聚焦队伍的头顶黄色箭头
    """
    # 标准起始方位的角度规定，有个center特殊判断
    START_MAP = {
        '180':"left",
        '0':"right",
        '360':"right",
        '120':"left-up",
        '240':"left-down",
        '60':"right-up",
        '300':"right-down",
        '90':"up",
        '270':"down"
    }
    # 队伍行走方向的距离方位偏，轴与数组轴保持一致
    WALK_MAP = {
        "left":(0, -115),
        "right":(0, 115),
        "left-up":(-80, -60),
        "left-down":(80, -60),
        "right-up":(-80, 60),
        "right-down":(80, 60),
        "center":(0, 0)
    }
    
    def __init__(self, sol_type, jsonfilename) -> None:
        self.jsonfilename = jsonfilename
        # 通过level_data是否为None判断是否读取成功
        self.level_data = None
        self.sol_type = sol_type
        # 尝试读取json文件
        try:
            with open(os.path.join(config.userconfigdict["GRID_SOL_PATH"], self.sol_type, self.jsonfilename), "r", encoding="utf8") as f:
                self.level_data = json.load(f)
        except Exception as e:
            print(e)
            raise Exception("读取关卡json文件失败")

    

    def get_mask(self, img, pixel_range, shrink_kernels=[(3, 3)]):
        """
        提取图片中特定颜色范围的元素，置为白。其他地方置为黑。返回灰度图
        """
        lower = np.array(pixel_range[0])
        upper = np.array(pixel_range[1])
        mask = cv2.inRange(img, lower, upper)
        # 转成灰度图
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        if shrink_kernels is None:
            return mask
        for shrink_kernel in shrink_kernels:
            # 对masker进行腐蚀操作，使用nxn的结构元素
            kernel = np.ones(shrink_kernel, np.uint8)
            mask = cv2.erode(mask, kernel)
        return mask

    def get_kmeans(self, img, n, max_iter=5):
        """
        对白色像素点套用kmeans算法
        
        当输入的图片白色有效像素点不足n个时，会返回loss为-1
        """
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 将img看成二维数组
        # 非0的像素点就是数据点
        # 为0的像素点就是背景
        # 随机n类，每类的中心点（x,y坐标）是随机的
        initial_centers = []
        for i in range(n):
            x = np.random.randint(0, img.shape[0])
            y = np.random.randint(0, img.shape[1])
            initial_centers.append([x, y])
        # print("initial_centers", initial_centers)
        
        centers = initial_centers
        # 每次迭代，每个类的中心点都会更新
        
        # 将图像数组展平
        all_points = img.reshape((-1, 1))
        # 在axis=1的方向上，添加两列，range
        all_points = np.hstack((all_points, np.arange(all_points.shape[0]).reshape((-1, 1))))
        all_points = np.hstack((all_points, np.arange(all_points.shape[0]).reshape((-1, 1))))
        
        # 处理第2列数据除以图像宽度得到整数，处理第3列数据除以图像宽度得到余数
        all_points[:, 1] = all_points[:, 1] // img.shape[1]
        all_points[:, 2] = all_points[:, 2] % img.shape[1]
        # 在axis=1的方向上，添加一列，初始值为0，为每个像素点的类别
        all_points = np.hstack((all_points, np.zeros((all_points.shape[0], 1))))
        # 后续只考虑非0的像素点 np.any(img[i] != 0)
        # 去除第一列为0的像素点
        all_points = all_points[all_points[:, 0] != 0]
        # print("all_points.shape", all_points.shape) # (n, 4)
        
        if all_points.shape[0] == 0:
            print("输入的图片全黑，没有有效像素点")
            return [(-1, -1)], -1
        
        for i in range(max_iter):
            # 每次迭代，计算每个像素点到每个类的距离，取最小的那个类下标赋值给第4列
            for j in range(all_points.shape[0]):
                distances = []
                for k in range(len(centers)):
                    distances.append(np.linalg.norm(all_points[j, 1:3] - centers[k]))
                all_points[j, 3] = np.argmin(distances)
            # 每次迭代，计算每个类的中心点
            for j in range(len(centers)):
                # 取出第4列等于j的所有像素点
                points = all_points[all_points[:, 3] == j]
                # 计算平均值，如果没有像素点（空簇问题），就在其他簇内的点随机挑一个设为这个的中心点
                if points.shape[0] != 0:
                    centers[j] = np.mean(points[:, 1:3], axis=0)
                else:
                    centers[j] = all_points[np.random.randint(0, all_points.shape[0]), 1:3]
            # print("iter centers", centers)
        # 计算最终的centers的失真函数
        loss = 0
        for j in range(len(centers)):
            points = all_points[all_points[:, 3] == j]
            loss += np.sum(np.linalg.norm(points[:, 1:3] - centers[j], axis=1))
        return centers, loss

    def multikmeans(self, img, n, each_max_iter=3, num_of_kmeans=5):
        """
        运行多次kmeans，取loss最小的centers返回，解决零簇问题
        
        没有中心的话会返回loss为-1
        """
        for i in range(num_of_kmeans):
            centers, loss = self.get_kmeans(img, n, each_max_iter)
            if i == 0:
                best_centers = centers
                best_loss = loss
            else:
                if loss < best_loss:
                    best_centers = centers
                    best_loss = loss
        # 计算全局中心点
        # 得到所有centers的中心点
        global_center = np.mean(centers, axis=0)
        return best_centers, best_loss, global_center

    def get_angle(self, start_centers, start_total_center):
        """
        求start_centers里每个点到start_total_center的角度和距离，角度计算以图像右侧，逆时针0-360度为标准
        """
        angles = []
        for center in start_centers:
            angle = np.arctan2(start_total_center[0] - center[0], center[1] - start_total_center[1]) * 180 / np.pi
            if angle < 0:
                angle += 360
            angles.append(angle)
        distances = []
        for center in start_centers:
            distance = np.sqrt((center[0] - start_total_center[0]) ** 2 + (center[1] - start_total_center[1]) ** 2)
            distances.append(distance)
        return angles, distances

    def get_direction(self, angles, distances, direction_list):
        """
        计算angles每个角度，与哪一个direction_list里标准方位的角度最接近，注意靠近360度的角度，要特殊处理
        
        angles: 屏幕上已知的聚类中心点相对角
        direction_list: 攻略说明的队伍初始位置
        """
        # print(direction_list)
        start_map_cv = {}
        
        # 只保留direction_list里有的方位
        for k in self.START_MAP:
            if self.START_MAP[k] in direction_list:
                start_map_cv[k] = self.START_MAP[k]
        # 开始处理，不过先筛选出center
        has_center_ind = -1
        if "center" in direction_list:
            # 找到distances里最小的那个下标作为center_ind
            has_center_ind = distances.index(min(distances))
        # print("start_map_cv", start_map_cv)
        directions = []
        for angle_ind in range(len(angles)):
            angle = angles[angle_ind]
            # 判断是否是center
            if angle_ind == has_center_ind:
                directions.append("center")
                continue
            min_diff = 360
            min_direction = ""
            for key in start_map_cv:
                diff = abs(int(key) - angle)
                if diff < min_diff:
                    min_diff = diff
                    min_direction = start_map_cv[key]
            # 匹配到之后，将键值对从start_map中删除，避免重复匹配
            need_delete = set()
            for key in start_map_cv:
                if start_map_cv[key] == min_direction:
                    need_delete.add(key)
            for key in need_delete:
                start_map_cv.pop(key)
            directions.append(min_direction)
        return directions
    
    def get_requires_list(self):
        """
        获取该关卡可以执行的策略方式名dict
        """
        return self.level_data["requires"]
    
    def get_initialteams(self, require_type):
        """
        获取require_type方案初始的初始队伍配置
        """
        return self.level_data[require_type]["initial_teams"]
    
    def get_num_of_steps(self, require_type):
        """
        获取require_type方案的回合总数
        """
        return len(self.level_data[require_type]["fight_plan"])
    
    def get_action_of_step(self, require_type, step_ind):
        """
        获取require_type方案第step_ind回合的行动，step_ind从0开始
        """
        return self.level_data[require_type]["fight_plan"][step_ind]
    
    def get_map_from_team_name2real_team_ind(self, require_type):
        """
        从推图文件里将下标0的A，下标1的B，下标2的C映射到正确的队伍编号上。这一步会读取用户配置的队伍强度表，并返回基于强度表的映射结果。

        比如，A对应的红色队伍是编队2，B对应的蓝色队伍是编队3，C对应的是编队1

        那么编队名列表（[A,B,C])的队伍对应实际队伍编号关系就应该是 [2,3,1]，取下标也就是 [1，2，0]
        """
        try:
            matched_team_ind = set()
            
            # 需要的攻击类型之间的权重
            weighted_matrix = {
                "red":{
                    "red": 4.0, "blue": 2.0, "yellow": 0.5, "purple": 2.0
                },
                "blue":{
                    "red": 0.5, "blue": 4.0, "yellow": 2.0, "purple": 3.0
                },
                "yellow":{
                    "red": 2.0, "blue": 0.5, "yellow": 4.0, "purple": 0.5
                },
                "purple":{
                    "red": 0.5, "blue": 2.0, "yellow": 2.0, "purple": 4.0
                }
            }
            # 队伍的强度表 red, blue, yellow, purple
            team_strength = config.userconfigdict["TEAM_SET_STRENGTH"]
            # 推图文件要求的队伍颜色 red, blue, yellow, purple, any
            team_color_required = [each["type"] for each in self.get_initialteams(require_type)]
            match_result_list = [0 for i in range(len(team_color_required))]
            # 先计算归一化后的team_strength,
            normalized_team_strength = []
            summarize_team_strength = []
            for ind,team in enumerate(team_strength):
                team_sum = sum([team[color] for color in team])
                # 小组长度为0的情况，就是没有配队
                if team_sum == 0:
                    matched_team_ind.add(ind)
                    summarize_team_strength.append(0)
                    normalized_team_strength.append({color:0 for color in team})
                else:
                    summarize_team_strength.append(team_sum)
                    normalized_team_strength.append({color:team[color]/team_sum for color in team})
            #? 找的时候，对于相同的优先级，使用靠前的队伍
            #! 这样排出来的队伍，会优先照顾推图文件里靠前出现的color
            def compute_similarity(team_weights_dict, color_weight):
                """
                team_weights_dict: 这个team的属性 {"red":8, "blue":4, "yellow":2, "purple":0}
                color_weight: 目标颜色的权重 {"red": 4.0, "blue": 2.0, "yellow": 0.5, "purple": 2.0}
                """
                # print(team_weights_dict, color_weight)
                manhattan_distance = 0
                for color in team_weights_dict:
                    manhattan_distance += team_weights_dict[color] * color_weight[color]
                return manhattan_distance
            # 1. 对于每个非any的required team,找到相似度最高的team_strength,匹配后记录下标到matched_team_ind
            for c_ind, required_color in enumerate(team_color_required):
                if required_color == "any":
                    continue
                # 计算相似度
                max_similarity = -1
                max_similarity_ind = 0
                # !先不考虑归一化 normalized_team_strength or team_strength
                for t_ind, user_team_weights in enumerate(team_strength):
                    similarity_val = compute_similarity(user_team_weights, weighted_matrix[required_color])
                    print(f"Team: {t_ind} with {required_color} : {similarity_val}")
                    if similarity_val > max_similarity and t_ind not in matched_team_ind:
                        max_similarity = similarity_val
                        max_similarity_ind = t_ind
                matched_team_ind.add(max_similarity_ind)
                match_result_list[c_ind] = max_similarity_ind
            
            # 2. 对于那些any的required team，找到team_strength里没有匹配的曼哈顿长度最长的，匹配后记录下标到matched_team_ind
            for c_ind, required_color in enumerate(team_color_required):
                if required_color != "any":
                    continue
                # 计算相似度
                max_similarity = -1
                max_similarity_ind = 0
                # !先不考虑归一化 normalized_team_strength or team_strength
                for t_ind, user_team_weights in enumerate(team_strength):
                    similarity_val = summarize_team_strength[t_ind]
                    print(f"Team: {t_ind} with {required_color} : {similarity_val}")
                    if similarity_val > max_similarity and t_ind not in matched_team_ind:
                        max_similarity = similarity_val
                        max_similarity_ind = t_ind
                matched_team_ind.add(max_similarity_ind)
                match_result_list[c_ind] = max_similarity_ind
            # 返回
            print(f"Color strength mapping (index list): {match_result_list}")
            return match_result_list
        except Exception as e:
            import traceback
            traceback.print_exc()
            return [i for i in range(len(self.get_initialteams(require_type)))]

    # 忽略成就弹窗
    # def ignore_achievement_popup(self, imgdata):
    #     """检测是否有成就弹窗，有的话忽略"""
    #     pass

    def get_head_triangle(self, imgdata):
        """
        获取头顶的黄色箭头的位置，返回中心点坐标，这里按照数组轴
        
        Parameters
        ----------
        imgdata : np.ndarray
            输入的图片
        pixel_range : tuple
            黄色箭头的颜色范围
        """
        ini_image = imgdata

        # 切割UI部分
        xs = [50, 1279] # 左右
        ys = [50, 590] # 上下

        image = ini_image[ys[0]:ys[1], xs[0]:xs[1]]

        # 筛选出黄色箭头
        head_yellow = ((2, 213, 250), (65, 235, 255))
        mask_head = self.get_mask(image, head_yellow, shrink_kernels=None)
        # 腐蚀操作
        # kernel = np.ones((3, 3), np.uint8)
        # eroded = cv2.erode(mask_head, kernel, iterations=1)
        # show(eroded)
        # 膨胀操作
        kernel = np.ones((8, 8), np.uint8)
        dilated = cv2.dilate(mask_head, kernel, iterations=1)
        # 边缘检测
        edges = cv2.Canny(dilated, 50, 150, apertureSize=3)

        # 找到轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        max_area = 0
        max_triangle = None

        # 对于每个轮廓，找最小的外接三角形，然后我们从中找到最大的一个
        for contour in contours:
            # 计算轮廓的最小外接三角形
            area, trg1 = cv2.minEnclosingTriangle(contour)
            if area > max_area:
                max_area = area
                max_triangle = trg1
        
        if max_triangle is None:
            return None

        # 去掉max_triangle的第2个维度
        max_triangle = max_triangle[:, 0, :]
        center_of_triangle = np.mean(max_triangle, axis=0)
        
        # print(max_triangle)
        # # 画出三角形，max_triangle是三个点的坐标
        # for i in range(3):
        #     cv2.line(image, (int(max_triangle[i][0]), int(max_triangle[i][1])), (int(max_triangle[(i + 1) % 3][0]), int(max_triangle[(i + 1) % 3][1])), (0, 255, 0), 3)
        # cv2.circle(image, (int(center_of_triangle[0]), int(center_of_triangle[1])), 7, (0, 0, 255), -1)
        
        # 加上截取掉的坐标
        real_center = center_of_triangle + np.array([xs[0], ys[0]])
        
        # 图片坐标转数组坐标
        return real_center[::-1]
