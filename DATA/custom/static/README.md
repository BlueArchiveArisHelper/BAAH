# 目录说明

此目录为自定义静态文件目录，用于存放自定义的静态文件，如图片、CSS、JavaScript等。

若要修改CSS,建议直接修改`style.css`或将css文件放入此目录下，在`head.html`中引入。

## 用法

目录映射关系：`DATA/custom/static/` -> `/custom/static/`

如果你想添加背景图，将`background.jpg`放入此目录，然后在`style.css`中调用，如：

``` css
body {
    background-image: url("/custom/static/background.jpg");
}
```