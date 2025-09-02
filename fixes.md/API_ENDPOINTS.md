# API Endpoints Documentation

## Table Download API

### Endpoint
```
GET /api/dataset/{dataset_id}/table/{table_type}
```

### Description
Downloads a specific table from a dataset as JSON format. The user must be authenticated and must own the dataset.

### Parameters
- `dataset_id` (integer): The ID of the dataset
- `table_type` (string): The type of table to download. Must be one of:
  - `patients`: Patient demographic and clinical data
  - `taxonomy`: Taxonomic classification data
  - `bracken`: Bracken abundance results data

### Authentication
- **Required**: User must be logged in
- **Authorization**: User must be the owner of the specified dataset

### Response Format

#### Success Response (200)
```json
{
  "success": true,
  "dataset_id": 123,
  "dataset_name": "My Dataset",
  "table_type": "patients",
  "rows": 150,
  "columns": 8,
  "data": [
    {
      "patient_id": "P001",
      "age": 45,
      "gender": "F",
      "race": "Caucasian",
      "ethnicity": "Non-Hispanic"
    },
    // ... more rows
  ]
}
```

#### Error Responses

**404 - Dataset not found or access denied**
```json
{
  "error": "Dataset not found or access denied"
}
```

**400 - Invalid table type**
```json
{
  "error": "Invalid table type. Must be one of: patients, taxonomy, bracken"
}
```

**400 - Table not found in dataset**
```json
{
  "error": "Patients table not found in this dataset"
}
```

**400 - Table not yet processed**
```json
{
  "error": "Patients table is not yet processed"
}
```

**500 - Processing error**
```json
{
  "error": "Failed to process table data",
  "details": "Error message details"
}
```

### Headers
- `Content-Type: application/json`
- `Content-Disposition: attachment; filename="{dataset_name}_{table_type}_table.json"`

### Example Usage

#### Using curl
```bash
# Download patients table from dataset 123
curl -H "Cookie: session=your_session_cookie" \
     "http://localhost:5005/api/dataset/123/table/patients" \
     -o patients_table.json
```

#### Using JavaScript/Fetch
```javascript
fetch('/dataset/123/table/patients', {
  method: 'GET',
  credentials: 'include'  // Include cookies for authentication
})
.then(response => {
  if (response.ok) {
    return response.json();
  }
  throw new Error('Download failed');
})
.then(data => {
  console.log('Table data:', data.data);
  console.log('Rows:', data.rows);
  console.log('Columns:', data.columns);
})
.catch(error => {
  console.error('Error:', error);
});
```

#### Using Python requests
```python
import requests

# Assuming you have a session cookie
session = requests.Session()
session.cookies.set('session', 'your_session_cookie')

response = session.get('http://localhost:5005/api/dataset/123/table/patients')

if response.status_code == 200:
    data = response.json()
    print(f"Downloaded {data['rows']} rows with {data['columns']} columns")
    print("First row:", data['data'][0])
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### Security Features
1. **Authentication Required**: Users must be logged in to access the endpoint
2. **Authorization Check**: Only dataset owners can download their tables
3. **Input Validation**: Table type is validated against allowed values
4. **File Existence Check**: Verifies that the requested table file exists and is processed
5. **Comprehensive Logging**: All access attempts and errors are logged for audit purposes

### Performance Considerations
- Large tables may take time to process and return
- The endpoint reads CSV files and converts them to JSON on-the-fly
- Consider implementing pagination for very large datasets in future versions

### Related Endpoints
- `GET /dataset/{dataset_id}` - View dataset details
- `GET /dataset/{dataset_id}/data-stats` - Get dataset statistics
- `GET /dataset/{dataset_id}/files` - List dataset files
