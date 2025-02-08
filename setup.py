from cx_Freeze import setup, Executable

# 这里的 app.py 是你要打包的 Python 脚本
build_options = {
    "packages": [
        "PyQt5.QtCore", 
        "PyQt5.QtGui", 
        "PyQt5.QtWidgets", 
        "image_view",  # 自定义模块
        "shot",        # 自定义模块
        "shot_view",   # 自定义模块
        "connect",     # 自定义模块
    ],
    "excludes": [],  # 通常不需要排除标准库，除非你有特定需求
    "include_files": [],  # 如果有额外的文件（如图像、配置文件等），可以添加到此
}

setup(
    name="Latex标签器",   
    version="1.0",         
    description="Latex标签器程序",  
    options={"build_exe": build_options},  
    executables=[Executable("app.py", base="Win32GUI", icon="icons/logo.ico")],  
)
