import streamlit as st
import json

def compare_json(json1, json2, path=""):
    """Compare two JSON objects and return the missing keys and differing values in both."""
    missing_in_json1 = []
    missing_in_json2 = []
    differing_values = []

    for key in json1:
        if key not in json2:
            missing_in_json2.append(f"{path}/{key}")
        elif isinstance(json1[key], dict) and isinstance(json2[key], dict):
            sub_missing1, sub_missing2, sub_diffs = compare_json(json1[key], json2[key], path=f"{path}/{key}")
            missing_in_json1.extend(sub_missing1)
            missing_in_json2.extend(sub_missing2)
            differing_values.extend(sub_diffs)
        elif json1[key] != json2[key]:
            differing_values.append(f"{path}/{key}: {json1[key]} != {json2[key]}")

    for key in json2:
        if key not in json1:
            missing_in_json1.append(f"{path}/{key}")

    return missing_in_json1, missing_in_json2, differing_values

def prettify_json(json_str):
    try:
        parsed_json = json.loads(json_str)
        # Sort keys and use an indentation of 4 for the prettified JSON
        prettified_json = json.dumps(parsed_json, indent=4, sort_keys=True)
        return True, prettified_json
    except json.JSONDecodeError as e:
        return False, str(e)

def main():
    st.title("JSON Comparator")

    col1, col2 = st.columns(2)
    
    with col1:
        # Note the unique key for the text area
        json_str1 = st.text_area("Paste JSON 1", height=300, key="json_input_1")
        
    with col2:
        # Note the unique key for the text area
        json_str2 = st.text_area("Paste JSON 2", height=300, key="json_input_2")

    if st.button('Prettify & Check Syntax'):
        success1, result1 = prettify_json(json_str1)
        success2, result2 = prettify_json(json_str2)

        if success1:
            st.session_state['prettified_json1'] = result1  # Use unique session state key
        else:
            st.error(f"JSON 1 Syntax Error: {result1}")
        
        if success2:
            st.session_state['prettified_json2'] = result2  # Use unique session state key
        else:
            st.error(f"JSON 2 Syntax Error: {result2}")

        if success1 and success2:
            st.success("Both JSON inputs are valid and have been prettified.")

    if st.button('Compare'):
        if 'prettified_json1' in st.session_state and 'prettified_json2' in st.session_state:
            try:
                json1 = json.loads(st.session_state['prettified_json1'])
                json2 = json.loads(st.session_state['prettified_json2'])

                missing_in_json1, missing_in_json2, differing_values = compare_json(json1, json2)

                if missing_in_json1 or missing_in_json2 or differing_values:
                    if missing_in_json1:
                        with st.expander("Missing in JSON 1"):
                            for item in missing_in_json1:
                                st.markdown(f"- `{item}`")
                    
                    if missing_in_json2:
                        with st.expander("Missing in JSON 2"):
                            for item in missing_in_json2:
                                st.markdown(f"- `{item}`")
                    
                    if differing_values:
                        with st.expander("Differing Values"):
                            for item in differing_values:
                                st.markdown(f"- `{item}`")
                else:
                    st.success("No missing attributes or differing values found!")
            except json.JSONDecodeError:
                st.error("An unexpected error occurred while comparing JSONs.")
        else:
            st.error("Please prettify & check syntax before comparing.")

if __name__ == "__main__":
    main()
