// Dashboard-specific JavaScript functions
// Extracted from dashboard.html for better organization and maintainability

class DashboardManager {
    constructor() {
        this.gridView = null;
        this.listView = null;
        this.gridContainer = null;
        this.listContainer = null;
        this.datasetToDelete = null;
    }

    // Initialize dashboard functionality
    init() {
        this.gridView = document.getElementById("gridView");
        this.listView = document.getElementById("listView");
        this.gridContainer = document.getElementById("grid-container");
        this.listContainer = document.getElementById("list-container");

        this.setupViewToggle();
        this.setupGlobalFunctions();
    }

    // Setup view toggle functionality
    setupViewToggle() {
        if (this.gridView) {
            this.gridView.addEventListener("click", () => {
                this.gridView.classList.add("active");
                this.listView.classList.remove("active");
                this.gridContainer.classList.remove("d-none");
                this.listContainer.classList.add("d-none");
            });
        }

        if (this.listView) {
            this.listView.addEventListener("click", () => {
                this.listView.classList.add("active");
                this.gridView.classList.remove("active");
                this.listContainer.classList.remove("d-none");
                this.gridContainer.classList.add("d-none");
            });
        }
    }

    // Setup global functions for dataset deletion
    setupGlobalFunctions() {
        // Make functions globally available
        window.showDeleteConfirmation = (datasetId, datasetName) => {
            this.showDeleteConfirmation(datasetId, datasetName);
        };

        window.checkDeleteConfirmation = () => {
            this.checkDeleteConfirmation();
        };

        window.deleteDataset = () => {
            this.deleteDataset();
        };
    }

    // Show delete confirmation modal
    showDeleteConfirmation(datasetId, datasetName) {
        this.datasetToDelete = { id: datasetId, name: datasetName };

        // Update modal content
        const nameElement = document.getElementById("datasetNameToDelete");
        if (nameElement) {
            nameElement.textContent = datasetName;
        }

        // Get dataset details from the table row
        const row = document
            .querySelector(`button[onclick="showDeleteConfirmation(${datasetId}, '${datasetName}')"]`)
            .closest("tr");
        
        if (row) {
            const fileCount = row.querySelector("td:nth-child(3)").textContent;
            const size = row.querySelector("td:nth-child(4)").textContent;

            // Populate dataset details
            const detailsElement = document.getElementById("datasetDetailsToDelete");
            if (detailsElement) {
                detailsElement.innerHTML = `
                    <li><strong>${fileCount}</strong> uploaded files</li>
                    <li><strong>${size}</strong> of data</li>
                    <li>All analysis results and metadata</li>
                `;
            }
        }

        // Reset confirmation input
        const confirmationInput = document.getElementById("deleteConfirmation");
        const confirmBtn = document.getElementById("confirmDeleteBtn");
        
        if (confirmationInput) {
            confirmationInput.value = "";
        }
        if (confirmBtn) {
            confirmBtn.disabled = true;
        }

        // Show modal
        const modalElement = document.getElementById("deleteDatasetModal");
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        }
    }

    // Check delete confirmation input
    checkDeleteConfirmation() {
        const input = document.getElementById("deleteConfirmation");
        const confirmBtn = document.getElementById("confirmDeleteBtn");

        if (input && confirmBtn) {
            if (input.value.toLowerCase() === "delete") {
                confirmBtn.disabled = false;
            } else {
                confirmBtn.disabled = true;
            }
        }
    }

    // Delete dataset
    async deleteDataset() {
        if (!this.datasetToDelete) {
            console.error("No dataset selected for deletion");
            return;
        }

        const confirmBtn = document.getElementById("confirmDeleteBtn");
        const input = document.getElementById("deleteConfirmation");

        if (!confirmBtn || !input) {
            console.error("Required elements not found");
            return;
        }

        // Double-check confirmation
        if (input.value.toLowerCase() !== "delete") {
            this.showAlert('Please type "delete" to confirm deletion', "warning");
            return;
        }

        // Disable button and show loading
        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Deleting...';

        try {
            // Send delete request
            const response = await fetch(`/dataset/${this.datasetToDelete.id}/delete`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            const data = await response.json();

            if (data.success) {
                this.showAlert(data.message, "success");

                // Close modal
                const modalElement = document.getElementById("deleteDatasetModal");
                if (modalElement) {
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) {
                        modal.hide();
                    }
                }

                // Remove the row from the table
                const row = document
                    .querySelector(
                        `button[onclick="showDeleteConfirmation(${this.datasetToDelete.id}, '${this.datasetToDelete.name}')"]`
                    )
                    ?.closest("tr");
                if (row) {
                    row.remove();
                }

                // Update the grid view if it exists
                const gridCard = document.querySelector(`[data-dataset-id="${this.datasetToDelete.id}"]`);
                if (gridCard) {
                    gridCard.remove();
                }

                // Update statistics
                this.updateDashboardStats();

                // Redirect to dashboard after a short delay
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                this.showAlert(data.message, "danger");
                this.resetDeleteButton();
            }
        } catch (error) {
            console.error("Delete error:", error);
            this.showAlert("Error deleting dataset. Please try again.", "danger");
            this.resetDeleteButton();
        }
    }

    // Reset delete button to original state
    resetDeleteButton() {
        const confirmBtn = document.getElementById("confirmDeleteBtn");
        if (confirmBtn) {
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = '<i class="fas fa-trash me-1"></i>Delete Dataset';
        }
    }

    // Update dashboard statistics
    updateDashboardStats() {
        // Update the total datasets count
        const totalDatasetsCard = document.querySelector(".card.bg-primary .card-title + h2");
        if (totalDatasetsCard) {
            const currentCount = parseInt(totalDatasetsCard.textContent);
            totalDatasetsCard.textContent = currentCount - 1;
        }

        // Update ready datasets count if needed
        const readyDatasetsCard = document.querySelector(".card.bg-success .card-title + h2");
        if (readyDatasetsCard) {
            // This would need more complex logic to determine if the deleted dataset was ready
            // For now, we'll just reload the page to get accurate counts
        }
    }

    // Show alert messages
    showAlert(message, type) {
        // Create alert element
        const alertDiv = document.createElement("div");
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at the top of the content
        const container = document.querySelector(".container");
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);

            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
    const dashboard = new DashboardManager();
    dashboard.init();
});

// Export for potential external use
window.DashboardManager = DashboardManager;
