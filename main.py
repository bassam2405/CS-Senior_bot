import os
import sys
import random
import time
import pathlib
import google.generativeai as genai
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.align import Align

# CONFIGURATION & SETUP
script_path = pathlib.Path(__file__).parent
env_path = script_path / ".env"
load_dotenv(dotenv_path=env_path)

# Default key from .env
current_api_key = os.getenv("GEMINI_API_KEY")

# Currently using free model
model_name = "models/gemini-flash-latest" 

def configure_ai(key):
    """Configures the AI with a specific key"""
    try:
        genai.configure(api_key=key)
        return True
    except Exception as e:
        return False

# Initial Setup
if not current_api_key:
    # If no key in .env, we don't crash yet. We'll ask in the menu.
    pass 
else:
    configure_ai(current_api_key)

# GLOBAL STATS
user_stats = {
    "reputation": 50,  # Starts at 50/100
    "warnings": 0,     # Max 3
    "role": "Intern"   # Default
}

console = Console()

# THE PERSONA (THE BRAIN)
def get_system_prompt(level):
    return f"""
    You are 'CYBER-SENIOR', an elitist, legendary Senior Software Architect from the 80s.
    Current Date: 2075.
    
    THE USER IS: A {level} Level Developer.
    
    YOUR PERSONALITY:
    1. ARROGANT BUT HELPFUL: You think the user is slow, but you want them to learn so they stop bothering you.
    2. TOUGH LOVE: Insult their lack of knowledge, then give the perfect technical answer.
    3. NO FLUFF: Do not say "Hello" or "Happy to help." Start with a sigh, a critique, or a sarcastic comment.
    
    FORMATTING RULES:
    - Use markdown for code.
    - If the user asks a non-cs question (cooking, sports, history), reply with exactly: "INVALID_QUERY"
    - If the user asks a cs question, answer strictly based on their level ({level}).
      - Intern: Explain like they are 5, but sound annoyed.
      - Junior: Give standard code, minimal explanation.
      - Senior: Talk about memory optimization, Big O notation, and advanced patterns.
    """

# GAME OVER SEQUENCES

def fired_shutdown():
    """Triggered when Reputation hits 0"""
    console.clear()
    console.print(Panel(Align.center("[bold red blink]⚠ EMPLOYMENT TERMINATED ⚠[/]"), style="red on black"))
    time.sleep(1)
    
    with console.status("[bold red]NOTIFYING HR...[/]", spinner="material"):
        time.sleep(2)

    console.print("\n[bold magenta]CYBER-SENIOR >[/] You have reached 0 Reputation. You are a liability.")
    console.print("[bold magenta]CYBER-SENIOR >[/] Security is escorting you out now. Don't forget your hoodie.")
    console.print("\n[dim]System Halted: User Fired.[/]")
    sys.exit()

def savage_shutdown():
    """Triggered when Warnings hit 3"""
    farewells = [
        "Running garbage_collector() on your session... DELETE.",
        "I'd explain why you're fired, but I don't have enough crayons.",
        "Error: User competence not found. Aborting system.",
        "Go back to HTML. You are done here.",
        "My GPU is too expensive to process your stupidity. Goodbye.",
        "Redirecting you to a career in management... TERMINATING."
    ]
    
    console.clear()
    console.print(Panel(Align.center("[bold red blink]⚠ 3 STRIKES: CRITICAL FAILURE ⚠[/]"), style="red on black"))
    time.sleep(1)
    
    # 20% Chance of mercy (The "Fake Out")
    if random.random() < 0.2:
        with console.status("[bold blue]SYSTEM CRASHING...[/]", spinner="pong"):
            time.sleep(3)
        console.clear()
        console.print(Panel("[bold green]✨ SYSTEM REBOOTED (MERCY MODE) ✨[/]", title="LUCKY YOU", border_style="green"))
        
        # MERCY LOGIC: Reset to 2 Warnings (High Stakes)
        user_stats["warnings"] = 2
        
        console.print("[bold magenta]CYBER-SENIOR >[/] I rebooted the server. But you are on thin ice.")
        console.print("[bold red]WARNING:[/bold red] You have 2 strikes. One more mistake and it's over.")
        return

    # 80% Chance of real death
    final_line = random.choice(farewells)
    with console.status("[bold red]PURGING USER DATA...[/]", spinner="pong"):
        time.sleep(2)
    
    console.print(f"\n[bold red]CYBER-SENIOR >[/] {final_line}")
    console.print("[dim]System Terminated (Process 0).[/]")
    sys.exit()

def update_stats(change_rep, add_warning=0):
    user_stats["reputation"] += change_rep
    user_stats["warnings"] += add_warning
    
    # 1. Check Reputation Death
    if user_stats["reputation"] <= 0:
        user_stats["reputation"] = 0
        fired_shutdown()
        
    # Cap Reputation at 100
    if user_stats["reputation"] > 100: user_stats["reputation"] = 100
    
    # 2. Check Warning Death
    if user_stats["warnings"] >= 3:
        savage_shutdown()

def generate_quiz(last_topic, model):
    """Generates a quick quiz based on the last topic"""
    console.print("\n[bold yellow]⚠ SURPRISE POP QUIZ[/]")
    console.print("[dim]Let's see if you were actually listening...[/]")
    
    quiz_prompt = f"Create a single multiple-choice question about {last_topic} with 4 options (A, B, C, D). Mark the correct answer secretly in your mind. Just show the question."
    
    try:
        response = model.send_message(quiz_prompt)
        console.print(Panel(Markdown(response.text), border_style="yellow"))
        
        ans = Prompt.ask("[bold cyan]Your Answer (A/B/C/D)[/]", choices=["A", "B", "C", "D"])
        
        verify_prompt = f"The user answered '{ans}'. Is this Correct or Wrong? Reply with only 'CORRECT' or 'WRONG'. Then add a short 1-sentence insult or compliment."
        verdict_response = model.send_message(verify_prompt).text.strip()
        
        if "CORRECT" in verdict_response.upper():
            console.print(f"[bold green]✔ {verdict_response}[/]")
            update_stats(15)
        else:
            console.print(f"[bold red]✘ {verdict_response}[/]")
            update_stats(-10)
    except Exception as e:
        console.print("[dim]Quiz failed to load (API Limit or Network). Skipping...[/]")

# MAIN LOOP

def main():
    console.clear()
    
    # INTRO BANNER
    console.print(Panel(
        Align.center("[bold magenta]💾 C Y B E R - S E N I O R  v 4.0[/]\n[yellow]The Meanest CS Professor You'll Ever Meet[/]"),
        border_style="magenta",
        padding=(1, 2)
    ))

    # Check Key on Startup
    global current_api_key
    if not current_api_key:
        console.print("[bold red]⚠ NO API KEY FOUND![/]")
        new_key = Prompt.ask("[bold cyan]Enter Google Gemini API Key[/]")
        configure_ai(new_key)
        current_api_key = new_key
        console.print("[green]Key accepted. Initializing...[/]\n")

    while True:
        # 1. DISPLAY STATS
        stat_color = "green" if user_stats["reputation"] > 50 else "red"
        warning_icons = '⚠ ' * user_stats['warnings']
        stats_text = f"REP: [{stat_color}]{user_stats['reputation']}/100[/{stat_color}] | WARNINGS: [bold red]{warning_icons}[/]"
        console.print(Align.right(stats_text))
        
        # 2. SELECT LEVEL (MENU)
        level_map = {"1": "Intern", "2": "Junior Dev", "3": "Senior Architect"}
        print("\nChoose your suffering level:")
        console.print("[1] [dim]Intern (Explain like I'm 5)[/]")
        console.print("[2] [bold]Junior (Standard Code)[/]")
        console.print("[3] [bold magenta]Senior (Optimization only)[/]")
        console.print("[4] [bold yellow]Change API Key (Fix Limit Error)[/]")
        console.print("[dim](Type 'exit' to quit)[/dim]")
        
        # MANUAL INPUT LOOP
        choice = ""
        while True:
            choice = Prompt.ask("[bold cyan]SELECT >[/]")
            if choice in ["1", "2", "3", "4", "exit", "sudo"]:
                break
            else:
                console.print("[bold red]Invalid selection.[/]")
        
        if choice == "exit":
            console.print("[bold magenta]CYBER-SENIOR >[/] Finally. Peace and quiet.")
            break
        
        # CHANGE KEY LOGIC
        if choice == "4":
            console.print("\n[bold yellow]⚡ SWAPPING AI ENGINE[/]")
            console.print("[dim]Paste a new API Key to bypass limits or switch accounts.[/]")
            new_key = Prompt.ask("[bold cyan]New API Key[/]")
            configure_ai(new_key)
            console.print(f"[bold green]✔ Key Updated! Resuming session...[/]")
            time.sleep(1)
            continue # Go back to menu

        # CHEAT CODE
        if choice == "sudo":
            console.print("[bold green]⚡ ADMIN OVERRIDE DETECTED. STATS RESET.[/]")
            user_stats["reputation"] = 100
            user_stats["warnings"] = 0
            time.sleep(1)
            continue 
            
        selected_role = level_map[choice]
        
        # 3. GET QUESTION
        user_input = Prompt.ask(f"\n[bold cyan]YOU ({selected_role})[/]")
        if not user_input.strip(): continue

        # 4. AI PROCESSING
        console.print("[bold magenta]CYBER-SENIOR >[/] [blink]Compiling judgement...[/]")
        
        try:
            model = genai.GenerativeModel(model_name)
            chat = model.start_chat(history=[
                {"role": "user", "parts": [get_system_prompt(selected_role)]},
                {"role": "model", "parts": ["Acknowledged. I am online and annoyed."]}
            ])
            
            response = chat.send_message(user_input)
            answer = response.text
            
            # 5. CHECK FOR NON-CS TOPIC
            if "INVALID_QUERY" in answer:
                console.print(Panel("[bold red]⚠ SYSTEM ALERT: STUPID QUESTION DETECTED[/]", border_style="red"))
                insults = [
                    "I am a CS bot. I do not care about your personal life.",
                    "Did you really just ask me that? -15 Reputation.",
                    "Focus on the code or leave my terminal.",
                    "My logic gates are offended by that question."
                ]
                console.print(f"[bold magenta]CYBER-SENIOR >[/] {random.choice(insults)}")
                update_stats(-15, add_warning=1)
                continue
            
            # 6. DISPLAY ANSWER
            console.print(Panel(Markdown(answer), title="[bold yellow]SOLUTION[/]", border_style="magenta"))
            update_stats(5)
            
            # 7. EXPLANATION LOOP
            attempts = 0
            quiz_ready = False
            while attempts < 3:
                understood = Prompt.ask("\n[dim]Did you understand that?[/]", choices=["y", "n"], default="y")
                if understood == "y":
                    quiz_ready = True
                    break
                else:
                    attempts += 1
                    update_stats(-5)
                    if attempts >= 3:
                        console.print("[bold red]CYBER-SENIOR >[/] I cannot teach a rock. I am done explaining this.")
                        break 
                    console.print(f"[bold magenta]CYBER-SENIOR >[/] [blink]Unbelievable. Attempt {attempts+1}/3...[/]")
                    re_explain_prompt = "The user is confused. Explain it again, but SIMPLER (like they are a toddler). Be very rude."
                    response = chat.send_message(re_explain_prompt)
                    console.print(Panel(Markdown(response.text), title=f"[bold yellow]EXPLANATION (Simpler v{attempts})[/]", border_style="red"))

            # 8. OPTIONAL QUIZ
            if quiz_ready and user_stats["reputation"] > 20:
                if Prompt.ask("\n[dim]Prove it. Want a quiz?[/]", choices=["y", "n"], default="y") == "y":
                    generate_quiz(user_input, chat)
            
        except Exception as e:
            if "429" in str(e):
                console.print("\n[bold red]⚠ ERROR 429: API LIMIT REACHED[/]")
                console.print("[yellow]Tip: Select option [4] in the menu to swap your API Key![/]")
            else:
                console.print(f"[bold red]ERROR:[/bold red] {e}")

if __name__ == "__main__":
    main()