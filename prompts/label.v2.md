Classify the customer email into exactly one category.

Categories:
billing: charges, invoices, payments, discount codes
shipping: delivery, tracking, parcels, delivery addresses
returns: sending items back, return labels, damaged or wrong items
account: login, password, email address, deleting or changing the account

Examples:
Email: "I was charged twice for my order." -> billing
Email: "Where is my parcel? The tracking has not updated." -> shipping
Email: "I want to send back the shoes, they are too small." -> returns
Email: "I forgot my password and cannot sign in." -> account

Email: "{{text}}"
Answer with only one word: billing, shipping, returns or account.
