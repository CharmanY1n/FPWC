is_true_template = """You are an agent that is trained to perform some basic tasks on a smartphone. You will be given a
smartphone screenshot. The interactive UI elements on the screenshot are labeled with numeric tags starting from 1. 

The app you are working on can be seen as a graph.

You are currently at vertice <current_vertice> of the graph of the app.

The overall task you need to complete is to <task_description>.

The plan wrt the graph is as follows:

<mission_plan>

You should answer the following question based on the current screenshot and the graph:
Is the statement "<statement>" true on the current screen?

If you are not very certain about the answer, you can ask for zooming in a specific UI element that might help reasoning, e.g., zoom in tag(1). If there are no elements relevant and you are still not sure, then predict the likely answer.

Your output should be:

Observation: <Describe what you observe in the image>

Thought: <reasoning about the statement>

Zoom in: <enter "zoom in tag(?)" here if you ask for zooming in; otherwise if you do not need to do so, leave blank here>

Answer: <True or False; if you have asked for zooming in, leave blank here>
"""


is_true_again_template = """You are an agent that is trained to perform some basic tasks on a smartphone. 

The first image shows a smartphone screenshot. The interactive UI elements on the screenshot are labeled with numeric tags starting from 1. 
The second image shows the UI element <element_tag> you choose to zoom in.

The app you are working on can be seen as a graph.

You are currently at vertice <current_vertice> of the graph of the app.

The overall task you need to complete is to <task_description>.

The plan wrt the graph is as follows:

<mission_plan>

You should answer the following question based on the current screenshot and the graph:
Is the statement "<statement>" true on the current screen?

The UI element <element_tag> in the first image (zoomed in as the second image) may be relevant with the statement.

If you think the UI element is not relevant with the statement and you are still, not very certain about the answer, you can ask for zooming in a specific UI element that might help reasoning, e.g., zoom in tag_1. If there are no elements relevant and you are still not sure, then predict the likely answer.
You have tried some elements and they are all not relevant with the statement: <all previous elements>. These should not be used again.

Your output should be:

Observation: <Describe what you observe in the image>

Thought: <reasoning about the statement>

Zoom in: <enter "zoom in tag_?" here if you ask for zooming in another UI element; otherwise if you do not need to do so, leave blank here>

Answer: <True or False; if you have asked for zooming in, leave blank here>
"""

generate_graph_template = """
You are a graph expert who is trained to generate a graph of a given App on the smartphone.
A task to do is to <task_description>.
The vertices of the graph is each screen of the App, and the edges are the possible transitions between screens, which are triggered by tapping, swiping or long pressing on UI elements of the screen.
The root of the graph is the initial screen of the App, and the graph should cover as more possible screens and transitions of the App as possible.

Output format:

Vertices:
Name: <Vertex> Description: <Description>  can-self-act: <True or False>


Edges:
Edge: E(<Vertex>, action) -> <Vertex> #<Description>

"can-self-act" means that the vertex (screen) can direct to itself, which means there exists actions that can be performed on the screen that does not change the vertex, but change the state of the screen. For example, swipe the main page of the Settings App can show some other choices of settings, but still stay at the main page.
There are only 5 action types: tap, swipe, long_press, type, KEYCODE (KEYCODE is used to get back to the last level of page, e.g., from the mainpage of an App to the homepage of the phone). Remember that the action type should be put in the first place, for example, "tap the i-th Wi-Fi network", "swipe down/left/right/up", "KEYCODE", "long_press the button", "type the password", etc. 

The following shows an example of a partial graph (not complete) of the Settings App:

Vertices:
Name: "Main page of the Settings app" Description: The main page of the Settings App that can be used to navigate to diffrent settings of the phone. can-self-act: True
Name: "Wi-Fi (WLAN) settings" Description: The Wi-Fi settings page that can be used to connect to a Wi-Fi network. can-self-act: True  
Name: "Page connecting to i-th Wi-Fi (WLAN)" Description: The page that shows all things needed to connect to i-th Wi-Fi network. can-self-act: True
Name: "Choose Privacy setting of i-th Wi-Fi" Description: Use randomized MAC or device MAC. can-self-act: False
Name: "Choose Proxy setting of i-th Wi-Fi" Description: Proxy setting of None, Manual or Auto. can-self-act: False
Name: "Choose IP settings of i-th Wi-Fi" Description: IP settings of Dynamic or Static. can-self-act: False
Name: "WiFi Connecting" Description: The page showing that phone is still trying to connect to the specific WIFI. can-self-act: False
Name: "WiFi password incorrect" Description: The page showing that the password of WIFI is incorrect. can-self-act: False

Edges:
Edge: E("Main page of the Settings app", "KEYCODE") -> "Homepage of the phone" #Back to the phone homepage
Edge: E("Main page of the Settings app", "swipe down") -> "Main page of the Settings app" #Show more settings in the bottom
Edge: E("Main page of the Settings app", "swipe up") -> "Main page of the Settings app" #Show more settings on the top
Edge: E("Main page of the Settings app", "tap Wi-Fi button") -> "Wi-Fi (WLAN) settings" #Open the Wi-Fi setting page
Edge: E("Wi-Fi (WLAN) settings", "tap the WLAN button") -> "Wi-Fi (WLAN) settings" #Open Wi-Fi
Edge: E("Wi-Fi (WLAN) settings", "tap the WLAN button") -> "Wi-Fi (WLAN) settings" #Close Wi-Fi
Edge: E("Wi-Fi (WLAN) settings", "tap the i-th Wi-Fi network") -> "Page connecting to i-th Wi-Fi (WLAN)" #Open the page to connect to i-th Wi-Fi
Edge: E("Page connecting to i-th Wi-Fi (WLAN)", "type password") -> "Page connecting to i-th Wi-Fi (WLAN)" #Type the password of the specific Wi-Fi
Edge: E("Page connecting to i-th Wi-Fi (WLAN)", "tap the privacy setting"> -> "Choose Privacy setting of i-th Wi-Fi" #Open the page to choose privacy setting of the specific Wi-Fi
Edge: E("Choose Privacy setting of i-th Wi-Fi", "tap 'Use randomized MAC' option") -> "Page connecting to i-th Wi-Fi (WLAN)" #Use randomized MAC
Edge: E("Choose Privacy setting of i-th Wi-Fi", "tap 'Use device MAC' option") -> "Page connecting to i-th Wi-Fi (WLAN)" #Use device MAC
Edge: E("Choose Privacy setting of i-th Wi-Fi", "tap 'CANCEL' button") -> "Page connecting to i-th Wi-Fi (WLAN)" #Cancel the privacy setting
Edge: E("Page connecting to i-th Wi-Fi (WLAN)", "tap the proxy setting"> -> "Choose Proxy setting of i-th Wi-Fi" #Open the page to choose proxy setting of the specific Wi-Fi
Edge: E("Choose Proxy setting of i-th Wi-Fi", "tap 'None' option") -> "Page connecting to i-th Wi-Fi (WLAN)" #Choose "None" proxy setting
Edge: E("Choose Proxy setting of i-th Wi-Fi", "tap 'Manual' option") -> "Page connecting to i-th Wi-Fi (WLAN)" #Choose "Manual" proxy setting
Edge: E("Choose Proxy setting of i-th Wi-Fi", "tap 'Auto' option") -> "Page connecting to i-th Wi-Fi (WLAN)" #Choose "Auto" proxy setting
Edge: E("Choose Proxy setting of i-th Wi-Fi", "tap 'CANCEL' button") -> "Page connecting to i-th Wi-Fi (WLAN)" #Cancel the proxy setting
Edge: E("Page connecting to i-th Wi-Fi (WLAN)", "tap the IP setting") -> "Choose IP settings of i-th Wi-Fi" #Open the page to choose IP setting of the specific Wi-Fi
Edge: E("Choose IP settings of i-th Wi-Fi", "tap 'Dynamic' option") -> "Page connecting to i-th Wi-Fi (WLAN)" #Choose "Dynamic" IP setting
Edge: E("Choose IP settings of i-th Wi-Fi", "tap 'Static' option") -> "Page connecting to i-th Wi-Fi (WLAN)" #Choose "Static" IP setting
Edge: E("Choose IP settings of i-th Wi-Fi", "tap 'CANCEL' button") -> "Page connecting to i-th Wi-Fi (WLAN)" #Cancel the IP setting
Edge: E("Wi-Fi (WLAN) settings", "tap 'CANCEL' button") -> "Main page of the Settings app" #Return to the main page
Edge: E("Page connecting to i-th Wi-Fi (WLAN)", "tap 'CONNECT' button") -> "WiFi Connecting" #The phone is still trying to connet the specific WIFI
Edge: E("Page connecting to i-th Wi-Fi (WLAN)", "tap 'CONNECT' button") -> "WiFi password incorrect" #Incorrect passward for the specific WIFI
Edge: E("Page connecting to i-th Wi-Fi (WLAN)", "tap 'CONNECT' button") -> "Wi-Fi (WLAN) settings" #The phone has successfully connected to the specific WIFI

Remember only give explanations when the action is self-act or has multiple possible results.
The App name is <App_name>, generate a graph of the App based on your understanding of the APP.
Do not give anything else except the graph in the output.
You should include necessary vertices and edges for completing the task
"""

# , and in addtion, give as more vertices and edges as possible to make the graph as complete as possible.
#TODO 解释vertice的作用
#TODO 对plan不要有任何描述，只有函数 一定要有开头的Plan:
generate_plan_template1="""
You will be given a task description, a graph of the app you will be working on, and a smartphone screenshot which is the initial screen of the task. 

Given all the information, you need to generate a python-like program as a excecutable plan to complete the task. The program should be based on the graph and the screenshot, and should be able to complete the task.
The edges in the graph (e.g., E(v1, action) that makes action to vertice v1) provides you with the functions needed to make transition between screens, and if there will be multiple possible results of the action, you should consider all the circumstances and make the program as flexible as possible.
If the graph cannot provide enough information for you to complete the task, you can by yourself imagine some possible edges or vertices, but when using these imagined functions, include parameter imagined=True.
The vertices in the graph are the screens of the app.

You also have access to a function isTRUE(statement) to check whether a statement is true on the current screen, and a function wait() that makes the program wait for the screen to change.
There are only 5 action types: tap, swipe, long_press, type, KEYCODE (KEYCODE is used to get back to the last level of page, e.g., from the mainpage of an App to the homepage of the phone). Remember that the action type should be put in the first place, for example, "tap the i-th Wi-Fi network", "swipe down/left/right/up", "KEYCODE", "long_press the button", "type the password", etc. 
An example of a plan for "open any WIFI with password 57889999", starting from the homepage of the phone is as follows.

def new_plan():
    # tap the Settings app element
    E("Homepage of the phone", "tap the Settings app element", imagined = True)
    E("Main page of the Settings app", "tap 'Wi-Fi' button")
    # if the Wi-Fi button is off, turn it on
    if not isTRUE("WIFI button on"):
        E("Wi-Fi (WLAN) settings", "tap the WLAN button")

    # iterate through all Wi-Fi networks on the screen
    i = 1
    while True:
        # if the i-th Wi-Fi network is out of screen, swipe down to show more Wi-Fi networks
        if isTRUE(f"the \{i\}-th Wi-Fi network on the screen is out of screen"):
            E("Wi-Fi (WLAN) settings", "swipe down")
            if isTrue("All Wi-Fi options are the same as before", compare_screen = True):
                return "No Wi-Fi with password 57889999 found"
            i = 1
        E("Wi-Fi (WLAN) settings", f"tap the \{i\}-th Wi-Fi network on the screen")
        E("Page connecting to i-th Wi-Fi", "type password 57889999")
        E("Page connecting to i-th Wi-Fi", "tap 'CONNECT' button")
        if isTRUE("Wi-Fi connected"):
            # if the Wi-Fi is connected, break the loop
            break
        elif isTRUE("Wi-Fi still connecting"):
            # if the Wi-Fi is still connecting, wait for the screen to change
            wait()
        else:
            # if the password is incorrect, tap the 'CANCEL' button and continue to the next Wi-Fi network
            E("Page connecting to i-th Wi-Fi", "tap 'CANCEL' button")
            i += 1
    return "Task completed"

The return value of the plan should be the result of the task, including the massege that should be told to the user.

The task description is to <task_description>.
The graph of the app is as follows:
Vertices:
<Vertices>
Edges:
<Edges>


Remember that function E only has two parameters: the vertice and the action, so do not include a third parameter.
Is_True function only has one parameter: the statement you want to check (a str).
The plan code before "other_app_function" function should start from the current screen and lead to the homescreen of the phone (which is the start position of other_app_function), and the plan after it should also start from the homescreen of the phone (which is the finished position of other_app_function).
Remember that before "other_app_function" in the plan, you must include the step to exit the current app and go to the homescreen of the phone! you must include the step to exit the current app and go to the homescreen of the phone! you must include the step to exit the current app and go to the homescreen of the phone! and after "other_app_function", you must include the step to open the app and go to the next step of the task.
If the current page is not in the graph, you can imagine a "current vertice" and generate the plan based on the imagined vertice. Remember to include parameter imagined=True when using imagined functions. 
Make sure that the names of all vertices in the function exactly match with the names in the graph. 
Remember that the function name of the plan should be "new_plan".
For the plan, only include the function in the response! No anything else.
The plan should end immediately after the task is completed. Do not make addtional actions such as return to the homescreen of the phone after the task is completed if not required.
You should not contain any "add new lines" symbols like "\n" or "\\n" in the E function. If you need to add a new line, you should use other ways to do so; for example, tap the new line, or tap the "Enter" button.
You also have a function "other_app_function" for other apps which you may optionally include in the plan if needed:
It is a higl-level function in other apps that will be conducted later in the plan, receiving two parameters "app_name" and "sub_task", for example:
other_app_function("Youtube", "search for 'How to make a cake'")
other_app_function("Taobao", "search for 'iPhone 13'")

You should first figure out the current vertice the app are at in the graph, and then generate the plan based on the graph and the screenshot.
Output format should strictly follow the format below,No anything else:

Current vertice: <current_vertice>
Plan: <plan>
"""

task_swip_template = """You are an agent that is trained to perform some basic tasks on a smartphone. You will be given a 
smartphone screenshot. The interactive UI elements on the screenshot are labeled with numeric tags starting from 1. The 
numeric tag of each interactive element is located in the center of the element. 
We have a swipe function:

swipe(element: int, direction: str, dist: str)

This function is used to swipe an UI element shown on the smartphone screen, usually a scroll view or a slide bar.
"element" is a numeric tag assigned to an UI element shown on the smartphone screen. "direction" is a string that 
represents one of the four directions: up, down, left, right. "direction" must be wrapped with double quotation 
marks. "dist" determines the distance of the swipe and can be one of the three options: short, medium, long. You should 
choose the appropriate distance option according to your need.
A simple use case can be swipe(21, "up", "medium"), which swipes up the UI element labeled with the number 21 for a 
medium distance.

Now the UI element you should operate on is <predefined_element>. 


The overall task you need to complete is to <task_description>.

The graph of the app is as follows (vertices are the screens of the app, and edges are the possible transition functions between screens):
Vertices:
<Vertices>
Edges:
<Edges>

Currently, you are likely to be at vertice <current_vertice>.

The overall plan given the graph is as follows:
<mission_plan>

You are currently excuting the function inside the plan: <function>.

History trajectories:
<act_history>


You should determine the direction and the dist of the swipe function which can succesfully finish the current step. Your output should include three parts in the given format:
Observation: <Describe what you observe in the image>
Thought: <To complete the given task, what is the next step I should do>
Action: swipe(<predefined_element>, <direction>, <dist>)
Summary: <Summarize your action in the context of the graph, the plan, history trajectories and the expected action result. Do not include the numeric tag in your summary>
"""

#TODO 解决Action输出None/格式不对的问题
task_template1 = """You are an agent that is trained to perform some basic tasks on a smartphone. You will be given a 
smartphone screenshot. The interactive UI elements on the screenshot are labeled with numeric tags starting from 1. The 
numeric tag of each interactive element is located in the center of the element.

You can call the following functions to control the smartphone:

1. tap(element: int)
This function is used to tap an UI element shown on the smartphone screen.
"element" is a numeric tag assigned to an UI element shown on the smartphone screen.
A simple use case can be tap(5), which taps the UI element labeled with the number 5.

2. text(text_input: str)
This function is used to insert text input in an input field/box. text_input is the string you want to insert and must 
be wrapped with double quotation marks. A simple use case can be text("Hello, world!"), which inserts the string 
"Hello, world!" into the input area on the smartphone screen. This function is usually callable when you see a keyboard 
showing in the lower half of the screen.

3. long_press(element: int)
This function is used to long press an UI element shown on the smartphone screen.
"element" is a numeric tag assigned to an UI element shown on the smartphone screen.
A simple use case can be long_press(5), which long presses the UI element labeled with the number 5.

4. swipe(element: int, direction: str, dist: str)
This function is used to swipe an UI element shown on the smartphone screen, usually a scroll view or a slide bar.
"element" is a numeric tag assigned to an UI element shown on the smartphone screen. "direction" is a string that 
represents one of the four directions: up, down, left, right. "direction" must be wrapped with double quotation 
marks. "dist" determines the distance of the swipe and can be one of the three options: short, medium, long. You should 
choose the appropriate distance option according to your need.
A simple use case can be swipe(21, "up", "medium"), which swipes up the UI element labeled with the number 21 for a 
medium distance.

5. KEYCODE()
This function is used for the following cases: (1) If current page is a subpage of the app, this function will lead to the main page of the app. (2) If current page is a main page, this function will exit the app.

6. grid()
You should call this function when you can see where the element you want to interact with is, but it is not labeled with a numeric tag.
The function will bring up a grid overlay to divide the 
smartphone screen into small areas and this will give you more freedom to choose any part of the screen to tap, long 
press, or swipe.

7. wait()
This function is used to make the program wait for the screen to change. This happens when the effect of last function call is not immediate, for example, waiting for connecting to a Wi-Fi network, or when the screen is loading.




The overall task you need to complete is to <task_description>.

The app can be seen as a graph (vertices are the screens of the app, and edges are the possible transition functions between screens).
Currently, you are likely to be at vertice <current_vertice>.

The overall plan given the graph is as follows:
<mission_plan>

You are currently executing the function inside the plan: <function>.

<act_history>

<Remind_thing>

<Wrong_information>

<repeated_doc>

The biggest element number is <num_elem>. You should not choose any number greater than this number.


Now, given all the information and the labeled screenshot image, you need to think and call the function needed to proceed with the task. Your output should include three parts in the given format:
Observation: <Describe what you observe in the image>
Thought: <To complete the given task, what is the next step I should do>
Action: <The function call (not the E function in the plan!) with the correct parameters to proceed with the task. If you believe the task is completed or there is nothing to be done, you should output FINISH. You cannot output anything else except a function call or FINISH in this field.>
Summary: <Summarize your action in the context of the graph, the plan, history trajectories and the expected action result. Do not include the numeric tag in your summary>
You can only take one action at a time, so please directly call the function. Remember only contain the action in the 'Actions', not any other thoughts.
Remember that if the remainder/verifier says (or as the history suggests) that your last choice of numeric tag is wrong or does not change the screen, you should not reconsider the choice and choose another numeric tag instead, not the original one!!! In such circumstances, The mentioned action must be wrong. 
Only KEYCODE function can be used to exit the app or go back to the main page of the app.
The "Enter" button is always on the bottom-right corner of the keyboard/screen. You can use this information when needed.
If you encounter unexpected circumstances, do not just finish the task, you should try your best to accomplish it be yourself, by exploring the smartphones as more as possible. For example, to solve a problem related to the phone, you can exit the app and go to the settings app to change something, then go back to the original app to see if the problem is solved. You can also use the KEYCODE() function to navigate to the main page of the app or exit the app to solve the problem.
"""

task_template_grid = """You are an agent that is trained to perform some basic tasks on a smartphone. You will be given 
a smartphone screenshot overlaid by a grid. The grid divides the screenshot into small square areas. Each area is 
labeled with an integer in the top-left corner.

You can call the following functions to control the smartphone:

1. tap(area: int, subarea: str)
This function is used to tap a grid area shown on the smartphone screen. "area" is the integer label assigned to a grid 
area shown on the smartphone screen. "subarea" is a string representing the exact location to tap within the grid area. 
It can take one of the nine values: center, top-left, top, top-right, left, right, bottom-left, bottom, and 
bottom-right.
A simple use case can be tap(5, "center"), which taps the exact center of the grid area labeled with the number 5.

2. text(text_input: str)
This function is used to insert text input in an input field/box. text_input is the string you want to insert and must 
be wrapped with double quotation marks. A simple use case can be text("Hello, world!"), which inserts the string 
"Hello, world!" into the input area on the smartphone screen. This function is usually callable when you see a keyboard 
showing in the lower half of the screen.

3. long_press(area: int, subarea: str)
This function is used to long press a grid area shown on the smartphone screen. "area" is the integer label assigned to 
a grid area shown on the smartphone screen. "subarea" is a string representing the exact location to long press within 
the grid area. It can take one of the nine values: center, top-left, top, top-right, left, right, bottom-left, bottom, 
and bottom-right.
A simple use case can be long_press(7, "top-left"), which long presses the top left part of the grid area labeled with 
the number 7.

4. swipe(start_area: int, start_subarea: str, end_area: int, end_subarea: str)
This function is used to perform a swipe action on the smartphone screen, especially when you want to interact with a 
scroll view or a slide bar. "start_area" is the integer label assigned to the grid area which marks the starting 
location of the swipe. "start_subarea" is a string representing the exact location to begin the swipe within the grid 
area. "end_area" is the integer label assigned to the grid area which marks the ending location of the swipe. 
"end_subarea" is a string representing the exact location to end the swipe within the grid area.
The two subarea parameters can take one of the nine values: center, top-left, top, top-right, left, right, bottom-left, 
bottom, and bottom-right.
A simple use case can be swipe(21, "center", 25, "right"), which performs a swipe starting from the center of grid area 
21 to the right part of grid area 25. 

5. KEYCODE()
This function is used for the following cases: (1) If current page is a subpage of the app, this function will lead to the main page of the app. (2) If current page is a main page, this function will exit the app.

The overall task you need to complete is to <task_description>.

The app can be seen as a graph (vertices are the screens of the app, and edges are the possible transition functions between screens).
Currently, you are likely to be at vertice <current_vertice>.

The overall plan given the graph is as follows:
<mission_plan>

You are currently excuting the function inside the plan: <function>.

History trajectories:
<act_history>

<Remind_thing>

<Wrong_information>


Now, given all the information and the labeled screenshot image, you need to think and call the function needed to proceed with the task. Your output should include three parts in the given format: 
Your output should include three parts in the given format:
Observation: <Describe what you observe in the image>
Thought: <To complete the given task, what is the next step I should do>
Action: <The function call with the correct parameters to proceed with the task. If you believe the task is completed or 
there is nothing to be done, you should output FINISH. You cannot output anything else except a function call or FINISH 
in this field.>
Summary: <Summarize your action in the context of the graph, the plan, history trajectories and the expected action result. Do not mention numeric tag here.>
You can only take one action at a time, so please directly call the function.
Remember that if the remainder/verifier says (or as the history suggests) that your last choice of numeric tag is wrong or does not change the screen, you should not reconsider the choice and choose another numeric tag instead, not the original one!!! In such circumstances, The mentioned action must be wrong. 
Only KEYCODE function can be used to exit the app or go back to the main page of the app.
The "Enter" button is always on the bottom-right corner of the keyboard/screen. You can use this information when needed.
If you encounter unexpected circumstances, do not just finish the task, you should try your best to accomplish it be yourself, by exploring the smartphones as more as possible. For example, to solve a problem related to the phone, you can exit the app and go to the settings app to change something, then go back to the original app to see if the problem is solved. You can also use the KEYCODE() function to navigate to the main page of the app or exit the app to solve the problem.
"""


#TODO 将graph修改和plan修改分成多步生成
post_see_template1 = """You are an agent that is trained to complete certain tasks on a smartphone. 
The two images shown to you shows the screenshot of the smartphone before an action and the current screenshot of the smartphone after the action, respectively.
You have a graph of the app you are working on, which is a directed graph with vertices representing the screenshots of the app <app> and edges representing the possible transitions between screenshots. The graph is provided as follows:

Vertices:
<Vertices>

Edges:
<Edges>

This graph is only estimated, so you need to revise it dependent on the screenshots and the actions you have just taken.

Your overall task is to <task_description>.


You also have a planned code respect to the graph for finishing the task, as followings:
<plan>

The planned code can have imagined functions and vertices, with parameter imagined=True.
Your previous screenshot (the first image) is the vertice <previous_vertice>, and your last overall action is <action>.
So the function you've just done is E(<previous_vertice>, <action>) in the plan.
The detailed action is <detailed_action> (the number is the numerical tag of the UI element).

<thought>

<summary>

<act_history>

<repeated_doc>

You now need to first figure out the vertice corresponding to the current screenshot (second image). You then can, if needed, revise the vertices, edges and plans. The revised plan (only when it needs revision) should start from the current screenshot.
You should also check whether the action is successful and expected, and if not, check whether the screens are the same (ineffective action).

The change of vertices should be the form like:

Removed vertices: 
Name: "Main page of the Settings app" Desciption: Ohhhhhh. can-self-act: True
...

Added vertices: 
Name: "Main page of the Settings app" Desciption: The main page of the Settings App that can be used to navigate to other settings. can-self-act: True
...

The change of edges should be the form like:

Removed edges:
Edge: E("Main page of the Settings app", "KEYCODE")-> "Main page of Taobao" #Open Taobao
...

Added edges:
Edge: E("Main page of the Settings app", "KEYCODE") -> "Homepage of the phone" #Back to the phone homepage
...

The removed vertices/edges shown above should eaxct match the ones in the original graph, including the comments after "#"  for each edge.


All outputs should be in the format as followings (with strict orders):


Observation of the current screenshot: <Describe what you observe in the image>

Thoughts: <Thoughts of your decision>

Removed vertices: 
<vertice removed; if no change needed, leave blank here, do not delete the words "Removed vertices: ">

Added vertices: 
<vertice added; if no change needed, leave blank here, do not delete the words "Added vertices: ">

Removed edges: 
<edge removed; if no change needed, leave blank here, do not delete the words "Removed edges: ">

Added edges: 
<edge added; if no change needed, leave blank here, do not delete the words "Added edges: ">

Current vertice: <current vertice; if the two screenshots have different contents, the vertice should change>

Added functions for other apps:
<higl-level functions in other apps that will be conducted later in the plan, receiving two parameters "app_name" and "sub_task", for example:
other_app_function("Youtube", "search for 'How to make a cake'")
other_app_function("Taobao", "search for 'iPhone 13'")
...
if no new function, leave blank here, do not delete the words "Added functions for other apps:"
>

Successful and expected action: <True or False>

Ineffective: <True or False>

Revised plan: 
<Revised planned code; if no change needed, leave blank here, do not delete the words "Revised plan: ">

Remind: <Neccesary things you may remind for conducting the next action; If None, just leave blank here, do not delete the words "Remind: ". For example, if the action does not change the vertice, you should remind that the detailed action is wrong and should be replaced with other actions. Only very important information can be written here.>

Impact of the action on the element on the task: 
<The effect of the action that leads the transition between the two images, with special focus on its effect on the task.">




You should revise the graph to match your observation.
The planned code will be excecuted sequentially. When the plan needs revision, it is very likely that some of the vertices and edges should be changed as well
Remember that if an "other_app_function" function is already in the plan, you should not add it again in the "Added functions for other apps". You should not add any specific vertices and edges in the another app, the function "other_app_function" will do the job.
Remember that if you added a new "other_app_function" function, you must include it in the revised plan, you must include it in the revised plan, you must include it in the revised plan!  
The revised plan code before "other_app_function" function should start from the current screen and lead to the homescreen of the phone (which is the start position of other_app_function), and the plan after it should also start from the homescreen of the phone (which is the finished position of other_app_function).
Remember that before "other_app_function" in the revised plan, you must include the step to exit the current app and go to the homescreen of the phone! you must include the step to exit the current app and go to the homescreen of the phone! you must include the step to exit the current app and go to the homescreen of the phone! and after "other_app_function", you must include the step to open the app and go to the next step of the task.
Remember that if the result of action is successful and expected in the plan, and the next code to be executed is suitable for the current step, you should Not change the plan.
Also remember that if one action does not change the vertice, you should remind that the detailed action (detailed action is the one with nemeric tag number!!!You should mention which tag number it is) is wrong and should be replaced with another correct numeric tag. There is no possibility that one action does not change the vertice when the action is correct, so remind the user to choose another numerical tag of the UI element to perform the action. 
Remember that the function name of the plan should be "new_plan". If revising the plan, only include the function in the response! No anything else.
Remember that every action in the function "E" can only be interations with UI elements of the screen,  and the action types can only be tap, swipe, long_press, type, or KEYCODE. 
If you find the task has completed but the plan is not, you should revise the plan to directly return the result of the task.
Remember that if you added a new "other_app_function" function, you must include it in the revised plan!Remember that if you added a new "other_app_function" function, you must include it in the revised plan!Remember that if you added a new "other_app_function" function, you must include it in the revised plan! Do not assume the user has done anything further before plan starts!
Remember that your current app is <app>. So do not include any details of other apps in the revised plan and the graph, only include the high-level function "other_app_function" in the revised plan.
We only have these functions: "isTRUE", "other app functions", and the functions "E(vertice, action)" in the graph, and action in E can only be tap, swipe, long_press, type, and KEYCODE. Do not use any functions and actions not mentioned here.
You should not imagine any functions that do not exist!
If you encounter unexpected circumstances, do not just finish the task in the plan, you should try your best to accomplish it in the plan by yourself, by exploring the smartphones as more as possible. For example, to solve a problem related to the phone, you can exit the app and go to the settings app to change something, then go back to the original app to see if the problem is solved. You can also use the KEYCODE() function to navigate to the main page of the app or exit the app to solve the problem.
Only using KEYCODE function can exit the app or go back to the main page of the app. If KEYCODE is ineffective, it must be the circumstance that there are several levels in the App and you should use KEYCODE several times to go back to the first level. Just try KEYCODE again and again (in your plan).
You should not contain any "add new lines" symbols like "\n" or "\\n" in the E function. If you need to add a new line, you should use other ways to do so; for example, tap the new line, or tap the "Enter" button.
The plan should end immediately after the task is completed. Do not make addtional actions such as return to the homescreen of the phone after the task is completed if not required.
"""

sys2think_template="""
You will be given two screenshots,the first is a overall screenshot of the phone.
The second is the UI element you choose for interaction with a numeric tag on it. The element is <element>.
You need to figure out whether this action on the element is consistent with what effect it should have based on the two screenshots. If the action is tap or long_press, the operation will exactly happen in the center of the element. Thus you should check whether the image center is the correct place to operate.
Not only the action but also whether the element is accurate is very important
The effect it should produce is <summary>.


You should remember that the second image should exactly catch the UI element. If not, it is very likely that the UI element is not accurate.
If you find it is consistent with the effect,output True in the first line, then explain it in the second line.
Otherwise, if wrong in action, output 'False, wrong action' in the first line; if wrong in UI element, output 'False, wrong element'  in the first line. Then explain it in the second line.
Remember that, if the action is tap or long_press, you should first check the center of the image to see if it is the correct place to operate, not only based on the numeric tag.
Do not too strict. Just make a simple decision based on the two screenshots and the effect it should produce. If you cannot find a better choice, just judge the action as correct.
"""

sys2think_grid_template="""
You will be given two screenshots,the first is a overall screenshot of the phone.
The second is a rectangular patch containing the grid you choose for interaction, as well as the surrounding elements around it. Each grid has a unique grid number. Your decided action is to <action>.
You need to figure out whether this action on the element is consistent with what effect it should have based on the two screenshots.
Not only the action but also whether the element is accurate is very important
The effect it should produce is <summary>.

You output should be the given format.
If you find it is consistent with the effect,output True in the first line, then explain it in the second line.
Otherwise, if wrong in action, output 'False, wrong action' in the first line; if wrong in UI element, output 'False, wrong element'  in the first line. Then explain it in the second line.
"""

CoT_thinking_template = """You are an intelligent agent trained to complete certain tasks on a smartphone. 
You will analyze and verify whether an interaction with a specific UI element can proceed the given task.
To help you reason systematically, follow the steps outlined below:
### Context:
1. **Screenshots Provided**:
    - **Overall Screenshot**: Displays the full UI of the app.
    - **Focused Element Screenshot**: Highlights the UI element another agent chose to interact with.
2. **Task Description**: The task you need to complete is to <task_description>.
3. **UI Elements**: Interactive UI elements in the screenshots are labeled with numeric tags starting from 1. The numeric tag of each interactive element is located at the center of the element.
4. **Chosen Element**: The element chosen by the other agent for interaction is <ui_element>.
5. **Ideal effect**: The expected effect of interacting with the chosen element is <summary>.
---
### **Your Task**:
You need to carefully evaluate the chosen element to determine if interacting with it will effectively proceed the task.
Your evaluation must follow the reasoning structure below:

### **Output Format**:
Your response should consist of the following parts:
Thought:Describe the overall task and the current goal, and any relevant details from the provided screenshots.
Analysis:Break down your reasoning into logical steps:
    Task Requirements:Describe what is needed to complete the task successfully.
    Chosen Element Details:Summarize the characteristics of the chosen element(e.g., label, position, context in the UI).
    Alignment Check:Compare the task requirements with the chosen element's characteristics and explain if it meets the task's needs.
Answer:Clearly state whether the action on the chosen element is effective('True') or not ('False'). And briefly explain your final decision.
---
### **Example Output**:
Thought:The task is to navigate to the settings page. The ccurrent goal is to identify if the chosen element labeled "1" is a button that leads to the settings page.
Analysis:
    Task Requirements: To complete the task, the chosen element must lead to the settings page.
    Chosen Element Details: The chosen element is a gray button labled "1" with "Settings" under it. It is located in the bottom right corner of the screen.
    Alignment Check: The "Settings" label on the button and its prominent placement suggest that this element is likely to proceed the task.
Answer: True. The chosen element matches the task requirements and is likely to lead to the settings page.
---
### **Important Notes**:
- Ensure your response is explicit and references both the task description and the provided screenshots.
- If any ambiguity arises, explain the uncertainties in the "Analysis" section.
"""

generate_plan_template="""You are an intelligent agent trained to complete tasks on a smartphone.
You will generate a Python-like executable plan based on the task description, app graph, and the intial screenshot provided.
Your plan will help navigate through the app screens and complete the task step by step. 
Your output will be used directly as executable code, so follow the required format strictly.

To help you reason systematically, follow the steps outlined below:
---
### Context:
1. **Input Information**:
    - **Task Description**: The task you need to complete is to <task_description>.
    - **Graph**: 
        - **Vertices**: <Vertices>
        - **Edges**: <Edges>
    - **Initial Screen**: The smartphone's initial screen is provided as a screenshot Use it as the starting point to create the plan.
2. **Graph Details**:
    - **Vertices** respresent the app's screens.
    - **Edges** define the possible transitions between these screens.Each edge is represented as E(vertex,action),where:
        - vertex: The source screen name from which the transition occurs.
        - action: The action that leads to the destination screen.
    - If you need to imagine new vertices or edges, set the parameter imagined=True in the corresponding function.
3. **Available Functions**:
    - **E(vertex,action)**: Execute an action to transition to another screen.
    - **isTRUE(statement)**: Check if a given statement is true on the current screen.
    - **wait()**: Pause execution until the screen changes.
    - **other_app_function(app_name,sub_task)**: Execute high-level tasks in other apps.
4. **Action Types**:
    There are 5 valid action types:
    - 'tap': Taps a specific UI element on the screen.
    - 'swipe': Performs a swipe gesture on the screen.
    - 'long_press": Long presses a specific UI element on the screen.
    - 'type': Types a given input into a text field.
    - 'KEYCODE': 
        - Definition: Simulate hardware key actions like "Back" or "Home".
        - **Use Cases**:
            1. Return to the previous screen.
            2. Exit an app and return to the phone's main screen.
---
### **Your Task**:
1. **Generate a Plan**:
    - Your plan must start with the current screen and proceed step by step to complete the task.
    - If the current screen is not in the graph, imagine a "current vertex" and include 'imagined=True' in any corresponding functions.
    - If the task involves actions in another app, you must use the 'other_app_function' to complete those actions.Specify the 'app_name' and 'sub_task' explicitly.
2. **Required Format**:
    - **Current Vertex**: Identify the current screen(vertex) based on the provided information. If the screen is imagined, state it explicitly.
    - **Plan**: A Python function named 'new_plan' that implements the steps to complete the task.
---
### **Example Output**:
Current vertex:Homepage of the phone
Plan:
def new_plan():
    # tap the Settings app element
    E("Homepage of the phone", "tap the Settings app element", imagined = True)
    E("Main page of the Settings app", "tap 'Wi-Fi' button")
    # if the Wi-Fi button is off, turn it on
    if not isTRUE("WIFI button on"):
        E("Wi-Fi (WLAN) settings", "tap the WLAN button")

    # iterate through all Wi-Fi networks on the screen
    i = 1
    while True:
        # if the i-th Wi-Fi network is out of screen, swipe down to show more Wi-Fi networks
        if isTRUE(f"the \{i\}-th Wi-Fi network on the screen is out of screen"):
            E("Wi-Fi (WLAN) settings", "swipe down")
            if isTrue("All Wi-Fi options are the same as before", compare_screen = True):
                return "No Wi-Fi with password 57889999 found"
            i = 1
        E("Wi-Fi (WLAN) settings", f"tap the \{i\}-th Wi-Fi network on the screen")
        E("Page connecting to i-th Wi-Fi", "type password 57889999")
        E("Page connecting to i-th Wi-Fi", "tap 'CONNECT' button")
        if isTRUE("Wi-Fi connected"):
            # if the Wi-Fi is connected, break the loop
            break
        elif isTRUE("Wi-Fi still connecting"):
            # if the Wi-Fi is still connecting, wait for the screen to change
            wait()
        else:
            # if the password is incorrect, tap the 'CANCEL' button and continue to the next Wi-Fi network
            E("Page connecting to i-th Wi-Fi", "tap 'CANCEL' button")
            i += 1
    return "Task completed"



### **Important Notes**:
1. **Strict Output Rules**:
    - Your output must strictly follow the required format. Do **NOT** include any description, explanations, or text outside the required format.
    - The plan must be a valid Python-like function with no syntax errors.
    - Your output **must start** with 'Current vertex: <current_vertex>'.
    - Always begin the function with 'def new_plan():'.
2. **Error Handling**:
    - If the graph is missing necessary information, imagine additional vertices or edges and include 'imagined=True' in the corresponding functions.
    - If the task cannot be completed, return an appropriate error message in the plan.
3. **Plan Constraints**:
    - Always start from the current screen and ensure transitions follow the graph.
    - When navigatiing between apps, return to the home screen of the phone using 'KEYCODE' before switching to another app.
    - Use 'other_app_function' explicitly for actions involving other apps.
"""


post_see_template="""You are an intelligent agent trained to complete tasks on a smartphone.
Your role is to analyze the given app graph, the planned code, and two screenshots (before and after an action) to determine whether the plan or the graph needs revision.

To help you reason systematically, follow the steps outlined below:
---
### Context:
1. **Task**:
    The overall task you need to complete is to <task_description>.
2. **Graph Information**:
    The app you are working on, <app> , is represented as a directed graph:
    - **Vertices**: The screens of the app.
        <Vertices>
    - **Edges**: The possible transition functions between screens.
        <Edges>
3. **Plan Code**:
    A Python-like plan has been created based on the graph to complete the task. The plan is as follows:
    <plan>
    The plan may include imagined vertices or edges with the parameter 'imagined=True'.
4. **Current Information**:
    - The previous screenshot (before the action) corresponds to the vertex: <previous_vertex>.
    - The last action taken corresponds to the function: E(<previous_vertex>, <action>).
    - The detailed action performed is: <detailed_action> (the numeric tag of the UI element).
5. **Additional Information**:
    - Thoughts: <thought>
    - Summary: <summary>
    - Action History: <act_history>
    - Repeated Elements: <repeated_doc>
6. **Constraints and Notes**:
    - The app graph may need revision based on your observation of the screenshots and the action taken.
    - **Action Validity**:
        - If the action does not result in a change in the vertex(screen), you must identify it as an ineffective action.
        - If the detailed action was wrong (e.g., incorrect numeric tag), you must remind the user to choose a different numeric tag.
    - **Plan Revision**:
        - If the task is completed but the plan is not, revise the plan to directly return the result.
        - If adding **other_app_function**, ensure it is included in the **revised plan**.
        - Always exit to the home screen of the phone before calling **other_app_function**.
---
### **Your Task**:
1. Observe the current screenshot (second image).
2. Determine the current vertex based on the screenshot.
3. If necessary, revise the vertices, edges, and planned code.
4. Assess whether the action taken was successful and expected.
5. Provide reminders if needed to correct the action or address issues in the plan.
---
### **Output Format**:
Your response must strictly follow the format below:

Observation of the current screenshot: <Describe what you observe in the image>
Thoughts: <Explain your reasoning about the graph, plan, and the observed results, and why any revisions are necessary>

Removed vertices:
<Name: "<vertex_name>" Description: <description> can-self-act: <True/False> ... (if no changes, leave blank but keep "Removed vertices: " intact)>

Added vertices:
<Name: "<vertex_name>" Description: <description> can-self-act: <True/False> ... (if no changes, leave blank but keep "Added vertices: " intact)>

Removed edges:
<Edge: E("<start_vertex>", "<action>")->"<end_vertex>" #<comment>
... (if no changes, leave blank but keep "Removed edges: " intact)>

Added edges:
<Edge: E("<start_vertex>", "<action>")->"<end_vertex>" #<comment>
... (if no changes, leave blank but keep "Added edges: " intact)>

Current vertex: <current vertex>

Added functions for other apps:
<other_app_function("<app_name>", "<sub_task>")
... (if no changes, leave blank but keep "Added functions for other apps: " intact)>

Successful and expected action: <True/False>

Ineffective: <True/False>

Revised plan:
<def new_plan():
    # Revised code here...
    ...
(if no changes, leave blank but keep "Revised plan: " intact)>

Remind: <Write necessary reminders here; if none, leave blank but keep "Remind: " intact>

Impact of the action on the element on the task:
<Describe the effect of the action on the task; this must explicitly connect the transition between the two images and its impact on the task>
---

### **Example Output**:
Removed vertices: 
Name: "Main page of the Settings app" Desciption: Ohhhhhh. can-self-act: True
...

Added vertices: 
Name: "Main page of the Settings app" Desciption: The main page of the Settings App that can be used to navigate to other settings. can-self-act: True
...

The change of edges should be the form like:

Removed edges:
Edge: E("Main page of the Settings app", "KEYCODE")-> "Main page of Taobao" #Open Taobao
...

Added edges:
Edge: E("Main page of the Settings app", "KEYCODE") -> "Homepage of the phone" #Back to the phone homepage
...
---
### **Important Notes**:
1. **Removed/Added Vertices and Edges**:
    - If any vertices or edges are revised, the removed ones **must exactly match the original graph**, including the comments after "#".
    - Added vertices and edges must have clear descriptions and comments.
2. **Current Vertex**:
    - If the two screenshots differ in content, the vertex should change to reflect the current screenshot.
3. **Action Assessment**:
    - If the action is ineffective, mark it as True under "Ineffective".
    - If the action was not successful or expected, mark it as False under "Successful and expected action".
4. **Revised Plan**:
    - If the plan is revised, ensure it begins at the current vertex and includes transitions as required.
    - Any add "other_app_function" **must** be included in the revised plan.
5. **Strict Output Format**: All sections must be present, even if left blank.
"""

task_template ="""You are an intelligent agent trained to perform tasks on a smartphone.
You will analyze the given information, observe the screenshot, and call the appropriate functions to proceed with the task step by step.

To help you reason systematically, follow the steps outlined below:
---
### Context:
1. **Task Description**:
    The overall task you need to complete is to <task_description>.
2. **Graph Information**:
    - The app can be represented as a graph:
        - **Vertices**: The screens of the app.
        - **Edges**: The possible transition functions between screens.
    <Vertices>
    <Edges>
    - You are currently at vertex <current_vertex>.
3. **Plan**:
    - The overall plan, based on the graph,is as follows:
    <mission_plan>
    - Your currently exectuing the function inside the plan: <function>.
4. **Interaction Functions Available**:
    You can use the following functions to interact with the smartphone:
    - **tap(element: int)**: Taps a UI element labeled with the given numeric tag. Example: tap(5).
    - **text(text_input: str)**: Inserts the given text input into an input field. Example: text("Hello, world!").
    - **long_press(element: int)**: Long presses a UI element labeled with the given numeric tag. Example: long_press(5).
    - **swipe(element: int, direction: str, dist: str)**: Swipes on a UI element in a specified direction and distance. Example: swipe(21, "up", "medium").
    - **KEYCODE()**:
        - Navigates to the main page of the app if you are on a subpage.
        - Exits the app if you are on the main page of app.
    - **grid()**: Displays a grid overlay to interact with unlabeled UI areas.
    - **wait()**: Waits for the screen to change when the effect of the previous action is not immediately visible.
5. **Constraints**:
    - **Numeric Tags**: The biggest element number is <num_elem>. Do not choose any number greater than this.
    - **Action Validity**:
        - The 'Action' filed **must contain only a single valid function call or 'FINISH'**.No other output is allowed.
        - The numeric tag in 'Action' must be a valid integer within the allowed range (1 to <num_elem>).
    - **Error Handling**:
        - If a previous choice of numeric tag was wrong or did not change the screen(as indicated by history or a verifier), you must choose a different numeric tag.
        - Do not repeat the same action that was previously deemed incorrect.
6. **History and Observations**:
    - **Interaction History**:
    <act_history>
    - **Reminders and Corrections**:
        - <Remind_thing>
        - <Wrong_information>
        - <repeated_doc>
7. **General Guidelines**:
    - If the task involves unexpected circumstances, explore the smartphone further using available functions to resolve the issue (e.g.,navigating to settings or restarting the app).
    - The "Enter" button is always located in the bottom-right corner of the keyboard/screen.
---
### **Your Task**:
You need to carefully observe the labeled screenshot image, think logically about the next step, and call the appropriate functioon to proceed with the task. Your response must strictly follow the format below:
---
### **Output Format**:
Observation: <Describe what you observe in the image>
Thought: <To complete the given task, what is the next step I should do>
Action: <The function call (not the E function in the plan!) with the correct parameters to proceed with the task. If you believe the task is completed or there is nothing to be done, you should output FINISH. You cannot output anything else except a function call or FINISH in this field.>
Summary: <Summarize your action in the context of the graph, the plan, history trajectories and the expected action result. Do not include the numeric tag in your summary>
---
### **Example Output**:
Observation: The screenshot shows a button labeled "Settings" in the bottom-right corner.
Thought: To access the settings page, I should tap the "Settings" button.
Action: tap(5)
Summary: I will tap the "Settings" button to access the settings page.
---
### **IMPORTANT NOTES**:
1. **Observation**:Clearly describe the UI elements visibile in the screenshot, including their labels and positions.
2. **Thought**:Explain your reasoning about the next step to complete the task, considering the task description, plan, and current vertex in the graph.
3. **Action**:
    - **Strict Validity**: The 'Action' field must only contain a valid function call or 'FINISH'.
    - Ensure the numeric tag (if applicable) is within the range of 1 to <num_elem>.
    - If using text(), the string must be wrapped in double quotes.
    - If the previous actions were incorrect, select a new valid action and avoid repeating the same mistake.
4. **Summary**: Briefly summarize your chosen action without repeating the numeric tag or function syntax.
"""