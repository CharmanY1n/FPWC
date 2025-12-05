#相当于是一个接口 调用task_executor
import argparse
import os

from scripts.utils import print_with_color

arg_desc = "AppAgent - deployment phase"
#解析命令行参数
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=arg_desc)
parser.add_argument("--app")
parser.add_argument("--root_dir", default="./")
parser.add_argument("--task_desc")
parser.add_argument("--grid", default=0, type=int)

#解析命令行参数,将结果转换为字典存储在args中
args = vars(parser.parse_args())

app = args["app"]
root_dir = args["root_dir"]
task_desc = args["task_desc"]
grid = args["grid"]

# task_desc = task_desc.replace(" ", "_")

print_with_color("Welcome to the deployment phase of AppAgent!\nBefore giving me the task, you should first tell me "
                 "the name of the app you want me to operate and what documentation base you want me to use. I will "
                 "try my best to complete the task without your intervention. First, please enter the main interface "
                 "of the app on your phone and provide the following information.", "yellow")

if not app:#如果命令行中没输入app,则手动输入
    print_with_color("What is the name of the target app?", "blue")
    app = input()
    app = app.replace(" ", "")

if not task_desc: #如果命令行中没输入task_desc,则手动输入
    print_with_color("What is the task description?", "blue")
    task_desc = input()
    task_desc = task_desc.replace(" ", "_")



#os.system()用于在命令行执行os命令
os.system(f"python /home/yinxiaoran/data/PhoneAgent/OurAgent/Smartphone-Agent-world-model/scripts/task_executor.py --app {app} --root_dir {root_dir} --task_desc {task_desc} --grid {grid}")
