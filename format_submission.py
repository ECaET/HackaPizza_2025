import json

def json_txt_to_submission(dish_mapping_path: str, input_txt_path: str, output_csv_path: str) -> None:

    """
    Converte i risultati della Chain in un csv pronto alla submission su Kaggle

    ### Input
    * input_txt_path: path al file txt di input, contenente un json le cui chiavi sono l'ID intero della domanda posta
    e i valori una lista contenente le ricette restituite dalla query
    * dish_mapping_path: path al file di mapping, contenente un json le cui chiavi sono il nome della ricetta
    e i valori l'ID intero corrispondente
    * output_csv_path: path al csv di output da caricare su Kaggle
    """

    # Read the input file
    with open(input_txt_path, "r") as infile:
        data = json.load(infile)

    with open(dish_mapping_path) as f:
        dish_mapping = json.load(f)

    submission = {}
    for question_number, corresponding_recipies_list in data.values():
        submission[question_number] = [dish_mapping.get(elem, 999) for elem in corresponding_recipies_list]

    # Prepare the output content
    output_lines = ["row_id,result"]
    for key, values in submission.items():
        row = f"{int(key)},\"{",".join(map(str, values))}\""
        output_lines.append(row)

    # Write the output to a new file
    with open(output_csv_path, "w") as outfile:
        outfile.write("\n".join(output_lines))

    return