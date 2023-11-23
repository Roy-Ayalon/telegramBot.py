import socket
import requests

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

def get_ip_address(url):
    try:
        ip = socket.gethostbyname(url)
        IP = ip
        return IP
    except:
        pass


def create_dictionary(new_text, url, date, Notifier, OS, ip_of_server):
    lines = new_text.split('\n')
    dictionary = {}
    dictionary = {'url': url}
    for line in lines:
        dictionary['date'] = date
        dictionary['Notifier'] = Notifier
        dictionary['OS'] = OS
        if line.startswith('person:'):
            dictionary['person'] = line.split(':', 1)[1].strip()
        elif line.startswith('phone:'):
            dictionary['phone'] = line.split(':', 1)[1].strip()
        elif line.startswith('e-mail:'):
            dictionary['email'] = (line.split(':', 1)[1].strip()).replace(' AT ', '@')
    dictionary['ip_of_server'] = ip_of_server
    return dictionary


def get_whois_info(url):
    response = requests.get(f'https://who.is/whois/{url}', headers=headers, verify=False)
    if response.status_code == 200:
        return response.text
    else:
        return None


def get_text_between_phrases(text, start_phrase, end_phrase):
    start_index = text.find(start_phrase)
    end_index = text.find(end_phrase)
    if start_index != -1 and end_index != -1:
        return text[start_index:end_index + len(end_phrase)]
    else:
        return None


def get_contact(new_list):
    data = []
    for list in new_list:
        try:
            url = list[2]
            whois_info = get_whois_info(url)
            new_text = get_text_between_phrases(whois_info, "person:", "registrar info:")
            ip_of_server = get_ip_address(url)
            dictionary = create_dictionary(new_text, url, list[0], list[1], list[3], ip_of_server)
            if new_text is not None:
                data.append(dictionary)  # Add the dictionary to the list
                print(dictionary)
            else:
                pass
        except:
            pass

    return data
