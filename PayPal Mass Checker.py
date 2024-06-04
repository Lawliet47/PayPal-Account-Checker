import requests
import time

def get_paypal_access_token(client_id, client_secret):
    url = 'https://api.sandbox.paypal.com/v1/oauth2/token'
    headers = {'Accept': 'application/json'}
    data = {'grant_type': 'client_credentials'}
    response = requests.post(url, headers=headers, data=data, auth=(client_id, client_secret))
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"Failed to obtain access token: {response.status_code}, {response.text}")
        return None

def check_paypal_email(email, access_token):
    url = 'https://api.sandbox.paypal.com/v2/invoicing/invoices'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    invoice_number = f"INV-{email.replace('@', '-').replace('.', '-')}-{int(time.time())}"
    data = {
        "detail": {
            "invoice_number": invoice_number,
            "currency_code": "USD",
            "note": "Test invoice",
            "term": "Due on receipt",
            "memo": "This is a test invoice",
            "payment_term": {
                "term_type": "DUE_ON_RECEIPT"
            }
        },
        "invoicer": {
            "name": {
                "given_name": "Test",
                "surname": "User"
            },
            "email_address": "your-email@example.com"
        },
        "primary_recipients": [
            {
                "billing_info": {
                    "name": {
                        "given_name": "Test",
                        "surname": "Recipient"
                    },
                    "email_address": email
                }
            }
        ],
        "items": [
            {
                "name": "Test Item",
                "quantity": "1",
                "unit_amount": {
                    "currency_code": "USD",
                    "value": "1.00"
                }
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return True  # Email is associated with a PayPal account
    elif response.status_code == 422:
        # Check if the error is related to invalid recipient email
        error_details = response.json().get('details', [])
        for detail in error_details:
            if detail.get('field') == 'primary_recipients[0].billing_info.email_address' and detail.get('issue') == 'EMAIL_ADDRESS_NOT_VALID':
                return False  # Email is not associated with a PayPal account
    print(f"Error checking email: {response.status_code}, {response.text}")
    return None

def validate_paypal_emails(emails, client_id, client_secret):
    access_token = get_paypal_access_token(client_id, client_secret)
    if not access_token:
        return []

    results = []
    for email in emails:
        has_paypal_account = check_paypal_email(email, access_token)
        if has_paypal_account is not None:
            results.append((email, "Valid (GO)" if has_paypal_account else "Invalid"))
        else:
            results.append((email, "Invalid"))
    return results

# Read emails from a file
def read_emails_from_file(file_path):
    with open(file_path, 'r') as file:
        emails = file.readlines()
    return [email.strip() for email in emails]

# Write validation results to a file
def write_validation_results_to_file(results, output_file_path):
    with open(output_file_path, 'w') as file:
        for email, status in results:
            file.write(f"{email}: {status}\n")

# Main function
def main(input_file, output_file, client_id, client_secret):
    emails = read_emails_from_file(input_file)
    results = validate_paypal_emails(emails, client_id, client_secret)
    write_validation_results_to_file(results, output_file)

# Usage
input_file = '/Users/l/Downloads/emails.txt'  # Replace with your input file path
output_file = '/Users/l/Downloads/valid_emails.txt'  # Replace with your desired output file path
client_id = 'XXXXXXXX'  # Replace with your PayPal client ID
client_secret = 'XXXXXXXXX'  # Replace with your PayPal client secret

if __name__ == "__main__":
    main(input_file, output_file, client_id, client_secret)
