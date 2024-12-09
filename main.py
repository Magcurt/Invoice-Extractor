import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
global empty_df

# openai_api_key = os.getenv('OPENAI_API_KEY')
# genai.configure(api_key=openai_api_key)

st.set_page_config(page_title="Invoice Extractor")
st.title("Gen AI Invoice Extraction")
uploaded_files = st.file_uploader("Choose PDF files",
                                  accept_multiple_files=True,
                                   type=["pdf", "jpg"])
if uploaded_files:
    if st.button('Extract'):
        image_bytes = pdf_to_image(uploaded_files)
        all_texts = []
        for image_byte in image_bytes:
            print('This is image_byte: ', image_bytes)

            combine_text = ''
            for image_bits in image_byte:
                print('This is image bits goes into image_to_text: -----', image_bits)
                text = image_to_text(image_bits)
                combine_text += text
            print('This is the text from single PDF: ', combine_text)
            all_texts.append(combine_text)

        empty_df = pd.DataFrame()

        for text in all_texts:
            extracted_text = extractor(text)
            task_details_dict = extracted_text.dict()
            df = pd.DataFrame([task_details_dict])
            empty_df = pd.concat([empty_df, df])

        st.write(empty_df)
        csv = empty_df.to_csv(index=False)
        st.download_button(
            label='Click to Download CSV',
            data=csv,
            file_name='Extracted_data.csv',
            mime='text/csv',
        )
