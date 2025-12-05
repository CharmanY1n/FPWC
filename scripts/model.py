import re
import requests

from config import load_config
from utils import print_with_color
from openai import OpenAI


configs = load_config()


def ask_gpt4v(content):
    client = OpenAI(api_key=configs['OPENAI_API_KEY'], base_url=configs["OPENAI_API_BASE"])

    count = 0
    while True:
        try:
            response = client.chat.completions.create(
                model=configs["OPENAI_API_MODEL"],

                messages=[
                    {"role": "user", "content": content}],
                max_tokens=configs["MAX_TOKENS"],
                temperature=configs["TEMPERATURE"],

            )
            break
        except:
            count += 1
            if count < 4:
                print_with_color(f"ERROR: Request failed, retrying... {count}", "red")
                continue
            else:
                print_with_color(f"ERROR: Request failed, please check your network and try again.", "red")
                raise Exception("Request failed")

    if "error" not in response:
        usage = response.usage
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        print_with_color(f"Request cost is "
                         f"${'{0:.2f}'.format(prompt_tokens / 1000 * 0.01 + completion_tokens / 1000 * 0.03)}",
                         "yellow")
    return response

def parse_generate_graph(rsp):
    if isinstance(rsp, str):
        msg = rsp
    else:
        msg=rsp.choices[0].message.content
        

    #Vertices: xxx Edges: xxx
    _, contents = msg.split("Vertices:") 
    vertices, edges = contents.split("Edges:")
    edges,_ = edges.split("```")

    print_with_color("Vertices:","yellow")
    print_with_color(vertices,"magenta")
    print_with_color("Edges:","yellow")
    print_with_color(edges,"magenta")
    return [vertices,edges]


def parse_explore_rsp(rsp):
    try:
        msg=rsp.choices[0].message.content
        observation = re.findall(r"Observation: (.*?)$", msg, re.MULTILINE)[0]
        if not observation:
            observation = ""
            print_with_color("ERROR: no observation in the model response!", "red")
        think = re.findall(r"Thought: (.*?)$", msg, re.MULTILINE)[0]
        if not think:
            think = ""
            print_with_color("ERROR: no thought in the model response!", "red")
        act = re.findall(r"Action: (.*?)$", msg, re.MULTILINE)[0]
        if not act:
            act = ""
            print_with_color("ERROR: no action in the model response!", "red")
        last_act = re.findall(r"Summary: (.*?)$", msg, re.MULTILINE)[0]
        if not last_act:
            last_act = ""
            print_with_color("ERROR: no summary in the model response!", "red")
        print_with_color("Observation:", "yellow")
        print_with_color(observation, "magenta")
        print_with_color("Thought:", "yellow")
        print_with_color(think, "magenta")
        print_with_color("Action:", "yellow")
        print_with_color(act, "magenta")
        print_with_color("Summary:", "yellow")
        print_with_color(last_act, "magenta")
        if "FINISH" in act:
            return ["FINISH",last_act]
        act_name = act.split("(")[0]
        if act_name == "tap" or act_name == "`tap":
            act_name = "tap"
            act = act.replace("`tap","tap")
            area = int(re.findall(r"tap\((.*?)\)", act)[0])
            return [act_name, area, last_act]
        elif act_name == "text" or act_name == "`text":
            act_name = "text"
            act = act.replace("`text","text")
            input_str = re.findall(r"text\((.*?)\)", act)[0][1:-1]
            return [act_name, input_str, last_act]
        elif act_name == "long_press" or act_name == "`long_press":
            act_name = "long_press"
            act = act.replace("`long_press","long_press")
            area = int(re.findall(r"long_press\((.*?)\)", act)[0])
            return [act_name, area, last_act]
        elif act_name == "swipe" or act_name == "`swipe":
            act_name = "swipe"
            act = act.replace("`swipe","swipe")
            params = re.findall(r"swipe\((.*?)\)", act)[0]
            area, swipe_dir, dist = params.split(",")
            area = int(area)
            swipe_dir = swipe_dir.strip()[1:-1]
            dist = dist.strip()[1:-1]
            return [act_name, area, swipe_dir, dist, last_act]
        elif act_name == "grid" or act_name == "`grid":
            act_name = "grid"
            return [act_name]
        elif act_name == "KEYCODE" or act_name == "`KEYCODE":
            act_name = "KEYCODE"
            return [act_name, last_act]
        else:
            print_with_color(f"ERROR: Undefined act {act_name}!", "red")
            return ["ERROR"]
    except Exception as e:
        print_with_color(f"ERROR: an exception occurs while parsing the model response: {e}", "red")
        print_with_color(rsp, "red")
        return ["ERROR"]









def parse_grid_rsp(rsp):
    # try:
    msg=rsp.choices[0].message.content
    observation = re.findall(r"Observation: (.*?)$", msg, re.MULTILINE)[0]
    think = re.findall(r"Thought: (.*?)$", msg, re.MULTILINE)[0]
    act = re.findall(r"Action: (.*?)$", msg, re.MULTILINE)[0]
    last_act = re.findall(r"Summary: (.*?)$", msg, re.MULTILINE)[0]
    print_with_color("Observation:", "yellow")
    print_with_color(observation, "magenta")
    print_with_color("Thought:", "yellow")
    print_with_color(think, "magenta")
    print_with_color("Action:", "yellow")
    print_with_color(act, "magenta")
    print_with_color("Summary:", "yellow")
    print_with_color(last_act, "magenta")
    if "FINISH" in act:
        return ["FINISH",last_act]
    act_name = act.split("(")[0]
    if act_name == "tap":
        params = re.findall(r"tap\((.*?)\)", act)[0].split(",")
        area = int(params[0].strip())
        subarea = params[1].strip()[1:-1]
        return [act_name + "_grid", area, subarea, last_act]
    elif act_name == "text":
        input_str = re.findall(r"text\((.*?)\)", act)[0][1:-1]
        return [act_name, input_str, last_act]
    elif act_name == "long_press":
        params = re.findall(r"long_press\((.*?)\)", act)[0].split(",")
        area = int(params[0].strip())
        subarea = params[1].strip()[1:-1]
        return [act_name + "_grid", area, subarea, last_act]
    elif act_name == "swipe":
        params = re.findall(r"swipe\((.*?)\)", act)[0].split(",")
        start_area = int(params[0].strip())
        start_subarea = params[1].strip()[1:-1]
        end_area = int(params[2].strip())
        end_subarea = params[3].strip()[1:-1]
        return [act_name + "_grid", start_area, start_subarea, end_area, end_subarea, last_act]
    elif act_name == "grid":
        return [act_name]
    elif act_name == "KEYCODE":
        return [act_name, last_act]
    else:
        print_with_color(f"ERROR: Undefined act {act_name}!", "red")
        return ["ERROR"]
    # except Exception as e:
    #     print_with_color(f"ERROR: an exception occurs while parsing the model response: {e}", "red")
    #     print_with_color(msg, "red")
    #     return ["ERROR"]




def parse_post_see_rsp(rsp):
    msg=rsp.choices[0].message.content

    observation = msg.split("Observation of the current screenshot:")[1]
    observation,think = observation.split("Thoughts:")
    # code_next = re.findall(r"Next code to be conducted in the original plan:(.*?)$", msg, re.MULTILINE)[0]
    removed_vertices = msg.split("Removed vertices:")[1]
    removed_vertices, added_vertices = removed_vertices.split("Added vertices:")

    added_vertices, removed_edges = added_vertices.split("Removed edges:")
    removed_edges, added_edges = removed_edges.split("Added edges:")
    added_edges, current_vertex = added_edges.split("Current vertex:")
    current_vertex, Added_functions = current_vertex.split("Added functions for other apps:")

    Added_functions, Successful_expected = Added_functions.split("Successful and expected action:")
    Successful_expected, Ineffective = Successful_expected.split("Ineffective:")

    Ineffective, Revised_plan = Ineffective.split("Revised plan:")
    Revised_plan, remind = Revised_plan.split("Remind:")
    remind, effect = remind.split("Impact of the action on the element on the task:")
    #remind, effect = remind.split("Impact of the action on the element on the task:")

    print_with_color("Observation:", "yellow")
    print_with_color(observation, "magenta")
    print_with_color("Thought:", "yellow")
    print_with_color(think, "magenta")
    print_with_color("Removed vertices:", "yellow")
    print_with_color(removed_vertices, "magenta")
    print_with_color("Added vertices:", "yellow")
    print_with_color(added_vertices, "magenta")
    print_with_color("Removed edges:", "yellow")
    print_with_color(removed_edges, "magenta")
    print_with_color("Added edges:", "yellow")
    print_with_color(added_edges, "magenta")
    print_with_color("Current vertex:", "yellow")
    print_with_color(current_vertex, "magenta")
    print_with_color("Added functions for other apps:", "yellow")
    print_with_color(Added_functions, "magenta")
    print_with_color("Successful and expected action:", "yellow")
    print_with_color(Successful_expected, "magenta")
    print_with_color("Ineffective:", "yellow")
    print_with_color(Ineffective, "magenta")
    print_with_color("Revised plan:", "yellow")
    print_with_color(Revised_plan, "magenta")
    print_with_color("Remind:", "yellow")
    print_with_color(remind, "magenta")
    print_with_color("Effect of the action related to the task:", "yellow")
    print_with_color(effect, "magenta")
    if "true" in Ineffective.lower():
        Ineffective = True
    else:
        Ineffective = False
        # print_with_color("Next code to be conducted in the original plan:", "yellow")
        # print_with_color(code_next, "magenta")
        
    return [observation, think, removed_vertices, added_vertices, removed_edges, added_edges, current_vertex, Added_functions, Successful_expected, Ineffective, Revised_plan, remind, effect]



def parse_istrue_rsp(rsp):
    msg=rsp.choices[0].message.content
    observation = re.findall(r"Observation:(.*?)$", msg, re.MULTILINE)[0]
    think = re.findall(r"Thought:(.*?)$", msg, re.MULTILINE)[0]
    if "Zoom in:" in msg:
        zoom_in = re.findall(r"Zoom in:(.*?)$", msg, re.MULTILINE)[0]
    else:
        zoom_in = ""
    if "Answer:" in msg:
        answer = re.findall(r"Answer:(.*?)$", msg, re.MULTILINE)[0]
    else:
        answer = ""
    print_with_color("Observation:", "yellow")
    print_with_color(observation, "magenta")
    print_with_color("Thoughts:", "yellow")
    print_with_color(think, "magenta")
    print_with_color("Zoom in:", "yellow")
    print_with_color(zoom_in, "magenta")
    print_with_color("Answer:", "yellow")
    print_with_color(answer, "magenta")
    return [observation, think, zoom_in, answer]






def parse_summary_rsp(rsp):
    try:
        msg=rsp.choices[0].message.content
        think = re.findall(r"Thought: (.*?)$", msg, re.MULTILINE)[0]
        last_act = re.findall(r"Summary: (.*?)$", msg, re.MULTILINE)[0]
        return [think,last_act]

    except Exception as e:
        print_with_color(f"ERROR: an exception occurs while parsing the model response: {e}", "red")
        print_with_color(rsp, "red")
        return ["ERROR"]



