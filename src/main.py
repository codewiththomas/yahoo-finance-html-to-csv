import os
from bs4 import BeautifulSoup
import csv
from datetime import datetime


def read_html_file():
    """ Liest den Inhalt der Datei table.html - diese muss im relativen Pfad ../data/table.html liegen. """
    base_path = os.path.dirname(__file__)
    html_path = os.path.join(base_path, '..', 'data', 'table.html')
    try:
        with open(html_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "Die Datei ../data/table.html konnte nicht gefunden werden."


def clean_text(element):
    """ Entfernt verschachtelte HTML-Elemente, wo eigentlich nur Text stehen sollte (z.B. Tooltips). """
    for tag in element.find_all():
        tag.decompose()  # Entfernt alls Tags innerhalb des Elements
    return element.text.strip()


def parse_numbers(number_str, input_decimal, input_thousand_separator, output_decimal):
    """ Adjust numbers to switch decimal and thousand separators. """
    if input_thousand_separator:
        number_str = number_str.replace(input_thousand_separator, '')  # Entferne Tausendertrennzeichen
    if input_decimal and input_decimal != output_decimal:
        number_str = number_str.replace(input_decimal, output_decimal)  # Wechsle Dezimaltrennzeichen von Eingabe- zu Ausgabeformat
    return number_str


def convert_date(date_str):
    """ Kovertiert 'MMM d, yyyy' zu 'yyyy-MM-dd'. """
    try:
        return datetime.strptime(date_str, '%b %d, %Y').strftime('%Y-%m-%d')
    except ValueError:
        return date_str  # Return original if conversion fails


def parse_html_to_csv(html_content, csv_settings):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    rows = []

    for row in table.find_all('tr'):
        cols = []
        for ele in row.find_all(['th', 'td']):
            text = clean_text(ele)
            # Zuerst Datumswerte konvertieren (Bei Parsingfehler wird der Originalwert zurückgegeben)
            if ',' in text:
                text = convert_date(text)
			# Potenziell Zahlenwerte konvertieren
            if any(char.isdigit() for char in text):
                text = parse_numbers(text, html_settings['decimal'], html_settings['thousand_separator'], csv_settings['decimal'])

            cols.append(text)
        rows.append(cols)

    # CSV ausgeben
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'output.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=csv_settings['delimiter'], quotechar=csv_settings['quotechar'], quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)
    return f"CSV gepeichert nach {csv_path}"


# Einstellungen für das HTML-Eingabeformat
html_settings = {
    'decimal': '.',             # Dezimaltrennzeichen
    'thousand_separator': ',',  # Tausendertrennzeichen
 }

# Einstellungen für die CSV-Ausgabe
csv_settings = {
    'delimiter': ';',
    'quotechar': '"',
    'decimal': ',',
 }

html_content = read_html_file()
if not html_content.startswith("The file"):
    result = parse_html_to_csv(html_content, csv_settings)
    print(result)
else:
    print(html_content)
