import streamlit as st
import pandas as pd
import utils
import os

from dotenv import load_dotenv
load_dotenv()

global empty_df


st.set_page_config(page_title="Invoice Extractor")
st.title("Gen AI Invoice Extraction")
uploaded_files = st.file_uploader("Choose PDF files",
                                  accept_multiple_files=True,
                                   type=["pdf", "jpg"])
if uploaded_files:
    if st.button('Extract'):
        image_bytes = utils.pdf_to_image(uploaded_files)

        all_texts = []
        for image_byte in image_bytes:
            print('This is image_byte: ', image_bytes)

            combine_text = ''
            for image_bits in image_byte:
                print('This is image bits goes into image_to_text: -----', image_bits)
                text = utils.image_to_text(image_bits)
                combine_text += text
            print('This is the text from single PDF: ', combine_text)
            all_texts.append(combine_text)

        empty_df = pd.DataFrame()

        for text in all_texts:
            try:
                json_data = utils.structured_extract(text)
                df = pd.DataFrame([json_data])
                empty_df = pd.concat([empty_df, df])
            except Exception as e:
                print('This is the error: ', e)
            continue

        st.write(empty_df)
        csv = empty_df.to_csv(index=False)
        st.download_button(
            label='Click to Download CSV',
            data=csv,
            file_name='Extracted_data.csv',
            mime='text/csv',
        )