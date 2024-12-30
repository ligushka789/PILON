import streamlit as st
import pandas as pd
from difflib import SequenceMatcher

# Made by Roman Gribanov
class checker:
    def __init__(self):
        pass

    def app(self):
        st.title("Сравнение двух документов (Формат CSV)")
        st.subheader("Загрузите два документа, выберите колонки для сравнения и сопоставления.")

        def load_csv(file):
            try:
                return pd.read_csv(file)
            except Exception as e:
                st.error(f"Ошибка при чтении файла: {e}")
                return None

        # File upload for two CSV files
        file1 = st.file_uploader("Документ 1", type="csv")
        file2 = st.file_uploader("Документ 2", type="csv")

        if file1 and file2:
            # Load the CSV files
            df1 = load_csv(file1)
            df2 = load_csv(file2)

            if df1 is not None and df2 is not None:
                # Use columns to display dataframes side-by-side
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Документ 1")
                    st.dataframe(df1, height=300)

                with col2:
                    st.subheader("Документ 2")
                    st.dataframe(df2, height=300)

                # Dropdown to select text columns for comparison
                col1_selection, col2_selection = st.columns(2)

                with col1_selection:
                    col1_name = st.selectbox("Колонка для текстового сравнения из Документа 1", df1.columns)

                with col2_selection:
                    col2_name = st.selectbox("Колонка для текстового сравнения из Документа 2", df2.columns)

                # Dropdown to select additional columns for display
                additional_col1 = st.selectbox("Дополнительная колонка для отображения из Документа 1", df1.columns)
                additional_col2 = st.selectbox("Дополнительная колонка для отображения из Документа 2", df2.columns)

                if col1_name and col2_name:
                    # Extract the selected columns for text comparison
                    col1_data = df1[col1_name].astype(str)
                    col2_data = df2[col2_name].astype(str)

                    # Extract additional data for display
                    additional_data_1 = df1[[col1_name, additional_col1]].astype(str)
                    additional_data_2 = df2[[col2_name, additional_col2]].astype(str)

                    # Calculate similarity for text columns
                    similarity_results = []
                    unmatched_col1 = set(col1_data)
                    unmatched_col2 = set(col2_data)

                    for idx, val1 in enumerate(col1_data):
                        max_similarity = 0
                        best_match = None
                        match_idx = None
                        for jdx, val2 in enumerate(col2_data):
                            similarity = SequenceMatcher(None, val1, val2).ratio()
                            if similarity > max_similarity:
                                max_similarity = similarity
                                best_match = val2
                                match_idx = jdx

                        if best_match:
                            unmatched_col2.discard(best_match)
                        unmatched_col1.discard(val1)

                        similarity_results.append({
                            "Значение из Документа 1": val1,
                            "Наиболее схожее значение из Документа 2": best_match,
                            "Схожесть": max_similarity,
                            "Доп. данные из Документа 1": additional_data_1.iloc[idx, 1],
                            "Доп. данные из Документа 2": additional_data_2.iloc[match_idx, 1] if match_idx is not None else None
                        })

                    # Add unmatched values from both columns
                    for val1 in unmatched_col1:
                        idx = col1_data[col1_data == val1].index[0]
                        similarity_results.append({
                            "Значение из Документа 1": val1,
                            "Наиболее схожее значение из Документа 2": None,
                            "Схожесть": 0,
                            "Доп. данные из Документа 1": additional_data_1.iloc[idx, 1],
                            "Доп. данные из Документа 2": None
                        })

                    for val2 in unmatched_col2:
                        idx = col2_data[col2_data == val2].index[0]
                        similarity_results.append({
                            "Значение из Документа 1": None,
                            "Наиболее схожее значение из Документа 2": val2,
                            "Схожесть": 0,
                            "Доп. данные из Документа 1": None,
                            "Доп. данные из Документа 2": additional_data_2.iloc[idx, 1]
                        })

                    # Convert results to a DataFrame
                    results_df = pd.DataFrame(similarity_results)
                    results_df["Схожесть"] = results_df["Схожесть"].round(2)

                    # Sort results: high similarity first, low similarity last
                    results_df = results_df.sort_values(by="Схожесть", ascending=False)

                    # Display all results
                    st.subheader("Результаты сравнения")
                    st.dataframe(results_df)

# Launch the app
if __name__ == '__main__':
    checker = checker()
    checker.app()