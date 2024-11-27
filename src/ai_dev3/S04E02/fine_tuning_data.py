from ai_dev3.utils.files import read_as_text, save_text_to_file

line = '{{"messages": [{{"role": "system", "content": "S04EO2_Custom_Classification"}}, {{"role": "user", "content": "{user}"}}, {{"role": "assistant", "content": "{assistant}"}}]}}'


def fine_tuning_data():
    correct_items = read_as_text("data/correct.txt").splitlines()
    dataset = [line.format(user=item, assistant="OK") for item in correct_items]
    incorrect_items = read_as_text("data/incorrect.txt").splitlines()
    dataset += [line.format(user=item, assistant="ERROR") for item in incorrect_items]
    save_text_to_file("\n".join(dataset), "data/fine-tuning.jsonl")


if __name__ == "__main__":
    fine_tuning_data()
