import os
from dotenv import load_dotenv
import json
import jsonschema
import requests #to see the responses
from getpass import getpass
import streamlit as st

load_dotenv()
openaikey = os.getenv('OPENAI_API_KEY')

chatgpt_url = "https://api.openai.com/v1/chat/completions"
chatgpt_headers = {
    "content-type": "application/json",
    "Authorization":"Bearer {}".format(openaikey)}

text= ""

prompt_prefix = f"""You are specialized in generating JSON files from a description of a natural text with a description of a workout.
It helps users upload their workout information, analyzes it, and creates accurate JSON.
Generate a JSON file from the above text.
You have forbidden to add keys that are not in the text; if they are not in the text, they don't have to be in the JSON.

Strictly output in JSON format and do not invent names (keys), follow the examples names of the JSON keys."""

# How should the text be:
sample_1 = """###
I need you to generate a detailed workout routine for the workout with name Timed Test.
The total duration of the workout is 60 seconds, the workout type is timed, and the rate of Perceived Exertion is 6.
The round type is fixed (Exercises remain constant in each round) and there are 2 rounds in total. In each round, the exercises are as follows:

The first exercise is called air squat with 3 repetitions and a duration of 10 seconds.
The second exercise is called back squat with 3 repetitions, a duration of 10 seconds and a weight of 50.
The third exercise is called mountain climber with a duration of 10 seconds and a weight of 50.

Ensure the generated workout routine accurately reflects these details, and consider presenting it in a clear and well-organized format.
---
Count: 1
Output:"""

#Count: 1 == one set of JSON based on the information provided
# It is used in the context in OpenAI's GPT-3 and GPT-4 models when using the chat-based API

# How should the output be:
sample1_output_json = [

   {
    "name": "Timed Test",
    "duration": 60,
    "description": "",
    "nrounds": 2,
    "type": "timed",
    "rpe": 6,
    "content": {
        "roundType": "fixed",
        "rounds": [
            {
                "exercises": [
                    {
                        "id": "air-squat",
                        "targets": {
                            "target_repetitions": 3,
                            "target_duration": 10
                        }
                    },
                    {
                        "id": "back-squat",
                        "targets": {
                            "target_repetitions": 3,
                            "target_duration": 10,
                            "target_weight": 50
                        }
                    },
                    {
                        "id": "mountain-climber",
                        "targets": {
                            "target_duration": 10,
                            "target_weight": 50
                        }
                    }
                ]
            }
        ]
    },
    "id": "_test-timed"
}

]

sample_2 = """###
I need you to generate a detailed workout routine for the workout with name Cardio 101.
The total duration of the workout is 480 seconds, the workout type is timed, and the rate of Perceived Exertion is 4.
The round type is fixed (Exercises remain constant in each round) and there are 4 rounds in total.In each round, the exercises are as follows:

The first exercise is called skater with a heart rate zone of 4 and a duration of 60 seconds.
The second exercise is called high knww with a heart rate zone of 4 and a duration of 30 seconds.
The third exercise is called squat jump with 20 repetitions, a heart rate zone of 5 and a duration of 30 seconds.

Ensure the generated workout routine accurately reflects these details, and consider presenting it in a clear and well-organized format.
---
Count: 1
Output:"""

sample2_output_json = [
{
    "name": "Cardio 101",
    "duration": 480,
    "description": "Cardio",
    "nrounds": 4,
    "type": "timed",
    "rpe": 4,
    "content": {
        "roundType": "fixed",
        "rounds": [
            {
                "exercises": [
                    {
                        "id": "skater",
                        "targets": {
                            "target_hr_zone": 4,
                            "target_duration": 60
                        }
                    },
                    {
                        "id": "high-knee",
                        "targets": {
                            "target_hr_zone": 4,
                            "target_duration": 30
                        }
                    },
                    {
                        "id": "squat-jump",
                        "targets": {
                            "target_repetitions": 20,
                            "target_hr_zone": 5,
                            "target_duration": 30
                        }
                    }
                ]
            }
        ]
    },
    "id": "ftz-timed-cardio-002"
}
]

sample_3 = """###
I need you to generate a detailed workout routine for the workout with name Leg 101.
This is a leg workout for beginners. It is a timed workout with 3 rounds. The goal is to complete the workout in the shortest time possible.
The total duration of the workout is 540 seconds, the workout type is timed, and the rate of Perceived Exertion is 6.
The round type is fixed (Exercises remain constant in each round) and there are 3 rounds in total.In each round, the exercises are as follows:

The first exercise is called air squat with 30 repetitions and a duration of 60 seconds.
The second exercise is called back squat with 30 repetitions and a duration of 60 seconds and a weight of 50.
The third exercise is called front squat with a duration of 60 seconds and a weight of 50.

Ensure the generated workout routine accurately reflects these details, and consider presenting it in a clear and well-organized format.
---
Count: 1
Output:"""

sample3_output_json = [
{
    "name": "Leg 101",
    "duration": 540,
    "description": "This is a leg workout for beginners. It is a timed workout with 3 rounds. The goal is to complete the workout in the shortest time possible.",
    "nrounds": 3,
    "type": "timed",
    "rpe": 6,
    "content": {
        "roundType": "fixed",
        "rounds": [
            {
                "exercises": [
                    {
                        "id": "air-squat",
                        "targets": {
                            "target_repetitions": 30,
                            "target_duration": 60
                        }
                    },
                    {
                        "id": "back-squat",
                        "targets": {
                            "target_repetitions": 30,
                            "target_duration": 60,
                            "target_weight": 50
                        }
                    },
                    {
                        "id": "front-squat",
                        "targets": {
                            "target_duration": 60,
                            "target_weight": 50
                        }
                    }
                ]
            }
        ]
    },
    "id": "ftz-timed-strength-leg-001"
}
]


#Pass the real text which i want the output to be a JSON
# 2 placeholders: one for text and the other one to count (in this case 1 output)
inference_example_text = """###
{}
---
Count: {}
Output:
""".format(text, 1)

#Creation of the prompt with the examples:
training_instructions = prompt_prefix + sample_1 + json.dumps(sample1_output_json) + sample_2 + json.dumps(sample2_output_json) + sample_3 + json.dumps(sample3_output_json) + "\n"
inference_example_text = "###\n{}\n---\nCount: 3\nOutput:".format(text)
prompt = training_instructions + inference_example_text

messages = [
        {"role": "system", "content": "You are an experienced JSON workout creator."},
        {"role": "user", "content": prompt}

    ]

chatgpt_payload = {
    "model": "gpt-4-1106-preview",
    "messages": messages,
    "temperature": 1.2,
    "max_tokens": 300,
    "top_p": 1,
    "stop": ["###"]
}

response = requests.request("POST", chatgpt_url, json=chatgpt_payload, headers=chatgpt_headers)
response = response.json()
print (response)
print (response['choices'][0]['message']['content'])

# Define the JSON schema
json_schema = {
    "title": "Workout Definition",
    "description": "A workout in the catalog",
    "type": "object",
    "properties": {
        "id": {
            "description": "The unique identifier for a workout",
            "type": "string"
        },
        "name": {
            "description": "Name of the workout",
            "type": "string"
        },
        "description": {
            "description": "Description of the workout",
            "type": "string"
        },
        "duration": {
            "description": "Duration of the workout in seconds",
            "anyOf": [
                {
                    "type": "integer",
                    "minimum": 0
                },
                {
                    "type": "null"
                }
            ]
        },
        "nrounds": {
            "description": "Number of rounds in the workout",
            "type": "integer",
            "minimum": 1
        },
        "rpe": {
            "description": "RPE of the workout",
            "type": "integer",
            "minimum": 1,
            "maximum": 10
        },
        "type": {
            "description": "Type of the workout",
            "enum": [
                "amrap",
                "emom",
                "timed",
                "for-time",
                "rest"
            ]
        },
        "content": {
            "description": "Content of the workout",
            "$ref": "#/$defs/rounds-definition"
        }
    },
    "required": [
        "name",
        "duration",
        "type",
        "content"
    ],
    "$defs": {
        "exercise-targets": {
            "title": "Exercise Targets",
            "description": "Target definition for an exercise in a workout",
            "type": "object",
            "properties": {
                "target_repetitions": {
                    "description": "Number of repetitions to perform",
                    "type": "integer",
                    "minimum": 1
                },
                "target_duration": {
                    "description": "Duration of the exercise in seconds",
                    "anyOf": [
                        {
                            "type": "integer",
                            "minimum": 0
                        },
                        {
                            "type": "null"
                        }
                    ]
                },
                "target_hr_zone": {
                    "description": "Target heart rate zone",
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5
                },
                "target_weight": {
                    "description": "Target weight in %1RM",
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "minProperties": 1
        },
        "exercise": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "The unique identifier for an exercise"
                },
                "targets": {
                    "$ref": "#/$defs/exercise-targets"
                }
            },
            "required": [
                "id",
                "targets"
            ]
        },
        "round-details": {
            "title": "Round details",
            "description": "Set of exercises in a round",
            "type": "object",
            "properties": {
                "exercises": {
                    "description": "Exercises included in the round",
                    "type": "array",
                    "items": {
                        "$ref": "#/$defs/exercise"
                    },
                    "minItems": 1
                }
            }
        },
        "ladder-config": {
            "title": "Ladder configuration",
            "description": "Configuration of the ladder",
            "type": "object",
            "properties": {
                "repetitionsIncrement": {
                    "description": "Incremental value of the repetitions",
                    "type": "integer"
                },
                "durationIncrement": {
                    "description": "Incremental value of the repetitions",
                    "type": "integer"
                }
            },
            "minProperties": 1
        },
        "rounds-definition": {
            "title": "Rounds definition",
            "description": "Definition of the distribution of rounds",
            "type": "object",
            "properties": {
                "roundType": {
                    "description": "Type of the rounds definition",
                    "enum": [
                        "fixed",
                        "alternating",
                        "ladder",
                        "custom"
                    ],
                    "default": "fixed"
                },
                "if": {
                    "properties": {
                        "roundType": {
                            "const": "ladder"
                        }
                    }
                },
                "then": {
                    "properties": {
                        "ladderConfig": {
                            "$ref": "#/$defs/ladder-config"
                        }
                    },
                    "required": [
                        "ladderConfig"
                    ]
                },
                "rounds": {
                    "description": "Exercises included in the workout",
                    "type": "array",
                    "items": {
                        "$ref": "#/$defs/round-details"
                    },
                    "minItems": 1
                }
            },
            "required": [
                "roundType",
                "rounds"
            ]
        }
    }
}

def get_generated_messages():
    return []

def run_chatbot_and_validate(model, user_input, temperature=1.2, max_tokens=300, max_attempts=3, top_p=1, stop=["###"]):
    attempts = 0
    generated_json_list = []

    while attempts < max_attempts:
        messages = [
            {"role": "system", "content": "You are an experienced JSON workout creator."},
            {"role": "user", "content": user_input}
        ]

        chatgpt_payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stop": stop
        }

        response = requests.post(chatgpt_url, json=chatgpt_payload, headers=chatgpt_headers)
        result = response.json()
        
        # Extract the generated JSON from the response
        generated_json_str = result['choices'][0]['message']['content']
        
        # Skip the "Generated Options" message
        if "Generated Options" not in generated_json_str:
            print(f"\nOption {attempts + 1} - Generated JSON String:\n{generated_json_str}")
            
            # Add each generated message to the history
            generated_json_list.append(generated_json_str)
            attempts += 1

    return generated_json_list

def validate_json(json_data, schema):
    try:
        jsonschema.validate(instance=json_data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        print("Validation Error:", e)
        return False


#STREAMLIT APP CONSTRUCTION: 
def main():
    st.title("FITIZENS Chatbot : Your Training Scheduler 🏋️🎽🏃")
    st.image("fitizens.png", use_column_width=True)  

    user_prompt = st.text_area("Describe la rutina de ejercicios aquí:")
    max_attempts = 3  # Número máximo de intentos (tries)

    message_slot = st.empty()

    if st.button("Generar Rutinas"):
        if user_prompt:
            try:
                messages = [
                    {"role": "system", "content": "You are an experienced JSON workout creator."},
                    {"role": "user", "content": user_prompt}
                ]

                generated_json_list = run_chatbot_and_validate("gpt-4-1106-preview", user_prompt, max_attempts=max_attempts)

                # Print a message to the terminal
                print("Las opciones generadas se han impreso en la terminal.")
                
            except Exception as e:
                # Print an error message to the terminal
                print(f"Error: {e}")
                # Update the Streamlit message slot with an info message
                message_slot.info("Las opciones se encuentran en la terminal.")
        else:
            st.warning("Por favor, ingrese una descripción de rutina de ejercicio.")
    
    # Show a success message in Streamlit with larger font size
    st.success("Tus resultados se encuentran en la terminal.")
    
    # Additional styling for the info message
    st.markdown("<p style='font-size:18px; color: blue;'>Muchas gracias! Hasta la próxima </p>", unsafe_allow_html=True)

if __name__ == "__main__":
    st.set_page_config(page_title="FITIZENS Chatbot : Your Training Scheduler 🏋️🎽🏃")  
    main()
