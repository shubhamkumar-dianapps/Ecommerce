"""
Address App Constants

Central location for all magic numbers, strings, and configuration values.
Following DRY principles - define once, use everywhere.
"""

# Field Lengths
ADDRESS_TYPE_MAX_LENGTH = 10
CITY_MAX_LENGTH = 100
STATE_MAX_LENGTH = 100
COUNTRY_MAX_LENGTH = 100
POSTAL_CODE_MAX_LENGTH = 20
ADDRESS_LINE_MAX_LENGTH = 255

# Default Values
DEFAULT_COUNTRY = "India"

# Validation
MIN_POSTAL_CODE_LENGTH = 3
MAX_POSTAL_CODE_LENGTH = 10

# Indian postal code length
INDIA_POSTAL_CODE_LENGTH = 6

# Pagination
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 50

# Success Messages
ADDRESS_CREATED_SUCCESS = "Address created successfully"
ADDRESS_UPDATED_SUCCESS = "Address updated successfully"
ADDRESS_DELETED_SUCCESS = "Address deleted successfully"
DEFAULT_ADDRESS_UPDATED = "Default address updated successfully"

# Error Messages
ADDRESS_NOT_FOUND = "Address not found"
CANNOT_DELETE_DEFAULT = (
    "Cannot delete default address. Please set another address as default first."
)
INVALID_POSTAL_CODE = "Invalid postal code format"
INVALID_COUNTRY = "Country not supported"
POSTAL_CODE_REQUIRED = "Postal code is required"
NO_ADDRESSES_FOUND = "No addresses found for this user"

# Supported Countries (expand as needed)
SUPPORTED_COUNTRIES = [
    "India",
    "United States",
    "United Kingdom",
    "Canada",
    "Australia",
    "Germany",
    "France",
    "Japan",
    "Singapore",
]

# Country-specific postal code patterns
POSTAL_CODE_PATTERNS = {
    "India": r"^\d{6}$",
    "United States": r"^\d{5}(-\d{4})?$",
    "United Kingdom": r"^[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}$",
    "Canada": r"^[A-Z]\d[A-Z]\s?\d[A-Z]\d$",
    "Australia": r"^\d{4}$",
}
