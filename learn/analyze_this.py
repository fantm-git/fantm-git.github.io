import configparser
from typing import Dict, Any

# --- Helper Function (Remains the same) ---
def get_missing_variable(code: str, known_vars: Dict[str, Any]) -> str | None:
    """Attempts to execute the code to find the first NameError."""
    temp_scope = known_vars.copy()
    try:
        exec(code, temp_scope)
        return None
    except NameError as e:
        error_name = str(e).split("'")[1]
        return error_name
    except Exception as e:
        # Ignore other errors for the purpose of finding NameErrors
        return None

# --- Main Logic (Updated) ---
def process_code_and_configure(file_path: str, config_file: str = 'script_config.ini'):
    """
    Main function to process the code, load existing config, 
    and prompt for missing values.
    """
    with open(file_path, 'r') as f:
        code_to_run = f.read()

    config = configparser.ConfigParser()
    config['DEFAULT'] = {}
    
    # 1. Load Existing Configuration
    # This reads the existing file if it exists, populating the config object.
    files_read = config.read(config_file)
    
    if files_read:
        print(f"Loaded existing configuration from **{config_file}**.")
    else:
        print(f"**{config_file}** not found. Starting with a blank configuration.")

    # Use the loaded values (or empty dict if file didn't exist) to initialize the scope
    # config.defaults() returns a dictionary of the DEFAULT section items
    current_scope: Dict[str, Any] = dict(config.defaults())
    config_values = config['DEFAULT'] # Reference to the section being updated
    
    print(f"--- Analyzing '{file_path}' ---")

    while True:
        # 2. Try to find the next missing variable
        missing_var = get_missing_variable(code_to_run, current_scope)

        if not missing_var:
            print("\n✅ All necessary variables are defined. Configuration complete.")
            break

        print(f"\n❓ Unknown variable detected: **{missing_var}**")

        # 3. Check for Existing Value in Config
        existing_value = config_values.get(missing_var)
        
        if existing_value and existing_value.strip() != "":
            # Priority 1: Existing, Non-Empty Value from INI file
            value = existing_value
            print(f"-> Using existing config value for '{missing_var}': **{value}**")
        else:
            # Priority 2: Prompt User for a New Value
            if existing_value == "":
                 print("-> Existing value is empty, prompting for new value.")
            
            # Prompt the user
            user_input = input(f"Enter a value for '{missing_var}' (or 'SKIP' to halt): ")
            if user_input.upper() == 'SKIP':
                print("Execution halted by user.")
                return
            
            # Simple attempt to evaluate input as a Python literal 
            try:
                value = eval(user_input)
            except:
                value = user_input

        # 4. Assign the value and update scope
        config_values[missing_var] = str(value) # Store as string in ConfigParser
        current_scope[missing_var] = value      # Store actual type (if evaluated) in scope

    # 5. Write the (potentially updated) configuration file
    with open(config_file, 'w') as f:
        config.write(f)

    print(f"\n💾 Configuration written to **{config_file}**.")

# --- Example Setup ---
# 1. Create a dummy Python file
dummy_code = """
# script_config.ini should provide values for UNKNOWN_VAR and API_KEY
result = 100 * UNKNOWN_VAR
final_message = f"API: {API_KEY}"
print(result)
print(final_message)
"""
with open('target_script.py', 'w') as f:
    f.write(dummy_code)

# 2. Create an initial config file with some values and one empty one
#initial_config = configparser.ConfigParser()
#initial_config['DEFAULT'] = {
#    'UNKNOWN_VAR': '25', # This will be used
#    'API_KEY': '',       # This is empty, so the script will prompt the user
#}
#with open('script_config.ini', 'w') as f:
#    initial_config.write(f)

# 3. Run the process
print("--- FIRST RUN (Should load 25, prompt for API_KEY) ---")
process_code_and_configure('target_script.py')
