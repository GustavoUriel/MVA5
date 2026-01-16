# 2601161350-attribute_discarding_policy.md

## Summary
Implemented the Attribute Discarding Policy feature based on the architecture document `210.AttributeDiscarding.md`. This feature allows users to configure various filtering methods for microbial taxa based on data quality criteria.

## Changes Made

### 1. Metadata File Created
- **File**: `metadata/ATTRIBUTE_DISCARDING.py`
- **Content**: Defined 10 discarding policies including:
  - Prevalence Filtering
  - Abundance Filtering  
  - Variance-Based Selection
  - Univariate PFS Screening
  - Multivariate PFS Screening
  - Stability Selection
  - Information-Theoretic Selection
  - Boruta Algorithm
  - Elastic Net Regularization
  - Combined Multi-Method Selection
- **Parameters**: Each policy includes configurable parameters with defaults, min/max values, and descriptions

### 2. Backend API Endpoints Added
- **File**: `app/modules/datasets/datasets_bp.py`
- **Endpoints**:
  - `GET /dataset/<dataset_id>/metadata/attribute-discarding`: Returns discarding policies metadata
  - `POST /dataset/<dataset_id>/metadata/attribute-discarding/calculate-remaining`: Placeholder endpoint returning "Calculation of remaining attributes not yet implemented"

### 3. Frontend Template Updated
- **File**: `app/templates/dataset/analysis_config.html`
- **Changes**: Replaced placeholder content in Pre-Analysis tab with collapsible Attribute Discarding Policy card
- **Features**:
  - Collapsible interface matching Attribute Groups Selection style
  - Summary showing enabled policies count
  - "Calculate Remaining" button for future implementation

### 4. JavaScript Functionality Added
- **File**: `app/static/js/dataset_analysis.js`
- **New Methods**:
  - `loadDiscardingPolicies()`: Loads policies from API
  - `displayDiscardingPolicies()`: Renders policy cards with parameter inputs
  - `updateDiscardingPolicySummary()`: Updates summary text and counts
  - `collectDiscardingPolicies()`: Collects enabled policies and parameters for saving
  - `togglePolicyBody()`: Shows/hides parameter sections based on enable/disable
  - `calculateRemainingAttributes()`: Calls calculation API endpoint

- **File**: `app/static/js/dataset_utils.js`
- **New API Method**: `getAttributeDiscarding(datasetId)`: API helper for fetching discarding policies

### 5. Integration Points
- **Analysis Configuration**: Discarding policies are now collected and saved as part of analysis configurations
- **UI Consistency**: Matches the look and feel of existing Attribute Groups Selection
- **Event Handling**: Proper event listeners for policy toggles and parameter changes

## Technical Implementation Details

### Policy Structure
Each discarding policy includes:
- `name`: Display name
- `description`: Detailed explanation
- `parameters`: Configurable settings with types (float, int, select)
- `enabled`: Default enable/disable state
- `order`: Display ordering

### Parameter Types Supported
- **float**: Numeric inputs with min/max/step validation
- **int**: Integer inputs with range validation  
- **select**: Dropdown selections with predefined options

### UI Components
- Collapsible card with header checkbox for enable/disable
- Dynamic parameter input generation based on policy configuration
- Summary badge showing count of enabled policies
- Calculate button for future remaining attributes calculation

## Future Implementation Notes
- The `calculateRemainingAttributes` API endpoint currently returns a placeholder message
- Full implementation would require:
  - Data processing logic for each discarding policy
  - Integration with microbial abundance data
  - Calculation of remaining taxa after applying filters
  - Progress tracking for long-running calculations

## Testing
- UI renders correctly with policy cards
- Enable/disable toggles work properly
- Parameter inputs validate correctly
- Summary updates dynamically
- Configuration saving includes discarding policies
- API endpoints return expected data structures

## Compliance
- Follows existing code patterns and naming conventions
- Maintains consistency with other metadata-driven features
- Uses established UI components and styling
- Includes proper error handling and user feedback