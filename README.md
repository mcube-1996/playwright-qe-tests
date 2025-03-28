# Playwright QE Tests

## Setup Instructions

### Clone the repository
```sh
git clone https://github.com/mcube-1996/playwright-qe-tests.git
cd playwright-qe-tests


#create venv
python3 -m venv venv
# activate venv
source venv/bin/activate # playwright-qe-tests


#install requirements
pip install -r requirements.txt

#change directory to main folder
cd main

#run the code in folder main api_test.py and saucedemo_test.py
python -m api_test
python -m saucedemo_test