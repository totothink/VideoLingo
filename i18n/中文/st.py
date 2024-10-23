import streamlit as st
import os, sys
from st_components.imports_and_utils import *
from core.config_utils import load_key

# 设置路径
current_dir = os.path.dirname(os.path.abspath(__file__))
os.environ['PATH'] += os.pathsep + current_dir
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="VideoLingo", page_icon="st_components/icon.png")

def text_processing_section():
    st.header("翻译和生成字幕")
    with st.container(border=True):
        st.markdown("""
        <p style='font-size: 20px;'>
        这个阶段包括以下步骤：
        <p style='font-size: 20px;'>
            1. WhisperX 词级转录<br>
            2. 使用 NLP 和 LLM 进行句子分割<br>
            3. 摘要和多步翻译<br>
            4. 切割和对齐长字幕<br>
            5. 生成时间轴和字幕<br>
            6. 将字幕合并到视频中
        """, unsafe_allow_html=True)

        if not os.path.exists("output/output_video_with_subs.mp4"):
            if st.button("开始处理字幕", key="text_processing_button"):
                process_text()
                st.rerun()
        else:
            st.success("字幕翻译完成！建议下载 srt 文件并自行处理。")
            if load_key("resolution") != "0x0":
                st.video("output/output_video_with_subs.mp4")
            download_subtitle_zip_button(text="下载所有字幕")
            
            if st.button("归档到 'history'", key="cleanup_in_text_processing"):
                cleanup()
                st.rerun()
            return True

def process_text():
    with st.spinner("使用 Whisper 进行转录..."):
        step2_whisper.transcribe()
    with st.spinner("分割长句..."):  
        step3_1_spacy_split.split_by_spacy()
        step3_2_splitbymeaning.split_sentences_by_meaning()
    with st.spinner("摘要和翻译..."):
        step4_1_summarize.get_summary()
        if load_key("pause_before_translate"):
            input("⚠️ 翻译前暂停。请前往 `output/log/terminology.json` 编辑术语。然后按回车键继续...")
        step4_2_translate_all.translate_all()
    with st.spinner("处理和对齐字幕..."): 
        step5_splitforsub.split_for_sub_main()
        step6_generate_final_timeline.align_timestamp_main()
    with st.spinner("将字幕合并到视频..."):
        step7_merge_sub_to_vid.merge_subtitles_to_video()
    
    st.success("字幕处理完成！🎉")
    st.balloons()

def audio_processing_section():
    st.header("配音（测试版）")
    with st.container(border=True):
        st.markdown("""
        <p style='font-size: 20px;'>
        这个阶段包括以下步骤：
        <p style='font-size: 20px;'>
            1. 生成音频任务<br>
            2. UVR5 处理<br>
            3. 生成音频<br>
            4. 将音频合并到视频中
        """, unsafe_allow_html=True)
        if not os.path.exists("output/output_video_with_audio.mp4"):
            if st.button("开始音频处理", key="audio_processing_button"):
                process_audio()
                st.rerun()
        else:
            st.success("音频处理完成！您可以在 `output` 文件夹中查看音频文件。")
            if load_key("resolution") != "0x0": 
                st.video("output/output_video_with_audio.mp4") 
            if st.button("删除配音文件", key="delete_dubbing_files"):
                delete_dubbing_files()
                st.rerun()
            if st.button("归档到 'history'", key="cleanup_in_audio_processing"):
                cleanup()
                st.rerun()

def process_audio():
    with st.spinner("生成音频任务"): 
        step8_gen_audio_task.gen_audio_task_main()
    with st.spinner("UVR5 处理"):
        step9_uvr_audio.uvr_audio_main()
    with st.spinner("生成音频"):
        step10_gen_audio.process_sovits_tasks()
    with st.spinner("将音频合并到视频中"):
        step11_merge_audio_to_vid.merge_main()
    
    st.success("音频处理完成！🎇")
    st.balloons()

def main():
    logo_col, _ = st.columns([2,1])
    with logo_col:
        st.image("docs/logo.png", use_column_width=True)
    st.markdown(button_style, unsafe_allow_html=True)
    st.markdown("<p style='font-size: 20px; color: #808080;'>您好，感谢访问 VideoLingo。本项目目前正在建设中。如果遇到任何问题，请随时在 Github 上提问！您也可以访问我们的网站：<a href='https://videolingo.io' target='_blank'>videolingo.io</a></p>", unsafe_allow_html=True)
    # 添加设置
    with st.sidebar:
        page_setting()
        st.markdown(give_star_button, unsafe_allow_html=True)
    download_video_section()
    text_processing_section()
    audio_processing_section()

if __name__ == "__main__":
    main()
