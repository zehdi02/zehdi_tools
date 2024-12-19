import re
import os
import json
import glob
import zipfile
import argparse
from collections import defaultdict
from sudachipy import tokenizer
from sudachipy import dictionary

parser = argparse.ArgumentParser(description="Generate a frequency dictionary from OCR data.")
parser.add_argument("ocr_dir", type=str, help="Path to the directory containing OCR folders.")
args = parser.parse_args()

ocr_dir = args.ocr_dir

matching_folders = os.listdir(ocr_dir)
ocr_parent_name = os.path.basename(os.path.dirname(ocr_dir))
ocr_parent_name = ocr_parent_name.replace(' mangajanai', '')

print(f'Found {len(matching_folders)} folders containing text.')
print('=' * 40)

all_sentences = []

japanese_char_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')

for i in range(len(matching_folders)):
    folder_path = os.path.join(ocr_dir, matching_folders[i])

    json_files = sorted(glob.glob(os.path.join(folder_path, '*.json')))

    for json_fp in json_files:
        with open(json_fp, 'r', encoding='utf-8') as file:
            data = json.load(file)

        lines = [[''.join(block["lines"]) for block in data.get("blocks", [])]]

        cleaned_lines = [[
            ''.join(japanese_char_pattern.findall(line)) for line in sentence
        ] for sentence in lines]

        cleaned_lines = [sentence for sentence in cleaned_lines if any(sentence)]

        all_sentences.extend(cleaned_lines)

    if (i % 5) == 0 and i != 0:
        print(f'Finished processing {i} folders')

print(f'Finished processing {len(matching_folders)} folders')
print(f'Found {len(all_sentences)} sentences across {len(matching_folders)} folders.')
print('=' * 40)
tokenizer_obj = dictionary.Dictionary(dict="full").create(tokenizer.Tokenizer.SplitMode.C)

def is_kanji(char):
    return '\u4e00' <= char <= '\u9faf'

def is_pure_kanji(token):
    return all(is_kanji(char) for char in token)

def contains_kanji(token):
    return any(is_kanji(char) for char in token)

pure_kanji_freq = defaultdict(int)
kanji_kana_freq = defaultdict(int)
kana_freq = defaultdict(int)

def tokenize_text(text):
    return [word.dictionary_form() for word in tokenizer_obj.tokenize(text)]

for sentence in all_sentences:
    tokens = tokenize_text(str(sentence))
    for token in tokens:
        if not token:
            continue
        if is_pure_kanji(token):
            pure_kanji_freq[token] += 1
        elif contains_kanji(token):
            kanji_kana_freq[token] += 1
        else:
            kana_freq[token] += 1

kanji_words = sorted(pure_kanji_freq.items(), key=lambda item: item[1], reverse=True)
kanji_kana_words = sorted(kanji_kana_freq.items(), key=lambda item: item[1], reverse=True)
kana_words = sorted(kana_freq.items(), key=lambda item: item[1], reverse=True)

# print("Unique Pure Kanji Words:", len(kanji_words))
# print("Unique Kanji + Kana Words:", len(kanji_kana_words))
# print("Unique Kana Words:", len(kana_words))

all_vocab = kanji_words + kanji_kana_words + kana_words
sorted_occurences = sorted(all_vocab, key=lambda x: x[1], reverse=True)
# print(f'Total Unique Words: {len(sorted_occurences)}')

total_occurrences = sum(count for _, count in all_vocab)
print(f'Total Words: {total_occurrences}')
print('=' * 40)

JPDB_freq = "./JPDB_term_meta_bank_1.json"

all_vocab = sorted(sorted_occurences, key=lambda x: x[1], reverse=True)

new_frequencies = {word: i + 1 for i, (word, _) in enumerate(all_vocab)}

with open(JPDB_freq, 'r', encoding='utf-8') as file:
    jpdb_data = json.load(file)

filtered_data = []
for item in jpdb_data:
    word = item[0]
    if word in new_frequencies:
        filtered_data.append(item)

def update_frequencies(data, freq_dict):
    for item in data:
        word = item[0]
        reading = item[2].get('reading') if 'reading' in item[2] else None
        if word in freq_dict:
            freq = freq_dict[word]
        elif reading in freq_dict:
            freq = freq_dict[reading]
        else:
            continue
        
        if 'frequency' in item[2]:
          item[2]['frequency'] = {
              'value': freq,
              'displayValue': f"{freq}㋕"
          }

update_frequencies(filtered_data, new_frequencies)
sorted_data = sorted(filtered_data, key=lambda x: x[2]['frequency']['value'] if 'frequency' in x[2] else x[2]['value'])
print('Assigned proper frequencies')
print('=' * 40)

print('Deleting duplicates...')
unique_data = []
delete_counter = 0
for i in range(len(sorted_data)):
    is_duplicate = False
    for j in range(i + 1, len(sorted_data)):
        if sorted_data[i] == sorted_data[j]:
            is_duplicate = True
            delete_counter += 1
            if (delete_counter % 1000 == 0):
                print(f'Deleted {delete_counter} duplicates')
            break
    if not is_duplicate:
        unique_data.append(sorted_data[i])

print(f"Successfully removed {delete_counter} duplicates!")
print('=' * 40)

print(f'Total Unique Words: {len(unique_data)}')
print('=' * 40)

print('Fixing freq sequences...')
def find_occurrence(word):
    for item in sorted_occurences:
        if item[0] == word:
            return item[1]
    return None

unique_data.sort(key=lambda x: x[2]['frequency']['value'] if 'frequency' in x[2] else x[2]['value'])

for index, term in enumerate(unique_data):
    freq_value = find_occurrence(term[0])
    if 'frequency' in term[2]:
        term[2]['frequency']['displayValue'] = f"{freq_value}"
    else:
        term[2]['displayValue'] = f"{freq_value}"

unique_data.sort(key=lambda x: (int(x[2]['frequency']['displayValue']) if 'frequency' in x[2] else int(x[2]['displayValue'])), reverse=True)

for index, term in enumerate(unique_data):
    freq_value = find_occurrence(term[0])
    if 'frequency' in term[2]:
        term[2]['frequency']['value'] = index + 1
    else:
        term[2]['value'] = index + 1

print('Fixed term sequences!')
print('=' * 40)

print(f'Generating zip file named {ocr_parent_name}.zip')
print('=' * 40)

index_data = {
    "title": ocr_parent_name,
    "format": 3,
    "revision": "1",
    "sequenced": False,
    "author": "zehdi",
    "description": "x_occurences.",
    "weight": 4
}

archive_name = f"{ocr_parent_name}.zip"

with zipfile.ZipFile(archive_name, 'w') as zipf:
    with zipf.open('index.json', 'w') as index_file:
        index_file.write(json.dumps(index_data, indent=4).encode('utf-8'))
    
    with zipf.open('term_meta_bank_1.json', 'w') as term_meta_file:
        term_meta_file.write(json.dumps(unique_data, ensure_ascii=False, indent=4).encode('utf-8'))

print(f"Archived term_meta_bank_1.json and index.json into {archive_name}.")
