import os 
import random
import csv
from openai import OpenAI
import json
import ast
def clear_screen():
    os.system("clear")
#global variables
game_category = ""
answer = ""
answer_key = ""
score = 0
q_num = 0
question = ""
correct_answer = "" 
correct_n = 0
problem = ""
num_questions=10
another = "Y" 
gpt_response = ""
def load_questions(filename):
    loaded_questions = []
    with open(filename, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Debugging output to trace content format
            print("Original Row:", row)
            
            # Process 'options' assuming they are enclosed in quotes if they contain commas
            try:
                # Using ast.literal_eval to safely parse the string-list 'options'
                row['options'] = ast.literal_eval(row['options'])
            except Exception as e:
                # Fallback if ast.literal_eval fails, split on commas directly
                print(f"Failed to parse options with literal_eval: {row['options']}, error: {e}")
                row['options'] = [option.strip() for option in row['options'].strip('[]').split(',')]
            
            # Further debugging output to check post-processing contents
            print("Processed Options:", row['options'])
            loaded_questions.append(row)
    return loaded_questions
#Game selection
def start_game():
    clear_screen()
    global game_category
    valid_categories = ["Science","Math","History","English","Other"]
    print("Hello and welcome to the CLI quiz game!")
    while True:
        game_category = input("What category would you like to play?\n-Science\n-Math\n-History\n-English\n-Other\n").strip().title()
        if game_category in valid_categories:
            break            
        else:
            print("Error: Invalid Category. Please choose one of the listed categories.")

#Other quizzes
eng_questions = load_questions('EnglishQuizQuestions.csv')
sci_questions = load_questions('ScienceQuizQuestions.csv')
hist_questions = load_questions('HistoryQuizQuestions.csv')
def other_quizzes(questions):
    clear_screen()
    global score, answer_key, question, q_num, correct_answer, user_answer, game_category, ready
    if game_category == "English":
        quiz_questions = eng_questions
    elif game_category == "Science":
        quiz_questions = sci_questions
    elif game_category == "History":
        quiz_questions = hist_questions
    elif game_category == "Other":
        quiz_questions = other_questions

    print(f"Welcome to the {game_category} quiz, are you ready?")
    while True:
        ready = input("(Y/N) ").strip().title()
        if ready == "Y":
            break

    score = 0
    answer_key = []
    possible_answers = ["A", "B", "C", "D"]

    for q_num in range(1, 11):
        clear_screen()
        question_data = quiz_questions[q_num - 1]
        question = question_data['question']
        correct_answer = question_data['answer'].strip()
        options = [option.strip() for option in question_data['options']]

        # Store the index of the correct answer before shuffling
        try:
            correct_index = options.index(correct_answer)
        except ValueError:
            print(f"Error: The correct answer '{correct_answer}' is not in the options for the question: {question}")
            continue  # Skip this question

        random.shuffle(options)

        # Find the new index of the correct answer after shuffling
        new_correct_index = options.index(correct_answer)
        answer_key.append(possible_answers[new_correct_index])

        # Display the question and options
        problem = f"Question {q_num}:\n{question}\n"
        for idx, option in enumerate(options, start=1):
            problem += f"{possible_answers[idx-1]}. {option}\n"

        # Get user answer
        while True:
            user_answer = input(problem).strip().upper()
            if user_answer in possible_answers:
                break
            else:
                print("Error: Invalid answer. Answer must be A, B, C, or D.")

        # Check if answer is right
        if user_answer == possible_answers[new_correct_index]:
            score += 1
            print(f"Correct! Your score is currently {score}/10.")
        else:
            print(f"Wrong! The correct answer was '{possible_answers[new_correct_index]}'. Your current score is {score}/10.")

        if q_num < 10:
            input("Press Enter for the next question...")

    clear_screen()
    print(f"Congratulations! You have finished the {game_category} quiz with a score of {score} out of 10!")
    play_again()      
#BYO quiz with openAI API

model = "question,options,answer\nWhat is the synonym of 'begin'?,'Start,Finish,Endure,Decrease',Start\nChoose the correct spelling:,'Definitely,Definately,Definetly,Definitaly',Definitely\nWhat is the antonym of 'empty'?,'Void,Full,Hollow,Blank',Full"


def makecsv():
    client = OpenAI(
        api_key='',
    )
    global gpt_category,other_questions

    def ask_ai(gpt_category):
        prompt = f"Generate a JSON-formatted list of dictionaries for a quiz about {gpt_category}. There should be 10 entries. Each dictionary should include 'question', 'options' as a list of strings, and 'answer' as a single string. Example output should be: \n" \
             f"[{{'question': 'What is the capital of France?', 'options': 'Paris', 'Lyon', 'Marseille', 'Nice', 'answer': 'Paris'}}] Make sure it is JSON formatted and follow the formatiing of this exactly: {model}. Make sure you have no brackets around the options string and no double quotation marks; only '' around the entire list of strings for options."
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt},
            ],
            model="gpt-3.5-turbo-1106",
        )
        return chat_completion.choices[0].message.content

    gpt_response = ask_ai(gpt_category)
    print("GPT-3 Response:", gpt_response)  # Debug print to inspect the format of GPT-3 output

    try:
        data = json.loads(gpt_response)  # Attempt to parse GPT-3 response into JSON
    except json.JSONDecodeError:
        print("Failed to decode GPT-3 response into JSON. The response was:")
        print(gpt_response)  # Print the erroneous GPT-3 output for inspection
        return

    def write_csv(filename, data):
        with open(filename, mode='w', newline='') as file:
            fieldnames = ["question", "options", "answer"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for entry in data:
                writer.writerow(entry)

    filename = (f"/Users/aidanmorgan/VSCODE/{gpt_category}QuizQuestions.csv")
    write_csv(filename, data)
    other_questions = load_questions(f'{gpt_category}QuizQuestions.csv')
def fix_csv_options(input_file, output_file):
    corrected_rows = []
    fieldnames = []

    with open(input_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        
        for row in reader:
            options = row['options'].strip()
            if options.startswith('[') and options.endswith(']'):
                # Convert string representation of list to actual list
                options = options[1:-1].split(',')
                # Clean the options by stripping spaces and extra quotes
                options = [opt.strip().strip("'\"") for opt in options]
            else:
                options = options.split(',')
                options = [opt.strip() for opt in options]

            # Directly join the options with commas
            row['options'] = ','.join(options)
            corrected_rows.append(row)

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(corrected_rows)

    print(f"File has been processed and saved as: {output_file}")
#setup what is needed for custom quiz

#see if they want to play another quiz
def play_again():
    global another,game_category
    another = input("Would you like to do another quiz?(Y/N) ").title()
    if another == "Y":
         game_category = input("What category would you like to do next? ").strip().title()

#Math quiz
def math_quiz():
    #generate the math questions

    def gen_math_q():
        global question,correct_answer,correct_n
        correct_n = random.randint(1,4)
        operations = ['+','-','*','/']
        num1 = random.randint(1,100)
        num2 = random.randint(1,100)
        operation = random.choice(operations)
        question = f"What is {num1} {operation} {num2}?"
        correct_answer = str(round(eval(f"{num1}{operation}{num2}"), 2))
    #math answer check 

    def check_answer():
        global user_answer,score,answer_key,correct_answer
        if user_answer == answer_key[q_num - 1]:
            score +=1
            print(f"Correct! Your current score is {score}/10")
        else:
            print(f"Incorrect. Your current score is {score}/10")
    clear_screen()

    global answer_key,user_answer,q_num,question,correct_answer,score,problem
    print(f"Welcome to the {game_category} quiz, are you ready?")
    #start of quiz

    while True:
        ready = input("(Y/N)").title()
        if ready == "Y":
            break
    answer_key = []
    possible_answers = ["A","B","C","D"]
    score = 0
    for q_num in range(10):
        clear_screen()
        gen_math_q()
        q_num += 1
        if correct_n == 1:
                problem = f"Question {q_num}:\n{question}\nA. {correct_answer}\nB. {random.randint(-50,100)}\nC. {random.randint(-50,100)}\nD. {random.randint(-50,100)}\n"
                answer_key.append("A")            
        elif correct_n == 2:
                problem = f"Question {q_num}:\n{question}\nA. {random.randint(-50,100)}\nB. {correct_answer}\nC. {random.randint(-50,100)}\nD. {random.randint(-50,100)}\n"
                answer_key.append("B")
        elif correct_n == 3:
                problem = f"Question {q_num}:\n{question}\nA. {random.randint(-50,100)}\nB. {random.randint(-50,100)}\nC. {correct_answer}\nD. {random.randint(-50,100)}\n"
                answer_key.append("C")
        elif correct_n == 4:
                problem = f"Question {q_num}:\n{question}\nA. {random.randint(-50,100)}\nB. {random.randint(-50,100)}\nC. {random.randint(-50,100)}\nD. {correct_answer}\n"
                answer_key.append("D")   
        while True:
            user_answer = input(problem).title()
            if user_answer in possible_answers:
                break
            else:
                print("Error: invalid answer. Answer must be A,B,C, or D.")
        if q_num <= 9:
            check_answer()
            ready_up()
        clear_screen() 
        check_answer()
        clear_screen()
    print(f"Congratulations! You have finished the math quiz with a score of {score} out of 10!")
    play_again()

#ready between questions
def ready_up():
    input("Press Enter for next question...")

start_game()
while True:
    if another == "Y":
        if game_category == "Math":
            math_quiz()
        elif game_category == "English":
            questions = load_questions('EnglishQuizQuestions.csv')
            other_quizzes(questions)
        elif game_category == "Science":
             questions = load_questions('ScienceQuizQuestions.csv')
             other_quizzes(questions)
        elif game_category == "History":
             questions = load_questions('HistoryQuizQuestions.csv')
             other_quizzes(questions)
        elif game_category == "Other":
             gpt_category = input("What do you want to be quizzed on? ").strip().title()
             makecsv()
             input_filename = f'{gpt_category}QuizQuestions.csv'
             output_filename = f'new_{gpt_category}QuizQuestions.csv'
             fix_csv_options(input_filename, output_filename)
             questions = load_questions(f'new_{gpt_category}QuizQuestions.csv')
             other_quizzes(questions)

    else:
         print("Thanks for playing!")
         break