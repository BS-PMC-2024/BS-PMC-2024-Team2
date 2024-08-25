Installation Steps:
1.	Clone the Repository: Start by cloning the project repository from GitHub:
git clone https://github.com/username/Cover.git
cd Cover
2.	Set Up the Virtual Environment: Create and activate a virtual environment to manage Python dependencies:
python3 -m venv venv
source venv/bin/activate
3.	Install Dependencies: Install the required Python packages:
pip install -r requirements.txt
4.	Configure the Database: Set up MongoDB and configure the database settings in the .env file.
MONGODB_URI=mongodb://localhost:27017
5.	Run the Application: Start the application server:
python app.py



