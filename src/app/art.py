from app.config import Config

art = r""" 
 ██████╗ ██████╗ ███╗   ██╗████████╗ █████╗ ██╗███╗   ██╗███████╗██████╗ ██╗   ██╗
██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██║████╗  ██║██╔════╝██╔══██╗╚██╗ ██╔╝
██║     ██║   ██║██╔██╗ ██║   ██║   ███████║██║██╔██╗ ██║█████╗  ██████╔╝ ╚████╔╝ 
██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██║██║██║╚██╗██║██╔══╝  ██╔══██╗  ╚██╔╝  
╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║██║██║ ╚████║███████╗██║  ██║   ██║   
 ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝   ╚═╝   
"""

def display_art():
    blue = "\033[96m"
    reset = "\033[0m"
    
    colored_art = ""
    current_state = "reset"

    for char in art:
        if char == '█':
            if current_state != "blue":
                colored_art += blue
                current_state = "blue"
        elif char.strip(): # Non-whitespace non-block
            if current_state != "reset":
                colored_art += reset
                current_state = "reset"
        
        colored_art += char
    
    colored_art += reset
    print(colored_art)
    print(f"Version: {Config.VERSION}")
    print(reset)