import pandas as pd
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
from core.ask_gpt import ask_gpt
from core.prompts_storage import get_subtitle_trim_prompt
from core.config_utils import load_key  
from rich.panel import Panel
from rich.console import Console
from rich import print as rprint

console = Console()
speed_factor = load_key("speed_factor")

# 评估文本配音时长
def estimate_duration(text):
    multiplier = 1
    # Define speech speed: characters/second or words/second, punctuation/second
    speed_zh_ja = 4 * multiplier  # Chinese and Japanese characters per second
    speed_en_and_others = 3 * multiplier   # Words per second for English and other languages
    speed_punctuation = 4 * multiplier   # Punctuation marks per second

    # Count characters, words, and punctuation for each language
    chinese_japanese_chars = len(re.findall(r'[\u4e00-\u9fff\u3040-\u30ff\u3400-\u4dbf\uf900-\ufaff\uff66-\uff9f]', text))
    en_and_others_words = len(re.findall(r'\b[a-zA-ZàâçéèêëîïôûùüÿñæœáéíóúüñÁÉÍÓÚÜÑàèéìíîòóùúÀÈÉÌÍÎÒÓÙÚäöüßÄÖÜа-яА-Я]+\b', text))
    punctuation_count = len(re.findall(r'[,.!?;:，。！？；：](?=.)', text))    

    # Estimate duration for each language part and punctuation
    chinese_japanese_duration = chinese_japanese_chars / speed_zh_ja
    en_and_others_duration = en_and_others_words / speed_en_and_others
    punctuation_duration = punctuation_count / speed_punctuation
    
    # Total estimated duration
    estimated_duration = chinese_japanese_duration + en_and_others_duration + punctuation_duration
    
    return estimated_duration


def adjust_translate_by_duration():
    translation_results_file = "output/log/translation_results.xlsx"
    if os.path.exists(translation_results_file):
        df = pd.read_excel(translation_results_file)

        for index, row in df.iterrows():
           translation = row['Translation']
           duration = row['duration']
           if duration is not None and translation is not None:
               estimated_duration = estimate_duration(translation)
               if duration < estimated_duration:
                    prompt = get_subtitle_trim_prompt(translation, duration)
                    def valid_trim(response):
                       if 'trans_text_processed' not in response:
                           return {'status': 'error', 'message': 'No trans_text_processed in response'}
                       return {'status': 'success', 'message': ''}
                    try:
                       response = ask_gpt(prompt, response_json=True, log_title='translation_trim', valid_def=valid_trim)
                       adjusted_translation = response['trans_text_processed']
                    except Exception:
                        rprint("[bold red]🚫 AI refused to answer due to sensitivity, so manually remove punctuation[/bold red]")
                        adjusted_translation = re.sub(r'[,.!?;:，。！？；：]', ' ', translation).strip()
                    
                    rprint(Panel(f"Translation: {translation}\n Translation after shortening: {adjusted_translation}", title="Translation Shortening Result", border_style="green"))
                    df.at[index, 'Translation'] = adjusted_translation

        df.to_excel(translation_results_file, index=False)
        console.print("[bold green]✅ Translation adjustment completed![/bold green]")
    else:
        console.print("[yellow]🚨 File `translation_results.xlsx` not found, skipping this step.[/yellow]")

    

if __name__ == "__main__":
    adjust_translate_by_duration()