from modules.utils import match, page_pic
from DATA.assets.MatchAssets import MatchAssets

class Page(MatchAssets):

    # 父类
    def __init__(self, pagename) -> None:
        self.name = pagename
        self.topages = dict()
    
    def add_topage(self, pagename, item):
        """
        添加从这一页面到另一页面的链接
        
        page: 另一页面的Page名
        item: 图片地址或坐标元组
        """
        self.topages[pagename]=item
    
    @staticmethod
    def is_page(pagename, threshold=0.87) -> bool:
        """
        确定当前截图是否是指定页面
        
        Parameters
        ----------
        pagename: 
            PageName下的页面名
        
        Return
        ------
        如果是指定页面，返回True，否则返回False
        """
        return match(page_pic(pagename), threshold=threshold)