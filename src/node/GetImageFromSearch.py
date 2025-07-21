import pyautogui
from node.Node import Node
import requests
from bs4 import BeautifulSoup
import cv2
import numpy as np
import pyautogui


class GetImageFromSearch(Node):
    __identifier__ = 'action'  # Identifiant du noeud
    NODE_NAME = 'GetImageFromSearch'       # Nom du noeud

    def __init__(self):
        super(GetImageFromSearch, self).__init__()

        # Ajout de ports d'entrée et de sortie
        self.add_input('input', multi_input=True)
        self.add_output('output')
        self.add_output('data')
        
        self.add_text_input('object to search', label='object to search', tooltip=None, tab=None)
        self.add_text_input('number of match', label='number of match', text="5", tooltip=None, tab=None)

        self.botManager = None

        self.value = None


    def download_image(self, image_url):
        response = requests.get(image_url)
        if response.status_code == 200:
            image_array = np.frombuffer(response.content, np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            if image is not None:
                return image, True
            else:
                print("Error: the image could not be decoded.")
        else:
            print("Error while downloading the image:", response.status_code)
        return None, False

    def bing_image_search(self, query, num_images=5):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        
        query = query.replace(' ', '+')
        url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2&first=1&tsc=ImageBasicHover"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print("Error during request:", response.status_code)
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        image_tags = soup.find_all('a', {'class': 'iusc'})
        
        image_urls = []
        for tag in image_tags[:num_images]:
            m = tag.get('m')
            if m:
                m_dict = eval(m)
                image_urls.append(m_dict.get('murl'))
        
        return image_urls



    def action(self):

        print("action search")
        # Search for images
        query = self.get_property('object to search')
        image_urls = self.bing_image_search(query, num_images=5)

        # Download the first image
        image, is_downloaded = self.download_image(image_urls[1]) if image_urls else (None, False)

        # Take a screenshot
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

        if is_downloaded and image is not None:
            orb = cv2.ORB_create()
            keypoints1, descriptors1 = orb.detectAndCompute(image, None)
            keypoints2, descriptors2 = orb.detectAndCompute(screenshot_cv, None)

            # FLANN configuration
            FLANN_INDEX_LSH = 6
            index_params = dict(algorithm=FLANN_INDEX_LSH,
                                table_number=6,
                                key_size=12,
                                multi_probe_level=1)
            search_params = dict(checks=50)

            flann = cv2.FlannBasedMatcher(index_params, search_params)
            matches = flann.knnMatch(descriptors1, descriptors2, k=2)

            # Apply Lowe's ratio test to filter good matches
            good_matches = []
            for match in matches:
                if len(match) == 2:
                    m, n = match
                    if m.distance < 0.7 * n.distance:
                        good_matches.append(m)


            if len(good_matches) >= int(self.get_property('number of match')):

                # Calculate the coordinates of the matched keypoints
                src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

                matched_screen_pts = dst_pts  # Ces points sont dans le screenshot (référentiel écran)
                screen_x = np.mean(matched_screen_pts[:, 0, 0])
                screen_y = np.mean(matched_screen_pts[:, 0, 1])


                # Bouge la souris vers les coordonnées détectées
                self.value = (screen_x, screen_y)


            else:
                print("Not enough good matches found to determine coordinates.")
        else:
            print("No valid image downloaded.")


    def getValue(self):
        print("self.value:", self.value)
        setattr(self.get_output("data"), 'data', self.value)
        
