from datetime import datetime


def convert_unix_to_date(unix_timestamp):
    """Converts unix timestamp to datetime"""
    unix_timestamp /= 1000  # convert to seconds as unix timestamp is in milliseconds
    converted_to_date = datetime.utcfromtimestamp(unix_timestamp).strftime("%Y-%m-%d")

    return converted_to_date


def split_full_name(name):
    """Split full name based on if they have a title or not, checks to see if they have a last name"""
    name_list = name.split(" ")
    titles = ["Mr", "Mrs", "Miss", "Ms", "Dr"]

    if name_list[0] in titles:  # Exclude user titles from snowflake
        first_name = name_list[1]

        try:
            last_name = name_list[2]

        except IndexError:  # Catch index error incase user did not give lastname
            last_name = None

    else:
        first_name = name_list[0]
        last_name = name_list[1]

    return first_name, last_name


def flatten_list(address_list):
    """Expands sublists present in lists, which is a consequence of splitting addresses"""
    flat_list = []

    for element in address_list:
        if type(element) is list:
            flat_list.extend(element)
        else:
            flat_list.append(element)
            
    return flat_list


def split_address(address):
    """Splits address based on various conditions, such as if they have whitespace or commas, or how many elements they have"""
    address_list = address.split(",")

    if len(address_list) < 4:
        address_list[0] = address_list[0].split(" ", 1)
        address_list = flatten_list(address_list)

    house_number = address_list[0]
    street_name = address_list[1].title()
    region = address_list[2].title()
    postcode = address_list[3]

    return house_number, street_name, region, postcode


def clean_user_data(user_dictionary):
    """Clean user data by converting timestamps, obtaining first and lastname, and splitting address field"""
    user_dictionary["account_create_date"] = convert_unix_to_date(
        user_dictionary["account_create_date"]
    )
    user_dictionary["date_of_birth"] = convert_unix_to_date(
        user_dictionary["date_of_birth"]
    )

    first_name, last_name = split_full_name(user_dictionary["name"])

    user_dictionary["first_name"] = first_name
    user_dictionary["last_name"] = last_name

    house_number, street_name, region, postcode = split_address(
        user_dictionary["address"]
    )

    user_dictionary["house_number"] = house_number
    user_dictionary["street_name"] = street_name
    user_dictionary["region"] = region
    user_dictionary["postcode"] = postcode
    user_dictionary["gender"] = user_dictionary["gender"].title()

    return user_dictionary
