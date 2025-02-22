# Ranking Model

## Overview

The **Ranking Model** repository is a machine learning project developed to address the AiHello Hackathon Challenge. It focuses on building a model that ranks candidates based on specific criteria, leveraging advanced algorithms and data processing techniques.

## Features

- **Data Processing**: Scripts and tools for cleaning and preparing data for modeling.
- **Model Training**: Implementation of machine learning models to rank candidates effectively.
- **API Integration**: Endpoints to access the model's predictions programmatically.
- **Visualization**: Notebooks and scripts for visualizing data and model performance.

## Repository Structure

- `data/`: Contains datasets used for training and evaluation.
- `model/`: Includes trained models and related assets.
- `notebooks/`: Jupyter notebooks for exploratory data analysis and model development.
- `src/`: Source code for data processing and model implementation.
- `api/`: Flask application providing API endpoints for model inference.
- `requirements.txt`: List of dependencies required to run the project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/isatyamks/ranking_model.git
   cd ranking_model
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   - Create a `.env` file in the root directory.
   - Add necessary environment variables as specified in the project documentation.

### Usage

- **Data Processing**:
  - Run data preprocessing scripts located in the `src/` directory to prepare the dataset.

- **Model Training**:
  - Use the notebooks in the `notebooks/` directory to train and evaluate models.

- **API Deployment**:
  - Navigate to the `api/` directory and run the Flask application:
    ```bash
    python app.py
    ```
  - Access the API endpoints as documented to get model predictions.

## Related Repositories

- **Frontend Repository**: [Frontend Interface](https://github.com/shaurya-bajpai/Nexux)
  - A web-based interface allowing users to interact with the ranking model seamlessly.

- **Backend Repository**: [Backend Services](https://github.com/anmol420/nexux_backend)
  - Handles data management, authentication, and integrates with the ranking model API.

These repositories collectively form the complete application, providing a user-friendly frontend, a robust backend, and the machine learning ranking model.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure that your code adheres to the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

For any questions or support, please open an issue in this repository.

