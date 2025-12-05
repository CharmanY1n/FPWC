import argparse 
import ast 
import datetime 
import json 
import os 
import re 
import sys 
import time
import xml.etree.ElementTree as ET 
import shutil 

from mobile_agent_benchmark.task_orchestrator import TaskOrchestrator

import prompts
from config import load_config
from and_controller import list_all_devices, AndroidController, traverse_tree
from model import (
    ask_gpt4v, parse_explore_rsp, parse_grid_rsp, parse_select_rsp, parse_generate_rsp, 
    parse_summary_rsp, parse_generate_graph, parse_post_see_rsp, parse_istrue_rsp
)
from utils import (print_with_color, draw_bbox_multi, encode_image, 
                   draw_grid, crop_image, read_txt_files, read_txt_file
)


class PlanExecutionError(Exception):
    pass

def reset_state():
    task_complete = False
    round_count = 0
    plan=""
    current_vertex = ""
    act_history = ""
    vertices = ""
    edges = ""
    wrong_information = "You should specifically focus on the following information, which shows your previous wrong/ineffective actions on this screen. All numbers shown below should not be chosen anymore!! You should choose other elements to interact with or think about other actions to perform:"
    wrong_time = 0
    vertices_list = ""
    edge_list = ""
    grid_on = False
    Remind_thing = ""
    cols=0
    rows=0
    doc_list = {}
    act_history=""
    

orchestrator = TaskOrchestrator(log_dir='/home/yinxiaoran/data/PhoneAgent/OurAgent/logs') 

wrong_time = 0
round_count = 0
device_list = list_all_devices()
if not device_list:
    print_with_color("ERROR: No device found!", "red")
    raise Exception("No device found!")
print_with_color(f"List of devices attached:\n{str(device_list)}", "yellow")
if len(device_list) == 1:
    device = device_list[0]
    print_with_color(f"Device selected: {device}", "yellow")
else:
    print_with_color("Please choose the Android device to start demo by entering its ID:", "blue")
    device = input()
controller = AndroidController(device)

def area_to_xy(area, subarea):
    area -= 1
    row, col = area // cols, area % cols
    x_0, y_0 = col * (width // cols), row * (height // rows)
    if subarea == "top-left":
        x, y = x_0 + (width // cols) // 4, y_0 + (height // rows) // 4
    elif subarea == "top":
        x, y = x_0 + (width // cols) // 2, y_0 + (height // rows) // 4
    elif subarea == "top-right":
        x, y = x_0 + (width // cols) * 3 // 4, y_0 + (height // rows) // 4
    elif subarea == "left":
        x, y = x_0 + (width // cols) // 4, y_0 + (height // rows) // 2
    elif subarea == "right":
        x, y = x_0 + (width // cols) * 3 // 4, y_0 + (height // rows) // 2
    elif subarea == "bottom-left":
        x, y = x_0 + (width // cols) // 4, y_0 + (height // rows) * 3 // 4
    elif subarea == "bottom":
        x, y = x_0 + (width // cols) // 2, y_0 + (height // rows) * 3 // 4
    elif subarea == "bottom-right":
        x, y = x_0 + (width // cols) * 3 // 4, y_0 + (height // rows) * 3 // 4
    else:
        x, y = x_0 + (width // cols) // 2, y_0 + (height // rows) // 2
    return x, y




def wait():
    time.sleep(configs["REQUEST_INTERVAL"])



def act_plan(plan):
    # conduct a plan which is a string of python code as a function
    plan = str(plan)
    # the function is executed in a sandbox environment
    try:
        print("Plan Before Execution: ", plan)
        exec(compile(plan, 'plan', 'exec'), globals())
    # execute the function
    except PlanExecutionError as e:
        print(f"Plan define error: {e}")
        return
    
    try:

        print(new_plan())
        global task_complete
        task_complete = True
    except ValueError as e: 
        # new plan will raises an error as e, then we will recursively call act_plan with e
        print("new plan!")
        act_plan(e)






def isTRUE(statement):
    # judge if a statement is true or false, based on the screenshot and the statement
    global act_history
    global round_count
    global vertices
    global edges
    global current_vertex
    global plan
    global wrong_information
    global wrong_time
    global vertices_list
    global edges_list
    global grid_on
    global Remind_thing
    global cols
    global rows
    global doc_list
    
    zoom_in = False
    area = ""
    previous_elements = ""
    
    while True:
        screenshot_path = controller.get_screenshot(f"{dir_name}_{round_count}", task_dir)
        xml_path = controller.get_xml(f"{dir_name}_{round_count}", task_dir)

        tree=ET.parse(xml_path)
        root=tree.getroot()
        xml_data=ET.tostring(root,encoding='utf8').decode('utf8')

        if screenshot_path == "ERROR" or xml_path == "ERROR":
            print_with_color("ERROR: Failed to capture screenshot or get UI tree", "red")
            reset_state()
            raise Exception("Failed to capture screenshot or get UI tree")

        clickable_list = []
        focusable_list = []
        traverse_tree(xml_path, clickable_list, "clickable", True)
        traverse_tree(xml_path, focusable_list, "focusable", True)
        elem_list = clickable_list.copy()
        for elem in focusable_list:
            bbox = elem.bbox
            center = (bbox[0][0] + bbox[1][0]) // 2, (bbox[0][1] + bbox[1][1]) // 2
            close = False
            for e in clickable_list:
                bbox = e.bbox
                center_ = (bbox[0][0] + bbox[1][0]) // 2, (bbox[0][1] + bbox[1][1]) // 2
                dist = (abs(center[0] - center_[0]) ** 2 + abs(center[1] - center_[1]) ** 2) ** 0.5
                if dist <= configs["MIN_DIST"]:
                    close = True
                    break
            if not close:
                elem_list.append(elem)

        draw_bbox_multi(screenshot_path, os.path.join(task_dir, f"{dir_name}_{round_count}_istrue.png"), elem_list,
                        dark_mode=configs["DARK_MODE"])

        img1 = encode_image(os.path.join(task_dir, f"{dir_name}_{round_count}_istrue.png"))

        if zoom_in:
            source_path = os.path.join(task_dir, f"{dir_name}_{round_count}_istrue.png")
            crop_path = os.path.join(task_dir,f"{dir_name}_{round_count}_istrue_element.png")
            tl,br=elem_list[area - 1].bbox
            crop_img=crop_image(source_path,[tl[0],tl[1],br[0],br[1]],crop_path)
            img2=encode_image(crop_path)

        if zoom_in:
            prompt = prompts.is_true_again_template
            prompt = re.sub(r"<element_tag>", area, prompt)
            prompt = re.sub(r"<all previous elements>", previous_elements, prompt)
        else:
            prompt = prompts.is_true_template

        prompt = re.sub(r"<element_tag>", area, prompt)
        prompt = re.sub(r"<task_description>", task_desc, prompt)
        prompt=re.sub(r"<mission_plan>",plan,prompt)
        prompt=re.sub(r"<statement>",statement,prompt)
        prompt=re.sub(r"<current_vertex>",current_vertex,prompt)

                    

        
        content = [
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img1}",
                    "detail": "high"
                }
            }
        ]
        if zoom_in:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img2}",
                    "detail": "high"
                }
            })
        print_with_color(f"judging statement: {statement}", "yellow")

        rsp = ask_gpt4v(content)
        observation, think, zoom_in_tag, answer = parse_istrue_rsp(rsp)
        if "tag" in zoom_in_tag:
            zoom_in = True
            area = re.findall(r"(.*?)$", zoom_in, re.MULTILINE)[0]
            previous_elements = previous_elements + area + " "
            continue
        else:
            answer = answer.strip()
            assert answer.lower() == "true" or answer.lower() == "false"
            act_history+=f"Statement {statement} is {answer}. Thought: "+think+"\n"

            if answer.lower() == "true":
                return True
            else:
                return False

def upper_left(area, rows, cols):
    # the upper left grid of the current grid
    area -= 1
    row, col = area // cols, area % cols
    upper_left_row = row-1 if row-1 >= 0 else row
    upper_left_col = col-1 if col-1 >= 0 else col

    return upper_left_row * cols + upper_left_col + 1

def bottom_right(area, rows, cols):
    # the bottom right grid of the current grid
    area -= 1
    row, col = area // cols, area % cols
    bottom_right_row = row+1 if row+1 < rows else row
    bottom_right_col = col+1 if col+1 < cols else col

    return bottom_right_row * cols + bottom_right_col + 1


def E(vertex, action, uid = None, imagined = False):
    # this function executes the E function (edge in the graph) in the plan
    # use global to modify global variables in this function
    global act_history
    global round_count
    global vertices
    global edges
    global current_vertex
    global plan
    global wrong_information
    global wrong_time
    global vertices_list
    global edges_list
    global grid_on
    global Remind_thing
    global cols
    global rows
    global doc_list


    from_doc = False

    current_vertex = vertex


    # when wrong_time >= 2, the grid will be on
    if wrong_time >=2:
        grid_on = True

    

    print_with_color(f"Round {round_count}", "yellow")
    orchestrator.before_one_action()

    screenshot_path = controller.get_screenshot(f"{dir_name}_{round_count}", task_dir)
    xml_path = controller.get_xml(f"{dir_name}_{round_count}", task_dir)

    tree=ET.parse(xml_path)
    root=tree.getroot()
    xml_data=ET.tostring(root,encoding='utf8').decode('utf8')
    
    act_name = None
    num_elem = None
    
    if screenshot_path == "ERROR" or xml_path == "ERROR":
        print_with_color("ERROR: Failed to capture screenshot or get UI tree", "red")
        reset_state()
        raise Exception("Failed to capture screenshot or get UI tree!")

    if grid_on:
        all_done = False

        rows, cols = draw_grid(screenshot_path, os.path.join(task_dir, f"{dir_name}_{round_count}_grid.png"))


        base64_img = encode_image(os.path.join(task_dir, f"{dir_name}_{round_count}_grid.png"))
        prompt = prompts.task_template_grid

    else:
        all_done = False
        # The agent will use the document to help make decisions when it meets the same elements it met before
        repeated_doc_pre = "When you are previously at this page (possibly with different contents displayed), you have acted on some of the UI elements. You should pay special attention to these elements to aid your decision:" # area, effect
        clickable_list = []
        focusable_list = []
        traverse_tree(xml_path, clickable_list, "clickable", True)
        traverse_tree(xml_path, focusable_list, "focusable", True)
        

        for elem in clickable_list:
            bbox = elem.bbox
            box_areas = (bbox[1][0] - bbox[0][0]) * (bbox[1][1] - bbox[0][1])

            # ignore all elements that are too large (the full screen is 2423520 pixels)
            if box_areas>2423520/4:
                clickable_list.remove(elem)

        elem_list = clickable_list.copy()
        area = 1

        for elem in focusable_list:
            bbox = elem.bbox
            center = (bbox[0][0] + bbox[1][0]) // 2, (bbox[0][1] + bbox[1][1]) // 2
            # the area the box takes up
            box_areas = (bbox[1][0] - bbox[0][0]) * (bbox[1][1] - bbox[0][1])
            
            close = False

            if box_areas>2423520/4:
                close = True
            else:

                for e in clickable_list:
                    bbox = e.bbox
                    center_ = (bbox[0][0] + bbox[1][0]) // 2, (bbox[0][1] + bbox[1][1]) // 2
                    dist = (abs(center[0] - center_[0]) ** 2 + abs(center[1] - center_[1]) ** 2) ** 0.5
                    if dist <= configs["MIN_DIST"]:
                        close = True
                        break
            if not close:
                elem_list.append(elem)
                

                if elem in doc_list:
                    repeated_doc_pre += "\nNumerical tag " + str(area) + ": "+ doc_list[elem]
                
                area += 1


        
        num_elem = draw_bbox_multi(screenshot_path, os.path.join(task_dir, f"{dir_name}_{round_count}_labeled.png"), elem_list,
                        dark_mode=configs["DARK_MODE"])

        base64_img = encode_image(os.path.join(task_dir, f"{dir_name}_{round_count}_labeled.png"))
        if uid is None:
            pass
        else:

            for i, elem in enumerate(elem_list):
                if elem.uid == uid:
                    from_doc = True
                    elem_ID = i + 1
                    if "tap" in action:
                        # action = "tap(" + str(i + 1) + ")"
                        act_name  = "tap"
                        res = [act_name, i + 1]

                        all_done = True
                    elif "long_press" in action:
                        # action = "long_press(" + str(i + 1) + ")"
                        act_name = "long_press"
                        res = [act_name, i + 1]
                        all_done = True
                    elif "swipe" in action:
                        # action = "swipe(" + str(i + 1) + ")"
                        act_name = "swipe"
                    #只能指定一个UID
                    break

    ################################################################################################
    # get the action
    elem_ID = None
    if all_done:
        print("Using doc for this action.")
    else:
        while True:

            if grid_on:
                all_done = False
                rows, cols = draw_grid(screenshot_path, os.path.join(task_dir, f"{dir_name}_{round_count}_grid.png"))


                base64_img = encode_image(os.path.join(task_dir, f"{dir_name}_{round_count}_grid.png"))

            

            if act_name is not None:
                #
                prompt = prompts.task_swip_template
                prompt = re.sub(r"<predefined_element>", str(elem_ID), prompt)
            else:
                if grid_on:
                    prompt = prompts.task_template_grid
                else:
                    prompt = prompts.task_template
                    if "\n" in repeated_doc_pre:

                        prompt = re.sub(r"<repeated_doc>", repeated_doc_pre, prompt)
                    else:
                        prompt = re.sub(r"<repeated_doc>", "", prompt)
            

            prompt = re.sub(r"<task_description>", task_desc, prompt)
            prompt=re.sub(r"<Vertices>",vertices,prompt)
            prompt=re.sub(r"<Edges>",edges,prompt)
            prompt=re.sub(r"<mission_plan>",plan,prompt)

            if num_elem is not None:
                prompt=re.sub(r"<num_elem>",str(num_elem),prompt)
            

            if act_history:
                prompt=re.sub(r"<act_history>","History trajectories:" + act_history,prompt)
            else:
                prompt=re.sub(r"<act_history>","",prompt)
            

            print("wrong time:", wrong_time)


            # the first line in the wrong_information is a "must-exist" sentence, the rest lines are the wrong information
            if "\n" in wrong_information:

                prompt=re.sub(r"<Wrong_information>",wrong_information ,prompt)
            else:
                prompt=re.sub(r"<Wrong_information>","",prompt)

            current_vertex = current_vertex.strip()

            current_vertex = current_vertex.replace("\n", "")
            prompt=re.sub(r"<current_vertex>",current_vertex,prompt)

            prompt = re.sub(r"<function>", "E("+ current_vertex + ", " +action + ")", prompt) 
            # the thing that should be reminded from the graph and plan revisor in the last round
            Remind_thing = Remind_thing.replace("\n", "")
            Remind_thing = Remind_thing.strip()
            if Remind_thing:
                prompt = re.sub(r"<Remind_thing>","Important reminder from the last round of action that needs special attention: " + Remind_thing, prompt)
            else:
                prompt = re.sub(r"<Remind_thing>", "", prompt)


            print("act history:",act_history)
            
            content = [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_img}",
                        "detail": "high"
                    }
                }
            ]
            print_with_color("Thinking about what to do in the next step...", "yellow")

            rsp = ask_gpt4v(content)
            resp_sum=rsp
            if "error" not in rsp:

                if grid_on:
                    res = parse_grid_rsp(rsp)

                else:
                    res = parse_explore_rsp(rsp)
                act_name = res[0]
                last_act = res[-1] 
                res = res[:-1]

                if act_name == "grid":
                    grid_on = True
                    act_name = None
                    continue


                if act_name == "FINISH":
                    task_complete = True
                    break
                elif act_name == "ERROR":
                    print_with_color("ERROR: failed to parse act_name", "red")
                    reset_state()
                    raise Exception("Failed to parse act_name!")

        ################################################################################################
        # verify the action 
                
                elif not from_doc and ("tap" in act_name or "long_press" in act_name or "swipe" in act_name):
                
                    print("\n\n\nNow we come to verification.")
                    if act_name == "tap" or act_name == "long_press":
                        _,area=res 
                        
                    elif act_name == "swipe":
                        _, area, swipe_dir, dist = res

                    
                    
                    if not "grid" in act_name:
                        source_path = os.path.join(task_dir, f"{dir_name}_{round_count}_labeled.png")
                        crop_path = os.path.join(task_dir,f"{dir_name}_{round_count}_element.png")
                        tl,br=elem_list[area - 1].bbox
                        try:

                            crop_img=crop_image(source_path,[tl[0],tl[1],br[0],br[1]],crop_path)
                        except:
                            grid_on = True
                            continue
                    else:
                        source_path = os.path.join(task_dir, f"{dir_name}_{round_count}_grid.png")
                        crop_path = os.path.join(task_dir,f"{dir_name}_{round_count}_element.png")

                        
                        if "swipe" in act_name:
                            _, start_area, start_subarea, end_area, end_subarea = res
                            if start_area<end_area:
                                left_up = area_to_xy(start_area, "top-left")
                                right_down = area_to_xy(end_area, "bottom-right")
                            else:
                                left_up = area_to_xy(end_area, "top-left")
                                right_down = area_to_xy(start_area, "bottom-right")
                        else:
                            _, area, subarea = res
                            bottom_right_area = bottom_right(area, rows, cols)
                            upper_left_area = upper_left(area, rows, cols)
                            

                            left_up = area_to_xy(upper_left_area, "top-left")
                            right_down = area_to_xy(bottom_right_area, "bottom-right")
                        

                            

                        crop_img=crop_image(source_path,[left_up[0],left_up[1],right_down[0],right_down[1]],crop_path)
                    
                    img1=encode_image(source_path)
                    img2=encode_image(crop_path)

                    if grid_on:
                        prompt = re.sub(r"<summary>", last_act, prompts.sys2think_grid_template)
                    else:

                        prompt = re.sub(r"<task_description>",task_desc,prompts.CoT_thinking_template)
                        prompt=re.sub(r"<ui_element>",str(res[1]),prompt)
                        prompt=re.sub(r"<summary>",last_act,prompt)
                    
                    detailed_action=act_name 
                    if "grid" not in act_name:
                        detailed_action += "(" + str(res[1]) + ")"
                    if act_name == "swipe":
                        detailed_action+="Direction: "+str(swipe_dir)+"Distance: "+str(dist)
                    if act_name == "swipe_grid":
                        detailed_action=act_name+ " from " + str(start_area) + " to " + str(end_area)
                        action_for_prompt = act_name+ " from " + str(start_area) + " to " + str(end_area)
                    elif "grid" in act_name:
                        detailed_action = detailed_action.replace("_grid", "")
                        action_for_prompt = detailed_action + " the " + str(subarea) +" of the grid " + str(area)
                        detailed_action += "(" + str(area) + ", '" + str(subarea) + "')"
                        
            
                    if "grid" in act_name:
                        prompt = re.sub(r"<action>",action_for_prompt,prompt)

                    content=[
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url":f"data:image/jpeg;base64,{img1}",
                            "detail": "high"}
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url":f"data:image/jpeg;base64,{img2}",
                            "detail": "high"}
                        }
                    ]
                    rsp=ask_gpt4v(content)
                    if "error" not in rsp:
                        msg=rsp.choices[0].message.content
                        
                        msg = re.sub(r"###","",msg)
                        Answer = [line for line in msg.split("\n") if "Answer" in line][0]
                        answer_content = Answer.split(":")[1].strip()
                        answer_content = re.sub(r"\*\*", "", answer_content)
                        Decision,explanation = answer_content.split(".")[0],answer_content.split(".")[1]
                        
                        if "False" in msg:
                            msg=msg.replace(".","")
                            Err=msg.split(",")[1]
                        print("Crop Response:",msg)

                        if(Decision=="False"):
                            print_with_color("This round's decision is wrong.","magenta")

                            wrong_information += f"\n{wrong_time}: You have proposed one action but this is verified to be wrong. The wrong action is: "+ detailed_action
                            wrong_information +=". The reason for why the action is wrong is: "+explanation+"You should think another action/element to interact with."
                            wrong_time += 1
                            if wrong_time >=2:
                                grid_on = True
                                
                            act_name = None
                            continue
                        elif(Decision=="True"): 
                            break
                else:
                    break

    ################################################################################################

        if "KEYCODE" in act_name:
            detailed_action = "KeyCode: BACK" 
        elif act_name == "text":
            detailed_action = "Type " + res[1]



        if act_name == "tap":
            _, area = res
            tl, br = elem_list[area - 1].bbox
            x, y = (tl[0] + br[0]) // 2, (tl[1] + br[1]) // 2
            ret = controller.tap(x, y)
            if ret == "ERROR":
                print_with_color("ERROR: tap execution failed", "red")
                reset_state()
                raise Exception("tap execution failed")

        elif act_name == "text":
            _, input_str = res
            ret = controller.text(input_str)
            if ret == "ERROR":
                print_with_color("ERROR: text execution failed", "red")
                reset_state()
                raise Exception("text execution failed")

        elif act_name == "long_press":
            _, area = res
            
            tl, br = elem_list[area - 1].bbox
            x, y = (tl[0] + br[0]) // 2, (tl[1] + br[1]) // 2
            ret = controller.long_press(x, y)
            if ret == "ERROR":
                print_with_color("ERROR: long press execution failed", "red")
                reset_state()
                raise Exception("long press execution failed")

        elif act_name == "swipe":
            _, area, swipe_dir, dist = res
            tl, br = elem_list[area - 1].bbox
            x, y = (tl[0] + br[0]) // 2, (tl[1] + br[1]) // 2
            ret = controller.swipe(x, y, swipe_dir, dist)
            if ret == "ERROR":
                print_with_color("ERROR: swipe execution failed", "red")
                reset_state()
                raise Exception("swipe execution failed")

        elif act_name == "grid":
            grid_on = True
        elif act_name == "tap_grid" or act_name == "long_press_grid":
            _, area, subarea = res
            x, y = area_to_xy(area, subarea)
            if act_name == "tap_grid":
                detailed_action = f"Tap on the {subarea} of grid {area}"
                ret = controller.tap(x, y)
                if ret == "ERROR":
                    print_with_color("ERROR: tap execution failed", "red")
                    reset_state()
                    raise Exception("tap execution failed")

            else:
                detailed_action = f"Long press the {subarea} of grid {area}"
                ret = controller.long_press(x, y)
                if ret == "ERROR":
                    print_with_color("ERROR: tap execution failed", "red")
                    reset_state()
                    raise Exception("tap execution failed")

        elif act_name == "swipe_grid":
            _, start_area, start_subarea, end_area, end_subarea = res
            detailed_action = f"swipe from the {start_subarea} of grid {start_area} to the {end_subarea} at {end_subarea}"
            start_x, start_y = area_to_xy(start_area, start_subarea)
            end_x, end_y = area_to_xy(end_area, end_subarea)
            ret = controller.swipe_precise((start_x, start_y), (end_x, end_y))
            if ret == "ERROR":
                print_with_color("ERROR: tap execution failed", "red")
                reset_state()
                raise Exception("tap execution failed")

            
        elif act_name == "KEYCODE":
            ret = controller.back() 
            if ret == "ERROR":
                print_with_color("ERROR: back execution failed", "red")
                reset_state()
                raise Exception("back execution failed")

            
        time.sleep(configs["REQUEST_INTERVAL"])
        if not all_done:
            res=parse_summary_rsp(resp_sum)
            thought=res[0]
            effect=res[1]
            

        else:
            thought = None
            effect= None
    should_stop=orchestrator.after_one_action(act_name)
    if should_stop:
        reset_state()
        raise PlanExecutionError("Terminating the plan because the task is completed.")

    ##################revise the graph and the plan######################

    if "grid" not in act_name and "KEYCODE" not in act_name:
        # pre saves the one before change
        elem_list_pre = elem_list
        if act_name in ["tap", "long_press", "swipe"]:
            elem_pre = elem_list_pre[area-1]
        else:
            elem_pre = None
    else:
        elem_pre = None

    if act_name != "grid":



        # get the screen after the action
        repeated_doc_after = "When you were previously at the same page as the current page (the second image), you have acted on some of the UI elements and have seen their effects. You should pay special attention to these elements to aid you make your plan:" # area, effect
        after_path = controller.get_screenshot(f"{dir_name}_{round_count}_after", task_dir)
        xml_path = controller.get_xml(f"{dir_name}_{round_count}_after", task_dir)

        

        clickable_list = []
        focusable_list = []
        traverse_tree(xml_path, clickable_list, "clickable", True)
        traverse_tree(xml_path, focusable_list, "focusable", True)

        for elem in clickable_list:
            bbox = elem.bbox
            box_areas = (bbox[1][0] - bbox[0][0]) * (bbox[1][1] - bbox[0][1])

            # ignore all elements that are too large (the full screen is 2423520 pixels)
            if box_areas>2423520/4:
                clickable_list.remove(elem)

        elem_list = clickable_list.copy()
        area = 1



        for elem in focusable_list:
            bbox = elem.bbox
            center = (bbox[0][0] + bbox[1][0]) // 2, (bbox[0][1] + bbox[1][1]) // 2
            # the area the box takes up
            box_areas = (bbox[1][0] - bbox[0][0]) * (bbox[1][1] - bbox[0][1])
            
            close = False

            if box_areas>2423520/4:
                close = True
            else:
                for e in clickable_list:
                    bbox = e.bbox
                    center_ = (bbox[0][0] + bbox[1][0]) // 2, (bbox[0][1] + bbox[1][1]) // 2
                    dist = (abs(center[0] - center_[0]) ** 2 + abs(center[1] - center_[1]) ** 2) ** 0.5
                    if dist <= configs["MIN_DIST"]:
                        close = True
                        break
            if not close:
                elem_list.append(elem)
                

                if elem in doc_list:
                    repeated_doc_after += "\nNumerical tag " + str(area) + ": "+ doc_list[elem]
                
                area += 1


        draw_bbox_multi(after_path, os.path.join(task_dir, f"{dir_name}_{round_count}_labeled_after.png"), elem_list,
                        dark_mode=configs["DARK_MODE"])


        after_image = encode_image(os.path.join(task_dir, f"{dir_name}_{round_count}_after.png"))
        before_image = encode_image(os.path.join(task_dir, f"{dir_name}_{round_count}.png"))


        if thought is not None:
            prompt = re.sub(r"<thought>","The thought of your last action:"+ thought, prompts.post_see_template)
            prompt = re.sub(r"<summary>", "Your last action's summary: "+ effect, prompt)
        if "\n" in repeated_doc_after:
            prompt = re.sub(r"<repeated_doc>", repeated_doc_after, prompt)
        else:
            prompt = re.sub(r"<repeated_doc>", "", prompt)
        prompt = re.sub(r"<Vertices>", vertices, prompt)
        prompt = re.sub(r"<Edges>", edges, prompt)
        prompt = re.sub(r"<plan>", plan, prompt)
        prompt = re.sub(r"<previous_vertex>", current_vertex, prompt)
        prompt = re.sub(r"<action>", action, prompt)
        if not detailed_action:
            detailed_action  = act_name
        prompt = re.sub(r"<detailed_action>", detailed_action, prompt)
        prompt = re.sub(r"<task_description>", task_desc, prompt)
        prompt = re.sub(r"<app>", app, prompt)

        if act_history:
            prompt = re.sub(r"<act_history>", "History trajectories:" + act_history, prompt)
        else:
            prompt = re.sub(r"<act_history>", "", prompt)


        
        content = [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{before_image}",
                        "detail": "high",
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{after_image}",
                            "detail": "high"
                        }
                    }
                ]

        print_with_color("Rethinking action and revise...", "yellow")

        rsp = ask_gpt4v(content)
        if "error" not in rsp:
            res = parse_post_see_rsp(rsp)
            previous_vertex = current_vertex
            observation, think, removed_vertices, added_vertices, removed_edges, added_edges, current_vertex, Added_functions, Successful_expected, Ineffective, Revised_plan, remind, effect = res
            current_vertex = current_vertex.replace("\n","")
            act_history+=f"round {round_count}: The action intended to do is: E({previous_vertex}, {action}). The resultant vertex is: {current_vertex}. The observation of the resultant screen is: {observation}. The thought after taking the action is: {think}\n"
            

            Remind_thing = remind
            removed_vertices_list = re.findall(r"Name: (.*?)$", removed_vertices, re.MULTILINE)
            added_vertices_list = re.findall(r"Name: (.*?)$", added_vertices, re.MULTILINE)
            removed_edges_list = re.findall(r"Edge: (.*?)$", removed_edges, re.MULTILINE)
            added_edges_list = re.findall(r"Edge: (.*?)$", added_edges, re.MULTILINE)

            if elem_pre is not None:
                doc_list[elem_pre] = effect

            if Ineffective:
                wrong_information += f"\n{wrong_time}: The action {detailed_action} you have done is not effective. You should think another action to interact with."
                wrong_time+=1
            else:
                wrong_information = "You should specifically focus on the following information, which shows your previous wrong/ineffective actions on this screen. You should choose other elements to interact with or think about other actions to perform:"
                wrong_time = 0
                grid_on = False

            

            
            vertices_list = vertices_list + added_vertices_list
            for vertex in removed_vertices_list:
                try:
                    vertices_list.remove(vertex)
                except:
                    pass
            

            edges_list = edges_list + added_edges_list
            for edge in removed_edges_list:
                try:
                    edges_list.remove(edge)
                except:
                    pass
            
            
            new_vertex = ""
            for vert in vertices_list:
                new_vertex = new_vertex + vert + "\n"
            vertices = new_vertex


            new_edges = ""
            for edge in edges_list:
                new_edges = new_edges + edge + "\n" 
            edges = new_edges

            if "def" in Revised_plan:
                plan = Revised_plan
                plan = plan.strip()
                plan = plan.replace("```python\n", "")
                plan = plan.replace("```python", "")
                plan = plan.replace("```", "")
                plan = plan.replace("```\n", "")

                all_arrow = re.findall(r'->.*?\n', plan)
                for arrow in all_arrow:
                    plan = plan.replace(arrow, "\n")

            log_all_history["graphs"][f"round{round_count+1}"] = {"vertices": vertices, "edges": edges}
            log_all_history["plans"][f"round{round_count+1}"] = plan

            with open(log_file, "w") as f:
                json.dump(log_all_history, f,indent=4)
            
            


            current_vertex = vertex


            round_count += 1



            if round_count > configs["MAX_ROUNDS"]:
                print("terminated due to max rounds")


            if "def" in Revised_plan:
                raise ValueError(plan)



def other_app_function(app_name, task):
    root_dir="./"
    # execute another task in the app, as specified in the plan.
    print("New agent with app name: ", app_name, " and task: ", task)
    try:
        app_name = app_name.replace(" ", "_")
        task = task+', after doing this, go back to the home screen of the phone'
        task = task.replace(" ", "_")
        # create a brand-new agent to execute the task
        os.system(f"python scripts/task_executor.py --app {app_name} --root_dir {root_dir} --task_desc {task}")
        global act_history
        global round_count
        # return the information
        act_history += f"Round {round_count}: Successfully executed the task {task} in the app {app_name}.\n"
        round_count += 1
    except:
        act_history += f"Round {round_count}: The task {task} in the app {app_name} has not been finished, please refine the plan accordingly.\n"
        round_count += 1

def Test_Agent(task,task_name):
    global plan
    global current_vertex
    global dir_name 
    global app
    global task_dir
    global width
    global height
    global log_all_history
    global log_file
    global vertices
    global edges
    global vertices_list
    global edges_list
    global act_history
    global grid_on
    global Remind_thing
    global doc_list
    global wrong_information
    global round_count
    global wrong_time
    
    app=task_name.split("_")[0]
    global task_desc
    task_desc=task
    root_dir="./"
    print("app:",app)
    print("task_desc:",task_desc)
    global configs
    configs = load_config()




    work_dir = os.path.join(root_dir, "tasks") #./tasks
    if not os.path.exists(work_dir):
        os.mkdir(work_dir)

    task_timestamp = int(time.time())
    
    dir_name = datetime.datetime.fromtimestamp(task_timestamp).strftime(f"task_{app}_%Y-%m-%d_%H-%M-%S")
    
    task_dir = os.path.join(work_dir, dir_name)
    os.mkdir(task_dir)
            
    
    width, height = controller.get_device_size()
    if not width and not height:
        print_with_color("ERROR: Invalid device size!", "red")
        reset_state()
        raise Exception("Invalid device size!")

    print_with_color(f"Screen resolution of {device}: {width}x{height}", "yellow")


    task_desc = task_desc.replace("_", " ")
    print_with_color("task description: " + task_desc, "blue")

    last_act = "None"
    task_complete = False
    rows, cols = 0, 0
    # log all plans and graphs at each step
    
    log_all_history = {}
    log_all_history["graphs"] = {}
    log_all_history["plans"] = {}
    
    log_file = os.path.join(task_dir, "log_all_history.json") 
    

    raw_screenshot=controller.get_screenshot(f"raw_screenshot",task_dir)
    raw_image=encode_image(os.path.join(task_dir,f"raw_screenshot.png"))


    had_graph_content=False 
    had_plan_content=False

########################################    creating the initial graph and plan  ######################################## 

    if not had_graph_content:
        print_with_color(f"Creating graph...","yellow")
        prompt=re.sub(r"<task_description>",task_desc,prompts.generate_graph_template)
        prompt = re.sub(r"<App_name>", app, prompt)

        content=prompt
        rsp=ask_gpt4v(content)
        
        vertices,edges=parse_generate_graph(rsp) 

    else:
        vertices,edges=parse_generate_graph(had_graph_content)

    log_all_history["graphs"]["initial"] = {"vertices": vertices, "edges": edges}


    with open(log_file, "w") as f:
        json.dump(log_all_history, f,indent=4)



    vertices_list = re.findall(r"Name: (.*?)$", vertices, re.MULTILINE)
    edges_list = re.findall(r"Edge: (.*?)$", edges, re.MULTILINE)

# merge all edges in edges_list to on string

    new_edges = ""
    for edge in edges_list:
        new_edges = new_edges + edge + "\n" 
    edges = new_edges


### planning



    print_with_color(f"Creating plan...","yellow")


    if not had_plan_content:
        print_with_color("Thinking about the plan...", "yellow")


        prompt=re.sub(r"<Vertices>",vertices,prompts.generate_plan_template)
        prompt=re.sub(r"<Edges>",edges,prompt)
        prompt=re.sub(r"<task_description>",task_desc,prompt)

    # print(prompt)

        content = [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{raw_image}",
                        "detail": "high"
                    }
                }
            ]



        rsp=ask_gpt4v(content)

        if "error" not in rsp:
            rsp=rsp.choices[0].message.content #Current vertex: xxx \n Plan: xxx
        else:
            print_with_color("Invalid response from GPT-4", "red")
            reset_state()
            raise Exception("Invalid response from GPT-4")

    else:
        rsp = had_plan_content


    current_vertex=""
    print(rsp) 
  

    
    _, all_thing = rsp.split("Current vertex:")
    current_vertex, plan = all_thing.split("Plan:")


    current_vertex = current_vertex.strip()
    current_vertex = current_vertex.replace("\n", "")
    
    plan = plan.strip()
    plan = plan.replace("```python\n", "")
    plan = plan.replace("```python", "")
    plan = plan.replace("```", "")
    plan = plan.replace("```\n", "")
    log_all_history["plans"]["initial"] = plan
# save log_all_history to file
    with open(log_file, "w") as f:
        json.dump(log_all_history, f,indent=4)

    print_with_color("Current Vertex: " + current_vertex, "magenta")
    print_with_color("Plan: " + plan, "magenta")

    print_with_color(f"Plan generated","yellow")

    round_count = 1

    
    act_history = ""
    
    grid_on = False
    
    Remind_thing = ""
    task_complete = False
    
    doc_list = {} 
    
    wrong_information = "You should specifically focus on the following information, which shows your previous wrong/ineffective actions on this screen. All numbers shown below should not be chosen anymore!! You should choose other elements to interact with or think about other actions to perform:"
    
    act_plan(plan)


if __name__ == "__main__":
    orchestrator.run(Test_Agent)

    if task_complete:
        print_with_color("Task completed successfully", "yellow")
    elif round_count >= configs["MAX_ROUNDS"]:
        print_with_color("Task finished due to reaching max rounds", "yellow")
    else:
        print_with_color("Task finished unexpectedly", "red")
