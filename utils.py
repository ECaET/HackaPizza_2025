import fitz
import json
import os

def call_gpt(client, msg, model_name="gpt-4o-mini"):

    result = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": msg}],
        temperature=0
    )

    return result.choices[0].message.content


def parse_pdfs_folder(pdf_folder_path, customized_prompt):
    # Iterate through all PDF files in the folder
    for filename in os.listdir(pdf_folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder_path, filename)
            # Read the PDF and store the content in menu_text
            menu_text = read_pdf_to_string(pdf_path)
            
            prompt = customized_prompt + menu_text

            #result = model.chat(messages=[{'role': 'user', 'content': prompt}])

            result = call_gpt(prompt)

            #print(result['choices'][0]['message']['content'])

            #save_string_to_json_file(result['choices'][0]['message']['content'])

            save_planet_to_json_file(result)


def read_pdf_to_string(pdf_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    menu_text = ""

    # Iterate through each page
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        menu_text += page.get_text()

    return menu_text


def save_planet_to_json_file(json_string):
    # Rimuove eventuali intestazioni ```json iniziali e ``` finali
    json_string = json_string.strip().strip('```json').strip('```')
    
    # Parse the JSON string
    data = json.loads(json_string)
    
    # Extract the restaurant name
    restaurant_name = data.get("nome_ristorante", "default_name").replace(" ", "_")
    
    # Define the file name
    file_name = f"{restaurant_name}_planet.json"
    
    # Save the JSON content to the file
    with open(file_name, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)