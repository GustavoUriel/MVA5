# JavaScript Function Map for Dashboard

This document provides a comprehensive map of all JavaScript functions that are or might be called in the dashboard, including their file locations and line numbers.

## Dashboard-Specific Functions (`app/static/js/dashboard.js`)

### Class Definition
- **`DashboardManager`** - Line 4
  - **Location**: `app/static/js/dashboard.js:4`
  - **Type**: Class
  - **Purpose**: Main dashboard management class

### Constructor and Initialization
- **`constructor()`** - Line 5
  - **Location**: `app/static/js/dashboard.js:5`
  - **Type**: Constructor
  - **Purpose**: Initialize dashboard manager properties

- **`init()`** - Line 14
  - **Location**: `app/static/js/dashboard.js:14`
  - **Type**: Method
  - **Purpose**: Initialize dashboard functionality

### View Management
- **`setupViewToggle()`** - Line 25
  - **Location**: `app/static/js/dashboard.js:25`
  - **Type**: Method
  - **Purpose**: Setup grid/list view toggle functionality

- **`setupGlobalFunctions()`** - Line 46
  - **Location**: `app/static/js/dashboard.js:46`
  - **Type**: Method
  - **Purpose**: Setup global functions for dataset deletion

### Dataset Deletion Functions
- **`showDeleteConfirmation(datasetId, datasetName)`** - Line 62
  - **Location**: `app/static/js/dashboard.js:62`
  - **Type**: Method
  - **Purpose**: Show delete confirmation modal

- **`checkDeleteConfirmation()`** - Line 111
  - **Location**: `app/static/js/dashboard.js:111`
  - **Type**: Method
  - **Purpose**: Validate delete confirmation input

- **`deleteDataset()`** - Line 125
  - **Location**: `app/static/js/dashboard.js:125`
  - **Type**: Async Method
  - **Purpose**: Execute dataset deletion

- **`resetDeleteButton()`** - Line 207
  - **Location**: `app/static/js/dashboard.js:207`
  - **Type**: Method
  - **Purpose**: Reset delete button to original state

### Utility Functions
- **`updateDashboardStats()`** - Line 216
  - **Location**: `app/static/js/dashboard.js:216`
  - **Type**: Method
  - **Purpose**: Update dashboard statistics

- **`showAlert(message, type)`** - Line 233
  - **Location**: `app/static/js/dashboard.js:233`
  - **Type**: Method
  - **Purpose**: Display alert messages

### Global Window Functions (Exposed by DashboardManager)
- **`window.showDeleteConfirmation`** - Line 48
  - **Location**: `app/static/js/dashboard.js:48`
  - **Type**: Arrow Function
  - **Purpose**: Global access to showDeleteConfirmation

- **`window.checkDeleteConfirmation`** - Line 52
  - **Location**: `app/static/js/dashboard.js:52`
  - **Type**: Arrow Function
  - **Purpose**: Global access to checkDeleteConfirmation

- **`window.deleteDataset`** - Line 56
  - **Location**: `app/static/js/dashboard.js:56`
  - **Type**: Arrow Function
  - **Purpose**: Global access to deleteDataset

- **`window.DashboardManager`** - Line 264
  - **Location**: `app/static/js/dashboard.js:264`
  - **Type**: Class Export
  - **Purpose**: Export DashboardManager class globally

### Event Listeners
- **`document.addEventListener("DOMContentLoaded", function () { ... })`** - Line 258
  - **Location**: `app/static/js/dashboard.js:258`
  - **Type**: Event Listener
  - **Purpose**: Initialize dashboard when DOM is loaded

## Application-Wide Functions (`app/static/js/app.js`)

### MicrobiomeApp Object Functions
- **`MicrobiomeApp.init()`** - Line 14
  - **Location**: `app/static/js/app.js:14`
  - **Type**: Async Method
  - **Purpose**: Initialize the application

- **`MicrobiomeApp.loadConfiguration()`** - Line 24
  - **Location**: `app/static/js/app.js:24`
  - **Type**: Async Method
  - **Purpose**: Load server configuration

- **`MicrobiomeApp.setupEventListeners()`** - Line 43
  - **Location**: `app/static/js/app.js:43`
  - **Type**: Method
  - **Purpose**: Setup global event listeners

- **`MicrobiomeApp.initializeTooltips()`** - Line 58
  - **Location**: `app/static/js/app.js:58`
  - **Type**: Method
  - **Purpose**: Initialize Bootstrap tooltips

- **`MicrobiomeApp.setupFormValidation()`** - Line 66
  - **Location**: `app/static/js/app.js:66`
  - **Type**: Method
  - **Purpose**: Setup form validation

- **`MicrobiomeApp.setupFlashMessages()`** - Line 81
  - **Location**: `app/static/js/app.js:81`
  - **Type**: Method
  - **Purpose**: Handle flash message auto-dismiss

- **`MicrobiomeApp.setupFormSubmissions()`** - Line 104
  - **Location**: `app/static/js/app.js:104`
  - **Type**: Method
  - **Purpose**: Setup form submissions with loading states

- **`MicrobiomeApp.setupFileUploads()`** - Line 126
  - **Location**: `app/static/js/app.js:126`
  - **Type**: Method
  - **Purpose**: Setup file upload handling

- **`MicrobiomeApp.validateFileUpload(input)`** - Line 137
  - **Location**: `app/static/js/app.js:137`
  - **Type**: Method
  - **Purpose**: Validate file uploads

- **`MicrobiomeApp.setupNavigation()`** - Line 171
  - **Location**: `app/static/js/app.js:171`
  - **Type**: Method
  - **Purpose**: Setup navigation enhancements

- **`MicrobiomeApp.checkAuthStatus()`** - Line 192
  - **Location**: `app/static/js/app.js:192`
  - **Type**: Method
  - **Purpose**: Check authentication status

- **`MicrobiomeApp.showAlert(type, message, dismissible)`** - Line 298
  - **Location**: `app/static/js/app.js:298`
  - **Type**: Method
  - **Purpose**: Show alert messages (global version)

- **`MicrobiomeApp.showLoading(element, text)`** - Line 324
  - **Location**: `app/static/js/app.js:324`
  - **Type**: Method
  - **Purpose**: Show loading spinner

- **`MicrobiomeApp.hideLoading()`** - Line 342
  - **Location**: `app/static/js/app.js:342`
  - **Type**: Method
  - **Purpose**: Hide loading spinner

### MicrobiomeApp.api Object Functions
- **`MicrobiomeApp.api.call(endpoint, options)`** - Line 203
  - **Location**: `app/static/js/app.js:203`
  - **Type**: Async Method
  - **Purpose**: Generic API call method

- **`MicrobiomeApp.api.getDatasets()`** - Line 230
  - **Location**: `app/static/js/app.js:230`
  - **Type**: Async Method
  - **Purpose**: Get user's datasets

- **`MicrobiomeApp.api.createDataset(data)`** - Line 235
  - **Location**: `app/static/js/app.js:235`
  - **Type**: Async Method
  - **Purpose**: Create new dataset

### MicrobiomeApp.utils Object Functions
- **`MicrobiomeApp.utils.formatFileSize(bytes)`** - Line 246
  - **Location**: `app/static/js/app.js:246`
  - **Type**: Method
  - **Purpose**: Format file size

- **`MicrobiomeApp.utils.formatDate(dateString)`** - Line 257
  - **Location**: `app/static/js/app.js:257`
  - **Type**: Method
  - **Purpose**: Format date

- **`MicrobiomeApp.utils.formatDateTime(dateString)`** - Line 267
  - **Location**: `app/static/js/app.js:267`
  - **Type**: Method
  - **Purpose**: Format date and time

- **`MicrobiomeApp.utils.debounce(func, wait)`** - Line 279
  - **Location**: `app/static/js/app.js:279`
  - **Type**: Method
  - **Purpose**: Debounce function

- **`MicrobiomeApp.utils.generateId()`** - Line 292
  - **Location**: `app/static/js/app.js:292`
  - **Type**: Method
  - **Purpose**: Generate random ID

### DatasetManager Object Functions
- **`DatasetManager.refreshDatasets()`** - Line 353
  - **Location**: `app/static/js/app.js:353`
  - **Type**: Async Method
  - **Purpose**: Refresh dataset list

- **`DatasetManager.updateDatasetDisplay(datasets)`** - Line 363
  - **Location**: `app/static/js/app.js:363`
  - **Type**: Method
  - **Purpose**: Update dataset display

- **`DatasetManager.updateGridView(container, datasets)`** - Line 379
  - **Location**: `app/static/js/app.js:379`
  - **Type**: Method
  - **Purpose**: Update grid view

- **`DatasetManager.updateListView(container, datasets)`** - Line 385
  - **Location**: `app/static/js/app.js:385`
  - **Type**: Method
  - **Purpose**: Update list view

### Global Event Listeners
- **`document.addEventListener('DOMContentLoaded', function() { ... })`** - Line 392
  - **Location**: `app/static/js/app.js:392`
  - **Type**: Event Listener
  - **Purpose**: Initialize app when DOM loads

- **`window.addEventListener('popstate', function(event) { ... })`** - Line 419
  - **Location**: `app/static/js/app.js:419`
  - **Type**: Event Listener
  - **Purpose**: Handle browser back/forward buttons

- **`window.addEventListener('online', function() { ... })`** - Line 425
  - **Location**: `app/static/js/app.js:425`
  - **Type**: Event Listener
  - **Purpose**: Handle online status

- **`window.addEventListener('offline', function() { ... })`** - Line 429
  - **Location**: `app/static/js/app.js:429`
  - **Type**: Event Listener
  - **Purpose**: Handle offline status

### Global Exports
- **`window.MicrobiomeApp`** - Line 434
  - **Location**: `app/static/js/app.js:434`
  - **Type**: Global Export
  - **Purpose**: Export MicrobiomeApp globally

- **`window.DatasetManager`** - Line 435
  - **Location**: `app/static/js/app.js:435`
  - **Type**: Global Export
  - **Purpose**: Export DatasetManager globally

## Dataset-Specific Functions (`app/static/js/dataset.js`)

### Global Window Functions (Available if needed)
- **`window.showAlert(message, type)`** - Line 2544
  - **Location**: `app/static/js/dataset.js:2544`
  - **Type**: Function
  - **Purpose**: Show alert messages (dataset version)

- **`window.downloadFile(fileId)`** - Line 2566
  - **Location**: `app/static/js/dataset.js:2566`
  - **Type**: Function
  - **Purpose**: Download file

- **`window.duplicateFile(fileId)`** - Line 2782
  - **Location**: `app/static/js/dataset.js:2782`
  - **Type**: Function
  - **Purpose**: Duplicate file

- **`window.renameFile(fileId, currentName, fileType)`** - Line 2824
  - **Location**: `app/static/js/dataset.js:2824`
  - **Type**: Function
  - **Purpose**: Rename file

- **`window.editTable(fileId)`** - Line 2874
  - **Location**: `app/static/js/dataset.js:2874`
  - **Type**: Function
  - **Purpose**: Edit table

- **`window.cureData(fileId)`** - Line 2879
  - **Location**: `app/static/js/dataset.js:2879`
  - **Type**: Function
  - **Purpose**: Cure data

- **`window.deleteFile(fileId)`** - Line 2919
  - **Location**: `app/static/js/dataset.js:2919`
  - **Type**: Function
  - **Purpose**: Delete file

## Smart Table Functions (`app/static/js/smart_table.js`)

### Global Window Functions (Available if needed)
- **`window.smartTableDepsReady`** - Line 881
  - **Location**: `app/static/js/smart_table.js:881`
  - **Type**: Async Function
  - **Purpose**: Check if smart table dependencies are ready

- **`window.createTableComponent(containerSelector, apiBase, options, title)`** - Line 895
  - **Location**: `app/static/js/smart_table.js:895`
  - **Type**: Async Function
  - **Purpose**: Create table component

- **`window.getModifiedData()`** - Line 3115
  - **Location**: `app/static/js/smart_table.js:3115`
  - **Type**: Function
  - **Purpose**: Get modified data

- **`window.saveToServer()`** - Line 3191
  - **Location**: `app/static/js/smart_table.js:3191`
  - **Type**: Function
  - **Purpose**: Save data to server

## HTML Event Handlers (`app/templates/dashboard.html`)

### onclick Handlers
- **`onclick="showDeleteConfirmation({{ dataset.id }}, '{{ dataset.name }}')"`** - Line 217
  - **Location**: `app/templates/dashboard.html:217`
  - **Type**: HTML onclick
  - **Purpose**: Trigger delete confirmation

- **`onclick="deleteDataset()"`** - Line 296
  - **Location**: `app/templates/dashboard.html:296`
  - **Type**: HTML onclick
  - **Purpose**: Execute dataset deletion

### oninput Handlers
- **`oninput="checkDeleteConfirmation()"`** - Line 289
  - **Location**: `app/templates/dashboard.html:289`
  - **Type**: HTML oninput
  - **Purpose**: Real-time validation of delete input

## Bootstrap Functions (Available via CDN)

### Modal Functions
- **`bootstrap.Modal(element)`** - Used in dashboard for delete confirmation modal
- **`bootstrap.Modal.getInstance(element)`** - Get existing modal instance
- **`modal.show()`** - Show modal
- **`modal.hide()`** - Hide modal

### Alert Functions
- **`bootstrap.Alert(element)`** - Used for auto-dismissing alerts
- **`alert.close()`** - Close alert

### Tooltip Functions
- **`bootstrap.Tooltip(element)`** - Used for tooltips

## Function Call Hierarchy

### Dashboard Initialization Flow
1. **`document.addEventListener("DOMContentLoaded", ...)`** (dashboard.js:258)
2. **`new DashboardManager()`** (dashboard.js:259)
3. **`dashboard.init()`** (dashboard.js:14)
4. **`setupViewToggle()`** (dashboard.js:25)
5. **`setupGlobalFunctions()`** (dashboard.js:46)

### Dataset Deletion Flow
1. **`onclick="showDeleteConfirmation(...)"`** (dashboard.html:217)
2. **`window.showDeleteConfirmation()`** (dashboard.js:48)
3. **`showDeleteConfirmation()`** (dashboard.js:62)
4. **`oninput="checkDeleteConfirmation()"`** (dashboard.html:289)
5. **`window.checkDeleteConfirmation()`** (dashboard.js:52)
6. **`checkDeleteConfirmation()`** (dashboard.js:111)
7. **`onclick="deleteDataset()"`** (dashboard.html:296)
8. **`window.deleteDataset()`** (dashboard.js:56)
9. **`deleteDataset()`** (dashboard.js:125)

### Application Initialization Flow
1. **`document.addEventListener('DOMContentLoaded', ...)`** (app.js:392)
2. **`MicrobiomeApp.init()`** (app.js:14)
3. **`loadConfiguration()`** (app.js:24)
4. **`setupEventListeners()`** (app.js:43)
5. **`initializeTooltips()`** (app.js:58)
6. **`setupFormValidation()`** (app.js:66)
7. **`setupFlashMessages()`** (app.js:81)
8. **`setupFormSubmissions()`** (app.js:104)
9. **`setupFileUploads()`** (app.js:126)
10. **`setupNavigation()`** (app.js:171)
11. **`checkAuthStatus()`** (app.js:192)

## Summary

The dashboard uses a total of **47+ JavaScript functions** across multiple files:

- **Dashboard-specific**: 12 functions in `dashboard.js`
- **Application-wide**: 20+ functions in `app.js`
- **Dataset-specific**: 7+ functions in `dataset.js` (available if needed)
- **Smart table**: 4+ functions in `smart_table.js` (available if needed)
- **Bootstrap**: 6+ functions via CDN
- **HTML handlers**: 3 inline event handlers

The main functionality is self-contained within the dashboard template and `dashboard.js`, with the external `app.js` providing additional utility functions and application-wide features.
