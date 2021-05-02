import requests
import re


def solve():
    return get_flag_1() + get_flag_2() + get_flag_3()


def get_flag_1():
    # desktop password is hidden in an image on flickr, check that the page exists:
    assert_exists('https://www.flickr.com/photos/191794730@N08/50952526891/')

    password = '6AV-Wh+X-mP#YLMa'
    base_url = 'https://lost-and-found.secchallenge.crysys.hu'
    session = requests.session()
    login = session.get(base_url).text
    csrf_token = re.search(r'csrf_token.*value="(.*)"', login).group(1)
    session.post(base_url, data={
        'username': 'bigjack',
        'password': password,
        'csrf_token': csrf_token
    })

    t = session.get(f'{base_url}/desktop').text

    return re.search('cd21{.*', t).group()


def get_flag_2():
    # these 3 images give us google maps coordinates:
    assert_exists('https://www.flickr.com/photos/191794730@N08/50958883777/', '1000meters')
    assert_exists('https://www.flickr.com/photos/191794730@N08/50952613822/', '550meters')
    assert_exists('https://www.flickr.com/photos/191794730@N08/50951763253/', '450meters')

    # flag 2 is hidden in a panorama image on google maps. Check that the image exists:
    assert_exists('https://lh5.googleusercontent.com/p/AF1QipMSJ5adLATi-5d2LbIJolC45Y9Krzu0N5uaNyZn='
                  'w600-h600-k-no-pi-10-ya180-ro-0-fo90')
    return "_17'5_b4r3ly_50c14l_3n6"


def get_flag_3():
    # flag 2 is hidden in the activity chart of a github user.
    # Check that the corresponding repo still exists:
    assert_exists('https://raw.githubusercontent.com/themrbigjack/code/'
                  '7123a754155e6cc1fe12c1f1a0e94264a42a1ab0/flag.c0r3dump')

    return "1nE3r1n6}"


def assert_exists(url, content=None):
    response = requests.get(url)
    assert response.status_code == 200
    if content is not None:
        assert content in response.text


if __name__ == "__main__":
    print(solve())
