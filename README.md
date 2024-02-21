### OpenPlugin

Please see the complete documentation here: https://openplugin.org/

#### Summary:

# Using Project
python openplugin/main.py --help

python openplugin/main.py run-plugin --openplugin manifests/sample_klarna.json --prompt sample_prompt.txt --log-level="FLOW"

python openplugin/main.py run-plugin --openplugin manifests/sample_klarna.json --prompt "show me some t shirts" --log-level="INFO"

# Using PIP
pip install openplugin
openplugin --help