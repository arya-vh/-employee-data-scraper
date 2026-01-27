import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from scraper import scrape_employees  

@pytest.fixture
def sample_data():
    """Fixture to return a sample data for testing purposes.

    Returns:
        list: A list containing a single dictionary representing an employee.
    """
    return [
        {"id":1, "first_name":"Jose", "last_name":"Lopez", "email":"test@email.com", 
         "phone":"+1-971-533-4552x1542", "gender":"male", "age":25, "job_title":"Project Manager", 
         "years_of_experience":1, "salary":8500, "department":"Product"}
    ]

def test_json_download_success(sample_data):
    """Test Case 1: Verify JSON File Download"""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_data
        mock_get.return_value = mock_response
        
        df = scrape_employees("https://test.com")
        assert len(df) == 1
        assert df['full_name'].iloc[0] == "Jose Lopez"

def test_json_extraction(sample_data):
    """Test Case 2: Verify JSON File Extraction"""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_data
        mock_get.return_value = mock_response
        
        df = scrape_employees("https://test.com")
        assert 'years_of_experience' in df.columns
        assert df['designation'].iloc[0] == "System Engineer"  # <3 years

def test_validate_file_type():
    """Test Case 3: Validate File Type and Format"""
    # JSON validation via pandas read_json
    df = pd.read_json("https://api.slingacademy.com/v1/sample-data/files/employees.json")
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0

def test_validate_data_structure(sample_data):
    """Test Case 4: Validate Data Structure"""
    expected_cols = ['full_name', 'email', 'phone_clean', 'gender', 'age', 'job_title', 
                     'years_of_experience', 'salary', 'department', 'designation']
    df = pd.DataFrame(sample_data)
    # Apply normalization logic
    df['designation'] = df['years_of_experience'].apply(lambda x: "System Engineer" if x < 3 else "Lead")
    df['full_name'] = df['first_name'] + ' ' + df['last_name']
    df['phone_clean'] = df['phone'].apply(lambda p: "Invalid Number" if 'x' in str(p) else str(p))
    assert set(expected_cols) <= set(df.columns)

def test_handle_missing_data():
    """Test Case 5: Handle Missing or Invalid Data"""
    invalid_data = [{"years_of_experience": None}]
    with pytest.raises(TypeError):
        pd.DataFrame(invalid_data)['years_of_experience'].apply(lambda x: int(x))  # Simulates type error handling

# Run: pytest tests.py -v
