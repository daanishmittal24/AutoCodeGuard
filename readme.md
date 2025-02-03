# 🚀 AutoCodeGuard - Automated Custom Code Testing for Hackathons

## 🎯 Project Overview
AutoCodeGuard is an automated testing platform for evaluating coding solutions submitted in hackathons. It verifies coding guidelines, checks performance, and provides structured feedback to participants. No Docker is required for execution.

## 📌 Features
- 🛠 **Automated Code Verification**: Checks for adherence to predefined coding guidelines.
- ⚡ **Performance Evaluation**: Measures efficiency and execution time.
- ✅ **Custom Linting Rules**: Enforces coding standards using linters.
- 📊 **Automated Scoring**: Assigns scores based on correctness, efficiency, and readability.
- ☁ **GitHub Deployment Support**: Submissions must be pushed to GitHub for evaluation.
- 💾 **MongoDB Integration**: Stores user submissions and results.


## 🔧 Setup & Installation
### 1️⃣ Clone the Repository
```sh
git clone https://github.com/daanishmittal24/AutoCodeGuard.git
cd AutoCodeGuard
```

### 2️⃣ Install Dependencies
For Python:
```sh
pip install -r requirements.txt
```
For JavaScript:
```sh
npm install
```

### 3️⃣ Setup Pre-commit Hooks
```sh
pre-commit install
```

### 4️⃣ Run Linter Checks
For Python:
```sh
pylint src/
flake8 src/
```
For JavaScript:
```sh
eslint src/ --fix
```

### 5️⃣ Start Evaluation Engine
```sh
python src/main.py
```

## 🔬 Evaluation Criteria
1. **Coding Guidelines** - Code must adhere to predefined standards (e.g., PEP8 for Python, ESLint rules for JavaScript).
2. **Execution Efficiency** - Code should run within an optimal time and memory limit.
3. **Code Quality** - Readability, maintainability, and documentation.
4. **Correctness** - Code should produce expected outputs for test cases.
5. **Security** - No unauthorized file access or security risks.

## 📜 Custom Linter Configuration
### Python Linter (`.pylintrc`)
```ini
[MESSAGES CONTROL]
disable=missing-docstring,invalid-name

[FORMAT]
max-line-length=100
```

### JavaScript Linter (`.eslintrc.json`)
```json
{
  "rules": {
    "indent": ["error", 4],
    "quotes": ["error", "double"],
    "semi": ["error", "always"]
  }
}
```

## 🚀 Future Enhancements
- ✅ Add support for more programming languages.
- 🔗 Integrate with GitHub Actions for CI/CD.
- 🏆 Leaderboard system for ranking participants.

## 📄 License
This project is licensed under the MIT License.

## 👨‍💻 Contributors
- **[Your Name]** - Project Lead
- **[Other Contributors]**

---
⚡ **AutoCodeGuard** - Ensuring Quality Code, Every Submission!
