# AutoVal
An interactive full-stack web application that uses machine learning to estimate second-hand vehicle market values and visualizes comparative price trends.

---

## 💻 How to Run Locally

### Prerequisite
Make sure you have **Python 3** installed on your computer. You can check by running `python --version` in your terminal.

### 🐍 1. Start the Backend Server
1. Open your terminal and navigate into the backend folder:
    ```
   cd backend
    ```   
2. Install the required backend dependencies (only need to do this the first time):
    ```   
   pip install -r requirements.txt
    ```   
3. Boot up the local server by running:
    ```   
   python -m uvicorn app:app --reload
    ```   
   *Keep this terminal open! If you close it, the backend server turns off.*
   *(You can verify it's working by going to http://127.0.0.1:8000/docs in your browser.)*

### 🌐 2. Launch the Frontend UI
1. Open your project workspace in VS Code.
2. Navigate to the `frontend` folder and find `index.html`.
3. Right-click `index.html` and select **Open with Live Server** (or Five Server and if you dont see either, install them in vscode extensions).
4. Fill out the car attributes in the form and hit estimate.

> ⚠️ **Note:** The backend server must be active in your terminal before launching the frontend, otherwise the app won't be able to process estimations or generate the depreciation charts.