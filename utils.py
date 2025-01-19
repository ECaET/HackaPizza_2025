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


def json_txt_to_submission(dish_mapping_path: str, input_txt_path: str, output_csv_path: str, empty_guess_filler: list=[288]) -> None:

    """
    Converte i risultati della Chain in un csv pronto alla submission su Kaggle

    ### Input
    * input_txt_path: path al file txt di input, contenente un json le cui chiavi sono l'ID intero della domanda posta
    e i valori una lista contenente le ricette restituite dalla query
    * dish_mapping_path: path al file di mapping, contenente un json le cui chiavi sono il nome della ricetta
    e i valori l'ID intero corrispondente
    * output_csv_path: path al csv di output da caricare su Kaggle
    * empty_guess_filler: lista sostituita a tutte le risposte che non contengono alcuna ricetta, con default
    """

    # Read the input file
    with open(input_txt_path, "r") as infile:
        data = json.load(infile)

    with open(dish_mapping_path) as f:
        dish_mapping = json.load(f)

    submission = {}
    for question_number, corresponding_recipies_list in data.items():
        submission[question_number] = [dish_mapping.get(elem, 999) for elem in corresponding_recipies_list]
        if not submission[question_number]:
            submission[question_number] = empty_guess_filler

    # Prepare the output content
    output_lines = ["row_id,result"]
    for key, values in submission.items():
        row = str(int(key)) + ',"' + ','.join(map(str, values)) + '"'
        output_lines.append(row)

    # Write the output to a new file
    with open(output_csv_path, "w") as outfile:
        outfile.write("\n".join(output_lines))

    return


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