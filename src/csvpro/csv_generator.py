import random

from faker import Faker

fake = Faker()


def generate_full_name():
    return f"{fake.last_name()} {fake.first_name()}"


def generate_job():
    return fake.job()


def generate_email():
    return fake.email()


def generate_text(sentences):
    return fake.paragraph(nb_sentences=sentences)


def generate_company():
    return fake.company()


def generate_address():
    return fake.address()


def generate_date():
    return fake.date()


def generate_integer(from_val, to_val):
    return random.randint(from_val, to_val)


def generate_phone_number():
    return fake.phone_number()


def generate_domain():
    return fake.domain_name()


def generate_csv(range_values):
    result = []
    choices = {
        "Full Name": generate_full_name(),
        "Job": generate_job(),
        "Email": generate_email(),
        "Domain Name": generate_domain(),
        "Phone Number": generate_phone_number(),
        "Company Name": generate_company(),
        "Address": generate_address(),
        "Date": generate_date(),
    }
    for row in range_values:
        column = row["column_type"]
        if column == "Text":
            result.append(generate_text(row["to_value"]))
        elif column == "Integer":
            result.append(generate_integer(row["from_value"], row["to_value"]))
        else:
            result.append(choices[column])
    return result
